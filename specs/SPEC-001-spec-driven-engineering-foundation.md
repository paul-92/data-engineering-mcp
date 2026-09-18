# SPEC-001 — Spec-Driven Engineering Foundation

| Campo | Valor |
|---|---|
| ID | SPEC-001 |
| Título | Spec-Driven Engineering Foundation |
| Tipo | Fundação de governança e processo |
| Status | ACCEPTED |
| Resultado | DONE |
| Baseline de referência | `data-engineering-mcp` v0.1.0, commit `862abae4237997bc7165b27a4fc179429ff11359` |
| Product Owner | HUMAN — a designar/confirmar |
| Implementação autorizada | Sim — exclusivamente documental, conforme `PLAN-001` |
| Última atualização | 2026-09-11 |

## 1. Resumo executivo

Esta spec define a metodologia canônica para construir, manter e revisar o próprio projeto `data-engineering-mcp`. Toda mudança relevante deve percorrer o fluxo:

`REQUEST → INSPECT → SPEC → PLAN → IMPLEMENT → VERIFY → EVIDENCE → APPROVE`

O fluxo torna intenção, decisões, implementação e comprovação rastreáveis. A passagem entre fases depende de critérios objetivos e, nos gates definidos, de decisão humana explícita. Uma spec aprovada autoriza somente o escopo nela descrito; não transforma protótipos, patches ou experimentos em capacidades oficiais.

Esta rodada cria apenas a fundação documental. Não autoriza implementação, mudança de tool, incorporação de experimento, release ou publicação.

Plano aprovado para esta fundação: `PLAN-001-spec-driven-engineering-foundation.md`.

## 2. Objetivo

Estabelecer um processo único, auditável e proporcional ao risco para:

- converter solicitações em requisitos verificáveis antes de alterar o produto;
- separar fatos observados, hipóteses, decisões e trabalho aprovado;
- controlar mudanças de contrato, compatibilidade, dados, segurança e operação;
- exigir evidência reproduzível para aceite;
- permitir manutenção, revisão e rollback com rastreabilidade;
- impedir que experimentos ou workspaces externos entrem no baseline por acidente.

## 3. Escopo

Esta metodologia governa mudanças no próprio `data-engineering-mcp`, incluindo:

- código, testes, dependências e configuração do projeto;
- contratos MCP e suas tools;
- modelos, catálogo, relacionamentos, geração e explicação de SQL;
- documentação de produto e arquitetura;
- correções, manutenção, refatorações, segurança e compatibilidade;
- experimentos que possam futuramente originar mudanças no produto;
- preparação de releases e revisão de mudanças, quando autorizadas por specs futuras.

## 4. Não-escopo

Esta spec não:

- implementa código ou modifica as 12 tools da v0.1.0;
- incorpora qualquer capacidade preservada do experimento BI S/CEP;
- altera ou versiona os 11 XLSX locais;
- acessa ou altera Power BI, Power BI MCP, bancos ou serviços externos;
- altera configuração global do Codex ou cria uma skill;
- define a metodologia operacional da futura skill `data-engineering-spec-driven`;
- autoriza commit, push, release ou publicação;
- substitui decisões humanas de produto, risco, segurança ou compatibilidade.

## 5. Separação obrigatória entre as duas metodologias

### 5.1 Metodologia deste documento

A SPEC-001 governa o ciclo de desenvolvimento do repositório e do produto `data-engineering-mcp`: como suas mudanças são solicitadas, investigadas, especificadas, planejadas, implementadas, verificadas, evidenciadas e aprovadas.

### 5.2 Futura skill `data-engineering-spec-driven`

A futura skill será um artefato separado, proposto pela SPEC-005. Ela poderá aplicar uma metodologia semelhante a tarefas de engenharia de dados — por exemplo, construção, manutenção e revisão de tabelas, relacionamentos e consultas — usando capacidades determinísticas do MCP.

Semelhança de etapas não implica identidade de escopo, implementação ou autoridade. A SPEC-001 não define o contrato da skill, não embute raciocínio de agente no núcleo do MCP e não autoriza sua criação. A skill deverá ter requisitos, riscos, gates, testes e evidências próprios.

## 6. Princípios normativos

