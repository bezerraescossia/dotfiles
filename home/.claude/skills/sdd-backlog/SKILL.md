---
name: sdd-backlog
description: Turns an epic idea (e.g. "recommendation system") or a single feature description into the full backlog of specified, clarified features — drafting the CRISP-ML(Q)-phase-organized epic backlog if it's a multi-feature effort, then walking each feature in priority order to write and clarify its spec.md, one at a time with a pause for review between each. Also handles a standalone one-off feature with no epic. Re-invoking it against an existing epic only specs whatever hasn't been spec'd yet, or generates a phase-completion report once a phase is fully implemented.
user_invocable: true
argument-hint: "<epic or feature description, or an existing epic/feature name>"
---

# Backlog Generator (Epic → Specify → Clarify)

This skill guides Claude through everything that happens *before* any technical planning: scoping a multi-feature epic into a dependency-ordered backlog (if applicable), then producing a rigorous, clarified specification for each feature in it — one at a time, pausing for the user's review after each, never all at once. It acts as a Staff ML Engineer / Product Lead for the epic-scoping part, and a senior ML Product Manager for each feature's spec.

**Position in the SDD pipeline**: after `sdd-constitution` (optional dependency — proceed with a warning if `.spec/constitution.md` is missing), before `sdd-implement`. Output: `.spec/NN-epic-name/epic.md` (+ `shared-data-model.md`, phase reports) when an epic is involved, and `.spec/[feature-dir]/spec.md` (+ `requirements.md`) for every feature it walks — each ready for `sdd-implement`.

**Default assumption**: features involve a model, a fine-tune, a prompt/LLM-backed capability, or a data pipeline unless the description clearly describes plain CRUD/UI work with no learned component. When a feature is genuinely non-ML, its spec may omit the Business & Data Understanding and Risk Assessment sections — say explicitly why, rather than leaving them blank.

## Directory conventions

Everything lives under one folder, `.spec/`:

- `.spec/constitution.md` — the project's governance principles, global, persists across features and epics. Written by `sdd-constitution`.
- `.spec/NN-epic-name/` — one directory per **epic**, e.g. `01-rag-system`, `02-fraud-detection`. `NN` is its own counter, zero-padded to 2 digits (`01`, `02`, ... `99`). Contains `epic.md` and, when the epic has genuinely shared entities, `shared-data-model.md`, plus `reports/<phase-name>-report.md` once a phase's backlog is fully implemented.
- `.spec/NN-epic-name/[phase][nn]-feature-name/` — one directory per **feature that belongs to an epic**, nested directly under that epic's directory, e.g. `01-rag-system/dp01-document-parse`. `[phase][nn]` is that feature's own Feature Backlog ID from `epic.md`, lowercased and 2-digit-zero-padded, matching `epic.md`'s ID exactly.
- `.spec/00NNN-feature-name/` — one directory per **standalone feature** (no epic), e.g. `00211-churn-prediction`, flat at the `.spec/` root. `00` marks it standalone; `NNN` is a counter local to standalone features, zero-padded to 3 digits.
- Either kind of feature directory contains `spec.md` and, flat alongside it, `requirements.md` (built-in spec-quality checklist). `sdd-implement` adds `plan.md`, `tasks.md`, and other artifacts to the same directory later — no `checklists/` or `contracts/` subfolder ever.

---

## Step 1: Load Context & Determine Mode

1. If it exists, read `.spec/constitution.md` — every principle in it is binding on everything this skill writes. If it doesn't exist, warn the user once and suggest running `sdd-constitution` first, but proceed if they want to.
2. Check for an existing `.spec/` directory (create it if none exists yet). List its epic directories (`NN-*`, i.e. directories containing an `epic.md`) and standalone feature directories (`00NNN-*`).
3. Determine which mode applies:
   - **New Epic**: the user describes a new multi-feature effort that doesn't match any existing epic. Go to Step 2.
   - **Incremental Epic**: the user references an existing epic and is either adding new scope to it or simply asking to continue/finish specifying it. Go to Step 2 (Epic sub-stage) only if there's new scope to fold into the backlog, otherwise skip straight to Step 3 with the existing backlog.
   - **Standalone Feature**: the user describes a single feature with no larger epic behind it. Skip Step 2 entirely, go straight to Step 3 for that one feature.
   - **Phase Report**: the user references an existing epic and isn't describing new scope, and at least one of its CRISP-ML(Q) phases is fully `Implemented` with no report yet. Skip to Step 5.
   - If genuinely ambiguous which mode applies, or which existing epic/feature is meant, ask before proceeding.
4. If the matched epic's `epic.md` still uses an old flat, unphased backlog table (a single table with plain `F1, F2...` IDs and no phase subsections), say so explicitly and ask the user how to proceed — don't silently reinterpret it.

