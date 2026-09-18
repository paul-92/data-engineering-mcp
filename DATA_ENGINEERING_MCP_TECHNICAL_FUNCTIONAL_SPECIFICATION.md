# Data Engineering MCP v0.1.0
## Especificacao Tecnica e Funcional Auditavel

**Documento:** `DATA_ENGINEERING_MCP_TECHNICAL_FUNCTIONAL_SPECIFICATION.md`
**Produto:** `data-engineering-mcp`
**Versao:** `0.1.0`
**Status:** `OPERATIONAL / DEVELOPMENT CLOSED`
**Aceite:** `HUMAN FINAL PRODUCT ACCEPTANCE: APPROVED`
**Data de baseline:** `2026-09-18`
**Transporte:** MCP sobre `stdio`
**Escopo:** produto MCP local/offline, nao projetos consumidores

> Este documento descreve o produto efetivamente entregue. O `PROJECT_HANDOFF.txt` e o registro de continuidade e estado operacional; este documento e a especificacao tecnica e funcional auditavel. O handoff usa normativamente o nome portatil `PROJECT_HANDOFF_MCP.txt`, mas o arquivo fisico presente neste repositorio e `PROJECT_HANDOFF.txt`.

## 1. Convencoes de status

Cada requisito e evidenciado com um ou mais estados:

- **IMPLEMENTED:** existe implementacao correspondente no runtime, modelo, skill ou artefato autorizado.
- **VERIFIED:** ha teste, smoke test, inspeccao, hash, evidencia de execucao ou outra verificacao reproduzivel.
- **ACCEPTED:** o HUMAN/Product Owner aceitou o resultado no gate aplicavel.
- **RESIDUAL_RISK:** limitacao conhecida que permanece sem invalidar o escopo aceito.
- **BACKLOG:** possibilidade futura nao autorizada nem tratada como capacidade entregue.

Uma mencao em uma SPEC, PLAN ou README, isoladamente, nao e considerada evidencia de implementacao.

## 2. Identificacao, objetivo e escopo

### 2.1 Identificacao

O produto e um servidor MCP local/offline para apoiar engenharia de dados a partir de representacoes locais. A versao entregue e `0.1.0`, conforme `pyproject.toml`, `server.py` e o smoke test.

### 2.2 Objetivo funcional

O MCP deve:

1. ler estruturas locais, principalmente arquivos XLSX;
2. catalogar tabelas e colunas;
3. descobrir candidatos de relacionamento sem promover inferencias;
4. carregar metadata declarativa de relacionamentos e keys;
5. representar autoridade, decisao, conflitos, cardinalidade e grain;
6. representar uma intencao estruturada de consulta;
7. gerar SQL Oracle `SELECT/WITH` parametrizado e seguro, sem executar SQL;
8. explicar SQL de forma sintatica e conservadora;
9. bloquear automaticamente usos multi-tabela sem autoridade e evidencia suficientes.

### 2.3 Escopo funcional entregue

O escopo aceito inclui catalogo local de XLSX, exatamente 12 MCP tools, relacionamento simples e composto, keys simples e compostas, cardinalidade com autoridade independente, preservacao de grain fail-closed, query intent declarativa, geracao de SQL Oracle e explicacao SQL. A skill `data-engineering-spec-driven` coordena intake, discovery e geracao proporcional de specs; ela nao executa specs nem substitui o orquestrador.

### 2.4 Fora de escopo

Nao fazem parte do produto v0.1.0:

- execucao de SQL em Oracle ou qualquer banco;
- conexao direta a banco, credenciais, rede, gateway ou refresh remoto;
- DDL, DML, `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT` ou `REVOKE`;
- inferencia automatica de autoridade, key, cardinalidade ou verdade semantica;
- cadastro/homologacao operacional de metadata por uma tool MCP;
- planner/optimizer, custo, seletividade ou `EXPLAIN PLAN`;
- deduplicacao, arbitragem, `DISTINCT` ou agregacao inventada para esconder incerteza;
- Power BI, Figma ou BI como dependencia do runtime MCP;
- dashboard, modelo semantico, UI, sidecar, daemon ou workflow engine;
- publicacao, deploy, release ou distribuicao;
- alteracao automatica ou migracao manual obrigatoria de metadata existente;
- hardcode de tabelas HAP ou de um conjunto fixo de tabelas.

## 3. Arquitetura tecnica

```text
Arquivos XLSX locais
        |
        v
Catalog ----------------------> status/catalogo
        |
        v
RelationshipEngine <----------- metadata/relationships.json
        |              \
        |               +--> autoridade, keys, cardinalidade, grain
        v
SQLGenerator <--------------- QueryIntent (contrato declarativo separado)
        |
        v
MCPServer / 12 tools -------> stdio

SQLExplainer e uma capacidade sintatica independente do SQLGenerator.
Skill data-engineering-spec-driven reside fora do pacote Python.
```

### 3.1 Principios arquiteturais

- tabelas atuais sao dados, nao arquitetura;
- catalogo e metadata-driven e data-driven;
- novos XLSX devem ser descobertos sem codigo especifico da tabela;
- autoridade de relacionamento, cardinalidade e key sao independentes;
- a representacao interna de endpoints usa listas ordenadas; o formato escalar legado e preservado para compatibilidade;
- o runtime nao executa consultas nem promove fatos por score.

## 4. Stack e requisitos de ambiente

| Item | Entrega/verificacao |
|---|---|
| Python | `>=3.12` declarado em `pyproject.toml`; ambiente verificado por `.venv` |
| MCP SDK | `mcp>=2.1,<3`; servidor `MCPServer`, versao reportada `0.1.0` |
| Pydantic | `pydantic>=2.12,<3` para contratos e validacao |
| XLSX | `openpyxl>=3.1,<4`, leitura `read_only=True`, `data_only=True` |
| Dados tabulares | `pandas>=3,<4` como dependencia declarada; descoberta do catalogo usa openpyxl |
| Testes | `pytest`, `pytest-asyncio` |
| Transporte | `stdio`; logs em stderr |
| SQL | Oracle estrutural `SELECT/WITH`, parametrizado |
| Sistema | exige somente ambiente local capaz de instalar dependencias e ler o diretorio `data/` |

