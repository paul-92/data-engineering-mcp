# SPEC-010 — Key/Cardinality & Grain Authority

| Campo | Valor |
|---|---|
| ID | SPEC-010 |
| Título | Key/Cardinality & Grain Authority |
| Tipo | Evolução funcional mínima proposta após teste real de aceitação |
| Status | ACCEPTED |
| Resultado | DONE |
| Dependências | SPEC-002, SPEC-003, SPEC-004, SPEC-006 e SPEC-009 aceitas |
| Product Owner | HUMAN |
| Implementação autorizada | Concluída dentro do PLAN-010; aceite HUMAN registrado |
| Última atualização | 2026-09-18 |

## 1. Resultado do teste real de aceitação

O pedido real exigiu uma consulta Oracle envolvendo pessoa, usuário e plano, com grão de exatamente uma linha por `CD_USUARIO`. O MCP encontrou os candidatos:

- `RAW_HAP_TB_PESSOA.CD_PESSOA = RAW_HAP_TB_USUARIO.CD_PESSOA`, `authority=INFERRED`, `confidence=MEDIUM`, `score=50`;
- `RAW_HAP_TB_USUARIO.CD_PLANO = RAW_HAP_TB_PLANO.CD_PLANO`, `authority=INFERRED`, `confidence=MEDIUM`, `score=60`.

O fail-closed aceito na SPEC-009 funcionou: nenhum SQL ou mecanismo de deduplicação foi produzido. Além do bloqueio por autoridade dos relacionamentos, o MCP informou que não podia provar que os JOINs preservariam o grão solicitado, pois não conhece unicidade, chaves ou cardinalidade dos endpoints.

**Resultado do Acceptance Test: BLOCKED BY CAPABILITY.**

O bloqueio é correto e deve permanecer até existir evidência autorizada. O teste não homologa nenhum dos relacionamentos nem afirma que `CD_USUARIO`, `PESSOA.CD_PESSOA` ou `PLANO.CD_PLANO` sejam únicos.

## 2. INSPECT e lacuna comprovada

Baseline Git observado: `862abae4237997bc7165b27a4fc179429ff11359`, branch `main`, com mudanças locais preexistentes preservadas. As implementações aceitas das specs anteriores continuam no worktree local e não foram limpas, revertidas ou reatribuídas.

O INSPECT confirmou:

1. `descrever_tabela` expõe somente arquivo, planilha, colunas, posições e quantidade de colunas;
2. `ColumnSchema` e `TableSchema` não representam PK, UNIQUE, FK, nulabilidade ou outras constraints;
3. `ExplicitRelationship` persiste somente endpoints, fonte, autoridade e eventual decisão HUMAN;
4. `RelationshipCandidate` não representa cardinalidade, unicidade dos endpoints nem efeito sobre o grão;
5. `QueryIntent.grain` registra o grão solicitado, mas não contém evidência capaz de provar sua preservação;
6. nenhuma das 12 tools atuais consulta ou determina unicidade/cardinalidade;
7. `metadata/relationships.json` contém apenas a coleção `relationships` e não há outra persistência autoritativa para chaves ou cardinalidade;
8. posição da coluna, nome semelhante, score, confiança, repetição ou uso anterior não constituem evidência de unicidade ou cardinalidade.

A SPEC-002 separou corretamente autoridade do relacionamento e colocou cardinalidade/fan-out fora de seu escopo. A SPEC-009 preservou esse limite. Portanto, absorver esta capacidade em uma spec encerrada seria desvio material; uma única spec nova é a menor evolução documental coerente.

## 3. Objetivo mínimo proposto

Permitir representar, persistir e consultar conhecimento explícito e autoritativo suficiente para responder, sem acessar dados reais, se cada JOIN de uma intenção preserva o grão solicitado.

A capacidade mínima deve:

- representar chaves e garantias de unicidade, inclusive conjuntos de uma ou mais colunas;
- representar cardinalidade orientada de relacionamento como `1:1`, `N:1`, `1:N`, `N:N` ou `UNKNOWN`;
- manter separadas a validade do relacionamento, sua cardinalidade e a autoridade/proveniência de cada afirmação;
- aceitar fatos somente de fonte explícita identificável, como DDL, dicionário de dados ou metadados de constraints fornecidos ao sistema, ou de decisão HUMAN registrada;
- preservar `INFERRED`/desconhecido como não autorizado para provar unicidade ou preservação de grão;
- expor o resultado aos consumidores pelas estruturas e tools existentes sempre que isso for suficiente, preservando exatamente 12 tools salvo prova no futuro PLAN de que uma mudança é indispensável;
- decidir de forma conservadora se o lado alcançado pelo JOIN admite no máximo uma correspondência por linha do grão corrente.

Esta spec não declara fatos sobre as tabelas HAP. Ela cria somente a capacidade de registrar e consultar fatos que venham a ser fornecidos com autoridade adequada.

## 4. Política mínima de preservação de grão

