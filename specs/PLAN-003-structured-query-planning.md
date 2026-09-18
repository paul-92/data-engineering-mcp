# PLAN-003 — Structured Query Planning

| Campo | Valor |
|---|---|
| Spec | `SPEC-003` |
| Baseline | `862abae4237997bc7165b27a4fc179429ff11359`, com SPEC-002 aceita |
| Gate de entrada | G1 aprovado em 2026-09-11 pelo HUMAN/Product Owner |
| Status | `COMPLETED` |
| Implementação autorizada | Sim — G2 aprovado em 2026-09-11; execução concluída e aceita no G4 |

## 1. Objetivo e solução mínima

Materializar, antes da geração SQL, um contrato declarativo, serializável e determinístico para intenção de consulta. O contrato conterá somente `sources`, `output_columns`, `filters`, `relationships`, `grain` opcional, `warnings` e `authority_pending`.

A solução futura será um conjunto pequeno de modelos de dados, sem comportamento de planejamento ou execução. Relacionamentos apenas carregarão sua identidade e a autoridade já produzida pela SPEC-002; não haverá descoberta, promoção ou resolução própria. O contrato não duplicará validação, montagem ou geração do `SQLGenerator`.

## 2. Arquivos mínimos previstos

- Criar `src/data_engineering_mcp/query_intent.py`: modelos mínimos do contrato e serialização determinística.
- Criar `tests/test_query_intent.py`: testes unitários somente do contrato.
- Alterar `README.md`: documentar formato, limites e um exemplo curto.

Não alterar `server.py`, `relationships.py`, `models.py`, `sql_generator.py`, metadata ou datasets. Se a implementação revelar necessidade de qualquer outro arquivo, ela para e retorna ao HUMAN/Product Owner.

**Nova tool: não proposta.** O contrato é uma primitiva interna para consumo futuro; expô-lo agora por uma 13ª tool não é indispensável, criaria interface pública sem caso de uso validado e violaria a decisão de preservar exatamente as 12 tools.

## 3. Comportamento previsto

1. Representar fontes/tabelas e colunas de saída em ordem estável, com alias somente quando informado.
2. Representar filtros como dados declarativos (`field`, `operator`, `value` ou referência), sem interpretar, executar ou converter condições em SQL.
3. Representar relacionamentos necessários com referência explícita à identidade e à `authority` da SPEC-002; `INFERRED`, conflito ou autoridade ausente deve permanecer visível em `warnings` ou `authority_pending`.
4. Permitir omitir `grain`; quando presente, tratá-lo apenas como declaração de nível de detalhe.
5. Preservar avisos e pendências na serialização, sem resolvê-los silenciosamente.
6. Não gerar SQL, selecionar caminhos, otimizar, executar, criar CTEs/`EXISTS`, inferir agregações ou incorporar capacidades do BI S/CEP.

## 4. Testes e verificações mínimas

- Contrato mínimo com fonte e coluna serializa de modo estável.
- Contrato completo cobre exatamente os sete elementos e preserva aliases, filtros e `grain`.
- `grain` pode ser omitido.
- Relacionamentos preservam `APPROVED`, `KNOWN` e `INFERRED` recebidos da SPEC-002 sem promoção.
- Autoridade ausente, `INFERRED` ou conflitante permanece explícita em aviso ou pendência.
- A estrutura não chama nem replica o `SQLGenerator` e não produz SQL.
- Suíte existente continua passando e a enumeração permanece em exatamente 12 tools.
- Diff final fica restrito aos três arquivos da seção 2 e não inclui metadata, datasets, Power BI MCP, Codex global, Git remoto ou release.

## 5. Rollback

Remover `src/data_engineering_mcp/query_intent.py` e `tests/test_query_intent.py` e reverter somente a seção adicionada ao `README.md`. Confirmar que a suíte anterior continua passando e que as 12 tools e os artefatos protegidos permanecem inalterados. Não haverá migração, persistência ou conversão de dados.

## 6. Critérios de aceite

- **AC-P3-001:** os sete elementos da SPEC-003 são representáveis em contrato pequeno, declarativo e serializável.
- **AC-P3-002:** `grain` é opcional e avisos/pendências permanecem explícitos.
- **AC-P3-003:** relacionamentos reutilizam a autoridade da SPEC-002 sem inferência, promoção ou resolução paralela.
- **AC-P3-004:** nenhum SQL é gerado ou executado e nenhuma lógica do `SQLGenerator` é duplicada.
- **AC-P3-005:** nenhuma DSL complexa, planner, otimizador, executor, framework, infraestrutura ou capacidade automática do BI S/CEP é introduzida.
- **AC-P3-006:** nenhuma nova tool é criada; as 12 tools e contratos existentes permanecem compatíveis.
- **AC-P3-007:** os testes mínimos passam e o rollback é executável apenas sobre os três arquivos previstos.

## 7. Impactos positivos e riscos/ônus

**Impactos positivos:** torna a intenção revisável antes do SQL, melhora rastreabilidade, expõe ambiguidades cedo e reutiliza a autoridade já aceita sem ampliar a superfície pública.

| Risco/ônus | Mitigação |
|---|---|
| Modelos crescerem para uma DSL | Limitar campos aos sete elementos; expansão exige nova decisão |
| Duplicação do gerador SQL | Manter somente dados e serialização, sem tradução para SQL |
| Autoridade ser reinterpretada | Consumir os estados da SPEC-002 sem promover ou resolver |
| `grain` virar requisito artificial | Campo opcional, sem validação semântica avançada |
| Consumidor ignorar avisos | Preservar `warnings` e `authority_pending` explicitamente |
| Módulo ainda não ter interface pública | Aceitar como primitiva interna; validar necessidade antes de propor tool |

## 8. Decisões HUMAN/Product Owner para G2

1. Autorizar somente os três arquivos da seção 2 e a solução de modelos declarativos em um único módulo.
2. Confirmar que não haverá nova tool e que as 12 atuais serão preservadas.
3. Aprovar que o contrato apenas carregue autoridade da SPEC-002, sem descoberta ou política paralela.
4. Aprovar os testes mínimos, critérios de aceite e rollback deste plano.
5. Confirmar a exclusão de SQL, DSL, planner, otimizador, executor, framework, infraestrutura e extensões do BI S/CEP.
6. Determinar que qualquer arquivo adicional, mudança pública incompatível ou necessidade de nova tool interrompa a execução e retorne para decisão.

## 9. Registro de G2, evidências e encerramento

**G2 — APPROVED em 2026-09-11 pelo HUMAN/Product Owner.** Autorizada somente a execução de IMPLEMENT → VERIFY → EVIDENCE dentro do escopo travado deste plano.

Evidências aceitas em 2026-09-11:

- implementação restrita a `query_intent.py`, `test_query_intent.py` e `README.md`;
- 11 testes específicos e 42 testes na suíte completa: PASS;
- smoke MCP: PASS, com exatamente 12 tools e nomes originais preservados;
- `git diff --check`: PASS;
- nenhum SQL gerado ou executado pelo contrato e nenhuma lógica do `SQLGenerator` duplicada;
- nenhum commit, push, release ou alteração nos demais itens protegidos.

**G4 — APPROVED em 2026-09-11 pelo HUMAN/Product Owner.** Evidências e risco residual aceitos. O PLAN-003 está `COMPLETED` e a SPEC-003 foi encerrada como `ACCEPTED/DONE`.

Este encerramento não autoriza implementação de capacidades posteriores.
