# Epic Document Template

```markdown
# Epic: [EPIC NAME]

**Epic ID**: `[NN-epic-short-name]`
**Created**: [TODAY'S DATE]
**Status**: Draft
**Input**: User description: "$ARGUMENTS"

## Objective & Business Context

[Why this epic exists, the business problem/opportunity, and what success at the epic level looks like — broader and longer-horizon than any single feature's objective]

## Scope & Non-Goals

**In Scope**: [what this epic covers]
**Non-Goals**: [what it explicitly does not attempt, including anything deferred to a later epic]

## Constitution Check

*Gate: must pass before the feature backlog below is considered final.*

| Principle (.spec/constitution.md) | Assessment | Note |
|---|---|---|
| [Principle name] | Pass / Violation | [justification if Violation] |

If any `Violation` lacks an acceptable justification, resolve it before finalizing the backlog — don't let a downstream feature quietly inherit a governance conflict.

## Feature Backlog

*Organized by CRISP-ML(Q) phase. Omit any phase with no epic-level feature; state why in Assumptions.*

### Business & Data Understanding

**Requirements & Constraints**: [...]

| ID | Feature Name | Type | Goal | Priority | Depends On | Status |
|---|---|---|---|---|---|---|
| BDU1 | [...] | Feature | [...] | P1 | — | Not Started |

**Risks & QA**

| Risk | Feasible As-Is? | QA Method / Mitigation | Resulting Backlog ID |
|---|---|---|---|
| [...] | No | [...] | BDU2 |

### Data Preparation

[same structure as above]

### Modeling

[same structure as above]

### Evaluation

[same structure as above]

### Deployment

[same structure as above]

### Monitoring & Maintenance

[same structure as above]

## Shared Entities

[Entities used by more than one feature above, across any phase — see `shared-data-model.md`. If no entity is genuinely shared, state that explicitly and omit the file.]

- **[Entity]**: used by [DP1, MOD1, ...]

## Sequencing / Minimum Viable Epic

[Which feature, or minimal subset of P1 features, constitutes a working end-to-end walking skeleton of the epic — the first slice worth shipping before adding the rest of the backlog. Include a QA row here only if its risk severity would block a minimum viable version (e.g. a compliance gate); lower-severity QA can land after the walking skeleton ships.]

## Assumptions

- [Assumption about data, infra, scope boundaries, or an omitted phase, made while drafting this backlog]

## Phase Reports

[Links to reports/<phase-name>-report.md, appended by the Phase Report flow as each phase completes. Empty until the first phase finishes.]
```

## ID and Status Rules

- **ID**: `[PHASE][N]` using the phase code — `BDU`, `DP`, `MOD`, `EVAL`, `DEPLOY`, `MON` — numbered sequentially within that phase (`DP1`, `DP2`, ...). This ID is also, lowercased and zero-padded, the name given to the feature's own directory nested under this epic (e.g. `DP1` → `dp01-short-name`).
- **Type**: `Feature` (delivers epic capability) or `QA` (mitigates a risk).
- **Status**: always starts `Not Started`. Flips to `Specified` once that row's `spec.md` exists (with a link added). Flips to `Implemented` once every task in that feature's own `tasks.md` is complete and its Evaluation Gate (if any) has passed — done by `sdd-implement`, not here. Never set anything other than these three values.