Os termos **DEVE**, **NÃO DEVE**, **DEVERIA** e **PODE** indicam obrigação, proibição, recomendação e opção, respectivamente.

1. **Baseline explícito:** toda spec DEVE declarar a versão ou commit de partida.
2. **Inspeção antes de solução:** decisões DEVEM se apoiar no estado observado do projeto, não em memória ou presunção.
3. **Spec antes de implementação:** mudança de comportamento ou contrato NÃO DEVE começar sem spec aprovada.
4. **Escopo mínimo:** cada spec DEVE resolver um objetivo delimitado e listar seu não-escopo.
5. **Fato separado de hipótese:** inferências DEVEM ser rotuladas e não podem ser promovidas a contrato sem decisão.
6. **Compatibilidade por padrão:** mudanças DEVEM ser aditivas e preservar contratos existentes, salvo aprovação explícita de quebra.
7. **Segurança fechada:** ausência de evidência ou ambiguidade relevante bloqueia comportamentos potencialmente inseguros.
8. **Evidência reproduzível:** alegações de conclusão DEVEM apontar para resultados verificáveis.
9. **Aprovação humana:** automação pode recomendar; somente o HUMAN/Product Owner decide gates de produto.
10. **Experimento não é produto:** utilidade, generalidade aparente ou sucesso local não constituem aprovação.
11. **Dados locais não são código:** datasets permanecem externos ao versionamento salvo decisão específica e análise de risco.
12. **Proporcionalidade:** rigor e volume de artefatos aumentam com risco, impacto e irreversibilidade, sem eliminar campos obrigatórios.
13. **Uma autorização não se propaga:** aprovar uma fase não aprova automaticamente a fase seguinte.
14. **Sem aprovação retroativa tácita:** código ou documentos preexistentes fora do baseline precisam de uma spec própria para entrar no produto.

## 7. Papéis e responsabilidades

| Papel | Responsabilidades | Autoridade exclusiva |
|---|---|---|
| Solicitante | Expõe necessidade, contexto, restrições e resultado esperado | Aceitar que a necessidade foi compreendida |
| Spec Owner | Mantém a spec, rastreabilidade, perguntas e decisões | Propor status e revisões |
| Implementer | Executa somente o plano aprovado e registra desvios | Parar e devolver a spec se o plano deixar de ser válido |
| Reviewer | Revisa requisitos, desenho, diffs, testes, riscos e evidências | Recomendar aprovação, rejeição ou retrabalho |
| Verifier | Executa ou audita verificações independentes quando o risco exigir | Declarar evidência suficiente ou insuficiente |
| HUMAN/Product Owner | Decide valor, prioridade, escopo, compatibilidade e risco residual | Aprovar SPEC, autorizar IMPLEMENT e dar aceite final |

Uma pessoa pode acumular papéis, mas o registro DEVE indicar quem tomou cada decisão. Mudança de alto risco DEVERIA ter Reviewer/Verifier diferente do Implementer. Agentes e automações não ocupam o papel HUMAN/Product Owner.

## 8. Estados da spec

Fluxo normal:

`DRAFT → PROPOSED → APPROVED_FOR_IMPLEMENTATION → IMPLEMENTING → VERIFYING → AWAITING_ACCEPTANCE → ACCEPTED → SUPERSEDED`

Estados excepcionais: `BLOCKED`, `REJECTED`, `WITHDRAWN`.

| Estado | Significado |
|---|---|
| DRAFT | Documento incompleto, sem pedido formal de decisão |
| PROPOSED | Pronto para revisão do gate de spec |
| APPROVED_FOR_IMPLEMENTATION | Escopo e plano autorizados pelo HUMAN/Product Owner |
| IMPLEMENTING | Implementação autorizada em andamento |
| VERIFYING | Escopo implementado; verificações em andamento |
| AWAITING_ACCEPTANCE | Evidências completas; aguardando aceite humano |
| ACCEPTED | Critérios atendidos e risco residual aceito |
| SUPERSEDED | Substituída por spec posterior identificada |
| BLOCKED | Impedimento registrado, com condição objetiva de desbloqueio |
| REJECTED | Proposta recusada, com motivo e decisão registrados |
| WITHDRAWN | Retirada antes do aceite, com justificativa |

