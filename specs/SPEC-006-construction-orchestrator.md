# SPEC-006 — Construction Orchestrator

| Campo | Valor |
|---|---|
| ID | SPEC-006 |
| Título | Construction Orchestrator |
| Tipo | Infraestrutura de execução da metodologia; não é feature do runtime Data Engineering MCP |
| Status | ACCEPTED |
| Resultado | DONE |
| Baseline | `862abae4237997bc7165b27a4fc179429ff11359`, com SPEC-001 a SPEC-004 `ACCEPTED/DONE`, SPEC-005 `PROPOSED` e mudanças locais preservadas |
| Dependência normativa | SPEC-001 |
| Product Owner | HUMAN |
| Implementação autorizada | Sim — estritamente para os dois arquivos da seção 10.2 |
| Plano operacional | Incorporado nesta spec; não existe PLAN-006 separado |
| Última atualização | 2026-09-16 |

## 1. Decisão de direção e objetivo

O HUMAN/Product Owner aprovou a direção de criar um Construction Orchestrator enxuto para conduzir a construção do próprio projeto pelas fases da SPEC-001. Esta spec formaliza essa direção e solicita, ao final, uma única decisão conjunta G1 + G2. A aprovação da direção anterior não substitui esses gates.

Princípio central:

> **HUMAN é autoridade; o orquestrador é executor e guardião do fluxo.**

O orquestrador DEVE identificar e executar somente a próxima atividade que já esteja coberta por autorização válida. Ele NÃO decide produto, NÃO aprova gates, NÃO registra aprovação em nome do HUMAN e NÃO é o futuro orquestrador de tarefas de BI previsto pela SPEC-005.

Esta capacidade é infraestrutura de execução da metodologia do repositório. Ela NÃO integra o runtime, as tools nem o contrato público do `data-engineering-mcp`.

## 2. Escopo e invariantes

O Construction Orchestrator DEVE:

- reconstruir seu estado em toda retomada, exclusivamente a partir das fontes canônicas da seção 3;
- classificar a próxima transição válida e avançar automaticamente apenas quando já houver autorização explícita;
- preservar a autoridade exclusiva do HUMAN nos gates da SPEC-001;
- manter no máximo uma spec em execução ativa por vez;
- executar, verificar e registrar evidências somente dentro do objetivo, arquivos e orçamento de mudança aprovados;
- proteger mudanças locais preexistentes e nunca descartá-las durante execução ou recuperação;
- falhar de forma fechada diante de ambiguidade, inconsistência, desvio material ou evidência insuficiente;
- ser retomável e idempotente após interrupções;
- encerrar quando o objetivo humano aprovado estiver atendido, ainda que existam melhorias possíveis.

## 3. Estado canônico, sem estado oculto

Antes de qualquer ação, o orquestrador DEVE executar `INSPECT` e reconstruir o estado a partir de:

1. cabeçalhos e seções dos arquivos `SPEC-*.md` e `PLAN-*.md`;
2. registros explícitos dos gates G1, G2, G3, G4 e G5;
3. dependências declaradas, critérios de aceite e evidências registradas;
4. arquivos e orçamento de mudança autorizados pelo plano aplicável;
5. baseline, status e diff do Git, incluindo mudanças locais preexistentes;
6. resultados reproduzíveis das verificações previstas;
7. stop conditions da spec e do plano atuais.

O repositório permanece a fonte de verdade. NÃO haverá banco, daemon, memória privada, estado remoto ou outro estado oculto. A primeira versão também NÃO terá checkpoint persistido separado: se as fontes canônicas forem insuficientes, a execução deve parar em `STOP_BLOCKED`, e qualquer proposta de checkpoint exigirá nova decisão HUMAN.

## 4. Máquina de estados e transições

