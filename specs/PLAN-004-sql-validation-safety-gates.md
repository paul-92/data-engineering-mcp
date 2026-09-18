# PLAN-004 — SQL Validation & Safety Gates

| Campo | Valor |
|---|---|
| Spec | `SPEC-004` |
| Baseline | `862abae4237997bc7165b27a4fc179429ff11359`, com SPEC-002 e SPEC-003 aceitas |
| Gate de entrada | G1 aprovado em 2026-09-11 pelo HUMAN/Product Owner |
| Status | `COMPLETED` |
| Implementação autorizada | Sim — G2 aprovado em 2026-09-16; execução concluída e aceita no G4 |

## 1. Objetivo e solução mínima

Inserir no fluxo atual do `SQLGenerator` um único gate para consultas multi-tabela, reutilizando diretamente `RelationshipAuthority` e `conflicts` da SPEC-002. Antes de emitir qualquer `JOIN`, o gerador aceitará somente relacionamento `APPROVED` sem conflitos. `INFERRED`, `KNOWN`, autoridade ausente ou conflito bloquearão a geração.

O gate não descobrirá, promoverá, corrigirá nem replanejará relacionamentos. Ao bloquear, retornará erro claro com os endpoints do relacionamento e o motivo da homologação necessária, sem escolher silenciosamente outro candidato ou caminho. Consultas de uma tabela não passarão pelo gate e manterão o comportamento atual.

## 2. Arquivos mínimos previstos

- Alterar `src/data_engineering_mcp/sql_generator.py`: aplicar o gate na seleção de relacionamentos já existente, antes da emissão do SQL.
- Alterar `tests/test_sql_generator.py`: cobrir permissão, bloqueios, mensagem e regressão de tabela única.
- Alterar `README.md`: documentar sucintamente a política de autoridade para SQL multi-tabela.

Não alterar modelos, engine de relacionamentos, exceções, servidor, contratos das tools, metadata ou datasets. A exceção de relacionamento já existente será reutilizada. Qualquer necessidade de arquivo adicional interrompe a execução e retorna ao HUMAN/Product Owner.

## 3. Comportamento previsto

1. Consulta com uma tabela continua gerando SQL como hoje, sem exigir relacionamento.
2. Consulta multi-tabela só usa candidato `APPROVED` com `conflicts` vazio.
3. Candidato `INFERRED` ou `KNOWN`, autoridade ausente ou qualquer conflito causa falha antes da emissão do SQL.
4. A falha identifica `TABELA.COLUNA ↔ TABELA.COLUNA`, informa a autoridade/conflito que bloqueou e indica que a relação precisa de homologação válida como `APPROVED` e livre de conflitos.
5. O parâmetro atual de baixa confiança não contorna autoridade nem conflitos; confiança continua sendo um controle adicional, não substituto da homologação.
6. Se o candidato aplicável estiver bloqueado, o gerador não escolhe silenciosamente outro caminho. Ausência de candidato continua usando o erro atual de relacionamento inexistente.
7. As 12 tools, nomes, argumentos e formatos permanecem; a mudança é aditiva na segurança e restrita à recusa de `JOIN` não autorizado.

## 4. Testes e verificações mínimas

- Tabela única permanece compatível e não exige relacionamento aprovado.
- Duas tabelas com relação `APPROVED` e sem conflitos geram o `JOIN` atual.
- `INFERRED` e `KNOWN` bloqueiam separadamente, mesmo com confiança alta ou média.
- Relação `APPROVED` com conflito bloqueia.
- `permitir_baixa_confianca`/`allow_low_confidence` não funciona como bypass de autoridade ou conflito.
- Erro de bloqueio contém os endpoints, o motivo e a necessidade de homologação, sem SQL parcial nem alternativa silenciosa.
- Casos existentes de catálogo, colunas, filtros parametrizados e ausência de relacionamento continuam passando.
- Suíte completa passa; smoke confirma exatamente 12 tools; `git diff --check` passa.
- Diff de implementação fica restrito aos três arquivos da seção 2 e não inclui runtime externo, tools, datasets, metadata, Power BI MCP, Codex global, Git remoto ou release.

## 5. Rollback

Reverter somente a alteração em `sql_generator.py`, os testes adicionados em `test_sql_generator.py` e a seção correspondente do `README.md`. Confirmar a suíte anterior e a enumeração das 12 tools. Não haverá migração, persistência, dependência ou conversão de dados.

## 6. Critérios de aceite

- **AC-P4-001:** nenhum `JOIN` é emitido usando relação `INFERRED`, `KNOWN`, sem autoridade ou conflitante.
- **AC-P4-002:** somente `APPROVED` sem conflitos sustenta `JOIN` automático, mantendo os controles atuais de confiança como restrição adicional.
- **AC-P4-003:** bloqueio ocorre antes da emissão do SQL e identifica claramente a relação e a homologação necessária.
- **AC-P4-004:** o gerador não seleciona caminho alternativo silencioso para contornar uma relação aplicável bloqueada.
- **AC-P4-005:** consultas de tabela única e proteções existentes permanecem compatíveis.
- **AC-P4-006:** a solução reutiliza SPEC-002 e o fluxo atual, sem novo sistema de validação, parser, framework, serviço, dependência, banco, planner ou tool.
- **AC-P4-007:** exatamente 12 tools e seus contratos públicos são preservados; nenhuma alteração incompatível é introduzida.
- **AC-P4-008:** testes, smoke e verificação de diff passam, e o rollback limita-se aos três arquivos previstos.

