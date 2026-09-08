---
name: sdd-implement
description: Takes one feature already specified by sdd-backlog (user-declared) from technical plan through working code — Plan, an optional on-demand requirements-quality Checklist, Tasks, a read-only Analyze consistency pass, and Implement — resuming from whatever's already on disk so re-running it only does what's left. Pauses once, after Plan, to show the Constitution Check and Evaluation Gate before generating tasks, and gates Implement on any checklist file's unchecked items and on the Evaluation Gate passing.
user_invocable: true
argument-hint: "<feature name or directory>"
---

# Feature Implementer (Plan → Checklist → Tasks → Analyze → Implement)

This skill guides Claude from a feature's specification to its working implementation, for **exactly one feature per invocation**, declared by the user. It acts as a Senior ML/Software Architect for planning, a Tech Lead for task breakdown, and an implementation engineer for execution — the same person walking the whole way, not four separate handoffs.

**Position in the SDD pipeline**: after `sdd-backlog` has produced `.spec/[feature-dir]/spec.md`. Required input: that `spec.md`, and `.spec/constitution.md` if it exists (proceed with a warning if missing). Output: `plan.md` (+ `research.md`/`data-preparation.md`/`data-model.md`/contract files/`quickstart.md` as needed), an optional domain checklist, `tasks.md`, an Analyze report (not persisted), and the actual code/pipeline/model — plus `tasks.md` checkbox state and, if this feature belongs to an epic, that epic's `epic.md` row.

**Default assumption**: the feature trains, fine-tunes, or prompts a model. If `spec.md` scoped itself as non-ML, skip the ML-specific Technical Context fields and the Evaluation Gate throughout, and treat this as a traditional software feature.

## Directory conventions

- `.spec/constitution.md` — global governance principles, written by `sdd-constitution`.
- `.spec/NN-epic-name/[phase][nn]-feature-name/` or `.spec/00NNN-feature-name/` — the feature directory, created by `sdd-backlog`. Contains `spec.md` already; this skill adds `plan.md`, `tasks.md`, and everything else flat alongside it — no `checklists/` or `contracts/` subfolder, ever. If this feature belongs to an epic, its `epic.md` lives at `.spec/NN-epic-name/epic.md`.

---

## Step 1: Identify the Feature and Resume State

1. Identify the feature: if the user names one, use it (matching by directory name or short name). If ambiguous, list `.spec/` feature directories that have a `spec.md` and ask.
2. Read `.spec/[feature-dir]/spec.md` (required — without it, stop and tell the user to run `sdd-backlog` first).
3. Read `.spec/constitution.md` if it exists (warn once if missing, then proceed).
4. **Build a resume checklist from disk** — this run only does what's not already done:
   - `plan.md` present → Plan already done, skip to Step 3's pause-point summary instead of regenerating (unless the user asks to redo it).
   - Any non-core `.md` file in the feature directory containing `- [ ]`/`- [x]` items → a checklist already exists; Step 4 is on-demand regardless, but note its current pass/fail state.
   - `tasks.md` present → Tasks already done (report `[X]` count / total); skip Step 5 unless the user asks to regenerate it.
   - `tasks.md` fully `[X]` → Implement already complete; Step 7 has nothing to do besides re-confirming gates if re-entered.
5. Report this resume state to the user before doing anything else.

## Step 2: Plan Sub-Stage (skip if `plan.md` already exists and the user isn't asking to redo it)