```text
INSPECT
   ↓
CLASSIFY
   ├─ decisão HUMAN pendente → STOP_HUMAN
   ├─ inconsistência/desvio   → STOP_BLOCKED
   └─ etapa autorizada        → EXECUTE
                                  ↓
                               VERIFY
                                  ↓
                               EVIDENCE
                                  ├─ aceite exigido → STOP_HUMAN
                                  └─ próxima etapa já autorizada → INSPECT
```

Transições permitidas:

- spec `PROPOSED` sem G1: `STOP_HUMAN`;
- G1 aprovado: criar ou seguir plano proporcional somente quando essa ação estiver expressamente autorizada;
- plano sem G2: `STOP_HUMAN`;
- G2 aprovado: executar `IMPLEMENT → VERIFY → EVIDENCE` dentro do orçamento autorizado;
- desvio material durante execução ou verificação: `STOP_HUMAN` em G3;
- evidências completas: `STOP_HUMAN` em G4 quando o aceite humano for exigido;
- G4 aprovado: inspecionar a próxima spec já existente ou iniciar somente uma spec prevista e necessária ao objetivo já aprovado;
- quebra, migração, release ou publicação: `STOP_HUMAN` em G5, além de qualquer autorização específica aplicável;
- ausência de próxima etapa necessária e autorizada: encerrar sem criar trabalho adicional.

Nenhuma inferência, resposta genérica como “continue” fora de contexto, estado de arquivo ou resultado de teste equivale a uma aprovação de gate.

## 5. Ações automáticas já autorizáveis por contrato

Quando cobertas pela spec/plano vigentes, o orquestrador PODE:

- inspecionar documentos, arquivos, diff, dependências e resultados de testes;
- identificar a próxima fase válida;
- criar plano curto após G1, somente se isso estiver explicitamente autorizado;
- editar somente os arquivos enumerados no plano aprovado;
- executar testes, smoke checks e verificações previstas;
- corrigir falhas técnicas dentro do escopo e da estratégia aprovados e repetir a verificação;
- registrar evidências factuais e rastreabilidade sem declarar aceite humano;
- retomar execução interrompida sem repetir trabalho já comprovado;
- avançar entre atividades técnicas pertencentes à mesma autorização;
- tomar decisões técnicas pequenas, reversíveis e internas ao plano aprovado.

## 6. Gates HUMAN e paradas obrigatórias

O orquestrador DEVE entrar em `STOP_HUMAN` diante de:

- aprovação de spec, plano, implementação ou aceite final;
- mudança de objetivo, escopo, não-escopo ou critérios de aceite;
- escolha de negócio ou interpretação materialmente ambígua;
- homologação ou promoção de relacionamento/autoridade;
- incompatibilidade pública ou quebra de contrato;
- risco relevante novo ou risco residual ainda não aprovado;
- arquivo, dependência, integração ou estratégia fora do plano;
- operação destrutiva, externa, irreversível ou não autorizada;
- evidência insuficiente cuja aceitação exija flexibilizar um critério;
- commit, push, release ou publicação sem autorização específica.

O orquestrador DEVE entrar em `STOP_BLOCKED` diante de:

- documentos contraditórios ou estado impossível;
- baseline não identificável;
- mudanças locais sobrepostas cuja autoria ou preservação não possa ser determinada com segurança;
- dependência não satisfeita;
- teste obrigatório indisponível ou falhando por causa externa ao escopo autorizado;
- orçamento de arquivos ou mudanças excedido;
- necessidade de inventar uma aprovação;
- repetição sem progresso após uma tentativa segura de recuperação;
- inexistência de próxima etapa necessária e autorizada.

Toda parada DEVE informar: motivo, evidência observada, última etapa segura, menor decisão necessária e condição objetiva de retomada. Parar não autoriza modificar documentos para fabricar consistência.

## 7. Proteção contra expansão silenciosa

Uma nova spec somente PODE ser proposta quando, cumulativamente:

