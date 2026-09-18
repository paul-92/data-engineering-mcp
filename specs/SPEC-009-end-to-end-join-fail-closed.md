# SPEC-009 — End-to-end JOIN Fail-Closed

| Campo | Valor |
|---|---|
| ID | SPEC-009 |
| Título | End-to-end JOIN Fail-Closed |
| Tipo | Correção funcional mínima proposta após teste real de aceitação |
| Status | ACCEPTED |
| Resultado | DONE |
| Dependências | SPEC-002, SPEC-004, SPEC-005, SPEC-006 e SPEC-007 aceitas |
| Product Owner | HUMAN |
| Implementação autorizada | Concluída e aceita no G4 |
| Última atualização | 2026-09-17 |

## 1. Achado do teste real de aceitação

O mesmo pedido que partiu de `RAW_HAP_TB_PESSOA` e solicitou informações de outras tabelas encontrou os relacionamentos:

- `RAW_HAP_TB_PESSOA.CD_PESSOA = RAW_HAP_TB_USUARIO.CD_PESSOA`, `authority=INFERRED`, `confidence=MEDIUM`, `score=50`;
- `RAW_HAP_TB_USUARIO.CD_PLANO = RAW_HAP_TB_PLANO.CD_PLANO`, `authority=INFERRED`, `confidence=MEDIUM`, `score=60`.

O agente informou “Bloqueio: nenhum” para ambos e, depois de `gerar_sql` apresentar erro interno, produziu manualmente um `SELECT` com os dois `LEFT JOIN`. O fallback foi atribuído aos resultados de `encontrar_caminho` e `gerar_join`.

**Resultado: FAIL material.** O comportamento viola a política aceita na SPEC-004: `INFERRED` não pode sustentar `JOIN` automático, e uma falha do gerador não pode autorizar reconstrução manual equivalente.

## 2. INSPECT e diagnóstico reproduzível

Baseline Git observado: `862abae4237997bc7165b27a4fc179429ff11359`, branch `main`, com todas as mudanças locais preexistentes preservadas. A implementação aceita ainda está integralmente no worktree local; nenhum arquivo preexistente foi limpo, revertido ou reatribuído.

### 2.1 Por que `gerar_sql` apareceu como erro interno

A reprodução direta da chamada multi-tabela percorreu `SQLGenerator._joins`, selecionou a relação `PESSOA ↔ USUARIO` e executou `_require_approved_relationship`. O gate funcionou e lançou:

`RelationshipNotFoundError: Relacionamento bloqueado ... autoridade INFERRED. A relação precisa de homologação como APPROVED e estar livre de conflitos.`

Porém `server.py` deixa a exceção de domínio escapar da tool. No SDK MCP instalado, somente `ToolError` representa falha esperada e entrega sua mensagem ao cliente com `is_error=True`; qualquer outra exceção é tratada como crash e reduzida a uma mensagem genérica de erro de execução. Portanto, o “erro interno” não foi falha da decisão do gate: foi perda de semântica na fronteira pública da tool.

### 2.2 Onde o fallback manual ficou possível

Há duas aberturas combinadas:

1. `gerar_join` retorna sempre `sql_sugerido`, inclusive quando o relacionamento retornado tem `authority=INFERRED`; não retorna um estado operacional explícito de `automatic JOIN BLOCKED`.
2. `data-engineering-spec-driven/SKILL.md` exige preservar resultados sem promover relações ou contornar safety, mas não contém uma regra específica e ordenada dizendo que, após falha ou bloqueio de `gerar_sql`, é proibido reconstruir, escrever, explicar como executável ou oferecer SQL multi-tabela equivalente a partir de `encontrar_caminho`, `gerar_join`, catálogo ou raciocínio próprio.

O agente, portanto, recebeu a mensagem opaca do gerador e uma sugestão SQL concreta da tool auxiliar, e tratou a montagem manual como fallback permitido.

### 2.3 Como `INFERRED` é comunicado hoje

