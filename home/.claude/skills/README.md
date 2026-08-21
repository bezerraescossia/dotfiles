# Spec-Driven Development (SDD) Pipeline — CRISP-ML(Q)-native

Ten skills that take a project — new or existing — from "no formal spec" to "implemented and monitored feature," mirroring [github/spec-kit](https://github.com/github/spec-kit)'s command set (`/speckit.constitution`, `/speckit.specify`, `/speckit.clarify`, `/speckit.plan`, `/speckit.checklist`, `/speckit.tasks`, `/speckit.analyze`, `/speckit.implement`) plus two additions, `sdd-epic` and `sdd-monitor`.

The pipeline is **CRISP-ML(Q)-native by default**: it assumes each feature involves training, fine-tuning, prompting, or otherwise shipping a model/LLM-backed system, and structures every stage around [CRISP-ML(Q)](https://arxiv.org/abs/2003.05155)'s six phases (Business & Data Understanding, Data Preparation, Modeling, Evaluation, Deployment, Monitoring & Maintenance) — including its hallmark quality-assurance mechanism, an explicit Risk Assessment carried through every artifact. A plain software feature with no model or data involved is the supported edge case: say so explicitly in the spec, and the ML-specific sections (Risk Assessment, Evaluation Gate, Data Preparation, drift monitoring) are omitted rather than forced.

The artifact hierarchy is **Epic → Feature → User Stories → Acceptance Scenarios / Success Criteria**: a multi-feature effort (e.g. "recommendation system", "RAG system") is declared once with `sdd-epic`, which drafts a dependency-ordered feature backlog organized by CRISP-ML(Q) phase (see below); each backlog entry then gets its own full spec → plan → tasks → implement → monitor cycle via `sdd-specify` onward. A one-off feature with no larger epic behind it can skip straight to `sdd-specify`.

spec-kit itself has no separate brownfield/greenfield pipeline — "Iterative Enhancement" (brownfield) is just the same commands run again against an existing codebase, not a different flow. These skills follow that: there's one pipeline, and `sdd-constitution`/`sdd-epic`/`sdd-plan` simply use whatever real evidence the repository already offers (existing code, data, models, configs, conventions) instead of asking the user to redecide it, falling back to direct questions only for what can't be inferred.

## Directory conventions

Everything lives under one folder, `.spec/`:

- `.spec/constitution.md` — the project's governance principles, global, persists across features and epics.
- `.spec/NN-epic-name/` — one directory per **epic**, e.g. `01-rag-system`, `02-fraud-detection`. `NN` is its own counter, zero-padded to 2 digits (`01`, `02`, ... `99`). Contains `epic.md` (objective, Constitution Check, CRISP-ML(Q)-phase-organized feature backlog, sequencing) and, when the epic has genuinely shared entities, `shared-data-model.md`, plus `reports/<phase-name>-report.md` once a phase's backlog is fully implemented.
- `.spec/NN-epic-name/[phase][nn]-feature-name/` — one directory per **feature that belongs to an epic**, nested directly under that epic's directory, e.g. `01-rag-system/bdu01-corpus-scoping`, `01-rag-system/dp01-document-parse`. `[phase][nn]` is that feature's own Feature Backlog ID from `epic.md` (`bdu`/`dp`/`mod`/`eval`/`deploy`/`mon`), lowercased, with its number zero-padded to 2 digits — a counter local to that phase code *within this epic* (`bdu01`, `bdu02`, `dp01`, ...), matching `epic.md`'s ID exactly.
- `.spec/00NNN-feature-name/` — one directory per **standalone feature** (no epic), e.g. `00211-churn-prediction`, flat at the `.spec/` root. `00` marks it standalone; `NNN` is a counter local to standalone features, zero-padded to 3 digits.
- Either kind of feature directory contains `spec.md`, `plan.md`, `tasks.md`, and, when relevant, `research.md` / `data-preparation.md` / `data-model.md` / `quickstart.md` / `monitoring.md` — plus, as flat sibling files with no subfolder, `requirements.md` (built-in spec-quality checklist), any custom checklist (reviewer-owned — e.g. `ux.md`, `security.md`, `data-quality.md`, `fairness.md`), and any interface contract (e.g. `artifact-schemas.md`). Every artifact for a feature lives directly in its own feature directory — no `checklists/` or `contracts/` subfolder. Pick a name for a new checklist or contract file that doesn't collide with another artifact already in the same directory.
- Elsewhere in these skill docs, `.spec/[feature-dir]/` is shorthand for a feature directory named per either convention above.

## Pipeline

```
sdd-constitution → sdd-epic → sdd-specify → sdd-clarify → sdd-plan → sdd-checklist → sdd-tasks → sdd-analyze → sdd-implement → sdd-monitor
                    (optional)               (optional)                (optional)                (optional)                    (optional)
```

CRISP-ML(Q) phase vocabulary shows up at two distinct, non-conflicting levels — don't conflate them:

- **Epic-level (the backlog itself)**: `sdd-epic` organizes the *features it drafts* into CRISP-ML(Q)'s six phases (Business & Data Understanding → Data Preparation → Modeling → Evaluation → Deployment → Monitoring & Maintenance), one subsection per phase, each with its own requirements/constraints, a Feature Backlog table, and a risk-driven QA table (every infeasible risk gets its own trackable `QA`-typed backlog row). Re-invoking `sdd-epic` against an existing epic generates a completion report for any phase whose backlog is fully implemented. This is *what CRISP-ML(Q) actually structures* in this pipeline.
- **Single-feature level (internal task organization)**: independent of which epic-phase bucket a feature was filed under, every feature still runs the full `sdd-specify` → `sdd-clarify` → `sdd-plan` → `sdd-checklist` → `sdd-tasks` → `sdd-analyze` → `sdd-implement` → `sdd-monitor` pipeline end to end. `sdd-tasks` happens to name its own internal phases after CRISP-ML(Q) too (Data Preparation, Modeling/Experimentation, Evaluation, Deployment, Monitoring Setup) purely as a task-organizing convention *within that one feature's `tasks.md`* — this is unrelated to, and does not mean, "this whole pipeline stage equals one epic-level phase."

1. **sdd-constitution** establishes (or amends) the project's non-negotiable governance principles — for ML projects: reproducibility, experiment tracking, model risk/responsible AI, data governance, evaluation rigor, versioning & rollback → `.spec/constitution.md`. Runs first; everything downstream must comply with it.
2. **sdd-epic** *(optional, for multi-feature efforts)* declares an epic (e.g. "recommendation system") and drafts its CRISP-ML(Q)-phase-organized feature backlog — including risk-driven QA features per phase — plus a shared cross-feature data model when warranted → `.spec/NN-epic-name/epic.md` (+ `shared-data-model.md`). Re-invoking it against an existing epic instead generates a completion report for any phase whose backlog is fully implemented → `.spec/NN-epic-name/reports/<phase-name>-report.md`. Skip straight to `sdd-specify` for a one-off feature.
3. **sdd-specify** turns a natural-language feature description into a structured spec: Business & Data Understanding, user stories, functional requirements, a mandatory Risk Assessment, and Success Criteria split into Business KPIs and Model/ML Metrics → `.spec/[feature-dir]/spec.md`. If the feature belongs to an epic, picks up its context and shared entities automatically and checks the backlog row off as `Specified`.
4. **sdd-clarify** *(optional but recommended)* asks up to 5 targeted questions — scanning an ML-first taxonomy (data availability, evaluation protocol, drift, fairness, compute budget) alongside the classic functional/UX one — to resolve ambiguity before planning starts, and writes the answers back into the spec.
5. **sdd-plan** defines the feature's data pipeline, modeling approach, and Evaluation Gate, validated against the constitution → `.spec/[feature-dir]/plan.md` (+ `research.md`/`data-preparation.md`/`data-model.md`/a contract file/`quickstart.md` as needed).
6. **sdd-checklist** *(optional, can run any time after step 3)* generates a domain-specific "unit tests for English" checklist — validates requirement quality, not implementation. Domains span classic areas (UX, API, security) and ML-specific ones (data quality, fairness, evaluation rigor).
7. **sdd-tasks** breaks the plan into dependency-ordered tasks organized by CRISP-ML(Q) phase (Data Preparation → Modeling/Experimentation → Evaluation → Deployment → Monitoring Setup), with explicit accept/reject criteria and backward-loop fallbacks on every modeling task → `.spec/[feature-dir]/tasks.md`.
8. **sdd-analyze** *(optional, read-only)* cross-checks spec/plan/tasks for inconsistencies, gaps, Evaluation Gate mismatches, and constitution violations before implementation starts.
9. **sdd-implement** executes `tasks.md` phase by phase, gating on both checklist completion and the Evaluation Gate before any deployment task runs, and produces the actual code/pipeline/model.
10. **sdd-monitor** *(optional, strongly recommended for anything deployed)* generates the post-launch monitoring plan — drift signals, retraining triggers, alerting, rollback runbook — → `.spec/[feature-dir]/monitoring.md`.

## Skills

| Skill | Reads | Writes |
|---|---|---|
| `sdd-constitution` | repo context (code, data, models, configs, README) if available | `.spec/constitution.md` |
| `sdd-epic` | `.spec/constitution.md`, natural-language epic description; on re-invocation, an existing epic's `epic.md` and each completed phase feature's `spec.md`/`plan.md`/`monitoring.md` | `.spec/NN-epic-name/epic.md` (+ optional `shared-data-model.md`); on re-invocation, `.spec/NN-epic-name/reports/<phase-name>-report.md` for any newly-completed phase |
| `sdd-specify` | `.spec/constitution.md`, `.spec/NN-epic-name/epic.md` (if applicable), natural-language description | `.spec/[feature-dir]/spec.md`, `.spec/[feature-dir]/requirements.md`; updates the epic's backlog row if applicable |
| `sdd-clarify` | `.spec/[feature-dir]/spec.md` | same file, updated in place |
| `sdd-plan` | `.spec/[feature-dir]/spec.md`, `.spec/constitution.md`, epic's `shared-data-model.md` (if applicable) | `.spec/[feature-dir]/plan.md` (+ optional `research.md`/`data-preparation.md`/`data-model.md`/a contract file/`quickstart.md`) |
| `sdd-checklist` | `.spec/[feature-dir]/{spec,plan,tasks}.md` | `.spec/[feature-dir]/[domain].md` |
| `sdd-tasks` | `.spec/[feature-dir]/plan.md`, `.spec/[feature-dir]/spec.md` | `.spec/[feature-dir]/tasks.md` |
| `sdd-analyze` | `.spec/[feature-dir]/{spec,plan,tasks}.md`, `.spec/constitution.md` | nothing (read-only report) |
| `sdd-implement` | `.spec/[feature-dir]/tasks.md` and all other feature artifacts | source code, `.spec/[feature-dir]/tasks.md` (checkbox state); if the feature belongs to an epic and finishes fully, flips its row's Status to `Implemented` in `.spec/NN-epic-name/epic.md` |
| `sdd-monitor` | `.spec/[feature-dir]/plan.md`, `.spec/[feature-dir]/spec.md`, `.spec/constitution.md` | `.spec/[feature-dir]/monitoring.md` |
