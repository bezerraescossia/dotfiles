# Specification Quality Checklist Template

Write `.spec/[feature-dir]/requirements.md` (flat in the feature directory, no `checklists/` subfolder):

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

- Items left unchecked require spec updates before Clarify or `sdd-implement`.
```