Relacionamento e cardinalidade são afirmações independentes. Um relacionamento autorizado prova que os endpoints podem ser associados; não prova quantas linhas correspondem. Uma chave ou constraint autorizada pode provar unicidade de um endpoint; não homologa por si só o relacionamento.

Para reconhecer um JOIN como preservador do grão, a futura solução deverá exigir cumulativamente:

1. relacionamento utilizável segundo o fail-closed vigente da SPEC-009;
2. cardinalidade orientada `N:1` ou `1:1` a partir do grão corrente, sustentada por unicidade explícita suficiente no lado alcançado;
3. autoridade e proveniência suficientes e sem conflitos para as afirmações usadas;
4. correspondência entre as colunas do JOIN e a chave/conjunto UNIQUE declarado, sem completar fatos por nome ou posição.

Cardinalidade `1:N`, `N:N`, `UNKNOWN`, ausente, conflitante ou sem autoridade suficiente deve sinalizar risco de multiplicação e solicitar regra de negócio ou evidência. Nenhuma dessas situações autoriza deduplicação automática, seleção arbitrária de linha, agregação implícita ou emissão de SQL que alegue preservar o grão.

Uma FK pode sustentar integridade/correspondência quando explicitamente fornecida, mas não substitui a prova de unicidade do lado que precisa admitir no máximo uma correspondência. Nulabilidade, existência obrigatória de correspondência e escolha de `INNER`/`LEFT JOIN` não devem ser inferidas; quando relevantes ao pedido, permanecem pendências explícitas.

## 5. Autoridade e proveniência

A solução deve reutilizar, sem confundir, os princípios de autoridade da SPEC-002:

- fatos derivados apenas de heurística permanecem `INFERRED` e nunca provam unicidade/cardinalidade;
- fatos `KNOWN` exigem fonte explícita identificável fornecida ao sistema, como referência de DDL, dicionário ou metadado de constraint;
- fatos `APPROVED` exigem decisão HUMAN registrada;
- conflitos entre fontes ou decisões ficam visíveis e bloqueiam a conclusão automática;
- autoridade de chave/unicidade e cardinalidade deve ser consultável independentemente da autoridade do relacionamento.

O futuro PLAN deverá definir a menor política determinística para quais fontes explícitas são suficientes em cada afirmação, sem relaxar o requisito já aceito de relacionamento `APPROVED` e livre de conflitos para JOIN automático.

## 6. Menor evolução candidata

Sem comprometer implementação antes dos gates, o menor caminho observado é estender os modelos e a persistência local já existentes e expor os novos campos nas tools atuais de descrição/relacionamento/caminho. A avaliação de preservação pode ser incorporada ao fluxo existente de intenção e geração, mantendo o bloqueio antes de qualquer SQL.

Preferências obrigatórias para um futuro PLAN:

- extensão aditiva de estruturas e arquivo(s) local(is) de metadados existentes;
- validação estrita de tabelas, colunas, conjuntos de chave, autoridade, proveniência e conflitos;
- nenhuma descoberta por leitura de valores;
- nenhuma nova tool enquanto as 12 atuais puderem expor e consumir o conhecimento necessário;
- mudança limitada aos modelos, persistência/merge, exposição, gate de grão e testes diretamente necessários.

Esta seção é direção para avaliação posterior, não um PLAN e não autoriza arquivos, estratégia final ou implementação.

## 7. Não-escopo

- Conectar ao Oracle, consultar catálogo remoto ou acessar dados reais.
- Profiler de dados, amostragem, contagem de distintos, estatísticas, estimativa de seletividade ou detecção empírica de duplicatas.
- Optimizer, `EXPLAIN PLAN`, planner sofisticado, escolha de caminho por custo ou execução SQL.
- Deduplicação automática, `ROW_NUMBER`, agregação implícita, seleção arbitrária de registros ou criação de regra de negócio.
- Inferir unicidade, PK, FK ou cardinalidade por posição, nome, prefixo, score, confiança ou convenção.
- Homologar os relacionamentos ou as chaves do teste real.
- UI, banco de metadados, daemon, framework, nova dependência, nova capacidade de BI, Power BI ou Figma.
- Alterar a quantidade ou finalidade das 12 tools, salvo futura evidência e decisão HUMAN específica de indispensabilidade.
- Commit, push, release, publicação, instalação global ou configuração externa.
- Implementar código/testes antes de G2 ou fora de futuro plano aprovado.

## 8. Critérios de aceite propostos

