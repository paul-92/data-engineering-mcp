# data-engineering-mcp

Servidor MCP local que transforma cabeçalhos de XLSX em catálogo consultável, infere **relacionamentos candidatos**, mantém definições confirmadas de colunas e gera SQL Oracle `SELECT/WITH`. O modelo de linguagem do cliente MCP interpreta pedidos em linguagem natural; o servidor valida e executa apenas operações locais sobre arquivos, sem acessar bancos nem executar SQL.

## Requisitos e instalação

- Python 3.12
- MCP Python SDK 2.x (`MCPServer`, a API pública atual da versão instalada)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Dependências de runtime: `mcp`, `pandas`, `openpyxl` e `pydantic`; testes usam `pytest`. O catálogo lê os cabeçalhos em modo read-only. O perfil de colunas lê as linhas localmente somente quando solicitado e não grava valores brutos.

## Dados e arquitetura

Os datasets são fornecidos localmente pelo usuário e não fazem parte do repositório. Coloque arquivos `.xlsx` em `data/`; eles permanecem disponíveis ao MCP, mas são ignorados pelo Git. Cada arquivo é uma tabela. O nome lógico remove `.xlsx`, o prefixo `rawzn.` e o sufixo `_SINTETICO`, com comparação case-insensitive. A primeira aba não chamada `SQL` que tenha cabeçalhos é usada. Registros não participam da descoberta do schema; podem ser lidos localmente sob demanda para produzir perfis agregados.

```text
data/*.xlsx -> Catalog -> RelationshipEngine <- metadata/relationships.json
                                      |
                                      +-> SQLGenerator
                                      \-> explicação conservadora de SQL
```

Novos arquivos são descobertos por `atualizar_catalogo`, sem alteração de código. A atualização também detecta remoções e mudanças na lista ordenada de cabeçalhos, atualiza o timestamp e recalcula candidatos. O diretório local de schemas/datasets é configurável pela variável `DATA_ENGINEERING_MCP_DATA_DIR`; o padrão é `data/`. O arquivo de relacionamentos pode ser substituído por `DATA_ENGINEERING_MCP_RELATIONSHIPS_FILE`; o padrão é `metadata/relationships.json`.

## Execução e testes

```powershell
.\.venv\Scripts\data-engineering-mcp.exe
# ou
.\.venv\Scripts\python.exe -m data_engineering_mcp.server

.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts\smoke_test.py
```

O transporte padrão é stdio. Logs vão para stderr para não corromper o protocolo. Defina `DATA_ENGINEERING_MCP_DATA_DIR` para usar outra pasta local.

## Tools

- `listar_tabelas`, `descrever_tabela`, `buscar_coluna`, `buscar_tabelas`
- `inferir_relacionamentos`, `encontrar_caminho`, `gerar_join`
- `atualizar_catalogo`, `status_catalogo`
- `gerar_sql`, `gerar_select`, `explicar_sql`, `revisar_sql`
- `entender_coluna`, `perfil_colunas`, `ensinar_coluna`

`gerar_sql` recebe `tabelas`, `colunas`, filtros tipados `{table?, column, operator, value}` e `grain` opcional. Operadores: `=`, `<>`, `>`, `>=`, `<`, `<=`, `IN`, `IS NULL`, `IS NOT NULL`, `LIKE`. Valores viram bind variables (`:p1`), nunca texto concatenado. Colunas ambíguas exigem `TABELA.COLUNA`. O JOIN padrão é `LEFT JOIN`, escolha conservadora para preservar linhas da primeira tabela. Consultas multi-tabela só geram JOIN com relacionamento `APPROVED`, livre de conflitos e aceito também pelo controle de confiança; `permitir_baixa_confianca` não contorna autoridade ou conflitos. Relações `INFERRED`, `KNOWN`, sem autoridade ou conflitantes falham com os endpoints e a homologação necessária, sem escolha silenciosa de alternativa. Consultas de uma tabela permanecem inalteradas.

Quando `grain` é informado, suas colunas devem pertencer à primeira tabela solicitada. Antes de emitir SQL, cada JOIN também precisa ter cardinalidade orientada `MANY_TO_ONE` ou `ONE_TO_ONE`, com autoridade explícita, sem conflitos, e uma chave `PRIMARY_KEY` ou `UNIQUE` correspondente no lado alcançado. `ONE_TO_MANY`, `MANY_TO_MANY`, `UNKNOWN`, chave ausente ou conflito bloqueiam a geração sem SQL parcial e sem deduplicação automática. O gate prova somente no máximo uma correspondência no lado alcançado; não infere nulabilidade ou existência obrigatória.

Exemplo de argumentos:

