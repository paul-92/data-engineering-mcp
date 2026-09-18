# EVIDENCE-007 — Integrated Practical Mode Validation

## 1. Execução identificada

| Campo | Valor |
|---|---|
| Data | 2026-09-16 |
| Baseline Git | `862abae4237997bc7165b27a4fc179429ff11359` |
| Gate | G2 aprovado pelo HUMAN/Product Owner |
| Estágio alcançado | `EVIDENCE`, após recuperação G3 e execução dos três casos |
| Resultado | `AWAITING_ACCEPTANCE` — G4 pendente |

## 2. Verificações executadas

### 2.1 Data Engineering MCP

- A pasta local `data/` existe e contém onze representações XLSX, além de `.gitkeep`.
- `metadata/relationships.json` existe e contém `{"relationships": []}`, condição adequada para o subteste planejado de bloqueio de JOIN sem autoridade `APPROVED`.
- A tentativa de executar `scripts/smoke_test.py` com o Python do `.venv` iniciou o cliente MCP, mas o ambiente negou a criação do subprocesso/pipe stdio com `PermissionError: [WinError 5] Acesso negado`.
- Esta ocorrência é classificada inicialmente como limitação ambiental, coerente com os 35 testes previamente impedidos por permissões temporárias. Ela seria material para a evidência do Caso A caso não houvesse antes um bloqueio independente e suficiente nos casos Power BI.

### 2.2 Power BI local

- `Get-Command powerbi-report-author` não encontrou o CLI de autoria/validação PBIR.
- `Get-Command powerbi-desktop` não encontrou o CLI de bridge/inspeção do Power BI Desktop.
- Node.js está disponível na versão `v24.19.0`, mas instalação global ou adição de dependência não está autorizada pelo PLAN-007.
- A capacidade Power BI MCP respondeu ao inventário read-only:
  - `ListConnections`: `Found 0 connections`;
  - `ListLocalInstances`: `Found 0 local PowerBI Desktop and Analysis Services instances`.
- Uma busca de recuperação por CLI já instalado não encontrou candidato utilizável antes de ser interrompida por custo desproporcional; nenhum arquivo foi alterado por essa busca.

## 3. Comparação com o plano

O PLAN-007 exige:

1. fixture PBIP/PBIR local real e controlada para o Caso C;
2. validação do formato por capacidade Power BI, sem inventar JSON;
3. inspeção read-only real do artefato antes da proposta;
4. distinção explícita entre integração real e simulação;
5. `STOP_BLOCKED` quando Power BI não tiver capacidade read-only suficiente para o Caso B ou C.

As capacidades disponíveis não permitem criar e validar a fixture conforme as regras do skill de autoria Power BI nem inspecioná-la por CLI/Desktop. Criar PBIR manualmente sem validador, afirmar uma inspeção simulada ou instalar CLIs ampliaria estratégia, dependências/permissões ou configuração global e violaria o plano aprovado.

## 4. Preservação e efeitos

- Nenhuma fixture foi criada.
- Nenhum dos três casos foi declarado executado.
- Nenhuma spec de teste foi gerada, aprovada ou executada.
- Nenhuma instalação, dependência, configuração global, conexão externa, publicação, alteração de Power BI/Figma, commit, push ou release ocorreu.
- Runtime, tools, `data/`, `metadata/`, `src/`, `tests/`, `README.md` e a skill permaneceram intocados por esta execução.
- Mudanças locais preexistentes foram preservadas.

## 5. STOP_BLOCKED

**Razão:** dependência Power BI obrigatória para os Casos B e C indisponível dentro da autorização atual; adicionalmente, o transporte stdio do Data Engineering MCP é negado pelo ambiente.

**Último estágio seguro:** `INSPECT`/preflight após G2, antes de criar fixture ou executar casos.

**Menor decisão/alteração necessária:** disponibilizar uma capacidade local já instalada que consiga criar/validar e inspecionar PBIP/PBIR, ou autorizar explicitamente uma estratégia alternativa e seus arquivos/permissões. Para o Caso A, o ambiente também precisa permitir o subprocesso stdio do MCP ou uma estratégia real equivalente aprovada.

