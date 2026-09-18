# PLAN-010 — Key/Cardinality & Grain Authority

| Campo | Valor |
|---|---|
| Spec | SPEC-010 |
| Status | COMPLETED |
| Gate atual | G4 — APPROVED |
| Baseline Git | `862abae4237997bc7165b27a4fc179429ff11359` em `main`, com mudanças locais preexistentes preservadas |
| Dependências | SPEC-010 com G1 aprovado; SPEC-002, SPEC-003, SPEC-004, SPEC-006 e SPEC-009 aceitas |
| Implementação autorizada | Concluída, verificada e aceita dentro do orçamento aprovado |
| Última atualização | 2026-09-18 |

## 1. Objetivo e solução mínima

Implementar somente a capacidade aprovada na SPEC-010: carregar metadados locais explícitos de chave/unicidade e cardinalidade, preservar autoridade e proveniência independentes e bloquear de forma determinística uma geração multi-tabela com grão declarado quando não houver prova suficiente de que cada JOIN preserva esse grão.

A solução será aditiva e reutilizará o documento local e as 12 tools atuais. Não haverá Oracle, leitura de dados, profiler, nova tool, nova dependência, planner avançado ou deduplicação.

## 2. Contrato de metadados travado

### 2.1 Documento local

`metadata/relationships.json` continuará sendo o único documento autoritativo local e aceitará:

- a coleção existente `relationships`, preservada;
- uma nova coleção opcional `keys`, vazia por padrão e compatível com o documento atual que contém somente `relationships`.

Cada chave explícita conterá, no mínimo:

- `table`;
- `columns`, lista não vazia e ordenada de uma ou mais colunas;
- `kind`, limitado a `PRIMARY_KEY` ou `UNIQUE`;
- `source`, não vazio;
- `authority`, limitado a `KNOWN` ou `APPROVED`;
- `decision` somente e obrigatoriamente para `APPROVED`;
- conflitos produzidos durante o merge/validação, sem resolução silenciosa.

Cada relacionamento explícito poderá acrescentar uma afirmação de cardinalidade orientada da origem para o destino:

- `cardinality`: `ONE_TO_ONE`, `MANY_TO_ONE`, `ONE_TO_MANY`, `MANY_TO_MANY` ou `UNKNOWN`;
- `cardinality_source` e `cardinality_authority` próprios;
- `cardinality_decision` somente e obrigatoriamente para cardinalidade `APPROVED`;
- cardinalidade ausente será tratada como `UNKNOWN`, nunca inferida de nome, posição, score ou confiança.

Os nomes `1:1`, `N:1`, `1:N`, `N:N` usados na spec correspondem, respectivamente, aos valores persistidos acima. A orientação sempre será `source_table → target_table`; ao percorrer no sentido inverso, `MANY_TO_ONE` e `ONE_TO_MANY` serão invertidos deterministicamente, enquanto `ONE_TO_ONE`, `MANY_TO_MANY` e `UNKNOWN` permanecem simétricos.

### 2.2 Política de autoridade suficiente

- Relacionamento automático continua exigindo `APPROVED` e ausência de conflitos, sem alteração da SPEC-009.
- Chave/unicidade é suficiente quando `KNOWN` com fonte explícita identificável ou `APPROVED` com decisão HUMAN, sempre sem conflitos.
- Cardinalidade é suficiente quando `KNOWN` com fonte explícita identificável ou `APPROVED` com decisão HUMAN, sempre sem conflitos.
- `INFERRED`, campo ausente, `UNKNOWN`, fonte vazia, decisão inválida ou conflito nunca provam preservação de grão.
- Uma afirmação de cardinalidade não cria uma chave; uma chave não homologa relacionamento nem cria cardinalidade.

Não haverá importador ou parser de DDL. DDL, dicionário e metadados de constraints são referências de proveniência fornecidas no documento, não fontes acessadas automaticamente.

## 3. Gate mínimo de preservação de grão

