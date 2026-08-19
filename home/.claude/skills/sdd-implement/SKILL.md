---
name: sdd-implement
description: Executes a feature's implementation plan by working through every task in tasks.md, phase by phase, respecting dependencies and parallel markers, and checking off completed work.
user_invocable: true
---

# Implementation Executor

This skill guides Claude to execute a feature end-to-end from its generated artifacts, rather than planning it. It's the last step of the SDD pipeline — where code actually gets written.

**Position in the SDD pipeline**: Tasks → Analyze (optional) → **Implement**. Required input: `specs/NNN-feature/tasks.md` and `specs/NNN-feature/plan.md`. Optional context: `data-model.md`, `contracts/`, `research.md`, `quickstart.md`, `docs/constitution.md`, and any checklists under `specs/NNN-feature/checklists/`.

If `tasks.md` is missing or incomplete, tell the user to run `sdd-tasks` first — don't improvise a task breakdown here.

---

## Step 1: Check Checklist Status (gate)

If `specs/NNN-feature/checklists/` exists, scan every checklist file:

- Count total items (`- [ ]`/`- [x]`/`- [X]`), checked, and unchecked, per file.
- Show a status table:
  ```text
  | Checklist    | Total | Checked | Unchecked | Status |
  |--------------|-------|---------|-----------|--------|
  | ux.md        | 12    | 12      | 0         | ✓ PASS |
  | security.md  | 6     | 4       | 2         | ✗ FAIL |
  ```
- This is a **read-only gate** — never modify checklist files or their markers here.
- If any checklist has unchecked items: show the table, then **stop** and ask "Some checklists have unchecked items. Proceed with implementation anyway?" Wait for the answer; only continue on an explicit yes.
- If all checklists pass: show the table and continue automatically.

## Step 2: Load Implementation Context

- **Required**: `tasks.md` (full task list and execution plan), `plan.md` (tech stack, architecture, file structure).
- **If present**: `data-model.md`, `contracts/`, `research.md`, `docs/constitution.md`, `quickstart.md`.

## Step 3: Verify Project Setup

Check for the ignore files the detected stack actually needs, and create or top up whichever are missing essential patterns (never blindly overwrite an existing one — only append missing critical patterns):

- Git repo (`git rev-parse --git-dir` succeeds) → `.gitignore`.
- `Dockerfile*` present or Docker mentioned in `plan.md` → `.dockerignore`.
- `.eslintrc*` → `.eslintignore`; `eslint.config.*` → check its `ignores` entries instead.
- `.prettierrc*` → `.prettierignore`.
- Terraform files → `.terraformignore`; Helm charts → `.helmignore`.

Use the patterns standard for the stack found in `plan.md` (e.g. Node: `node_modules/`, `dist/`, `.env*`; Python: `__pycache__/`, `.venv/`, `*.egg-info/`; Go: `vendor/`, `*.out`; Rust: `target/`; and so on for the language actually in use), plus universal patterns (`.DS_Store`, `*.tmp`, `.idea/`).

## Step 4: Parse the Task Plan

Extract from `tasks.md`: phases (Setup, Foundational, per-user-story, Polish), task IDs, descriptions, file paths, `[P]` parallel markers, and dependency/execution order.

## Step 5: Execute Phase by Phase

- Complete each phase fully before moving to the next.
- Run sequential tasks in order; `[P]`-marked tasks in the same phase may run together.
- If a phase includes test tasks before implementation tasks (TDD), write and run the tests first — they should fail before the corresponding implementation exists.
- Tasks touching the same file must run sequentially even if not both marked `[P]`.
- Order within a phase: setup/init → tests (if any) → models → services → endpoints/UI → integration → polish.
- Verify each phase's completion before moving to the next.

## Step 6: Track Progress

- Report progress after each completed task.
- Mark each completed task `[X]` in `tasks.md` as you finish it — this is the one file this skill is expected to keep editing throughout the run.
- On a failure in a non-parallel task, halt and report it clearly with enough context to debug, and suggest next steps.
- On a failure in a `[P]` task, continue with the other parallel tasks and report the failed one at the end of that batch.

## Step 7: Validate Completion

- Confirm every task in `tasks.md` is marked `[X]`.
- Confirm the implemented feature matches the original spec.
- Confirm tests pass (where applicable) and the implementation follows the technical plan.

## Step 8: Closing

Report final status: summary of completed work, any tasks left incomplete and why, test results, and anything that still needs manual follow-up.
