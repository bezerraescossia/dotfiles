---
name: sdd-specify
description: Generates a detailed feature specification in structured Markdown from a natural-language description, at .spec/[feature-dir]/spec.md. CRISP-ML(Q)-native — covers Business & Data Understanding and a mandatory Risk Assessment alongside user stories and functional requirements; falls back to a plain software spec when no model/data is involved. When the feature belongs to an epic (see sdd-epic), picks up its context and shared data model automatically.
user_invocable: true
---

# Feature Specification Generator

This skill guides Claude to act as a senior ML Product Manager and ML Engineer. The goal is to turn a raw feature idea into a rigorous specification document, covering the business/ML objective, data understanding, prioritized usage scenarios, independently testable user stories, functional requirements, a risk assessment, and measurable success criteria (business and model metrics alike).

**Position in the SDD pipeline**: Constitution → Epic (optional) → **Specify** → Clarify (optional) → Plan → Checklist (optional) → Tasks → Analyze (optional) → Implement → Monitor (optional). Expected input: `.spec/constitution.md` (if it exists), the epic's `epic.md` (if this feature belongs to one), and a natural-language feature description. Output: `.spec/[feature-dir]/spec.md`, consumed next by `sdd-plan` (and optionally `sdd-clarify` first).

**Default assumption**: the feature involves a model, a fine-tune, a prompt/LLM-backed capability, or a data pipeline unless the description clearly describes plain CRUD/UI work with no learned component. When it's genuinely non-ML, you may omit the Business & Data Understanding and Risk Assessment sections — say explicitly in the spec that they were omitted and why, rather than leaving them blank.

---

## Step 1: Load Context

Don't block execution if something is missing — a brand-new project may not have any of this yet:
- `.spec/constitution.md`: if it exists, check whether anything in the user's request conflicts with a non-negotiable principle. Flag any conflict explicitly before generating the spec — never silently generate a spec that violates the constitution.
- `.spec/`: if it exists, scan its `E<N>-*` directories (epic directories, each containing an `epic.md`) and check whether the user's description names one of them or one of its Feature Backlog entries. If exactly one epic matches, load its `epic.md` (Objective & Business Context, Non-Goals, Constitution Check) and, if present, `shared-data-model.md` — both become binding context for this spec. If more than one epic could plausibly match, ask the user which one (or "standalone, no epic"). If none match, proceed as a standalone feature — this skill works perfectly well without an epic.

## Step 2: Analyze Scope and Feasibility

Identify the main user stories, the entities involved, the edge cases, and the functional requirements — implicit or explicit — from the description.

Before drafting, do an explicit feasibility pass: is this solvable at all with a reasonable ML/LLM approach and the data that's plausibly available? If the description implies data that likely doesn't exist yet (no historical labels, no logged events, no examples), say so as a flagged assumption or a `[NEEDS CLARIFICATION]` — don't quietly draft a spec around data that may not exist.

## Step 3: Generate a Short Feature Name

2-4 words, action-noun format, kebab-case: extract the most relevant keywords from the description, preserving technical terms and acronyms (e.g. "I want to flag at-risk customers before they churn" → `churn-prediction`; "Add a support-ticket summarizer" → `ticket-summarizer`).

## Step 4: Determine the Feature Directory