Somente o HUMAN/Product Owner pode mover uma spec para `APPROVED_FOR_IMPLEMENTATION` ou `ACCEPTED`. Reabertura após aceite exige nova revisão registrada; mudanças materiais exigem nova versão da spec ou uma nova spec dependente.

## 9. Gates humanos

| Gate | Momento | Decisão requerida |
|---|---|---|
| G0 — Request reconhecido | REQUEST → INSPECT | Confirmar problema, objetivo e restrições quando houver ambiguidade material |
| G1 — Spec aprovada | SPEC → PLAN/IMPLEMENT | Aprovar escopo, não-escopo, critérios de aceite, riscos e decisões abertas resolvidas |
| G2 — Implementação autorizada | PLAN → IMPLEMENT | Autorizar execução do plano, arquivos afetados, orçamento de mudança e estratégia de rollback |
| G3 — Desvio material | Durante IMPLEMENT/VERIFY | Aprovar mudança de escopo, contrato, risco, dependência ou estratégia; sem aprovação, parar |
| G4 — Aceite | EVIDENCE → APPROVE | Aceitar evidências, impactos e risco residual; decidir próximos passos |
| G5 — Quebra/release | Antes de quebra, migração ou publicação | Autorizar depreciação, mudança incompatível, versão e release |

G1 e G2 PODEM ocorrer na mesma decisão apenas quando a spec contém plano completo e o decisor declara explicitamente ambas as aprovações. O silêncio nunca é aprovação.

## 10. Artefatos obrigatórios

Cada mudança governada DEVE manter, na própria spec ou por links estáveis:

1. cabeçalho: ID, título, owner, status, baseline e datas;
2. request normalizado e fonte da solicitação;
3. relatório de inspeção com fatos, hipóteses e lacunas;
4. objetivo, escopo e não-escopo;
5. requisitos funcionais e não funcionais identificados;
6. decisões e alternativas relevantes;
7. análise de impacto, dependências, compatibilidade, segurança e dados;
8. plano de implementação com arquivos/componentes previstos;
9. matriz de rastreabilidade;
10. plano de verificação e critérios de aceite;
11. plano de rollback ou justificativa documentada de não aplicabilidade;
12. índice/manifesto de evidências;
13. registro de aprovações, rejeições, desvios e risco residual;
14. resultado final e Definition of Done.

Para mudanças pequenas, os itens podem ser seções concisas no mesmo arquivo; não podem ser omitidos silenciosamente.

## 11. Estrutura, pastas e nomenclatura

Estrutura canônica proposta:

```text
specs/
├── README.md                         # índice e convenções, quando necessário
├── SPEC-001-spec-driven-engineering-foundation.md
├── SPEC-NNN-slug-descritivo.md
└── evidence/
    └── SPEC-NNN/
        ├── README.md                 # manifesto da evidência
        └── ...                       # somente evidência segura e versionável
```

Regras:

- IDs são sequenciais, imutáveis e nunca reutilizados: `SPEC-001`, `SPEC-002` etc.
- Arquivos usam `SPEC-NNN-slug-em-kebab-case.md`.
- O ID identifica a decisão; revisão material preserva histórico em Git e registra versão/revisão no documento.
- Evidência versionada fica em `specs/evidence/SPEC-NNN/` e NÃO DEVE conter segredos, dados pessoais, datasets locais ou saídas sensíveis.
- Evidência externa deve ser referenciada por localização, data, hash quando aplicável e política de retenção; sua ausência futura deve ser tratada como risco.
- Implementações, protótipos e datasets NÃO DEVEM ser guardados dentro de `specs/`.

Nesta rodada, somente o arquivo da SPEC-001 é criado. O índice e diretórios de evidência surgem quando houver necessidade aprovada.

## 12. Fases e critérios de entrada/saída

### 12.1 REQUEST

**Entrada:** necessidade, problema, incidente ou oportunidade identificada.

**Atividades:** registrar solicitante, contexto, resultado esperado, urgência, restrições, exemplos e dúvidas.

**Saída:** request normalizado, com problema e resultado desejado distinguíveis da solução sugerida.