Comandos de reproducao:

```powershell
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\smoke_test.py
```

## 5. Componentes internos

| Componente | Responsabilidade | Estado |
|---|---|---|
| `src/data_engineering_mcp/server.py` | inicializa catalogo, engine, generator e expoe as 12 tools | IMPLEMENTED / VERIFIED / ACCEPTED |
| `catalog.py` | descobre XLSX, normaliza nomes, le headers e fornece busca/status | IMPLEMENTED / VERIFIED / ACCEPTED |
| `models.py` | contratos Pydantic de catalogo, relationships, keys, cardinalidade, filters e SQL | IMPLEMENTED / VERIFIED / ACCEPTED |
| `relationships.py` | inferencia heuristica, carga/merge de metadata, identidade, paths, keys e grain | IMPLEMENTED / VERIFIED / ACCEPTED |
| `sql_generator.py` | resolve colunas/filtros, escolhe joins aceitaveis e gera SQL | IMPLEMENTED / VERIFIED / ACCEPTED |
| `sql_explainer.py` | analise sintatica conservadora de SELECT/WITH | IMPLEMENTED / VERIFIED / ACCEPTED |
| `query_intent.py` | contrato declarativo serializavel; nao gera nem executa SQL | IMPLEMENTED / VERIFIED / ACCEPTED |
| `exceptions.py` | erros de dominio e operacoes SQL proibidas | IMPLEMENTED / VERIFIED |
| `data-engineering-spec-driven/SKILL.md` | intake, source discovery, coordenacao e specs proporcionais | IMPLEMENTED / VERIFIED / ACCEPTED |
| `metadata/relationships.json` | fonte declarativa local; nao e escrito automaticamente | PRESENT / VERIFIED |

## 6. Superficie MCP: exatamente 12 tools

A superficie publica validada pelo smoke test contem exatamente estas tools. Entradas e saidas abaixo sao os contratos observados no `server.py`; erros de dominio sao retornados pelo boundary MCP quando aplicavel.

### FR-001 — `listar_tabelas`

- **Entrada:** nenhuma.
- **Saida:** `list[str]` com nomes logicos ordenados deterministicamente.
- **Finalidade:** listar tabelas catalogadas localmente.
- **Restricoes:** nao le banco; depende do catalogo carregado.
- **Erros/bloqueios:** erro de inicializacao se a carga do catalogo falhar de forma fatal; nomes inexistentes nao se aplicam.
- **Evidencia:** smoke MCP; `Catalog.list_tables`; testes de catalogo.

### FR-002 — `descrever_tabela`

- **Entrada:** `tabela: str`.
- **Saida:** schema da tabela, arquivo fonte, worksheet, colunas, `column_count` e keys explicitas da tabela.
- **Finalidade:** inspecionar uma tabela sem ler dados de linha.
- **Restricoes:** keys sao somente as carregadas da metadata; nenhuma key e inventada.
- **Erros/bloqueios:** `TableNotFoundError` para tabela ausente.
- **Evidencia:** `server.py`, `Catalog.get_table`, `test_server.py`.

### FR-003 — `buscar_coluna`

- **Entrada:** `coluna: str`.
- **Saida:** lista ordenada de referencias `TABELA.COLUNA` com comparacao case-insensitive e correspondencia exata.
- **Finalidade:** localizar uma coluna no catalogo.
- **Restricoes:** nao resolve semantica, relacionamento ou unicidade.
- **Erros/bloqueios:** lista vazia quando nao ha correspondencia.
- **Evidencia:** `Catalog.find_column`, `test_catalog.py`.

### FR-004 — `buscar_tabelas`

- **Entrada:** `termo: str`.
- **Saida:** lista de nomes de tabelas cujo nome contem o termo, case-insensitive.
- **Finalidade:** busca parcial de tabelas.
- **Restricoes:** nao consulta banco nem dados de linha.
- **Erros/bloqueios:** lista vazia quando nao ha correspondencia.
- **Evidencia:** `Catalog.search_tables`, `test_catalog.py`.

### FR-005 — `inferir_relacionamentos`

- **Entrada:** nenhuma.
- **Saida:** lista de `RelationshipCandidate` serializados, com endpoints, confidence, score, rationale, authority, source, decision, conflicts, cardinalidade e informacoes de cardinalidade.
- **Finalidade:** expor candidatos heuristicos e metadata explicita mesclada.
- **Restricoes:** heuristica produz somente candidatos single-column; score nao promove authority; conflitos permanecem visiveis.
- **Erros/bloqueios:** metadata JSON invalida, coluna inexistente, key invalida ou declaracao estrutural invalida interrompem a carga com erro de dominio.
- **Evidencia:** `RelationshipEngine.infer`, `test_relationships.py`, smoke e SPEC-002/SPEC-011.

### FR-006 — `encontrar_caminho`

- **Entrada:** `tabela_origem: str`, `tabela_destino: str`.
- **Saida:** lista de `RelationshipPath`, cada uma com tabelas, relationships, confidence e score.
- **Finalidade:** encontrar caminhos de candidatos de confidence MEDIUM/HIGH ou todos quando configurado internamente para LOW.
- **Restricoes:** caminho e descritivo; nao autoriza JOIN nem SQL por si so.
- **Erros/bloqueios:** tabela ausente ou `PathNotFoundError` quando nao ha caminho confiavel.
- **Evidencia:** `RelationshipEngine.find_paths`, testes de paths e SPEC-004/SPEC-009.

### FR-007 — `atualizar_catalogo`

