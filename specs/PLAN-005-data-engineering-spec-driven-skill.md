# PLAN-005 — `data-engineering-spec-driven` Skill

| Campo | Valor |
|---|---|
| Spec | `SPEC-005` |
| Baseline | `862abae4237997bc7165b27a4fc179429ff11359`, com SPEC-001 a SPEC-004 e SPEC-006 aceitas |
| Gate de entrada | G1 aprovado em 2026-09-16 pelo HUMAN/Product Owner |
| Status | `COMPLETED` |
| Implementação autorizada | Sim — execução concluída e aceita no G4 |

## 1. Objetivo e solução mínima

Criar uma skill curta e autocontida que faça intake nos três modos aprovados, execute Source Discovery proporcional, coordene os especialistas disponíveis e, somente após inspeção, produza uma a N specs executáveis. A skill preservará informação já conhecida, reservará ao HUMAN apenas decisões genuínas e entregará as specs para execução posterior pelo orquestrador aplicável.

A skill será orientação de coordenação. Não implementará gates, estado, workflow, descoberta de catálogo, autoridade de relacionamentos, query intent, safety, SQL, operações Power BI ou operações Figma.

## 2. Arquivos e orçamento de mudança

- Criar `data-engineering-spec-driven/SKILL.md`: contrato operacional integral da skill.
- Atualizar `specs/SPEC-005-data-engineering-spec-driven-skill.md`: somente gate, evidências e encerramento.
- Atualizar este `specs/PLAN-005-data-engineering-spec-driven-skill.md`: somente decisão G2, evidências e encerramento.

Não criar referências, scripts, testes, fixtures, templates, dependências ou arquivos adicionais. Não instalar ou copiar a skill para o Codex global. Qualquer necessidade de ampliar este orçamento exige parada em G3 antes da mudança.

## 3. Conteúdo e comportamento previstos

1. Intake obrigatório em um dos modos: BI novo, melhorar/revisar BI existente ou somente SQL.
2. Reuso de respostas e descobertas existentes, sem perguntar novamente informação confiável já disponível.
3. Source Discovery proporcional: pedir caminho ausente para XLSX/CSV/TXT; para banco, usar somente representações/tabelas locais em `data/`, sem conexão direta.
4. Data Engineering MCP como especialista em catálogo, relacionamentos, query intent, safety e SQL, sem duplicação.
5. Power BI MCP e todas as capacidades/skills relevantes disponíveis para tarefas Power BI.
6. Figma opcional quando houver criação ou reformulação visual e estiver disponível.
7. Inspeção obrigatória antes de planejamento ou geração.
8. Uma spec compacta para trabalho simples; N specs somente por entregáveis, dependências, riscos ou ordem de execução separáveis.
9. Specs com objetivo, escopo, não-escopo, entradas, dependências, critérios verificáveis, decisões HUMAN e condições de parada.
10. Encaminhamento para execução automática posterior, sem a skill executar gates ou implementação.

## 4. Verificação mínima

Executar uma matriz documental controlada cobrindo: os três modos de intake; não repetição de informação; caminho de arquivo ausente e presente; banco limitado a `data/`; delegação ao Data Engineering MCP; uso proporcional de Power BI; Figma aplicável, indisponível e desnecessário; inspeção antes da geração; uma spec simples; múltiplas specs justificadas; ambiguidade material com `STOP_HUMAN`; e ausência de segunda ASEP, orquestrador ou capacidade duplicada.

Também verificar:

- presença de todos os requisitos e critérios da SPEC-005 no `SKILL.md`;
- ausência de PLAN/spec adicional, script, dependência ou instalação global;
- diff limitado aos três arquivos da seção 2;
- `git diff --check` sem erro;
- preservação de runtime, tools, testes, datasets, metadata, Power BI MCP, Figma, Codex global, Git remoto e release.

## 5. Rollback

Remover somente `data-engineering-spec-driven/SKILL.md` e reverter apenas os registros de execução/evidência adicionados à SPEC-005 e a este plano. Não há migração, persistência, dependência, dado ou runtime a restaurar.

## 6. Critérios de aceite

- **AC-P5-001:** o `SKILL.md` implementa integralmente intake, discovery, especialistas, proporcionalidade e paradas da SPEC-005.
- **AC-P5-002:** todos os cenários da seção 4 passam e demonstram inspeção anterior à geração de uma a N specs.
- **AC-P5-003:** a skill coordena capacidades existentes sem duplicar MCP, Power BI, Figma, ASEP ou orquestrador.
- **AC-P5-004:** a implementação permanece em um único artefato autocontido, sem arquivo auxiliar, dependência ou instalação global.
- **AC-P5-005:** orçamento, itens protegidos e rollback são verificados; nenhum commit, push ou release ocorre.

## 7. Riscos e mitigação

