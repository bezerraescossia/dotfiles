# Feature Specification Template

```markdown
# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[feature-dir]`
**Created**: [TODAY'S DATE]
**Status**: Draft
**Epic**: [.spec/NN-epic-name/epic.md — Feature [backlog ID], or "None — standalone feature"]
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
- If this feature belongs to an epic and an entity already exists in its `shared-data-model.md`, reference it instead of redefining it: "**[Entity]**: see .spec/NN-epic-name/shared-data-model.md" — only define entities here that are genuinely local to this feature.

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

## Clarifications Section (added by the Clarify sub-stage)

The first accepted clarification for a feature adds this section right after the highest-level overview section (i.e. right after the header fields, before `## Business & Data Understanding`):

```markdown
## Clarifications

### Session YYYY-MM-DD

- Q: <question> → A: <final answer>
```

Append one bullet per accepted answer, under the current session's subheading (add a new subheading if Clarify runs again on a different date). Apply each clarification to the most relevant section(s) elsewhere in the spec too — this section is a log, not the only place the answer lives.