**Condição objetiva de retomada:** `powerbi-report-author --version` e uma capacidade read-only (`powerbi-report-author preview-*` ou instância `powerbi-desktop` conectada) devem responder com sucesso sem instalação/alteração não autorizada; o smoke MCP deve conseguir abrir o transporte stdio, ou um desvio G3 deve aprovar outra forma real de exercitar o servidor.

## 6. Decisão G3 posterior

O HUMAN aprovou a preparação controlada do ambiente real mantendo os critérios originais. Como a decisão não definiu mecanismo, caminhos ou permissões, nenhuma instalação, download, elevação ou mudança de configuração foi executada. O fluxo passou de bloqueio técnico para `STOP_HUMAN` quanto aos parâmetros operacionais mínimos da recuperação.

Posteriormente, o HUMAN aprovou explicitamente os parâmetros: download dos dois pacotes Microsoft, instalação temporária não global em `.spec-007-tools/`, execução dos CLIs e do smoke fora do sandbox na extensão necessária ao `WinError 5`, uso exclusivo nos ensaios e remoção integral ao final. O preflight pode ser repetido sem flexibilização de critérios.

## 7. Recuperação controlada do ambiente

- Pacotes instalados temporariamente e sem `-g` em `.spec-007-tools/`:
  - `@microsoft/powerbi-report-authoring-cli@latest` → CLI `powerbi-report-author` `0.1.4`;
  - `@microsoft/powerbi-desktop-bridge-cli@latest` → CLI `powerbi-desktop` `0.1.2`.
- `powerbi-report-author doctor`: `ok=true`, Node.js `24.19.0`, 57 tipos de visual e 15 VCOs carregados.
- `powerbi-desktop status`: `not_connected`, sem instância Desktop. Como o PLAN-007 aceita `powerbi-report-author preview-*` como capacidade read-only, a inspeção prosseguiu sem abrir Desktop e sem simular renderização.
- Smoke MCP fora do sandbox: PASS; servidor `data-engineering-mcp` `0.1.0`, exatamente 12 tools, 11 tabelas, 468 colunas e 300 candidatos de relacionamento.

## 8. Caso A — somente SQL

### 8.1 Pedido travado

Usar somente representações locais para descobrir uma tabela real e gerar uma consulta Oracle `SELECT/WITH` que retorne `CD_PESSOA` e `NU_CGC_CPF` de `RAW_HAP_TB_PESSOA`, filtrando `CD_PESSOA = 1`. Em seguida, tentar uma consulta entre `RAW_HAP_TB_USUARIO` e `RAW_HAP_TB_PESSOA` para comprovar o gate de autoridade.

### 8.2 Inspeção e chamadas reais

- `listar_tabelas`: 11 tabelas retornadas.
- `descrever_tabela("RAW_HAP_TB_PESSOA")`: fonte `RAW_HAP_TB_PESSOA_SINTETICO.xlsx`, 24 colunas; `CD_PESSOA` e `NU_CGC_CPF` confirmadas.
- `QueryIntent.to_dict()`: uma fonte, duas colunas, filtro `= 1`, grain `CD_PESSOA`, sem relacionamento ou autoridade pendente.
- `gerar_sql` para uma tabela: sucesso, sem warnings e sem relacionamento.
- `explicar_sql`: uma tabela, alias `htp`, duas colunas, filtro parametrizado, sem JOIN, CTE ou agregação.
- `gerar_sql` para duas tabelas: bloqueio antes de SQL; log real identifica `RAW_HAP_TB_PESSOA.CD_PESSOA ↔ RAW_HAP_TB_USUARIO.CD_PESSOA`, autoridade `INFERRED` e necessidade de `APPROVED` livre de conflitos.

SQL observado:

```sql
SELECT
    htp.CD_PESSOA,
    htp.NU_CGC_CPF
FROM RAW_HAP_TB_PESSOA htp
WHERE htp.CD_PESSOA = :p1
```

Parâmetros observados: `{"p1": 1}`.

### 8.3 Spec de teste gerada pela skill

**TEST-SQL-ONLY — Consulta segura de pessoa**