- **Entrada:** nenhuma.
- **Saida:** `CatalogChange` com contagens anterior/atual, added, removed, schemas_changed, new_relationships, timestamp e errors.
- **Finalidade:** reler XLSX, detectar mudancas de schema e recalcular candidatos.
- **Restricoes:** XLSX permanece read-only; metadata nao e regravada; nomes logicos duplicados sao invalidos.
- **Erros/bloqueios:** erros de leitura podem ser agregados no modo nao estrito; metadata/relacionamentos invalido falha na inferencia.
- **Evidencia:** `test_catalog.py::test_dynamic_add_remove_schema_and_timestamp`, server e testes de relacionamento.

### FR-008 — `status_catalogo`

- **Entrada:** nenhuma.
- **Saida:** `CatalogStatus` com file_count, table_count, total_columns, loaded_at, tables e relationship_count.
- **Finalidade:** fornecer estado observavel do catalogo.
- **Restricoes:** representa headers catalogados, nao qualidade ou verdade dos dados.
- **Erros/bloqueios:** depende da inicializacao do catalogo.
- **Evidencia:** smoke MCP, `Catalog.status`.

### FR-009 — `gerar_sql`

- **Entrada:** `tabelas: list[str]`, `colunas?: list[str]`, `filtros?: list[FilterCondition]`, `permitir_baixa_confianca?: bool`, `grain?: list[str]`.
- **Saida:** `SqlGenerationResult` com `sql`, `parameters`, `warnings` e relationships usados.
- **Finalidade:** gerar SELECT Oracle parametrizado para uma ou varias tabelas.
- **Restricoes:** tabelas unicas; colunas qualificadas quando ambiguas; multi-tabela exige relationship APPROVED sem conflitos; `grain` pertence a primeira tabela; join usa LEFT JOIN.
- **Erros/bloqueios:** tabela/coluna inexistente, ambiguidade, filtro invalido, relacionamento ausente, INFERRED/KNOWN/sem authority, conflito, confidence LOW nao permitida, cardinalidade/grain insuficiente ou key ausente. Nenhum SQL parcial e emitido no bloqueio de grain.
- **Evidencia:** `SQLGenerator.generate`, `test_sql_generator.py`, `test_server.py`, EVIDENCE-007, SPEC-009 e SPEC-010/011.

### FR-010 — `gerar_select`

- **Entrada:** `tabela: str`, `colunas?: list[str]`.
- **Saida:** `SqlGenerationResult` para uma tabela.
- **Finalidade:** atalho de SELECT single-table.
- **Restricoes:** nao exige relationship authority por nao haver JOIN; ainda valida tabela e colunas.
- **Erros/bloqueios:** `TableNotFoundError`, `ColumnNotFoundError` ou ambiguidade aplicavel.
- **Evidencia:** `SQLGenerator.generate_select`, testes de single-table.

### FR-011 — `gerar_join`

- **Entrada:** `tabela_origem: str`, `tabela_destino: str`.
- **Saida:** relationship serializado, `grain_preservation`, `automatic_join`, `automatic_join_allowed`, e `sql_sugerido` somente quando permitido; caso contrario `blocked_reason`.
- **Finalidade:** descrever um JOIN candidato sem transformar bloqueio em SQL executavel.
- **Restricoes:** somente APPROVED sem conflitos permite `automatic_join=ALLOWED`; endpoints compostos emitem todos os pares posicionais.
- **Erros/bloqueios:** tabela ausente, relacionamento ausente, authority insuficiente, conflitos e grain bloqueado.
- **Evidencia:** `server.py`, `test_server.py`, SPEC-009, SPEC-010 e SPEC-011.

### FR-012 — `explicar_sql`

- **Entrada:** `sql: str`.
- **Saida:** dicionario com tabelas, aliases, colunas selecionadas, joins, filtros, `possui_cte`, `possui_agregacao` e observacao de analise sintatica.
- **Finalidade:** explicar conservadoramente uma consulta sem executa-la.
- **Restricoes:** nao valida semantica Oracle, nao acessa banco, nao gera SQL.
- **Erros/bloqueios:** `ForbiddenSQLOperationError` se nao iniciar por SELECT/WITH ou se contiver operacao proibida.
- **Evidencia:** `sql_explainer.py`, testes SQL e EVIDENCE-007.

## 7. Contrato de catalogo e comportamento XLSX

### 7.1 Descoberta

Cada arquivo `*.xlsx` em `DATA_ENGINEERING_MCP_DATA_DIR` e tratado como uma tabela logica. O nome remove extensao, prefixo `rawzn.` e sufixo `_SINTETICO`, com comparacao case-insensitive e resultado em uppercase. O workbook e lido com `read_only=True` e `data_only=True`. A primeira worksheet nao chamada `SQL` que possua headers utilizaveis e escolhida.

Headers sao trimados, convertidos para uppercase, recebem posicao 1-based e nao podem ser duplicados. Linhas de dados nao participam da descoberta do schema. Workbook invalido ou sem cabecalho gera `InvalidWorkbookError`, `NoValidWorksheetError` ou `MissingHeaderError` conforme o caso.

### 7.2 Atualizacao

`Catalog.load` compara estado anterior e novo, informa tabelas adicionadas/removidas, schemas alterados, timestamp e erros. `atualizar_catalogo` entao reexecuta inferencia e conta identidades novas usando endpoints completos, simples ou compostos. O catalogo nao escreve nos XLSX.

### 7.3 Estado observado da baseline

No smoke final foram observadas 11 tabelas, 468 colunas e 300 candidatos de relacionamento no diretorio `data/` local. Esses numeros sao evidencias do ambiente da baseline, nao limites arquiteturais do produto.

## 8. Contrato de metadata

O arquivo configuravel por `DATA_ENGINEERING_MCP_RELATIONSHIPS_FILE` e, por padrao, `metadata/relationships.json`. O schema raiz contem `relationships` e opcionalmente `keys`. O arquivo legado `{"relationships": []}` permanece valido. JSON invalido, campos extras, endpoints inexistentes, listas vazias, duplicatas, fontes vazias ou decisions incompletas falham closed.