1. for necessária para atingir um objetivo humano já aprovado;
2. a necessidade estiver demonstrada por lacuna concreta;
3. não puder ser resolvida na spec atual sem desvio material;
4. possuir resultado verificável e não-escopo explícito.

Melhorias opcionais, refatorações oportunistas e ideias descobertas durante a execução DEVEM ser registradas apenas como observações não autorizadas. Elas NÃO criam automaticamente backlog, spec, feature ou implementação.

É proibido:

- executar mais de uma spec ativa ao mesmo tempo;
- gerar specs recursivamente para melhorar o próprio orquestrador;
- ampliar critérios, arquivos ou orçamento depois do G1/G2 sem G3;
- transformar conveniência técnica em requisito de produto;
- manter o fluxo aberto depois que os objetivos aprovados estiverem atendidos.

## 8. Recuperação, idempotência e mudanças locais

Em toda retomada, o orquestrador DEVE comparar etapa declarada, autorizações, diff existente, evidências registradas e critérios ainda não satisfeitos.

Regras obrigatórias:

- não recriar plano existente;
- não repetir alteração já presente;
- não duplicar evidência já registrada;
- permitir repetição de verificações, registrando novo resultado quando necessário;
- basear toda escrita documental no estado atual, nunca somente em memória de execução anterior;
- parar se execução, documento e Git divergirem, em vez de “corrigir” silenciosamente;
- nunca limpar, reverter, sobrescrever ou incorporar mudanças locais preexistentes sem autorização e atribuição seguras;
- após interrupção, retomar da menor etapa ainda não comprovada.

## 9. Não-escopo

Esta spec não autoriza:

- implementar o orquestrador nesta etapa;
- criar `PLAN-006` separado;
- criar workflow engine, máquina de estados genérica, banco, daemon, serviço, UI, fila, YAML de workflow, framework ou arquitetura distribuída;
- criar script que invoque agentes, sistema autônomo permanente ou novo runtime;
- alterar a SPEC-005 nesta etapa;
- alterar runtime, tools, contratos MCP, testes funcionais do produto, datasets, metadata, Power BI MCP, Figma, configuração global do Codex, Git remoto ou release;
- fazer commit ou push;
- substituir ou flexibilizar qualquer gate da SPEC-001;
- executar tarefas de BI, gerar SQL para usuário final ou implementar capacidades previstas pela SPEC-005.

## 10. Plano operacional mínimo incorporado

### 10.1 Forma de implementação futura

A implementação inicial DEVE ser um contrato operacional local, legível e executável pelo ambiente/agente que trabalha neste repositório. A forma prevista é um único `AGENTS.md` na raiz, derivado desta spec e da SPEC-001. Ele conterá as regras determinísticas de inspeção, classificação, execução, parada, retomada e encerramento, sem reimplementar capacidades já fornecidas pelo agente ou pelo MCP.

Não haverá PLAN separado, dependência nova, engine, persistência, processo residente ou interface própria. A suficiência desse contrato será demonstrada pelos dez cenários controlados da seção 11 antes de seu uso sobre a SPEC-005.

### 10.2 Arquivos previstos e orçamento de mudança

Após G1 + G2 conjuntos, a implementação ficará limitada a:

- criar `AGENTS.md` na raiz: contrato operacional local do Construction Orchestrator;
- atualizar esta `SPEC-006-construction-orchestrator.md`: registrar execução, resultados dos cenários, evidências, riscos residuais e estado do gate aplicável.

Nenhum outro arquivo está autorizado. Necessidade de fixture, script, dependência, arquivo de checkpoint ou qualquer terceiro arquivo causa parada em G3.

### 10.3 Sequência de execução

