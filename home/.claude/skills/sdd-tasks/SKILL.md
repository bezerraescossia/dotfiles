---
name: sdd-tasks
description: Generates an actionable, dependency-ordered task list (tasks.md) from a feature's implementation plan and spec, organized by CRISP-ML(Q) phase (Data Preparation, Modeling/Experimentation, Evaluation, Deployment, Monitoring Setup) with explicit accept/reject criteria on modeling tasks. Falls back to plain Setup/Foundational/Polish phasing for a non-ML feature.
user_invocable: true
---

# Task List Generator (Actionable Tasks)

This skill guides Claude to act as a Tech Lead planning a feature's execution. The goal is to break `plan.md` + `spec.md` into concrete tasks, specific enough to be executed without additional context, organized by CRISP-ML(Q) phase so an ML feature's inherent iterate-and-backtrack cycle is represented, not hidden.

**Position in the SDD pipeline**: Plan → Checklist (optional) → **Tasks** → Analyze (optional) → Implement → Monitor (optional). Required input: `.spec/[feature-dir]/plan.md` and `.spec/[feature-dir]/spec.md`. Optional context: `.spec/constitution.md`, `research.md`, `data-preparation.md`, `data-model.md`, `contracts/` in the same directory. Output: `.spec/[feature-dir]/tasks.md`.

---

## Step 1: Load Context

1. Identify the feature (same logic as `sdd-plan`: if ambiguous, ask, or use the most recent `.spec/` directory with a `plan.md` but no `tasks.md`).
2. Read `.spec/[feature-dir]/plan.md` (required — without it, stop and ask the user to run `sdd-plan` first): extract stack, dependencies, Evaluation Gate thresholds, and the defined project structure.
3. Read `.spec/[feature-dir]/spec.md` (required): extract user stories with their priorities (P1, P2, P3...), the Risk Assessment table, and Success Criteria (Business KPIs and Model/ML Metrics).
4. If present, read `research.md` (decisions → become setup tasks), `data-preparation.md` (data pipeline steps → Data Preparation phase tasks), `data-model.md` (entities → mapped to the phase that first uses them), and `contracts/` (each interface contract → mapped to Deployment).
5. If it exists, read `.spec/constitution.md`: check for a non-negotiable Test-First/TDD principle and for a mandated experiment-tracking tool.
6. If `plan.md` has no Evaluation Gate section (confirmed non-ML feature), skip straight to the non-ML phase structure in Step 4B.

## Step 2: Decide Whether Test Tasks Are Included

By default, test tasks for non-model code (data pipeline unit tests, API contract tests, integration tests) are **optional** and only included if:
- the spec explicitly requests tests, OR
- the user asks for a TDD approach in this run, OR
- `.spec/constitution.md` has a non-negotiable Test-First/TDD principle — in which case test tasks become **mandatory** and must precede implementation in every phase (Red-Green-Refactor).

Evaluation tasks (Step 4A, Phase 5) are never optional for an ML feature — they are the mechanism by which the Evaluation Gate is enforced, independent of whether TDD is in effect.

## Step 3: Mandatory Format for Every Task

Every task **MUST** follow exactly this format:

```text
- [ ] T### [P?] [USn?] Action description with the exact file path
```

- **Checkbox**: always `- [ ]`.
- **ID**: sequential (`T001`, `T002`, ...) in execution order.
- **`[P]`**: include ONLY if the task is parallelizable (different file, no dependency on an incomplete task).
- **`[USn]`**: an optional prioritization tag referencing a spec user story (`[US1]`, `[US2]`...). Allowed only on Modeling/Experimentation and Deployment tasks; FORBIDDEN in Setup, Foundational, Data Preparation, Evaluation, Monitoring Setup, and Polish phases.
- **Description**: a clear action plus the exact file path, consistent with the project structure defined in `plan.md`.
- **Modeling/Experimentation tasks additionally require** an inline **Accept/Reject** clause (see Step 4A, Phase 4).

Correct examples: `- [ ] T001 Create project structure per implementation plan` / `- [ ] T012 [P] [US1] Wire the scoring endpoint to the trained model in src/serving/predict.py` / `- [ ] T015 Train baseline gradient-boosted model in src/models/baseline.py — Accept if F1 ≥ 0.85 on the held-out test set (plan.md Evaluation Gate), else return to T009 (Feature Engineering)`.
Wrong examples: missing checkbox, missing ID, `[USn]` on a Data Preparation/Evaluation task, missing a file path, or a Modeling task with no accept/reject clause.

## Step 4A: Phase Structure — ML Feature (default)

