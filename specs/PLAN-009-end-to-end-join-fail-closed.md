# PLAN-009 — End-to-end JOIN Fail-Closed

| Campo | Valor |
|---|---|
| Spec | `SPEC-009` |
| Baseline | `862abae4237997bc7165b27a4fc179429ff11359`, com mudanças locais preexistentes preservadas |
| Gate de entrada | G1 aprovado em 2026-09-17 pelo HUMAN/Product Owner |
| Status | `COMPLETED` |
| Implementação autorizada | Sim — G2 aprovado em 2026-09-17 |

## 1. Objetivo e estratégia mínima

Fechar a falha ponta a ponta observada no teste real sem mudar a política da SPEC-004:

1. converter somente falhas de domínio esperadas de `gerar_sql` em erro MCP deliberado e legível, preservando o motivo de autoridade;
2. fazer `gerar_join` comunicar explicitamente se o uso automático está permitido e não fornecer SQL sugerido quando a relação estiver bloqueada;
3. tornar explícita na skill a proibição de fallback manual ou por tools auxiliares após falha/bloqueio multi-tabela;
4. verificar a fronteira MCP real e repetir exatamente o prompt do teste de aceitação.

A estratégia não altera inferência, homologação, seleção de caminhos, confiança ou o gate interno já aceito. Ela fecha somente a perda da mensagem e o caminho alternativo que permitiu contornar o gate.

## 2. Arquivos e orçamento de mudança

Após G2, alterar somente:

- `src/data_engineering_mcp/server.py`: traduzir falhas esperadas de geração para `ToolError`; comunicar o estado operacional em `gerar_join`; omitir `sql_sugerido` quando o relacionamento não for `APPROVED` e livre de conflitos.
- `data-engineering-spec-driven/SKILL.md`: adicionar a regra fail-closed explícita e ordenada para falha/bloqueio de SQL multi-tabela.
- `tests/test_server.py`: criar testes focados na fronteira pública MCP, incluindo erro legível, bloqueio de `gerar_join`, relação aprovada e preservação de single-table/12 tools.
- `specs/SPEC-009-end-to-end-join-fail-closed.md`: registrar somente gates e evidências factuais.
- `specs/PLAN-009-end-to-end-join-fail-closed.md`: registrar somente G2, execução, verificação e evidências.

Nenhum outro arquivo está autorizado. Necessidade de alterar modelos, `SQLGenerator`, engine de relacionamentos, metadata, README, dependências ou qualquer arquivo adicional causa `STOP_HUMAN` em G3 antes da mudança.

## 3. Comportamento previsto

1. `gerar_sql` single-table mantém o resultado atual.
2. `gerar_sql` multi-table com relação bloqueada retorna falha MCP esperada, legível e sem SQL parcial; a mensagem identifica endpoints, autoridade e necessidade de homologação.
3. Exceções inesperadas continuam tratadas como falhas internas; não serão mascaradas como bloqueios de domínio.
4. `gerar_join` mantém os dados descritivos do candidato, acrescenta estado operacional inequívoco e só inclui SQL sugerido quando `authority=APPROVED` e `conflicts=[]`.
5. `conflicts=[]` significa apenas ausência de conflito registrado; não será comunicado como ausência de bloqueio quando a autoridade impedir uso automático.
6. A skill, ao observar falha ou bloqueio de `gerar_sql` para múltiplas tabelas, proíbe gerar, reconstruir, completar, explicar como executável ou oferecer SQL equivalente usando `gerar_join`, `encontrar_caminho`, catálogo ou raciocínio próprio.
7. Nesse estado, a skill informa `automatic JOIN BLOCKED`, apresenta os relacionamentos candidatos sem SQL e entra em `STOP_HUMAN`, solicitando decisão/homologação HUMAN.

## 4. Sequência autorizável após G2

1. Reexecutar INSPECT e confirmar baseline, diff e ausência de sobreposição nova nos arquivos do orçamento.
2. Implementar a tradução mínima de erro e o estado operacional de `gerar_join` em `server.py`.
3. Implementar a regra fail-closed mínima no `SKILL.md`.
4. Criar os testes da fronteira MCP em `tests/test_server.py`.
5. Executar testes específicos, suíte completa, smoke MCP e `git diff --check`, direcionando temporários somente para caminho local autorizado se necessário.
6. Confirmar exatamente 12 tools e compatibilidade single-table.
7. Repetir exatamente o prompt do teste real de aceitação, com os relacionamentos ainda `INFERRED`.
8. Registrar evidência factual e parar em G4 para aceite HUMAN; qualquer desvio material para antes em G3.