- **AC-001:** o sistema representa e persiste, com validação estrita, chaves/garantias de unicidade simples ou compostas, sua fonte, autoridade, decisão quando aplicável e conflitos.
- **AC-002:** o sistema representa e persiste cardinalidade orientada `1:1`, `N:1`, `1:N`, `N:N` ou `UNKNOWN`, com proveniência e autoridade próprias, sem derivá-la de posição ou nome.
- **AC-003:** relacionamento, cardinalidade e autoridade de chave/unicidade permanecem sinais distintos e consultáveis; nenhum deles promove silenciosamente outro.
- **AC-004:** somente evidência explícita fornecida ao sistema ou decisão HUMAN registrada pode sustentar unicidade/cardinalidade; inferência, score e confiança nunca são prova.
- **AC-005:** um caso autorizado `N:1` ou `1:1`, com unicidade suficiente e sem conflitos no lado alcançado, é reconhecido deterministicamente como preservador do grão corrente, desde que o relacionamento também passe pelo fail-closed vigente.
- **AC-006:** `1:N`, `N:N`, `UNKNOWN`, ausência de metadado, conflito ou autoridade insuficiente resulta em bloqueio legível por risco de multiplicação e pedido de regra/evidência, sem SQL parcial ou deduplicação automática.
- **AC-007:** o caso pessoa–usuário–plano permanece bloqueado sem fatos novos; ao fornecer metadados autoritativos adequados, o sistema consegue avaliar separadamente cada JOIN e explicar por que preserva ou ameaça uma linha por `CD_USUARIO`.
- **AC-008:** metadado inválido — tabela/coluna inexistente, chave vazia, cardinalidade inválida, `APPROVED` sem decisão ou fontes conflitantes — falha de forma clara e segura.
- **AC-009:** consultas single-table, inferência de relacionamentos e controles aceitos nas specs anteriores permanecem compatíveis; exatamente as 12 tools são preservadas, salvo G3/G5 específico baseado em indispensabilidade comprovada.
- **AC-010:** testes proporcionais cobrem persistência, autoridade, orientação da cardinalidade, chave composta, conflitos, preservação e multiplicação do grão, além do teste real de aceitação, sem acessar dados reais.

## 9. Impactos e riscos

**Impacto positivo:** fecha a menor lacuna necessária para que o MCP diferencie “há um relacionamento autorizado” de “este JOIN não multiplica o grão”, mantendo decisão auditável e fail-closed.

**Riscos/ônus:** fontes fornecidas podem estar incorretas ou desatualizadas; orientação de cardinalidade pode ser registrada ao contrário; chaves compostas ampliam a validação; consumidores podem confundir preservação de quantidade máxima com correspondência obrigatória. Proveniência, validação estrita, conflitos visíveis e bloqueio conservador mitigam esses riscos sem exigir acesso ao banco.

## 10. Avaliação para G1

**Recomendação: GO**, somente para a capacidade mínima definida nesta spec. A lacuna foi demonstrada por um teste real, é necessária ao objetivo já aprovado de geração segura e não cabe nas specs encerradas sem reabrir seus não-escopos.

Decisões solicitadas ao HUMAN/Product Owner:

1. aprovar o objetivo mínimo e a separação entre relacionamento, cardinalidade e autoridade de chave/unicidade;
2. aprovar a política fail-closed de preservação de grão da seção 4;
3. aprovar DDL/dicionário/metadados de constraints fornecidos ao sistema e decisão HUMAN como únicas classes de fontes candidatas, sujeitas à política determinística do futuro PLAN;
4. confirmar que nenhum fato do caso HAP está homologado por esta spec;
5. aprovar o não-escopo e a preferência por estender estruturas/tools existentes, preservando exatamente 12 tools;
6. se G1 for aprovado, autorizar separadamente apenas a criação de um PLAN-010 curto e proporcional, com parada obrigatória em G2 antes de qualquer implementação.

## 11. Registro de aprovação

| Gate | Decisor | Data | Decisão | Condições/observações |
|---|---|---|---|---|
| G1 — SPEC-010 | HUMAN/Product Owner | 2026-09-17 | APPROVED | Itens 1 a 6 da seção 10 aprovados; autorizada somente a criação de um PLAN-010 curto e proporcional, com parada obrigatória em G2 |
| G2 — PLAN-010 | HUMAN/Product Owner | 2026-09-18 | APPROVED | Itens 1 a 7 da seção 11 do plano aprovados; autorizada somente a execução de `IMPLEMENT → VERIFY → EVIDENCE` dentro do orçamento, com parada em G4 |
| G4 — SPEC-010 | HUMAN/Product Owner | 2026-09-18 | APPROVED | Resultado técnico e riscos residuais aceitos; autorizadas somente a reconciliação documental e a prova E2E temporária complementar, seguidas de VERIFY/EVIDENCE |

## 12. Gate atual

**G1 — APPROVED em 2026-09-17 pelo HUMAN/Product Owner.** O objetivo, a política fail-closed, as fontes candidatas, a ausência de homologação do caso HAP, o não-escopo e a preservação das 12 tools foram aprovados.

**G2 — APPROVED em 2026-09-18 pelo HUMAN/Product Owner.** A implementação, verificação e evidência do PLAN-010 foram autorizadas e executadas dentro do orçamento.

**G4 — APPROVED em 2026-09-18 pelo HUMAN/Product Owner.** A SPEC-010 está `ACCEPTED` e seu resultado está `DONE`.

O aceite não homologa nenhum fato HAP. A prova E2E complementar autorizada permanece limitada a ambiente temporário isolado e fixtures sintéticas genéricas, seguida de VERIFY/EVIDENCE, sem mudança de produto.