## 7. Impactos positivos e riscos/ônus

**Impactos positivos:** alinha a geração SQL à autoridade já modelada; impede JOIN semanticamente não homologado; mantém o controle central, determinístico e pequeno; fornece diagnóstico acionável para homologação sem ampliar a superfície pública.

| Risco/ônus | Mitigação |
|---|---|
| Consultas multi-tabela atuais com relações inferidas ou conhecidas passam a falhar | Ônus aceito pelo G1; mensagem indica exatamente a relação a homologar |
| Metadados ainda não possuírem relações aprovadas suficientes | Homologação manual no mecanismo existente da SPEC-002, fora desta implementação |
| Confiança ser confundida com autoridade | Gate de autoridade é obrigatório; `allow_low_confidence` não o contorna |
| Seleção alternativa mascarar a relação bloqueada | Falhar no candidato aplicável, sem busca silenciosa de desvio |
| Crescimento para novo validador ou planner | Mudança limitada ao ponto atual de seleção no `SQLGenerator`; qualquer expansão volta ao G2 |

## 8. Decisões HUMAN/Product Owner para G2

1. Autorizar somente os três arquivos da seção 2 e o gate único no `SQLGenerator`.
2. Confirmar a matriz: `INFERRED` bloqueia, `KNOWN` bloqueia, somente `APPROVED` sem conflitos permite JOIN e qualquer conflito bloqueia.
3. Aprovar falha imediata e explicativa, com endpoints e necessidade de homologação, sem caminho alternativo silencioso.
4. Confirmar que `allow_low_confidence` não é bypass de autoridade e que os controles de confiança atuais permanecem adicionais.
5. Aprovar testes mínimos, critérios de aceite, impactos, riscos/ônus e rollback deste plano.
6. Confirmar preservação de consultas de uma tabela, exatamente 12 tools e compatibilidade aditiva.
7. Confirmar que arquivo adicional, mudança incompatível ou novo sistema, parser, framework, serviço, dependência, banco, planner ou tool exige interrupção e nova decisão.
8. Confirmar que runtime externo, tools, datasets, metadata, Power BI MCP, Codex global, Git remoto e release permanecem intocados.

## 9. Gate atual

**G2 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** Autorizada somente a execução de IMPLEMENT → VERIFY → EVIDENCE dentro deste plano, sem ampliação de escopo e com parada obrigatória no G4.

## 10. Evidências de implementação e verificação

- implementação: gate único no `SQLGenerator`, reutilizando `RelationshipAuthority`, `RelationshipCandidate.conflicts` e `RelationshipNotFoundError` da infraestrutura existente;
- política validada: autoridade ausente, `INFERRED` e `KNOWN` bloqueiam; somente `APPROVED` sem conflitos pode avançar; conflito bloqueia mesmo com `allow_low_confidence=True`;
- seleção validada: o candidato aplicável de maior score é submetido ao gate antes do controle adicional de confiança; se bloqueado, não há escolha silenciosa de candidato alternativo;
- diagnóstico validado: o erro informa os dois endpoints, a autoridade ou os conflitos e a necessidade de homologação como `APPROVED` livre de conflitos;
- compatibilidade validada: consulta de uma tabela não exige relacionamento; filtros parametrizados, catálogo, colunas, ambiguidade e ausência de relacionamento mantêm os testes existentes;
- testes específicos: `11 passed` em `tests/test_sql_generator.py`;
- suíte completa: `48 passed`;
- smoke MCP: PASS com servidor `data-engineering-mcp` v0.1.0, exatamente 12 tools, nomes originais preservados, `listar_tabelas_error=False` e `status_catalogo_error=False`;
- `git diff --check`: PASS (exit code 0; somente avisos informativos de normalização LF/CRLF);
- auditoria de escopo: implementação limitada a `sql_generator.py`, `test_sql_generator.py` e à seção correspondente do `README.md`; somente estes documentos de status/evidência foram atualizados adicionalmente; sem mudança em datasets, metadata, tools, dependências, Power BI MCP, Codex global, Git remoto ou release; sem commit ou push.

## 11. Riscos residuais e encerramento

- relações ainda não homologadas interrompem intencionalmente consultas multi-tabela até decisão humana registrada;
- o gate não valida PK/FK física, cardinalidade, fan-out ou custo, todos fora do escopo aprovado;
- entre candidatos para o mesmo passo, o maior score continua definindo o candidato aplicável; se ele estiver bloqueado, a geração falha em vez de procurar desvio silencioso;
- `allow_low_confidence` continua permitindo baixa confiança apenas depois da homologação, nunca como bypass de autoridade ou conflito.

**G4 — APPROVED em 2026-09-16 pelo HUMAN/Product Owner.** Evidências, impactos e riscos residuais aceitos. O PLAN-004 está `COMPLETED` e a SPEC-004 foi encerrada como `ACCEPTED/DONE`.

Este encerramento não autoriza commit, push, release nem implementação da SPEC-005.
