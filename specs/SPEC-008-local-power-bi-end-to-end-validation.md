# SPEC-008 — Local Power BI End-to-End Validation

| Campo | Valor |
|---|---|
| ID | SPEC-008 |
| Título | Local Power BI End-to-End Validation |
| Tipo | Validação prática mínima end-to-end |
| Status | ACCEPTED / DONE |
| Resultado | PASS — aceito pelo HUMAN no G4 |
| Dependências | SPEC-005, SPEC-006 e SPEC-007 `ACCEPTED/DONE` |
| Baseline | `862abae4237997bc7165b27a4fc179429ff11359`, com mudanças locais preservadas |
| Product Owner | HUMAN |
| Implementação autorizada | Sim — G2 aprovado em 2026-09-17, dentro do PLAN-008 |
| Última atualização | 2026-09-17 |

## 1. Lacuna concreta e objetivo

A SPEC-007 validou os três modos da skill, o Data Engineering MCP e a fronteira PBIR, mas encerrou com duas limitações aceitas: não houve renderização real no Power BI Desktop e a fixture não possuía modelo materializado. Portanto, ainda não existe evidência de um fluxo local completo que parta de uma representação de dados disponível, produza um modelo semântico real, vincule um visual a esse modelo e confirme o resultado renderizado no Desktop.

O objetivo mínimo desta spec é executar uma única prova local de **BI novo** end-to-end, sem publicação: reutilizar uma fonte XLSX sintética já existente em `data/`, materializar um modelo pequeno, criar uma página com um único visual data-bound e comprovar sua abertura e renderização real no Power BI Desktop.

## 2. Escopo mínimo proposto

1. Selecionar no plano uma única planilha sintética já existente em `data/`, sem alterar a fonte.
2. Executar Source Discovery proporcional e reutilizar o Data Engineering MCP somente nas capacidades relevantes para identificar tabela, colunas, tipos, limitações e intenção.
3. Criar um artefato Power BI local, controlado e não produtivo, com um modelo materializado derivado somente da fonte escolhida.
4. Criar uma única página e um único visual simples, vinculado a campos reais do modelo, suficientes para provar o fluxo.
5. Validar estruturalmente o artefato, abri-lo em uma instância local do Power BI Desktop e registrar evidência de renderização real sem erro material.
6. Preservar separadamente fatos observados, limitações e qualquer warning; não apresentar preview estrutural, schema ou simulação como renderização Desktop.
7. Remover apenas ferramentas temporárias que um futuro plano autorize explicitamente; manter a fixture e a evidência até a decisão G4.

## 3. Resultado verificável

A prova termina quando houver evidência reproduzível de toda a cadeia:

`XLSX local → descoberta → modelo materializado → visual data-bound → validação → abertura/renderização no Power BI Desktop`.

Não é necessário demonstrar mais de uma tabela, relacionamento, medida complexa, redesign ou publicação para fechar essa lacuna.

## 4. Critérios de aceite propostos

- **AC-001:** uma fonte XLSX sintética existente em `data/` é inspecionada sem alteração, conexão externa ou repetição desnecessária de fatos já conhecidos.
- **AC-002:** o modelo semântico local é materializado e contém somente a tabela e os campos mínimos definidos pelo plano, sem credenciais ou dependência remota.
- **AC-003:** o relatório contém exatamente uma página de prova e ao menos um visual simples realmente vinculado a campos do modelo materializado.
- **AC-004:** validação estrutural termina sem erro material antes da abertura no Desktop.
- **AC-005:** o artefato é aberto e renderizado em uma instância real do Power BI Desktop; a evidência distingue renderização observada de preview, schema ou inferência.
- **AC-006:** a evidência registra entrada, capacidades usadas, ambiente, método, esperado, observado, limitações, riscos residuais e rollback de forma reproduzível.
- **AC-007:** nenhuma publicação, workspace, gateway, conexão de banco, dado produtivo, alteração global, commit, push ou release ocorre; baseline e mudanças locais são preservados.

## 5. Não-escopo

