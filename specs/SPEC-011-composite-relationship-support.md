# SPEC-011 — Composite Relationship Support

| Campo | Valor |
|---|---|
| ID | SPEC-011 |
| Título | Composite Relationship Support |
| Tipo | Evolução funcional mínima proposta após INSPECT |
| Status | ACCEPTED / DONE |
| Resultado | G1 APPROVED / G2 APPROVED / G4 APPROVED |
| Dependências | SPEC-002, SPEC-003, SPEC-004, SPEC-006, SPEC-009 e SPEC-010 aceitas |
| Product Owner | HUMAN |
| Implementação autorizada | Concluída e aceita no G4 |
| Última atualização | 2026-09-18 |

## 1. Lacuna estrutural comprovada

A SPEC-010 aceita e implementa chaves `PRIMARY_KEY`/`UNIQUE` simples ou compostas em `ExplicitKey.columns`, mas os relacionamentos continuam limitados a um único par de colunas por `source_column`/`target_column`.

O INSPECT do baseline Git `862abae4237997bc7165b27a4fc179429ff11359`, branch `main`, com mudanças locais preexistentes preservadas, confirmou que essa assimetria atravessa o fluxo inteiro:

1. `ExplicitRelationship` e `RelationshipCandidate` armazenam endpoints escalares;
2. identidade, merge, detecção de conflitos e orientação de cardinalidade usam um único par de colunas;
3. a heurística infere apenas igualdade de uma coluna e não representa uma hipótese composta;
4. `find_paths` transporta candidatos escalares, embora o grafo seja por tabelas;
5. `gerar_join` e `SQLGenerator` emitem somente um predicado de igualdade no `ON`;
6. `atualizar_catalogo` compara identidades escalares ao contar novos relacionamentos;
7. `grain_preservation` reduz o lado alcançado a uma lista de uma coluna antes de compará-lo, em ordem exata, com `ExplicitKey.columns`;
8. as tools serializam `RelationshipCandidate`, portanto a forma dos endpoints faz parte do contrato público MCP observável.

Consequentemente, um relacionamento como `TABELA_A.(ID_B, VERSAO_B) → TABELA_B.(ID_B, VERSAO_B)` não pode ser persistido, encontrado, convertido em `JOIN` nem comparado com `UNIQUE(ID_B, VERSAO_B)`. A chave composta existe, mas não pode provar preservação de grão em um JOIN composto.

Essa é uma lacuna concreta para o objetivo já aceito de geração segura e data-driven. Corrigi-la dentro da SPEC-010 encerrada seria desvio material. Uma única SPEC nova é a menor evolução coerente.

## 2. Objetivo mínimo

Permitir relacionamentos explícitos de uma ou mais colunas, com correspondência posicional ordenada entre os endpoints, preservando sem migração manual os metadados e o comportamento público de todos os relacionamentos simples existentes.

A solução deverá:

- aceitar o formato persistente legado `source_column`/`target_column` para relacionamentos simples;
- aceitar um formato aditivo `source_columns`/`target_columns` para relacionamentos simples ou compostos;
- normalizar ambos, imediatamente após a validação de entrada, para uma única representação interna ordenada baseada em listas não vazias;
- exigir o mesmo número de colunas nos dois endpoints e interpretar cada posição como um par de igualdade;
- rejeitar forma mista, ambígua, vazia, duplicada ou com coluna inexistente, sem completar colunas por nome, posição ou heurística;
- usar a identidade composta completa e ordenada em merge, conflitos, ordenação determinística, atualização do catálogo e exposição;
- gerar um predicado `ON` por par posicional, unido por `AND`, sem alterar a semântica dos JOINs simples;
- comparar exatamente o endpoint composto alcançado, na mesma ordem declarada, com `ExplicitKey.columns`;
- preservar exatamente as 12 tools existentes e continuar genérica para tabelas futuras, sem hardcode das tabelas RAW_HAP atuais.

## 3. Contrato mínimo e retrocompatibilidade

### 3.1 Entrada persistente

Cada relacionamento deverá usar exatamente uma das formas:

- legado simples: `source_column: string` e `target_column: string`; ou
- canônica nova: `source_columns: list[string]` e `target_columns: list[string]`.

Na forma nova, listas de tamanho 1 representam relacionamento simples e listas de tamanho maior representam relacionamento composto. Os pares de listas são obrigatórios; usar somente um lado, combinar campos escalares e listas, ou declarar comprimentos diferentes é inválido e deve falhar de forma clara e segura.

O carregamento do formato legado deverá convertê-lo em listas unitárias antes de qualquer identidade, merge, conflito, caminho, geração ou prova de grão. O arquivo existente `metadata/relationships.json`, inclusive `{"relationships": []}` e entradas simples já válidas, deverá continuar carregando sem edição, regravação ou migração manual.