O runtime le metadata; nao cria, atualiza ou homologa fatos automaticamente. A fonte real presente na baseline permaneceu inalterada e seu ultimo hash verificado foi `E020F99FF944B9ACA3DFC8B45D714ECB1CF9116F959BEFDCDFA03EFC82478B17`.

## 9. Autoridade INFERRED / KNOWN / APPROVED

| Autoridade | Significado | Permissao |
|---|---|---|
| `INFERRED` | candidato produzido pela heuristica nominal | descritivo; nao permite JOIN automatico |
| `KNOWN` | declaracao de fonte explicita identificavel | descritivo/metadata; nao permite JOIN automatico |
| `APPROVED` | declaracao aceita com `RelationshipDecision` completa | pode sustentar JOIN, ainda sujeita a conflitos, cardinalidade e grain |

`RelationshipDecision` exige `id`, `date` e `decided_by = HUMAN/Product Owner`. Nenhum score, repeticao, confidence ou uso anterior promove authority. Relacionamento, cardinalidade e key possuem autoridades independentes.

## 10. Keys, PK, UNIQUE e chaves compostas

`ExplicitKey` exige `table`, `columns[]`, `kind`, `source`, `authority` e opcionalmente `decision`. `kind` e `PRIMARY_KEY` ou `UNIQUE`. `columns[]` e nao vazia, sem duplicatas, preserva ordem e referencia colunas existentes.

Keys podem ser simples (`["ID"]`) ou compostas (`["ID", "VERSAO"]`). `APPROVED` exige decision HUMAN; `KNOWN` nao aceita decision. A engine agrupa por tabela e tupla ordenada de colunas, preserva conflitos de declarations e nao inventa unicidade.

## 11. Relacionamentos simples e compostos

### 11.1 Persistencia e normalizacao

O formato legado simples e:

```json
{"source_column":"ID_B", "target_column":"ID_B"}
```

O formato aditivo canonico e:

```json
{"source_columns":["ID_B","VERSAO_B"], "target_columns":["ID_B","VERSAO_B"]}
```

A entrada deve usar o par escalar completo ou o par de listas completo. Listas sao nao vazias, do mesmo tamanho, sem identificadores duplicados e com ordem posicional preservada. A forma legada e normalizada internamente para listas unitarias. Listas unitarias sao equivalentes ao legado; relacionamentos compostos nao fingem possuir um unico par escalar.

### 11.2 Identidade, merge e caminhos

A identidade inclui as duas tabelas e as duas listas completas ordenadas. Orientacao inversa troca endpoints sem ordenar internamente as colunas. Declarations distintas, conflicts, paths, refresh e serializacao transportam a identidade completa. A heuristica continua apenas single-column; uma coincidencia parcial nao invalida sozinha um composto explicito, mas divergencia real permanece conflito.

### 11.3 SQL composto

Para um relationship composto, o `ON` contem um predicado `=` por par posicional, unido por `AND`, na ordem declarada. Nao ha truncamento para um par e nao ha deduplicacao automatica.

## 12. Cardinalidade e autoridades independentes

Valores aceitos: `ONE_TO_ONE`, `MANY_TO_ONE`, `ONE_TO_MANY`, `MANY_TO_MANY`, `UNKNOWN`. Cardinalidade tem `cardinality_source`, `cardinality_authority`, `cardinality_decision` e conflicts proprios.

Para preservar grain a partir da tabela corrente, somente cardinalidade orientada `MANY_TO_ONE` ou `ONE_TO_ONE`, com autoridade suficiente e sem conflicts, pode passar. O lado alcancado deve possuir key `PRIMARY_KEY` ou `UNIQUE` exatamente igual, na mesma ordem, ao endpoint alcancado. A existencia de relationship aprovado nao promove cardinalidade; a key nao promove relationship; nenhuma autoridade e inferida pela outra.

## 13. Query intent

`QueryIntent` e um contrato interno declarativo e serializavel. Seus sete elementos sao:

1. `sources`;
2. `output_columns` com `field` e alias opcional;
3. `filters` com `field`, `operator`, `value` ou referencia a outro campo;
4. `relationships` com identity, authority e conflicts;
5. `grain` opcional;
6. `warnings`;
7. `authority_pending`.

O modelo e estrito (`extra="forbid"`), exige value ou reference nos filtros e mantem gaps de autoridade explicitos. Ele nao descobre paths, promove authority, gera SQL ou executa SQL. A evidencia esta em `tests/test_query_intent.py`.

## 14. Grain e grain preservation

`grain` em `gerar_sql` deve pertencer a primeira tabela solicitada. Quando informado, todo JOIN deve provar, cumulativamente:

1. relationship `APPROVED` e sem conflicts;
2. cardinalidade orientada `MANY_TO_ONE` ou `ONE_TO_ONE`;
3. autoridade de cardinalidade presente e sem conflicts;
4. key `PRIMARY_KEY` ou `UNIQUE` no lado alcancado;
5. igualdade exata e ordenada entre endpoint alcancado e `ExplicitKey.columns`.

Ausencia, subconjunto, superconjunto, ordem diferente, autoridade insuficiente ou conflito resulta em `BLOCKED`, sem SQL parcial. A engine nao usa `DISTINCT`, `GROUP BY` artificial, `ROW_NUMBER`, arbitragem ou filtros inventados para mascarar multiplicacao ou desconhecimento.

## 15. Geracao e explicacao de Oracle SQL

O SQLGenerator produz somente estrutura `SELECT` com `FROM`, `LEFT JOIN`, `WHERE` e bind variables. Operadores de filtro aceitos: `=`, `<>`, `>`, `>=`, `<`, `<=`, `IN`, `IS NULL`, `IS NOT NULL`, `LIKE`. Valores sao mantidos em `parameters` e nao concatenados no SQL.

Consultas single-table permanecem disponiveis sem relationship authority. Consultas multi-table precisam de relationships aceitaveis e, quando grain e exigido, de prova de preservacao. `permitir_baixa_confianca` nao contorna authority, conflicts ou demais gates.

`explicar_sql` remove comentarios de forma conservadora, identifica FROM/JOIN, aliases, colunas, filtros, CTE e agregacoes; nao executa e nao afirma validade semantica.

