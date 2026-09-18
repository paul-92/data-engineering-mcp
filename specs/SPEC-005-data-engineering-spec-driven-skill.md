# SPEC-005 — `data-engineering-spec-driven` Skill

| Campo | Valor |
|---|---|
| ID | SPEC-005 |
| Título | `data-engineering-spec-driven` Skill |
| Tipo | Proposta comportamental consolidada para intake, discovery e geração proporcional de specs |
| Status | ACCEPTED |
| Resultado | DONE |
| Dependências | SPEC-002, SPEC-003 e SPEC-004 aceitas; capacidades atuais do MCP |
| Product Owner | HUMAN |
| Implementação autorizada | Concluída e aceita no G4 |
| Última atualização | 2026-09-16 |

## 1. Objetivo e problema

Definir uma skill que transforme pedidos de BI e SQL em uma ou mais specs executáveis, após intake e inspeção proporcionais. A skill deve cobrir três modos iniciais: **criar BI novo**, **melhorar ou revisar BI existente** e **gerar somente SQL**.

Hoje o Data Engineering MCP fornece as capacidades técnicas de catálogo, autoridade de relacionamentos, intenção estruturada, gate de segurança e geração/explicação SQL. A skill deve coordenar essas capacidades, as capacidades relevantes de Power BI e, opcionalmente, Figma, para descobrir o contexto necessário e decompor o trabalho sem antecipar implementação.

A skill deve coordenar essas capacidades, não reproduzi-las nem criar uma segunda ASEP.

## 2. Escopo mínimo

- iniciar pelo modo solicitado — **BI novo**, **melhorar/revisar BI existente** ou **somente SQL** — e identificar resultado esperado, limites e autorização disponível;
- preservar e reutilizar toda informação já fornecida pelo HUMAN ou descoberta durante a inspeção, sem perguntar novamente;
- executar Source Discovery proporcional antes de planejar ou especificar;
- para XLSX, CSV ou TXT, usar o caminho já informado ou perguntar somente pelo caminho ausente necessário para acesso à fonte;
- para banco de dados, usar as representações e tabelas locais disponíveis na pasta `data/` do Data Engineering MCP, sem conexão direta ao banco;
- estruturar a intenção quando houver consulta ou mudança com múltiplas fontes, ambiguidade, filtros relevantes ou grain;
- verificar autoridade, conflitos, segurança e riscos antes de propor, gerar ou revisar SQL;
- usar o Data Engineering MCP como especialista técnico em catálogo, relacionamentos, query intent, safety e SQL;
- coordenar o Power BI MCP e todas as suas capacidades e skills relevantes ao trabalho de Power BI;
- usar Figma opcionalmente quando houver criação ou reformulação visual e a capacidade estiver disponível, sem torná-lo dependência obrigatória;
- somente após a inspeção, gerar de **uma a N specs executáveis**, em quantidade proporcional ao trabalho, com dependências e critérios verificáveis;
- preparar as specs para execução automática posterior por um orquestrador, reservando ao HUMAN apenas decisões genuínas;
- produzir um fechamento curto com specs geradas, decisões pendentes, impactos e riscos residuais.

## 3. Regra de proporcionalidade

Uma tarefa simples, local, reversível, de baixo impacto e com intenção inequívoca deve resultar em **uma única spec compacta**, sem decomposição, documentos ou gates artificiais adicionais.

Mais de uma spec somente se justifica quando houver entregáveis separáveis, dependências entre componentes, riscos ou decisões independentes, mudança estrutural, integração relevante, rollback não trivial ou uma ordem de execução que precise ficar explícita. Cada spec deve ser a menor unidade executável e verificável; a quantidade não pode crescer por conveniência documental.

A skill não executa as specs que gera, não implementa um motor de gates e não governa o ciclo de construção. A execução posterior pertence ao orquestrador e ao contrato metodológico aplicável.

## 4. Fluxo operacional mínimo