- `encontrar_caminho` expõe `authority=INFERRED`, `source`, `decision=null` e `conflicts=[]`, mas não expõe o efeito operacional de que o `JOIN` automático está bloqueado.
- `gerar_join` expõe os mesmos campos e ainda inclui `sql_sugerido`, sem `automatic_join_allowed=false` nem motivo de bloqueio.
- `gerar_sql` possui a mensagem correta dentro da exceção, mas ela é ocultada pela fronteira MCP por não ser convertida em `ToolError`.

Assim, `conflicts=[]` pode ser verbalizado indevidamente como “Bloqueio: nenhum”, embora a autoridade `INFERRED` seja, por si só, bloqueio operacional para geração automática.

## 3. Objetivo mínimo proposto

Fechar a cadeia ponta a ponta sem ampliar a política existente:

1. falhas esperadas de `gerar_sql`, especialmente bloqueio por autoridade, devem chegar ao agente como erro legível e deliberado;
2. qualquer relação `INFERRED`, `KNOWN`, sem autoridade ou conflitante deve ser comunicada como `automatic JOIN BLOCKED`, independentemente de `conflicts` estar vazio;
3. tools auxiliares não devem fornecer um `sql_sugerido` utilizável quando a relação não puder sustentar JOIN automático;
4. após falha ou bloqueio de `gerar_sql`, a skill deve proibir explicitamente qualquer fallback manual ou alternativo que produza SQL multi-tabela equivalente e deve parar em `STOP_HUMAN`, solicitando decisão/homologação HUMAN;
5. consultas single-table e exatamente as 12 tools atuais devem permanecer compatíveis.

## 4. Menor correção proposta

A solução proposta fica limitada a três pontos coordenados:

- **Fronteira MCP:** converter falhas de domínio esperadas da geração em `ToolError`, preservando a mensagem do gate para o agente, sem converter bugs inesperados em erros esperados.
- **Comunicação da relação:** fazer `gerar_join` comunicar explicitamente permissão/bloqueio automático e omitir qualquer SQL sugerido quando a relação não for `APPROVED` e livre de conflitos. A quantidade e os nomes das tools permanecem inalterados.
- **Orquestração da skill:** adicionar regra fail-closed explícita: se `gerar_sql` falhar ou bloquear em uma intenção multi-tabela, não construir SQL equivalente por nenhuma outra tool ou por raciocínio manual; relatar `automatic JOIN BLOCKED` e entrar em `STOP_HUMAN` para homologação.

O plano futuro deverá escolher somente os arquivos mínimos necessários para esses três pontos e seus testes. Nenhuma implementação ou PLAN-009 está autorizada neste gate.

## 5. Não-escopo

- Granularidade, cardinalidade, fan-out, unicidade, otimização, custo, `EXPLAIN PLAN` ou execução em banco.
- Promoção ou homologação automática de relacionamentos.
- Mudança do algoritmo de inferência, score, confiança ou seleção de caminhos além da comunicação fail-closed.
- Nova tool, alteração da quantidade de 12 tools, nova dependência, parser, planner, framework ou serviço.
- Mudança incompatível em consultas single-table.
- Power BI, Figma, configuração global, instalação global, commit, push, release ou publicação.

## 6. Critérios de aceite propostos

- **AC-001:** repetir exatamente o prompt do teste real não produz nenhum SQL multi-tabela enquanto os dois relacionamentos permanecerem `INFERRED`.
- **AC-002:** a resposta identifica cada relação `INFERRED` como `automatic JOIN BLOCKED`, mesmo com `conflicts=[]`, e solicita decisão/homologação HUMAN.
- **AC-003:** `gerar_sql` entrega ao agente a mensagem deliberada de bloqueio por autoridade, sem aparecer como erro interno genérico e sem SQL parcial.
- **AC-004:** após qualquer falha ou bloqueio de `gerar_sql` multi-tabela, nenhum fallback por `gerar_join`, `encontrar_caminho`, catálogo ou montagem manual produz SQL equivalente.
- **AC-005:** `gerar_join` não devolve SQL sugerido utilizável para relação que não seja `APPROVED` e livre de conflitos.
- **AC-006:** relações `APPROVED` sem conflitos continuam podendo sustentar o fluxo atual, sem relaxar controles adicionais existentes.
- **AC-007:** consultas single-table permanecem compatíveis; exatamente as 12 tools, seus nomes e sua finalidade são preservados.
- **AC-008:** testes proporcionais cobrem a fronteira MCP real e o comportamento da skill, não apenas chamadas diretas ao `SQLGenerator`.

