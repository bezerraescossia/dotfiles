# Phase Completion Report Template

Write `.spec/NN-epic-name/reports/<phase-name>-report.md` (kebab-case phase name, e.g. `reports/data-preparation-report.md`):

```markdown
# Phase Report: [PHASE NAME] — [EPIC NAME]

**Epic**: .spec/NN-epic-name/epic.md | **Date**: [DATE]

## Features Delivered

| ID | Feature Name | Type | spec.md | plan.md |
|---|---|---|---|---|
| DP1 | [...] | Feature | [link] | [link] |
| DP2 | [...] | QA | [link] | [link] |

## Risks Realized vs. Planned

| Risk (from epic.md Risks & QA table) | Materialized? | Outcome |
|---|---|---|
| [...] | Yes/No | [...] |

## QA Outcomes

[One line per QA-typed row: what its mitigation achieved, referencing its own spec.md Success Criteria / plan.md Evaluation Gate result.]

## Key Metrics

*Omit if no feature in this phase has an Evaluation Gate.*

| Metric | Threshold | Actual Result | Source Feature |
|---|---|---|---|

## Go/No-Go for Next Phase

[Recommendation + rationale — does anything here block the next phase from starting?]

## Carry-Forward Items

- [Deferred risk, follow-up QA, or scope item that didn't fit this phase but must be tracked going forward]
```