Generate `.spec/[feature-dir]/tasks.md` following this organization:

1. **Phase 1 — Setup**: project/dependency initialization, experiment-tracking tool wiring — no `[Story]`.
2. **Phase 2 — Foundational**: blocking prerequisites shared by everything downstream (base config, data-access credentials, shared schemas) — no `[Story]`. Nothing in Phase 3+ may start before this finishes.
3. **Phase 3 — Data Preparation**: sourcing, cleaning, labeling, splitting (per `data-preparation.md`'s split strategy), and versioning tasks — no `[Story]`. End with a `Checkpoint`: the versioned train/validation/test datasets exist and are reproducible.
4. **Phase 4 — Modeling / Experimentation**: baseline task first, then iteration tasks. **Every task in this phase states its Accept/Reject criteria inline**, quoting the relevant Evaluation Gate metric/threshold from `plan.md`, plus an explicit fallback naming which earlier task to return to on rejection (e.g. "if F1 < 0.75, return to T009 Feature Engineering — do not proceed to Phase 5"). `[USn]` may tag a task here to show which user story/capability it serves. End with a `Checkpoint`: a specific model/prompt version is selected as the candidate for evaluation.
5. **Phase 5 — Evaluation**: a formal gate phase — task(s) that run the full Evaluation Protocol from `plan.md` against the candidate from Phase 4 and record the result against every row of the Evaluation Gate table. No `[Story]`. This phase must pass in full before any Phase 6 task runs.
6. **Phase 6 — Deployment**: rollout tasks (batch job, online endpoint, shadow deployment as specified), rollback-procedure tasks. `[USn]` may tag a task here.
7. **Phase 7 — Monitoring Setup**: lightweight instrumentation tasks wiring the signals `plan.md`'s Monitoring & Retraining Triggers calls for (metric logging, drift-detection hooks) — no `[Story]`. Full monitoring design is generated later by `sdd-monitor`; these tasks just make the hooks exist.
8. **Final Phase — Polish & Cross-Cutting Concerns**: documentation, refactor, performance, hardening, additional tests, model card — no `[Story]`.

## Step 4B: Phase Structure — Non-ML Feature (fallback)

Use this only when `plan.md` has no Evaluation Gate (confirmed non-ML feature):

1. **Phase 1 — Setup**: project/dependency initialization (no `[Story]`).
2. **Phase 2 — Foundational**: blocking prerequisites shared by all user stories (base data schema, middleware, routing, config) — no `[Story]`. No user story may start before this phase finishes.
3. **Phase 3+ — one phase per user story**, in priority order (P1 first, then P2, P3...):
   - Header with `Goal` (what the story delivers) and `Independent Test` (how to validate it in isolation), copied/refined from the spec.
   - If tests are included (Step 2): test tasks first, marked `[P]` where possible, which must FAIL before implementation.
   - Implementation tasks: models → services → endpoints/UI → integration/validation/logging, in that dependency order.
   - End with a `Checkpoint`: the story should be functional and independently testable at this point.
4. **Final phase — Polish & Cross-Cutting Concerns**: documentation, refactor, performance, hardening, additional tests — no `[Story]`.

## Step 5: Content at the End of the Document

Include, regardless of which phase structure was used:
- **Dependencies & Execution Order**: dependencies between phases (and, for the ML structure, the explicit backward-loop edges from Phase 4/5 rejections).
- **Parallel Example**: a block showing `[P]` tasks from the same phase that can be launched together.
- **Implementation Strategy**: for the ML structure, MVP = Setup + Foundational + Data Preparation + a single baseline model through Evaluation; deployment and further modeling iterations come after. For the non-ML structure, MVP = Setup + Foundational + User Story 1 only, then incremental delivery adding one story at a time.

## Step 6: Validate Before Writing

- Every Modeling/Experimentation task has an inline Accept/Reject clause with a named fallback task.
- No Setup/Foundational/Data Preparation/Evaluation/Monitoring Setup/Polish task has `[USn]`.
- The Evaluation phase's metrics/thresholds match `plan.md`'s Evaluation Gate table exactly — no restating them with different numbers.
- Every cited file path is consistent with the "Project Structure" defined in `plan.md`.
- Each user story, in isolation, covers everything needed to be testable end-to-end (no story leaves an implicit dependency on a story of equal or lower priority).

## Step 7: Closing

Report to the user: the `tasks.md` path, total task count, count per phase, identified parallelization opportunities, the Evaluation Gate thresholds tasks must clear, and the suggested MVP scope. Suggest `sdd-analyze` as an optional consistency pass before `sdd-implement`.
