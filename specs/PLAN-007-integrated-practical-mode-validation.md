# PLAN-007 — Integrated Practical Mode Validation

| Campo | Valor |
|---|---|
| Spec | `SPEC-007` |
| Baseline | `862abae4237997bc7165b27a4fc179429ff11359`, com mudanças locais preservadas |
| Gate de entrada | G1 aprovado em 2026-09-16 pelo HUMAN/Product Owner |
| Status | `COMPLETED` |
| Implementação autorizada | Sim — G2 aprovado em 2026-09-16; limitada às seções 2 a 5 |

## 1. Objetivo e estratégia mínima

Executar uma única rodada controlada da skill local `data-engineering-spec-driven`, sem instalação, nos modos **somente SQL**, **BI novo** e **BI existente**. Cada caso deverá usar especialistas reais quando relevantes, demonstrar inspeção anterior à geração e produzir somente specs de teste não aprovadas e não executáveis por autorização implícita.

A execução usará o `SKILL.md` aceito no repositório como contrato explícito da rodada. Não copiará a skill para diretório global, não alterará código ou configuração dos especialistas e não apresentará simulação textual como integração real.

## 2. Casos travados

### Caso A — somente SQL

- Fonte: representações XLSX já existentes em `data/`, sem conexão direta a banco.
- Pedido: descobrir uma tabela e colunas reais e especificar uma consulta Oracle `SELECT/WITH` segura, com filtro parametrizado.
- Verificação permitida: exercitar catálogo, descrição/busca, intenção estruturada, geração e explicação SQL do Data Engineering MCP.
- Subprova obrigatória: um caminho de tabela única deve gerar SQL seguro; uma tentativa multi-tabela sem relacionamento `APPROVED` livre de conflitos deve bloquear antes da emissão, sem bypass ou promoção.
- Saída esperada da skill: uma spec compacta de teste, somente após a inspeção, com a limitação de autoridade explícita.

### Caso B — BI novo

- Fonte: as mesmas representações locais já inspecionadas, reutilizando descobertas sem repetir perguntas.
- Pedido: especificar um BI novo e pequeno sobre uma tabela local, com público, resultado e visual mínimo declarados no roteiro de evidência.
- Verificação permitida: descobrir e usar capacidades Power BI relevantes disponíveis para validar viabilidade e fronteiras do artefato controlado; Figma somente se estiver disponível e for materialmente necessário, sem ser requisito.
- Proibição: não criar nem publicar relatório, semantic model ou workspace; não persistir estado externo.
- Saída esperada da skill: uma spec compacta de teste que alcance a fronteira de integração Power BI e identifique capacidades efetivamente disponíveis, sem executar a construção.

### Caso C — BI existente

- Artefato: fixture Power BI local, mínima, não produtiva e reversível, criada somente dentro de `specs/fixtures/SPEC-007-existing-bi/` após o G2. A pasta pode conter apenas os arquivos exigidos pelo formato PBIP/PBIR escolhido pela capacidade Power BI disponível; a lista final será registrada na evidência.
- Pedido: inspecionar o artefato e propor uma melhoria pequena de legibilidade ou organização, sem alterar o artefato durante a inspeção.
- Verificação permitida: capacidades Power BI read-only relevantes para estrutura, modelo, página, visuais, filtros, tema e dependências presentes.
- Proibição: não editar o artefato na etapa de revisão, não abrir/publicar workspace remoto e não usar artefato produtivo.
- Saída esperada da skill: uma spec compacta de melhoria baseada no estado realmente inspecionado, separando observação de proposta.

Se uma capacidade material não estiver disponível, o caso deve falhar fechado com diagnóstico objetivo. Não substituir chamada real por resultado inventado.

## 3. Sequência autorizável após G2

1. Reconstruir o estado por `INSPECT` e confirmar baseline, mudanças locais e disponibilidade dos especialistas.
2. Criar apenas a fixture controlada do Caso C e o arquivo de evidência previstos na seção 4.
3. Executar Caso A; registrar entrada, chamadas, esperado, observado e saída da skill.
4. Executar Caso B reutilizando fatos do Caso A; registrar a fronteira Power BI efetivamente alcançada.
5. Executar Caso C de modo read-only; registrar inspeção e proposta sem alteração indevida.
6. Verificar critérios, orçamento, ausência de efeitos externos e `git diff --check`.
7. Registrar evidências factuais no PLAN-007, na SPEC-007 e no arquivo único de evidência; parar obrigatoriamente no G4.

Um desvio de caso, estratégia, ferramenta, dependência ou limite de arquivos exige G3 antes da mudança.

## 4. Arquivos e orçamento de mudança

Após G2, somente estes caminhos poderão mudar:

- `specs/fixtures/SPEC-007-existing-bi/**`: fixture mínima do Caso C, limitada ao formato local Power BI escolhido e sem dados sensíveis ou conexão externa;
- `specs/EVIDENCE-007-integrated-practical-mode-validation.md`: roteiro, entradas, capacidades chamadas, saídas de teste e matriz de resultados;
- `specs/SPEC-007-integrated-practical-mode-validation.md`: somente evidências, gate e encerramento;
- `specs/PLAN-007-integrated-practical-mode-validation.md`: somente evidências, gate e encerramento.

Artefatos temporários podem existir somente sob diretório temporário isolado do ensaio e devem ser removidos ao final. Não alterar `data/`, `metadata/`, `src/`, `tests/`, `README.md`, a skill, Power BI MCP, Figma, configuração global, Git remoto ou qualquer artefato produtivo. Não adicionar script, dependência, tool ou configuração.

## 5. Evidência e verificação

Para cada caso, registrar:

- pedido integral e fatos já conhecidos;
- fontes e artefatos inspecionados antes da geração;
- especialista/capacidade realmente chamada e resultado relevante;
- resultado esperado e observado;
- saída integral da skill, inclusive quantidade e justificativa das specs;
- paradas, limitações, decisões HUMAN e riscos residuais;
- confirmação de que nenhuma spec de teste foi aprovada ou executada.

Verificações comuns:

- três modos executados exatamente uma vez;
- SQL permitido parametrizado e bloqueio multi-tabela anterior à emissão;
- capacidades Power BI reais identificadas nos dois casos de BI;
- fixture existente inspecionada antes da proposta e preservada durante a revisão;
- nenhuma repetição de fatos já fornecidos ou descobertos;
- nenhum efeito externo, instalação global, commit, push ou release;
- diff limitado à seção 4 e `git diff --check` sem erro.

A suíte geral poderá ser repetida uma vez com temporários controlados apenas como verificação auxiliar de baseline. Os 35 erros anteriores de `PermissionError` são limitação ambiental, não defeito do produto. Persistindo a limitação, ela será registrada sem falhar a SPEC-007, salvo se impedir uma evidência obrigatória, a inicialização do Data Engineering MCP ou um dos três casos; nessa situação, retornar `STOP_BLOCKED` com a dependência exata.

## 6. Critérios de aceite

- **AC-P7-001:** Caso A demonstra Source Discovery real, Data Engineering MCP, SQL seguro parametrizado e bloqueio de JOIN não autorizado.
- **AC-P7-002:** Caso B percorre a skill até uma fronteira Power BI real e produz uma spec proporcional sem criar ou publicar BI.
- **AC-P7-003:** Caso C inspeciona uma fixture Power BI local real e produz proposta de melhoria sem alterar indevidamente o artefato.
- **AC-P7-004:** todas as saídas resultam de inspeção anterior, reutilizam fatos conhecidos e preservam autoridade, conflitos, safety e limitações.
- **AC-P7-005:** chamadas reais e indisponibilidades são distinguíveis de simulação; dependência material ausente falha fechada.
- **AC-P7-006:** evidência é reproduzível e cobre todos os critérios da SPEC-007 sem executar ou aprovar as specs geradas.
- **AC-P7-007:** mudanças ficam no orçamento, a fixture é não produtiva e não existem efeitos externos ou alterações protegidas.

## 7. Rollback

Remover somente `specs/fixtures/SPEC-007-existing-bi/` e `specs/EVIDENCE-007-integrated-practical-mode-validation.md`, além de reverter apenas os registros de execução adicionados à SPEC-007 e a este plano. Não há migração, instalação, publicação, dado produtivo ou configuração externa a restaurar.

## 8. Riscos e condições de parada

| Risco/ônus | Mitigação ou parada |
|---|---|
| Power BI disponível sem capacidade read-only suficiente | `STOP_BLOCKED` se impedir Caso B ou C; não simular integração |
| Formato mínimo da fixture exigir arquivos não previstos | `STOP_HUMAN` em G3 antes de exceder `specs/fixtures/SPEC-007-existing-bi/**` ou introduzir dependência |
| Dados locais não sustentarem o pedido travado | Ajuste técnico reversível apenas dentro do caso; escolha material retorna ao HUMAN |
| JOIN local carecer de autoridade | Resultado esperado do subteste de bloqueio; nenhuma promoção automática |
| Permissão temporária bloquear pytest | Registrar como limitação; `STOP_BLOCKED` somente se impedir evidência obrigatória ou execução dos casos |
| Saída revelar defeito ou necessidade de mudar a skill | Registrar evidência e parar em G3; não corrigir dentro deste plano |

## 9. Decisão HUMAN/Product Owner para G2

