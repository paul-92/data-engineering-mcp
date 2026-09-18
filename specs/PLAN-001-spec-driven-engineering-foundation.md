# PLAN-001 — Fundação Spec-Driven mínima

| Campo | Valor |
|---|---|
| Spec | `SPEC-001` |
| Baseline | `862abae4237997bc7165b27a4fc179429ff11359` |
| Gate de entrada | G1 aprovado pelo HUMAN/Product Owner |
| Status | `COMPLETED` |
| Implementação autorizada | Sim — G2 aprovado em 2026-09-11 |

## Princípio de simplicidade/proporcionalidade

Adotar a menor solução que satisfaça a necessidade e a menor documentação que mantenha segurança e rastreabilidade. O processo e suas evidências devem crescer somente quando risco, impacto ou irreversibilidade justificarem. Não criar framework, automação ou artefato sem necessidade concreta.

## 1. Objetivo

Tornar a SPEC-001 a referência operacional mínima para mudanças futuras: registrar decisões de gate, manter rastreabilidade essencial e permitir verificação documental, sem alterar o comportamento do MCP.

## 2. Arquivos mínimos

- Alterar `specs/SPEC-001-spec-driven-engineering-foundation.md` somente para registrar G1, alinhar seu status e referenciar este PLAN.
- Manter este arquivo `specs/PLAN-001-spec-driven-engineering-foundation.md` como plano e registro do G2.

Não criar nesta implementação: templates, scripts, automações, índice, diretórios de evidência ou novas specs. Nenhum arquivo de código, teste, configuração, dataset ou integração será alterado.

## 3. Status, gates e rastreabilidade mínimos

- Usar apenas os estados e gates já definidos na SPEC-001; não criar fluxo paralelo.
- G1 aprova o escopo; G2 autoriza a implementação documental; G4 aceita o resultado. Silêncio não conta como aprovação.
- Registrar em cada gate: decisor, data, decisão e condição relevante.
- Rastreabilidade desta implementação: `SPEC-001 → PLAN-001 → diff documental → validações → G4`.
- Qualquer mudança fora dos dois arquivos previstos é desvio material e deve parar para nova decisão.

## 4. Validações mínimas

Após G2:

1. Confirmar que apenas os dois arquivos documentais previstos aparecem no diff da SPEC-001.
2. Confirmar que a SPEC registra G1 e referencia o PLAN.
3. Confirmar que o PLAN registra a decisão de G2.
4. Confirmar que código, testes, configuração, 12 tools, 11 XLSX, Power BI MCP, Codex global, Git remoto e releases permanecem inalterados.
5. Fazer leitura final de consistência entre status, gates e princípio de simplicidade/proporcionalidade.

Não executar testes de runtime, pois não haverá mudança executável.

## 5. Critérios de aceite

- **AC-P1:** G1 e G2 estão registrados com decisor, data e decisão.
- **AC-P2:** o princípio de simplicidade/proporcionalidade está explícito e operacional.
- **AC-P3:** a SPEC referencia este PLAN e não apresenta status contraditório.
- **AC-P4:** o diff contém somente a documentação prevista e nenhuma feature extra.
- **AC-P5:** as cinco validações mínimas têm resultado registrado para o G4.

## 6. Rollback

Reverter somente a alteração da SPEC-001 e remover este PLAN, preservando quaisquer mudanças alheias. Confirmar depois que o repositório voltou ao estado documental anterior e que nenhum arquivo fora de `specs/` foi afetado.

## 7. Avaliação para G2

**Impactos positivos:** cria um caminho operacional curto, registra autorizações e mantém o baseline protegido sem introduzir infraestrutura prematura.

**Riscos/ônus:** pequena manutenção documental; possibilidade de divergência entre SPEC e PLAN; dependência de registro humano nos gates. Mitigação: dois arquivos, diff restrito e validação de consistência.

**Decisões HUMAN/Product Owner:**

1. Autorizar no G2 a alteração exclusivamente documental dos dois arquivos listados.
2. Confirmar que não serão criados templates, automações, índice ou estrutura de evidências agora.
3. Confirmar que testes de runtime não são necessários para esta mudança documental.
4. Aceitar que qualquer ampliação de escopo interrompe a execução e retorna para decisão.

## Registro de execução e validação

| Item | Resultado |
|---|---|
| Diff limitado à SPEC-001 e ao PLAN-001 | PASS |
| G1 registrado e PLAN-001 referenciado na SPEC | PASS |
| G2 registrado no PLAN e na SPEC | PASS |
| Código, testes, configuração, tools, datasets e integrações sem alteração | PASS |
| Status, gates e simplicidade/proporcionalidade consistentes | PASS |

Testes de runtime não foram executados porque a mudança é exclusivamente documental.

## Gate final

**G4 — APPROVED em 2026-09-11 pelo HUMAN/Product Owner.** Evidências 5/5 PASS e risco residual aceito. O PLAN-001 está concluído; a SPEC-001 foi encerrada como `DONE/ACCEPTED`.
