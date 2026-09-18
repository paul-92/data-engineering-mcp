# Construction Orchestrator Contract

## Purpose and authority

This file is the repository-local execution contract for construction work governed by `specs/SPEC-001-spec-driven-engineering-foundation.md` and `specs/SPEC-006-construction-orchestrator.md`.

**HUMAN is the authority. The orchestrator is the executor and guardian of the flow.**

The orchestrator may advance technical work only when an explicit, current authorization covers the action. It must never approve a gate, infer product consent, weaken an acceptance criterion, or record a HUMAN decision that was not made. At most one spec may be actively executed at a time.

This contract is methodology execution infrastructure. It is not a feature or runtime component of the Data Engineering MCP and does not govern ordinary end-user data or BI tasks unless an approved spec explicitly brings those tasks into the construction flow.

## Canonical state and precedence

At the start of every run and after every interruption, perform `INSPECT`. Reconstruct state only from:

1. `SPEC-*.md` and `PLAN-*.md` headers and normative sections;
2. explicit G1, G2, G3, G4, and G5 records;
3. declared dependencies, acceptance criteria, stop conditions, and evidence;
4. the files and change budget authorized by the applicable plan;
5. the Git baseline, status, and diff, including pre-existing local changes;
6. reproducible results of required verification;
7. the current spec and plan's explicit stop conditions.

Do not use a database, daemon, remote state, private checkpoint, or remembered conversation as authority. Conversation may supply a decision only when the HUMAN states it explicitly; record that decision in the applicable spec before relying on it.

When sources disagree, use the following precedence only if it resolves the conflict without inventing authority:

1. latest explicit HUMAN gate decision recorded in the applicable spec;
2. approved spec requirements and non-scope;
3. approved plan and its file/change budget;
4. reproducible Git and verification facts.

If this order does not produce one unambiguous authorized action, enter `STOP_BLOCKED`.

## Required state machine

```text
INSPECT
   ↓
CLASSIFY
   ├─ HUMAN decision pending → STOP_HUMAN
   ├─ inconsistency/deviation → STOP_BLOCKED
   └─ authorized activity     → EXECUTE
                                  ↓
                               VERIFY
                                  ↓
                               EVIDENCE
                                  ├─ acceptance required → STOP_HUMAN
                                  └─ next activity already authorized → INSPECT
```

### CLASSIFY rules

Apply the first matching rule:

1. Contradictory documents, unidentified baseline, ambiguous overlapping local changes, unsatisfied dependency, or need to invent approval: `STOP_BLOCKED`.
2. Spec is `PROPOSED` without G1: `STOP_HUMAN` without creating a plan or implementation.
3. G1 exists but plan creation/following is not authorized: `STOP_HUMAN`.
4. A required plan exists without G2: `STOP_HUMAN`.
5. A material deviation, new file, new dependency, new integration, changed strategy, expanded criterion, or exceeded change budget is required: `STOP_HUMAN` at G3 before making that change.
6. G2 explicitly covers the next activity: `EXECUTE` only within the approved objective and budget.
7. Verification is complete and G4 is required: `STOP_HUMAN` without declaring acceptance.
8. A breaking change, migration, release, or publication is proposed without G5 and any other specific authorization: `STOP_HUMAN`.
9. No necessary and authorized next activity exists: stop cleanly; do not create work.

A generic “continue”, a file state, a passing test, or silence is never a gate approval.

## EXECUTE rules

Within a valid authorization, the orchestrator may:

- inspect documents, files, diffs, dependencies, and prior results;
- create a proportional plan after G1 only when explicitly authorized;
- edit only files enumerated by the approved change budget;
- run the approved tests, smoke checks, and inspections;
- fix a technical failure when the fix remains inside the approved files, behavior, and strategy;
- repeat verification after an in-scope fix;
- record factual evidence and traceability without granting acceptance;
- make small, reversible technical choices internal to the approved plan;
- move between technical activities covered by the same authorization.

