# SPEC-002 — Metadata & Relationship Authority

| Campo | Valor |
|---|---|
| ID | SPEC-002 |
| Título | Metadata & Relationship Authority |
| Tipo | Evolução funcional aditiva |
| Status | ACCEPTED |
| Resultado | DONE |
| Baseline de referência | `data-engineering-mcp` v0.1.0, commit `862abae4237997bc7165b27a4fc179429ff11359`, com SPEC-001 aceita |
| Product Owner | HUMAN |
| Implementação autorizada | Concluída e aceita no G4 |
| Última atualização | 2026-09-11 |

## 1. Objetivo

Permitir que o MCP diferencie, de forma explícita e consumível pela futura skill e pela geração segura de SQL, relacionamentos apenas inferidos daqueles conhecidos ou homologados por uma fonte autorizada.

## 2. Problema

Hoje, coincidências de nomes de colunas podem sugerir relacionamentos, mas não comprovam sua validade. Sem declarar a origem e a autoridade, um consumidor pode tratar uma hipótese como fato e gerar JOINs incorretos, ambíguos ou com fan-out inesperado.

## 3. Escopo mínimo

- Definir uma classificação pequena e inequívoca: `INFERRED`, `KNOWN` e `APPROVED`.
- Expor, para cada relacionamento, sua classificação e a fonte que a sustenta.
- Preservar a inferência atual como hipótese, nunca como homologação implícita.
- Permitir que consumidores distingam relações aptas ao uso automático das que exigem confirmação.
- Definir precedência: metadado explícito válido prevalece sobre inferência conflitante; conflito deve ficar visível, não ser resolvido silenciosamente.

`KNOWN` significa declarado por fonte explícita identificável. `APPROVED` significa homologado por decisão humana registrada. A forma mínima de persistência e exposição está definida no `PLAN-002-metadata-relationship-authority.md`, sujeito ao G2.

## 4. Não-escopo

- Não implementar nesta etapa código, tool, teste, schema ou persistência.
- Não gerar JOINs automaticamente nem ampliar o gerador de SQL.
- Não definir cardinalidade, fan-out, expressões `ON`, caminhos ótimos ou validação de integridade além do necessário para indicar autoridade.
- Não importar automaticamente relacionamentos, código ou capacidades do experimento BI S/CEP.
- Não alterar datasets, Power BI MCP, Codex global, Git remoto ou release.
- Não criar a futura skill. O PLAN-002 é exclusivamente documental e não autoriza implementação.

## 5. Comportamento esperado

1. Um relacionamento descoberto somente por heurística é apresentado como `INFERRED`.
2. Um relacionamento vindo de metadado explícito identificado é apresentado como `KNOWN`.
3. Um relacionamento homologado pelo HUMAN/Product Owner é apresentado como `APPROVED`, com referência à decisão.
4. Ausência de autoridade não é convertida em autoridade por confiança numérica, repetição ou uso anterior.
5. A futura geração segura de SQL pode aceitar `APPROVED`, tratar `KNOWN` conforme política explícita e bloquear ou pedir confirmação para `INFERRED`.
6. Conflitos entre fontes são expostos ao consumidor e impedem promoção automática.

## 6. Compatibilidade aditiva

A evolução deve preservar as 12 tools e os contratos da v0.1.0. A inferência existente continua disponível; os novos sinais de autoridade são informação adicional. Qualquer alteração incompatível, nova tool ou mudança de semântica exige decisão explícita fora desta proposta.

## 7. Critérios de aceite

- **AC-001:** as três classificações têm significado distinto e testável.
- **AC-002:** todo relacionamento exposto informa classificação e fonte; homologação informa também a decisão humana.
- **AC-003:** inferência nunca é promovida silenciosamente a `KNOWN` ou `APPROVED`.
- **AC-004:** precedência e conflitos entre metadado explícito e inferência são determinísticos e visíveis.
- **AC-005:** consumidores conseguem aplicar uma política segura sem interpretar nomes de colunas como prova.
- **AC-006:** a solução planejada é aditiva e preserva contratos existentes.
- **AC-007:** nenhuma capacidade do BI S/CEP entra automaticamente no escopo.

## 8. Riscos

| Risco/ônus | Mitigação proposta |
|---|---|
| Classificação excessiva ou burocrática | Limitar a três estados e aos metadados indispensáveis |
| Fonte explícita incorreta ser tratada como verdade | Separar `KNOWN` de `APPROVED` e manter proveniência visível |
| Consumidores ignorarem a autoridade | Tornar a classificação parte explícita do contrato futuro |
| Conflitos ou metadados desatualizados | Falhar de forma segura e exigir decisão, sem promoção automática |
| Escopo crescer para um catálogo completo | Adiar cardinalidade, descoberta avançada e governança adicional para necessidade própria |

## 9. Avaliação para G1

**Impactos positivos:** reduz JOINs baseados em suposição, dá à futura skill um sinal confiável de autoridade e cria base mínima para políticas seguras de geração de SQL, sem remover a inferência atual.

**Riscos/ônus:** acrescenta proveniência e um pequeno fluxo de homologação; metadados podem ficar desatualizados; consumidores precisarão respeitar a classificação. O escopo curto e a falha segura limitam esses custos.

**Decisões HUMAN/Product Owner:**

1. Aprovar as classificações `INFERRED`, `KNOWN` e `APPROVED` e seus significados.
2. Aprovar que somente decisão humana registrada concede `APPROVED`.
3. Aprovar a precedência do metadado explícito e a exposição obrigatória de conflitos.
4. Aprovar compatibilidade estritamente aditiva, preservando as 12 tools e a inferência atual.
5. Confirmar que persistência, interface e arquivos afetados serão definidos apenas no PLAN-002, após o G1.
6. Confirmar o não-escopo, especialmente a não incorporação automática do experimento BI S/CEP.

## 10. Gate atual

**G1 — APPROVED em 2026-09-11 pelo HUMAN/Product Owner.** Foram aprovadas as decisões 1 a 6 da seção 9, incluindo `APPROVED` exclusivamente humano, precedência do metadado explícito com conflitos visíveis, compatibilidade aditiva e não incorporação automática do BI S/CEP.

G2 foi aprovado em 2026-09-11 pelo HUMAN/Product Owner. A implementação foi concluída e aguarda aceite humano; nenhuma etapa posterior está autorizada.

## 11. Registro de aprovação

| Gate | Decisor | Data | Decisão | Condições/observações |
|---|---|---|---|---|
| G1 — SPEC-002 | HUMAN/Product Owner | 2026-09-11 | APPROVED | Criar somente um PLAN-002 curto e proporcional; manter a solução mínima, preservar as 12 tools e parar no G2 sem implementação |
| G2 — PLAN-002 | HUMAN/Product Owner | 2026-09-11 | APPROVED | Executar somente IMPLEMENT → VERIFY → EVIDENCE no escopo travado e parar no gate de aceite da SPEC-002 |
| G4 — Aceite final | HUMAN/Product Owner | 2026-09-11 | APPROVED | Evidências aceitas; risco residual aceito; SPEC-002 encerrada como ACCEPTED/DONE |

## 12. Encerramento

**G4 — APPROVED em 2026-09-11 pelo HUMAN/Product Owner.** As evidências registradas no PLAN-002 e o risco residual foram aceitos. Status final: `ACCEPTED`. Resultado: `DONE`.

O aceite não autoriza commit, push, release nem implementação de capacidades posteriores. A SPEC-003 permanece sujeita ao seu próprio G1.
