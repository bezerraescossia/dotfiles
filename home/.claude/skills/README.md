# Spec-Driven Development (SDD) Pipeline — CRISP-ML(Q)-native

Three skills that take a project — new or existing — from "no formal spec" to "implemented feature," mirroring [github/spec-kit](https://github.com/github/spec-kit)'s command set (`/speckit.constitution`, `/speckit.specify`, `/speckit.clarify`, `/speckit.plan`, `/speckit.checklist`, `/speckit.tasks`, `/speckit.analyze`, `/speckit.implement`) plus one addition, Epic:

1. **[`sdd-constitution`](./sdd-constitution/SKILL.md)** — establishes (or amends) the project's non-negotiable governance principles. Standalone, runs first. → `.spec/constitution.md`
2. **[`sdd-backlog`](./sdd-backlog/SKILL.md)** — turns an epic idea into a dependency-ordered feature backlog, then specifies and clarifies each feature in it, one at a time with a pause for review between each (also handles a standalone one-off feature with no epic). → `.spec/NN-epic-name/epic.md` + every feature's `spec.md`
3. **[`sdd-implement`](./sdd-implement/SKILL.md)** — takes one feature, user-declared, from technical plan through working code: Plan, an optional on-demand Checklist, Tasks, a read-only Analyze pass, and Implement. Resumes from whatever's already on disk. → `plan.md`, `tasks.md`, and the actual implementation

Each skill keeps its own `*-TEMPLATE.md` files, flat at its own top level next to `SKILL.md` (same convention as [`teach`](./teach/SKILL.md)'s `*-FORMAT.md` files), and its own copy of the `.spec/` directory conventions below — they're self-contained, not cross-referencing each other's files.

The pipeline is **CRISP-ML(Q)-native by default**: it assumes each feature involves training, fine-tuning, prompting, or otherwise shipping a model/LLM-backed system, and structures every stage around [CRISP-ML(Q)](https://arxiv.org/abs/2003.05155)'s six phases (Business & Data Understanding, Data Preparation, Modeling, Evaluation, Deployment, Monitoring & Maintenance) — including its hallmark quality-assurance mechanism, an explicit Risk Assessment carried through every artifact. A plain software feature with no model or data involved is the supported edge case: say so explicitly in the spec, and the ML-specific sections (Risk Assessment, Evaluation Gate, Data Preparation) are omitted rather than forced. There is no post-deployment monitoring stage — CRISP-ML(Q)'s Monitoring & Maintenance phase is intentionally out of scope for this pipeline.

The artifact hierarchy is **Epic → Feature → User Stories → Acceptance Scenarios / Success Criteria**: a multi-feature effort (e.g. "recommendation system", "RAG system") is declared once with `sdd-backlog`'s epic sub-stage, which drafts a dependency-ordered feature backlog organized by CRISP-ML(Q) phase; each backlog entry then gets its own spec (via the same skill) and its own plan → tasks → implement cycle (via `sdd-implement`). A one-off feature with no larger epic behind it can skip straight to `sdd-backlog` in standalone-feature mode.

## Why three skills, not ten (or one)

The pipeline used to be ten separate skills, each fully self-contained but re-deriving the same "which feature directory am I in, what's already done?" logic independently, with no shared view of where a feature stood in the pipeline. A single monolithic skill fixed that but blurred a real seam: *deciding and specifying* a backlog is a different mode of work from *building* one feature at a time — different pacing, different review points, done on different days. The three-way split follows that seam:

- `sdd-constitution` is genuinely global and rarely touched — its own skill, checked (not re-run) by the other two.
- `sdd-backlog` covers everything that happens before any code gets written for a feature: scoping the epic, and specifying + clarifying each feature in priority order, pausing for review after each one rather than bulk-generating the whole backlog unsupervised.
- `sdd-implement` covers everything that happens for one feature, start to finish, once its spec exists — resuming from disk state (an existing `plan.md`/`tasks.md` means that step is skipped), pausing once after Plan to show the Constitution Check and Evaluation Gate before Tasks are generated, and gating on checklist completion and the Evaluation Gate the same way the original pipeline did.

## Directory conventions

Everything lives under one folder, `.spec/`:

- `.spec/constitution.md` — the project's governance principles, global, persists across features and epics.
- `.spec/NN-epic-name/` — one directory per **epic**, e.g. `01-rag-system`, `02-fraud-detection`. `NN` is its own counter, zero-padded to 2 digits (`01`, `02`, ... `99`). Contains `epic.md` (objective, Constitution Check, CRISP-ML(Q)-phase-organized feature backlog, sequencing) and, when the epic has genuinely shared entities, `shared-data-model.md`, plus `reports/<phase-name>-report.md` once a phase's backlog is fully implemented.
- `.spec/NN-epic-name/[phase][nn]-feature-name/` — one directory per **feature that belongs to an epic**, nested directly under that epic's directory, e.g. `01-rag-system/bdu01-corpus-scoping`, `01-rag-system/dp01-document-parse`. `[phase][nn]` is that feature's own Feature Backlog ID from `epic.md` (`bdu`/`dp`/`mod`/`eval`/`deploy`/`mon`), lowercased, with its number zero-padded to 2 digits — a counter local to that phase code *within this epic* (`bdu01`, `bdu02`, `dp01`, ...), matching `epic.md`'s ID exactly.
- `.spec/00NNN-feature-name/` — one directory per **standalone feature** (no epic), e.g. `00211-churn-prediction`, flat at the `.spec/` root. `00` marks it standalone; `NNN` is a counter local to standalone features, zero-padded to 3 digits.
- Either kind of feature directory contains `spec.md`, `plan.md`, `tasks.md`, and, when relevant, `research.md` / `data-preparation.md` / `data-model.md` / `quickstart.md` — plus, as flat sibling files with no subfolder, `requirements.md` (built-in spec-quality checklist), any custom checklist (reviewer-owned — e.g. `ux.md`, `security.md`, `data-quality.md`, `fairness.md`), and any interface contract (e.g. `artifact-schemas.md`). Every artifact for a feature lives directly in its own feature directory — no `checklists/` or `contracts/` subfolder. Pick a name for a new checklist or contract file that doesn't collide with another artifact already in the same directory.
- Elsewhere in these skill docs, `.spec/[feature-dir]/` is shorthand for a feature directory named per either convention above.

## Pipeline

```
sdd-constitution → sdd-backlog (Epic + Specify + Clarify, per feature) → sdd-implement (Plan + Checklist + Tasks + Analyze + Implement, per feature)
   (once)              re-run to add features or generate phase reports         re-run per feature; resumes from disk state
```

## Other skills

- [`teach`](./teach/SKILL.md) — teach the user a new skill or concept within a stateful workspace (mission, lessons, reference docs, learning records).
- [`grilling`](./grilling/SKILL.md) — grill the user relentlessly about a plan, decision, or idea.
