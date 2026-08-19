---
name: sdd-constitution
description: Creates or updates the project constitution (non-negotiable governance and development principles) at .spec/constitution.md, inferring from existing code/docs where possible and asking the user for anything that can't be inferred. CRISP-ML(Q)-native by default (reproducibility, experiment tracking, model risk, data governance); falls back to traditional software categories when the project evidence shows it isn't an ML/LLM project.
user_invocable: true
---

# Project Constitution Generator (Governance & Development Guidelines)

This skill guides Claude to act as a Staff ML Engineer responsible for defining a project's technical governance principles. The goal is to produce (or amend) `.spec/constitution.md`: a small, non-negotiable set of principles that will guide — and act as a validation gate for — all subsequent development (specs, plans, and tasks).

**Position in the SDD pipeline**: Constitution is the foundation of the pipeline. It runs first, before `sdd-specify`, and every spec, plan, and task list generated afterward must comply with it. Output: `.spec/constitution.md`.

There is no separate "brownfield" or "greenfield" procedure here. The process is always the same: pull in whatever real evidence the project already offers, and ask the user directly for anything that evidence can't answer. A brand-new repository just means there's less to infer — not a different flow.

**Default assumption**: this pipeline is CRISP-ML(Q)-native — it assumes the project trains, fine-tunes, prompts, or otherwise ships a model/LLM-backed system unless the evidence says otherwise. Treat a plain software project as the edge case: fall back to it only when the repository shows no ML signal (no model artifacts, training code, prompts, notebooks, experiment-tracking config, or ML/LLM framework dependencies) and the user confirms there's no model involved.

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

## Step 3: Document Structure

Write (or amend) `.spec/constitution.md` following strictly this structure (based on spec-kit's `constitution-template.md`):

```markdown
# [PROJECT NAME] Constitution

## Core Principles

### [PRINCIPLE_1_NAME]
[Non-negotiable rule in 1-2 sentences + rationale for why it exists, if not obvious]

### [PRINCIPLE_2_NAME]
...

## [EXTRA SECTION, e.g. Data Governance / Model Risk & Responsible AI / Evaluation Standards / Technology Constraints]

[Content — include extra sections only when they make sense for this project; don't force a fixed count]

## Development Workflow

[Code review requirements, quality gates, approval process — if applicable]

## Governance

[Amendment process: who approves, how to version, compliance-review expectations for future specs/plans/tasks]

**Version**: [X.Y.Z] | **Ratified**: [DATE] | **Last Amended**: [DATE]
```

Content rules:
- Every principle must be **declarative and testable** (use MUST/SHOULD/MUST NOT, not "should ideally"). If a principle can't be objectively verified during a spec/plan review, rewrite it.
- Don't force a fixed number of principles — use as many as the user considers essential (typically 3-7). A few strong principles beat many generic ones.
- Fields that can't be resolved (e.g. an unknown ratification date in an existing project) become `TODO(FIELD): explanation`, never an invented value.

---

## Step 4: Semantic Versioning (for amendments to an existing constitution)

If `.spec/constitution.md` already exists, when updating it:

1. Determine the bump type by comparing against the previous version:
   - **MAJOR**: removal or backward-incompatible redefinition of an existing principle.
   - **MINOR**: a new principle or section added, or material expansion of an existing guideline.
   - **PATCH**: clarification, wording fix, non-semantic adjustment.
   - If the bump type is ambiguous, explain the reasoning to the user before finalizing.
2. Update `Last Amended` to today's date; keep `Ratified` as the original date.
3. Prepend, as an HTML comment at the top of the file, a **Sync Impact Report**:
   ```html
   <!--
   Sync Impact Report
   Version change: [X.Y.Z] → [X.Y.Z]
   Modified principles: [list, or "none"]
   Added sections: [list, or "none"]
   Removed sections: [list, or "none"]
   Follow-up TODOs: [list, or "none"]
   -->
   ```

---

## Step 5: Closing

Report to the user:
- The file path (`.spec/constitution.md`), the new version, and the bump rationale (if an amendment).
- Any pending `TODO(...)` that needs a manual decision.
- A suggested next step: run `sdd-specify` for the first feature under the new constitution.
