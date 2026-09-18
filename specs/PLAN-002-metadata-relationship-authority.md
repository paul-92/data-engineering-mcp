# PLAN-002 — Metadata & Relationship Authority

| Campo | Valor |
|---|---|
| Spec | `SPEC-002` |
| Baseline | `862abae4237997bc7165b27a4fc179429ff11359` |
| Gate de entrada | G1 aprovado em 2026-09-11 pelo HUMAN/Product Owner |
| Status | `COMPLETED` |
| Implementação autorizada | Sim — G2 aprovado em 2026-09-11 pelo HUMAN/Product Owner |

## 1. Objetivo e solução mínima

Adicionar autoridade e proveniência aos relacionamentos existentes com a menor superfície possível: um arquivo JSON local, versionado e legível por humanos, carregado pelo mecanismo atual. Não criar banco, painel, framework, serviço, nova tool ou dependência.

Cada relacionamento continuará identificado pelas tabelas e colunas de origem/destino e passará a expor:

- `authority`: `INFERRED`, `KNOWN` ou `APPROVED`;
- `source`: origem identificável; para inferência, a heurística atual;
- `decision`: obrigatório somente para `APPROVED`, com identificador, data e decisor humano.

O JSON conterá apenas relacionamentos explícitos `KNOWN` ou `APPROVED`. `INFERRED` continuará sendo produzido pela heurística atual. A edição do arquivo será a única interface de manutenção nesta spec.

## 2. Arquivos mínimos previstos

- Criar `metadata/relationships.json`: metadados explícitos locais, inicialmente vazio ou com exemplos apenas na documentação; sem conteúdo do BI S/CEP.
- Alterar `src/data_engineering_mcp/models.py`: enum/campos aditivos de autoridade, fonte, decisão e conflito.
- Alterar `src/data_engineering_mcp/relationships.py`: carregar/validar o JSON, combinar metadado explícito com inferência e expor conflitos.
- Alterar `src/data_engineering_mcp/server.py`: fornecer o caminho local ao engine e manter a recarga coerente, sem adicionar ou remover tools.
- Alterar `tests/test_relationships.py`: cobrir classificação, precedência, decisão humana obrigatória e conflitos.
- Alterar `README.md`: documentar o JSON, os três estados e a edição manual.

Somente se necessário para preservar fixtures isoladas, alterar `tests/conftest.py`. Nenhum outro arquivo está autorizado; necessidade adicional exige retorno ao HUMAN/Product Owner.

## 3. Comportamento e precedência

1. Relação apenas heurística recebe `INFERRED` e mantém score/rationale atuais.
2. Entrada explícita válida recebe `KNOWN`; se trouxer decisão humana completa, recebe `APPROVED`.
3. O sistema não aceita `APPROVED` sem `decision.id`, `decision.date` e decisor identificado como `HUMAN/Product Owner`; uso anterior, score ou repetição nunca promovem autoridade.
4. Para a mesma identidade de relação, metadado explícito prevalece sobre a inferência.
5. Se fontes discordarem sobre endpoints ou houver entradas explícitas incompatíveis, o conflito é retornado de modo determinístico e visível; não há promoção nem resolução silenciosa.
6. Arquivo ausente equivale a nenhum metadado explícito e preserva a inferência atual. JSON inválido ou entrada inválida falha de forma clara, sem fingir que o metadado foi aplicado.
7. As 12 tools, seus argumentos e a capacidade atual de inferência permanecem; os campos novos nas respostas de relacionamento são aditivos.

## 4. Sequência de implementação após G2

1. Definir os modelos e a validação do JSON sem dependência nova.
2. Integrar a carga e a mesclagem determinística no `RelationshipEngine`.
3. Conectar inicialização/recarga existentes e expor os campos pelas respostas atuais.
4. Adicionar os testes mínimos e atualizar a documentação.
5. Executar as verificações e registrar evidências; qualquer desvio material para no G3.

## 5. Testes e verificações mínimas

- Relação somente inferida retorna `INFERRED` com fonte heurística.
- Entrada explícita retorna `KNOWN` com fonte identificável.
- Entrada com decisão humana completa retorna `APPROVED`; decisão ausente/inválida é rejeitada.
- Metadado explícito prevalece sobre inferência da mesma relação.
- Conflitos ficam visíveis, estáveis e não são promovidos automaticamente.
- Arquivo ausente preserva o comportamento atual; JSON inválido produz erro claro.
- Suíte existente continua passando e a contagem de tools permanece exatamente 12.
- Diff final não contém datasets, BI S/CEP, Power BI MCP, configuração global do Codex, Git remoto ou release.

