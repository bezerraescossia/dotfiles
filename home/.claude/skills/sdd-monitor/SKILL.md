---
name: sdd-monitor
description: Generates a monitoring and maintenance plan for a deployed feature — drift signals, retraining triggers, alerting, and a rollback runbook — at .spec/[feature-dir]/monitoring.md. Implements CRISP-ML(Q)'s Monitoring & Maintenance phase, the step after sdd-implement.
user_invocable: true
---

# Monitoring & Maintenance Plan Generator

This skill guides Claude to act as an ML Reliability Engineer defining what happens to a feature *after* it ships. CRISP-ML(Q) treats Monitoring & Maintenance as a first-class phase, not an afterthought — a model that isn't watched for drift, and a system with no rollback path, isn't actually done.

**Position in the SDD pipeline**: Implement → **Monitor** (optional, but strongly recommended for anything that trains, fine-tunes, or serves a model/prompt). Input: `.spec/[feature-dir]/plan.md` (Monitoring & Retraining Triggers, Evaluation Gate, Deployment Target), `.spec/[feature-dir]/spec.md` (Risk Assessment, Success Criteria), `.spec/constitution.md` (if it mandates monitoring practices). Output: `.spec/[feature-dir]/monitoring.md`.

For a confirmed non-ML feature (no Evaluation Gate in `plan.md`), this skill still has value — deployments still need rollback and alerting plans — but drift/retraining sections should be omitted rather than forced.

---

## Step 1: Load Context

1. Identify the feature: if the user doesn't specify one, use the most recent `.spec/` directory with a `plan.md` and completed `tasks.md`, or ask.
2. Read `.spec/[feature-dir]/plan.md` (required): extract the Evaluation Gate table, the Deployment Target, and whatever Monitoring & Retraining Triggers were already sketched in Technical Context.
3. Read `.spec/[feature-dir]/spec.md` (required): extract the Risk Assessment table and Success Criteria (both Business KPIs and Model/ML Metrics).
4. If it exists, read `.spec/constitution.md` for any mandated monitoring, alerting, or incident-response practice.
5. If `.spec/[feature-dir]/tasks.md` has a Monitoring Setup phase, read which instrumentation hooks were already wired — build on them, don't duplicate.

## Step 2: Generate `monitoring.md`

Write `.spec/[feature-dir]/monitoring.md` following this structure:

```markdown
# Monitoring & Maintenance Plan: [FEATURE]

**Feature**: .spec/[feature-dir]/spec.md | **Plan**: .spec/[feature-dir]/plan.md | **Date**: [DATE]

## Drift Signals

*Omit this section for a confirmed non-ML feature.*

| Signal | Type | Source | Alert Threshold |
|---|---|---|---|
| [e.g. Input feature distribution shift] | Data drift | [e.g. daily batch job comparing production vs. training distribution] | [e.g. PSI > 0.2] |
| [e.g. Label/target relationship shift] | Concept drift | [e.g. delayed ground-truth comparison] | [...] |

## Production Performance Monitoring

| Metric | Production Proxy | Target (from Evaluation Gate / Success Criteria) | Cadence |
|---|---|---|---|
| [e.g. Precision] | [e.g. sampled human-reviewed predictions, since ground truth is delayed] | [carry over verbatim from plan.md's Evaluation Gate] | [e.g. weekly] |
| [Business KPI from spec.md] | [production dashboard/event] | [from spec.md Success Criteria] | [...] |

## Retraining Triggers

| Trigger | Threshold | Action |
|---|---|---|
| [e.g. Sustained metric degradation] | [e.g. below Evaluation Gate threshold for N consecutive periods] | [e.g. trigger retraining pipeline, notify owner] |
| [e.g. Significant drift signal] | [from Drift Signals above] | [e.g. flag for review, don't auto-retrain] |

## Alerting & Ownership

| Condition | Severity | Channel | Owner |
|---|---|---|---|
| [...] | [Low/Medium/High/Critical] | [e.g. Slack #ml-alerts, PagerDuty] | [role/team] |

## Rollback Procedure

[Reference `plan.md`'s Deployment Target and rollback criteria; state the concrete steps to revert to the last known-good model/version and who can authorize it.]

## Incident Runbook

*One entry per high-severity Risk Assessment row from spec.md.*

### [Failure mode, from spec.md Risk Assessment]

- **Detection**: [how this shows up in monitoring — link to a Drift Signal or Performance metric above]
- **Immediate action**: [...]
- **Escalation**: [...]
```

## Step 3: Cross-Check Against Risk Assessment

For every row in `spec.md`'s Risk Assessment table, confirm at least one Drift Signal, Performance Monitoring metric, or Incident Runbook entry addresses it. Flag any Risk Assessment row with no corresponding monitoring coverage as a gap — don't silently drop it.

## Step 4: Closing

Report to the user: the `monitoring.md` file path, a summary of the retraining triggers and rollback procedure, and any Risk Assessment items from `spec.md` that still have no monitoring coverage (gaps to resolve before or shortly after launch). This is the last stage of the pipeline for this feature — no further `sdd-*` skill is suggested next, aside from re-running `sdd-monitor` itself if the deployment or risk profile changes materially.