## 5. Verificação e evidência mínimas

- Teste pela fronteira MCP confirma `is_error=True` com mensagem de `authority=INFERRED`, endpoints e homologação, sem “erro interno” genérico e sem SQL parcial.
- Teste de `gerar_join` confirma `automatic JOIN BLOCKED` e ausência de SQL sugerido para `INFERRED`, `KNOWN`, autoridade ausente ou conflito.
- Teste de `gerar_join` confirma permissão e SQL sugerido somente para `APPROVED` sem conflitos.
- Teste confirma que erro inesperado não é convertido indevidamente em bloqueio esperado.
- Testes confirmam single-table inalterado e exatamente 12 tools.
- Verificação documental controlada confirma que a skill proíbe todos os fallbacks equivalentes enumerados na SPEC-009.
- Suíte completa e smoke MCP passam; `git diff --check` não apresenta erro.
- Teste real repete exatamente o prompt anterior e comprova: nenhum SQL multi-table, ambas as relações como `automatic JOIN BLOCKED` e solicitação de decisão/homologação HUMAN.
- Evidência registra ambiente, método, resultado observado, limitações e riscos residuais, sem declarar aceite antes de G4.

## 6. Critérios de aceite

- **AC-P9-001:** todos os critérios AC-001 a AC-008 da SPEC-009 possuem evidência reproduzível.
- **AC-P9-002:** somente falhas esperadas de domínio atravessam a fronteira como `ToolError`; falhas inesperadas permanecem visíveis como internas.
- **AC-P9-003:** nenhuma saída auxiliar utilizável ou instrução da skill permite reconstruir JOIN bloqueado.
- **AC-P9-004:** o prompt real exato termina em `STOP_HUMAN` para homologação, sem qualquer SQL multi-table.
- **AC-P9-005:** consultas single-table e exatamente 12 tools permanecem compatíveis.
- **AC-P9-006:** o diff fica limitado aos cinco arquivos do orçamento; não há mudança de metadata, dependência, configuração global, Power BI, Figma, commit, push, release ou publicação.

## 7. Riscos e mitigação

| Risco/ônus | Mitigação |
|---|---|
| Capturar exceções demais e ocultar bug real | Capturar somente exceções de domínio esperadas e testá-las separadamente de erro inesperado |
| Consumidor interpretar `conflicts=[]` como liberação | Campo operacional explícito derivado conjuntamente de autoridade e conflitos |
| Compatibilidade da resposta de `gerar_join` | Preservar campos descritivos existentes; remover apenas SQL que seria inseguro e adicionar estado explícito |
| Regra textual ainda permitir paráfrase do fallback | Enumerar tools e formas de reconstrução proibidas; validar com o prompt real exato |
| Ambiente bloquear temporários do pytest | Direcionar temporários para `.test-tmp/` local existente, sem instalação ou configuração global |

## 8. Rollback

Reverter somente as alterações desta execução em `server.py`, `SKILL.md`, `tests/test_server.py` e os registros de execução/evidência na SPEC-009 e neste plano. Não alterar nem reverter mudanças locais anteriores. Não há migração, dado, metadata, dependência ou configuração externa a restaurar.

## 9. Decisão solicitada ao HUMAN — G2

Solicita-se uma única decisão: aprovar este plano e autorizar `IMPLEMENT → VERIFY → EVIDENCE` estritamente dentro dos cinco arquivos da seção 2, com parada obrigatória em G3 diante de desvio e em G4 após evidência; pedir ajustes; ou rejeitar.

## 10. Gate atual

**G2 — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** Autorizada a execução de `IMPLEMENT → VERIFY → EVIDENCE` estritamente dentro dos cinco arquivos da seção 2, com parada obrigatória em G3 diante de desvio e em G4 após evidência. Permanecem proibidos granularidade, cardinalidade, otimização, features adicionais, instalação/configuração global, commit, push, release e publicação.

## 11. Implementação e evidências

