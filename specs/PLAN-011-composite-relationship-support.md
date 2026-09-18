# PLAN-011 — Composite Relationship Support

| Campo | Valor |
|---|---|
| Spec | `SPEC-011` |
| Baseline | `862abae4237997bc7165b27a4fc179429ff11359`, branch `main`, com mudanças locais preexistentes preservadas |
| Gate de entrada | G1 aprovado em 2026-09-18 pelo HUMAN/Product Owner |
| Status | `COMPLETED` |
| G2 | `APPROVED` |
| Implementação | `AUTHORIZED AND COMPLETED` |
| VERIFY | `COMPLETED` |
| EVIDENCE | `COMPLETED` |
| G4 | `APPROVED` |

## 1. Objetivo e estratégia mínima

Fechar somente a assimetria entre chaves compostas já suportadas e relacionamentos ainda escalares, mantendo o contrato simples existente e o comportamento fail-closed.

A estratégia proposta é:

1. aceitar no metadado persistente exatamente uma forma por relacionamento: legado `source_column`/`target_column` ou nova `source_columns`/`target_columns`;
2. normalizar ambas, na fronteira de validação, para listas internas não vazias, ordenadas e de mesmo tamanho;
3. manter a heurística atual exclusivamente single-column, produzindo listas unitárias;
4. usar todos os pares posicionais na identidade, merge, conflitos, caminhos, atualização, serialização, JOIN e prova de grão;
5. preservar os campos escalares públicos para relacionamentos simples e adicionar listas canônicas sem remover ou mudar tipos existentes;
6. bloquear qualquer caso incompleto, ambíguo, conflitante ou sem autoridades suficientes;
7. interromper em G5 antes de qualquer mudança pública incompatível que se revele necessária.

Não haverá migração ou regravação automática de `metadata/relationships.json`.

## 2. Invariantes obrigatórias

```text
relacionamento simples legado -> continua funcionando
relacionamento simples novo -> equivalente ao legado
relacionamento composto -> pares de colunas ordenados e posicionais
endpoint composto = chave UNIQUE/PK correspondente -> pode sustentar preservação do grão, respeitadas as demais autoridades
evidência incompleta/conflitante -> BLOCKED
```

Também permanecem obrigatórios: exatamente 12 tools; nenhuma migração manual; heurística somente single-column; nenhuma lógica específica para HAP; nenhuma interface de cadastro; nenhum Oracle, profiler, planner/optimizer, deduplicação ou BI.

## 3. Arquivos e orçamento de mudança

Após G2, alterar somente:

- `src/data_engineering_mcp/models.py`: entrada legada/nova, validação estrutural, normalização canônica e serialização aditiva compatível.
- `src/data_engineering_mcp/relationships.py`: identidade vetorial, merge, conflitos, orientação, seleção e prova de grão com endpoint completo.
- `src/data_engineering_mcp/sql_generator.py`: emissão determinística de todos os pares posicionais no `ON` e mensagens sem truncamento.
- `src/data_engineering_mcp/server.py`: identidade completa em `atualizar_catalogo` e JOIN sugerido composto, preservando as 12 tools.
- `tests/test_relationships.py`: persistência, normalização, validação, identidade, conflitos, caminhos, heurística e grain gate.
- `tests/test_sql_generator.py`: JOIN simples regressivo, JOIN composto e bloqueios sem SQL parcial.
- `tests/test_server.py`: schema/payload MCP, `gerar_join`, atualização e contagem exata das tools.
- `README.md`: documentar somente o formato persistente aditivo e a retrocompatibilidade efetivamente implementados.
- `specs/SPEC-011-composite-relationship-support.md`: registrar gates e evidências factuais.
- `specs/PLAN-011-composite-relationship-support.md`: registrar G2, execução, verificação e evidências.

Nenhum outro arquivo está autorizado. Necessidade de alterar dependência, configuração, metadata real, skill, catálogo, query intent, SQL explainer ou qualquer arquivo adicional causa `STOP_HUMAN — G3` antes da mudança. Remoção, renomeação ou mudança de tipo de campo público existente causa `STOP_HUMAN — G5`.