```json
{
  "tabelas": ["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA"],
  "colunas": ["CD_USUARIO", "NM_PESSOA_RAZAO_SOCIAL"],
  "filtros": [{"column": "FL_STATUS_USUARIO", "operator": "=", "value": 2}],
  "grain": ["RAW_HAP_TB_USUARIO.CD_USUARIO"]
}
```

## Intenção estruturada de consulta

`data_engineering_mcp.query_intent.QueryIntent` é um contrato interno, declarativo e revisável antes da geração SQL. Ele contém somente `sources`, `output_columns`, `filters`, `relationships`, `grain` opcional, `warnings` e `authority_pending`. Colunas podem declarar `alias`; filtros carregam `field`, `operator` e `value` ou referência a outro campo. Relacionamentos carregam uma identidade e preservam a autoridade `INFERRED`, `KNOWN` ou `APPROVED` recebida da autoridade de relacionamentos, sem promoção. Autoridade ausente, `INFERRED` ou conflitos exigem aviso ou pendência explícita.

```python
from data_engineering_mcp.query_intent import OutputColumn, QueryFilter, QueryIntent, RelationshipIntent

intent = QueryIntent(
    sources=["ORDERS", "CUSTOMERS"],
    output_columns=[OutputColumn(field="CUSTOMERS.NAME", alias="customer_name")],
    filters=[QueryFilter(field="ORDERS.STATUS", operator="=", value="OPEN")],
    relationships=[RelationshipIntent(identity="REL-001", authority="KNOWN")],
    grain=["ORDERS.ID"],
)
payload = intent.to_dict()
```

O módulo apenas representa e serializa intenção em ordem estável. Ele não descobre relacionamentos, escolhe caminhos, valida semântica de catálogo, gera ou executa SQL, cria CTEs/`EXISTS`, infere agregações nem adiciona uma tool MCP.

## Autoridade e confiança de relacionamentos

Todo relacionamento expõe `authority`, `source`, `decision` e `conflicts`. `INFERRED` é produzido somente pela heurística atual; `KNOWN` vem de uma fonte explícita identificável; `APPROVED` exige `decision.id`, `decision.date` e `decision.decided_by` exatamente igual a `HUMAN/Product Owner`. Score, repetição ou uso anterior nunca promovem autoridade. Metadado explícito válido prevalece sobre a mesma relação inferida; discordâncias de endpoints são preservadas em `conflicts`, sem resolução ou promoção silenciosa.

O único meio de manutenção é a edição manual de `metadata/relationships.json`. O arquivo contém `relationships` e pode conter `keys`. O exemplo abaixo é fictício e não está incluído no arquivo real:

```json
{
  "relationships": [{
    "source_table": "TABELA_A", "source_column": "ID_A",
    "target_table": "TABELA_B", "target_column": "ID_A",
    "authority": "APPROVED", "source": "decision:REL-001",
    "decision": {"id": "REL-001", "date": "2026-09-11", "decided_by": "HUMAN/Product Owner"},
    "cardinality": "MANY_TO_ONE",
    "cardinality_source": "ddl:exemplo-v1",
    "cardinality_authority": "KNOWN"
  }],
  "keys": [{
    "table": "TABELA_B", "columns": ["ID_A"], "kind": "PRIMARY_KEY",
    "source": "ddl:exemplo-v1", "authority": "KNOWN"
  }]
}
```

Relacionamentos compostos usam `source_columns` e `target_columns` com pares posicionais na ordem declarada. O formato legado escalar continua válido para relações simples; não misture as duas formas no mesmo relacionamento. Por exemplo:

```json
{
  "source_table": "TABELA_A", "source_columns": ["ID_B", "VERSAO_B"],
  "target_table": "TABELA_B", "target_columns": ["ID_B", "VERSAO_B"],
  "authority": "APPROVED", "source": "decision:REL-COMPOSITE",
  "decision": {"id": "REL-COMPOSITE", "date": "2026-09-18", "decided_by": "HUMAN/Product Owner"},
  "cardinality": "MANY_TO_ONE", "cardinality_source": "ddl:exemplo-v1",
  "cardinality_authority": "KNOWN"
}
```

Para preservar o grão, todos os pares precisam corresponder exatamente, na mesma ordem, a uma chave `PRIMARY_KEY` ou `UNIQUE` autorizada no lado alcançado; chave parcial, reordenada, autoridade insuficiente ou conflito bloqueiam o SQL.

