---
name: sdd-epic
description: Declares a multi-feature epic (e.g. "recommendation system", "RAG system", "fraud detection") and drafts a CRISP-ML(Q)-phase-organized, dependency-ordered feature backlog needed to realize it — plus a shared cross-feature data model — at .spec/NN-epic-name/. Re-invoking it against an existing epic generates phase-completion reports. Optional step between sdd-constitution and sdd-specify.
user_invocable: true
---

# Epic Backlog Generator

This skill guides Claude to act as a Staff ML Engineer / Product Lead scoping a multi-feature effort before any single feature gets specified. The goal is to turn a raw epic idea ("build a recommendation system") into a dependency-ordered **feature backlog**, organized by CRISP-ML(Q) phase — the list of features needed to realize it — plus, when the epic has entities multiple features will share, a shared cross-feature data model. It does **not** write user stories or acceptance criteria itself; that's `sdd-specify`'s job, one feature at a time.

Two distinct, non-conflicting uses of CRISP-ML(Q) phase vocabulary exist in this pipeline: the phase bucket a feature is filed under **here** classifies what epic-level capability it delivers (e.g. a feature filed under Evaluation might be "build the epic-wide model comparison harness"). It is unrelated to that same feature's own internal Data Preparation/Modeling/Evaluation/Deployment/Monitoring Setup sub-phases inside its own `tasks.md` (via `sdd-tasks`), which every feature has regardless of which epic-phase bucket it's filed under here.

**Position in the SDD pipeline**: Constitution → **Epic** (optional) → Specify → Clarify (optional) → Plan → Checklist (optional) → Tasks → Analyze (optional) → Implement → Monitor (optional). Expected input: `.spec/constitution.md` (if it exists) and a natural-language epic description, OR a reference to an existing epic (to generate its phase reports). Output: `.spec/NN-epic-name/epic.md`, plus `.spec/NN-epic-name/shared-data-model.md` when warranted, plus `.spec/NN-epic-name/reports/<phase-name>-report.md` once a phase's backlog is fully implemented.

**Hierarchy this skill sits at the top of**: Epic → Feature (`sdd-specify`) → User Stories → Acceptance Scenarios, alongside each feature's own Success Criteria. Skip this skill entirely for a one-off feature with no larger epic behind it — go straight to `sdd-specify`.

---

## Step 1: Load Context & Determine Flow

1. Check for an existing `.spec/` directory (create it if none exists yet). List its existing epic directories (`NN-*`, i.e. directories containing an `epic.md`).
2. Read `.spec/constitution.md` if it exists — every principle in it is binding on this epic, the same as on any feature.
3. Determine which flow applies:
   - **New Epic flow**: the user is describing a new epic that doesn't match any existing one. Find the highest `NN` in use and use `NN+1` for the new epic — this is its own counter, zero-padded to 2 digits (`01`, `02`, ... `99`), and independent of the features' 3-digit counter (see `sdd-specify`). Continue at Step 2.
   - **Phase Report flow**: the user names or clearly references an existing epic and isn't describing new scope. Skip to Step 7.
   - If it's genuinely ambiguous which flow applies, or which existing epic is meant, ask before proceeding — mirroring the epic-disambiguation logic in `sdd-specify` Step 1.
4. If the matched epic's `epic.md` still uses the old flat, unphased backlog table (a single `Feature Backlog` table with plain `F1, F2...` IDs and no phase subsections), say so explicitly and ask the user how to proceed before continuing — don't silently reinterpret it into the new structure.

## Step 2: Generate a Short Epic Name

2-4 words, kebab-case, preserving technical terms (e.g. "I want to build a recommendation system for our marketplace" → `recommendation-system`; "Add retrieval-augmented generation over our docs" → `rag-system`).

## Step 3: Draft the Feature Backlog, Organized by CRISP-ML(Q) Phase

From the epic description, identify the discrete features needed to realize it — not implementation tasks, features (each substantial enough to eventually get its own `sdd-specify` run). Organize them into the six CRISP-ML(Q) phases — Business & Data Understanding, Data Preparation, Modeling, Evaluation, Deployment, Monitoring & Maintenance — by which epic-level capability each feature delivers.