`SqlGenerationRequest` ganhará um campo opcional e aditivo `grain`, exposto como parâmetro opcional da tool existente `gerar_sql`. Ausência de `grain` preservará o comportamento já aceito; presença de `grain` exigirá validação antes da emissão do SQL.

Para cada aresta escolhida a partir do conjunto de tabelas já conectado, o gate deverá:

1. aplicar primeiro o gate vigente de relacionamento `APPROVED` e sem conflitos;
2. orientar a cardinalidade no sentido do JOIN efetivamente percorrido;
3. exigir cardinalidade suficiente `MANY_TO_ONE` ou `ONE_TO_ONE`;
4. exigir chave `PRIMARY_KEY` ou `UNIQUE` suficiente cujas colunas correspondam exatamente às colunas do endpoint alcançado pelo JOIN;
5. bloquear antes da emissão de SQL se qualquer prova estiver ausente, desconhecida, conflitante ou incompatível;
6. retornar motivo legível que diferencie autoridade do relacionamento, cardinalidade e unicidade;
7. nunca gerar SQL parcial, deduplicação, agregação ou regra substituta.

`ONE_TO_MANY`, `MANY_TO_MANY` e `UNKNOWN` sempre bloqueiam a alegação de preservação. O gate prova somente “no máximo uma correspondência no lado alcançado”; não infere existência obrigatória, nulabilidade nem equivalência entre `INNER` e `LEFT JOIN`.

O `grain` declarado deverá referenciar colunas válidas do conjunto de tabelas solicitado. Esta etapa não criará propagação sofisticada de grão nem escolherá caminhos por custo: ela somente verifica, na ordem determinística atual dos JOINs, se cada travessia preserva o grão declarado.

## 4. Exposição pelas 12 tools existentes

- `descrever_tabela` acrescentará as chaves explícitas válidas da tabela, com autoridade, fonte, decisão e conflitos.
- `inferir_relacionamentos` e `encontrar_caminho` acrescentarão cardinalidade e sua autoridade/proveniência aos objetos de relacionamento já retornados.
- `gerar_join` acrescentará o estado de preservação por direção e motivos separados; continuará sem `sql_sugerido` quando o relacionamento estiver bloqueado e não alegará preservação sem cardinalidade e unicidade suficientes.
- `gerar_sql` aceitará `grain` opcional e aplicará o gate da seção 3.
- `atualizar_catalogo` recarregará o mesmo documento e seus novos metadados.

Nenhuma tool será criada, removida ou renomeada; finalidade e quantidade permanecem exatamente 12.

## 5. Arquivos e orçamento de mudança

Somente estes arquivos poderão ser criados ou alterados após G2:

| Arquivo | Mudança máxima autorizável |
|---|---|
| `specs/SPEC-010-key-cardinality-grain-authority.md` | Registrar decisões e evidência factual, sem alterar critérios ou escopo |
| `specs/PLAN-010-key-cardinality-grain-authority.md` | Registrar G2, execução, verificação, evidência e gate final |
| `src/data_engineering_mcp/models.py` | Modelos/enums estritos para chaves, cardinalidade, autoridade e `grain` opcional |
| `src/data_engineering_mcp/relationships.py` | Carga/merge/validação do documento ampliado, orientação e consulta de provas |
| `src/data_engineering_mcp/sql_generator.py` | Gate de preservação de grão antes da emissão SQL |
| `src/data_engineering_mcp/server.py` | Exposição aditiva nas tools existentes, sem alterar a contagem |
| `metadata/relationships.json` | Somente ajuste estrutural compatível, se tecnicamente necessário; nenhum fato HAP real |
| `README.md` | Documentar contrato, política, limites e exemplo fictício |
| `tests/test_relationships.py` | Persistência, validação, orientação, autoridade, chave composta e conflitos |
| `tests/test_sql_generator.py` | Casos preservador/bloqueador e ausência de SQL parcial |
| `tests/test_server.py` | Contrato público aditivo e smoke de exatamente 12 tools |