**Critério de saída:** objetivo inspecionável e restrições críticas registradas; ambiguidades materiais seguem como perguntas explícitas.

### 12.2 INSPECT

**Entrada:** request reconhecido e baseline candidato.

**Atividades:** confirmar estado Git, versão, arquitetura, contratos, testes, dados locais, dependências e histórico relevante; classificar fatos, inferências e desconhecidos; não alterar produto.

**Saída:** relatório de inspeção e mapa inicial de impacto.

**Critério de saída:** baseline comprovado, lacunas registradas e evidência suficiente para especificar sem inventar o estado atual.

### 12.3 SPEC

**Entrada:** inspeção concluída.

**Atividades:** definir objetivo, escopo/não-escopo, requisitos, invariantes, compatibilidade, riscos, critérios de aceite, rollback e decisões abertas.

**Saída:** spec em `PROPOSED`.

**Critério de saída:** requisitos testáveis, decisões materiais resolvidas ou explicitamente submetidas ao G1, e nenhuma autorização implícita.

### 12.4 PLAN

**Entrada:** spec aprovada no G1.

**Atividades:** decompor trabalho, ordenar dependências, indicar componentes/arquivos, verificações, evidências, checkpoints e rollback.

**Saída:** plano executável e limitado ao escopo aprovado.

**Critério de saída:** cada passo rastreia requisito e verificação; riscos têm mitigação; G2 registrado.

### 12.5 IMPLEMENT

**Entrada:** G2 explícito e árvore de trabalho compreendida.

**Atividades:** alterar somente o necessário, preservar mudanças alheias, criar/ajustar testes, registrar decisões e interromper em caso de desvio material.

**Saída:** mudança candidata, sem alegação prematura de conclusão.

**Critério de saída:** plano executado, diff revisável, desvios registrados/aprovados e rollback ainda viável.

### 12.6 VERIFY

**Entrada:** implementação candidata e plano de verificação.

**Atividades:** executar testes e análises proporcionais ao risco; validar critérios, regressão, segurança, compatibilidade, contratos e artefatos protegidos.

**Saída:** resultados brutos e avaliação por critério.

**Critério de saída:** todas as verificações obrigatórias executadas; falhas corrigidas e repetidas, ou exceções submetidas à decisão humana.

### 12.7 EVIDENCE

**Entrada:** verificação concluída.

**Atividades:** organizar manifesto, comandos/métodos, ambiente, timestamps, resultados, diffs, limitações e hashes relevantes; remover ou excluir conteúdo sensível.

**Saída:** pacote de evidência reproduzível e matriz de rastreabilidade final.

**Critério de saída:** cada critério de aceite aponta para evidência suficiente, acessível e segura; lacunas estão visíveis.

### 12.8 APPROVE

**Entrada:** spec, mudança e evidências completas.

**Atividades:** revisão humana de resultado, impactos, desvios e risco residual.

**Saída:** `ACCEPTED`, `REJECTED`, `BLOCKED` ou retorno a fase anterior, com decisão registrada.

**Critério de saída:** decisor, data, decisão, condições e próximos passos documentados. Commit, push ou release continuam dependendo da autorização específica aplicável.

## 13. Rastreabilidade

Cada requisito recebe identificador estável (`REQ-001`, `NFR-001`); riscos usam `RISK-001`; decisões, `DEC-001`; critérios de aceite, `AC-001`; evidências, `EV-001`.

A matriz mínima deve relacionar:

| Request | Requisito | Decisão/plano | Mudança | Verificação | Evidência | Critério | Resultado |
|---|---|---|---|---|---|---|---|

Regras:

- todo requisito aprovado DEVE ter pelo menos um critério de aceite;
- toda mudança de comportamento DEVE apontar para requisito e verificação;
- todo critério DEVE apontar para evidência ou registrar por que não foi atendido;
- mudanças sem requisito são escopo excedente e DEVEM ser removidas ou submetidas ao G3;
- links externos devem incluir identidade suficiente para auditoria, sem expor dados protegidos.

## 14. Evidências

Evidência aceitável pode incluir diffs, resultados de testes, smoke tests, contagem/lista de tools, validações de schema, relatórios estáticos, benchmarks controlados, capturas ou logs sanitizados e hashes de artefatos.