## 6. Rollback

Reverter apenas os arquivos listados na seção 2 e remover `metadata/relationships.json`. Verificar que a suíte anterior volta a passar, que as 12 tools permanecem disponíveis e que a inferência retorna ao comportamento do baseline. Como não há migração nem escrita em datasets, o rollback não exige conversão de dados.

## 7. Critérios de aceite

- **AC-P2-001:** `INFERRED`, `KNOWN` e `APPROVED` são expostos com fonte e sem promoção implícita.
- **AC-P2-002:** `APPROVED` somente é válido com decisão do HUMAN/Product Owner registrada.
- **AC-P2-003:** precedência explícita é determinística e todo conflito relevante fica visível.
- **AC-P2-004:** as 12 tools, seus argumentos e a inferência atual permanecem compatíveis; mudanças de resposta são somente aditivas.
- **AC-P2-005:** a persistência/interface consiste apenas no JSON local e edição manual, sem banco, painel, framework, serviço ou dependência nova.
- **AC-P2-006:** os testes mínimos da seção 5 passam e cobrem os critérios AC-001 a AC-007 da SPEC-002.
- **AC-P2-007:** nenhum artefato do BI S/CEP é incorporado e nenhum item protegido é alterado.
- **AC-P2-008:** rollback documental e de implementação é executável apenas sobre os arquivos previstos.

## 8. Impactos positivos e riscos/ônus

**Impactos positivos:** consumidores distinguem hipótese, conhecimento explícito e homologação humana; JOINs inseguros ficam identificáveis; a solução continua local, auditável e pequena.

| Risco/ônus | Mitigação |
|---|---|
| JSON ficar desatualizado ou incorreto | Proveniência visível, validação estrita e conflito exposto |
| Edição manual gerar erro | Schema pequeno, erro claro e testes de entradas inválidas |
| Consumidor ignorar autoridade | Campos explícitos nas respostas atuais e documentação |
| Campo aditivo afetar consumidor rígido | Teste de regressão e registro do risco; nenhuma remoção/renomeação |
| Escopo crescer para catálogo corporativo | Um arquivo, sem CRUD/tool/painel; ampliação exige nova decisão |

## 9. Decisões HUMAN/Product Owner para G2

1. Autorizar somente os arquivos e a sequência descritos neste plano.
2. Aprovar `metadata/relationships.json` editado manualmente como persistência/interface mínima.
3. Confirmar que não haverá nova tool, dependência, banco, painel, framework ou infraestrutura.
4. Aceitar campos aditivos nas respostas atuais, preservando as 12 tools e a inferência existente.
5. Aprovar os testes, critérios de aceite e rollback acima.
6. Confirmar que qualquer arquivo adicional, mudança incompatível ou uso do BI S/CEP exige interrupção e nova decisão.

## 10. Registro de G2, evidências e gate atual

**G2 — APPROVED em 2026-09-11 pelo HUMAN/Product Owner.** Autorizada somente a execução de IMPLEMENT → VERIFY → EVIDENCE dentro deste plano, sem ampliação de escopo.

Evidências objetivas de 2026-09-11:

- suíte completa: `31 passed in 1.81s`;
- smoke MCP: handshake com `data-engineering-mcp` v0.1.0, exatamente 12 tools, `listar_tabelas_error=False` e `status_catalogo_error=False`;
- JSON persistido em `metadata/relationships.json`, inicialmente vazio e sem conteúdo BI S/CEP;
- diff restrito aos arquivos autorizados e às atualizações documentais desta SPEC/PLAN; nenhuma dependência, dataset, integração, configuração global, remoto ou release alterado.

## 11. Encerramento

**G4 — APPROVED em 2026-09-11 pelo HUMAN/Product Owner.** As evidências e o risco residual foram aceitos. O PLAN-002 está `COMPLETED` e a SPEC-002 foi encerrada como `ACCEPTED/DONE`.

Nenhum commit, push ou release foi autorizado ou realizado por este encerramento.