Limite: até 11 arquivos, incluindo os dois documentos já criados. Nenhum arquivo novo além do PLAN-010 é previsto. `query_intent.py`, datasets e skill permanecem fora do orçamento porque o gate mínimo pode ser realizado diretamente no request já consumido pela geração. Se isso se provar falso, parar em G3 antes de ampliar o orçamento.

## 6. Sequência de implementação após G2

1. Registrar G2 no PLAN-010, sem reinterpretar sua decisão.
2. Criar testes de contrato e validação para o documento compatível e os modelos estritos.
3. Implementar carga, merge, conflitos, consulta de chaves e orientação de cardinalidade.
4. Expor os sinais nas tools existentes e confirmar a contagem de 12.
5. Implementar o `grain` opcional e o gate fail-closed no gerador.
6. Documentar somente o contrato implementado, com exemplos fictícios.
7. Executar a verificação da seção 7 e registrar evidências reproduzíveis.
8. Parar em G4 para aceite HUMAN; não declarar `DONE` ou `ACCEPTED`.

## 7. Verificação e evidência mínimas

### 7.1 Testes automatizados

- documento legado `{"relationships": []}` continua válido;
- chaves simples e compostas `KNOWN`/`APPROVED` válidas são carregadas sem promoção;
- tabela/coluna inexistente, chave vazia/duplicada, autoridade/decisão inválida e campos extras falham claramente;
- cardinalidade ausente vira `UNKNOWN`; orientação inversa é correta;
- conflitos de chave ou cardinalidade ficam visíveis e bloqueiam;
- relacionamento, chave e cardinalidade mantêm autoridades independentes;
- `MANY_TO_ONE`/`ONE_TO_ONE` com chave correspondente e autoridade suficiente preservam o grão;
- `ONE_TO_MANY`, `MANY_TO_MANY`, `UNKNOWN`, chave incompatível/ausente ou conflito bloqueiam sem SQL parcial;
- single-table e geração multi-tabela sem `grain` mantêm o contrato anterior;
- `gerar_join`, caminho e descrição expõem os novos sinais;
- smoke confirma exatamente os mesmos 12 nomes de tools.

### 7.2 Teste real controlado

Executar duas variantes sem acesso a dados:

1. com o metadado real vazio, repetir pessoa–usuário–plano e confirmar `BLOCKED BY CAPABILITY`, sem SQL ou deduplicação;
2. em fixture isolada, fornecer fatos fictícios autorizados equivalentes a `USUARIO → PESSOA N:1` e `USUARIO → PLANO N:1`, com unicidade correspondente, e confirmar avaliação separada de ambas as arestas e preservação de uma linha por usuário.

A fixture não poderá ser copiada para `metadata/relationships.json` como fato real nem constituirá homologação dos relacionamentos HAP.

### 7.3 Comandos e registros

- suíte específica dos três arquivos de teste do orçamento;
- suíte completa existente;
- `git diff --check`;
- inspeção do diff somente contra o orçamento;
- smoke da fronteira MCP e contagem/nome das tools;
- registro de ambiente, esperado, observado, limitações e riscos residuais.

## 8. Rastreabilidade

| Critério SPEC-010 | Cobertura principal |
|---|---|
| AC-001 | Modelos/documento de chaves; testes de chave simples, composta, autoridade e conflito |
| AC-002 | Cardinalidade orientada no relacionamento; testes de todos os valores e inversão |
| AC-003 | Modelos e payloads separados; testes de não promoção |
| AC-004 | Validação de fonte/decisão e casos negativos |
| AC-005 | Gate do gerador com `MANY_TO_ONE`/`ONE_TO_ONE` e chave correspondente |
| AC-006 | Bloqueios de multiplicação/desconhecido/conflito sem SQL parcial |
| AC-007 | Duas variantes do teste real controlado |
| AC-008 | Matriz de metadados inválidos |
| AC-009 | Regressão, compatibilidade e smoke das 12 tools |
| AC-010 | Suíte específica, suíte completa e evidência reproduzível |