1. List all existing feature directories under `.spec/` — any directory containing a `spec.md` (an epic directory contains `epic.md` instead and doesn't count). Find the highest `NNN` used across `F<NNN>-*` and `E<N>F<NNN>-*` names — features share **one global counter** regardless of which epic (if any) they belong to — and use `NNN+1` zero-padded to 3 digits (`001`, `002`, ...).
2. If this feature belongs to an epic `E<K>` (per Step 1), name the directory `.spec/E<K>F<NNN>-short-name/`. Otherwise (standalone feature), name it `.spec/F<NNN>-short-name/`.

You must only create **one** feature per invocation of this skill.

## Step 5: Write the Specification

Generate the document in Markdown following strictly the template below, replacing bracketed placeholders (`[...]`) with details derived from the provided description, preserving section order and headings. Remove any optional section that doesn't apply — never leave it as "N/A". Omit `## Business & Data Understanding` and `## Risk Assessment` only for confirmed non-ML features (state why in an `## Assumptions` line if you do).

**Focus on WHAT and WHY, not HOW** — no model architecture, no tech stack, no infra. Written for business and ML stakeholders jointly, not for the eventual implementation.

For unclear aspects:
- Make an informed guess based on context and industry/ML-practice standards.
- Only mark `[NEEDS CLARIFICATION: specific question]` when the choice significantly affects scope, data strategy, or risk, multiple reasonable interpretations exist with different implications, or no reasonable default exists.
- **Limit: at most 3 `[NEEDS CLARIFICATION]` markers total.** Prioritize by impact: data availability/feasibility > scope > safety/fairness/privacy > user experience > technical detail.
- Document reasonable defaults you assumed in the Assumptions section instead of asking about them (e.g. standard train/validation/test split ratios, standard data-retention practice, standard latency expectations for the deployment surface, user-friendly fallback on low-confidence predictions).

Model/ML success metrics must be measurable, tied to a named evaluation set, and framed statistically (e.g. "F1 ≥ 0.85 on the held-out test set" — not "the model is accurate"). Business success metrics must be technology-agnostic and verifiable without knowing the implementation (e.g. "at-risk customers flagged by the model are contacted 5 days earlier on average").

### Template

```markdown
# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[feature-dir]`
**Created**: [TODAY'S DATE]
**Status**: Draft
**Epic**: [.spec/E<N>-epic-name/epic.md — Feature FN, or "None — standalone feature"]
**Input**: User description: "$ARGUMENTS"

## Business & Data Understanding *(mandatory unless explicitly non-ML — see Assumptions)*

**Business Objective**: [The business problem or opportunity this addresses, in plain language]

**ML Objective**: [How the business objective translates into a model/system task — e.g. "binary classification of customer churn within a 30-day window" — and why this framing was chosen]

**Data Availability & Quality**: [What data exists today, its source, approximate volume, labeling status, known gaps or biases. If data doesn't exist yet, say so explicitly — this is a blocking feasibility concern, not a footnote]

**Non-Goals**: [What this feature explicitly does not attempt — e.g. "not intended to explain individual predictions to end customers"]

## User Scenarios & Testing *(mandatory)*

*Prioritization and testability note:*
* Each user story/journey must be independently testable, enabling incremental delivery of value (MVP).
* Priorities: P1 (Critical/Essential), P2 (Important), P3 (Nice-to-have).

### User Story 1 - [Short Title] (Priority: P1)

[Describe this user journey in plain, clear language]

**Why this priority**: [Explain the business value and reason for this priority]

**Independent Test**: [How this can be tested in isolation, e.g. "Can be tested by performing X action to get Y outcome"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action taken], **Then** [expected result]
2. **Given** [initial state], **When** [action], **Then** [expected result]

---

### User Story 2 - [Short Title] (Priority: P2)

[Same structure as above]

---

### User Story 3 - [Short Title] (Priority: P3)

[Same structure as above]

---

### Edge Cases

- What happens when [boundary condition]?
- How does the system handle [error or failure scenario]?
- How does the system behave on a low-confidence or out-of-distribution prediction?
- How does the system behave when input data is stale, drifted, or the model/service is unavailable?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST [specific capability, e.g. "score each customer daily for churn risk"]
- **FR-002**: The system MUST [specific capability, e.g. "expose a confidence score alongside each prediction"]
- **FR-003**: Users MUST be able to [key interaction, e.g. "override or dismiss a flagged prediction"]

*Requirements needing alignment must be marked explicitly:*
- **FR-00N**: The system MUST [NEEDS CLARIFICATION: unspecified requirement detail]

### Key Entities *(include if the feature involves data)*

- **[Entity 1]**: [What it represents, key attributes at a conceptual/business level]
- **[Entity 2]**: [What it represents, relationships to other entities]
- If this feature belongs to an epic and an entity already exists in its `shared-data-model.md`, reference it instead of redefining it: "**[Entity]**: see .spec/E<N>-epic-name/shared-data-model.md" — only define entities here that are genuinely local to this feature.

## Risk Assessment *(mandatory unless explicitly non-ML — see Assumptions)*

| Failure Mode | Likelihood | Severity | Mitigation |
|---|---|---|---|
| [e.g. Model systematically under-predicts risk for a customer segment] | [Low/Medium/High] | [Low/Medium/High] | [e.g. Fairness audit across segments before launch; human review for borderline cases] |
| [e.g. Data pipeline silently drops recent events] | [...] | [...] | [...] |

## Success Criteria *(mandatory)*

### Business KPIs

- **SC-001**: [Measurable, technology-agnostic business metric, e.g. "Customers flagged as at-risk are contacted 5 days earlier on average"]
- **SC-002**: [Business impact metric, e.g. "Voluntary churn among flagged customers drops by 10% within two quarters"]

### Model/ML Metrics

- **SC-003**: [Metric tied to a named eval set, e.g. "Recall ≥ 0.80 and precision ≥ 0.60 on the held-out test set"]
- **SC-004**: [Operational metric, e.g. "P95 inference latency under 200ms in production"]

## Assumptions

- [Assumption about data availability, split strategy, or labeling]
- [Assumption about scope boundaries]
- [Assumption or dependency on existing systems/APIs/data sources]
```

## Step 6: Validate Specification Quality

After writing the spec, validate it against a quality checklist:

1. Write `.spec/[feature-dir]/checklists/requirements.md`:
   ```markdown
   # Specification Quality Checklist: [FEATURE NAME]

   **Purpose**: Validate specification completeness and quality before proceeding to planning
   **Created**: [DATE]
   **Feature**: [Link to spec.md]

   ## Content Quality

   - [ ] No implementation details (model internals, frameworks, infra)
   - [ ] Focused on business/ML value, not implementation
   - [ ] Written for business and ML stakeholders jointly
   - [ ] All mandatory sections completed

   ## Business & Data Understanding

   - [ ] Business Objective and ML Objective are both stated and distinct
   - [ ] Data Availability & Quality is addressed with real evidence, not assumed
   - [ ] Feasibility concerns (missing/insufficient data) are flagged, not glossed over

   ## Requirement Completeness

   - [ ] No [NEEDS CLARIFICATION] markers remain
   - [ ] Requirements are testable and unambiguous
   - [ ] Business KPIs are measurable and technology-agnostic
   - [ ] Model/ML metrics are measurable and each names its evaluation set
   - [ ] All acceptance scenarios are defined
   - [ ] Edge cases include model-specific failure modes (low confidence, drift, unavailability)
   - [ ] Scope is clearly bounded (Non-Goals stated)
   - [ ] Dependencies and assumptions identified

   ## Risk Assessment

   - [ ] Risk Assessment table is present (or its absence is justified as non-ML)
   - [ ] Each failure mode has a likelihood, severity, and concrete mitigation

   ## Feature Readiness

   - [ ] All functional requirements have clear acceptance criteria
   - [ ] User scenarios cover primary flows
   - [ ] Feature meets measurable outcomes defined in Success Criteria
   - [ ] No implementation details leak into the specification

   ## Notes

   - Items left unchecked require spec updates before `sdd-clarify` or `sdd-plan`.
   ```
2. Review the spec against each item; document specific issues found (quote the relevant spec section).
3. If items fail (excluding `[NEEDS CLARIFICATION]`): fix the spec and re-validate, up to 3 iterations. If still failing, note the remaining issues in the checklist and warn the user.
4. If `[NEEDS CLARIFICATION]` markers remain (max 3, per Step 5): present each as a question with a small options table (Option / Answer / Implications, plus a "Custom" row), wait for the user's choices, then replace each marker with the chosen answer and re-validate.
5. Keep the checklist file's checkbox states in sync with the final spec.

## Step 7: Update the Epic (conditional)

If this spec has an `Epic` back-reference (Step 1), update that epic's `epic.md`: flip the matching Feature Backlog row's `Status` to `Specified` and add a link to the new `spec.md`. Don't touch any other row.

## Step 8: Closing

Report to the user: the created file path, the feature name/number, the checklist result, and the list of any items still marked `[NEEDS CLARIFICATION]` (there shouldn't be any left) so they can be resolved before `sdd-plan`. If an epic was updated, mention it and note which backlog features remain. Suggest `sdd-clarify` as an optional next step if any ambiguity remains, otherwise `sdd-plan`.