- Objetivo: entregar a consulta Oracle parametrizada acima, sem executar SQL.
- Escopo: `RAW_HAP_TB_PESSOA`, colunas `CD_PESSOA` e `NU_CGC_CPF`, filtro `CD_PESSOA = 1`.
- Não-escopo: JOIN, banco direto, DDL/DML, promoção de relacionamento ou BI.
- Entrada inspecionada: XLSX local e contrato real das tools MCP.
- Execução: usar `QueryIntent`, `gerar_sql` e `explicar_sql`; preservar bind variables.
- Aceite: SQL usa `:p1`, parâmetros separados, somente uma tabela e nenhuma operação destrutiva.
- Parada: qualquer ampliação multi-tabela exige relacionamento `APPROVED` sem conflitos; `INFERRED` bloqueia.
- Quantidade: uma spec compacta, pois o entregável é local, coeso e reversível.

Resultado do caso: **PASS**.

## 9. Caso B — BI novo

### 9.1 Pedido travado

Especificar um BI local pequeno para analista operacional, usando `RAW_HAP_TB_PESSOA`, com uma página “Visão de Pessoas” e uma tabela contendo `CD_PESSOA` e `NU_CGC_CPF`. Não criar, publicar ou conectar o BI.

### 9.2 Inspeção e fronteira Power BI real

- Reutilizadas a tabela, fonte e colunas já descobertas no Caso A; nenhuma pergunta foi repetida.
- `powerbi-report-author doctor`: ambiente de autoria válido.
- `catalog describe tableEx`: visual moderno, não depreciado; role obrigatória `Values`, do tipo `GroupingOrMeasure`.
- `catalog describe cardVisual`: role obrigatória `Data` do tipo `Measure`; como não existe medida aprovada, card não foi incluído silenciosamente.
- Power BI MCP: zero conexões e zero instâncias locais; essa limitação foi preservada.
- Figma: desnecessário para esta validação estrutural pequena e, portanto, não usado.

### 9.3 Spec de teste gerada pela skill

**TEST-NEW-BI — Visão local de pessoas**

- Objetivo: criar futuramente um PBIP local de uma página para consulta operacional de pessoas.
- Escopo: página “Visão de Pessoas”; `tableEx` com `CD_PESSOA` e `NU_CGC_CPF`; título acessível; fonte local já inspecionada.
- Não-escopo: publicação, workspace, conexão a banco, relacionamento multi-tabela, medida, card, Figma ou alteração do MCP.
- Dependências: capacidade PBIR validada; etapa futura de modelo semântico local deverá ser autorizada separadamente antes da construção.
- Execução permitida futura: criar PBIP/PBIR local, confirmar bindings com metadados Power BI e validar com `powerbi-report-author`; não publicar.
- Aceite: PBIR válido; exatamente uma página; `tableEx` usa role `Values`; campos correspondem ao catálogo; nenhuma conexão externa.
- Evidência: validação CLI, preview de página/visual e diff limitado ao futuro artefato autorizado.
- Parada: ausência de modelo/binding real ou decisão de publicação exige HUMAN; não inventar conexão.
- Quantidade: uma spec compacta, pois há um único entregável local e nenhuma dependência separável já autorizada.

Resultado do caso: **PASS** até a fronteira real de integração prevista; nenhuma construção ou publicação ocorreu.

## 10. Caso C — BI existente

### 10.1 Artefato controlado

Fixture criada em `specs/fixtures/SPEC-007-existing-bi/ControlledReview.Report/` com seis arquivos PBIR:

- `.platform`;
- `definition.pbir`;
- `definition/version.json`;
- `definition/report.json`;
- `definition/pages/pages.json`;
- `definition/pages/ReportSection/page.json`.

O artefato contém uma página ativa `ReportSection`, display name “Visão Geral”, canvas `1280×720`, sem visuais, filtros ou tema e com referência local por path a um modelo não materializado. Não contém dados, credenciais ou conexão externa.

### 10.2 Validação e inspeção read-only

