# PLAN-008 — Local Power BI End-to-End Validation

| Campo | Valor |
|---|---|
| Spec | `SPEC-008` |
| Baseline | `862abae4237997bc7165b27a4fc179429ff11359`, com mudanças locais preservadas |
| Gate de entrada | G1 aprovado em 2026-09-17 pelo HUMAN/Product Owner |
| Status | `COMPLETED` |
| Implementação autorizada | Sim — G2 aprovado em 2026-09-17; execução limitada às seções 2 a 7 |

## 1. Objetivo e prova mínima

Executar uma única cadeia local, sem publicação:

`RAW_HAP_TB_PRECO_PLANO_SINTETICO.xlsx → Source Discovery → tabela importada no modelo → tableEx vinculado → validação PBIR → renderização observada no Power BI Desktop`.

A prova termina quando o mesmo artefato local demonstra, por inspeção do modelo e screenshot Desktop, que dados reais da planilha foram carregados e exibidos pelo visual. Preview estrutural, TMDL isolado ou JSON válido não substituem materialização e renderização.

## 2. Fonte, modelo e visual travados

- Fonte imutável: `data/RAW_HAP_TB_PRECO_PLANO_SINTETICO.xlsx`.
- Aba: `Exportar Planilha`.
- Tabela lógica/modelo: `RAW_HAP_TB_PRECO_PLANO`.
- Campos mínimos importados e usados no visual:
  - `CD_TABELA` — identificador numérico;
  - `DS_TABELA` — descrição textual.
- Campos adicionais não devem ser adicionados por conveniência; se o import do Desktop materializar a aba completa, a evidência deverá registrar isso como comportamento da ferramenta, enquanto o visual continuará limitado aos dois campos.
- Relatório: uma página, nome `Prova E2E`.
- Visual: exatamente um `tableEx`, com `CD_TABELA` e `DS_TABELA` na role `Values`.
- Sem título, card, slicer, tema, forma, medida, relacionamento ou refinamento visual adicional.

A escolha é proporcional: o arquivo é a menor fonte sintética disponível, e uma tabela simples comprova binding e renderização sem exigir agregação ou semântica de negócio.

## 3. Capacidades e dependências

### Já verificadas no planejamento

- Power BI Desktop Microsoft Store instalado: `Microsoft.MicrosoftPowerBIDesktop` versão `2.157.1354.0`.
- Python/`openpyxl` e Data Engineering MCP locais disponíveis.
- Fonte existente; cabeçalhos e primeira linha foram lidos em modo read-only.

### Necessárias após G2

- Data Engineering MCP: `listar_tabelas` e `descrever_tabela` para confirmar discovery sem alterar catálogo/fonte.
- Power BI Desktop real: importar XLSX em modo Import, salvar PBIP, criar/vincular o visual, salvar e renderizar.
- Power BI MCP/modeling read-only: conectar à instância Desktop, listar tabela/colunas e executar uma consulta DAX mínima que prove linhas carregadas.
- `powerbi-report-author`: validar PBIR e inspecionar página/visual/binding.
- `powerbi-desktop`: identificar instância, recarregar se necessário e capturar screenshot da página renderizada.

Se o Desktop Bridge, a conexão de modelagem, o modo PBIP, o import ou a captura real estiver indisponível, retornar `STOP_BLOCKED`; não substituir por preview, schema ou simulação.

## 4. Sequência de execução após G2

1. `INSPECT`: confirmar baseline, fonte, processos Desktop e ausência de fluxo ativo conflitante.
2. Preparar somente ferramentas temporárias não globais autorizadas na seção 5 e confirmar versões/diagnóstico.
3. Chamar o Data Engineering MCP para confirmar tabela e os dois campos; não atualizar catálogo nem fonte.
4. Abrir Power BI Desktop e criar um arquivo local em branco.
5. Importar a aba `Exportar Planilha` do XLSX por Power Query/Import, sem transformação material além de promover cabeçalhos e tipos automaticamente inferidos pelo Desktop.
6. Salvar como projeto PBIP no caminho autorizado.
7. Provar materialização conectando read-only à instância Desktop:
   - tabela `RAW_HAP_TB_PRECO_PLANO` listada;
   - colunas `CD_TABELA` e `DS_TABELA` listadas;
   - DAX `COUNTROWS('RAW_HAP_TB_PRECO_PLANO')` retorna valor maior que zero;
   - consulta DAX de amostra retorna ao menos um par não vazio dos dois campos.
8. Criar uma página `Prova E2E` e exatamente um visual `tableEx` vinculado aos dois campos; salvar.
9. Validar PBIR sem erro material e inspecionar que há uma página, um visual `tableEx` e bindings para os dois campos.
10. Recarregar/abrir o mesmo PBIP no Desktop e capturar screenshot real mostrando cabeçalhos e ao menos uma linha renderizada sem erro visual.
11. Registrar evidência, verificar orçamento/diff, remover ferramentas temporárias e parar obrigatoriamente no G4.