For an ML/LLM epic, this typically spans: data/feature pipeline (Data Preparation), the core model or retrieval component (Modeling), an evaluation harness (Evaluation), a serving/API layer (Deployment), and a feedback/monitoring loop (Monitoring & Maintenance) — but derive the actual list from the specific epic, don't force every phase to be populated. Omit a phase section entirely if the epic genuinely has no distinct feature for it (e.g. no dedicated evaluation-harness feature because each feature's own Evaluation Gate is judged sufficient) — state why in Assumptions, never render an empty table. If a feature doesn't cleanly fit one phase (e.g. a vertical-slice MVP spanning data + model + serving), file it under the earliest phase it substantially starts in and say so in its Goal — don't split one feature across two rows to satisfy the grouping.

For each phase you populate, capture:

- **Requirements & Constraints**: 2-4 bullets — what this phase must satisfy at the epic level (data/business needs, binding constitution principles, hard constraints) before scoping its features and risks.
- **Feature Backlog**, one row per feature:
  - **ID**: `[PHASE][N]` using the phase code — `BDU`, `DP`, `MOD`, `EVAL`, `DEPLOY`, `MON` — numbered sequentially within that phase (`DP1`, `DP2`, ...). This ID is also, lowercased and zero-padded, the name `sdd-specify` later gives the feature's own directory nested under this epic (e.g. `DP1` → `dp01-short-name`).
  - **Feature Name**: short, matches the name `sdd-specify` would derive from it.
  - **Type**: `Feature` (delivers epic capability) or `QA` (mitigates a risk identified in Step 4).
  - **Goal**: one line — what this feature delivers on its own.
  - **Priority**: P1 (needed for any working version of the epic) / P2 (important, not blocking) / P3 (nice-to-have).
  - **Depends On**: other backlog IDs, any phase, this one requires first (empty if none). Reflect the real gating relationship — a QA row auditing an already-built feature typically depends on it, but a QA row that gates a later phase (e.g. an evaluation harness that must pass before deployment) is instead a dependency *of* that later feature.
  - **Status**: always starts `Not Started`. `sdd-specify` flips a row to `Specified` (with a link to the resulting `spec.md`). `sdd-implement` flips it to `Implemented` once every task in that feature's own `tasks.md` is complete and its Evaluation Gate (if any) has passed. Never set anything other than these three values here.

Flag any feature whose feasibility is genuinely uncertain (e.g. depends on data that may not exist) the same way `sdd-specify` flags feasibility concerns — as an explicit note, not a silent assumption.

## Step 4: Identify Risks & Derive QA Backlog Rows

For each phase drafted in Step 3, walk CRISP-ML(Q)'s own quality-assurance loop — identify the risk a planned feature carries, judge whether it's feasible to accept as-is, and where it isn't, name the QA method that would mitigate it. This operationalizes that loop as a one-time drafting-time worksheet, not a literal runtime loop: the actual per-task iterate/re-check cycle the loop describes already happens for real inside each feature's own specify → plan → tasks → implement run. This step exists so a needed QA activity becomes a visible, trackable backlog row instead of disappearing into prose.

Per phase:

| Risk | Feasible As-Is? | QA Method / Mitigation | Resulting Backlog ID |
|---|---|---|---|
| [e.g. Training data may encode demographic bias] | No | Fairness audit across protected segments before Modeling proceeds | DP2 |
| [e.g. Serving latency budget is generous, no exotic infra needed] | Yes | — | — |

Every `No` row **must** produce a corresponding `QA`-typed row in that phase's Feature Backlog table (Step 3) — same execution model as any other feature, its own full `sdd-specify` → `sdd-plan` → `sdd-tasks` → `sdd-implement` run. Exception: if the mitigation is trivial enough to be fully contained inside another feature's own `tasks.md` (e.g. "add one extra unit test," "add a checklist item to code review") rather than warranting its own spec/plan/implementation cycle, fold it into that feature's tasks instead of creating a redundant top-level row — say so in the QA Method column rather than leaving it implicit.

A `Yes` row needs no further action here.

## Step 5: Write `epic.md`

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

*Organized by CRISP-ML(Q) phase — see sdd-epic Steps 3-4. Omit any phase with no epic-level feature; state why in Assumptions.*

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

[Entities used by more than one feature above, across any phase — see `shared-data-model.md`. If no entity is genuinely shared, state that explicitly and omit the file in Step 6.]