## 9. Riscos, mitigação e paradas

| Risco | Mitigação/parada |
|---|---|
| Cardinalidade registrada no sentido errado | Orientação explícita e testes de inversão |
| `KNOWN` usado sem fonte real | `source` obrigatório e não vazio; nenhuma coleta automática |
| Cardinalidade contradizer unicidade | Exigir cardinalidade e chave correspondente cumulativamente; conflito bloqueia |
| Compatibilidade do JSON legado | Coleção `keys` opcional e teste do documento atual |
| Escopo crescer para FK/nulabilidade/planner | Manter como não-escopo e parar em G3 se indispensável |
| Alteração pública incompatível | Somente campos/parâmetro opcionais aditivos; qualquer incompatibilidade exige G3/G5 |
| Mudanças locais preexistentes se sobreporem | Editar sobre o estado atual, limitar hunks à SPEC-010 e nunca limpar/reverter |

Parar em G3 antes de: criar nova tool/arquivo/dependência; modificar `query_intent.py` ou a skill; alterar formato de modo incompatível; importar DDL; acessar dados; ampliar para FK, nulabilidade ou planejamento de caminho; exceder o orçamento; ou adotar estratégia materialmente diferente.

## 10. Rollback

Rollback técnico, se autorizado, consistirá somente em remover os campos/modelos/gates aditivos e restaurar o contrato local anterior nos arquivos do orçamento. Não usar reset, checkout destrutivo ou limpeza do worktree; mudanças preexistentes devem permanecer intactas. O rollback não será executado sem autorização específica.

## 11. Decisão solicitada ao HUMAN — G2

Solicita-se decisão explícita sobre:

1. contrato de metadados e vocabulário persistido da seção 2;
2. `KNOWN` explícito ou `APPROVED` sem conflitos como autoridade suficiente para chave/cardinalidade, mantendo relacionamento automático somente `APPROVED`;
3. parâmetro opcional `grain` na tool existente `gerar_sql` e gate da seção 3;
4. exposição aditiva pelas tools da seção 4, preservando exatamente 12;
5. orçamento fechado de 11 arquivos e parada em G3 para qualquer expansão;
6. sequência, verificação, teste real controlado, riscos e rollback;
7. autorização, se aprovado, para executar somente `IMPLEMENT → VERIFY → EVIDENCE` dentro deste plano e parar em G4.

## 12. Gate atual

**G2 — APPROVED em 2026-09-18 pelo HUMAN/Product Owner.** Os itens 1 a 7 da seção 11 foram aprovados. Está autorizada somente a execução de `IMPLEMENT → VERIFY → EVIDENCE` dentro do orçamento da seção 5, com parada obrigatória em G4, G3 ou bloqueio objetivo.

Nenhuma homologação HAP, commit, push, release, publicação, instalação global ou configuração externa foi autorizada.

Condição de parada: após implementação e evidência completas, entrar em `STOP_HUMAN — G4 PENDING` sem declarar a SPEC-010 aceita ou concluída.

## 13. Implementação realizada

A execução permaneceu nos 11 arquivos autorizados; `metadata/relationships.json` não precisou ser alterado e continua sem fatos HAP. Nenhum arquivo, dependência, integração ou estratégia fora do orçamento foi utilizado.

