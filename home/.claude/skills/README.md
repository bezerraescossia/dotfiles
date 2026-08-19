# Spec-Driven Development (SDD) Pipeline — CRISP-ML(Q)-native

Ten skills that take a project — new or existing — from "no formal spec" to "implemented and monitored feature," mirroring [github/spec-kit](https://github.com/github/spec-kit)'s command set (`/speckit.constitution`, `/speckit.specify`, `/speckit.clarify`, `/speckit.plan`, `/speckit.checklist`, `/speckit.tasks`, `/speckit.analyze`, `/speckit.implement`) plus two additions, `sdd-epic` and `sdd-monitor`.

The pipeline is **CRISP-ML(Q)-native by default**: it assumes each feature involves training, fine-tuning, prompting, or otherwise shipping a model/LLM-backed system, and structures every stage around [CRISP-ML(Q)](https://arxiv.org/abs/2003.05155)'s six phases (Business & Data Understanding, Data Preparation, Modeling, Evaluation, Deployment, Monitoring & Maintenance) — including its hallmark quality-assurance mechanism, an explicit Risk Assessment carried through every artifact. A plain software feature with no model or data involved is the supported edge case: say so explicitly in the spec, and the ML-specific sections (Risk Assessment, Evaluation Gate, Data Preparation, drift monitoring) are omitted rather than forced.

The artifact hierarchy is **Epic → Feature → User Stories → Acceptance Scenarios / Success Criteria**: a multi-feature effort (e.g. "recommendation system", "RAG system") is declared once with `sdd-epic`, which drafts the dependency-ordered feature backlog; each backlog entry then gets its own full spec → plan → tasks → implement → monitor cycle via `sdd-specify` onward. A one-off feature with no larger epic behind it can skip straight to `sdd-specify`.

spec-kit itself has no separate brownfield/greenfield pipeline — "Iterative Enhancement" (brownfield) is just the same commands run again against an existing codebase, not a different flow. These skills follow that: there's one pipeline, and `sdd-constitution`/`sdd-epic`/`sdd-plan` simply use whatever real evidence the repository already offers (existing code, data, models, configs, conventions) instead of asking the user to redecide it, falling back to direct questions only for what can't be inferred.

## Directory conventions

Everything lives under one folder, `.spec/`:

- `.spec/constitution.md` — the project's governance principles, global, persists across features and epics.
- `.spec/E<N>-epic-name/` — one directory per **epic**, e.g. `E1-rag-system`, `E2-fraud-detection`. `N` is its own counter, un-padded (`E1`, `E2`, ... `E10`, ...), separate from the feature counter below. Contains `epic.md` (objective, Constitution Check, dependency-ordered feature backlog, sequencing) and, when the epic has genuinely shared entities, `shared-data-model.md`.
- `.spec/F<NNN>-feature-name/` (standalone) or `.spec/E<N>F<NNN>-feature-name/` (belongs to epic `E<N>`) — one directory per **feature**, e.g. `F211-churn-prediction` or `E1F210-document-parse`. `NNN` is a single **global counter shared by every feature in the repo**, regardless of which epic (if any) it belongs to — zero-padded to 3 digits. Contains `spec.md`, `plan.md`, `tasks.md`, and, when relevant, `research.md` / `data-preparation.md` / `data-model.md` / `contracts/` / `quickstart.md` / `monitoring.md`, plus `checklists/requirements.md` (built-in spec-quality checklist) and `checklists/[domain].md` (custom, reviewer-owned — e.g. `ux.md`, `security.md`, `data-quality.md`, `fairness.md`).
- A feature belonging to an epic carries that epic's `E<N>` prefix in its own directory name *and* links back via its `spec.md`'s `Epic` field — it is never nested on disk under the epic's directory.
- Elsewhere in these skill docs, `.spec/[feature-dir]/` is shorthand for "whichever of the two feature-directory forms above applies to the current feature."

## Pipeline

```
sdd-constitution → sdd-epic → sdd-specify → sdd-clarify → sdd-plan → sdd-checklist → sdd-tasks → sdd-analyze → sdd-implement → sdd-monitor
                    (optional)               (optional)                (optional)                (optional)                    (optional)
```

CRISP-ML(Q) phase mapping:

| CRISP-ML(Q) phase | Pipeline stage(s) |
|---|---|
| Business & Data Understanding | `sdd-specify` |
| Data Preparation | `sdd-plan` (`data-preparation.md`) → `sdd-tasks` Data Preparation phase |
| Modeling | `sdd-plan` (Technical Context) → `sdd-tasks` Modeling/Experimentation phase |
| Evaluation | `sdd-plan` (Evaluation Gate) → `sdd-tasks` Evaluation phase → `sdd-implement` gate |
| Deployment | `sdd-plan` (Deployment Target) → `sdd-tasks` Deployment phase |
| Monitoring & Maintenance | `sdd-monitor` |

1. **sdd-constitution** establishes (or amends) the project's non-negotiable governance principles — for ML projects: reproducibility, experiment tracking, model risk/responsible AI, data governance, evaluation rigor, versioning & rollback → `.spec/constitution.md`. Runs first; everything downstream must comply with it.
2. **sdd-epic** *(optional, for multi-feature efforts)* declares an epic (e.g. "recommendation system") and drafts its dependency-ordered feature backlog, plus a shared cross-feature data model when warranted → `.spec/E<N>-epic-name/epic.md` (+ `shared-data-model.md`). Skip straight to `sdd-specify` for a one-off feature.
3. **sdd-specify** turns a natural-language feature description into a structured spec: Business & Data Understanding, user stories, functional requirements, a mandatory Risk Assessment, and Success Criteria split into Business KPIs and Model/ML Metrics → `.spec/[feature-dir]/spec.md`. If the feature belongs to an epic, picks up its context and shared entities automatically and checks the backlog row off as `Specified`.
4. **sdd-clarify** *(optional but recommended)* asks up to 5 targeted questions — scanning an ML-first taxonomy (data availability, evaluation protocol, drift, fairness, compute budget) alongside the classic functional/UX one — to resolve ambiguity before planning starts, and writes the answers back into the spec.
5. **sdd-plan** defines the feature's data pipeline, modeling approach, and Evaluation Gate, validated against the constitution → `.spec/[feature-dir]/plan.md` (+ `research.md`/`data-preparation.md`/`data-model.md`/`contracts/`/`quickstart.md` as needed).
6. **sdd-checklist** *(optional, can run any time after step 3)* generates a domain-specific "unit tests for English" checklist — validates requirement quality, not implementation. Domains span classic areas (UX, API, security) and ML-specific ones (data quality, fairness, evaluation rigor).
7. **sdd-tasks** breaks the plan into dependency-ordered tasks organized by CRISP-ML(Q) phase (Data Preparation → Modeling/Experimentation → Evaluation → Deployment → Monitoring Setup), with explicit accept/reject criteria and backward-loop fallbacks on every modeling task → `.spec/[feature-dir]/tasks.md`.
8. **sdd-analyze** *(optional, read-only)* cross-checks spec/plan/tasks for inconsistencies, gaps, Evaluation Gate mismatches, and constitution violations before implementation starts.
9. **sdd-implement** executes `tasks.md` phase by phase, gating on both checklist completion and the Evaluation Gate before any deployment task runs, and produces the actual code/pipeline/model.
10. **sdd-monitor** *(optional, strongly recommended for anything deployed)* generates the post-launch monitoring plan — drift signals, retraining triggers, alerting, rollback runbook — → `.spec/[feature-dir]/monitoring.md`.

## Skills

| Skill | Reads | Writes |
|---|---|---|
| `sdd-constitution` | repo context (code, data, models, configs, README) if available | `.spec/constitution.md` |
| `sdd-epic` | `.spec/constitution.md`, natural-language epic description | `.spec/E<N>-epic-name/epic.md` (+ optional `shared-data-model.md`) |
| `sdd-specify` | `.spec/constitution.md`, `.spec/E<N>-epic-name/epic.md` (if applicable), natural-language description | `.spec/[feature-dir]/spec.md`, `.spec/[feature-dir]/checklists/requirements.md`; updates the epic's backlog row if applicable |
| `sdd-clarify` | `.spec/[feature-dir]/spec.md` | same file, updated in place |
| `sdd-plan` | `.spec/[feature-dir]/spec.md`, `.spec/constitution.md`, epic's `shared-data-model.md` (if applicable) | `.spec/[feature-dir]/plan.md` (+ optional `research.md`/`data-preparation.md`/`data-model.md`/`contracts/`/`quickstart.md`) |
| `sdd-checklist` | `.spec/[feature-dir]/{spec,plan,tasks}.md` | `.spec/[feature-dir]/checklists/[domain].md` |
| `sdd-tasks` | `.spec/[feature-dir]/plan.md`, `.spec/[feature-dir]/spec.md` | `.spec/[feature-dir]/tasks.md` |
| `sdd-analyze` | `.spec/[feature-dir]/{spec,plan,tasks}.md`, `.spec/constitution.md` | nothing (read-only report) |
| `sdd-implement` | `.spec/[feature-dir]/tasks.md` and all other feature artifacts | source code, `.spec/[feature-dir]/tasks.md` (checkbox state) |
| `sdd-monitor` | `.spec/[feature-dir]/plan.md`, `.spec/[feature-dir]/spec.md`, `.spec/constitution.md` | `.spec/[feature-dir]/monitoring.md` |