- Publicar em Power BI Service, criar workspace, configurar gateway, refresh agendado ou credenciais externas.
- Criar dashboard produtivo, múltiplas páginas, múltiplos visuais, tema, navegação, RLS, relacionamento, medida DAX complexa ou refinamento visual.
- Testar novamente os três modos da SPEC-007 ou ampliar a skill, o MCP, suas 12 tools, datasets ou metadata.
- Alterar Power BI MCP, Figma, configuração global do Codex, PATH permanente ou instalar ferramenta globalmente.
- Conectar diretamente a banco de dados ou usar dados não sintéticos/produtivos.
- Commit, push, release ou distribuição.

## 6. Limite para um futuro plano

Se G1 for aprovado, um PLAN-008 curto deverá definir antes da execução:

- a planilha, tabela, campos e visual exatos;
- o formato local do modelo/relatório e todos os caminhos que poderão mudar;
- a capacidade real disponível para autoria, materialização, validação, abertura e captura da renderização;
- qualquer ferramenta temporária não global, seu diretório isolado e sua remoção;
- os passos de verificação, evidência e rollback;
- as condições objetivas de `STOP_BLOCKED` caso Desktop, autoria ou materialização não estejam disponíveis.

Até G2, não podem ser criados plano de implementação executado, fixture, modelo, relatório, ferramenta temporária ou evidência de ensaio. Qualquer alteração global, instalação global, publicação ou mudança de estratégia continuará exigindo autorização específica.

## 7. Riscos e mitigação proposta

| Risco/ônus | Mitigação ou parada |
|---|---|
| Power BI Desktop indisponível ou não controlável | Diagnóstico objetivo e `STOP_BLOCKED`; não substituir por preview |
| Materialização exigir ferramenta, arquivo ou permissão ainda não autorizada | Detalhar no PLAN-008 e obter G2/G3 antes da mudança |
| Fonte exigir transformação ou semântica material | Escolher no plano a prova mais simples; decisão de negócio retorna ao HUMAN |
| Renderização visual parecer válida sem binding real | Inspecionar modelo e binding, além da evidência visual |
| Ensaio crescer para construção de produto | Limitar a uma fonte, uma tabela, uma página e um visual; demais melhorias ficam fora do escopo |

## 8. Proporcionalidade e necessidade

Uma única spec é suficiente porque existe uma única lacuna encadeada e um único resultado: comprovar localmente a passagem de dados materializados até um visual renderizado. A SPEC-007 não pode absorver essa execução sem reabrir um trabalho já aceito e ampliar materialmente seu escopo, que proibia construir BI e não exigia Desktop ou modelo materializado.

Esta proposta não transforma as limitações aceitas da SPEC-007 em falhas retroativas. Ela cobre somente a etapa adicional necessária para o objetivo humano de chegar ao teste prático completo/end-to-end.

## 9. Decisão HUMAN/Product Owner para G1

Solicita-se uma única decisão: aprovar esta proposta mínima e autorizar somente a criação de um PLAN-008 curto e proporcional, com parada obrigatória no G2; pedir ajustes; ou rejeitar.

Nenhuma construção, materialização, abertura do Desktop, instalação, download, publicação ou alteração técnica está autorizada por esta proposta.

## 10. Gate atual

**G1 — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** A proposta foi aprovada como validação proporcional da cadeia `XLSX local → descoberta → modelo materializado → visual vinculado → validação → renderização real no Power BI Desktop`. Foi autorizada somente a criação de um PLAN-008 curto e operacional, reutilizando capacidades existentes e sem ampliar para dashboard, design/Figma, publicação, otimizações, novos recursos do MCP ou melhorias estéticas.

**G2 — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** O PLAN-008 foi aprovado para executar até `STOP_HUMAN`, `STOP_BLOCKED` ou G4, sem ampliar escopo, arquivos, estratégia ou critérios.

## 11. Registro de decisões