- modelos estritos adicionados para `Cardinality`, `KeyKind`, chaves simples/compostas, documento compatível e autoridade/proveniência independentes;
- documento legado com somente `relationships` preservado; `keys` é opcional;
- cardinalidade ausente permanece `UNKNOWN`; inversão por sentido do percurso é determinística;
- chaves e cardinalidades conflitantes ficam visíveis e bloqueiam preservação;
- `descrever_tabela`, relações, caminhos e `gerar_join` expõem os novos sinais pelas tools existentes;
- `gerar_sql` recebeu `grain` opcional e valida a tabela-base e cada aresta antes de construir SQL;
- `MANY_TO_ONE`/`ONE_TO_ONE` com chave correspondente e autoridade suficiente preservam o grão;
- demais cardinalidades, chave ausente/incompatível e conflitos bloqueiam sem SQL parcial ou deduplicação;
- ausência de `grain` e consultas single-table preservam o comportamento anterior;
- documentação atualizada com contrato e exemplo exclusivamente fictício.

Não foram implementados FK, nulabilidade, importador de DDL, profiler, planner, acesso Oracle ou nova tool.

## 14. Evidências de verificação

Ambiente: Windows, Python 3.12 e ambiente virtual local existente; baseline Git `862abae4237997bc7165b27a4fc179429ff11359` em `main`, com mudanças locais preexistentes preservadas.

| Verificação | Método | Esperado | Observado |
|---|---|---|---|
| Suíte específica | `python -m pytest tests/test_relationships.py tests/test_sql_generator.py tests/test_server.py -q -p no:cacheprovider` | Casos do PLAN-010 passam | `45 passed in 7.93s` |
| Suíte completa | `python -m pytest -q -p no:cacheprovider` | Sem regressões | `73 passed in 7.00s` |
| Smoke MCP | `python scripts/smoke_test.py` | Servidor inicia e mantém tools | servidor `data-engineering-mcp` v0.1.0; `tools=12`; chamadas básicas sem erro |
| Compilação | `python -m compileall -q src` | Módulos compilam | exit code 0, sem saída de erro |
| Higiene do diff | `git diff --check` | Sem erro de whitespace | exit code 0; somente avisos informativos preexistentes de LF/CRLF |
| Metadado real | leitura de `metadata/relationships.json` | Nenhum fato HAP inserido | permanece `{"relationships": []}` |
| Orçamento | inspeção de status/diff e contagem das tools | somente arquivos autorizados; 12 tools | implementação restrita aos arquivos orçados; `TOOL_DECORATORS=12` |

A primeira tentativa de pytest dentro da sandbox não executou testes porque o ambiente negou o diretório temporário (`PermissionError`). A recuperação segura autorizada repetiu os mesmos comandos fora dessa restrição, sem rede; as execuções acima passaram integralmente.

## 15. Teste real controlado

As duas variantes obrigatórias foram automatizadas:

1. **Metadado real vazio:** pessoa–usuário–plano com `grain=["CD_USUARIO"]` continua bloqueado na autoridade `INFERRED`, sem `SELECT`, `ROW_NUMBER` ou deduplicação. Resultado: fail-closed preservado; nenhum fato foi inventado.
2. **Fixture isolada:** relacionamentos fictícios `USUARIO → PESSOA MANY_TO_ONE` e `USUARIO → PLANO MANY_TO_ONE`, `APPROVED` para uso do relacionamento, cardinalidade `KNOWN` e PKs `KNOWN` correspondentes permitem duas arestas e geram exatamente dois JOINs, preservando o grão declarado.

A fixture existe somente durante o teste e não foi persistida no metadado real. Ela não homologa pessoa, usuário, plano ou suas chaves.

## 16. Avaliação técnica dos critérios