Toda evidência DEVE registrar, conforme aplicável:

- o que foi verificado e contra qual requisito/critério;
- método ou comando reproduzível;
- baseline, ambiente e versões relevantes;
- data/hora e resultado esperado/observado;
- limitações, falhas, exceções e risco residual;
- localização e hash quando externa ou sujeita a substituição.

Não são evidência suficiente, isoladamente: “funcionou”, ausência de erro, opinião do implementador, screenshot sem contexto ou resultado sem vínculo com critério.

## 15. Mudança e compatibilidade

### 15.1 Classificação de mudança

- **Documental/processual:** não muda runtime nem contrato.
- **Patch compatível:** corrige comportamento sem remover contrato suportado.
- **Aditiva compatível:** adiciona capacidade sem alterar consumidores existentes.
- **Incompatível:** remove, renomeia, muda semântica, schema, defaults ou garantias observáveis.
- **Emergencial:** reduz dano imediato; exige registro e revisão posterior, sem dispensar evidência.

### 15.2 Regras

- Compatibilidade é avaliada sobre tools, nomes, argumentos, tipos, respostas, erros, segurança, configuração e comportamento documentado.
- Mudança incompatível exige justificativa, consumidores afetados, alternativa aditiva analisada, migração, depreciação, rollback, versionamento e G5.
- Dependência nova exige análise de necessidade, licença, segurança, operação e impacto offline.
- Toda ampliação de SQL deve preservar a política de somente `SELECT/WITH` e binds seguros, salvo spec e decisão explícitas que redefinam o produto.
- Alteração do número ou contrato das 12 tools do baseline exige spec específica; a SPEC-001 não a autoriza.
- Correções emergenciais podem iniciar com documentação mínima, desde que o HUMAN autorize o modo emergencial; a spec e as evidências devem ser completadas antes do aceite.

## 16. Experimentos e workspaces externos

Experimentos DEVEM ocorrer fora do baseline canônico ou em área explicitamente isolada. Devem possuir objetivo, baseline, owner, prazo/retenção e aviso “NÃO É PRODUTO”.

Para promover qualquer parte de um experimento ao produto, é obrigatório:

1. abrir nova REQUEST independente;
2. inspecionar o baseline atual e o artefato experimental sem presumir validade;
3. identificar proveniência, licença, dados, segurança e dependências;
4. reespecificar a capacidade como requisito genérico do produto;
5. avaliar alternativas, compatibilidade e risco;
6. obter G1 e G2 explícitos;
7. implementar de forma limpa, com testes próprios — não apenas copiar o patch;
8. verificar e obter aceite pelos gates normais.

Referenciar, preservar ou testar um experimento NÃO o legitima. Código “genérico em aparência” continua experimental até concluir o fluxo.

Datasets locais, consultas de cliente, benchmarks específicos, backups, arquivos `.bak`, `before_*`, `patch_*`, `fix_*` e produtos de investigação não pertencem ao repositório por padrão. Devem permanecer ignorados ou externamente preservados conforme sua política, sem serem apagados apenas por esta regra.

## 17. Regra específica para o experimento BI S/CEP

O pacote BI S/CEP preservado é exclusivamente evidência histórica/experimental externa. Nenhuma de suas ideias ou implementações — incluindo relacionamentos explícitos, expressões `ON`, `DISTINCT`, `GROUP BY`, agregações, `KEEP (DENSE_RANK ...)`, composição de CTEs ou `EXISTS` — é requisito, contrato, backlog aprovado ou extensão legitimada do `data-engineering-mcp`.

Cada capacidade somente poderá ser considerada futuramente mediante request própria, justificativa genérica independente do caso S/CEP, inspeção atualizada, spec aprovada, implementação limpa, verificação e aceite. A aprovação da SPEC-001 não aprova nenhuma delas, individualmente ou em conjunto.

## 18. Rollback e recuperação

Toda spec que autorize mudança DEVE definir:

- estado conhecido para retorno (commit/tag/versão/configuração);
- gatilhos objetivos de rollback;
- passos ordenados e responsável;
- tratamento de migração e compatibilidade de dados, quando houver;
- como verificar que o retorno foi concluído;
- artefatos que devem ser preservados para diagnóstico;
- limites de reversibilidade e riscos de perda.

