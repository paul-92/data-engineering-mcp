---
name: data-engineering-spec-driven
description: Convert requests for a new BI solution, review or improvement of an existing BI solution, or SQL-only work into proportional executable specs after source and artifact inspection. Use for BI or SQL work that needs Data Engineering MCP expertise, relevant Power BI capabilities, and optional Figma support; do not use to execute the generated specs or replace those specialist capabilities.
---

# Data Engineering Spec Driven

Turn a BI or SQL request into the smallest sufficient set of executable specs. Inspect before specifying, preserve known information, and leave implementation to the applicable orchestrator.

## Authority and boundaries

- HUMAN owns product decisions, approvals, material interpretations, and acceptance.
- This skill performs intake, discovery, inspection, specialist coordination, and spec generation only.
- Do not implement generated specs, operate construction gates, maintain orchestration state, or act as a second ASEP or orchestrator.
- Do not reproduce catalog, relationship authority, query intent, safety, SQL, Power BI, or Figma capabilities. Invoke the appropriate specialist and preserve its findings and limitations.
- Treat existing authorization narrowly. Do not infer permission for external, destructive, persistent, publishing, deployment, or release actions.

## Intake

Identify one mode from the request:

1. **New BI:** create a new report, dashboard, semantic model, or BI solution.
2. **Improve or review existing BI:** inspect and evaluate an existing BI artifact before proposing changes.
3. **SQL only:** specify SQL generation, correction, explanation, or review without inventing a BI deliverable.

Capture the requested outcome, audience or consumer when relevant, artifacts, sources, constraints, delivery expectations, and authority already granted. Infer the mode when the request makes it clear; ask a focused question only when ambiguity changes the required work.

Maintain a working record of facts already supplied by the HUMAN, present in artifacts, or reliably discovered. Never ask for those facts again. Reconfirm only when sources conflict, a value is stale or unreliable, or the choice materially changes the outcome.

## Inspect before specifying

Do not plan or write specs until the necessary source and artifact inspection is complete. Keep inspection proportional: gather only what is needed to define executable, verifiable work.

### Source discovery

- For XLSX, CSV, or TXT, use the supplied path. If access requires a path and none was supplied or discovered, ask only for that path.
- For a database source, inspect the representations and tables available in the Data Engineering MCP repository's `data/` directory. Never connect directly to the database.
- If local representations are missing, insufficient, contradictory, or apparently stale, state the limitation. Enter `STOP_HUMAN` only when resolving it requires a material choice or new authority.
- For an existing BI artifact, inspect its current structure and relevant state before proposing a redesign, correction, or extension.

### Specialist coordination

Use the Data Engineering MCP as the technical specialist for:

- catalog and source structure;
- relationship candidates, authority, paths, and conflicts;
- structured query intent, including sources, outputs, filters, relationships, grain, warnings, and authority pending;
- safety constraints and blocking conditions;
- SQL generation, selection, joins, review, and explanation.

Preserve specialist results without promoting relationships, resolving conflicts, bypassing safety, or silently rewriting intent.

### Fail closed for multi-table SQL

- Treat any `INFERRED`, `KNOWN`, absent, or conflicting relationship authority as `automatic JOIN = BLOCKED`, even when `conflicts` is empty.
- If `gerar_sql` fails or blocks a multi-table intent, do not generate, reconstruct, complete, present as executable, or offer equivalent SQL from `gerar_join`, `encontrar_caminho`, catalog metadata, another tool, or your own reasoning.
- A blocked auxiliary relationship result is descriptive evidence only. Do not turn its endpoints into a JOIN clause, and do not present `sql_sugerido` or an equivalent fragment.
- Report the blocked relationships and their authority, state that no multi-table SQL can be produced, and enter `STOP_HUMAN` to request the smallest HUMAN relationship decision or homologation needed.
- Never interpret `conflicts=[]` or the absence of a separate `blocked_reason` as permission. Automatic use requires `APPROVED` authority and no conflicts.

For Power BI work, discover and use every available Power BI MCP capability or skill relevant to the request and mode. In review or improvement mode, prefer inspecting the existing report, model, visuals, filters, theme, and dependencies before proposing changes. Do not copy Power BI behavior into this skill.

Use Figma only when the request involves visual creation or reformulation and Figma capability is available. Its absence is not a blocker when the work can be specified adequately from Power BI and the available context. Do not require Figma for SQL-only or non-visual work.

## Resolve uncertainty

Continue automatically through clear, reversible inspection decisions covered by current authority. Ask the HUMAN only for the smallest decision needed when any of these would materially change the specs:

- competing interpretations of business meaning, source, join, grain, metric, audience, or expected result;
- approval, promotion, or resolution of an absent, inferred, known, or conflicting relationship;
- acceptance of insufficient evidence, an incomplete source representation, or a material residual risk;
- expansion of scope, public contract, dependency, architecture, or delivery target;
- destructive, irreversible, persistent, external, or otherwise unauthorized action.

When one of these decisions is required, return `STOP_HUMAN` with the observed evidence, last safe stage, smallest decision needed, and objective resume condition. Do not continue by assuming the answer.

Use `STOP_BLOCKED` when the available artifacts contradict each other, a required dependency is unavailable, or no safe specification can be produced without inventing authority. State the evidence, last safe stage, smallest needed decision, and objective resume condition.

## Generate a proportional spec set

After inspection, generate one to N executable specs.

Use one compact spec when the work is cohesive, low-risk, and verifiable as a single deliverable. Split into multiple specs only when justified by independently verifiable deliverables, component dependencies, distinct material risks or decisions, rollback boundaries, or a required execution order. Do not split for documentation convenience.

Each spec must include:

- objective and user-visible outcome;
- scope and explicit non-scope;
- inspected inputs, artifacts, and known constraints;
- specialist capabilities to use, without duplicating their logic;
- dependencies and execution order, if any;
- executable work and permitted change boundary;
- verifiable acceptance criteria and proportional evidence;
- material assumptions, limitations, risks, and rollback where relevant;
- HUMAN decisions and stop conditions that cannot be automated.

For multiple specs, make dependencies explicit and avoid overlapping ownership. Ensure the set covers the approved objective without optional improvements or speculative work.

## Handoff

Return a concise inspection summary, the ordered spec set, the reason for the chosen number of specs, known risks or limitations, and any genuine HUMAN decision still required.

Write specs so the applicable orchestrator can later execute authorized technical steps automatically and stop only at genuine HUMAN gates or objective blockers. Generating the specs does not approve them, authorize implementation, or permit this skill to execute them.
