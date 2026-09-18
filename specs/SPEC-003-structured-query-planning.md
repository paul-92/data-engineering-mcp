# SPEC-003 — Structured Query Planning

| Campo | Valor |
|---|---|
| ID | SPEC-003 |
| Título | Structured Query Planning |
| Tipo | Proposta funcional aditiva |
| Status | ACCEPTED |
| Resultado | DONE |
| Baseline de referência | `data-engineering-mcp` v0.1.0, commit `862abae4237997bc7165b27a4fc179429ff11359`, com SPEC-002 aceita |
| Product Owner | HUMAN |
| Implementação autorizada | Concluída e aceita no G4 |
| Última atualização | 2026-09-11 |

## 1. Objetivo

Definir o menor contrato útil para representar, de forma estruturada e revisável, a intenção de uma consulta antes da geração SQL. O contrato deve tornar explícito o que será consultado e o que ainda depende de autoridade, sem executar planejamento autônomo.

## 2. Contrato mínimo proposto

Uma intenção de consulta deve poder declarar somente:

- `sources`: fontes ou tabelas necessárias;
- `output_columns`: colunas de saída, com alias apenas quando necessário;
- `filters`: condições solicitadas, com campo, operador e valor ou referência;
- `relationships`: relacionamentos necessários entre fontes, referenciando a autoridade definida na SPEC-002;
- `grain`: nível de detalhe esperado, somente quando aplicável;
- `warnings`: ambiguidades, riscos ou limitações identificadas;
- `authority_pending`: decisões ou confirmações humanas ainda necessárias.

Campos não aplicáveis podem ser omitidos ou permanecer vazios. A representação deve ser simples, serializável e determinística; nomes finais e formato de exposição ficam para um eventual PLAN-003 após G1.

## 3. Regras e comportamento esperado

1. A estrutura representa intenção; não gera, executa nem otimiza SQL por si só.
2. Fontes, colunas e filtros devem permanecer rastreáveis ao pedido do consumidor.
3. Todo relacionamento necessário deve apontar para autoridade disponível; `INFERRED`, conflito ou ausência de autoridade gera aviso ou pendência, nunca aprovação implícita.
4. `grain` é informado apenas quando necessário para evitar ambiguidade de agregação ou nível de detalhe.
5. Avisos e pendências devem permanecer visíveis para revisão antes da geração SQL.
6. A evolução deve ser estritamente aditiva e preservar as 12 tools atuais.

## 4. Não-escopo

- Criar DSL complexa, planner autônomo, otimizador, framework ou infraestrutura nova.
- Definir algoritmo de busca de caminhos, custo, reescrita, execução ou geração completa de SQL.
- Adicionar, remover ou alterar semanticamente tools nesta proposta.
- Criar PLAN-003, código, testes, schemas persistidos ou implementação.
- Reintroduzir automaticamente recursos, contratos ou artefatos do experimento BI S/CEP.
- Alterar runtime, metadata, datasets, Power BI MCP, Codex global, Git remoto ou release.

## 5. Critérios de aceite para a futura solução

- **AC-001:** o contrato cobre fontes/tabelas, colunas de saída, filtros, relacionamentos necessários, grain quando aplicável, avisos e pendências de autoridade.
- **AC-002:** ausência, conflito ou insuficiência de autoridade é explícita e não é resolvida silenciosamente.
- **AC-003:** uma intenção pode ser revisada antes de qualquer geração SQL.
- **AC-004:** a solução permanece aditiva, proporcional e compatível com as 12 tools.
- **AC-005:** nenhum componente de planner autônomo, otimizador, framework ou BI S/CEP é incorporado sem nova decisão humana.

## 6. Impactos positivos e riscos/ônus

**Impactos positivos:** melhora a rastreabilidade entre pedido e SQL futuro; antecipa ambiguidades de fonte, JOIN e grain; permite revisão humana com um contrato pequeno; reutiliza a autoridade de relacionamentos da SPEC-002.

| Risco/ônus | Mitigação proposta |
|---|---|
| Contrato crescer para uma linguagem própria | Limitar aos sete elementos da seção 2; expansão exige necessidade e decisão próprias |
| Representação duplicar lógica do gerador SQL | Manter o contrato declarativo, sem execução ou otimização |
| Grain ser exigido sem necessidade | Torná-lo opcional e usá-lo apenas quando houver ambiguidade relevante |
| Consumidor ignorar avisos | Manter avisos e pendências explícitos antes da geração SQL |
| Autoridade incompleta bloquear consultas simples | Distinguir aviso de pendência que exige decisão, com política definida apenas em plano futuro |

## 7. Decisões HUMAN/Product Owner para G1

1. Aprovar o contrato mínimo e seus sete elementos.
2. Aprovar que a estrutura represente somente intenção, sem planner autônomo, otimização, execução ou geração SQL nesta spec.
3. Aprovar que relacionamentos usem a autoridade da SPEC-002 e que insuficiências permaneçam explícitas.
4. Aprovar `grain` como campo opcional, usado somente quando aplicável.
5. Confirmar compatibilidade aditiva e preservação das 12 tools atuais.
6. Confirmar todo o não-escopo, especialmente a não incorporação automática do BI S/CEP.
7. Autorizar, se aprovada a spec, somente a criação posterior de um PLAN-003 curto; implementação continuará dependendo de G2 separado.

## 8. Gate atual

**G4 — APPROVED em 2026-09-11 pelo HUMAN/Product Owner.** As evidências da implementação e o risco residual foram aceitos. Status final: `ACCEPTED`. Resultado: `DONE`.

## 9. Registro de aprovação

| Gate | Decisor | Data | Decisão | Condições/observações |
|---|---|---|---|---|
| G1 — SPEC-003 | HUMAN/Product Owner | 2026-09-11 | APPROVED | Criar somente um PLAN-003 curto e proporcional; não implementar; preservar as 12 tools e todo o não-escopo |
| G2 — PLAN-003 | HUMAN/Product Owner | 2026-09-11 | APPROVED | Executar somente IMPLEMENT → VERIFY → EVIDENCE no escopo travado e parar no gate de aceite |
| G4 — Aceite final | HUMAN/Product Owner | 2026-09-11 | APPROVED | Evidências aceitas; risco residual aceito; SPEC-003 encerrada como ACCEPTED/DONE |

## 10. Encerramento

O contrato declarativo foi entregue em `query_intent.py`, com testes e documentação, sem nova tool e preservando exatamente as 12 existentes. As verificações aceitas foram: 11 testes específicos, 42 testes na suíte completa, smoke MCP e `git diff --check`, todos com resultado PASS.

O risco residual de permanecer uma primitiva interna foi aceito. Este encerramento não autoriza commit, push, release nem a implementação de etapa posterior.
