---
name: sdd-plan
description: Generates the technical implementation plan (data pipeline, model approach, evaluation gate, deployment target) for a feature from its spec and the project constitution, at .spec/[feature-dir]/plan.md. CRISP-ML(Q)-native — Technical Context and artifacts cover Data Preparation and Modeling; falls back to a plain stack/architecture plan when no model/data is involved.
user_invocable: true
---

# Implementation Plan Generator (Technical Plan)

This skill guides Claude to act as a Senior ML/Software Architect. The goal is to turn a feature specification (what/why) into a concrete technical plan — data pipeline, modeling approach, evaluation gate, deployment target — validated against the project's non-negotiable constitution.

**Position in the SDD pipeline**: Specify → Clarify (optional) → **Plan** → Checklist (optional) → Tasks. Required input: `.spec/[feature-dir]/spec.md` and `.spec/constitution.md`. Output: `.spec/[feature-dir]/plan.md` plus, when relevant, `research.md`, `data-preparation.md`, `data-model.md`, one or more contract files, and `quickstart.md` in the same directory — consumed next by `sdd-tasks`.

**Default assumption**: the feature trains, fine-tunes, or prompts a model. If the spec explicitly scoped itself as non-ML (see `sdd-specify`), skip the ML-specific Technical Context fields and the Evaluation Gate, and plan as a traditional software feature instead.

---

## Step 1: Load Context

1. Identify the feature: if the user doesn't specify one, look in `.spec/` for the most recent feature directory (one containing a `spec.md`) without a `plan.md`, or ask.
2. Read `.spec/[feature-dir]/spec.md` (required — without it, stop and ask the user to run `sdd-specify` first).
3. Read `.spec/constitution.md` (required for the Constitution Check). If it doesn't exist, warn the user there's no governance gate defined and suggest running `sdd-constitution`; you may proceed without it, but say so explicitly in the plan.
4. If `spec.md` has an `Epic` back-reference, read that epic's `shared-data-model.md` if it exists — its entities are binding for Step 5's `data-model.md` (see below).

## Step 2: Fill the Technical Context

Fill every Technical Context field with real evidence, never assumption — the same fidelity-to-evidence rule used across this pipeline:

- Where a stack, data pipeline, or model already exists (dependency manifests, notebooks, training scripts, an existing directory tree), inspect it directly and treat what you find as binding, not optional.
- Where nothing is decided yet, whatever the constitution already fixes (e.g. a mandatory experiment-tracking tool, a mandatory eval protocol) is binding. For the rest, ask the user directly (via `AskUserQuestion` or short question blocks) — don't choose the data source, model approach, or stack unilaterally.
- Anything still open after asking becomes an explicit `NEEDS CLARIFICATION` in the document — never a silent assumption.

## Step 3: Generate `plan.md`

Write `.spec/[feature-dir]/plan.md` following this structure:

```markdown
# Implementation Plan: [FEATURE]

**Branch**: `[feature-dir]` | **Date**: [DATE] | **Spec**: .spec/[feature-dir]/spec.md

## Summary

[Primary requirement extracted from the spec + technical/modeling approach in 2-3 sentences]

## Technical Context

**Language/Version**: [...]
**Primary Dependencies**: [ML/serving frameworks, libraries]
**Data Sources & Pipeline**: [where training/inference data comes from, how it's ingested/refreshed]
**Feature Engineering**: [key transforms/features, or "N/A — raw input to model/prompt"]
**Model Architecture Candidates**: [baseline + candidate approaches to try, or "N/A" for non-ML]
**Training Infra/Compute**: [where training runs, compute ceiling, or "N/A"]
**Experiment Tracking Tool**: [tool mandated by constitution, or chosen here — never skip if the constitution requires one]
**Evaluation Protocol**: [split strategy, metrics, statistical test used to accept/reject a model]
**Storage**: [...or N/A]
**Testing**: [test types for non-model code: unit/integration/contract]
**Deployment Target**: [batch / online real-time / edge / shadow deployment]
**Monitoring & Retraining Triggers**: [high-level signals and thresholds; full detail deferred to sdd-monitor after implementation]
**Target Platform**: [...]
**Project Type**: [single project / web app / mobile+api / cli / lib / other]
**Performance Goals**: [latency/throughput, ...or NEEDS CLARIFICATION]
**Constraints**: [...or NEEDS CLARIFICATION]
**Scale/Scope**: [...or NEEDS CLARIFICATION]

## Constitution Check

*Gate: must pass before detailing the project structure below.*

| Principle (.spec/constitution.md) | Assessment | Note |
|---|---|---|
| [Principle name] | Pass / Violation | [justification if Violation] |

If any `Violation` lacks an acceptable justification, **do not proceed** — go back to the spec or the technical design until it's resolved, or record the exception in Complexity Tracking below with explicit rationale.

## Evaluation Gate

*Gate: the thresholds a model/prompt must clear before any Deployment-phase task in `tasks.md` may run. Omit this section entirely only for a confirmed non-ML feature.*

| Metric | Threshold | Eval Set | Source |
|---|---|---|---|
| [e.g. F1] | [e.g. ≥ 0.85] | [e.g. held-out test set, n=2,000] | [spec.md Success Criteria SC-00N] |

These thresholds must match the Model/ML Metrics in `spec.md`'s Success Criteria — carry them over verbatim, don't restate them differently.

## Project Structure

### Documentation (this feature)

```text
.spec/[feature-dir]/
├── plan.md
├── spec.md
├── research.md            # if any NEEDS CLARIFICATION item needs resolving
├── data-preparation.md    # if the feature involves a non-trivial data pipeline
├── data-model.md          # if the feature involves meaningful data entities
├── <contract-name>.md     # one flat file per interface contract, if the feature exposes one — no contracts/ subfolder
├── quickstart.md          # runnable validation scenarios proving the feature works end-to-end
├── tasks.md               # generated later by sdd-tasks
└── monitoring.md          # generated later by sdd-monitor
```

### Source Code (repository root)

[The REAL, concrete directory tree — never leave generic labels like "Option 1/2/3" in the final result. In an existing codebase, reflect the layout already in place; in a new one, use the layout decided in the Technical Context.]

**Structure Decision**: [1-2 sentences justifying the chosen structure]

## Complexity Tracking

> Fill in ONLY if the Constitution Check recorded a violation above.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|---------------------------------------|
| [...] | [...] | [...] |
```

## Step 4: Phase 0 — Research (conditional)

If any `NEEDS CLARIFICATION` remains in the Technical Context, generate `research.md`:

1. For each unknown, dispatch a research task ("Research {unknown} for {feature context}"); for each technology or modeling choice, a best-practices task ("Find best practices for {approach} in {domain}").
2. Consolidate findings using the format: `Decision` / `Rationale` / `Alternatives considered`.

The final `plan.md` must not contain any `NEEDS CLARIFICATION` without a corresponding resolved entry here.

## Step 5: Phase 1 — Design & Contracts (conditional)

Prerequisite: `research.md` complete (if it was needed).

1. **`data-preparation.md`**: if the spec's Business & Data Understanding section is non-trivial, document data sourcing, the versioning scheme (e.g. DVC/lakeFS revision or snapshot policy), the train/validation/test split strategy (and why — random vs. temporal vs. grouped), and leakage checks (e.g. no future information, no duplicate entities across splits).
2. **`data-model.md`**: if the spec has a non-trivial "Key Entities" section, extract entity names, fields, relationships, and validation/state-transition rules derived from the functional requirements. If the feature belongs to an epic with a `shared-data-model.md`, do not redefine entities already documented there — reference them by name and only document feature-local entities here.
3. **Contract file(s)**: if the project exposes an interface to users or other systems (prediction API, batch-scoring contract, prompt/response schema, CLI), document it as a flat file directly in the feature directory (e.g. `artifact-schemas.md`, `openapi.yaml`) — no `contracts/` subfolder. One file per contract; pick a name that doesn't collide with another artifact already in the directory. Skip for purely internal/offline projects.
4. **`quickstart.md`**: a runnable validation guide proving the feature works end-to-end — prerequisites, setup commands, run/train/eval commands, expected outcomes. Reference the contract file(s), `data-model.md`, and `data-preparation.md` instead of duplicating them. Do not include full implementation code or complete test suites — that belongs in `tasks.md` and the implementation phase itself.

## Step 6: Closing

Report to the user: the `plan.md` path, the Constitution Check result (pass/violations), the Evaluation Gate thresholds (or why it was omitted), any auxiliary artifacts generated, and the suggested next step (`sdd-checklist` if a requirements-quality pass on a specific domain is warranted, otherwise `sdd-tasks` to break the plan into actionable tasks).