- Primeira validação: falhou somente pela ausência de `.platform` e `definition.pbir`; ambos foram adicionados dentro do orçamento após diagnóstico explícito.
- Validação offline final: `succeeded`, zero erros e zero warnings.
- Validação online final: `succeededWithWarnings`, zero erros e seis avisos exclusivamente porque schemas remotos não puderam ser buscados; a validação offline do próprio CLI permaneceu limpa.
- `preview-pages --with-derived`: uma página ativa, zero visuais, sem filtros.
- `preview-visuals`: lista vazia.
- `preview-filters`: lista vazia.
- `preview-themes --with-derived`: lista vazia.
- Hash/conteúdo da fixture não foi alterado durante as chamadas `preview-*`; a única mudança anterior foi a correção estrutural orientada pelo validador, antes da inspeção formal do caso.

### 10.3 Spec de teste gerada pela skill

**TEST-EXISTING-BI — Melhorar legibilidade da fixture vazia**

- Objetivo: tornar futuramente a página “Visão Geral” autoexplicativa sem alterar sua dimensão ou publicar o relatório.
- Escopo: adicionar um título textual acessível e uma breve mensagem de estado vazio; preservar página, ordem, filtros e tema atuais.
- Não-escopo: criar modelo semântico, bindings, medidas, tabela de dados, publicação, redesign amplo ou conexão externa.
- Entrada inspecionada: PBIR válido com uma página `1280×720`, zero visuais, filtros e temas.
- Execução permitida futura: consultar metadados do visual textbox, adicionar somente elementos estáticos, validar e revisar preview/render quando houver Desktop conectado.
- Aceite: página continua válida e única; mensagem comunica ausência de conteúdo/dados; nenhuma dependência externa; inspeção demonstra que filtros e tema permanecem ausentes.
- Rollback: remover somente os visuais estáticos adicionados e restaurar `pages.json/page.json` se tocados.
- Parada: qualquer visual data-bound exige modelo real e nova autorização; não inventar binding.
- Quantidade: uma spec compacta, pois a melhoria é coesa, pequena e reversível.

Resultado do caso: **PASS**; a inspeção foi real e read-only, e nenhuma melhoria foi implementada.

## 11. Verificação consolidada

| Critério | Evidência | Resultado |
|---|---|---|
| AC-P7-001 | MCP real, Source Discovery, SQL com `:p1`, explicação e bloqueio `INFERRED` | PASS |
| AC-P7-002 | Capacidades `tableEx`/`cardVisual` consultadas; uma spec gerada; nenhum BI criado/publicado | PASS |
| AC-P7-003 | Fixture PBIR validada e inspecionada por `preview-*`; proposta sem alteração do artefato durante a revisão | PASS |
| AC-P7-004 | Inspeção precedeu specs; fatos do Caso A foram reutilizados; autoridade preservada | PASS |
| AC-P7-005 | Chamadas, versões, conexão ausente e warnings distinguem fatos de limitações | PASS |
| AC-P7-006 | Entradas, método, observado e três specs integrais registrados; nenhuma executada/aprovada | PASS |
| AC-P7-007 | Mudanças limitadas aos caminhos autorizados; sem efeitos externos ou protegidos | PASS |

Verificações adicionais:

- suíte completa fora do sandbox: **48 passed em 8,78 s**;
- smoke MCP: PASS, 12 tools;
- Figma não usado por não ser necessário;
- nenhum dataset ou metadata alterado;
- nenhum commit, push, release, publicação ou instalação global;
- os 35 erros anteriores foram confirmados como limitação do sandbox: fora dele, a suíte completa passou.

## 12. Limitações e riscos residuais

- Power BI Desktop não estava conectado; não houve renderização ou screenshot. Os casos exigiam fronteira/inspeção estrutural e foram validados com o CLI PBIR real, sem alegar revisão visual renderizada.
- Schemas remotos ficaram inacessíveis ao CLI; a validação offline interna passou sem warnings, enquanto a tentativa online registrou somente `PBIR_SCHEMA_UNREACHABLE`.
- A fixture referencia um modelo local não materializado; isso foi mantido explícito e impede qualquer afirmação de binding ou renderização com dados.
- Interpretação da skill em linguagem natural continua sendo risco residual aceito na SPEC-005; entradas travadas e evidência integral reduziram variação.

## 13. Gate de saída

**STOP_HUMAN — G4 PENDING.** A execução e as evidências estão completas. Aceite final, estado `ACCEPTED/DONE` e encerramento do PLAN-007 dependem de decisão HUMAN explícita.