1. **Intake:** identificar um dos três modos, objetivo, artefatos, fontes, restrições e autoridade já concedida; não repetir perguntas respondidas.
2. **Source Discovery:** inspecionar proporcionalmente fontes e artefatos. Para XLSX/CSV/TXT, solicitar o caminho apenas se ausente. Para banco, limitar-se às representações/tabelas em `data/`, sem conexão direta.
3. **Inspeção especializada:** usar o Data Engineering MCP para catálogo, relacionamentos, query intent, safety e SQL; em tarefas de Power BI, usar o Power BI MCP e todas as capacidades/skills relevantes disponíveis; usar Figma somente quando visualmente aplicável e disponível.
4. **Estruturar e avaliar:** representar a intenção conforme SPEC-003, consultar a autoridade da SPEC-002 e manter ambiguidades, conflitos, limitações e pendências explícitos.
5. **Decompor proporcionalmente:** decidir entre uma spec compacta ou N specs menores com justificativa objetiva baseada em entregáveis, dependências, riscos e ordem de execução.
6. **Gerar specs executáveis:** registrar objetivo, escopo, não-escopo, entradas, dependências, critérios verificáveis, decisões HUMAN genuínas e condições de parada, sem implementar a solução.
7. **Entregar para execução posterior:** ordenar dependências e tornar explícito o que o orquestrador poderá executar automaticamente após as aprovações aplicáveis.

## 5. Quando exigir decisão HUMAN

A skill deve parar antes de:

- aprovar, promover ou resolver relacionamento ausente, `INFERRED`, `KNOWN` ou conflitante;
- escolher entre interpretações que alterem fontes, JOIN, grain, semântica, dados ou resultado esperado;
- criar ou aprovar spec/plan/gate formal, ou ampliar escopo e critérios já aprovados;
- executar mudança destrutiva, irreversível, persistente, externa ou não autorizada;
- introduzir contrato público, dependência, tool, arquitetura ou incompatibilidade;
- aceitar evidência insuficiente ou risco residual material em nome do Product Owner.

Perguntas devem ser específicas e mínimas. A skill não deve interromper por preferências cosméticas ou decisões técnicas reversíveis dentro do escopo autorizado.

Informação já fornecida pelo HUMAN, presente nos artefatos ou obtida de forma confiável durante a inspeção não deve ser perguntada novamente. Ausência de caminho para XLSX/CSV/TXT, ambiguidade material de negócio, fonte local insuficiente ou decisão que altere resultado continuam sendo motivos legítimos para uma pergunta mínima.

## 6. Especialistas e capacidades coordenadas

A skill consome as interfaces existentes, sem adicionar ou modificar tools:

- descoberta: `listar_tabelas`, `descrever_tabela`, `buscar_coluna` e `buscar_tabelas`;
- relacionamentos: `inferir_relacionamentos` e `encontrar_caminho`, preservando autoridade e conflitos;
- catálogo: `atualizar_catalogo` somente quando autorizado e necessário, e `status_catalogo` para estado/evidência;
- SQL: `gerar_sql`, `gerar_select`, `gerar_join` e `explicar_sql`, mantendo parametrização, limitações e gates atuais.

O Structured Query Intent da SPEC-003 orienta a representação antes do SQL quando necessário; não requer uma nova tool. O MCP continua sendo a fonte das capacidades e políticas executáveis, enquanto a skill decide como aplicá-las ao trabalho solicitado.

Em tarefas de Power BI, a skill deve usar o Power BI MCP e todas as capacidades e skills disponíveis que sejam relevantes ao pedido, incluindo inspeção do estado existente quando o modo for melhorar/revisar. A proposta não fixa uma lista estática dessas capacidades, para permitir evolução compatível sem duplicá-las na skill.

Figma é um especialista visual opcional: pode apoiar criação ou reformulação visual quando aplicável e disponível, mas sua ausência não bloqueia pedidos que possam ser especificados com Power BI e contexto suficiente. A skill não duplica operações de Power BI ou Figma e não substitui suas políticas próprias.