1. If `spec.md` has an `Epic` back-reference, read that epic's `shared-data-model.md` if it exists — its entities are binding for `data-model.md` below.
2. Fill every Technical Context field with real evidence, never assumption: where a stack/pipeline/model already exists (dependency manifests, notebooks, training scripts, an existing directory tree), inspect it and treat it as binding. Where nothing is decided, whatever the constitution fixes is binding; for the rest, ask the user directly (`AskUserQuestion` or short question blocks) — never choose the data source, model approach, or stack unilaterally. Anything still open becomes an explicit `NEEDS CLARIFICATION` — never a silent assumption.
3. Write `.spec/[feature-dir]/plan.md` following `PLAN-TEMPLATE.md` exactly, including the Constitution Check and, unless confirmed non-ML, the Evaluation Gate (its thresholds must match `spec.md`'s Model/ML Metrics verbatim).
4. If the Constitution Check recorded a `Violation` with no acceptable justification, **do not proceed** — resolve it (back to the spec/design, or record it in Complexity Tracking with explicit rationale) before continuing.
5. Phase 0 (Research) and Phase 1 (Design & Contracts) sub-steps in `PLAN-TEMPLATE.md` run as described there, conditionally.

## Step 3: Pause for Review

Show the user the Constitution Check table and the Evaluation Gate table (or note why it was omitted) from the just-written `plan.md`. Ask them to confirm before generating tasks — this is the one built-in pause point in this skill. Only proceed to Step 5 on an explicit go-ahead; if they want changes, revise `plan.md` and re-show the tables.

## Step 4: Checklist Sub-Stage (on-demand only — do not run unless asked)

Only run this if the user explicitly asks for a domain checklist this session (e.g. "generate a security checklist for this feature"). Otherwise skip straight to Step 5.

**Core concept**: a checklist here is a **unit test suite for requirements writing**, not a test plan for the implementation — "Is 'fast loading' quantified with specific timing thresholds? [Clarity]", never "Verify the button clicks correctly."

1. Derive up to 3 contextual clarifying questions about scope/depth/audience from the user's request plus signals in spec/plan (domain keywords, risk indicators, stakeholder hints) — skip any already unambiguous. Present options as a compact table if needed (max A-E).
2. Read `spec.md`, `plan.md`, and `tasks.md` if it exists — only what's relevant to the chosen focus areas.
3. Write (or append to, continuing the `CHK###` numbering) `.spec/[feature-dir]/[domain].md` — a flat file, name it something that won't collide with another artifact in the directory (`ux.md`, `security.md`, `data-quality.md`, ...). Every item evaluates completeness/clarity/consistency/measurability/coverage of the *requirements*, tagged `[Gap]`/`[Ambiguity]`/`[Conflict]`/`[Assumption]` or `[Spec §X.Y]` for ≥80% of items. Leave every new item unchecked — checkbox state belongs to the reviewer, and this skill must never check its own items (except the built-in `requirements.md` from `sdd-backlog`, which is a separate exception).
4. Report the file path, item count, and whether it was created or appended to.

## Step 5: Tasks Sub-Stage (skip if `tasks.md` already exists and the user isn't asking to redo it)

1. Extract from `plan.md`: stack, dependencies, Evaluation Gate thresholds, project structure. Extract from `spec.md`: user stories with priorities, Risk Assessment, Success Criteria. If present, fold in `research.md`, `data-preparation.md`, `data-model.md`, and any contract file. If `.spec/constitution.md` has a non-negotiable Test-First/TDD principle, test tasks become mandatory throughout; otherwise they're optional (include only if the spec/user asks, or the constitution requires them).
2. **Every task** follows exactly: `- [ ] T### [P?] [USn?] Action description with the exact file path` — sequential IDs, `[P]` only if parallelizable, `[USn]` only on Modeling/Experimentation and Deployment tasks (forbidden elsewhere), and a Modeling task always adds an inline Accept/Reject clause naming a fallback task.
3. **If `plan.md` has an Evaluation Gate** (default ML case), organize into: Phase 1 Setup → Phase 2 Foundational → Phase 3 Data Preparation (checkpoint: reproducible versioned splits) → Phase 4 Modeling/Experimentation (baseline first, every task has Accept/Reject + named fallback, checkpoint: candidate selected) → Phase 5 Evaluation (formal gate, must pass before Phase 6) → Phase 6 Deployment (rollout + rollback tasks) → Final Phase Polish. (No standalone Monitoring Setup phase — this pipeline no longer has a Monitor stage; if `plan.md` sketched monitoring signals, note them as a Polish-phase follow-up instead.)
4. **If `plan.md` has no Evaluation Gate** (confirmed non-ML), organize into: Phase 1 Setup → Phase 2 Foundational → Phase 3+ one phase per user story in priority order (Goal + Independent Test header, tests-then-implementation if TDD, checkpoint per story) → Final Phase Polish.
5. End the document with Dependencies & Execution Order (including backward-loop edges for the ML structure), a Parallel Example block, and Implementation Strategy (MVP scope).
6. Validate before writing: every Modeling task has Accept/Reject + fallback; no `[USn]` outside Modeling/Deployment; Evaluation phase metrics match `plan.md` exactly; every file path matches the plan's Project Structure; each user story is independently testable end-to-end.

## Step 6: Analyze Sub-Stage (read-only — recommended but skippable)

Offer to run this before Implement; proceed straight to Step 7 if the user declines.

1. Load `spec.md`, `plan.md`, `tasks.md`, and `.spec/constitution.md` if present. Build (internally, don't dump raw artifacts) a requirements inventory (FR-###/SC-### keys), risk inventory, user-story/action inventory, task coverage mapping, and Evaluation Gate model.
2. Run detection passes (cap 50 findings, summarize overflow): **A** Duplication, **B** Ambiguity (vague adjectives, unresolved placeholders), **C** Underspecification, **D** Constitution alignment, **E** Coverage gaps, **F** Inconsistency (terminology drift, ordering contradictions), **G** Evaluation Gate mismatch (spec vs. plan vs. tasks), **H** Constitution/ML compliance (mandated tool missing from plan).
3. Severity: **CRITICAL** (constitution MUST violation, missing core artifact, zero-coverage baseline requirement, missing Risk Assessment on a non-confirmed-non-ML feature, Evaluation Gate mismatch) / **HIGH** (duplicate/conflicting requirement, untestable criterion, uncovered Risk mitigation, Modeling task missing Accept/Reject) / **MEDIUM** (terminology drift, missing non-functional coverage) / **LOW** (style).
4. Produce the report per `ANALYZE-REPORT-TEMPLATE.md`. Never modify files here. If CRITICAL issues exist, recommend resolving them before Step 7; offer to suggest concrete remediation edits but never apply them automatically.

## Step 7: Implement Sub-Stage

### 7a. Checklist Gate (read-only)

Identify every checklist file in the feature directory (any `.md` other than `spec.md`/`plan.md`/`tasks.md`/`research.md`/`data-preparation.md`/`data-model.md`/`quickstart.md`/a contract file, containing `- [ ]`/`- [x]`/`- [X]` items). Show a status table (Checklist | Total | Checked | Unchecked | Status). Never modify these files. If any has unchecked items, **stop** and ask "Some checklists have unchecked items. Proceed with implementation anyway?" — only continue on explicit yes.

### 7b. Evaluation Gate (read-only, independent of 7a)

If `plan.md` has an Evaluation Gate: locate the Evaluation phase in `tasks.md` — it must be `[X]` with its recorded result meeting every metric/threshold row. Show a status table (Metric | Threshold | Recorded Result | Status). If not yet run or failing, **stop before any Deployment-phase task** and ask "The Evaluation Gate hasn't passed. Proceed to deployment anyway?" — only continue on explicit yes. Non-deployment phases may proceed regardless.

### 7c. Verify Project Setup

Check for the ignore files the detected stack needs (`.gitignore` if a git repo, `.dockerignore` if Docker's involved, `.eslintignore`/`.prettierignore`/`.terraformignore`/`.helmignore` as applicable) and top up missing critical patterns — never blindly overwrite an existing file.

### 7d. Execute Phase by Phase

Complete each phase fully before the next. Sequential tasks in order; `[P]` tasks in the same phase may run together, but tasks touching the same file run sequentially regardless of markers. Order within a phase: setup/init → tests (if any, TDD-style, must fail first) → models → services → endpoints/UI → integration → polish. **Modeling tasks**: record the actual metric against the stated Accept/Reject clause; on Reject, follow the named fallback task instead of proceeding — this is the CRISP-ML(Q) backward loop, not a failure to halt on. **Evaluation phase**: run in full, record every metric against `plan.md`'s Evaluation Gate table before touching any Deployment task.

### 7e. Track Progress

Report after each completed task. Mark each `[X]` in `tasks.md` as you finish it. On a non-parallel failure, halt and report with debugging context. On a `[P]` failure, continue the rest of the batch and report the failure at the end of it.

### 7f. Validate Completion

Confirm every task is `[X]`, the implementation matches `spec.md`, the Evaluation Gate passed (or was explicitly overridden), and tests pass where applicable.

### 7g. Update the Epic (conditional)

If `spec.md` has an `Epic` field and 7f confirmed full completion: open that epic's `epic.md`, find the row whose Status cell links to this feature's `spec.md` (match by link, not name), flip Status to `Implemented`. Don't touch anything else — phase reports are `sdd-backlog`'s job. Note in Step 8 if this was the last row in its phase.

## Step 8: Closing

Report final status: completed work, any incomplete tasks and why, test results, follow-ups needed. Generate a short model/experiment summary (skip if confirmed non-ML): approaches tried in Modeling/Experimentation, final metrics vs. Evaluation Gate thresholds, where logged. If 7g flipped an epic row, say so, and if it was the phase's last row, recommend re-running `sdd-backlog` against that epic to generate the phase's completion report.