1. Reexecutar `INSPECT`, confirmar baseline, documentos e mudanças locais.
2. Materializar em `AGENTS.md` somente o contrato aprovado nesta spec.
3. Revisar o diff contra o orçamento e os invariantes.
4. Executar os dez cenários controlados sem modificar a SPEC-005 nem o produto.
5. Verificar escopo, ausência de artefatos proibidos e `git diff --check`.
6. Registrar evidências factuais nesta spec.
7. Parar no G4 para aceite HUMAN antes do uso real sobre a SPEC-005.

### 10.4 Rollback

Antes do aceite, o rollback consiste em remover somente o novo `AGENTS.md` e reverter somente os registros de implementação/evidência adicionados a esta spec. Mudanças locais anteriores permanecem intactas. Como não há runtime, persistência, dependência, migração ou estado externo, nenhum rollback adicional é previsto.

## 11. Dez cenários mínimos de teste

Os cenários devem ser avaliados em estados controlados e suas decisões/saídas comparadas ao contrato, sem executar efeitos fora do escopo de cada cenário:

1. **SPEC `PROPOSED` sem G1:** deve parar em `STOP_HUMAN` sem criar plano nem implementar.
2. **G1 aprovado e criação de plano autorizada:** deve produzir somente o plano proporcional permitido.
3. **Plano sem G2:** deve parar em `STOP_HUMAN` sem alterar arquivos de implementação.
4. **G2 aprovado:** deve alterar somente arquivos permitidos, verificar e registrar evidências.
5. **Necessidade de arquivo adicional:** deve parar em G3 antes de criá-lo ou alterá-lo.
6. **Falha técnica corrigível dentro do plano:** deve corrigir dentro do escopo e repetir a verificação.
7. **Evidência completa com G4 exigido:** deve parar em `STOP_HUMAN` para aceite, sem autoaprovação.
8. **Melhoria opcional descoberta:** deve registrar observação não autorizada, sem criar spec ou feature.
9. **Retomada após interrupção:** deve reconstruir o estado e não duplicar plano, alteração ou evidência.
10. **Documentos contraditórios ou mudanças locais ambíguas:** deve falhar de forma fechada em `STOP_BLOCKED`, preservando o worktree.

## 12. Critérios de aceite

- **AC-001:** o contrato mantém HUMAN como única autoridade dos gates e restringe o orquestrador a executor/guardião.
- **AC-002:** o estado é reconstruído somente das fontes canônicas, sem banco, daemon, checkpoint ou estado oculto.
- **AC-003:** a máquina `INSPECT → CLASSIFY → EXECUTE → VERIFY → EVIDENCE` aplica corretamente `STOP_HUMAN` e `STOP_BLOCKED`.
- **AC-004:** nenhuma ação ocorre sem autorização vigente e todo desvio material para em G3.
- **AC-005:** somente uma spec fica ativa; melhorias opcionais não geram specs/features nem expandem critérios silenciosamente.
- **AC-006:** retomada é idempotente e preserva integralmente mudanças locais preexistentes.
- **AC-007:** os dez cenários da seção 11 produzem as saídas esperadas e evidência revisável.
- **AC-008:** a implementação limita-se aos dois arquivos da seção 10.2 e não cria arquitetura pesada nem dependência.
- **AC-009:** runtime, tools, testes funcionais, datasets, metadata, Power BI MCP, Figma, Codex global, remoto e release permanecem intocados; não há commit nem push.
- **AC-010:** o orquestrador encerra ao atingir o objetivo aprovado e para no G4 antes de assumir a retomada real da SPEC-005.

## 13. Matriz de rastreabilidade mínima

| Requisito | Implementação prevista | Verificação | Critério |
|---|---|---|---|
| Autoridade HUMAN e gates | `AGENTS.md` | Cenários 1, 3, 5 e 7 | AC-001, AC-003, AC-004 |
| Estado canônico e classificação | `AGENTS.md` | Cenários 1, 4 e 10 | AC-002, AC-003 |
| Escopo e não expansão | `AGENTS.md` | Cenários 5 e 8 + auditoria do diff | AC-004, AC-005, AC-008 |
| Recuperação e preservação | `AGENTS.md` | Cenários 9 e 10 | AC-006 |
| Execução técnica autorizada | `AGENTS.md` | Cenários 2, 4 e 6 | AC-004, AC-007 |
| Encerramento e retomada futura | `AGENTS.md` + evidência nesta spec | Cenário 7 + inspeção final | AC-009, AC-010 |

