---
name: sdd-analyze
description: Runs a non-destructive, read-only cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation, before implementation. Includes ML-specific checks — Evaluation Gate consistency, Risk Assessment coverage, experiment-tracking compliance.
user_invocable: true
---

# Cross-Artifact Consistency Analysis

**Goal**: identify inconsistencies, duplications, ambiguities, and underspecified items across the three core artifacts (`spec.md`, `plan.md`, `tasks.md`) before implementation starts.

**Position in the SDD pipeline**: Tasks → **Analyze** (optional) → Implement. This must only run after `sdd-tasks` has successfully produced a complete `tasks.md`.

**Operating constraint — strictly read-only**: do not modify any files. Produce a structured report and, at the end, offer to suggest concrete remediation edits — but never apply them automatically without explicit approval.

**Constitution authority**: `.spec/constitution.md`, if it exists, is non-negotiable within this analysis. A conflict with it is automatically CRITICAL and requires adjusting the spec, plan, or tasks — not diluting or reinterpreting the principle. If a principle itself needs to change, that happens through a separate, explicit `sdd-constitution` run, outside this analysis.

---

## Step 1: Load Artifacts

Abort with a clear message if any required file is missing (name the missing prerequisite skill to run). Load, progressively and only what's needed:

- **spec.md**: overview/context, functional requirements, success criteria, user stories, edge cases.
- **plan.md**: architecture/stack choices, data-model references, phases, technical constraints.
- **tasks.md**: task IDs, descriptions, phase grouping, `[P]` markers, referenced file paths.
- **.spec/constitution.md** (if it exists): principles for validation.

## Step 2: Build Semantic Models (internal — don't dump raw artifacts into the output)

- **Requirements inventory**: one stable key per Functional Requirement (FR-###) and Success Criterion (SC-###); use the explicit ID as the primary key. Include Model/ML Metrics (they require buildable evaluation work) and any Business KPI that requires buildable infrastructure (e.g. load-testing, audit tooling); exclude pure post-launch outcome metrics (e.g. "Reduce support tickets by 50%").
- **Risk inventory**: one entry per Risk Assessment row (failure mode + mitigation), if the spec has one.
- **User story/action inventory**: discrete user actions with their acceptance criteria.
- **Task coverage mapping**: each task mapped to one or more requirements/stories/risks (by explicit ID reference or keyword inference).
- **Evaluation Gate model**: metric/threshold/eval-set rows from `plan.md`, to be diffed against `spec.md`'s Model/ML Metrics and `tasks.md`'s Evaluation phase.
- **Constitution rule set**: principle names and their MUST/SHOULD statements.

## Step 3: Detection Passes

Focus on high-signal findings; cap at 50 total, summarizing any overflow.

- **A. Duplication**: near-duplicate requirements; flag the lower-quality phrasing for consolidation.
- **B. Ambiguity**: vague, unquantified adjectives ("fast", "scalable", "secure", "intuitive", "robust"); unresolved placeholders (`TODO`, `TKTK`, `???`, `<placeholder>`).
- **C. Underspecification**: requirements with a verb but no object/measurable outcome; user stories missing acceptance-criteria alignment; tasks referencing files/components not defined in spec/plan.
- **D. Constitution alignment**: any requirement or plan element conflicting with a MUST principle; mandated sections or quality gates missing.
- **E. Coverage gaps**: requirements with zero associated tasks; tasks with no mapped requirement/story; buildable Success Criteria (performance, security, availability) absent from tasks; Risk Assessment mitigations in `spec.md` with no corresponding task in `tasks.md`.
- **F. Inconsistency**: terminology drift (same concept named differently across files); data entities in the plan but absent from the spec (or vice versa); task-ordering contradictions (e.g. integration before foundational setup, with no dependency note); conflicting requirements (e.g. one requires Next.js while another specifies Vue).
- **G. Evaluation Gate mismatch**: a Model/ML Metric in `spec.md` with no matching row in `plan.md`'s Evaluation Gate (or vice versa); a metric/threshold that differs between `plan.md` and the Evaluation phase in `tasks.md`; a Modeling/Experimentation task with no Accept/Reject clause or no named fallback task.
- **H. Constitution/ML compliance**: `.spec/constitution.md` mandates an experiment-tracking tool, data-versioning tool, or minimum eval protocol that doesn't appear in `plan.md`'s Technical Context.

## Step 4: Assign Severity

- **CRITICAL**: violates a constitution MUST, a core artifact is missing, a requirement has zero coverage and blocks baseline functionality, the spec's Risk Assessment section is missing for a feature that isn't confirmed non-ML, or an Evaluation Gate mismatch exists between `plan.md` and `tasks.md`.
- **HIGH**: duplicate/conflicting requirement, ambiguous security/performance attribute, untestable acceptance criterion, a Risk Assessment mitigation with no corresponding task, a Modeling task missing its Accept/Reject clause.
- **MEDIUM**: terminology drift, missing non-functional task coverage, underspecified edge case.
- **LOW**: style/wording improvement, minor redundancy not affecting execution order.

## Step 5: Produce the Report

Output a Markdown report (no file writes):

```markdown
## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | spec.md:L120-134 | Two similar requirements... | Merge phrasing; keep the clearer version |

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|

**Constitution Alignment Issues:** (if any)

**Unmapped Tasks:** (if any)

**Metrics:**
- Total Requirements / Total Tasks / Coverage % (requirements with ≥1 task)
- Ambiguity Count / Duplication Count / Critical Issues Count
```

Generate stable finding IDs prefixed by category initial (A through H). Re-running on unchanged artifacts should produce consistent IDs and counts.

## Step 6: Next Actions

- If CRITICAL issues exist: recommend resolving them before `sdd-implement`.
- If only LOW/MEDIUM issues exist: the user may proceed, but list improvement suggestions.
- Suggest concrete follow-ups (e.g. "Re-run `sdd-specify` with refinement", "Re-run `sdd-plan` to adjust the architecture", "Manually edit `tasks.md` to add coverage for X").
- Ask: "Would you like me to suggest concrete remediation edits for the top N issues?" — do not apply them automatically.

## Operating Principles

- **Never modify files** — this is read-only analysis.
- **Never hallucinate missing sections** — report their absence accurately.
- **Constitution violations are always CRITICAL.**
- **Cite specific instances**, not generic patterns.
- **Report zero issues gracefully** — a clean pass still gets a coverage-statistics summary.