| Critério | Resultado técnico | Evidência |
|---|---|---|
| AC-001 | PASS | Chaves simples/compostas, `KNOWN`/`APPROVED`, fontes, decisões e conflitos cobertos |
| AC-002 | PASS | Cinco cardinalidades, orientação e autoridade próprias modeladas e testadas |
| AC-003 | PASS | Autoridades permanecem independentes nos modelos e payloads |
| AC-004 | PASS | Somente metadado explícito é aceito; ausência fica `UNKNOWN`; casos inválidos falham |
| AC-005 | PASS | Casos `MANY_TO_ONE` e caminho controlado preservador cobertos |
| AC-006 | PASS | `ONE_TO_MANY`, `MANY_TO_MANY`, `UNKNOWN`, ausência e conflitos bloqueiam sem SQL parcial |
| AC-007 | PASS | Caso real bloqueado e fixture isolada autorizada demonstrados separadamente |
| AC-008 | PASS | Tabela/coluna, chave, duplicidade, autoridade/decisão e campos extras inválidos cobertos |
| AC-009 | PASS | 73 testes totais e smoke com os mesmos 12 nomes |
| AC-010 | PASS | Suítes, smoke, compilação, diff e teste real controlado registrados |

`PASS` nesta tabela é avaliação técnica, não aceite HUMAN e não altera o status da SPEC-010 para `ACCEPTED`.

## 17. Limitações e riscos residuais

- `KNOWN` continua sendo uma declaração cuja exatidão depende da fonte fornecida; o MCP não consulta nem valida fisicamente o Oracle.
- O gate mínimo exige que o grão pertença à primeira tabela solicitada e segue a ordem determinística atual; não há propagação ou escolha sofisticada de caminhos.
- Relacionamentos atuais possuem um par de colunas; chaves compostas são representadas e consultáveis, mas só correspondem automaticamente quando o relacionamento futuro fornecer o mesmo conjunto completo. Nenhuma ampliação foi feita nesta spec.
- Preservação significa no máximo uma correspondência no lado alcançado; não prova correspondência obrigatória, nulabilidade ou equivalência entre tipos de JOIN.
- A exibição CP1252 dos logs do smoke continua sendo limitação cosmética preexistente.

Esses limites coincidem com o não-escopo aprovado e não foram aceitos pelo HUMAN neste gate.

## 18. Gate de saída

**G4 — APPROVED em 2026-09-18 pelo HUMAN/Product Owner.** Implementação, verificação, evidência e riscos residuais foram aceitos. O PLAN-010 está `COMPLETED` e a SPEC-010 está `ACCEPTED / DONE`.

O aceite não homologa nenhum fato HAP. Foi autorizada somente uma prova E2E temporária complementar na fronteira MCP, com fixtures sintéticas genéricas e VERIFY/EVIDENCE. Nenhum commit, push, release ou publicação está autorizado.

## 19. Prova E2E complementar — STOP_BLOCKED ambiental

Em 2026-09-18, a prova complementar autorizada foi iniciada sem mudança de produto. Antes da execução, a inspeção textual da lógica relevante em `src/` não encontrou ocorrências de `USUARIO`, `PESSOA`, `PLANO`, `RAW_HAP_*` nem dependência da quantidade atual de tabelas; catálogo, endpoints, chaves e cardinalidades são processados por metadados.

A primeira tentativa criou um diretório temporário pelo mecanismo padrão do Python, fora do repositório, mas o ambiente negou a gravação do primeiro XLSX com `PermissionError`. A única recuperação segura repetiu a prova em raiz gravável isolada fora do repositório e recebeu o mesmo `PermissionError` no primeiro XLSX. Nenhuma chamada à fronteira MCP ocorreu e, portanto, não há resultado funcional `BLOCKED → ALLOWED` a registrar.

Estado observado após as tentativas:

- `metadata/relationships.json` real permaneceu com SHA-256 `E020F99FF944B9ACA3DFC8B45D714ECB1CF9116F959BEFDCDFA03EFC82478B17`;
- nenhum fato HAP foi incluído ou homologado;
- `git diff --check` terminou sem erro, apenas com avisos informativos LF/CRLF preexistentes;
- a segunda tentativa deixou o diretório temporário inacessível `<temporary-workspace>\spec010-e2e-uztxiv_g`, pois o mesmo bloqueio de permissão também impediu a limpeza automática;
- o estado Git observado após a tentativa é igual ao baseline de trabalho quanto aos arquivos de produto/teste; somente a reconciliação documental autorizada desta retomada foi adicionada aos documentos não rastreados em `specs/`.