## 7. Residência e distribuição propostas

A skill deve residir como artefato próprio `data-engineering-spec-driven/SKILL.md`, fora do pacote Python e do processo do servidor MCP. Durante desenvolvimento, pode ser versionada em área dedicada do repositório apenas se um plano futuro aprovar os arquivos exatos; para uso, deve ser instalada ou empacotada separadamente no diretório de skills do Codex ou por um mecanismo de distribuição de skills/plugins.

Essa separação permite versionar compatibilidade com o MCP sem tornar a inicialização, instalação ou release do runtime dependente da skill. Referências ou scripts auxiliares só devem existir se casos reais demonstrarem necessidade; a forma inicial preferida é um `SKILL.md` curto e autocontido. Local definitivo, política de invocação e canal de distribuição devem ser propostos no PLAN-005, sem criar uma decisão HUMAN adicional antes do planejamento quando não houver impacto material.

## 8. Não-escopo

- Implementar a skill, criar sua pasta, `SKILL.md`, PLAN-005, testes ou scripts.
- Executar as specs geradas ou assumir o papel do Construction Orchestrator.
- Criar uma segunda ASEP, workflow engine, banco, UI, serviço, framework, agente autônomo ou nova arquitetura.
- Duplicar catálogo, Relationship Authority, Structured Query Intent, Safety Gate ou gerador/explicador SQL.
- Criar burocracia, documentação automática ou gates formais para toda tarefa.
- Adicionar, remover ou alterar as 12 tools e seus contratos.
- Conectar-se diretamente a banco de dados ou exigir Figma como dependência obrigatória.
- Alterar runtime, código, testes, datasets, metadata, Power BI MCP, Codex global, Git remoto ou release.

## 9. Critérios de aceite

- **AC-001:** o intake distingue os três modos e não repete perguntas já respondidas ou resolvidas pela inspeção.
- **AC-002:** Source Discovery é proporcional; caminho ausente de XLSX/CSV/TXT é solicitado e fontes de banco são lidas somente pelas representações/tabelas locais em `data/`.
- **AC-003:** intenção, autoridade, conflitos e riscos permanecem explícitos, sem inferência ou aprovação silenciosa.
- **AC-004:** geração e revisão SQL reutilizam as capacidades e o Safety Gate existentes, sem duplicação ou bypass.
- **AC-005:** o Data Engineering MCP atua como especialista técnico; tarefas Power BI usam todas as capacidades/skills relevantes disponíveis; Figma é usado apenas quando visualmente aplicável e disponível.
- **AC-006:** a inspeção precede a geração e produz de uma a N specs executáveis em quantidade justificada pelo trabalho.
- **AC-007:** exatamente as 12 tools existentes são integradas conceitualmente e permanecem compatíveis.
- **AC-008:** as specs deixam claras dependências, critérios verificáveis, execução automática posterior e somente decisões HUMAN genuínas.
- **AC-009:** a skill permanece desacoplada do runtime MCP, não vira segunda ASEP/orquestrador e não introduz itens do não-escopo.

## 10. Compatibilidade, impactos e riscos/ônus

**Compatibilidade:** proposta aditiva e externa ao runtime; não altera tools, contratos, dados ou comportamento do MCP. A futura skill deverá declarar a versão/capacidades mínimas esperadas e degradar com diagnóstico claro quando indisponíveis, sem reimplementar o MCP.

**Impactos positivos:** cria uma entrada única para BI/SQL; evita redescoberta e perguntas repetidas; reduz improvisação e uso inseguro de JOIN; integra especialistas existentes; produz unidades executáveis proporcionais e preparadas para continuidade automática.

