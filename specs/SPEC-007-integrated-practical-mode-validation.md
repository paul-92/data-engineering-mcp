# SPEC-007 — Integrated Practical Mode Validation

| Campo | Valor |
|---|---|
| ID | SPEC-007 |
| Título | Integrated Practical Mode Validation |
| Tipo | Validação integrada mínima da skill aceita na SPEC-005 |
| Status | ACCEPTED |
| Resultado | DONE |
| Dependências | SPEC-002, SPEC-003, SPEC-004, SPEC-005 e SPEC-006 `ACCEPTED/DONE` |
| Baseline | `862abae4237997bc7165b27a4fc179429ff11359`, com mudanças locais preservadas |
| Product Owner | HUMAN |
| Implementação autorizada | Concluída e aceita no G4 |
| Última atualização | 2026-09-17 |

## 1. Lacuna concreta e objetivo

A SPEC-005 aceitou a estrutura e o contrato documental da skill `data-engineering-spec-driven` com matriz de 17/17 cenários. Seu orçamento proibiu testes, fixtures, scripts, instalação global e qualquer alteração de Power BI, Figma ou runtime. Portanto, ainda não existe evidência de uma execução integrada/prática dos três modos aceitos: **BI novo**, **melhorar/revisar BI existente** e **somente SQL**.

O repositório contém representações locais em `data/` e o Data Engineering MCP, mas não contém artefato Power BI existente. A menor próxima etapa necessária é executar três ensaios controlados, um por modo, usando a skill diretamente de seu `SKILL.md` local, sem instalação global, e registrar evidências reproduzíveis de intake, inspeção especializada, comportamento fail-closed e geração proporcional de specs.

## 2. Escopo mínimo proposto

1. Definir três pedidos de teste pequenos e determinísticos, um para cada modo.
2. Reutilizar as representações locais já disponíveis em `data/`; não conectar a banco de dados.
3. Usar o Data Engineering MCP real para descoberta, intenção, autoridade, safety e SQL quando aplicável.
4. Em **BI novo**, usar somente capacidades Power BI disponíveis e relevantes para inspecionar o contexto e produzir specs; não criar, publicar ou alterar relatório.
5. Em **BI existente**, criar ou selecionar no plano um artefato local mínimo, não produtivo e reversível que permita inspeção real; não usar nem modificar artefato produtivo.
6. Em **somente SQL**, demonstrar um caminho permitido e, quando provocado pelo cenário, um bloqueio real de relacionamento/autoridade sem bypass.
7. Invocar a skill pelo arquivo local aceito, sem copiá-la ou instalá-la no Codex global.
8. Registrar prompts/entradas, capacidades efetivamente disponíveis, inspeções, saídas, paradas, specs geradas e limitações suficientes para reprodução.

Os ensaios validam a coordenação e a geração de specs. As specs produzidas são artefatos de teste e não recebem aprovação nem autorização de implementação.

## 3. Limite de mudança a detalhar no plano

Se G1 for aprovado, um PLAN-007 curto deverá limitar previamente:

- os três casos e seus resultados esperados;
- o local exato de qualquer fixture e evidência;
- o mecanismo local de invocação, sem instalação;
- as operações read-only permitidas nos especialistas;
- os arquivos que poderão ser criados ou atualizados;
- o rollback integral dos artefatos de teste.

Até G2, não podem ser criados fixture, script, prompt persistido, saída de teste ou evidência de execução. O plano não poderá autorizar mudança em runtime, tools, datasets existentes, metadata existente, Power BI MCP, Figma, configuração global ou artefato produtivo.

## 4. Critérios de aceite propostos

- **AC-001:** cada um dos três modos é executado uma vez pela skill local, sem instalação global e sem repetir informação presente no caso ou descoberta na inspeção.
- **AC-002:** todos os casos demonstram inspeção anterior à geração; fontes de banco permanecem limitadas às representações locais em `data/`.
- **AC-003:** o Data Engineering MCP é exercitado de forma real nas capacidades relevantes e seus resultados, autoridades, conflitos e bloqueios são preservados sem promoção ou bypass.
- **AC-004:** os dois casos de BI descobrem e usam somente capacidades Power BI relevantes disponíveis; o caso de BI existente inspeciona um artefato local controlado antes de propor melhoria. Ausência material de capacidade produz diagnóstico fail-closed, não simulação apresentada como integração real.
- **AC-005:** Figma permanece opcional: só é usado se visualmente aplicável, disponível e necessário ao caso aprovado; sua ausência não invalida evidência que não dependa dele.
- **AC-006:** cada saída contém uma a N specs apenas após inspeção, com quantidade justificada, critérios verificáveis, dependências e decisões HUMAN genuínas; nenhuma spec gerada é executada ou autoaprovada.
- **AC-007:** um caso permitido e um bloqueio material demonstram que safety e autoridade reais não são contornados.
- **AC-008:** evidência identifica entrada, método, ambiente/capacidades, esperado, observado, limitações e risco residual; o teste é reproduzível sem rede, publicação ou mudança global.
- **AC-009:** baseline e mudanças locais preexistentes permanecem preservados; não ocorrem commit, push, release, instalação global ou alteração de configuração protegida.

## 5. Não-escopo

- Adicionar feature, tool, integração, engine, agente, dependência ou capacidade à skill ou ao MCP.
- Corrigir ou ampliar a skill durante os ensaios; qualquer desvio material exige G3.
- Implementar ou aprovar as specs produzidas pelos casos.
- Criar BI produtivo, publicar em workspace, alterar Power BI MCP, editar configuração global ou exigir Figma.
- Conectar a banco de dados, executar SQL ou modificar datasets/metadata existentes.
- Medir qualidade de design, performance de relatório ou correção de regra de negócio além do necessário para validar o fluxo.
- Commit, push, release ou distribuição/instalação da skill.

