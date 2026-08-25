# data-engineering-mcp

Servidor MCP genérico, local e offline que transforma cabeçalhos de arquivos XLSX em um catálogo consultável, infere **relacionamentos candidatos** e gera somente SQL Oracle `SELECT/WITH`. Não acessa bancos de dados, não executa SQL e não possui integração ou dependência de Power BI.

## Requisitos e instalação

- Python 3.12
- MCP Python SDK 2.x (`MCPServer`, a API pública atual da versão instalada)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Dependências de runtime: `mcp`, `pandas`, `openpyxl` e `pydantic`; testes usam `pytest`. O catálogo usa `openpyxl` diretamente para abrir os workbooks em modo read-only e ler somente a primeira linha necessária.

## Dados e arquitetura

Os datasets são fornecidos localmente pelo usuário e não fazem parte do repositório. Coloque arquivos `.xlsx` em `data/`; eles permanecem disponíveis ao MCP, mas são ignorados pelo Git. Cada arquivo é uma tabela. O nome lógico remove `.xlsx`, o prefixo `rawzn.` e o sufixo `_SINTETICO`, com comparação case-insensitive. A primeira aba não chamada `SQL` que tenha cabeçalhos é usada; registros não participam da descoberta.

```text
data/*.xlsx -> Catalog -> RelationshipEngine -> SQLGenerator
                                      \-> explicação conservadora de SQL
```

Novos arquivos são descobertos por `atualizar_catalogo`, sem alteração de código. A atualização também detecta remoções e mudanças na lista ordenada de cabeçalhos, atualiza o timestamp e recalcula candidatos. O diretório local de schemas/datasets é configurável pela variável `DATA_ENGINEERING_MCP_DATA_DIR`; o padrão é `data/`.

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
- `gerar_sql`, `gerar_select`, `explicar_sql`

`gerar_sql` recebe `tabelas`, `colunas` e filtros tipados `{table?, column, operator, value}`. Operadores: `=`, `<>`, `>`, `>=`, `<`, `<=`, `IN`, `IS NULL`, `IS NOT NULL`, `LIKE`. Valores viram bind variables (`:p1`), nunca texto concatenado. Colunas ambíguas exigem `TABELA.COLUNA`. O JOIN padrão é `LEFT JOIN`, escolha conservadora para preservar linhas da primeira tabela; a ferramenta informa candidatos MEDIUM e rejeita LOW por padrão.

Exemplo de argumentos:

```json
{
  "tabelas": ["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA"],
  "colunas": ["CD_USUARIO", "NM_PESSOA_RAZAO_SOCIAL"],
  "filtros": [{"column": "FL_STATUS_USUARIO", "operator": "=", "value": 2}]
}
```

## Confiança de relacionamentos

Todo resultado é candidato nominal, nunca PK/FK confirmada. O score começa em 20 por nome idêntico; soma 30 para prefixos `CD_`, `ID_` ou `NU_`; soma 20 quando a entidade da coluna aparece no nome de uma tabela e mais 10 se aparece em ambas. Ocorrência em mais de duas tabelas reduz 5 por ocorrência excedente (máximo 25); campo genérico ou sem prefixo identificador reduz 25. `HIGH >= 75`, `MEDIUM >= 50`, `LOW < 50`. Não há leitura de valores nem cálculo de cardinalidade, e esta versão não possui metadados explícitos de PK/FK.

## Segurança e limitações

Somente SQL Oracle `SELECT/WITH` estruturado é gerado. Não há superfície para DDL/DML, SQL arbitrário em filtros, credenciais, rede, banco ou APIs externas.

Limitações conhecidas:

- relacionamentos são inferidos nominalmente e podem produzir falsos positivos ou negativos semânticos;
- esta versão não possui metadados explícitos de PK/FK;
- campos genéricos ou compartilhados podem produzir caminhos inadequados;
- candidatos `LOW` não devem ser utilizados automaticamente;
- candidatos `MEDIUM` são inferências, não confirmações;
- `explicar_sql` faz análise sintática conservadora e não valida semanticamente a consulta no Oracle;
- alguns logs com acentos podem ter exibição cosmética incorreta no console Windows configurado como CP1252.

Os XLSX são sempre tratados como read-only. Datasets locais (`data/*`, `*.xlsx`, `*.xls`, `*.csv` e `*.parquet`) são ignorados e não fazem parte do repositório.
