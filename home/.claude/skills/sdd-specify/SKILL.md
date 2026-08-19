---
name: sdd-specify
description: Generates a detailed feature specification in structured Markdown from a natural-language description, at specs/NNN-feature/spec.md.
user_invocable: true
---

# Feature Specification Generator

This skill guides Claude to act as a senior Product Manager and Software Engineer. The goal is to turn a raw feature idea into a rigorous specification document, covering prioritized usage scenarios, independently testable user stories, functional requirements, measurable success criteria, and edge cases.

**Position in the SDD pipeline**: Constitution → **Specify** → Clarify (optional) → Plan → Checklist (optional) → Tasks → Analyze (optional) → Implement. Expected input: `docs/constitution.md` (if it exists) and a natural-language feature description. Output: `specs/NNN-feature-name/spec.md`, consumed next by `sdd-plan` (and optionally `sdd-clarify` first).

---

## Step 1: Load Context

Don't block execution if something is missing — a brand-new project may not have any of this yet:
- `docs/constitution.md`: if it exists, check whether anything in the user's request conflicts with a non-negotiable principle. Flag any conflict explicitly before generating the spec — never silently generate a spec that violates the constitution.

## Step 2: Analyze Scope

Identify the main user stories, the entities involved, the edge cases, and the functional requirements — implicit or explicit — from the description.

## Step 3: Generate a Short Feature Name

2-4 words, action-noun format, kebab-case: extract the most relevant keywords from the description, preserving technical terms and acronyms (e.g. "I want to add user authentication" → `user-auth`; "Create an analytics dashboard" → `analytics-dashboard`).

## Step 4: Determine the Feature Directory

List existing directories under `specs/` (create `specs/` if it doesn't exist yet), find the highest numeric prefix in use (`NNN-`), and use `NNN+1` zero-padded to 3 digits (`001`, `002`, ...) combined with the short name: `specs/NNN-short-name/`.

You must only create **one** feature per invocation of this skill.

## Step 5: Write the Specification

Generate the document in Markdown following strictly the template below, replacing bracketed placeholders (`[...]`) with details derived from the provided description, preserving section order and headings. Remove any optional section that doesn't apply — never leave it as "N/A".

**Focus on WHAT and WHY, not HOW** — no tech stack, no APIs, no code structure. Written for business stakeholders, not developers.

For unclear aspects:
- Make an informed guess based on context and industry standards.
- Only mark `[NEEDS CLARIFICATION: specific question]` when the choice significantly affects scope or UX, multiple reasonable interpretations exist with different implications, or no reasonable default exists.
- **Limit: at most 3 `[NEEDS CLARIFICATION]` markers total.** Prioritize by impact: scope > security/privacy > user experience > technical detail.
- Document reasonable defaults you assumed in the Assumptions section instead of asking about them (e.g. standard data-retention practice, standard web/mobile performance expectations, user-friendly error handling, session/OAuth2 auth, REST/GraphQL for services vs. CLI args for tools).

Success criteria must be measurable, technology-agnostic, user-focused, and verifiable without knowing the implementation (e.g. "Users complete checkout in under 3 minutes" — not "API response time is under 200ms").

### Template

```markdown
# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[NNN-feature-short-name]`
**Created**: [TODAY'S DATE]
**Status**: Draft
**Input**: User description: "$ARGUMENTS"

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

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST [specific capability, e.g. "allow users to create accounts"]
- **FR-002**: The system MUST [specific capability, e.g. "validate email formats"]
- **FR-003**: Users MUST be able to [key interaction, e.g. "reset their password"]

*Requirements needing alignment must be marked explicitly:*
- **FR-00N**: The system MUST [NEEDS CLARIFICATION: unspecified requirement detail]

### Key Entities *(include if the feature involves data)*

- **[Entity 1]**: [What it represents, key attributes at a conceptual/business level]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: [Measurable, technology-agnostic metric, e.g. "Users complete the flow in under 2 minutes"]
- **SC-002**: [Performance/scale metric, e.g. "System supports 1000 concurrent connections without degradation"]
- **SC-003**: [User satisfaction/success metric]
- **SC-004**: [Business impact metric]

## Assumptions

- [Assumption about user profile or behavior]
- [Assumption about scope boundaries]
- [Assumption or dependency on existing systems/APIs]
```

## Step 6: Validate Specification Quality

After writing the spec, validate it against a quality checklist:

1. Write `specs/NNN-feature/checklists/requirements.md`:
   ```markdown
   # Specification Quality Checklist: [FEATURE NAME]

   **Purpose**: Validate specification completeness and quality before proceeding to planning
   **Created**: [DATE]
   **Feature**: [Link to spec.md]

   ## Content Quality

   - [ ] No implementation details (languages, frameworks, APIs)
   - [ ] Focused on user value and business needs
   - [ ] Written for non-technical stakeholders
   - [ ] All mandatory sections completed

   ## Requirement Completeness

   - [ ] No [NEEDS CLARIFICATION] markers remain
   - [ ] Requirements are testable and unambiguous
   - [ ] Success criteria are measurable
   - [ ] Success criteria are technology-agnostic (no implementation details)
   - [ ] All acceptance scenarios are defined
   - [ ] Edge cases are identified
   - [ ] Scope is clearly bounded
   - [ ] Dependencies and assumptions identified

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

## Step 7: Closing

Report to the user: the created file path, the feature name/number, the checklist result, and the list of any items still marked `[NEEDS CLARIFICATION]` (there shouldn't be any left) so they can be resolved before `sdd-plan`. Suggest `sdd-clarify` as an optional next step if any ambiguity remains, otherwise `sdd-plan`.