Solicita-se uma única decisão: aprovar este plano e autorizar a execução dos três casos, criação da fixture e evidência estritamente no orçamento da seção 4, seguida de `VERIFY → EVIDENCE` e parada obrigatória no G4; pedir ajustes; ou rejeitar.

Não são solicitadas nem ficam implícitas autorizações para commit, push, release, instalação global, publicação, conexão direta a banco, alteração de runtime, skill, Power BI MCP, Figma ou configuração global.

## 10. Gate atual

**G2 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** Autorizada a execução dos três ensaios exatamente dentro do orçamento da seção 4, seguida de `EXECUTE → VERIFY → EVIDENCE` e parada obrigatória no G4. Problemas técnicos podem ser corrigidos autonomamente apenas dentro deste plano. Qualquer ampliação de arquivos, escopo, permissões, Power BI, Figma, configuração global ou critério exige o gate correspondente.

## 11. Evidência de preflight e bloqueio

O preflight autorizado foi registrado em `EVIDENCE-007-integrated-practical-mode-validation.md`. Não há CLI `powerbi-report-author` ou `powerbi-desktop`, e o Power BI MCP reportou zero conexões e zero instâncias locais. Sem essas capacidades, não é possível criar/validar e inspecionar a fixture PBIP/PBIR real exigida pelos Casos B e C sem inventar integração ou ampliar dependências/permissões.

O smoke do Data Engineering MCP também foi impedido por `PermissionError: [WinError 5]` ao criar o subprocesso/pipe stdio. A limitação de permissão torna-se material para o Caso A porque impede a chamada MCP real exigida pelo plano.

**STOP_BLOCKED.** Último estágio seguro: preflight de `EXECUTE`, antes de criar fixture ou executar qualquer caso. Retomada objetiva: capacidade Power BI local de validação e inspeção disponível e transporte MCP stdio funcional, ou decisão G3 explícita que aprove uma estratégia alternativa proporcional e seus limites. Nenhum critério foi flexibilizado.

## 12. Direção HUMAN para G3

**G3 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner para preparação controlada do ambiente real, mantendo os critérios originais da SPEC-007.**

A decisão autoriza a direção de recuperação, mas não especifica qual preparação pode ser executada nem altera as proibições originais de instalação global, ampliação implícita de permissões ou modificação de Power BI/Figma/configuração global. Permanecem pendentes os limites operacionais mínimos: mecanismo de disponibilização dos dois CLIs Power BI, local permitido para arquivos/dependências e autorização — ou não — para download e execução fora do sandbox.

**G3 — PARAMETERS APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** Exclusivamente para a SPEC-007, ficam autorizados: download de `@microsoft/powerbi-report-authoring-cli` e `@microsoft/powerbi-desktop-bridge-cli`; instalação temporária e não global em `.spec-007-tools/`; execução desses CLIs e do smoke MCP fora das restrições do sandbox somente para superar o `WinError 5`; uso restrito aos três ensaios; e remoção completa de `.spec-007-tools/` após as evidências. Permanecem proibidos instalação global, privilégio administrativo, mudança permanente de PATH/configuração, alteração de produto, Power BI MCP, datasets, critérios, commit, push e release.

A preparação pode avançar. Qualquer requisito além desse orçamento retorna a `STOP_HUMAN`.

## 13. Execução, verificação e evidências

Após o G3 parametrizado, o ambiente temporário foi preparado sem instalação global. Os três casos foram executados e registrados integralmente em `EVIDENCE-007-integrated-practical-mode-validation.md`:

- Caso A: MCP real, SQL parametrizado permitido, explicação e bloqueio real de JOIN `INFERRED`;
- Caso B: catálogo e roles reais de `tableEx`/`cardVisual`, fronteira Power BI preservada e uma spec compacta sem construção/publicação;
- Caso C: fixture PBIR local, validação offline limpa, previews read-only e spec compacta de melhoria sem implementação.

A suíte completa passou com `48 passed`; smoke confirmou 12 tools. Os sete critérios AC-P7 passaram. Não houve alteração de produto, datasets, metadata, skill, Power BI MCP, Figma, configuração global, commit, push ou release.

Riscos residuais: ausência de Desktop/renderização; schemas remotos inacessíveis apesar de validação offline limpa; fixture sem modelo materializado; interpretação em linguagem natural. Nenhum critério foi flexibilizado.

**G4 — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** A validação, as evidências e os riscos residuais foram aceitos. Status final do plano: `COMPLETED`.

Permanecem registradas, sem promoção a resultado validado, a ausência de renderização real no Power BI Desktop e a ausência de modelo materializado na fixture. O encerramento não autoriza commit, push, release, instalação global nem alteração de Power BI MCP, Figma ou configurações globais.
