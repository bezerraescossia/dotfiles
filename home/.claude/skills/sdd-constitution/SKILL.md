---
name: sdd-constitution
description: Creates or updates the project constitution (non-negotiable governance and development principles) at .spec/constitution.md, inferring from existing code/docs where possible and asking the user for anything that can't be inferred. CRISP-ML(Q)-native by default (reproducibility, experiment tracking, model risk, data governance); falls back to traditional software categories when the project evidence shows it isn't an ML/LLM project.
user_invocable: true
---

# Project Constitution Generator (Governance & Development Guidelines)

This skill guides Claude to act as a Staff ML Engineer responsible for defining a project's technical governance principles. The goal is to produce (or amend) `.spec/constitution.md`: a small, non-negotiable set of principles that will guide — and act as a validation gate for — all subsequent development.

**Position in the SDD pipeline**: runs first, standalone, before any epic or feature work (`sdd-backlog`, `sdd-implement`). Those skills check `.spec/constitution.md` for conflicts but don't hard-require it to exist — if it's missing, they warn and suggest running this skill first, then proceed anyway. Output: `.spec/constitution.md`.

There is no separate "brownfield" or "greenfield" procedure here. The process is always the same: pull in whatever real evidence the project already offers, and ask the user directly for anything that evidence can't answer. A brand-new repository just means there's less to infer — not a different flow.

**Default assumption**: this pipeline is CRISP-ML(Q)-native — it assumes the project trains, fine-tunes, prompts, or otherwise ships a model/LLM-backed system unless the evidence says otherwise. Treat a plain software project as the edge case: fall back to it only when the repository shows no ML signal (no model artifacts, training code, prompts, notebooks, experiment-tracking config, or ML/LLM framework dependencies) and the user confirms there's no model involved.

## Directory conventions

Everything the SDD pipeline produces lives under one folder, `.spec/`. This skill only ever writes `.spec/constitution.md`, but the full layout (relevant to the other two `sdd-*` skills too) is:

- `.spec/constitution.md` — the project's governance principles, global, persists across features and epics.
- `.spec/NN-epic-name/` — one directory per **epic**, `NN` zero-padded to 2 digits. Contains `epic.md` and, when warranted, `shared-data-model.md`, plus `reports/<phase-name>-report.md`.
- `.spec/NN-epic-name/[phase][nn]-feature-name/` — one directory per **feature that belongs to an epic**, nested under that epic, named after its Feature Backlog ID (e.g. `dp01-document-parse`).
- `.spec/00NNN-feature-name/` — one directory per **standalone feature** (no epic), flat at the `.spec/` root, `NNN` zero-padded to 3 digits.
- Either kind of feature directory contains `spec.md`, `plan.md`, `tasks.md`, plus optional artifacts and flat checklist/contract files — no subfolders.

---

## Step 1: Gather Context

1. Check whether `.spec/constitution.md` already exists — if so, this is an **amendment** (see Step 4 — Versioning), regardless of how much code exists.
2. Look for existing signal in the repository: README files, linter/formatter configs, CI pipelines, test setup, existing code conventions, package manifests, notebooks, training scripts, model artifacts (`.pkl`, `.pt`, `.onnx`, ...), experiment-tracking config (MLflow, W&B, Comet), data-versioning config (DVC, lakeFS), prompt/eval directories. This is opportunistic — an empty repository simply yields no signal here.
3. From real evidence only (never invention), draft candidate principles covering, for example:
   - Reproducibility posture already in practice (pinned seeds, pinned environments, data versioning in use)
   - Experiment-tracking tool already adopted, and what it logs
   - Testing/evaluation posture already in practice (eval harness present? held-out sets? CI running evals?)
   - Predominant architectural style (layering, module boundaries, couplings to preserve or avoid)
   - Simplicity/complexity conventions (e.g. preference for plain libraries, avoidance of premature abstraction)
   - Data governance, privacy, or compliance requirements already visible in the system
4. Mark every inference explicitly as a **hypothesis** when presenting it to the user — never write an unconfirmed hypothesis into the constitution as settled fact.

## Step 2: Fill the Gaps by Asking

For anything the repository can't answer (which, in a new project, may be everything), interview the user in short, iterative blocks — 3-5 questions per turn, most-blocking first.

If the project is (or will be) ML/LLM-backed — the default assumption — cover at least:

1. **Reproducibility**: Is a seed/determinism policy mandatory? Is a data-versioning tool required (DVC, lakeFS, plain object-storage snapshots)? Must environments be pinned (lockfiles, containers)?
2. **Experiment tracking**: Which tool is mandatory (MLflow, Weights & Biases, Comet, none)? What must every run log — hyperparameters, metrics, artifacts, data lineage?
3. **Model risk & responsible AI**: Is a fairness/bias review required before shipping a model? What's the human-in-the-loop fallback policy for low-confidence predictions? Are explainability requirements (e.g. SHAP, feature attribution) mandatory?
4. **Data governance & privacy**: Any PII handling, retention, access-control, or regulatory (GDPR/HIPAA/etc.) requirements the data pipeline must satisfy?
5. **Evaluation rigor**: What's the minimum acceptable eval protocol (held-out test set, cross-validation, statistical-significance testing) before anything can be marked ready to deploy?
6. **Versioning & rollback**: How are models/prompts versioned? Is shadow deployment or a rollback path mandatory before full rollout?

If the user confirms this is a traditional, non-ML project, fall back to the classic categories instead:

1. **Testing**: Is TDD mandatory (non-negotiable) or optional/pragmatic? Which test types are expected (unit, contract, integration)?
2. **Architecture**: Any preferred style (library-first, modular monolith, microservices, CLI-first)? Coupling constraints?
3. **Simplicity**: Appetite for upfront abstraction vs. YAGNI? Any hard complexity ceiling (e.g. number of projects/services)?
4. **Observability**: Are structured logging, tracing, and metrics mandatory from day one?
5. **Versioning & compatibility**: How should breaking changes be handled?
6. **Security & compliance**: Any non-negotiable regulatory, auth, or data-protection requirements?

Present the resulting principles — inferred and interviewed alike — to the user in short blocks (3-5 at a time), asking for confirmation, edits, or removal. Do not write anything to `.spec/constitution.md` before that confirmation.

## Step 3: Write the Document

Read `CONSTITUTION-TEMPLATE.md` for the exact structure and content rules, then write (or amend) `.spec/constitution.md` following it precisely.

## Step 4: Semantic Versioning (for amendments to an existing constitution)

If `.spec/constitution.md` already exists, when updating it:

1. Determine the bump type by comparing against the previous version:
   - **MAJOR**: removal or backward-incompatible redefinition of an existing principle.
   - **MINOR**: a new principle or section added, or material expansion of an existing guideline.
   - **PATCH**: clarification, wording fix, non-semantic adjustment.
   - If the bump type is ambiguous, explain the reasoning to the user before finalizing.
2. Update `Last Amended` to today's date; keep `Ratified` as the original date.
3. Prepend the Sync Impact Report (see `CONSTITUTION-TEMPLATE.md`) as an HTML comment at the top of the file.

## Step 5: Closing

Report to the user:
- The file path (`.spec/constitution.md`), the new version, and the bump rationale (if an amendment).
- Any pending `TODO(...)` that needs a manual decision.
- A suggested next step: run `sdd-backlog` to declare the first epic or feature under the new constitution.