Antes de IMPLEMENT, o baseline deve estar identificável e mudanças não relacionadas devem ser preservadas. Rollback não pode depender de destruir dados locais ou trabalho do usuário. Operações irreversíveis exigem aprovação explícita e plano de recuperação testado ou risco residual formalmente aceito.

Para mudanças apenas documentais, rollback consiste em reverter exclusivamente os arquivos documentais da mudança, preservando histórico e demais alterações.

## 19. Critérios de aceite da SPEC-001

- **AC-001:** o fluxo canônico contém as oito fases, com entrada, saída e critério de saída.
- **AC-002:** estados da spec, papéis e gates humanos estão definidos e reservam aprovação ao HUMAN/Product Owner.
- **AC-003:** artefatos, estrutura, nomenclatura, rastreabilidade e evidências têm regras mínimas verificáveis.
- **AC-004:** compatibilidade, mudanças, experimentos externos e rollback estão governados.
- **AC-005:** escopo e não-escopo proíbem implementação, alteração das 12 tools e interferência nos 11 XLSX, Power BI MCP, Codex global, commits, pushes e releases nesta rodada.
- **AC-006:** a metodologia do projeto está explicitamente separada da futura skill `data-engineering-spec-driven`.
- **AC-007:** a spec declara inequivocamente que o experimento BI S/CEP e suas extensões não são legitimados automaticamente.
- **AC-008:** o roadmap SPEC-002 a SPEC-007 é apenas documental e não cria requisitos aprovados para essas specs futuras.
- **AC-009:** a spec está ancorada no baseline v0.1.0 `862abae4237997bc7165b27a4fc179429ff11359`.
- **AC-010:** nenhum arquivo de runtime, teste, dataset ou integração é alterado pela criação desta spec.

## 20. Definition of Done

A SPEC-001 estará **pronta para aceite** quando:

- todos os critérios AC-001 a AC-010 estiverem revisados com evidência documental;
- decisões humanas abertas estiverem respondidas ou aceitas como condições explícitas;
- o único impacto no repositório for a documentação autorizada;
- a árvore continue baseada no commit declarado, sem mudanças prévias inesperadas;
- nenhum XLSX tenha sido modificado, adicionado ao Git ou lido além do necessário para confirmar inventário;
- nenhuma tool, código, teste, configuração, Power BI MCP ou Codex global tenha sido alterado;
- a validação de não-legitimação do BI S/CEP esteja registrada;
- o HUMAN/Product Owner registre `ACCEPTED` ou solicite revisão.

Aceitar esta spec torna a metodologia canônica para specs futuras. Não concede autorização de implementação além da manutenção documental necessária à própria governança.

## 21. Roadmap documental proposto (não criado e não autorizado)

| ID futuro | Título proposto | Propósito documental | Dependência/gate principal |
|---|---|---|---|
| SPEC-002 | Metadata & Relationship Authority | Definir fontes de verdade, metadados explícitos, confiança, cardinalidade, homologação e governança de relacionamentos | Aceite da SPEC-001; decisões humanas sobre autoridade e persistência |
| SPEC-003 | Structured Query Planning | Definir modelo de plano de consulta, grão, projeções, filtros, joins, fan-out e representação intermediária | SPEC-002 aceita; contrato de planejamento aprovado |
| SPEC-004 | SQL Validation & Safety Gates | Definir validações Oracle, segurança, compatibilidade, limites e evidências antes de emitir SQL | SPEC-003 aceita; política de risco aprovada |
| SPEC-005 | Data Engineering Spec Skill | Especificar separadamente a skill `data-engineering-spec-driven`, seus modos, contratos, uso das tools e gates para tabelas, relacionamentos e consultas | SPEC-002 a 004 aceitas; fronteira skill/MCP aprovada |
| SPEC-006 | Maintenance & Review Workflows | Definir fluxos operacionais de manutenção, revisão, incidentes, depreciação e evolução contínua | Aprendizados das SPEC-002 a 005 |
| SPEC-007 | Practical BI Integration Validation | Definir cenário controlado ponta a ponta de necessidade BI até consulta Oracle validada, sem transformar caso específico em contrato | Capacidades anteriores aceitas; dataset e integrações autorizados |

