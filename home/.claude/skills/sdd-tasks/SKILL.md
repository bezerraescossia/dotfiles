---
name: sdd-tasks
description: Generates an actionable, dependency-ordered task list (tasks.md) from a feature's implementation plan and spec, organized by user story for incremental delivery.
user_invocable: true
---

# Task List Generator (Actionable Tasks)

This skill guides Claude to act as a Tech Lead planning a feature's execution. The goal is to break `plan.md` + `spec.md` into concrete tasks, specific enough to be executed without additional context, organized by user story to enable incremental delivery (MVP first).

**Position in the SDD pipeline**: Plan → Checklist (optional) → **Tasks** → Analyze (optional) → Implement. Required input: `specs/NNN-feature/plan.md` and `specs/NNN-feature/spec.md`. Optional context: `docs/constitution.md`, `research.md`, `data-model.md`, `contracts/` in the same directory. Output: `specs/NNN-feature/tasks.md`.

---

## Step 1: Load Context

1. Identify the feature (same logic as `sdd-plan`: if ambiguous, ask, or use the most recent `specs/` directory with a `plan.md` but no `tasks.md`).
2. Read `specs/NNN-feature/plan.md` (required — without it, stop and ask the user to run `sdd-plan` first): extract stack, dependencies, and the defined project structure.
3. Read `specs/NNN-feature/spec.md` (required): extract user stories with their priorities (P1, P2, P3...).
4. If present, read `research.md` (decisions → become setup tasks), `data-model.md` (entities → mapped to the story that uses them first), and `contracts/` (each interface contract → mapped to the story it serves).
5. If it exists, read `docs/constitution.md`: check for a non-negotiable Test-First/TDD principle.

## Step 2: Decide Whether Test Tasks Are Included

By default, test tasks are **optional** and only included if:
- the spec explicitly requests tests, OR
- the user asks for a TDD approach in this run, OR
- `docs/constitution.md` has a non-negotiable Test-First/TDD principle — in which case test tasks become **mandatory** and must precede implementation in every user-story phase (Red-Green-Refactor).

## Step 3: Mandatory Format for Every Task

Every task **MUST** follow exactly this format:

```text
- [ ] T### [P?] [USn?] Action description with the exact file path
```

- **Checkbox**: always `- [ ]`.
- **ID**: sequential (`T001`, `T002`, ...) in execution order.
- **`[P]`**: include ONLY if the task is parallelizable (different file, no dependency on an incomplete task).
- **`[USn]`**: required on user-story-phase tasks (`[US1]`, `[US2]`...); FORBIDDEN in the Setup, Foundational, and Polish phases.
- **Description**: a clear action plus the exact file path, consistent with the project structure defined in `plan.md`.

Correct examples: `- [ ] T001 Create project structure per implementation plan` / `- [ ] T012 [P] [US1] Create User model in src/models/user.py`.
Wrong examples: missing checkbox, missing ID, missing `[USn]` in a user-story phase, or missing a file path.

## Step 4: Phase Structure

Generate `specs/NNN-feature/tasks.md` following this organization (based on spec-kit's `tasks-template.md`):

1. **Phase 1 — Setup**: project/dependency initialization (no `[Story]`).
2. **Phase 2 — Foundational**: blocking prerequisites shared by all user stories (base data schema, middleware, routing, config) — no `[Story]`. No user story may start before this phase finishes.
3. **Phase 3+ — one phase per user story**, in priority order (P1 first, then P2, P3...):
   - Header with `Goal` (what the story delivers) and `Independent Test` (how to validate it in isolation), copied/refined from the spec.
   - If tests are included (Step 2): test tasks first, marked `[P]` where possible, which must FAIL before implementation.
   - Implementation tasks: models → services → endpoints/UI → integration/validation/logging, in that dependency order.
   - End with a `Checkpoint`: the story should be functional and independently testable at this point.
4. **Final phase — Polish & Cross-Cutting Concerns**: documentation, refactor, performance, hardening, additional tests — no `[Story]`.

Include at the end of the document:
- **Dependencies & Execution Order**: dependencies between phases and between user stories (most stories should be independent of each other).
- **Parallel Example**: a block showing `[P]` tasks from the same story that can be launched together.
- **Implementation Strategy**: MVP = Setup + Foundational + User Story 1 only; then incremental delivery adding one story at a time.

## Step 5: Validate Before Writing

- Every user-story-phase task has `[USn]`; no Setup/Foundational/Polish task has `[USn]`.
- Every cited file path is consistent with the "Project Structure" defined in `plan.md`.
- Each user story, in isolation, covers everything needed to be testable end-to-end (no story leaves an implicit dependency on a story of equal or lower priority).

## Step 6: Closing

Report to the user: the `tasks.md` path, total task count, count per user story, identified parallelization opportunities, and the suggested MVP scope (typically Setup + Foundational + User Story 1). Suggest `sdd-analyze` as an optional consistency pass before `sdd-implement`.