## Step 2: Epic Sub-Stage (New Epic / Incremental Epic modes only)

Skip entirely for a Standalone Feature.

1. **Name the epic** (new epic only): 2-4 words, kebab-case, preserving technical terms (e.g. "recommendation system for our marketplace" → `recommendation-system`). Find the highest `NN` in use and use `NN+1`, zero-padded to 2 digits — independent of the standalone feature counter.
2. **Draft the Feature Backlog, organized by CRISP-ML(Q) phase**: identify the discrete features needed to realize the epic — not implementation tasks, features (each substantial enough to eventually get its own spec). Organize into the six CRISP-ML(Q) phases (Business & Data Understanding, Data Preparation, Modeling, Evaluation, Deployment, Monitoring & Maintenance) by which epic-level capability each feature delivers. Derive the actual list from the specific epic — don't force every phase to be populated; omit a phase entirely if there's no distinct feature for it, stating why in Assumptions. If a feature doesn't cleanly fit one phase, file it under the earliest phase it substantially starts in.

   For each phase populated, capture Requirements & Constraints (2-4 bullets) plus a Feature Backlog table — see `EPIC-TEMPLATE.md` for the exact columns, ID scheme (`[PHASE][N]`), and Status rules.

   Flag any feature whose feasibility is genuinely uncertain (e.g. depends on data that may not exist) as an explicit note, not a silent assumption.
3. **Identify risks & derive QA backlog rows**: for each phase drafted above, walk CRISP-ML(Q)'s own quality-assurance loop — identify the risk a planned feature carries, judge whether it's feasible to accept as-is, and where it isn't, name the QA method that would mitigate it, as a `Risk | Feasible As-Is? | QA Method / Mitigation | Resulting Backlog ID` table. Every `No` row **must** produce a corresponding `QA`-typed row in that phase's Feature Backlog table — same execution model as any other feature, its own full spec → plan → tasks → implement run — unless the mitigation is trivial enough to fold into another feature's own `tasks.md` (say so in the QA Method column instead of creating a redundant row).
4. **Write `epic.md`** following `EPIC-TEMPLATE.md` exactly.
5. **Write `shared-data-model.md`** (only if the Shared Entities section is non-empty) following `SHARED-DATA-MODEL-TEMPLATE.md`.
6. For **Incremental Epic**, only add new backlog rows / update sections implied by the new scope — never touch a `Status` cell here (that's Step 4 and `sdd-implement`'s job) and never regenerate rows that already exist unchanged.

## Step 3: Specify + Clarify Sub-Stage — One Feature at a Time

This is the core loop. Build the work queue first, then process it one feature at a time, **pausing for the user's review after each** before moving to the next — never generate multiple specs back-to-back without a pause.

**Build the queue**:
- Standalone Feature mode: queue has exactly one entry — the described feature.
- New/Incremental Epic mode: queue is every Feature Backlog row without a `Specified`/`Implemented` Status yet, in priority order (P1 first, then P2, P3; within the same priority, phase order as listed in `epic.md`). If the user names a specific row instead, queue just that one.

**For each feature in the queue, in order:**

### 3a. Specify