| Risco/ônus | Mitigação |
|---|---|
| Instruções em linguagem natural variarem entre execuções | Regras ordenadas, exemplos de decisão e matriz controlada |
| Uma a N specs causar fragmentação excessiva | Uma spec como padrão simples; N exige justificativa objetiva |
| Capacidade especializada não estar disponível | Diagnóstico explícito; Figma opcional; decisão HUMAN somente se a ausência for material |
| Representação local de banco ser insuficiente | Nunca conectar diretamente; expor a limitação e parar quando afetar o resultado |
| Skill crescer para segunda ASEP/orquestrador | Proibir estado, gates, execução e duplicação; limitar a intake, inspeção, coordenação e geração de specs |

## 8. Decisão HUMAN/Product Owner para G2

Solicita-se uma única decisão: aprovar este plano e autorizar `IMPLEMENT → VERIFY → EVIDENCE` estritamente dentro dos três arquivos da seção 2, com parada obrigatória no G4; pedir ajustes; ou rejeitar.

## 9. Gate atual

**G2 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** Autorizada a execução de `IMPLEMENT → VERIFY → EVIDENCE` estritamente dentro dos três arquivos da seção 2, com parada obrigatória no G4. Não foram autorizados commit, push, release nem alteração dos itens protegidos.

## 10. Evidências de implementação e verificação

- criado somente `data-engineering-spec-driven/SKILL.md` como artefato da skill; não há arquivo auxiliar na pasta;
- frontmatter, nome e estrutura validados pelo `quick_validate.py` oficial do `skill-creator`: **PASS**;
- inspeção de cobertura confirmou intake nos três modos, preservação de informação conhecida, Source Discovery para XLSX/CSV/TXT e banco local em `data/`, Data Engineering MCP, Power BI relevante, Figma opcional, inspeção anterior e uma a N specs;
- orçamento confirmado: somente o `SKILL.md`, esta atualização do PLAN-005 e a atualização de evidências da SPEC-005;
- baseline permaneceu `862abae4237997bc7165b27a4fc179429ff11359` e `git diff --check` passou, com apenas os avisos preexistentes de normalização LF/CRLF;
- nenhum script, teste, fixture, template, referência, dependência, instalação global, commit, push ou release foi criado ou executado.

### 10.1 Matriz documental controlada

| Cenário | Comportamento exigido e observado no contrato | Resultado |
|---|---|---|
| BI novo | seleciona `New BI` e inspeciona antes de especificar | PASS |
| BI existente | seleciona revisão/melhoria e inspeciona relatório, modelo, visuais, filtros, tema e dependências relevantes | PASS |
| Somente SQL | seleciona `SQL only` sem inventar entregável BI | PASS |
| Informação já conhecida | mantém registro e não pergunta novamente, salvo conflito ou materialidade | PASS |
| XLSX/CSV/TXT sem caminho | pergunta somente pelo caminho necessário | PASS |
| XLSX/CSV/TXT com caminho | usa o caminho fornecido sem repeti-lo como pergunta | PASS |
| Fonte banco | usa somente representações/tabelas em `data/` e proíbe conexão direta | PASS |
| Data Engineering MCP | delega catálogo, relações, query intent, safety e SQL sem duplicação ou promoção | PASS |
| Power BI | descobre e usa todas as capacidades/skills relevantes disponíveis | PASS |
| Figma aplicável | usa opcionalmente em criação/reformulação visual quando disponível | PASS |
| Figma ausente ou desnecessário | não bloqueia trabalho especificável e não é usado em SQL-only/não visual | PASS |
| Ordem do fluxo | proíbe planejar ou escrever specs antes da inspeção necessária | PASS |
| Trabalho simples | produz uma spec compacta | PASS |
| Trabalho separável | permite N specs somente com justificativa objetiva e dependências sem sobreposição | PASS |
| Ambiguidade material | retorna `STOP_HUMAN` com decisão mínima e condição de retomada | PASS |
| Contradição/dependência ausente | retorna `STOP_BLOCKED` sem inventar autoridade | PASS |
| Limite arquitetural | não executa specs, gates ou construção e não vira segunda ASEP/orquestrador | PASS |

Resultado: **17/17 PASS**.

## 11. Riscos residuais e gate de saída

- instruções em linguagem natural ainda dependem da interpretação do agente; regras ordenadas, limites explícitos e a matriz reduzem o risco;
- disponibilidade e nomes das capacidades Power BI/Figma podem variar; a skill descobre somente as relevantes e mantém Figma opcional;
- representações locais de banco podem estar incompletas ou desatualizadas; a skill expõe a limitação e falha fechada quando material;
- proporcionalidade de uma a N specs envolve julgamento; critérios objetivos e justificativa obrigatória reduzem fragmentação.

**G4 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** A implementação, as evidências, a matriz de 17/17 cenários e os riscos residuais foram aceitos. O PLAN-005 está `COMPLETED` e a SPEC-005 foi encerrada como `ACCEPTED/DONE`.

Este encerramento não autoriza instalação global da skill, commit, push, release nem alteração de runtime, tools, testes, datasets, metadata, Power BI MCP, Figma, Codex global ou Git remoto.
