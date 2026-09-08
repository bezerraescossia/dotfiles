# Constitution Document Template

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

## Amendment: Sync Impact Report

If `.spec/constitution.md` already exists, prepend this as an HTML comment at the top of the file whenever it's amended:

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