| Gate | Autoridade | Data | Decisão | Limite autorizado |
|---|---|---|---|---|
| G1 — SPEC-008 | HUMAN/Product Owner | 2026-09-17 | APPROVED | Criar somente PLAN-008 curto e operacional; definir evidência mínima de materialização e renderização; parar no G2 antes de mexer no Power BI |
| G2 — PLAN-008 | HUMAN/Product Owner | 2026-09-17 | APPROVED | Executar `EXECUTE → VERIFY → EVIDENCE` até `STOP_HUMAN`, `STOP_BLOCKED` ou G4, dentro do orçamento aprovado |
| G3 — recuperação da captura | HUMAN/Product Owner | 2026-09-17 | APPROVED | Recuperação controlada da captura real do Desktop, mantendo intactos os critérios da SPEC-008 |

## 12. Execução e parada atual

O modelo Import foi materializado em uma instância real do Power BI Desktop, com uma tabela, duas colunas e 40 linhas comprovadas por DAX; o PBIR possui exatamente uma página e um `tableEx` vinculado aos dois campos aprovados. O Desktop Bridge identificou o PBIP e a página corretos.

**STOP_BLOCKED em 2026-09-17:** a captura obrigatória da página falhou três vezes com `BRIDGE_ERROR -32505: Print metadata is not available`, inclusive após a única recuperação segura prevista — reload do PBIP pela Bridge, novo refresh completo e nova tentativa. A Bridge permaneceu `ready`, mas não expôs metadados de impressão. Como AC-005 exige screenshot real com cabeçalhos e dados e proíbe substituí-lo por preview, a SPEC-008 não pode avançar a G4.

Retomada objetiva: disponibilizar a página `Prova E2E` em estado capturável no Desktop/Bridge ou fornecer uma captura real verificável da instância aberta. Não é autorizado trocar o critério por preview, simulação ou inferência.

**G3 — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** Autorizada a recuperação controlada da captura real do Desktop, sem alterar modelo, visual, escopo ou critérios da SPEC-008.

## 13. Resultado da recuperação G3

O controle seguro da janela revelou um modal até então invisível à Bridge: primeiro, `Referência de objeto não definida para uma instância de um objeto`; após dispensá-lo e entrar na Report View, a página permaneceu vazia. Um reload suportado pela Bridge produziu `Falha ao carregar o relatório`. A Data View do mesmo Desktop continuou mostrando as 40 linhas e os campos corretos, isolando a falha na definição/carregamento do relatório, não no modelo materializado.

**STOP_HUMAN — G3 adicional:** a menor recuperação restante é recriar tecnicamente a definição PBIR do mesmo `tableEx`, preservando exatamente a página `Prova E2E`, o tipo do visual e os bindings `CD_TABELA`/`DS_TABELA`, e então repetir validate → reload → screenshot. Essa ação altera o arquivo do visual e não foi executada sem autorização inequívoca. Os critérios originais permanecem intactos.

**G3 adicional — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** Autorizada a correção técnica específica da definição do mesmo `tableEx`, preservando página, modelo, campos, bindings e critérios, seguida de validate → reload → screenshot.

## 14. Verificação final e gate atual

A correção PBIR mínima alinhou o relatório aos metadados nativos do Desktop sem mudar página, tipo do visual ou bindings. Em uma instância limpa, o modelo foi atualizado novamente e a Bridge capturou com sucesso `specs/evidence/SPEC-008/desktop-prova-e2e.png`. A imagem mostra os cabeçalhos `CD_TABELA` e `DS_TABELA` e múltiplas linhas reais, sem erro visual.

Verificação final:

- modelo Desktop Import: uma tabela, duas colunas, 40 linhas;
- DAX final: `COUNTROWS = 40` e amostra real dos dois campos;
- PBIR: zero erros materiais, uma página `Prova E2E`, um `tableEx`;
- screenshot real: PASS;
- fonte preservada pelo mesmo SHA-256;
- `git diff --check`: PASS, com avisos LF/CRLF preexistentes;
- nenhuma publicação, instalação global, alteração de configuração, commit, push ou release.

**G4 solicitado após a verificação:** implementação e evidências concluídas; a decisão permaneceu exclusiva do HUMAN/Product Owner até a aprovação registrada abaixo.

**G4 — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** A implementação, as evidências e os riscos residuais foram aceitos. `SPEC-008 → ACCEPTED/DONE` e `PLAN-008 → COMPLETED` estão autorizados. Não houve autorização para commit, push, release ou publicação.