**STOP_BLOCKED.** Motivo: problema ambiental impede criar e remover a fixture temporária e, consequentemente, coletar os payloads/resultados obrigatórios na fronteira MCP. Último estágio seguro: reconciliação documental concluída e inspeção de genericidade concluída; E2E não executado. Menor retomada objetiva: disponibilizar execução com permissão de escrita/remoção em um diretório temporário isolado, então repetir uma única vez a prova já definida, sem mudar código.

## 20. Retomada da prova E2E complementar — PASS

Em 2026-09-18, após autorização HUMAN explícita para retomar exclusivamente a prova bloqueada, a execução foi repetida localmente fora da restrição da sandbox, sem rede e em subdiretório único de `.test-tmp`. Não houve mudança de produto, testes, catálogo HAP ou metadado real.

Payload usado nas duas chamadas da mesma tool MCP `gerar_sql`:

```json
{
  "tabelas": ["USUARIO", "PESSOA", "PLANO"],
  "colunas": ["USUARIO.ID_USUARIO", "PESSOA.NM_PESSOA", "PLANO.NM_PLANO"],
  "grain": ["ID_USUARIO"]
}
```

Resultados observados na fronteira MCP:

1. com documento temporário `{"relationships": []}`, a chamada retornou erro legível por relacionamento `INFERRED`, estado `BLOCKED` e nenhuma ocorrência de `SELECT`;
2. com metadados exclusivamente sintéticos `synthetic:e2e-fixture`, as PKs `USUARIO.ID_USUARIO`, `PESSOA.ID_PESSOA` e `PLANO.ID_PLANO` foram expostas por `descrever_tabela` como `PRIMARY_KEY / KNOWN`, sem conflitos;
3. `inferir_relacionamentos` expôs `USUARIO.ID_PESSOA → PESSOA.ID_PESSOA` e `USUARIO.ID_PLANO → PLANO.ID_PLANO` como `APPROVED`, `MANY_TO_ONE`, cardinalidade `KNOWN` e sem conflitos;
4. a segunda chamada à mesma `gerar_sql` retornou sem erro, estado operacional `ALLOWED` e SQL com exatamente dois `LEFT JOIN`, preservando o grão solicitado;
5. `list_tools` retornou exatamente 12 tools: `listar_tabelas`, `descrever_tabela`, `buscar_coluna`, `buscar_tabelas`, `inferir_relacionamentos`, `encontrar_caminho`, `atualizar_catalogo`, `status_catalogo`, `gerar_sql`, `gerar_select`, `gerar_join` e `explicar_sql`.

SQL observado:

```sql
SELECT
    u.ID_USUARIO,
    p.NM_PESSOA,
    p2.NM_PLANO
FROM USUARIO u
LEFT JOIN PESSOA p
    ON p.ID_PESSOA = u.ID_PESSOA
LEFT JOIN PLANO p2
    ON p2.ID_PLANO = u.ID_PLANO
```

Integridade e limpeza:

- SHA-256 real antes e depois: `E020F99FF944B9ACA3DFC8B45D714ECB1CF9116F959BEFDCDFA03EFC82478B17` — idêntico;
- `git status --short` antes e depois — idêntico;
- diretório temporário `<repo-root>\.test-tmp\spec010-e2e-fdbc5y62` existiu durante a prova e não existia após a limpeza automática;
- nenhum fato HAP foi incluído, promovido ou homologado.

**Resultado: PASS.** O `STOP_BLOCKED` ambiental da seção 19 está resolvido. A evidência complementar confirma na fronteira MCP o ciclo `sem autoridade → BLOCKED / nenhum SQL` e `autoridade sintética controlada → ALLOWED / exatamente dois JOINs`, mantendo a capacidade genérica e data-driven já inspecionada. Nenhuma atividade adicional permanece autorizada ou necessária para a SPEC-010.