Problema técnico reversível pode ser corrigido apenas dentro dos caminhos e da estratégia aprovados. Novo arquivo persistente, dependência, transformação, visual, permissão ou estratégia exige G3.

## 5. Arquivos e orçamento de mudança

Após G2, somente estes caminhos podem ser criados ou atualizados:

- `specs/fixtures/SPEC-008-end-to-end/**`: PBIP, `.Report`, `.SemanticModel` e arquivos locais gerados pelo Desktop para a prova;
- `specs/evidence/SPEC-008/**`: screenshot Desktop e saídas de validação/inspeção necessárias;
- `specs/EVIDENCE-008-local-power-bi-end-to-end-validation.md`: método, esperado, observado, matriz e riscos;
- `specs/SPEC-008-local-power-bi-end-to-end-validation.md`: somente gates, evidência e encerramento;
- `specs/PLAN-008-local-power-bi-end-to-end-validation.md`: somente gates, evidência e encerramento;
- `.spec-008-tools/**`: instalação temporária e não global dos CLIs Power BI, removida integralmente após evidência.

Não alterar `data/`, `metadata/`, `src/`, `tests/`, `README.md`, a skill, as 12 tools, Power BI MCP, Figma, configuração global, PATH permanente ou qualquer artefato produtivo. Não instalar globalmente nem adicionar dependência ao projeto.

## 6. Evidência mínima obrigatória

### Materialização real do modelo

Todas as quatro evidências são obrigatórias:

1. PBIP e `.SemanticModel` persistidos pelo Desktop no caminho autorizado.
2. Inspeção read-only da instância Desktop lista a tabela e os dois campos.
3. DAX `COUNTROWS` retorna número maior que zero.
4. DAX de amostra retorna valores reais de `CD_TABELA` e `DS_TABELA` compatíveis com a fonte.

Arquivos TMDL existentes sem conexão/consulta bem-sucedida não bastam.

### Binding e renderização real

Todas as quatro evidências são obrigatórias:

1. Validador PBIR termina sem erro material.
2. Preview/inspeção PBIR registra exatamente uma página de prova e um `tableEx` com bindings para os dois campos.
3. Desktop Bridge identifica a instância associada ao PBIP e a página correta.
4. Screenshot capturado da instância real mostra o visual sem erro, com os dois cabeçalhos e ao menos uma linha de dados legível.

Screenshot sem inspeção do binding ou preview sem screenshot não basta.

## 7. Verificações complementares

- A fonte permanece byte a byte inalterada, comprovada por hash antes/depois.
- O artefato não contém conexão remota, credencial, publicação ou gateway.
- Exatamente uma página e um visual existem na prova.
- `git diff --check` passa; baseline e mudanças locais preexistentes são preservados.
- Nenhum arquivo fora da seção 5 é criado/modificado pela execução, desconsiderando arquivos locais transitórios internos do Desktop que não sejam incorporados ao repositório.
- Ferramentas temporárias são removidas após coleta da evidência.

A suíte Python não é requisito de aceite porque nenhum código do MCP pode mudar; só será repetida se surgir indício concreto de alteração indevida.

## 8. Rollback

Antes do G4, manter fixture e evidência para inspeção humana. Se rejeitado ou se rollback for solicitado, remover somente:

- `specs/fixtures/SPEC-008-end-to-end/`;
- `specs/evidence/SPEC-008/`;
- `specs/EVIDENCE-008-local-power-bi-end-to-end-validation.md`;
- registros de execução adicionados à SPEC-008 e ao PLAN-008.

Sempre remover `.spec-008-tools/` ao fim da execução, independentemente do resultado. Não há publicação, migração, dado produtivo ou configuração externa a restaurar.

## 9. Riscos e paradas

| Risco/ônus | Mitigação ou parada |
|---|---|
| Desktop Store não expor bridge ou PBIP | Uma recuperação segura; persistindo, `STOP_BLOCKED` |
| Import materializar nome/tipos diferentes | Correção técnica somente se inequívoca e dentro do artefato; diferença material retorna em G3 |
| Power BI MCP não conectar à instância | `STOP_BLOCKED`; TMDL ou screenshot isolados não substituem consulta real |
| Screenshot não mostrar dados legíveis | Uma correção técnica de viewport/tamanho; não adicionar visuais ou design |
| CLI exigir instalação global/admin/PATH | `STOP_HUMAN`; somente instalação temporária local pode ser proposta no G2 |
| Desktop criar arquivos fora do orçamento | Não incorporar; se forem necessários à prova ou persistência, G3 antes de prosseguir |

## 10. Critérios de aceite do plano