1. **Analyze scope and feasibility**: identify the main user stories, entities, edge cases, and functional requirements from the description (or, for an epic row, from its Goal + the epic's Objective & Business Context). Do an explicit feasibility pass — if the description implies data that likely doesn't exist yet, flag it as an assumption or `[NEEDS CLARIFICATION]` rather than drafting around it silently.
2. **Generate a short feature name**: 2-4 words, action-noun, kebab-case, preserving technical terms (e.g. "flag at-risk customers before they churn" → `churn-prediction`).
3. **Determine the feature directory**: if part of an epic, `.spec/NN-epic-name/[phase][nn]-short-name/` using that row's lowercased, zero-padded backlog ID (must match `epic.md` exactly). Otherwise, `.spec/00<NNN>-short-name/` using the next available 3-digit counter.
4. **Write `spec.md`** following `SPEC-TEMPLATE.md` exactly, replacing every bracketed placeholder with details derived from the description. Remove any optional section that doesn't apply — never leave "N/A". Omit Business & Data Understanding and Risk Assessment only for a confirmed non-ML feature (say why in Assumptions).

   Focus on WHAT and WHY, not HOW — no model architecture, no tech stack. For unclear aspects: make an informed guess and document it in Assumptions, or mark `[NEEDS CLARIFICATION: specific question]` — **at most 3 total**, prioritized data availability/feasibility > scope > safety/fairness/privacy > UX > technical detail. Model/ML success metrics must be measurable, tied to a named eval set, and statistical; business metrics must be technology-agnostic and verifiable without knowing the implementation.
5. **Validate quality**: write `.spec/[feature-dir]/requirements.md` per `REQUIREMENTS-CHECKLIST-TEMPLATE.md`, review the spec against every item (quoting the relevant section for any failure), fix and re-validate up to 3 iterations for anything failing besides `[NEEDS CLARIFICATION]`, then keep the checklist in sync with the final spec.
6. If `[NEEDS CLARIFICATION]` markers remain (max 3): present each as a question with a small options table (Option / Answer / Implications, plus "Custom"), wait for the user's choices, replace each marker with the chosen answer, and re-validate.
7. If this feature belongs to an epic, update `epic.md`: flip this row's `Status` to `Specified` and add a link to the new `spec.md`. Don't touch any other row.

### 3b. Clarify (auto-chained, skippable per feature)

Immediately after 3a, unless the user says to skip Clarify for this feature:

1. Scan the fresh spec for ambiguity against this taxonomy, marking each Clear / Partial / Missing. ML-first (skip if the spec is confirmed non-ML): Data Availability & Quality; Evaluation Protocol; Model/Approach Choice; Drift & Feedback Loops; Fairness & Responsible AI; Compute & Cost Budget; Human-in-the-loop Fallback. Classic (always apply): Functional Scope & Behavior; Domain & Data Model; Interaction & UX Flow; Non-Functional Quality; Integration & External Dependencies; Edge Cases & Failure Handling; Constraints & Tradeoffs; Terminology & Consistency; Completion Signals; Misc/Placeholders.
2. Build a prioritized queue of **at most 5** candidate questions from the Partial/Missing categories — each must be answerable as a short multiple-choice (2-5 options) or a ≤5-word phrase, and materially impact architecture, data modeling, task breakdown, test design, UX, operational readiness, or compliance. Balance category coverage; if no valid questions exist, say so immediately and move on to the next feature.
3. Ask **exactly one question at a time**: lead with `**Question:**` + a full interrogative sentence, one "why it matters" sentence, then either a recommended multiple-choice table or a suggested short answer (`**Recommended:**` / `**Suggested:**` with 1-2 sentences of reasoning). Accept "yes" as agreement with your stated answer. Stop when ambiguities are resolved, the user signals completion, or 5 questions are asked.
4. After each accepted answer (don't batch): add/append to a `## Clarifications` section per `SPEC-TEMPLATE.md`'s Clarifications format, apply the answer to the most relevant spec section(s) too (data/labeling → Business & Data Understanding; evaluation/model choice → Model/ML Metrics; drift/fairness/human-in-the-loop → Risk Assessment + Non-Goals; compute/latency → Success Criteria/Assumptions; functional → Functional Requirements; interaction → User Stories; data shape → Key Entities; vague adjective → a metric; edge case → Edge Cases; terminology → normalize across the spec), and save immediately.
5. Re-validate: one bullet per accepted answer, no contradictions left, consistent terminology; re-check `requirements.md` checkboxes and toggle only ones that actually changed.

### 3c. Pause for Review

Report this feature's result — spec path, checklist pass/fail, questions asked/answered, any Outstanding/Deferred clarification items — and stop. Ask the user whether to proceed to the next feature in the queue, revise this one, or stop here. Only continue the loop on an explicit go-ahead.

## Step 4: Update the Epic (ongoing)

Already covered inline at 3a.7 for each feature — no separate batch step. By the time the queue is exhausted, every row that got specified has `Status: Specified` and a link.

## Step 5: Phase Report Mode

For every phase in the matched epic's `epic.md` where every backlog row (`Feature` and `QA` alike) is `Implemented` and no `reports/<phase-name>-report.md` exists yet:

1. For each row, load its feature's `spec.md` (Risk Assessment, Success Criteria) and `plan.md` (Evaluation Gate: threshold vs. actual result).
2. Write `.spec/NN-epic-name/reports/<phase-name>-report.md` following `PHASE-REPORT-TEMPLATE.md`.
3. Append a link under `epic.md`'s **Phase Reports** section. Don't touch any Feature Backlog row or Status — that's `sdd-implement`'s job.
4. If more than one phase qualifies, generate all of them, one file each. If nothing qualifies, say so plainly and stop.

## Step 6: Closing

**New/Incremental Epic**: report the `epic.md` path (+ `shared-data-model.md` if generated), the full feature backlog by phase, how many features this run specified vs. how many remain in the queue, and the exact next step — run `sdd-implement` for the first specified feature (nested at `.spec/NN-epic-name/[phase][nn]-short-name/`), or re-run this skill to continue the queue.

**Standalone Feature**: report the created `spec.md` path, checklist result, and suggest `sdd-implement` as the next step.

**Phase Report**: report which phase(s) got a report, their Go/No-Go recommendation, any Carry-Forward items, and which phases are still in progress.