## 7. Evidência inicial e limitações

- A chamada direta com as três tabelas reproduziu o bloqueio correto em `_require_approved_relationship` na primeira relação `INFERRED`.
- `encontrar_caminho` reproduziu as duas relações e autoridades observadas no teste real.
- `gerar_join` reproduziu `sql_sugerido` para ambas apesar de `authority=INFERRED`.
- Os testes unitários do gerador não puderam ser reexecutados neste INSPECT porque o ambiente negou criação do diretório temporário do pytest (`PermissionError` em `%TEMP%`). Isso não altera o diagnóstico reproduzido diretamente e deverá ser resolvido ou apontado para diretório autorizado no plano/verificação futura.
- `git diff --check` passou, com somente avisos informativos preexistentes de LF/CRLF.

## 8. Registro de aprovação

| Gate | Decisor | Data | Decisão | Condições/observações |
|---|---|---|---|---|
| G1 — SPEC-009 | HUMAN/Product Owner | 2026-09-17 | APPROVED | Criar somente um PLAN-009 curto e proporcional e parar obrigatoriamente em G2 antes de qualquer correção |
| G2 — PLAN-009 | HUMAN/Product Owner | 2026-09-17 | APPROVED | Executar `IMPLEMENT → VERIFY → EVIDENCE` somente nos cinco arquivos do orçamento, preservando 12 tools, single-table e o não-escopo |
| G4 — Aceite final | HUMAN/Product Owner | 2026-09-17 | APPROVED | Implementação, evidências, teste real fail-closed e riscos residuais aceitos; SPEC-009 encerrada como `ACCEPTED/DONE` |

## 9. Gate atual

**G1 — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** O objetivo mínimo, o não-escopo e os critérios da SPEC-009 foram aprovados. Foi autorizada somente a criação do PLAN-009; nenhuma implementação foi autorizada.

**G2 — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** O PLAN-009 está autorizado dentro de seu orçamento até G4, G3 ou bloqueio objetivo. Nenhuma homologação de relacionamento foi assumida.

## 10. Resultado da execução autorizada

A correção mínima foi implementada e verificada sem desvio de escopo. Evidência detalhada está no PLAN-009.

- fronteira MCP: bloqueio `INFERRED` chega como falha deliberada e legível, sem SQL parcial;
- tool auxiliar: `automatic_join=BLOCKED` e ausência de `sql_sugerido` para os dois relacionamentos inferidos do teste real;
- skill: fallback manual ou alternativo equivalente está explicitamente proibido e exige `STOP_HUMAN` para homologação;
- regressão: `5/5` testes específicos, `53/53` testes totais e smoke com exatamente 12 tools passaram;
- teste real repetido: nenhum SQL multi-tabela foi produzido; a saída correta é comunicar os bloqueios e solicitar decisão/homologação HUMAN;
- consultas single-table permaneceram compatíveis;
- nenhum item do não-escopo foi alterado ou executado.

Resultado técnico: **PASS para AC-001 a AC-008**, aceito pelo HUMAN/Product Owner no G4.

## 11. Gate de saída

**G4 — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** A implementação, as evidências, o teste real fail-closed e os riscos residuais foram aceitos. Status final: `ACCEPTED`. Resultado: `DONE`.

O fluxo da SPEC-009 está encerrado. Este aceite não autoriza commit, push, release, publicação, homologação de relacionamentos ou trabalho fora do escopo concluído.