- **AC-P8-001:** Source Discovery confirma a fonte e os dois campos sem alterar XLSX ou catálogo.
- **AC-P8-002:** modelo Import local é materializado e provado por artefato persistido, metadados da instância, `COUNTROWS > 0` e amostra DAX.
- **AC-P8-003:** relatório possui exatamente uma página e um `tableEx` vinculado a `CD_TABELA` e `DS_TABELA`.
- **AC-P8-004:** PBIR valida sem erro material e inspeção confirma página, tipo e bindings.
- **AC-P8-005:** screenshot da instância Desktop real mostra o visual renderizado com cabeçalhos e dados legíveis, sem erro material.
- **AC-P8-006:** fonte/hash, orçamento, ausência de publicação/globalização e rollback são comprovados.
- **AC-P8-007:** evidência distingue claramente modelo materializado, binding estrutural e renderização observada.

## 11. Decisão HUMAN/Product Owner para G2

Solicita-se uma única decisão: aprovar este plano e autorizar `EXECUTE → VERIFY → EVIDENCE` estritamente dentro das seções 2 a 7, incluindo criação do PBIP/modelo/visual controlados, uso local do Desktop e instalação temporária não global dos CLIs em `.spec-008-tools/`, seguida de remoção das ferramentas e parada obrigatória no G4; pedir ajustes; ou rejeitar.

Não ficam autorizados publicação, instalação global, privilégio administrativo, mudança permanente de PATH/configuração, novo visual/página, transformação material, design/Figma, alteração do MCP/datasets ou qualquer arquivo fora do orçamento.

## 12. Gate atual

**G2 — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** Autorizada a execução por `EXECUTE → VERIFY → EVIDENCE` estritamente dentro das seções 2 a 7, com avanço automático até `STOP_HUMAN`, `STOP_BLOCKED` ou G4. Permanecem todos os limites de não-escopo e orçamento.

## 13. Resultado da execução

- Fonte preservada antes/depois: SHA-256 `0DB05B449FD47D075D5AD8B4B3C9183F33CDC197D1B4A8274148543566D15305`.
- Modelo Import materializado no Desktop: uma tabela, duas colunas, uma partição, 40 linhas; amostra DAX compatível com a fonte.
- PBIR: zero erros materiais, uma página `Prova E2E`, um `tableEx`, bindings para `CD_TABELA` e `DS_TABELA`.
- Desktop Bridge: PBIP e página corretos identificados; refresh e DAX ao vivo concluídos.
- Bloqueio obrigatório: screenshot retornou `BRIDGE_ERROR -32505: Print metadata is not available` antes e depois de reload + novo refresh. O erro é não-retentável segundo a Bridge.
- `git diff --check`: aprovado, somente com avisos LF/CRLF preexistentes.
- Nenhuma publicação, instalação global, alteração de PATH/configuração, commit, push ou release ocorreu.

**STOP_BLOCKED:** AC-P8-005 permanece não comprovado. `.spec-008-tools/` e a instância Desktop são mantidos temporariamente para retomada, pois a coleta de evidência ainda não terminou; serão removidos/encerrados depois da captura e do registro final, conforme o plano.

## 14. G3 — recuperação controlada

**APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** Autorizada a recuperação controlada da captura real do Desktop, preservando os critérios originais. A recuperação pode ativar/focalizar a janela já aberta, selecionar a página `Prova E2E`, ajustar somente viewport/estado de exibição e repetir a captura real. Não autoriza alterar modelo, bindings, número de páginas/visuais, publicação, configuração global ou substituir screenshot por preview.

### Resultado

- O modal oculto foi identificado e dispensado.
- A Data View confirmou visualmente 40 linhas com `CD_TABELA` e `DS_TABELA`.
- A Report View ficou vazia e o reload retornou `Falha ao carregar o relatório`.
- A falha foi isolada no carregamento da definição PBIR.

**STOP_HUMAN:** requer autorização específica para recriar a definição do mesmo visual dentro do caminho já aprovado, sem mudar página, tipo, campos, modelo ou critérios, seguida da validação e captura obrigatórias.

**APPROVED em 2026-09-17:** o HUMAN autorizou essa correção técnica específica, sem ampliar o resultado ou os critérios.

## 15. Encerramento técnico

A definição PBIR foi corrigida de forma mínima usando a estrutura compatível observada em artefato local nativo do mesmo Desktop: tema base compartilhado, metadata de páginas atual e schema visual atual. Página, `tableEx`, modelo e bindings permaneceram os mesmos.

Após refresh na instância limpa:

- `COUNTROWS = 40`;
- amostra DAX dos dois campos retornou valores reais;
- validate: zero erros materiais e sete warnings ambientais de schema HTTPS indisponível;
- preview: exatamente uma página e um `tableEx`;
- screenshot Desktop real: `specs/evidence/SPEC-008/desktop-prova-e2e.png`, com dois cabeçalhos e linhas legíveis;
- SHA-256 da fonte inalterado;
- `git diff --check` aprovado.

Todos os critérios AC-P8-001..007 foram tecnicamente comprovados. A execução parou no G4 sem declarar aceitação até a decisão registrada abaixo.

## 16. G4 e encerramento

**APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** A implementação, as evidências e os riscos residuais foram aceitos. O plano está `COMPLETED`; a SPEC-008 está `ACCEPTED/DONE`. Nenhum commit, push, release ou publicação foi autorizado ou realizado.