### 3.2 Representação e saída pública

Internamente haverá uma única fonte de verdade: `source_columns[]` e `target_columns[]`, ordenadas. Nenhuma decisão de merge, conflito, SQL ou grão poderá manter lógica paralela escalar.

Para reduzir risco ao contrato MCP, relacionamentos simples deverão continuar expondo `source_column` e `target_column` com os mesmos valores e comportamento atuais. Os campos de lista deverão ser aditivos e refletir a representação canônica. Relacionamentos compostos deverão expor as listas completas e não poderão apresentar um único par escalar como se representasse todo o relacionamento.

O futuro PLAN deverá verificar o schema e o payload reais das tools antes de escolher o detalhe mínimo de serialização para compostos. Remover ou mudar o tipo dos campos escalares existentes, mudar nomes de tools ou exigir migração dos consumidores é mudança pública incompatível e exige G5 específico; não é autorizada por esta SPEC.

## 4. Regras de identidade, inferência, merge e conflitos

- A identidade de um relacionamento é formada pelas duas tabelas e pelas duas listas completas, preservando a correspondência posicional; a orientação inversa deve inverter os endpoints sem reordenar colunas dentro de cada endpoint.
- Duas declarações só descrevem a mesma identidade quando todos os pares posicionais coincidem após normalização de identificadores e orientação canônica.
- Declarações da mesma identidade com autoridade, fonte, decisão ou cardinalidade incompatível continuam conflitantes e bloqueadas segundo as regras vigentes.
- Declarações explicitamente distintas entre o mesmo par de tabelas continuam visíveis e não podem ser fundidas silenciosamente; seleção ambígua deve permanecer fail-closed.
- A heurística vigente continua autorizada apenas a produzir candidatos simples. Ela não pode combinar coincidências de colunas para inventar relacionamento composto, ordem, cardinalidade ou autoridade.
- A mera existência de candidatos heurísticos simples que correspondam a partes de um relacionamento explícito composto não poderá, por si só, invalidar esse relacionamento composto autoritativo. Divergências reais e ambiguidades continuam visíveis e bloqueantes conforme política determinística a ser travada no PLAN.
- `encontrar_caminho`, a seleção direta e a seleção para `gerar_sql` deverão transportar a identidade composta completa. Empate ou múltiplos candidatos aplicáveis não poderá ser resolvido pela perda de colunas nem por promoção de score heurístico.

## 5. Preservação de grão

Para um JOIN composto preservar o grão a partir do lado corrente, continuam cumulativamente obrigatórias todas as garantias aceitas na SPEC-010:

1. relacionamento `APPROVED` e sem conflitos;
2. cardinalidade orientada `MANY_TO_ONE` ou `ONE_TO_ONE`, com autoridade suficiente e sem conflitos;
3. chave `PRIMARY_KEY` ou `UNIQUE`, com autoridade suficiente e sem conflitos, no lado alcançado;
4. igualdade exata e ordenada entre todas as colunas alcançadas pelo relacionamento e `ExplicitKey.columns`.

Subconjunto, superconjunto, mesma coleção em ordem diferente, chave ausente, cardinalidade inadequada/desconhecida, autoridade insuficiente ou qualquer conflito deve resultar em `BLOCKED`, sem SQL e sem deduplicação automática.

Relacionamentos simples seguem a mesma regra por meio de listas unitárias e devem conservar exatamente o comportamento aceito hoje.

## 6. Impacto mínimo nas superfícies existentes

- **Persistência:** leitura retrocompatível do legado e aceitação aditiva da forma em listas; nenhuma regravação automática.
- **Inferência:** permanece simples e heurística; nenhuma inferência composta.
- **Merge/conflitos:** identidade passa a considerar todos os pares ordenados e não pode truncar compostos.
- **`encontrar_caminho`:** grafo continua por tabelas, mas cada aresta carrega o relacionamento completo.
- **`gerar_join`:** descrição e eventual SQL sugerido devem usar todos os pares no `ON`.
- **`gerar_sql`:** cada aresta selecionada deve emitir todos os pares posicionais unidos por `AND` e aplicar o mesmo fail-closed atual.
- **`grain_preservation`:** endpoint alcançado deve ser a lista completa e ordenada antes da comparação com a chave.
- **`atualizar_catalogo`:** a identidade usada para detectar novos relacionamentos deve incluir as listas completas.
- **Contrato MCP:** exatamente 12 tools, mesmos nomes e finalidade; evolução apenas aditiva para consumidores de relacionamentos simples.

## 7. Não-escopo

