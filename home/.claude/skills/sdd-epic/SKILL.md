---
name: sdd-epic
description: Declares a multi-feature epic (e.g. "recommendation system", "RAG system", "fraud detection") and drafts the dependency-ordered feature backlog needed to realize it, plus a shared cross-feature data model, at .spec/E<N>-epic-name/. Optional step between sdd-constitution and sdd-specify.
user_invocable: true
---

# Epic Backlog Generator

This skill guides Claude to act as a Staff ML Engineer / Product Lead scoping a multi-feature effort before any single feature gets specified. The goal is to turn a raw epic idea ("build a recommendation system") into a dependency-ordered **feature backlog** — the list of features needed to realize it — plus, when the epic has entities multiple features will share, a shared cross-feature data model. It does **not** write user stories or acceptance criteria itself; that's `sdd-specify`'s job, one feature at a time.

**Position in the SDD pipeline**: Constitution → **Epic** (optional) → Specify → Clarify (optional) → Plan → Checklist (optional) → Tasks → Analyze (optional) → Implement → Monitor (optional). Expected input: `.spec/constitution.md` (if it exists) and a natural-language epic description. Output: `.spec/E<N>-epic-name/epic.md`, plus `.spec/E<N>-epic-name/shared-data-model.md` when warranted.

**Hierarchy this skill sits at the top of**: Epic → Feature (`sdd-specify`) → User Stories → Acceptance Scenarios, alongside each feature's own Success Criteria. Skip this skill entirely for a one-off feature with no larger epic behind it — go straight to `sdd-specify`.

---

## Step 1: Load Context

1. Check for an existing `.spec/` directory (create it if none exists yet). List its existing epic directories (`E<N>-*`, i.e. directories containing an `epic.md`), find the highest `N` in use, and use `N+1` for the new epic — this is its own counter, **not** zero-padded (`E1`, `E2`, ... `E10`, ...), and independent of the features' `F<NNN>` counter (see `sdd-specify`).
2. Read `.spec/constitution.md` if it exists — every principle in it is binding on this epic, the same as on any feature.

## Step 2: Generate a Short Epic Name

2-4 words, kebab-case, preserving technical terms (e.g. "I want to build a recommendation system for our marketplace" → `recommendation-system`; "Add retrieval-augmented generation over our docs" → `rag-system`).

## Step 3: Draft the Feature Backlog

From the epic description, identify the discrete features needed to realize it — not implementation tasks, features (each substantial enough to eventually get its own `sdd-specify` run). For an ML/LLM epic, this typically spans the full path from data to production: data/feature pipeline, the core model or retrieval component, a serving/API layer, an evaluation harness, and often a feedback/monitoring loop — but derive the actual list from the specific epic, don't force a fixed template.

For each feature, capture:
- **ID**: `F1`, `F2`, ... in a sensible build order — a lightweight, backlog-local label for ordering and `Depends On` references, distinct from the real `F<NNN>` number `sdd-specify` later assigns to the feature's directory.
- **Feature Name**: short, matches the name `sdd-specify` would derive from it.
- **Goal**: one line — what this feature delivers on its own.
- **Priority**: P1 (needed for any working version of the epic) / P2 (important, not blocking) / P3 (nice-to-have).
- **Depends On**: other feature IDs this one requires first (empty if none).
- **Status**: always starts `Not Started`. `sdd-specify` flips a row to `Specified` (with a link to the resulting `spec.md`) when it runs against this epic — never set anything other than `Not Started` here.

Flag any feature whose feasibility is genuinely uncertain (e.g. depends on data that may not exist) the same way `sdd-specify` flags feasibility concerns — as an explicit note, not a silent assumption.

## Step 4: Write `epic.md`

```markdown
# Epic: [EPIC NAME]

**Epic ID**: `[E<N>-epic-short-name]`
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

| ID | Feature Name | Goal | Priority | Depends On | Status |
|---|---|---|---|---|---|
| F1 | [...] | [...] | P1 | — | Not Started |
| F2 | [...] | [...] | P1 | F1 | Not Started |
| F3 | [...] | [...] | P2 | F1 | Not Started |

## Shared Entities

[Entities used by more than one feature above — see `shared-data-model.md`. If no entity is genuinely shared, state that explicitly and omit the file in Step 5.]

- **[Entity]**: used by [F1, F2, ...]

## Sequencing / Minimum Viable Epic

[Which feature, or minimal subset of P1 features, constitutes a working end-to-end walking skeleton of the epic — the first slice worth shipping before adding the rest of the backlog]

## Assumptions

- [Assumption about data, infra, or scope boundaries made while drafting this backlog]
```

## Step 5: Draft `shared-data-model.md` (conditional)

Only if Step 4's Shared Entities section is non-empty:

```markdown
# Shared Data Model: [EPIC NAME]

**Epic**: .spec/E<N>-epic-name/epic.md

Entities defined here are binding for every feature under this epic — a feature's own `data-model.md` (generated by `sdd-plan`) must reference these, not redefine them.

## [Entity Name]

**Represents**: [what it is, at a conceptual/business level]
**Used by**: [feature IDs from the backlog]

| Field | Type | Notes |
|---|---|---|
| [...] | [...] | [...] |

**Relationships**: [to other shared entities]
```

## Step 6: Closing

Report to the user:
- The `epic.md` path and, if generated, the `shared-data-model.md` path.
- The full feature backlog (ID, name, priority, dependencies).
- The recommended first feature to run through `sdd-specify` (from Sequencing / Minimum Viable Epic).
- The exact next step: run `sdd-specify` for that feature, referencing `.spec/E<N>-epic-name/epic.md` so the spec picks up the Epic back-reference and shared entities automatically — the resulting feature directory will be named `E<N>F<NNN>-short-name`.