## 4. Sequência autorizável após G2

1. Reexecutar INSPECT; registrar baseline, status, diff e sobreposição com mudanças locais preexistentes.
2. Capturar antes da alteração os schemas e payloads públicos relevantes e os 12 nomes de tools.
3. Implementar a normalização de entrada para uma única representação vetorial interna, sem escrita de metadata.
4. Adaptar identidade, merge, conflitos, cardinalidade orientada, caminhos e preservação de grão para endpoints completos.
5. Adaptar `gerar_join`, `gerar_sql` e `atualizar_catalogo` sem alterar nomes ou quantidade de tools.
6. Criar testes exclusivamente com fixtures sintéticas genéricas `TABELA_A` e `TABELA_B` para a nova capacidade; manter regressões legadas existentes.
7. Atualizar a documentação estritamente conforme o comportamento implementado.
8. Executar VERIFY e registrar EVIDENCE; parar em G4. Qualquer desvio para antes em G3 e qualquer quebra pública para antes em G5.

## 5. Regras técnicas a travar na implementação

- Entrada deve usar o par escalar completo ou o par de listas completo, nunca mistura.
- Listas devem ser não vazias, ter comprimentos iguais e não conter identificadores vazios ou duplicados no mesmo endpoint.
- Normalização deve preservar a ordem declarada; não ordenar alfabeticamente colunas.
- A identidade canônica deve comparar tabelas e listas completas; inverter a orientação troca endpoints sem reordenar cada lista.
- Forma legada e listas unitárias equivalentes devem produzir uma única identidade lógica.
- Inferências simples coincidentes com partes de um composto explícito não constituem, isoladamente, conflito contra o composto.
- Ambiguidade real entre identidades aplicáveis deve permanecer visível e bloqueante; score não pode truncar ou promover compostos.
- O predicado `ON` deve conter um `=` por par posicional, unidos por `AND` na ordem declarada.
- `grain_preservation` deve comparar exatamente a lista alcançada com `ExplicitKey.columns`; subconjunto, superconjunto e ordem diferente bloqueiam.
- Autoridade de relacionamento, cardinalidade e chave continuam independentes conforme SPEC-010.

## 6. Matriz mínima de verificação

| Área | Evidência exigida |
|---|---|
| Legado | Documento atual e relacionamento escalar carregam sem edição, migração ou mudança comportamental |
| Novo simples | Listas unitárias são equivalentes ao legado, sem duplicação lógica |
| Estrutura | Forma mista, lado ausente, lista vazia, tamanhos diferentes, duplicatas, vazio e coluna inexistente falham antes do uso |
| Composto preservador | `TABELA_A -> TABELA_B`, composto `APPROVED`, `N:1`/`1:1` autorizado e PK/UNIQUE composta exata resultam em `PRESERVES` |
| Fail-closed | Chave ausente, parcial, superconjunto ou reordenada; cardinalidade/autoridade insuficiente; conflito ou ambiguidade resultam em `BLOCKED`, sem SQL |
| SQL | Todos os pares aparecem uma vez, em ordem, unidos por `AND`; simples mantém um predicado |
| Inferência | Continua somente single-column e não inventa nem invalida composto por mera parcialidade |
| Caminhos/refresh | Arestas e contagem de novos relacionamentos usam identidade completa sem truncamento |
| MCP | Schemas/payloads antes/depois comparados; escalares simples preservados; listas apenas aditivas; exatamente 12 tools |
| Genericidade | Código e testes novos sem nomes RAW_HAP ou dependência das 11 tabelas atuais |
| Integridade | SHA-256 de `metadata/relationships.json` idêntico antes/depois de implementação e testes |
| Regressão | Testes específicos, suíte completa, smoke MCP, compilação e `git diff --check` passam |

## 7. Critérios de aceite do plano