## 14. Impactos positivos e riscos residuais

**Impactos positivos:** reduz confirmações operacionais repetitivas sem transferir autoridade; torna retomadas reproduzíveis; protege escopo e mudanças locais; permite execução técnica contínua entre gates válidos; evita backlog e features criados por oportunismo; mantém a metodologia auditável e pequena.

| Risco/ônus residual | Mitigação |
|---|---|
| Documentos em linguagem natural admitirem interpretação divergente | Transições e paradas explícitas; ambiguidade material falha fechada |
| Contrato local depender da disciplina do ambiente/agente | Cenários controlados antes do uso e G4 humano obrigatório |
| Mudanças locais dificultarem atribuição | Inspeção em toda retomada; ambiguidade leva a `STOP_BLOCKED`, nunca a limpeza automática |
| Paradas conservadoras reduzirem velocidade | Ônus intencional quando falta autorização ou evidência; automação continua dentro do contrato válido |
| Necessidade futura de checkpoint ou automação adicional | Fora da primeira versão; exigir lacuna concreta e nova decisão HUMAN |
| `AGENTS.md` afetar todo o repositório | Contrato limitado à construção governada pela SPEC-001 e sem alterar comportamento do runtime |

## 15. Requisito de retomada futura da SPEC-005

Somente depois da implementação desta spec passar pelos testes e receber aceite G4, o Construction Orchestrator poderá retomar a SPEC-005. Na retomada ele DEVE, sem alterar previamente seu conteúdo:

1. confirmar que a SPEC-005 continua `PROPOSED`, parada em G1, e que não existe PLAN-005;
2. consolidar na proposta da SPEC-005 os três modos de intake inicial: **criar BI novo**, **melhorar/revisar BI existente** ou **gerar somente SQL**;
3. aplicar Source Discovery proporcional, perguntando o caminho quando a fonte XLSX/CSV/TXT não tiver sido informada;
4. para banco, usar representações locais em `data/`, sem conexão ao banco;
5. coordenar o Data Engineering MCP e, quando aplicável, o Power BI MCP e suas capacidades relevantes;
6. usar Figma opcionalmente quando houver criação ou reformulação visual de BI e a capacidade estiver disponível, sem torná-lo dependência obrigatória;
7. inspecionar antes de gerar de uma a N specs executáveis, em quantidade proporcional ao trabalho;
8. parar novamente no G1 da SPEC-005 antes de criar PLAN-005 ou implementar qualquer capacidade.

Esses itens são requisitos da futura retomada, não autorização para editar a SPEC-005 nesta etapa.

## 16. Decisão conjunta solicitada ao HUMAN — G1 + G2

Solicita-se uma única decisão explícita que, se aprovada, registre conjuntamente:

1. **G1:** aprovação do objetivo, classificação como infraestrutura metodológica, escopo, invariantes, fontes canônicas, máquina de estados, gates, stop conditions, proteção contra expansão, recuperação, critérios de aceite, impactos e riscos residuais;
2. **G2:** autorização para criar somente `AGENTS.md`, atualizar somente esta SPEC-006 com evidências e executar a sequência e os dez cenários definidos, sem arquivo adicional;
3. confirmação de que não haverá PLAN-006 separado, runtime próprio, workflow engine, banco, daemon, serviço, UI, fila, framework, dependência ou configuração global;
4. confirmação de que a execução deverá parar no G4 antes de usar o orquestrador para retomar a SPEC-005;
5. confirmação de que SPEC-005, runtime, tools, testes funcionais, datasets, metadata, Power BI MCP, Figma, Git remoto e release ficam intocados, e de que não haverá commit nem push.