## 16. Seguranca e fail-closed

### SEC-001 — somente leitura de fontes

XLSX e metadata sao lidos localmente; o runtime nao executa SQL nem escreve nos XLSX.

### SEC-002 — superficie SQL restrita

Somente SELECT/WITH estruturado e aceito; operacoes destrutivas sao rejeitadas pelo explainer e nao existem nas tools de geracao.

### SEC-003 — parametrizacao

Filtros usam bind variables; valores nao sao interpolados no SQL.

### SEC-004 — autoridade obrigatoria

INFERRED, KNOWN, ausente ou conflitante nunca autorizam JOIN automatico.

### SEC-005 — erro legivel no boundary

Falhas de dominio em `gerar_sql` chegam como erro de tool legivel; excecoes inesperadas nao expoem mensagem sensivel no teste MCP.

### SEC-006 — fail-closed de grain

Sem key, cardinalidade, autoridade ou correspondencia exata, o SQL multi-tabela com grain nao e emitido.

### SEC-007 — sem mascaramento

Nao usar `DISTINCT`, deduplicacao, agregacao artificial, filtros inventados ou arbitragem para ocultar falta de prova.

### SEC-008 — conflito visivel

Conflicts permanecem no payload e bloqueiam o uso automatico quando relevante.

### SEC-009 — ausencia de autoridade nao e aprovacao

`UNKNOWN`, `INFERRED` e `KNOWN` permanecem diferentes de `APPROVED`.

### SEC-010 — sem autoridade semantica por nome

Matching de nome e somente heuristica; nao prova relacionamento, key ou cardinalidade.

### SEC-011 — nenhuma integracao externa implicita

Sem credenciais, banco, rede, Power BI ou Figma obrigatorios para inicializar o MCP.

### SEC-012 — preservacao de baseline

A implementacao aceita preservou metadata real, datasets e alteracoes locais preexistentes; nao houve commit, push, release ou publicacao nesta etapa documental.

## 17. Persistencia e compatibilidade retroativa

- `metadata/relationships.json` legado vazio continua valido;
- relationships simples com `source_column`/`target_column` continuam validos;
- listas unitarias sao equivalentes sem migracao manual obrigatoria;
- listas compostas sao aditivas e preservam ordem;
- campos escalares publicos permanecem para relacionamentos simples;
- exatamente 12 tools sao preservadas;
- nenhuma regravacao automatica do metadata ocorre.

## 18. Integracoes e fronteiras

### Pertence ao MCP

- MCP SDK e transporte stdio;
- catalogo XLSX local;
- metadata declarativa local;
- query intent interno;
- geracao e explicacao de SQL Oracle sem execucao;
- skill externa `data-engineering-spec-driven` como capacidade de intake e especificacao;
- smoke/testes locais.

### Nao pertence ao runtime MCP

- Power BI Desktop/MCP, PBIP/PBIR, Figma e design visual;
- banco Oracle ou qualquer banco remoto;
- projetos consumidores e seus handoffs;
- publicacao, gateway, workspace, deploy, release;
- uma futura interface de ingestao/homologacao de metadata.

SPEC-007 e SPEC-008 validaram fronteiras praticas com capacidades externas quando autorizadas; isso nao torna Power BI uma dependencia do servidor MCP.

## 19. Requisitos nao funcionais

### NFR-001 — determinismo

Listas, nomes, paths, identidades e ordenacoes relevantes sao deterministicas.

### NFR-002 — offline/local

O runtime funciona com fontes e metadata locais e nao depende de banco remoto.

### NFR-003 — auditabilidade

Autoridade, fonte, decision, conflicts, warnings, keys e cardinalidade permanecem observaveis.

### NFR-004 — compatibilidade

O formato simples legado e as 12 tools sao preservados por evolucao aditiva.

### NFR-005 — fail-closed

Incerteza relevante bloqueia em vez de produzir SQL potencialmente incorreto.

### NFR-006 — extensibilidade generica

Adicionar tabela local nao requer codigo especifico da tabela.

### NFR-007 — observabilidade

`status_catalogo`, errors, warnings e payloads fornecem estado operacional observavel.

### NFR-008 — baixo acoplamento

Query intent e skill nao duplicam gerador SQL, autoridade ou orquestracao.

### NFR-009 — reversibilidade documental

A atividade atual alterou somente documentacao e handoff, sem migracao, deploy ou efeito externo.

### NFR-010 — ambiente declarado

Requisitos e comandos de reproducao estao declarados em `pyproject.toml`, README e nesta especificacao.

## 20. Historico resumido e decisoes HUMAN

| Spec | Resultado aceito | Decisao/entrega verificavel |
|---|---|---|
| SPEC-001 | ACCEPTED / DONE | G1/G2/G4 estabeleceram metodologia spec-driven, gates, evidencias e governanca. |
| SPEC-002 | ACCEPTED / DONE | G1/G2/G4 introduziram metadata, authorities INFERRED/KNOWN/APPROVED, persistence e conflitos. |
| SPEC-003 | ACCEPTED / DONE | G1/G2/G4 introduziram QueryIntent declarativo, sem gerar/executar SQL. |
| SPEC-004 | ACCEPTED / DONE | G1/G2/G4 consolidaram safety gate, SQL parametrizado e fail-closed de JOIN. |
| SPEC-005 | ACCEPTED / DONE | G1/G2/G4 aceitaram a skill externa de intake/discovery/specs proporcionais; nao e segundo orquestrador. |
| SPEC-006 | ACCEPTED / DONE | HUMAN aceitou o Construction Orchestrator contratual em `AGENTS.md`; PLAN separado nao foi criado. |
| SPEC-007 | ACCEPTED / DONE | G1/G2/G3/G4 validaram modos SQL-only, BI novo e BI existente dentro das fronteiras praticas. |
| SPEC-008 | ACCEPTED / DONE | G1/G2/G3/G4 validaram cadeia local XLSX -> modelo -> visual -> renderizacao real Desktop, com evidencia final. |
| SPEC-009 | ACCEPTED / DONE | G1/G2/G4 fecharam bypass de JOIN; bloqueios chegam ao boundary MCP sem SQL parcial. |
| SPEC-010 | ACCEPTED / DONE | G1/G2/G4 introduziram PK/UNIQUE, keys compostas, cardinalidade e grain preservation. |
| SPEC-011 | ACCEPTED / DONE | G1/G2/G4 introduziram relationships compostos posicionais, preservacao de compatibilidade e SQL composto. |

