# EVIDENCE-008 — Local Power BI End-to-End Validation

| Campo | Resultado |
|---|---|
| Data | 2026-09-17 |
| Estado | `PASS / G4 APPROVED` |
| Fonte | `data/RAW_HAP_TB_PRECO_PLANO_SINTETICO.xlsx` |
| SHA-256 antes/depois | `0DB05B449FD47D075D5AD8B4B3C9183F33CDC197D1B4A8274148543566D15305` |
| Desktop | Microsoft Store `2.157.1354.0` |
| Ferramentas temporárias | `powerbi-report-author 0.1.4`; `powerbi-desktop 0.1.2` em `.spec-008-tools/` |

## 1. Descoberta e entrada

O smoke do Data Engineering MCP executado fora da limitação de permissão do sandbox iniciou a versão `0.1.0`, expôs exatamente 12 tools e descobriu 11 arquivos XLSX, 468 colunas e 300 candidatos de relacionamento. A fonte aprovada permaneceu inalterada; a aba usada foi `Exportar Planilha`, limitada no modelo aos campos `CD_TABELA` e `DS_TABELA`.

## 2. Modelo materializado

O MCP de modelagem criou o modelo offline controlado, a tabela Import e a partição M apontando ao XLSX local, e exportou o TMDL para `specs/fixtures/SPEC-008-end-to-end/SPEC008.SemanticModel/definition/`. O PBIP foi aberto no Desktop real; a instância local foi encontrada em `localhost:57606` e conectada como `PBIDesktop-SPEC008-57606`.

Após refresh completo no Desktop, a inspeção ao vivo retornou:

- uma tabela `RAW_HAP_TB_PRECO_PLANO`;
- `storageMode: Import`, duas colunas e uma partição;
- `CD_TABELA` (`Int64`, `summarizeBy: None`);
- `DS_TABELA` (`String`, `summarizeBy: None`);
- `COUNTROWS('RAW_HAP_TB_PRECO_PLANO') = 40`;
- amostra DAX: `(3005, Tabela Preco Sintetica 3005)`, `(3004, Tabela Preco Sintetica 3004)`, `(3002, Tabela Preco Sintetica 3002)`, `(3001, Tabela Preco Sintetica 3001)`, `(3003, Tabela Preco Sintetica 3003)`.

Resultado: AC-002 e a materialização exigida por AC-P8-002 estão comprovados.

## 3. Relatório e binding

O artefato contém exatamente:

- uma página ativa `Prova E2E` (`ReportSectionProof`);
- um visual `tableEx` (`00000000000000000008`);
- duas projeções na role `Values`: `RAW_HAP_TB_PRECO_PLANO.CD_TABELA` e `RAW_HAP_TB_PRECO_PLANO.DS_TABELA`.

`powerbi-report-author validate` terminou com zero erros e sete warnings `PBIR_SCHEMA_UNREACHABLE`, todos relativos à indisponibilidade de schemas HTTPS; não houve diagnóstico material do PBIR. `preview-pages` e `preview-visuals` confirmaram a página e o visual únicos. A Bridge confirmou o arquivo `SPEC008.pbip` e a página `Prova E2E` na instância real.

Resultado: AC-003, AC-004, AC-P8-003 e AC-P8-004 estão comprovados.

## 4. Renderização Desktop — bloqueio

A captura solicitada pela Bridge para `ReportSectionProof` falhou com:

`BRIDGE_ERROR (-32505): Print metadata is not available.`

Foram executadas somente as recuperações previstas e reversíveis:

1. espera adicional e nova tentativa;
2. reload do PBIP pela própria Bridge;
3. novo refresh completo da tabela;
4. terceira tentativa de captura.

Todas retornaram o mesmo erro não-retentável. Durante o bloqueio, `powerbi-desktop status` permaneceu `ready`, apontou para o PBIP correto e listou a página correta. Não foi produzido PNG e nenhum preview foi apresentado como screenshot.

Resultado: AC-005 e AC-P8-005 não estão comprovados; a parada correta é `STOP_BLOCKED`, não G4.

## 5. Integridade, limites e rollback

- Fonte inalterada byte a byte pelo hash antes/depois.
- `git diff --check` aprovado, com avisos LF/CRLF preexistentes.
- Nenhuma publicação, workspace, gateway, conexão remota, credencial, instalação global, PATH/configuração permanente, commit, push ou release.
- Nenhum código do produto, dataset, metadata, Power BI MCP ou Figma foi alterado pela SPEC-008.
- `.spec-008-tools/` e o Desktop permanecem temporariamente disponíveis apenas para retomada; remover/encerrar depois da evidência final.

## 6. Condição objetiva de retomada

Retomar quando a página `Prova E2E` estiver em estado capturável pela Bridge ou quando houver uma captura real verificável da instância Desktop aberta mostrando `CD_TABELA`, `DS_TABELA` e ao menos uma linha. Não substituir por preview estrutural, screenshot simulado ou flexibilização do critério.

## 7. Recuperação G3

O controle direto da janela Power BI encontrou um modal oculto com `Referência de objeto não definida para uma instância de um objeto`. Depois de dispensá-lo, a Data View exibiu a tabela materializada com os dois cabeçalhos e linhas reais. A Report View, porém, permaneceu vazia; reload pela Bridge exibiu `Falha ao carregar o relatório`.

Isso explica o erro anterior `Print metadata is not available`: o host de impressão não recebe metadados porque a definição do relatório não carrega. O modelo e a partição continuam íntegros. A próxima correção mínima exige recriar a definição PBIR do mesmo visual e, por alterar o arquivo do visual, aguarda autorização G3 específica. Nenhuma captura da Data View foi promovida indevidamente como evidência de renderização do relatório.

## 8. Correção autorizada e evidência final

Após autorização G3 específica, a definição PBIR foi alinhada à estrutura nativa compatível com o Desktop instalado, preservando integralmente a página, o visual e os bindings aprovados. Uma segunda instância limpa abriu o PBIP; o modelo foi atualizado nessa instância e a consulta final retornou 40 linhas.

A Bridge capturou `specs/evidence/SPEC-008/desktop-prova-e2e.png` com sucesso. A revisão visual confirma:

- página real renderizada no Desktop;
- cabeçalhos `CD_TABELA` e `DS_TABELA`;
- múltiplas linhas legíveis, incluindo `3001 / Tabela Preco Sintetica 3001`;
- ausência de banner de erro no visual;
- um único visual de tabela na página.

O validate final retornou zero erros e sete warnings `PBIR_SCHEMA_UNREACHABLE`, restritos ao acesso dos schemas HTTPS e sem impacto material observado. Preview final confirmou uma página ativa `Prova E2E` e um `tableEx`.

Resultado técnico final: PASS para AC-001..007 e AC-P8-001..007. A aceitação formal foi submetida ao G4 e posteriormente aprovada conforme o registro abaixo.

## 9. Aceitação

**G4 APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** A implementação, as evidências e os riscos residuais foram aceitos. O fluxo foi encerrado sem commit, push, release ou publicação.