- **[Entity]**: used by [DP1, MOD1, ...]

## Sequencing / Minimum Viable Epic

[Which feature, or minimal subset of P1 features, constitutes a working end-to-end walking skeleton of the epic — the first slice worth shipping before adding the rest of the backlog. Include a QA row here only if its risk severity would block a minimum viable version (e.g. a compliance gate); lower-severity QA can land after the walking skeleton ships.]

## Assumptions

- [Assumption about data, infra, scope boundaries, or an omitted phase, made while drafting this backlog]

## Phase Reports

[Links to reports/<phase-name>-report.md, appended by sdd-epic's Phase Report flow as each phase completes. Empty until the first phase finishes.]
```

## Step 6: Draft `shared-data-model.md` (conditional)

Only if Step 5's Shared Entities section is non-empty:

```markdown
# Shared Data Model: [EPIC NAME]

**Epic**: .spec/NN-epic-name/epic.md

Entities defined here are binding for every feature under this epic — a feature's own `data-model.md` (generated by `sdd-plan`) must reference these, not redefine them.

## [Entity Name]

**Represents**: [what it is, at a conceptual/business level]
**Used by**: [feature IDs from the backlog]

| Field | Type | Notes |
|---|---|---|
| [...] | [...] | [...] |

**Relationships**: [to other shared entities]
```

## Step 7: Generate Phase Reports (Phase Report flow)

For every phase in the matched epic's `epic.md` where every backlog row (`Feature` and `QA` alike) is `Implemented` and no `reports/<phase-name>-report.md` exists yet:

1. For each row in that phase, load its feature's `spec.md` (Risk Assessment, Success Criteria), `plan.md` (Evaluation Gate: threshold vs. the actual result recorded during `sdd-implement`), and `monitoring.md` if present.
2. Write `.spec/NN-epic-name/reports/<phase-name>-report.md` (kebab-case phase name, e.g. `reports/data-preparation-report.md`):

```markdown
# Phase Report: [PHASE NAME] — [EPIC NAME]

**Epic**: .spec/NN-epic-name/epic.md | **Date**: [DATE]

## Features Delivered

| ID | Feature Name | Type | spec.md | plan.md |
|---|---|---|---|---|
| DP1 | [...] | Feature | [link] | [link] |
| DP2 | [...] | QA | [link] | [link] |

## Risks Realized vs. Planned

| Risk (from epic.md Step 4) | Materialized? | Outcome |
|---|---|---|
| [...] | Yes/No | [...] |

## QA Outcomes

[One line per QA-typed row: what its mitigation achieved, referencing its own spec.md Success Criteria / plan.md Evaluation Gate result.]

## Key Metrics

*Omit if no feature in this phase has an Evaluation Gate.*

| Metric | Threshold | Actual Result | Source Feature |
|---|---|---|---|

## Go/No-Go for Next Phase

[Recommendation + rationale — does anything here block the next phase from starting?]

## Carry-Forward Items

- [Deferred risk, follow-up QA, or scope item that didn't fit this phase but must be tracked going forward]
```

3. Append a link to it under `epic.md`'s **Phase Reports** section. Don't touch any Feature Backlog row or Status here — that's `sdd-implement`'s job.
4. If more than one phase qualifies in the same run, generate all of them, one file each.
5. If nothing qualifies (no phase is fully `Implemented` yet, or all completed phases already have reports), say so plainly and stop — don't force a report on an incomplete phase.

## Step 8: Closing

Report to the user:

**New Epic flow**:
- The `epic.md` path and, if generated, the `shared-data-model.md` path.
- The full feature backlog by phase (ID, name, type, priority, dependencies).
- The recommended first feature to run through `sdd-specify` (from Sequencing / Minimum Viable Epic).
- The exact next step: run `sdd-specify` for that feature, referencing `.spec/NN-epic-name/epic.md` so the spec picks up the Epic back-reference and shared entities automatically — the resulting feature directory will be nested at `.spec/NN-epic-name/[phase][nn]-short-name/`, named after that feature's own Feature Backlog ID (e.g. `bdu01-short-name`).

**Phase Report flow**:
- Which phase(s) got a report generated this run, their Go/No-Go recommendation, and any Carry-Forward items.
- Which phases are still in progress (rows not yet `Implemented`) and how many rows remain.