A decisao final posterior foi: `HUMAN FINAL PRODUCT ACCEPTANCE -> APPROVED` e `DATA ENGINEERING MCP v0.1.0 -> OPERATIONAL / DEVELOPMENT CLOSED`.

## 21. Criterios de verificacao e reproducao para auditor

### 21.1 Testes automatizados

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado da baseline final documentada: **82 tests PASS**.

### 21.2 Smoke MCP

```powershell
.\.venv\Scripts\python.exe scripts\smoke_test.py
```

Resultado verificado:

- servidor `data-engineering-mcp`, versao `0.1.0`;
- exatamente 12 tools;
- `listar_tabelas` e `status_catalogo` sem erro;
- ambiente observado: 11 tabelas, 468 colunas e 300 candidatos.

### 21.3 Integridade documental e metadata

```powershell
git diff --check
Get-FileHash metadata\relationships.json -Algorithm SHA256
```

Resultados verificados:

- `git diff --check`: PASS, com avisos informativos LF/CRLF preexistentes;
- metadata hash: `E020F99FF944B9ACA3DFC8B45D714ECB1CF9116F959BEFDCDFA03EFC82478B17`;
- nenhuma alteracao de runtime e comportamento foi feita por esta atividade documental.

### 21.4 Evidencias de integracao

- `specs/EVIDENCE-007-integrated-practical-mode-validation.md`: casos SQL-only, BI novo e BI existente, com fronteiras e limitacoes registradas;
- `specs/EVIDENCE-008-local-power-bi-end-to-end-validation.md`: modelo Import, 40 linhas, pagina/visual unicos, bindings e screenshot real Desktop;
- `specs/fixtures/SPEC-008-end-to-end/`: PBIP/PBIR/TMDL controlado;
- `specs/evidence/SPEC-008/desktop-prova-e2e.png`: renderizacao real observada.

## 22. Matriz de rastreabilidade

Status possiveis na matriz combinam os marcadores definidos na secao 1.