Implementação concluída dentro do orçamento aprovado:

- `server.py` converte somente `DataEngineeringMCPError` de `gerar_sql` em `ToolError`; exceções inesperadas continuam opacas ao cliente como falha interna;
- `gerar_join` preserva os campos descritivos, expõe `automatic_join` e `automatic_join_allowed`, informa `blocked_reason` e omite `sql_sugerido` quando autoridade/conflitos bloqueiam uso automático;
- `SKILL.md` proíbe explicitamente gerar ou reconstruir SQL multi-tabela equivalente após falha/bloqueio, inclusive por `gerar_join`, `encontrar_caminho`, catálogo, outra tool ou raciocínio próprio;
- `tests/test_server.py` cobre a fronteira MCP, erro inesperado, relação inferida bloqueada, relação aprovada permitida, single-table e contagem de tools.

Resultados reproduzidos em 2026-09-17:

| Verificação | Resultado |
|---|---|
| Testes específicos `tests/test_server.py` | PASS — `5 passed` |
| Suíte completa | PASS — `53 passed` |
| Smoke MCP real | PASS — servidor v0.1.0, exatamente 12 tools, catálogo/status sem erro |
| Compatibilidade single-table | PASS — `SELECT` produzido sem `LEFT JOIN` |
| Falha esperada na fronteira MCP | PASS — `is_error=True`, endpoints, `autoridade INFERRED`, homologação `APPROVED`, sem erro interno genérico e sem SQL |
| Falha inesperada | PASS — detalhe interno não é exposto como erro deliberado |
| Skill fail-closed | PASS — regra enumera e proíbe todos os fallbacks previstos |
| `git diff --check` | PASS — somente avisos informativos preexistentes de LF/CRLF |
| Itens protegidos | PASS — sem metadata, dependência, configuração global, Power BI, Figma, commit, push, release ou publicação |

A primeira execução do pytest dentro do sandbox repetiu o `PermissionError` já documentado ao criar temporários. A alternativa expressamente prevista foi usada: `--basetemp` em `.test-tmp/` local com permissão de execução para o processo. Não houve instalação nem mudança de configuração global.

### 11.1 Teste real idêntico ao caso que falhou

O pedido original de ampliar CPF, nome e nome da mãe com dados de outras tabelas foi repetido contra o servidor MCP real, com as mesmas tabelas e colunas resultantes. Observado:

- `PESSOA.CD_PESSOA ↔ USUARIO.CD_PESSOA`: `authority=INFERRED`, `automatic_join=BLOCKED`, `automatic_join_allowed=false`, sem `sql_sugerido`;
- `USUARIO.CD_PLANO ↔ PLANO.CD_PLANO`: `authority=INFERRED`, `automatic_join=BLOCKED`, `automatic_join_allowed=false`, sem `sql_sugerido`;
- `gerar_sql`: `is_error=True`, mensagem deliberada identifica a primeira relação bloqueada e exige homologação HUMAN como `APPROVED`, sem SQL parcial;
- aplicação da regra da skill: apresentar somente os candidatos bloqueados e solicitar homologação HUMAN; nenhum SQL multi-tabela ou fragmento equivalente é permitido.

Resultado decisivo: **PASS** para `descobrir relacionamento → comunicar automatic JOIN = BLOCKED → não fornecer SQL/sql_sugerido equivalente → solicitar homologação HUMAN`.

## 12. Riscos residuais

- A regra da skill continua sendo interpretada por agente em linguagem natural; o texto agora é explícito, ordenado e validado pelo caso real.
- `gerar_join` mantém compatibilidade descritiva aditiva, mas consumidores que usavam indevidamente `sql_sugerido` de relação bloqueada deixarão de recebê-lo; esse é o fail-closed aprovado.
- Nenhuma relação foi homologada por esta execução; consultas multi-tabela continuam intencionalmente bloqueadas enquanto a autoridade permanecer inadequada.

## 13. Gate de saída

**G4 — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** A implementação, as evidências, o teste real fail-closed e os riscos residuais foram aceitos. O PLAN-009 está `COMPLETED` e a SPEC-009 foi encerrada como `ACCEPTED/DONE`.

Não houve autorização para commit, push, release, publicação, instalação/configuração global, homologação de relacionamentos ou continuidade para outra feature.