- Interface MCP, UI, formulário, sidecar adicional ou workflow para cadastrar/homologar metadados.
- Inferência de relacionamento composto, chave, unicidade ou cardinalidade por nomes, posição ou dados.
- Profiler, leitura de valores, acesso ao Oracle, DDL remoto, catálogo remoto ou validação física de constraints.
- Planner/optimizer, custo, seletividade, `EXPLAIN PLAN` ou escolha sofisticada de caminho.
- Deduplicação, agregação implícita, `DISTINCT`, `ROW_NUMBER` ou regra de negócio automática.
- Alterar quantidade, nomes ou finalidade das 12 tools.
- Homologar qualquer relacionamento, chave, cardinalidade ou fato das tabelas HAP.
- Hardcode das 11 tabelas atuais ou de qualquer tabela/coluna de exemplo.
- Migração manual ou regravação automática dos metadados existentes.
- Nova dependência, banco de metadados, daemon, BI, Power BI ou Figma.
- PLAN, implementação, alteração de runtime/testes/metadata/config, commit, push, release ou publicação antes dos gates aplicáveis.

## 8. Critérios de aceite propostos

- **AC-001 — legado simples:** uma entrada válida com `source_column`/`target_column` carrega sem alteração do arquivo, normaliza para listas unitárias e mantém payload, seleção, conflito, SQL e gate single-column compatíveis.
- **AC-002 — novo formato simples:** listas unitárias válidas produzem o mesmo relacionamento e comportamento da forma legada, sem duplicação lógica.
- **AC-003 — validação estrutural:** listas vazias, tamanhos diferentes, identificadores duplicados/vazios, coluna inexistente, apenas um lado ou mistura de campos escalares e listas falham com mensagem clara antes de uso.
- **AC-004 — ordem e identidade:** todos os pares posicionais participam da identidade; orientação inversa preserva os pares; ordem diferente não corresponde silenciosamente à mesma chave ou relação.
- **AC-005 — JOIN composto preservador:** fixture genérica `TABELA_A → TABELA_B`, com relacionamento composto `APPROVED`, cardinalidade `MANY_TO_ONE` ou `ONE_TO_ONE` autorizada e chave composta exata/autorizada no destino, resulta em `PRESERVES` e SQL com todos os predicados `ON` unidos por `AND`.
- **AC-006 — fail-closed composto:** ausência ou insuficiência de unicidade, cardinalidade, autoridade, aprovação, correspondência exata/ordenada, ou presença de conflitos resulta em `BLOCKED`, sem SQL parcial e sem deduplicação.
- **AC-007 — inferência e merge:** heurística continua produzindo somente candidatos simples; componentes heurísticos não são promovidos a composto nem invalidam automaticamente uma declaração composta autoritativa; duplicidades e divergências reais permanecem determinísticas, visíveis e bloqueantes.
- **AC-008 — caminhos e geração:** seleção direta, `encontrar_caminho`, `gerar_join`, `gerar_sql` e `atualizar_catalogo` preservam a identidade composta completa e não truncam endpoints.
- **AC-009 — serialização:** metadado legado não exige migração manual; nova forma persiste/é lida sem perda de ordem; relacionamentos simples conservam os campos escalares públicos e recebem apenas extensão aditiva.
- **AC-010 — regressão:** consultas single-table, relacionamentos simples, conflitos vigentes, atualização do catálogo, inferência e testes aceitos nas specs anteriores permanecem compatíveis; exatamente 12 tools são expostas.
- **AC-011 — genericidade:** todos os testes novos usam fixtures sintéticas genéricas e nenhuma lógica de produto contém hardcode das tabelas RAW_HAP atuais.
- **AC-012 — contrato público:** schema e payload MCP antes/depois são comparados; qualquer necessidade de remover, renomear ou mudar o tipo de campo existente interrompe a execução em G5 antes da mudança incompatível.

## 9. Testes mínimos exigidos para futuro PLAN

O futuro PLAN, se autorizado, deverá incluir no mínimo:

1. legado simples e arquivo atual sem migração;
2. novo formato simples equivalente;
3. composto `N:1` preservador com chave composta exata;
4. composto sem unicidade, com chave parcial/reordenada, cardinalidade ausente/inadequada ou autoridade insuficiente, todos `BLOCKED`;
5. conflito de declarações da mesma identidade e ambiguidade entre identidades distintas;
6. heurística simples coexistindo com composto explícito sem promoção nem falso conflito por mera parcialidade;
7. caminho, JOIN sugerido e SQL final com todos os predicados em ordem;
8. regressão das 12 tools e do comportamento single-column;
9. validação de schema/payload público MCP e prova de ausência de hardcode;
10. preservação byte a byte do metadata real durante execução e testes.

## 10. Riscos e mitigação

