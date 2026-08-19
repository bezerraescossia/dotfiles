---
name: sdd-implement
description: Executes a feature's implementation plan by working through every task in tasks.md, phase by phase, respecting dependencies, parallel markers, and the Evaluation Gate, and checking off completed work.
user_invocable: true
---

# Implementation Executor

This skill guides Claude to execute a feature end-to-end from its generated artifacts, rather than planning it. It's where code, data pipelines, and models actually get built — the second-to-last step of the pipeline, followed by `sdd-monitor`.

**Position in the SDD pipeline**: Tasks → Analyze (optional) → **Implement** → Monitor (optional). Required input: `.spec/[feature-dir]/tasks.md` and `.spec/[feature-dir]/plan.md`. Optional context: `data-preparation.md`, `data-model.md`, `contracts/`, `research.md`, `quickstart.md`, `.spec/constitution.md`, and any checklists under `.spec/[feature-dir]/checklists/`.

If `tasks.md` is missing or incomplete, tell the user to run `sdd-tasks` first — don't improvise a task breakdown here.

---

## Step 1: Check Checklist Status (gate)

If `.spec/[feature-dir]/checklists/` exists, scan every checklist file:

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

## Step 2: Check Evaluation Gate Status (gate)

If `plan.md` has an Evaluation Gate section, this is a second **read-only gate**, independent of Step 1:

- Locate the Evaluation phase in `tasks.md`. Its task(s) must be marked `[X]` and their recorded result (in the task's own notes, or in `tasks.md`'s Checkpoint line) must meet every metric/threshold row in `plan.md`'s Evaluation Gate table — not merely be checked off.
- Show a status table mirroring the Evaluation Gate: Metric | Threshold | Recorded Result | Status (✓ PASS / ✗ FAIL / — Not yet run).
- If the Evaluation phase hasn't run yet, or any metric fails: show the table, then **stop before executing any Deployment-phase task** and ask "The Evaluation Gate hasn't passed. Proceed to deployment anyway?" Wait for the answer; only continue on an explicit yes. Non-deployment phases (Setup through Modeling/Experimentation) may still proceed normally regardless of this gate.
- If `plan.md` has no Evaluation Gate section (confirmed non-ML feature), skip this step entirely.

## Step 3: Load Implementation Context

- **Required**: `tasks.md` (full task list and execution plan), `plan.md` (tech stack, architecture, file structure, Evaluation Gate).
- **If present**: `data-preparation.md`, `data-model.md`, `contracts/`, `research.md`, `.spec/constitution.md`, `quickstart.md`.

## Step 4: Verify Project Setup

Check for the ignore files the detected stack actually needs, and create or top up whichever are missing essential patterns (never blindly overwrite an existing one — only append missing critical patterns):

- Git repo (`git rev-parse --git-dir` succeeds) → `.gitignore`.
- `Dockerfile*` present or Docker mentioned in `plan.md` → `.dockerignore`.
- `.eslintrc*` → `.eslintignore`; `eslint.config.*` → check its `ignores` entries instead.
- `.prettierrc*` → `.prettierignore`.
- Terraform files → `.terraformignore`; Helm charts → `.helmignore`.

Use the patterns standard for the stack found in `plan.md` (e.g. Node: `node_modules/`, `dist/`, `.env*`; Python: `__pycache__/`, `.venv/`, `*.egg-info/`; Go: `vendor/`, `*.out`; Rust: `target/`; and so on for the language actually in use), plus universal patterns (`.DS_Store`, `*.tmp`, `.idea/`).

## Step 5: Parse the Task Plan

Extract from `tasks.md`: phases (Setup, Foundational, Data Preparation, Modeling/Experimentation, Evaluation, Deployment, Monitoring Setup, Polish — or the non-ML fallback phases), task IDs, descriptions, file paths, `[P]` parallel markers, Accept/Reject clauses, and dependency/execution order.

## Step 6: Execute Phase by Phase

- Complete each phase fully before moving to the next.
- Run sequential tasks in order; `[P]`-marked tasks in the same phase may run together.
- If a phase includes test tasks before implementation tasks (TDD), write and run the tests first — they should fail before the corresponding implementation exists.
- Tasks touching the same file must run sequentially even if not both marked `[P]`.
- Order within a phase: setup/init → tests (if any) → models → services → endpoints/UI → integration → polish.
- **Modeling/Experimentation tasks**: run the task, record the actual metric result against its stated Accept/Reject clause. On Reject, follow the task's named fallback (return to the earlier task it points to) instead of proceeding to the next Modeling task — this is the CRISP-ML(Q) backward loop, not a failure to halt on.
- **Evaluation phase**: run it in full and record every metric against `plan.md`'s Evaluation Gate table before touching any Deployment task (re-checked by Step 2 if this skill is re-entered).
- Verify each phase's completion before moving to the next.

## Step 7: Track Progress

- Report progress after each completed task.
- Mark each completed task `[X]` in `tasks.md` as you finish it — this is the one file this skill is expected to keep editing throughout the run.
- On a failure in a non-parallel task, halt and report it clearly with enough context to debug, and suggest next steps.
- On a failure in a `[P]` task, continue with the other parallel tasks and report the failed one at the end of that batch.

## Step 8: Validate Completion

- Confirm every task in `tasks.md` is marked `[X]`.
- Confirm the implemented feature matches the original spec.
- Confirm the Evaluation Gate passed (or that the user explicitly approved proceeding without it, per Step 2).
- Confirm tests pass (where applicable) and the implementation follows the technical plan.

## Step 9: Closing

Report final status: summary of completed work, any tasks left incomplete and why, test results, and anything that still needs manual follow-up.

Generate a short **model/experiment summary** (skip for a confirmed non-ML feature): what approaches were tried in Modeling/Experimentation, the final metrics vs. the Evaluation Gate thresholds, and where artifacts were logged in the experiment-tracking tool.

Suggest `sdd-monitor` as the next step to set up drift detection, retraining triggers, and a rollback runbook before or shortly after this feature ships.