Cardinalidade é orientada de `source_table` para `target_table` e aceita `ONE_TO_ONE`, `MANY_TO_ONE`, `ONE_TO_MANY`, `MANY_TO_MANY` ou `UNKNOWN`. Autoridade de relacionamento, cardinalidade e chave são independentes: nenhuma promove outra. `KNOWN` exige fonte explícita; `APPROVED` exige decisão HUMAN completa. Cardinalidade ausente é `UNKNOWN`, nunca inferida por nome, posição ou score. Chaves podem ser simples ou compostas e aceitam somente `PRIMARY_KEY` ou `UNIQUE`.

Arquivo ausente equivale a nenhum metadado explícito. O documento legado `{"relationships": []}` continua válido. JSON inválido, campos extras, endpoints ou colunas inexistentes, chave vazia, fontes vazias ou `APPROVED` sem decisão humana completa interrompem a carga com erro claro. Conflitos ficam visíveis e bloqueiam a prova de preservação. O score de confiança continua independente: começa em 20 por nome idêntico; soma 30 para prefixos `CD_`, `ID_` ou `NU_`; soma 20 quando a entidade aparece no nome de uma tabela e mais 10 se aparece em ambas. `HIGH >= 75`, `MEDIUM >= 50`, `LOW < 50`. Perfis de valores são independentes dos relacionamentos: não há importação de DDL, acesso a banco ou cálculo empírico de cardinalidade.

## Segurança e limitações

Somente SQL Oracle `SELECT/WITH` estruturado é gerado. Não há superfície para DDL/DML, SQL arbitrário em filtros, credenciais, acesso ao banco ou execução de SQL. O servidor não faz chamadas externas; o cliente MCP pode enviar ao seu modelo o pedido, os metadados retornados e as respostas das ferramentas.

Limitações conhecidas:

- relacionamentos são inferidos nominalmente e podem produzir falsos positivos ou negativos semânticos;
- metadados explícitos são declarações fornecidas ao sistema, não validação física de PK/FK/cardinalidade;
- campos genéricos ou compartilhados podem produzir caminhos inadequados;
- candidatos `LOW` não devem ser utilizados automaticamente;
- candidatos `MEDIUM` são inferências, não confirmações;
- `explicar_sql` faz análise sintática conservadora e não valida semanticamente a consulta no Oracle;
- alguns logs com acentos podem ter exibição cosmética incorreta no console Windows configurado como CP1252.

Os XLSX são sempre tratados como read-only. Datasets locais (`data/*`, `*.xlsx`, `*.xls`, `*.csv` e `*.parquet`) são ignorados e não fazem parte do repositório.


## Linguagem natural, dicionário e perfis de colunas

O cliente MCP (por exemplo, ChatGPT ou Codex) interpreta o pedido em linguagem natural e usa as ferramentas para consultar o schema, os significados e os relacionamentos aprovados. O servidor não contém um modelo de linguagem. Se faltar uma decisão que possa mudar o resultado, o cliente deve perguntar antes de chamar `gerar_sql`.

- `entender_coluna`: retorna definição confirmada e perfil agregado local da coluna.
- `perfil_colunas`: calcula, em modo read-only, total de linhas com conteúdo, valores vazios e distribuição de tipos. O perfil não persiste exemplos de valores.
- `ensinar_coluna`: registra uma definição e sinônimos fornecidos ou confirmados pelo usuário.
- `revisar_sql`: analisa `SELECT/WITH` e emite alertas estáticos conservadores, sem reescrever nem executar a consulta.

Por padrão, exemplos brutos não são retornados. `perfil_colunas` aceita `incluir_amostras=true`, mas o cliente só deve usar essa opção depois de autorização explícita do usuário. Até cinco valores distintos por coluna podem ser retornados nessa chamada; eles não são persistidos pelo MCP. Os valores retornados passam a fazer parte da resposta da ferramenta e podem ser enviados ao modelo pelo cliente.

O dicionário é salvo em `data/.mcp_column_dictionary.json`; perfis agregados ficam em `data/.mcp_column_profiles.json`. Ambos são ignorados pelo Git junto com os dados locais. Use `DATA_ENGINEERING_MCP_COLUMN_DICTIONARY_FILE` e `DATA_ENGINEERING_MCP_COLUMN_PROFILES_FILE` para alterar os caminhos. Perfis são armazenados por fingerprint do arquivo e recalculados após mudança de tamanho, data de modificação ou schema, quando a ferramenta de perfil for chamada.

`revisar_sql` pode apontar, por exemplo, uso de `SELECT *` e padrão `LIKE` iniciado por curinga. Isso não confirma que a consulta é semanticamente equivalente nem que terá desempenho melhor. O cliente pode propor uma reescrita em linguagem natural; deve explicar as mudanças e preservar filtros, agregações e grão. A validação final do plano e do desempenho depende do Oracle, que este MCP não acessa.
