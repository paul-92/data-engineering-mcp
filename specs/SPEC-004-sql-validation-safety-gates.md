# SPEC-004 — SQL Validation & Safety Gates

| Campo | Valor |
|---|---|
| ID | SPEC-004 |
| Título | SQL Validation & Safety Gates |
| Tipo | Proposta funcional mínima |
| Status | ACCEPTED |
| Resultado | DONE |
| Dependências | SPEC-002 e SPEC-003 aceitas |
| Product Owner | HUMAN |
| Implementação autorizada | Concluída e aceita no G4 |
| Última atualização | 2026-09-16 |

## 1. Necessidade concreta

O MCP já protege nomes de tabelas e colunas pelo catálogo, rejeita colunas ambíguas, restringe operadores de filtro, parametriza valores e impede que o explicador aceite operações fora de `SELECT/WITH`. Também expõe autoridade e conflitos de relacionamentos (SPEC-002) e mantém avisos e pendências na intenção estruturada (SPEC-003).

Resta uma lacuna indispensável: o `SQLGenerator` escolhe relacionamentos por confiança numérica e pelo sinal `allow_low_confidence`, mas não aplica `RelationshipAuthority` nem bloqueia conflitos. Assim, um relacionamento `INFERRED` de confiança alta ou média pode ser usado automaticamente em um `JOIN`, e os avisos ou `authority_pending` da intenção ainda não funcionam como gate antes da emissão do SQL.

## 2. Proposta mínima

Definir um único gate determinístico antes da emissão de SQL com relacionamentos:

1. permitir uso automático somente de relacionamento `APPROVED`, sem conflitos;
2. bloquear `INFERRED`, `KNOWN`, autoridade ausente e qualquer relacionamento com conflito;
3. permitir `JOIN` automático exclusivamente com autoridade `APPROVED` e sem conflitos;
4. retornar erro claro com a relação bloqueada e o motivo, sem promover autoridade nem oferecer bypass genérico;
5. preservar a geração atual para consultas de uma única tabela e todos os controles sintáticos já existentes.

O gate deve reutilizar os modelos da SPEC-002. A futura skill poderá resolver a pendência com o usuário e tentar novamente após autoridade adequada; ela não deverá contornar o gate.

## 3. Não-escopo

- Parser ou validador SQL completo, nova DSL, framework, planner, otimizador ou arquitetura ampla.
- Execução em banco, `EXPLAIN PLAN`, validação de custo, performance, cardinalidade, fan-out ou dialeto Oracle completo.
- Geração automática de agregações, CTEs, `EXISTS`, reescritas ou escolha avançada de caminhos.
- Nova tool ou alteração da quantidade e dos nomes das 12 tools atuais.
- Criar PLAN-004 ou implementar código, testes ou runtime neste gate.
- Alterar datasets, metadata, Power BI MCP, Codex global, Git remoto ou release.

## 4. Critérios de aceite propostos

- **AC-001:** nenhum `JOIN` é emitido automaticamente com autoridade `INFERRED`, ausente ou conflitante.
- **AC-002:** somente `APPROVED` sem conflito é aceito automaticamente; `KNOWN` permanece bloqueado por padrão.
- **AC-003:** bloqueios retornam motivo claro e não promovem autoridade nem permitem bypass genérico.
- **AC-004:** consultas de tabela única e proteções atuais permanecem compatíveis.
- **AC-005:** a solução reutiliza SPEC-002 e SPEC-003, preserva exatamente as 12 tools e não incorpora itens do não-escopo.

## 5. Impactos e riscos/ônus

**Impactos positivos:** fecha a divergência entre confiança heurística e autorização semântica; impede `JOIN` não homologado antes que a futura skill consuma o MCP; mantém a política pequena, auditável e reutilizável.

**Riscos/ônus:** o padrão seguro bloqueará consultas multi-tabela enquanto os relacionamentos não forem aprovados; consumidores atuais que dependam de relacionamentos `INFERRED` ou `KNOWN` poderão precisar de homologação. O ônus é intencional e limitado ao ponto em que há risco semântico real.

## 6. Recomendação e gate atual

**Recomendação: GO**, exclusivamente para esta proposta mínima. A lacuna deve ser fechada antes da SPEC-005 porque confiar somente na futura skill deixaria outro consumidor das tools capaz de emitir SQL com `JOIN` semanticamente não autorizado.

**G1 — APPROVED em 2026-09-11 pelo HUMAN/Product Owner.** Aprovada a política conservadora: `INFERRED` e `KNOWN` não sustentam `JOIN` automático; somente `APPROVED` sem conflitos pode sustentá-lo; qualquer conflito bloqueia a geração. Autorizada somente a criação de um PLAN-004 mínimo e proporcional, com parada obrigatória no G2. Nenhuma implementação está autorizada.

## 7. Registro de aprovação

| Gate | Decisor | Data | Decisão | Condições/observações |
|---|---|---|---|---|
| G1 — SPEC-004 | HUMAN/Product Owner | 2026-09-11 | APPROVED | Reutilizar diretamente a SPEC-002; inserir somente o menor gate na geração SQL multi-tabela; preservar consultas de uma tabela, exatamente 12 tools e compatibilidade aditiva; criar somente o PLAN-004 e parar no G2 |
| G2 — PLAN-004 | HUMAN/Product Owner | 2026-09-16 | APPROVED | Executar somente IMPLEMENT → VERIFY → EVIDENCE no escopo travado e parar no G4 |
| G4 — Aceite final | HUMAN/Product Owner | 2026-09-16 | APPROVED | Evidências, impactos e riscos residuais aceitos; SPEC-004 encerrada como ACCEPTED/DONE |

## 8. Gate atual

**G4 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** As evidências, os impactos e os riscos residuais foram aceitos. Status final: `ACCEPTED`. Resultado: `DONE`.

Este encerramento não autoriza commit, push, release nem implementação da SPEC-005.