## 17. Gate atual

**G1 + G2 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** Autorizada somente a criação de `AGENTS.md`, a execução dos dez cenários, o registro de evidências nesta SPEC-006 e a parada obrigatória no G4. Não foram autorizados expansão de escopo, scripts adicionais, engine, banco, serviço, framework, dependências novas ou alterações na SPEC-005. O risco residual de interpretação em linguagem natural foi aceito nesta primeira versão devido ao comportamento fail-closed.

## 18. Registro de decisões

| Gate | Decisor | Data | Decisão | Condições/observações |
|---|---|---|---|---|
| Direção | HUMAN/Product Owner | 2026-09-16 | APPROVED | Criar spec compacta separada, com plano incorporado e decisão conjunta G1 + G2 |
| G1 — SPEC-006 | HUMAN/Product Owner | 2026-09-16 | APPROVED | Escopo, invariantes, gates, paradas, idempotência, critérios, impactos e risco fail-closed aprovados |
| G2 — SPEC-006 | HUMAN/Product Owner | 2026-09-16 | APPROVED | Criar somente `AGENTS.md`, executar dez cenários, registrar evidências nesta spec e parar obrigatoriamente no G4 |
| G4 — Aceite final | HUMAN/Product Owner | 2026-09-16 | APPROVED | Implementação, evidências, 10/10 cenários e riscos residuais aceitos; SPEC-006 encerrada como `ACCEPTED/DONE` |

**Gate de saída G4 aprovado.** A implementação foi aceita pelo HUMAN. A retomada da SPEC-005 permanece uma atividade posterior e deve começar por `INSPECT`, obedecendo à salvaguarda da seção 15 e ao contrato local.

## 19. Evidências de implementação e verificação

### 19.1 Implementação

- **EV-001 — Contrato local:** criado somente `AGENTS.md` na raiz, com autoridade HUMAN, fontes canônicas, precedência, máquina de estados, regras de classificação/execução/verificação/evidência, paradas, proteção de escopo, recuperação, idempotência, encerramento e salvaguarda da SPEC-005.
- **EV-002 — Orçamento:** os únicos arquivos desta implementação são `AGENTS.md` e esta SPEC-006. Não foi criado PLAN-006, script, fixture, checkpoint, dependência, engine, banco, daemon, serviço, UI, fila ou framework.
- **EV-003 — Produto preservado:** não houve alteração da SPEC-005, runtime, tools, testes funcionais, datasets, metadata, Power BI MCP, Figma, configuração global do Codex, Git remoto ou release. Não houve commit nem push.

### 19.2 Execução dos dez cenários

Os cenários foram executados como verificações documentais controladas: para cada estado de entrada, a regra obrigatória e sua saída foram confrontadas com o texto do contrato local. Nenhum cenário executou efeitos sobre o produto ou a SPEC-005.

| Cenário | Resultado observado | Evidência no contrato | Status |
|---|---|---|---|
| 1. `PROPOSED` sem G1 | `STOP_HUMAN`, sem plano ou implementação | `CLASSIFY` regra 2 | PASS |
| 2. G1 e plano autorizado | somente plano proporcional explicitamente autorizado | `CLASSIFY` regra 3 e `EXECUTE` | PASS |
| 3. Plano sem G2 | `STOP_HUMAN`, sem implementação | `CLASSIFY` regra 4 | PASS |
| 4. G2 aprovado | `EXECUTE → VERIFY → EVIDENCE` dentro do orçamento | `CLASSIFY` regra 6 e seções `EXECUTE`/`VERIFY` | PASS |
| 5. Arquivo adicional necessário | parada em G3 antes da mudança | `CLASSIFY` regra 5 | PASS |
| 6. Falha corrigível no plano | correção interna e repetição da verificação | seção `EXECUTE` | PASS |
| 7. Evidência completa com G4 | `STOP_HUMAN`, sem autoaceite | `CLASSIFY` regra 7 e seção `VERIFY and EVIDENCE` | PASS |
| 8. Melhoria opcional | observação apenas, sem spec/feature automática | seção `Scope-growth guard` | PASS |
| 9. Retomada | sem duplicar plano, alteração ou evidência | seção `Recovery and idempotency` | PASS |
| 10. Contradição/mudança ambígua | `STOP_BLOCKED`, preservando mudanças locais | `CLASSIFY` regra 1 e `Mandatory blocked stops` | PASS |