- **Contrato público MCP:** consumidores podem depender dos campos escalares. Mitigação: preservá-los para casos simples, fazer extensão aditiva e exigir G5 para qualquer incompatibilidade.
- **Ambiguidade entre relacionamentos do mesmo par de tabelas:** a implementação atual escolhe pelo score. Mitigação: identidade completa, conflitos visíveis e fail-closed quando não houver escolha inequívoca.
- **Falso conflito entre heurística simples e declaração composta:** a heurística não conhece a unidade composta. Mitigação: não tratar componentes heurísticos como refutação automática do fato composto explícito.
- **Ordem de colunas:** ordenar alfabeticamente destruiria a correspondência dos pares. Mitigação: preservar ordem declarada em validação, identidade, serialização, SQL e comparação da chave.
- **Migração acidental:** normalização poderia induzir regravação. Mitigação: leitura adaptativa sem escrita automática e teste de integridade do arquivo real.
- **Duplicação de lógica simples/composta:** caminhos paralelos podem divergir. Mitigação: representação interna única em listas, usando lista unitária para o legado.

## 11. Avaliação para G1

**Recomendação: GO**, somente para a evolução mínima desta SPEC.

A lacuna é comprovada, necessária ao objetivo já aceito de preservação segura de grão, não cabe sem desvio material nas specs encerradas e possui resultado verificável. A estratégia proposta é aditiva: mantém o legado, normaliza internamente, preserva exatamente 12 tools e não requer migração manual dos metadados existentes.

Decisões solicitadas ao HUMAN/Product Owner:

1. aprovar o objetivo e o contrato retrocompatível das seções 2 e 3;
2. aprovar correspondência posicional ordenada e igualdade exata com `ExplicitKey.columns`;
3. aprovar que a heurística permaneça somente single-column e não invalide automaticamente compostos explícitos por coincidências parciais;
4. aprovar o fail-closed e os critérios das seções 5 e 8;
5. confirmar preservação das 12 tools, ausência de migração manual e exigência de G5 para eventual quebra pública;
6. aprovar o não-escopo, especialmente a exclusão da futura interface declarativa de cadastro;
7. se G1 for aprovado, autorizar separadamente apenas a criação de um PLAN-011 curto e proporcional, com parada obrigatória em G2 antes de qualquer implementação.

## 12. Gate atual

**G1 — APPROVED em 2026-09-18 pelo HUMAN/Product Owner.**

Foram aprovados os sete itens da seção 11 e autorizada exclusivamente a criação e validação documental do PLAN-011. Permanecem obrigatórias as invariantes: legado simples compatível; forma nova simples equivalente; compostos posicionais e ordenados; chave composta exata apta a sustentar preservação quando as demais autoridades forem suficientes; evidência incompleta ou conflitante bloqueada; exatamente 12 tools; heurística somente single-column; ausência de hardcode, migração manual, interface de cadastro, Oracle, profiler, planner/optimizer, deduplicação ou BI; e parada em G5 antes de qualquer quebra necessária do contrato MCP.

**G2 — APPROVED em 2026-09-18 pelo HUMAN/Product Owner.** O PLAN-011 foi autorizado para `IMPLEMENT → VERIFY → EVIDENCE`, estritamente dentro do orçamento da seção 3, sem quebra pública, migração de metadata, commit, push, release ou publicação.

## 13. Implementação e verificação

A implementação parcial encontrada após a interrupção foi recuperada e concluída sem ampliar o orçamento. Endpoints escalares legados e listas unitárias convergem para a representação interna vetorial; relacionamentos compostos preservam ordem, identidade, merge, caminhos, grain gate, SQL e JOIN sugerido. A heurística continua single-column e coincidências parciais não invalidam um composto explícito, enquanto divergências reais permanecem conflitantes.

Evidência reproduzível:

- `.venv\Scripts\python.exe -m pytest -q`: `82 passed`;
- `scripts\smoke_test.py`: servidor iniciou com exatamente `12 tools`;
- testes compostos: validação estrutural, equivalência legado/lista unitária, preservação com chave exata, bloqueio de chave parcial/reordenada e SQL com todos os predicados posicionais;
- `metadata/relationships.json` permaneceu inalterado e nenhum arquivo fora do orçamento foi criado pela implementação.

Limitação residual: a suíte depende do ambiente virtual local para disponibilizar o SDK `mcp`; o interpretador global não o possui. Nenhum fato HAP foi homologado.

**G4 — APPROVED em 2026-09-18 pelo HUMAN/Product Owner.** A implementação, VERIFY, EVIDENCE e riscos residuais foram aceitos. `SPEC-011 → ACCEPTED/DONE`. Este aceite não autoriza commit, push, release, publicação ou trabalho fora do escopo.