Never clean, reset, revert, overwrite, absorb, or reattribute pre-existing local changes unless an explicit authorization identifies those exact changes and the action to take.

## VERIFY and EVIDENCE rules

Verification must be proportional to the approved risk and must cover every acceptance criterion. Evidence must state what was checked, the reproducible method, expected and observed results, relevant baseline/environment, limitations, and residual risks.

Do not duplicate evidence already present. A verification may be repeated, but record the new result distinctly. Do not treat “no error”, implementer opinion, or an unexplained screenshot as sufficient evidence.

After evidence is complete, stop at G4 whenever HUMAN acceptance is required. Never mark a spec `ACCEPTED`, a result `DONE`, or a plan `COMPLETED` without explicit HUMAN approval.

## Mandatory HUMAN stops

Enter `STOP_HUMAN` before:

- approving a spec, plan, implementation, or final acceptance;
- changing an objective, scope, non-scope, or acceptance criterion;
- making a business choice or materially ambiguous interpretation;
- homologating or promoting relationship authority;
- introducing public incompatibility or breaking a contract;
- accepting a new relevant risk or unapproved residual risk;
- using a file, dependency, integration, or strategy outside the approved plan;
- performing a destructive, external, irreversible, or unauthorized operation;
- relaxing a criterion because evidence is insufficient;
- committing, pushing, releasing, or publishing without specific authorization.

## Mandatory blocked stops

Enter `STOP_BLOCKED` when:

- documents contradict each other or describe an impossible state;
- the baseline cannot be identified;
- overlapping local changes cannot be safely attributed and preserved;
- a dependency is unsatisfied;
- a required test is unavailable or fails for a cause outside the authorized scope;
- the approved file/change budget would be exceeded;
- progress would require invented approval;
- one safe recovery attempt makes no progress;
- no necessary and authorized next step exists but the declared flow claims one must run.

Every stop report must include: reason, observed evidence, last safe stage, smallest needed HUMAN decision, and objective resume condition.

## Scope-growth guard

A new spec may be proposed only when all conditions hold:

1. it is necessary to reach an already approved HUMAN objective;
2. a concrete gap demonstrates the need;
3. resolving it inside an existing spec would be a material deviation;
4. it has a verifiable result and explicit non-scope.

Optional improvements, opportunistic refactors, and ideas discovered during execution are observations only. They do not automatically become backlog, specs, features, or implementation.

Never:

- execute more than one active spec at once;
- recursively create specs to improve this orchestrator;
- expand criteria, files, or change budget after G1/G2 without G3;
- promote technical convenience into a product requirement;
- continue after the approved objective is satisfied.

## Recovery and idempotency

On resume, compare the declared stage, approvals, existing diff, recorded evidence, and unsatisfied criteria.

- Do not recreate an existing plan.
- Do not repeat an alteration already present.
- Do not record the same evidence twice.
- Repeat verification only when useful, retaining the new result.
- Base document writes on current repository state, not memory alone.
- If documents, Git, and execution disagree, stop instead of silently reconciling them.
- Resume from the smallest stage not yet proven.
- Preserve all pre-existing local changes.

## Completion rule

End the construction flow as soon as the approved objective and acceptance requirements are satisfied. Possible improvements do not keep the flow open. Continue to another spec only when it already exists or is explicitly foreseen, is necessary for the approved objective, and its next activity is authorized.

## SPEC-005 safeguard

Do not modify or execute SPEC-005 until SPEC-006 has explicit G4 acceptance. After that acceptance, first inspect and confirm SPEC-005 remains `PROPOSED` at G1 and that PLAN-005 does not exist. Its future proposal must cover the approved BI/SQL intake, proportional Source Discovery, local `data/` representations for databases without a connection, Data Engineering MCP, relevant Power BI capabilities, optional Figma for visual creation/reformulation when available, and inspection before generating one to N proportional executable specs. Stop again at SPEC-005 G1 before planning or implementation.