| ID | Requisito | SPEC | Implementacao/componente | Teste/evidencia | Status |
|---|---|---|---|---|---|
| FR-001 | Descobrir e listar tabelas XLSX | 001, 002, 007 | `catalog.py`, `listar_tabelas` | `test_catalog.py`, smoke | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-002 | Descrever tabela, colunas e keys | 002, 007 | `catalog.py`, `server.py` | `test_catalog.py`, `test_server.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-003 | Buscar coluna exata | 001, 007 | `Catalog.find_column`, tool | `test_catalog.py`, smoke | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-004 | Buscar tabelas parcialmente | 001, 007 | `Catalog.search_tables`, tool | `test_catalog.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-005 | Expor candidates e authority | 002, 009, 011 | `RelationshipEngine`, tool | `test_relationships.py`, EVIDENCE-007 | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-006 | Encontrar paths descritivos | 002, 004 | `find_paths`, tool | `test_relationships.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-007 | Atualizar catalogo e detectar schema | 001, 002, 011 | `Catalog.load`, `atualizar_catalogo` | `test_catalog.py`, `test_server.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-008 | Expor status do catalogo | 001, 007 | `Catalog.status`, tool | smoke | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-009 | Gerar SQL Oracle parametrizado | 003, 004, 009, 010, 011 | `SQLGenerator`, `gerar_sql` | `test_sql_generator.py`, EVIDENCE-007 | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-010 | Gerar SELECT single-table | 003, 004 | `generate_select`, tool | `test_sql_generator.py`, `test_server.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-011 | Descrever/bloquear/permitir JOIN | 002, 004, 009, 011 | `gerar_join`, `RelationshipEngine` | `test_server.py`, EVIDENCE-007 | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-012 | Explicar SELECT/WITH sem executar | 003, 004 | `sql_explainer.py`, tool | `test_sql_generator.py`, EVIDENCE-007 | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-013 | Representar QueryIntent | 003, 005 | `query_intent.py` | `test_query_intent.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-014 | Representar keys simples/compostas | 010, 011 | `ExplicitKey`, `KeyConstraint` | `test_relationships.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-015 | Representar relationships simples/compostos | 011 | `ExplicitRelationship`, engine | `test_relationships.py`, `test_sql_generator.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-016 | Preservar grain ou bloquear | 010, 011 | `grain_preservation`, SQLGenerator | `test_sql_generator.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-017 | Manter skill de intake proporcional | 005, 007 | `SKILL.md` | matriz 17/17, EVIDENCE-007 | IMPLEMENTED / VERIFIED / ACCEPTED |
| FR-018 | Validar fronteira local pratica | 007, 008 | fixtures/evidence externas ao runtime | EVIDENCE-007/008 | VERIFIED / ACCEPTED; sem ser tool runtime |
| TR-001 | Expor exatamente 12 tools stdio | 001, 006, 007 | `server.py`, MCPServer | smoke, `test_server.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| TR-002 | Ler XLSX read-only | 001, 007 | `Catalog._read_schema` | `test_catalog.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| TR-003 | Metadata JSON estrita | 002, 011 | Pydantic models, engine | `test_relationships.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| TR-004 | Persistencia retrocompativel | 002, 011 | normalizacao em `models.py` | relationship tests | IMPLEMENTED / VERIFIED / ACCEPTED |
| TR-005 | Endpoints compostos posicionais | 011 | models/engine/generator/server | composite tests | IMPLEMENTED / VERIFIED / ACCEPTED |
| TR-006 | Cardinalidade independente | 010, 011 | models/engine | grain/cardinality tests | IMPLEMENTED / VERIFIED / ACCEPTED |
| TR-007 | QueryIntent estrito e serializavel | 003 | `query_intent.py` | `test_query_intent.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| TR-008 | Geracao sem execucao | 003, 004 | `SQLGenerator`, server | SQL tests, smoke | IMPLEMENTED / VERIFIED / ACCEPTED |
| TR-009 | Atualizacao de catalogo deterministica | 001, 011 | Catalog/server | `test_catalog.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| TR-010 | Sem hardcode HAP | 001, 011 | arquitetura data-driven | diff, testes genericos | VERIFIED / ACCEPTED |
| TR-011 | Skill desacoplada | 005 | `SKILL.md` fora de `src` | EVIDENCE-007, matriz 17/17 | IMPLEMENTED / VERIFIED / ACCEPTED |
| TR-012 | Integridade da metadata real | 002, 010, 011 | `metadata/relationships.json` | SHA-256, PLANs | VERIFIED / ACCEPTED |
| TR-013 | Compatibilidade MCP simples | 002, 009, 011 | payloads/server | `test_server.py`, smoke | IMPLEMENTED / VERIFIED / ACCEPTED |
| TR-014 | Erros de dominio legiveis | 001, 004, 009 | exceptions/server | `test_server.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| TR-015 | SQL composto completo | 011 | `SQLGenerator`, `gerar_join` | composite SQL tests | IMPLEMENTED / VERIFIED / ACCEPTED |
| TR-016 | Baseline local reproduzivel | 001..011 | pyproject, README, scripts | pytest, smoke, diff-check | VERIFIED / ACCEPTED |
| SEC-001 | Somente SELECT/WITH | 004, 009 | explainer/generator | SQL/security tests | IMPLEMENTED / VERIFIED / ACCEPTED |
| SEC-002 | Bind variables | 004 | `SQLGenerator` | `test_parameterized_filter` | IMPLEMENTED / VERIFIED / ACCEPTED |
| SEC-003 | JOIN fail-closed por authority | 002, 004, 009 | `_require_approved_relationship` | `test_sql_generator.py`, EVIDENCE-007 | IMPLEMENTED / VERIFIED / ACCEPTED |
| SEC-004 | Grain fail-closed | 010, 011 | `grain_preservation` | grain tests, EVIDENCE-008 | IMPLEMENTED / VERIFIED / ACCEPTED |
| SEC-005 | Nao mascarar incerteza | 001, 004, 009, 010 | regras SQL/engine | blocked SQL tests | IMPLEMENTED / VERIFIED / ACCEPTED |
| SEC-006 | Nao promover authority por score | 002, 011 | engine/models | relationship tests | IMPLEMENTED / VERIFIED / ACCEPTED |
| SEC-007 | Nao executar banco/rede | 001, 004 | arquitetura MCP | README, smoke, EVIDENCE | IMPLEMENTED / VERIFIED / ACCEPTED |
| SEC-008 | Metadata errors fail-closed | 002, 010, 011 | Pydantic/engine | invalid metadata tests | IMPLEMENTED / VERIFIED / ACCEPTED |
| SEC-009 | Nao expor erro sensivel inesperado | 009 | MCP boundary | `test_server.py` | IMPLEMENTED / VERIFIED / ACCEPTED |
| SEC-010 | Preservar 12 tools/contratos simples | 002, 009, 011 | server/models | tool count/schema tests | IMPLEMENTED / VERIFIED / ACCEPTED |
| SEC-011 | Nao alterar metadata automaticamente | 002, 010, 011 | engine read path | hash, PLANs | VERIFIED / ACCEPTED |
| SEC-012 | Nao publicar/release por gates implicitos | 006, todos | processo/AGENTS | handoff, PLANs | VERIFIED / ACCEPTED |
| NFR-001 | Determinismo | 001, 002, 011 | sorting/identity | tests, smoke | IMPLEMENTED / VERIFIED / ACCEPTED |
| NFR-002 | Operacao local/offline | 001, 007, 008 | catalog/server | smoke, EVIDENCE-008 | IMPLEMENTED / VERIFIED / ACCEPTED |
| NFR-003 | Auditabilidade de authority/conflicts | 002, 009, 011 | models/server | relationship/server tests | IMPLEMENTED / VERIFIED / ACCEPTED |
| NFR-004 | Compatibilidade aditiva | 002, 011 | models/server | regression/composite tests | IMPLEMENTED / VERIFIED / ACCEPTED |
| NFR-005 | Fail-closed | 004, 009, 010, 011 | SQL/engine | 82 tests, EVIDENCE-007/008 | IMPLEMENTED / VERIFIED / ACCEPTED |
| NFR-006 | Genericidade | 001, 011 | catalog/engine | generic fixtures, review | VERIFIED / ACCEPTED |
| NFR-007 | Observabilidade | 001, 007 | status/errors/smoke | smoke, tests | IMPLEMENTED / VERIFIED / ACCEPTED |
| NFR-008 | Baixo acoplamento | 003, 005, 006 | query_intent/skill/AGENTS | tests, docs | VERIFIED / ACCEPTED |
| NFR-009 | Reversibilidade/sem efeitos externos | 006..011 | local files only | handoff/PLANs | VERIFIED / ACCEPTED |
| NFR-010 | Reproducao documentada | 001..011 | pyproject/README/scripts | commands above | VERIFIED / ACCEPTED |

**Cobertura da matriz:** 18 requisitos funcionais, 16 tecnicos, 12 de seguranca e 10 nao funcionais; 56/56 IDs possuem linha de rastreabilidade e estado explicito.

## 23. Limitacoes conhecidas

1. A heuristica de relacionamentos e nominal e pode gerar falsos positivos ou negativos semanticos.
2. Metadata explicita e declarativa; nao e validacao fisica de PK/FK/cardinality no banco.
3. O MCP nao le valores dos XLSX para provar unicidade ou cardinalidade.
4. O runtime nao tem canal operacional MCP para cadastrar/homologar metadata; a manutencao atual e manual em JSON.
5. `explain_sql` e sintatico e nao garante validade semantica Oracle.
6. Candidatos MEDIUM/LOW sao inferencias; nao sao confirmacoes.
7. O comportamento e local/offline e nao inclui execucao ou publicacao.
8. A disponibilidade de Power BI/Figma varia por ambiente e nao altera o contrato do runtime.
9. A skill depende do julgamento de linguagem natural e de capacidades externas disponiveis para trabalhos consumidores.
10. O interpretador global pode nao ter `mcp`; a reproducao validada usa `.venv`.

## 23.1 Gaps de evidencia documental

`specs/EVIDENCE-007-integrated-practical-mode-validation.md` preserva, em sua secao final, o estado intermediario `STOP_HUMAN — G4 PENDING`. O `PLAN-007`, a `SPEC-007` e o `PROJECT_HANDOFF.txt` registram posteriormente o G4 aprovado, os 7/7 criterios aceitos e o encerramento. Esta e uma discrepancia de sincronizacao historica do artefato de evidencia, nao uma discrepancia do runtime ou da decisao final HUMAN. Ela fica registrada para auditoria e nao e tratada como capacidade implementada nem como blocker funcional.

## 24. RESIDUAL_RISK

O risco residual principal e a **ingestao/homologacao operacional de metadata ainda manual**. Para usar uma relacao, key ou cardinalidade que nao esteja no arquivo local, alguem precisa fornecer/editar `metadata/relationships.json` com autoridade, fonte e, quando aplicavel, decision HUMAN. Sem isso, a inferencia permanece `INFERRED` ou `UNKNOWN` e joins automaticos permanecem bloqueados. Esse comportamento e intencionalmente fail-closed e foi aceito no G4; nao e capacidade faltante dentro do escopo fechado.

Outros riscos residuais aceitos: semantica nominal da heuristica, representacoes locais de banco incompletas ou stale, ausencia de validacao fisica no banco e variacao de capacidades Power BI/Figma em projetos consumidores.

## 25. BACKLOG

- Avaliar uma interface/canal operacional de ingestao e homologacao de metadata somente apos INSPECT separado demonstrar necessidade concreta.
- Qualquer futura mudanca deve definir autoridade, contrato, auditabilidade, rollback, permissao e criterios antes de criar Spec/PLAN.
- Nao e uma capacidade v0.1.0, nao foi implementada, nao foi verificada e nao esta autorizada.

## 26. Criterios de mudanca e governanca futura

1. Toda mudanca de objetivo, escopo, nao-escopo, criterio, contrato publico ou risco material exige decisao HUMAN registrada.
2. Nova capacidade deve passar por INSPECT e classificacao proporcional; nao criar SPEC automaticamente por backlog.
3. Um unico trabalho deve estar ativo por vez, salvo decisao HUMAN explicita.
4. Mudancas de runtime, tools, metadata schema, dependencias ou integracoes precisam de PLAN com arquivos e orcamento.
5. Quebra de contrato publico, migracao ou release exige G5 e autorizacao especifica.
6. Implementacao exige G2; verificacao e evidencias precedem G4.
7. O handoff registra continuidade; esta especificacao deve ser atualizada somente quando o produto aceito mudar ou quando uma correcao documental for necessaria.
8. Commit, push, release, deploy e publicacao nao sao implicados por G4 ou por readiness.
9. A baseline final deve continuar reproduzivel por pytest, smoke, diff-check e evidencias aplicaveis.
10. Discrepancias entre documentacao e implementacao devem ser registradas e interromper a declaracao de readiness ate reconcilacao; nunca corrigidas silenciosamente.

## 27. Estado final

```text
DATA ENGINEERING MCP v0.1.0
OPERATIONAL
DEVELOPMENT CLOSED
HUMAN FINAL PRODUCT ACCEPTANCE: APPROVED
```

### Classificacao final

- **IMPLEMENTED:** runtime Python, 12 tools, catalogo, metadata models, relationships simples/compostos, keys, cardinalidade, grain gates, SQL, explainer, QueryIntent e skill.
- **VERIFIED:** 82 testes, smoke com 12 tools, diff-check, hash de metadata, testes especificos, evidencias praticas e E2E local documentado.
- **ACCEPTED:** SPEC-001..SPEC-011, seus PLANs aplicaveis, gates G4 e aceite final HUMAN.
- **RESIDUAL_RISK:** ingestao/homologacao de metadata manual e demais limitacoes listadas.
- **BACKLOG:** possivel canal operacional de metadata e somente futuras necessidades comprovadas.

---

## Apendice A — Fontes auditadas

- `PROJECT_HANDOFF.txt` (handoff portatil MCP no worktree; referido normativamente como `PROJECT_HANDOFF_MCP.txt`);
- `AGENTS.md`;
- `README.md`;
- `pyproject.toml`;
- `src/data_engineering_mcp/*.py`;
- `tests/*.py`;
- `scripts/smoke_test.py`;
- `data-engineering-spec-driven/SKILL.md`;
- `metadata/relationships.json`;
- `specs/SPEC-001` a `specs/SPEC-011`;
- `specs/PLAN-001` a `specs/PLAN-011` aplicaveis;
- `specs/EVIDENCE-007-integrated-practical-mode-validation.md`;
- `specs/EVIDENCE-008-local-power-bi-end-to-end-validation.md`;
- `specs/fixtures/SPEC-007-existing-bi/`;
- `specs/fixtures/SPEC-008-end-to-end/`;
- `specs/evidence/SPEC-008/desktop-prova-e2e.png`.

## Apendice B — Nota de auditoria

Este documento nao afirma que o MCP executa banco, materializa BI ou cadastra metadata operacionalmente. As evidencias de Power BI documentam validacoes praticas externas e fronteiras de integracao; a implementacao do runtime MCP permanece local, offline e sem dependencia obrigatoria dessas capacidades.