| Risco/ônus | Mitigação proposta |
|---|---|
| Virar processo burocrático ou segunda ASEP | Uma spec compacta para trabalho simples; a skill apenas prepara specs e não executa gates ou construção |
| Duplicar lógica do MCP | Skill coordena; MCP continua responsável por catálogo, autoridade, gates e SQL |
| Quantidade de specs variar ou fragmentar demais | Critérios observáveis de entregáveis, dependências, riscos e ordem; justificativa curta para N |
| Paradas humanas excessivas | Parar apenas nas condições materiais da seção 5 |
| Capacidades de Power BI/Figma variarem por ambiente | Descobrir e usar somente capacidades relevantes disponíveis; Figma permanece opcional |
| Representações locais de banco estarem incompletas/desatualizadas | Tornar a limitação explícita e pedir decisão HUMAN quando afetar materialmente a especificação; nunca conectar diretamente |
| Acoplamento de instalação/versionamento | Artefato e distribuição separados do runtime, com compatibilidade declarada |
| Escopo crescer por casos hipotéticos | Começar autocontida; adicionar recursos apenas após necessidade demonstrada e aprovação |

## 11. Decisões HUMAN/Product Owner para G1

1. Aprovar os três modos de intake, Source Discovery e a regra de não repetir informação já conhecida.
2. Aprovar uma spec compacta para trabalho simples e 1..N specs somente conforme os critérios proporcionais da seção 3.
3. Aprovar as condições de autonomia e de parada obrigatória para decisão HUMAN.
4. Confirmar que a skill coordena Data Engineering MCP, capacidades/skills relevantes de Power BI e Figma opcional, sem duplicá-los, contornar gates ou tornar-se segunda ASEP/orquestrador.
5. Aprovar o princípio de residência e distribuição desacopladas do runtime, delegando ao PLAN-005 a proposta concreta dentro desse limite.
6. Confirmar critérios de aceite, compatibilidade, impactos, riscos/ônus e todo o não-escopo.
7. Se G1 for aprovado, autorizar a criação de um PLAN-005 curto como próxima atividade; nenhuma implementação fica autorizada por esta proposta.

## 12. Gate atual

**G1 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** A proposta revisada, os requisitos consolidados, critérios de aceite, impactos, riscos/ônus e não-escopo foram aprovados. Foi autorizada somente a criação de um PLAN-005 curto como próxima atividade; nenhuma implementação da skill foi autorizada.

**G2 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** O PLAN-005 foi autorizado dentro de seu orçamento, com execução até evidências e parada obrigatória no G4.

## 13. Implementação e evidências

G2 foi aprovado em 2026-09-16 pelo HUMAN/Product Owner, limitado ao orçamento do PLAN-005. Foi criado somente `data-engineering-spec-driven/SKILL.md`; a SPEC-005 e o PLAN-005 receberam apenas registros de gates e evidências.

A skill passou na validação estrutural oficial do `skill-creator` e na matriz documental controlada de **17/17 cenários**, cobrindo os três modos, não repetição de informação, discovery de arquivos e banco local, especialistas, Figma opcional, ordem inspeção→specs, proporcionalidade, `STOP_HUMAN`, `STOP_BLOCKED` e proteção contra segunda ASEP/orquestrador.

O baseline permaneceu `862abae4237997bc7165b27a4fc179429ff11359`; `git diff --check` passou com somente avisos preexistentes de LF/CRLF. Runtime, tools, testes, datasets, metadata, Power BI MCP, Figma, Codex global, Git remoto e release permaneceram intocados. Não houve commit nem push.

Riscos residuais: interpretação de linguagem natural, variação de capacidades disponíveis, suficiência das representações locais de banco e julgamento proporcional de uma a N specs. As mitigações estão no PLAN-005 e no contrato da skill.

**G4 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** A implementação, as evidências de validação, a matriz de 17/17 cenários e os riscos residuais foram aceitos. Status final: `ACCEPTED`. Resultado: `DONE`.

Este aceite encerra a SPEC-005 e autoriza marcar o PLAN-005 como `COMPLETED`. Não autoriza instalação global da skill, commit, push, release ou alteração de qualquer item protegido.