O roadmap expressa sequência e intenção, não conteúdo aprovado. Cada item deverá começar em REQUEST/INSPECT, pode ser dividido, reordenado ou rejeitado pelo HUMAN/Product Owner e não herda automaticamente artefatos do BI S/CEP.

## 22. Decisões que exigem HUMAN/Product Owner

Antes do aceite desta spec:

- **DEC-001:** aprovar `specs/` e o padrão `SPEC-NNN-slug.md` como estrutura canônica.
- **DEC-002:** confirmar que G1 (spec) e G2 (implementação) permanecem gates distintos por padrão.
- **DEC-003:** aprovar os estados e a autoridade exclusiva humana para `APPROVED_FOR_IMPLEMENTATION` e `ACCEPTED`.
- **DEC-004:** aprovar compatibilidade aditiva como padrão e G5 para quebras/releases.
- **DEC-005:** aprovar a política de isolamento e promoção de experimentos.
- **DEC-006:** aprovar a separação arquitetural entre metodologia do MCP e futura skill.
- **DEC-007:** aprovar somente a ordem indicativa do roadmap, sem autorizar criação ou implementação das SPEC-002 a SPEC-007.

## 23. Riscos e ônus da adoção

| Risco/ônus | Efeito | Mitigação |
|---|---|---|
| Sobrecarga documental | Mudanças simples podem parecer lentas | Artefatos concisos e proporcionais, mantendo campos mínimos |
| Gates virarem gargalo | Espera por decisão humana | Owner e critérios claros; combinar G1/G2 somente de forma explícita |
| Evidência externa desaparecer | Auditoria incompleta | Manifesto, hash, retenção e evidência segura no repositório quando possível |
| Specs divergirem do código | Falsa confiança | Rastreabilidade, revisão de diff e atualização antes do aceite |
| Processo rígido demais em incidente | Atraso na contenção | Caminho emergencial autorizado e regularização obrigatória |
| Promoção acidental de protótipos | Dívida e contrato não intencional | Regra de não legitimação e fluxo completo de promoção |
| Acúmulo de specs obsoletas | Navegação e manutenção difíceis | Estados `SUPERSEDED/WITHDRAWN` e futuro índice canônico |

## 24. Validação documental desta proposta

| Verificação | Resultado |
|---|---|
| Baseline declarado corresponde ao commit solicitado | PASS |
| Fluxo de oito fases está completo | PASS |
| Objetivo, escopo, não-escopo e princípios estão definidos | PASS |
| Estados, papéis, gates e artefatos obrigatórios estão definidos | PASS |
| Pastas, nomenclatura, entradas/saídas e rastreabilidade estão definidos | PASS |
| Evidências, compatibilidade, experimentos e rollback estão definidos | PASS |
| Critérios de aceite e Definition of Done estão definidos | PASS |
| Metodologia do MCP e futura skill estão separadas | PASS |
| Roadmap SPEC-002 a SPEC-007 é somente proposta | PASS |
| Extensões do BI S/CEP recebem legitimidade automática | **NÃO — PASS** |

## 25. Encerramento

Status final: `ACCEPTED`. Resultado: `DONE`.

O HUMAN/Product Owner aceitou no G4 as evidências documentais e o risco residual. A SPEC-001 passa a ser a referência canônica de governança do projeto. O aceite não autoriza implementação de capacidades futuras; cada nova spec continua sujeita a G1 e G2 próprios.

## 26. Registro de aprovação

| Gate | Decisor | Data | Decisão | Condições/observações |
|---|---|---|---|---|
| G1 — SPEC-001 | HUMAN/Product Owner | 2026-09-11 | Aprovado | Spec-Driven enxuto; simplicidade e proporcionalidade são restrições do projeto |
| G2 — PLAN-001 | HUMAN/Product Owner | 2026-09-11 | Aprovado | Implementação exclusivamente documental, limitada à SPEC-001 e ao PLAN-001 |
| G4 — Aceite final | HUMAN/Product Owner | 2026-09-11 | Aprovado | Evidências 5/5 PASS; risco residual aceito; SPEC-001 encerrada como DONE/ACCEPTED |