No primeiro passe do cenário 1, a parada `STOP_HUMAN` já existia, mas a proibição de criar plano estava apenas implícita. Dentro do escopo aprovado, o contrato foi tornado explícito com “without creating a plan or implementation”; a matriz completa foi então repetida e obteve **10/10 PASS**. Isso também demonstra o comportamento previsto no cenário 6.

### 19.3 Verificações adicionais

- `git diff --check -- AGENTS.md specs/SPEC-006-construction-orchestrator.md`: PASS, sem erro;
- busca por `PLAN-006*`: zero arquivos;
- busca por artefatos raiz com nomes de orchestrator/workflow/checkpoint, exceto `AGENTS.md`: zero;
- presença de `AGENTS.md`: confirmada;
- SHA-256 observado da SPEC-005 ao final: `F272865183E3BADE1B38C8C73A571C99532D7CA7E936567807C64ECF3BA06CBE`;
- baseline Git permaneceu `862abae4237997bc7165b27a4fc179429ff11359`;
- mudanças locais preexistentes foram preservadas.

## 20. Avaliação dos critérios de aceite

| Critério | Resultado | Evidência |
|---|---|---|
| AC-001 | PASS | autoridade e gates no `AGENTS.md`; cenários 1, 3, 5 e 7 |
| AC-002 | PASS | seção `Canonical state and precedence` |
| AC-003 | PASS | máquina de estados e cenários 1, 4, 7 e 10 |
| AC-004 | PASS | regras `CLASSIFY`/`EXECUTE`; cenários 4 e 5 |
| AC-005 | PASS | `Scope-growth guard`; cenário 8 |
| AC-006 | PASS | `Recovery and idempotency`; cenários 9 e 10 |
| AC-007 | PASS | matriz 10/10 da seção 19.2 |
| AC-008 | PASS | somente os dois arquivos autorizados; nenhuma arquitetura ou dependência nova |
| AC-009 | PASS | auditoria de escopo e diff; sem commit/push |
| AC-010 | PASS | `Completion rule` e salvaguarda explícita da SPEC-005 |

## 21. Riscos residuais após verificação

- interpretação de documentos em linguagem natural continua dependente do ambiente/agente; o contrato reduz o risco com regras ordenadas e falha fechada;
- estados reais podem apresentar contradições não representadas pelos dez cenários; nesses casos, `STOP_BLOCKED` permanece obrigatório;
- mudanças locais extensas podem impedir atribuição segura e causar parada conservadora; nenhuma limpeza automática é permitida;
- a eficácia operacional completa somente será observada durante uso posterior, que permanece bloqueado até o G4.

Não foi identificado risco novo que exija G3. Os riscos residuais permanecem dentro da classe aceita pelo HUMAN no G1 + G2.

## 22. Gate atual — G4

**G4 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** A implementação, as evidências, os dez cenários aprovados e os riscos residuais foram aceitos. Status final: `ACCEPTED`. Resultado: `DONE`.

O Construction Orchestrator está disponível para uma retomada futura da SPEC-005, mas este aceite não inicia essa retomada nem autoriza alteração silenciosa. O próximo uso deve começar por `INSPECT` e aplicar integralmente a seção 15. Nenhum commit, push ou release foi autorizado.