- **AC-P11-001:** todos os AC-001 a AC-012 da SPEC-011 possuem evidência reproduzível.
- **AC-P11-002:** formatos legado e novo simples convergem para a mesma identidade e comportamento público.
- **AC-P11-003:** relacionamentos compostos preservam integralmente ordem, pares, autoridades e cardinalidade em todas as camadas.
- **AC-P11-004:** o gate só reconhece preservação com chave composta exata e demais autoridades suficientes; todo caso incompleto/conflitante permanece bloqueado sem SQL parcial.
- **AC-P11-005:** heurística permanece single-column e nenhuma lógica de produto contém hardcode de HAP ou das tabelas atuais.
- **AC-P11-006:** `metadata/relationships.json` real permanece byte a byte inalterado e nenhum fato é homologado.
- **AC-P11-007:** contrato MCP simples permanece compatível por extensão aditiva e exatamente 12 tools; necessidade de incompatibilidade para em G5.
- **AC-P11-008:** o diff fica limitado ao orçamento da seção 3, preservando mudanças locais preexistentes.

## 8. Riscos e mitigação

| Risco | Mitigação obrigatória |
|---|---|
| Normalização alterar o legado | Normalização única na entrada e testes equivalentes legado/lista unitária em modelo, engine, SQL e MCP |
| Ordem posicional perdida | Tuplas/listas ordenadas em identidade e testes com ordem invertida |
| Falso conflito com heurística parcial | Política explícita e teste de coexistência entre composto autoritativo e inferências simples |
| Seleção ambígua escolher por score | Fail-closed para múltiplas identidades aplicáveis; teste sem truncamento |
| Payload público incompatível | Snapshot estrutural antes/depois; escalares preservados para simples; G5 antes de quebra |
| Metadata real alterado | Hash antes/depois e fixtures somente temporárias |
| Mudanças locais sobrepostas | INSPECT antes de G2, edições mínimas e nenhuma limpeza/reset/reversão |

## 9. Verificação documental pré-G2

Este plano é rastreável às seções 2 a 10 da SPEC-011, cobre seus 12 critérios, mantém os não-escopos e define paradas G3/G5. A estratégia utiliza a persistência e as 12 tools existentes, sem interface nova, migração ou dependência.

Esta validação é somente documental; não constitui prova de implementação nem aprovação G2.

## 10. Rollback futuro

Se a execução for aprovada e precisar ser revertida, reverter apenas as alterações atribuíveis à SPEC-011 nos arquivos da seção 3, preservando todas as mudanças preexistentes. Como não haverá migração nem escrita automática em metadata, não existe conversão de dados a desfazer. Qualquer constatação contrária interrompe a execução antes da mudança correspondente.

## 11. Decisão solicitada ao HUMAN — G2

Solicita-se uma única decisão: aprovar este plano e autorizar `IMPLEMENT -> VERIFY -> EVIDENCE` estritamente dentro dos arquivos e estratégia definidos; pedir ajustes; ou rejeitar.

Uma aprovação G2 não autoriza quebra do contrato MCP. Se ela se revelar necessária, a execução deve parar separadamente em `G5 — HUMAN` antes da incompatibilidade.

## 12. Gate atual

**G2 — APPROVED em 2026-09-18 pelo HUMAN/Product Owner.** Autorizada a execução dentro do orçamento da seção 3.

## 13. Resultado da execução e evidência

A recuperação retomou a implementação parcial sem limpar ou reatribuir mudanças locais. Foram concluídos os caminhos vetoriais de modelos, identidade/merge, cardinalidade orientada, preservação de grão, SQL, JOIN sugerido e contagem de novos relacionamentos, com extensão aditiva dos campos de listas e preservação dos escalares simples.

Verificações executadas:

- `.venv\Scripts\python.exe -m pytest -q`: `82 passed`;
- `scripts\smoke_test.py`: `12 tools`, sem erro de inicialização ou chamada básica;
- testes novos cobrem legado, lista unitária, composto preservador, chave parcial/reordenada, entradas inválidas, não promoção heurística e predicados `ON` completos;
- metadata real não foi alterado; nenhuma dependência, configuração, publicação ou arquivo fora do orçamento foi introduzido.

**G4 — APPROVED em 2026-09-18 pelo HUMAN/Product Owner.** Todos os itens técnicos verificáveis e riscos residuais foram aceitos. `PLAN-011 → COMPLETED`. Este aceite não autoriza commit, push, release, publicação ou expansão de escopo.