## 6. Riscos e mitigação

| Risco/ônus | Mitigação proposta |
|---|---|
| Confundir simulação textual com integração real | Registrar capacidades efetivamente chamadas e falhar fechado quando uma dependência material não estiver disponível |
| Fixture de BI virar produto ou feature | Artefato mínimo, local, não produtivo, reversível e limitado previamente pelo PLAN-007 |
| Resultado variar por interpretação do agente | Casos pequenos, entradas e resultados esperados travados no plano, com evidência reproduzível |
| Specs de teste contaminarem o fluxo canônico | Mantê-las como saídas isoladas de teste, sem aprovação, execução ou numeração canônica |
| Ensaios alterarem estado externo | Operações read-only; nenhuma publicação, configuração, credencial, conexão direta ou persistência externa |

## 7. Proporcionalidade e necessidade

Uma única spec é suficiente porque os três ensaios verificam o mesmo entregável — comportamento integrado da skill aceita —, compartilham baseline, método, riscos e rollback. Separá-los criaria fragmentação sem independência material.

Esta spec é necessária para o objetivo já declarado de chegar ao teste integrado/prático. A lacuna não pode ser fechada na SPEC-005 encerrada: seu G4 já foi aceito e seu orçamento excluiu exatamente os testes, fixtures e arquivos adicionais agora necessários.

## 8. Decisão HUMAN/Product Owner para G1

Solicita-se uma única decisão: aprovar esta proposta mínima e autorizar somente a criação de um PLAN-007 curto e proporcional, com parada obrigatória no G2; pedir ajustes; ou rejeitar.

Nenhum ensaio, fixture, evidência, instalação ou alteração técnica está autorizado por esta proposta.

## 9. Gate atual

**G1 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** A lacuna, o escopo mínimo e a necessidade dos três ensaios foram aprovados. Foi autorizada somente a criação de um PLAN-007 curto e proporcional, preservando os modos somente SQL, BI novo e BI existente, com parada obrigatória no G2. Nenhum ensaio, fixture, evidência ou alteração técnica foi autorizado.

## 10. Registro de decisões

| Gate | Autoridade | Data | Decisão | Limite autorizado |
|---|---|---|---|---|
| G1 — SPEC-007 | HUMAN/Product Owner | 2026-09-16 | APPROVED | Criar somente o PLAN-007 curto; preservar os três ensaios; tratar os 35 testes bloqueados por permissão temporária como limitação ambiental e parar novamente no G2 |
| G4 — Aceite final | HUMAN/Product Owner | 2026-09-17 | APPROVED | Evidências, 7/7 critérios, 48 testes, smoke com 12 tools e riscos residuais aceitos; encerrar SPEC-007 como `ACCEPTED/DONE` e PLAN-007 como `COMPLETED` |

**G2 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** O PLAN-007 foi aprovado para executar os três ensaios dentro de seu orçamento, corrigir apenas problemas técnicos internos ao plano e avançar por `EXECUTE → VERIFY → EVIDENCE`, com parada obrigatória no G4 ou em bloqueio/desvio genuíno.

## 11. Estado de execução

O preflight após G2 encontrou dependências obrigatórias indisponíveis: ausência dos CLIs locais de autoria/inspeção Power BI, zero conexões e instâncias reportadas pelo Power BI MCP e negação ambiental do subprocesso/pipe stdio usado pelo smoke do Data Engineering MCP. Evidência detalhada: `EVIDENCE-007-integrated-practical-mode-validation.md`.

**STOP_BLOCKED.** Nenhum ensaio ou fixture foi executado/criado e nenhum critério foi flexibilizado. A retomada exige capacidades locais reais de validação/inspeção Power BI e transporte MCP funcional, ou aprovação G3 explícita de estratégia alternativa dentro de novos limites definidos pelo HUMAN.

## 12. G3 — preparação do ambiente

**G3 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner para preparação controlada do ambiente real, mantendo os critérios originais da SPEC-007.** A decisão não identifica mecanismo, caminhos ou permissões e, portanto, não é tratada como autorização implícita para instalação global, download, elevação de permissões ou alteração de Power BI/Figma/configuração global.

**G3 — PARAMETERS APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** Autorizados download e instalação temporária não global dos dois CLIs Power BI em `.spec-007-tools/`, execução necessária fora do sandbox para superar o `WinError 5`, uso exclusivo nos ensaios e remoção integral posterior. Não foram autorizados instalação global, privilégio administrativo, PATH/configuração permanente, alteração de produto, Power BI MCP, datasets ou critérios.

## 13. Execução e gate final

Os três modos foram executados com integrações reais e evidência reproduzível em `EVIDENCE-007-integrated-practical-mode-validation.md`. Resultado: **7/7 critérios do PLAN-007 PASS**, suíte completa **48 passed**, smoke com exatamente 12 tools e fixture PBIR validada/inspecionada.

Riscos residuais: ausência de renderização em Desktop, schemas remotos indisponíveis durante validação online, modelo da fixture não materializado e variação inerente à interpretação da skill. As limitações foram expostas e nenhum resultado simulado foi apresentado como integração real.

**G4 — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** As evidências, os sete critérios aprovados, a suíte com 48 testes, o smoke MCP com exatamente 12 tools e os riscos residuais foram aceitos. Status final: `ACCEPTED`. Resultado: `DONE`.

O aceite preserva como limitações: não houve renderização real no Power BI Desktop e a fixture não possui modelo materializado; esses pontos não foram tratados como capacidades validadas. O PLAN-007 pode ser encerrado como `COMPLETED`. Não foram autorizados commit, push, release, instalação global ou alteração de Power BI MCP, Figma ou configurações globais.
