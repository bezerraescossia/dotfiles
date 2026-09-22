# Phase 06: Monitoring & Maintenance

> Keep checking production behavior against the Phase 01 success criteria. Catch drift before users do, turn production failures into eval cases, and decide when to loop back to earlier phases.

**CRISP-ML(Q) origin:** *Monitoring & Maintenance*. What changes for GenAI:
- **Model staleness** takes new forms:
  - The provider deprecates or changes the model
  - Users ask different things over time (input drift)
  - The knowledge base goes stale `[R]`
  - Tool/API changes `[A]`
  - Token prices change
- **Monitoring quality without labels**: sample production traces, score them with the calibrated judge and SME spot-checks, and track quality proxies (feedback, escalations, edits, refusals).
- **"Retraining"** usually means updating the **prompt, the knowledge base, or the eval set**. Fine-tuning again is rare. Moving to a new model version is a **planned migration**, not an emergency.
- **CI/CT/CD** means that every change, whatever triggered it, goes through the Phase 05 release pipeline with the regression suite as a gate.

**Scope boundaries**
- **This phase owns:** ongoing monitoring, drift detection, the feedback/data flywheel, cost management, safety operations, model migrations, periodic reviews, and retirement.
- **Earlier phases own the fixes.** When monitoring finds a problem, the loop-back table (06.8) sends it to the phase that owns it. The fix then goes through Phase 04's regression suite and Phase 05's pipeline.

**Inputs from Phase 05:** dashboards, alerts, tracing and replay, feedback capture, runbooks, on-call, RACI, the KPI result from the A/B test, open issues. From Phase 04: regression suite, calibrated judge, held-out set (with its usage count). From Phase 02: freshness policy `[R]`. From Phase 01: KPI, baseline, thresholds.

## How this file is used

This phase has two parts:

1. **Setup tasks (06.0–06.10)**, executable with `/genai` exactly like the other phases. They build the monitoring the system runs on. The last one, **06.10**, moves the project to `operating`.
2. **Cycles**, the recurring work that follows. Once the project is operating, `/genai cycle start <kind>` copies that cycle's checklist into `.genai/ops/<date>-<kind>.md`, and `/genai cycle close` finishes it. Cycles never change the task graph.

Roles work as in [Phase 02](02-context-engineering.md): HUMAN (*AI prepares / You do / AI turns into / Review rules / Done when*), AI (*Plan / Build / Review rules / Done when*), DECISION (*Brief / Options / Decision record*). Artifacts go to `.genai/artifacts/06-monitoring-maintenance/`; monitoring code, queries and dashboards live in the project repo.

## Tags

Items tagged `[R]` (retrieval), `[A]` (tools/agents), `[FT]` (fine-tuned model) or `[SH]` (self-hosted) apply only when that tag is on.

## Task graph (setup)

| Task | Title | Role | Depends on | S | M-L |
|------|-------|------|------------|---|-----|
| 06.0 | Monitoring plan | HUMAN | 05.12 | 1h | 3h |
| 06.1 | SLOs & alert tuning | AI | 06.0 | 2h | 4h |
| 06.2 | Online quality monitoring | AI | 06.0 | 3h | 8h |
| 06.3 | Drift detection | AI | 06.0 | 2h | 5h |
| 06.4 | KPI & value tracking | HUMAN | 06.0 | 1h | 3h |
| 06.5 | Cost & capacity management | AI | 06.0 | 1h | 2h |
| 06.6 | Feedback & data flywheel | AI | 06.2 | 2h | 5h |
| 06.7 | Safety operations | AI | 06.0 | 1h | 2h |
| 06.8 | Maintenance triggers & loop-back | HUMAN | 06.0 | 1h | 3h |
| 06.9 | Model migration playbook | AI | 06.8 | 2h | 4h |
| 06.10 | Review cadence & start operations | DECISION | 06.1, 06.2, 06.3, 06.4, 06.5, 06.6, 06.7, 06.9 | 1h | 2h |
| | **Setup total** | | | **~17h** | **~41h** |

## Cycles (recurring)

| Kind | When | S | M-L |
|------|------|---|-----|
| `monthly` | Every month | ~11h | ~29h |
| `quarterly` | Every quarter | ~3h | ~8h |
| `migration` | A deprecation notice, or a clearly better/cheaper model | ~8h | ~24h |
| `change` | A loop-back fix that doesn't need a full re-plan | owning phase's rework | + |
| `incident` | An incident, per its runbook | ~1–3h | ~1–3h |

A **loop-back fix** runs as a `change` cycle: the owning phase's work → the 04.11 regression suite → the 05.7 release pipeline. Only a real re-frame (a new slice, a changed outcome) reopens the task graph with `project active` and `set <task> todo --cascade`.

---

## Tasks

### 06.0 Monitoring plan

```yaml task
id: "06.0"
title: Monitoring plan
role: HUMAN
depends_on: ["05.12"]
estimate: {S: 1, M-L: 3}
artifact: monitoring-plan.md
optional_tag: null
sets_tags: []
```

**AI prepares** (`06.0-prep.md`)
- A **re-read summary** of the Phase 05 handoff: dashboards, alerts, open issues, the KPI result
- A **draft signal table** (template below): every signal to watch, with a proposed threshold, cadence, owner and action on breach, traced to the Phase 01 thresholds and the Phase 04 weak spots
- A **proposed review cadence**: a daily alert watch, a weekly quality sample, a monthly report, a quarterly review
- The **RACI from Phase 05**, restated as a question: who may change prompts, models, sources, tools and guardrails

**You do**
- [ ] Confirm or correct each signal, threshold and cadence
- [ ] Name an **owner per signal**
- [ ] Confirm the RACI, and who receives the monthly report
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `monitoring-plan.md`: the signal table with owners and actions, the review cadence, the RACI, and the reporting line to the sponsor.

**Review rules**
- Every signal has a **threshold, a cadence, an owner and an action**. A signal with no action is noise — remove it or give it one.
- Thresholds trace to the Phase 01 metrics sheet or the Phase 04 results, not to round numbers.
- The cadence is realistic against the owner's time. Weekly work that nobody has time for is a gap.
- Every action points to a runbook or to the loop-back table (06.8).
- The RACI is confirmed by the people named in it.

**Done when** you approve the plan, and every signal has a named owner.

---

### 06.1 SLOs & alert tuning

```yaml task
id: "06.1"
title: SLOs & alert tuning
role: AI
depends_on: ["06.0"]
estimate: {S: 2, M-L: 4}
artifact: slos.md
optional_tag: null
sets_tags: []
```

**Plan** (`06.1-plan.md`): the SLOs to define, the error-budget policy, and which existing alerts will be measured for noise before tuning.

**Build**
- [ ] Define **SLOs**: availability, latency p95, error rate, fallback rate, cost per task, and the quality-proxy floors
- [ ] Set **error budgets**. When a budget is spent, stability work comes before new changes
- [ ] **Tune the alerts** against real post-launch data: remove the noisy ones, and add any that were missing
- [ ] Make sure every alert points to a runbook
- [ ] Wire the SLO dashboard so attainment can be reviewed monthly

**AI writes** `slos.md`: each SLO with its target, window and measurement query, the error-budget policy, the alert list with its measured firing rate and its runbook, and the changes made during tuning.

**Review rules**
- Every SLO has a **measurable query** against the Phase 05 telemetry, not a stated intention.
- Alert tuning uses **observed firing rates**, and the artifact shows before and after.
- Every alert maps to a runbook. An alert with no runbook is not shipped.
- The error-budget policy says what stops when the budget is spent, and who decides.

**Done when** you approve the SLOs, and the alerts fire at a rate their owners accept.

---

### 06.2 Online quality monitoring

```yaml task
id: "06.2"
title: Online quality monitoring
role: AI
depends_on: ["06.0"]
estimate: {S: 3, M-L: 8}
artifact: online-quality.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): continued model evaluation.*

**Plan** (`06.2-plan.md`): the sampling design, the scoring path (replay through the 04.11 suite and the calibrated judge), the SME spot-check workload, and the cost per week of scoring.

**Build**
- [ ] **Sample production traces** each week, stratified by segment/case type, including traces flagged by feedback or guardrails
- [ ] Score the sample with the **calibrated judge** and the automatic checks from the 04.11 regression suite, by replaying it
- [ ] Set up the **SME spot-check** of a smaller sample. This measures quality directly, and it checks the judge
- [ ] Track the **quality proxies**:
  - [ ] Thumbs up/down
  - [ ] User edit or correction rate
  - [ ] Escalations to humans
  - [ ] Refusal / "I don't know" rate
  - [ ] Citation rate `[R]`
  - [ ] Task success and approval-rejection rate `[A]`
- [ ] Compare against the Phase 04 levels and the thresholds, **per case type and segment**, not just the overall average
- [ ] Add a **judge-drift check**: if judge–SME agreement drops, recalibrate the judge (04.2)
- [ ] Produce the weekly/monthly report automatically, using the health report template

**AI writes** `online-quality.md`: the sampling design with its rationale, the scoring pipeline and its repo path, the proxy definitions and queries, the report format and schedule, the judge-drift check, and the first report produced from real traffic.

**Review rules**
- Sampling is **stratified** and includes flagged traces, so the report isn't dominated by easy cases.
- Scoring reuses the **calibrated** judge and the 04.11 checks. A new, uncalibrated judge is not introduced here.
- The SME spot-check has a size, a cadence and a named reviewer.
- Reports break results down **per case type and segment**, against the Phase 04 levels.
- The judge-drift check has a threshold and an action.
- A first real report exists. A pipeline with no output doesn't count.

**Done when** you approve the setup, and the first online quality report is produced.

---

### 06.3 Drift detection

```yaml task
id: "06.3"
title: Drift detection
role: AI
depends_on: ["06.0"]
estimate: {S: 2, M-L: 5}
artifact: drift-detection.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): model staleness.*

**Plan** (`06.3-plan.md`): what each drift check measures, how the baseline distribution is captured, and the thresholds proposed for each.

**Build**
- [ ] **Input drift**: new topics or intents (cluster the inputs), new languages, changes in length or format, new user groups
- [ ] **Knowledge drift** `[R]`:
  - [ ] Freshness SLA breaches, failed syncs, sources added or removed
  - [ ] A rising **retrieval miss** or "I don't know" rate on questions that should be answerable
- [ ] **Model/provider drift**:
  - [ ] Deprecation notices and new model versions
  - [ ] Behavior changes seen in the replayed regression results
  - [ ] Pricing changes
- [ ] **Tool/API drift** `[A]`: schema changes, new errors, or latency changes in the downstream systems
- [ ] **Usage drift**: volume, peak patterns, cost per task, new use cases users are bending the system to
- [ ] Route every drift finding through the loop-back table (06.8)

**AI writes** `drift-detection.md`: each check with its metric, baseline, threshold, cadence and owner; how deprecation notices and price changes are watched; and the first drift report.

**Review rules**
- Each check names a **baseline** captured from real traffic or from the Phase 04 distribution.
- The model/provider watch has a **concrete source** (a provider changelog, a status page, an account notification), not "we'll notice".
- Regression replays are used to catch silent provider behavior changes.
- Every check routes to the 06.8 loop-back table.
- The first report exists, even when it says "no drift".

**Done when** you approve the setup, and the first drift report is produced.

---

### 06.4 KPI & value tracking

```yaml task
id: "06.4"
title: KPI & value tracking
role: HUMAN
depends_on: ["06.0"]
estimate: {S: 1, M-L: 3}
artifact: kpi-tracking.md
optional_tag: null
sets_tags: []
```

**AI prepares** (`06.4-prep.md`)
- The **KPI definition and query** from Phase 01, against the baseline and the A/B result from 05.9
- **Adoption metrics** to agree: active users, share of eligible work done with the system, retention
- A **value-vs-cost model**: the benefit (time saved, errors avoided) against the total run cost, with the assumptions that need your confirmation
- **Counter-metric candidates**: what might get worse elsewhere (rework downstream, over-reliance, skill decay)
- A **monthly report draft** for the sponsor

**You do**
- [ ] Confirm the KPI query and the value assumptions with the sponsor
- [ ] Agree the adoption metrics and the counter-metrics
- [ ] Confirm who receives the report and when
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `kpi-tracking.md`: the KPI definition and query, the baseline and A/B reference, the adoption and counter-metrics, the value-vs-cost model with its confirmed assumptions, and the reporting schedule.

**Review rules**
- The KPI is the **Phase 01 business KPI**, measured the same way as the baseline. A new, friendlier metric is a red flag.
- Value assumptions are the sponsor's, and are marked as assumptions where they are not measured.
- At least one **counter-metric** is tracked.
- The report has a named recipient and a date, not "monthly, to whoever asks".

**Done when** you approve the tracking, and the sponsor has agreed the KPI and the value model.

---

### 06.5 Cost & capacity management

```yaml task
id: "06.5"
title: Cost & capacity management
role: AI
depends_on: ["06.0"]
estimate: {S: 1, M-L: 2}
artifact: cost-capacity.md
optional_tag: null
sets_tags: []
```

**Plan** (`06.5-plan.md`): the cost breakdown to build, the savings candidates to evaluate, and the capacity items to watch.

**Build**
- [ ] Build the **cost-per-task and monthly-spend** views against the budget and the Phase 01 cost model
- [ ] Assemble the **savings candidate list**:
  - [ ] Prompt caching
  - [ ] Shorter context (a tighter token budget)
  - [ ] Batch processing for work nobody is waiting on
  - [ ] Routing easy cases to a smaller model
  - [ ] Removing unused tools or steps `[A]`
- [ ] State the rule: **every saving goes through the regression suite. Cheaper must not mean worse**
- [ ] Set up the **capacity watch**: quotas, provisioned throughput renewals, `[SH]` instance utilization, and headroom for growth
- [ ] Add the alerts for budget and quota headroom

**AI writes** `cost-capacity.md`: the cost views and their queries, the savings candidates with their estimated gain and risk, the regression rule, the capacity watch items with renewal dates, and the current cost against the budget.

**Review rules**
- Cost figures come from the **provider's billing data or the traces**, not from list prices.
- Each savings candidate states its estimated gain **and** what it might cost in quality.
- Renewal and quota dates are concrete, with an owner.
- The alerts fire **before** the budget or quota is exhausted, not after.

**Done when** you approve the setup, and the first cost review is produced.

---

### 06.6 Feedback & data flywheel

```yaml task
id: "06.6"
title: Feedback & data flywheel
role: AI
depends_on: ["06.2"]
estimate: {S: 2, M-L: 5}
artifact: flywheel.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): collect & label new data.*

**Plan** (`06.6-plan.md`): the triage workflow, how items become eval items, the consent and retention checks, and the SME labeling load per month.

**Build**
- [ ] Build the **triage flow** for user feedback and failing traces: bug, knowledge gap, prompt issue, out of scope, or user error
- [ ] Turn real failures into **eval items**, with labels from SMEs, the case type, and the source docs `[R]`
- [ ] Enforce the **split discipline**: new items go to dev, and a **held-out refresh** is added periodically, so the held-out set stays unseen
- [ ] Check **consent and retention**: using production data for eval (or `[FT]` training) must follow the sensitivity plan and the user terms
- [ ] Correct for **feedback bias**: unhappy users report more, so combine feedback with random sampling
- [ ] Version the eval set, and record why each item was added

**AI writes** `flywheel.md`: the triage categories and routing, the promotion path from trace to eval item, the consent/retention gate, the random-sampling mix, the held-out refresh policy with its cadence, and the versioning and changelog rules.

**Review rules**
- The path from a production trace to an eval item passes a **consent and retention check**, and the artifact says who owns it.
- New items go to **dev**. The held-out refresh is a deliberate, scheduled act, and refreshed items are never used for tuning.
- Random sampling is mixed with feedback-driven items, and the ratio is stated.
- Every added item records its source trace and the reason it was added.
- PII in promoted traces is handled per the 02.3 plan before the item is stored.

**Done when** you approve the flywheel, and the first batch of production-derived items is in the dev set.

---

### 06.7 Safety operations

```yaml task
id: "06.7"
title: Safety operations
role: AI
depends_on: ["06.0"]
estimate: {S: 1, M-L: 2}
artifact: safety-ops.md
optional_tag: null
sets_tags: []
```

**Plan** (`06.7-plan.md`): the guardrail review queries, the red-team refresh cadence, the post-incident process, and the leak checks to automate.

**Build**
- [ ] Set up the **guardrail-hit review**: new jailbreak or injection patterns, and false positives that annoy users
- [ ] Schedule the **red-team refresh** (e.g. quarterly): new public attack techniques, new tools `[A]`, new data sources `[R]`
- [ ] Define the **post-incident review**: root cause, a new regression case, and runbook updates — every time
- [ ] Automate the **PII / data-leak checks** on outputs and logs, and verify that log retention is enforced
- [ ] Define what makes a finding a **stop-the-line** event, and who calls it

**AI writes** `safety-ops.md`: the review queries and cadence, the red-team refresh plan, the post-incident template and where the record goes, the leak checks with their first run result, and the retention verification.

**Review rules**
- Guardrail review covers **both** directions: attacks getting through, and false positives blocking real users.
- Every post-incident review must produce a **regression case**. That is the rule, not a suggestion.
- The leak checks ran at least once, and the artifact gives the result.
- Log retention was **verified**, not assumed.
- The stop-the-line criterion names an authority (from the Phase 05 kill-switch owner).

**Done when** you approve the setup, and the leak checks have run.

---

### 06.8 Maintenance triggers & loop-back

```yaml task
id: "06.8"
title: Maintenance triggers & loop-back
role: HUMAN
depends_on: ["06.0"]
estimate: {S: 1, M-L: 3}
artifact: loop-back-table.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): repeat engineering & evaluation.*

**AI prepares** (`06.8-prep.md`)
- A **draft trigger table** (template below), each row with its evidence, owning phase, owner and release path:
  - A quality metric below its threshold → error analysis → Phase 02 or 03
  - Knowledge stale or missing → Phase 02
  - A new failure pattern the prompt can fix → Phase 03
  - Model deprecation, or a clearly better/cheaper model → a `migration` cycle
  - The KPI isn't moving, or the workflow has changed → Phase 01 (re-frame)
  - A new use case is requested → a **new** Phase 01, not a widened scope
- The **change-log format**, linking each change to its trigger and its evidence
- The **no-hotfix rule**, stated for agreement: no prompt or model change outside the pipeline, even during an incident — use the kill switch or a rollback instead
- The distinction between a **`change` cycle** (fix through owning phase → regression → pipeline) and reopening the task graph (`project active` + `--cascade`) for a real re-frame

**You do**
- [ ] Confirm each trigger, its owning phase and its owner
- [ ] Agree the no-hotfix rule with on-call and the RACI owners
- [ ] Decide what counts as a re-frame rather than a change
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `loop-back-table.md`: the trigger table with owners and release paths, the change-log location and format, the no-hotfix rule as agreed, and the re-frame criteria.

**Review rules**
- Every trigger names an **owning phase and an owner**, and its evidence source.
- Each fix path ends at the **04.11 regression suite and the 05.7 pipeline**. No path goes straight to production.
- The no-hotfix rule is agreed by on-call, with the kill switch and rollback named as the emergency tools.
- A new use case starts a **new Phase 01**, and the table says so.
- The re-frame criteria are concrete enough to tell a `change` cycle from reopening the pipeline.

**Done when** you approve the table, and on-call has agreed the no-hotfix rule.

---

### 06.9 Model migration playbook

```yaml task
id: "06.9"
title: Model migration playbook
role: AI
depends_on: ["06.8"]
estimate: {S: 2, M-L: 4}
artifact: migration-playbook.md
optional_tag: null
sets_tags: []
```

**Plan** (`06.9-plan.md`): the playbook's structure, and where the deprecation dates of every pinned model will be tracked.

**Build**
- [ ] Write the playbook **before** it is needed. It is triggered by a deprecation notice, or by a better/cheaper candidate
- [ ] Steps:
  1. Shortlist candidates against the Phase 03 hard filters
  2. Run them on dev
  3. Re-tune the prompts
  4. Run them on held-out with the calibrated judge
  5. Run the red-team set
  6. Load/cost test
- [ ] `[FT]` Decide whether to re-tune on the new base model, or drop fine-tuning. Re-run the escalation gate (03.9)
- [ ] Roll out through the Phase 05 pipeline: shadow → canary → full, with rollback to the old version until the provider's retirement date
- [ ] Track the **deprecation dates** of every pinned model (primary, fallback, judge, embedding `[R]`), and start migrating well before them
- [ ] Estimate the effort and cost of one migration, so it can be planned

**AI writes** `migration-playbook.md`: the step-by-step procedure with the artifacts each step produces, the deprecation tracker (model → version → retirement date → owner → migration start date), the `[FT]` and `[R]` special cases, and the estimated effort.

**Review rules**
- The playbook is **runnable by someone else**: each step names the command, the script or the task to reuse.
- The tracker lists **every** pinned model, including the judge and the embedding model `[R]`.
- Each migration start date leaves room before the retirement date, and that margin is stated.
- The rollout follows the Phase 05 pipeline, with rollback available until retirement.
- A migration re-runs the red-team set, not only the quality suite.

**Done when** you approve the playbook, and every pinned model has a tracked retirement date or a flagged "unknown".

---

### 06.10 Review cadence & start operations

```yaml task
id: "06.10"
title: Review cadence & start operations
role: DECISION
depends_on: ["06.1", "06.2", "06.3", "06.4", "06.5", "06.6", "06.7", "06.9"]
estimate: {S: 1, M-L: 2}
artifact: null
optional_tag: null
sets_tags: []
```

**Brief** (`06.10-brief.md`)
- The **monitoring readiness walk-through**: each setup task, what it produced, and its first real output
- The **ongoing gate** below, walked for the first time
- The **cycle calendar**: when the monthly and quarterly cycles run, who runs them, and what triggers a `migration`, `change` or `incident` cycle
- The open issues from Phase 05 that operations inherits, with owners
- What would bring the project **back into the pipeline** (a re-frame) rather than into a `change` cycle

**Options**
- **Start operations**: monitoring is live and owned. The project moves to `operating`, and the work continues as cycles.
- **Start operations with conditions**: name the gaps, their owners and their dates.
- **Back to task X**: a setup task isn't really done. Reset it with `--cascade`.
- **Retire now**: the system should not run. Record why, and set the project to `completed` after the retirement checklist in the `quarterly` cycle.

End the brief with **AI recommendation:** `<option>`, followed by its reasoning.

**Decision record**: a `## 06.10` entry in `decisions.md` with the cadence, the owners, the inherited issues and the conditions. Then `set 06.10 done`, and `project operating`.

---

## Cycles

Each block below defines a cycle kind. `/genai cycle start <kind>` copies the checklist under it into `.genai/ops/<date>-<kind>.md`, where the run is recorded; `/genai cycle close <file> --hours N` closes it. The **Findings** and **Actions & loop-backs** sections are filled in as the cycle runs, and every action routes through the 06.8 table.

```yaml cycle
kind: monthly
title: Monthly health review
estimate: {S: 11, M-L: 29}
```

- [ ] **SLOs** (06.1): attainment, error budget left, alerts that fired, and any threshold to adjust with its owner
- [ ] **Online quality** (06.2): the weekly samples for this month, scored per case type and segment against the Phase 04 levels; judge–SME agreement; recalibrate the judge (04.2) if it has drifted
- [ ] **Quality proxies**: feedback, edit rate, escalations, refusals, citation rate `[R]`, task success and approval-rejection rate `[A]`
- [ ] **Drift** (06.3): inputs, knowledge `[R]`, model/provider, tools `[A]`, usage — route every finding through the loop-back table
- [ ] **KPI & value** (06.4): KPI against the baseline, adoption, value against cost, counter-metrics; send the report to the sponsor
- [ ] **Cost & capacity** (06.5): cost per task trend, spend against budget, savings to try (each through the regression suite), quota and renewal headroom
- [ ] **Flywheel** (06.6): triage the month's feedback and failing traces, add eval items to dev, check the held-out refresh status
- [ ] **Safety** (06.7): guardrail hits and false positives, new attack patterns, incidents and their post-incident actions, leak checks
- [ ] **Deprecations** (06.9): any pinned model approaching retirement → start a `migration` cycle
- [ ] Write the **monthly health report** (template below) and record the decisions and asks

```yaml cycle
kind: quarterly
title: Quarterly review & retirement decision
estimate: {S: 3, M-L: 8}
```

- [ ] Review the quarter: SLOs, quality trends, KPI/value, and cost
- [ ] Update the **system card**: known limitations, models, and data sources
- [ ] Review **access**: who can use it, change it, and see the logs
- [ ] Review **compliance**: new regulations or policies, and whether the provider terms changed
- [ ] Check the **judge calibration** and the **held-out refresh** status
- [ ] Refresh the **red-team cases** (06.7)
- [ ] Walk the **ongoing gate** below
- [ ] Decide: **continue / improve (loop back) / expand (new Phase 01) / retire**
- [ ] When retiring:
  - [ ] Tell the users, and restore or replace the workflow
  - [ ] Delete or archive the data, indexes `[R]`, and logs according to the retention rules
  - [ ] Revoke the credentials and tool access `[A]`
  - [ ] Update the registry
  - [ ] Record the decision in `decisions.md`, then `project completed`

```yaml cycle
kind: migration
title: Model migration
estimate: {S: 8, M-L: 24}
```

Follow `migration-playbook.md` (06.9). The checklist here is its summary:

- [ ] Record the trigger: a deprecation notice, or a better/cheaper candidate, with its evidence and the retirement date
- [ ] Shortlist candidates against the Phase 03 hard filters (03.1)
- [ ] Run them on the **dev** set with the existing prompts
- [ ] Re-tune the prompts for the new model (03.5 method), and record the versions
- [ ] Run the **held-out** set with the calibrated judge, and count the use (04.3)
- [ ] Run the **red-team** set (04.5) and the regression suite (04.11)
- [ ] Load and cost test at peak (04.8)
- [ ] `[FT]` Re-run the escalation gate (03.9): re-tune on the new base model, or drop fine-tuning
- [ ] Roll out through the Phase 05 pipeline: shadow → canary → full, keeping rollback available until the retirement date
- [ ] Update the frozen config, the system card and the deprecation tracker
- [ ] Log the change with its trigger and evidence

```yaml cycle
kind: change
title: Loop-back change
estimate: {S: 2, M-L: 6}
```

For a fix that the loop-back table (06.8) routes to an earlier phase without re-framing the project.

- [ ] Record the **trigger and its evidence**, and the owning phase from the loop-back table
- [ ] Confirm this is a change, not a re-frame. A re-frame reopens the pipeline instead: `project active`, then `set <task> todo --cascade`
- [ ] Make the fix in the owning phase's terms (knowledge/retrieval → Phase 02; prompt/model/tools → Phase 03), using that task's review rules
- [ ] Confirm on the **dev** set first
- [ ] Run the **regression suite** (04.11). It is the gate
- [ ] Release through the **pipeline** (05.7): shadow/canary if the change is significant
- [ ] Add a regression case that would have caught the problem
- [ ] Update the affected artifacts (system card, frozen config, eval set) and the change log

```yaml cycle
kind: incident
title: Incident response & post-incident review
estimate: {S: 1, M-L: 3}
```

- [ ] Follow the runbook for this incident type (05.11). **No hotfix outside the pipeline** — use the kill switch or a rollback
- [ ] Record the timeline: detection, actions taken, who acted, and when it was resolved
- [ ] Root-cause it, and name the owning phase
- [ ] Add a **regression case** that would have caught it (04.11)
- [ ] Update the runbook with what was actually needed
- [ ] Decide whether a `change` cycle follows
- [ ] Inform the affected users and the stakeholders, per the communication plan

---

## Quality assurance

### Requirements & constraints

- Every signal in the monitoring plan has a threshold, an owner, and an action.
- Production quality is measured regularly with the calibrated judge **and** SME spot-checks, per case type and segment.
- Drift is detected on inputs, knowledge `[R]`, model/provider, tools `[A]`, and usage.
- The KPI and value are reported to the sponsor against the baseline.
- Every production change goes through the owning phase → regression suite → release pipeline, and is logged.
- The eval set grows from real failures while keeping the dev/held-out split intact.
- Every pinned model has a known deprecation date and a migration plan.

### Risks → QA measures

| Risk | QA measure | Task / cycle |
|------|------------|--------------|
| Model staleness: quality decays without anyone noticing | Weekly sampled online eval + quality proxies vs thresholds | 06.2, `monthly` |
| Dependency changes: hardware/software, provider, tool APIs | Model/provider and tool drift checks, pinned versions, deprecation tracking | 06.3, 06.9 |
| No labels in production, so quality is unknown | Judge scoring + SME spot-checks + proxies | 06.2 |
| Judge drifts or becomes miscalibrated | Periodic judge–SME agreement check, recalibration | 06.2, `quarterly` |
| Knowledge goes stale `[R]` | Freshness SLA monitoring, retrieval-miss trend | 06.3 |
| Forced, rushed migration on deprecation | Migration playbook written in advance, deprecation dates tracked | 06.9, `migration` |
| Cost creep | Monthly cost review, optimizations gated by the regression suite | 06.5, `monthly` |
| Value not realized (usage without impact) | KPI, adoption and counter-metrics reported to the sponsor | 06.4 |
| Eval set becomes stale or unrepresentative | Flywheel from real failures + random samples, held-out refresh | 06.6 |
| Feedback bias skews priorities | Combine feedback with random sampling | 06.6 |
| Production data used without consent | Consent/retention check before adding to eval or training | 06.6 |
| New attack patterns | Guardrail-hit review, periodic red-team refresh | 06.7, `quarterly` |
| Unsafe hotfixes bypass quality gates | Pipeline-only changes, kill switch/rollback for emergencies, change log | 06.8, `incident` |
| Scope creep through the back door | New use cases start a new Phase 01 | 06.8 |
| Alert fatigue hides real problems | Alert tuning, SLOs, every alert tied to a runbook | 06.1 |
| A zombie system nobody owns | Quarterly review with a continue/retire decision, retirement checklist | `quarterly` |

### Ongoing gate (walked in 06.10, then at each quarterly review)

- [ ] SLOs are met, or an error-budget action is under way.
- [ ] Online quality is at or above its thresholds per case type, and the judge is still calibrated.
- [ ] No unhandled drift findings are open.
- [ ] The KPI and value are reported, and the sponsor confirms the system should continue.
- [ ] Cost is within budget.
- [ ] The eval set has been updated from production this quarter, and the held-out set is still unseen.
- [ ] All pinned models are ≥ 1 quarter away from deprecation, or their migration is under way.
- [ ] The system card, access list and compliance status are current.

---

## Templates

### Monitoring plan

| Signal | Metric | Threshold | Cadence | Owner | Action on breach (runbook / loop-back) |
|--------|--------|-----------|---------|-------|----------------------------------------|
| Availability | | | | | |
| Latency | p95 | | | | |
| Online quality | judge score per case type | | weekly | | |
| Quality proxies | feedback, edits, escalations | | | | |
| Knowledge freshness `[R]` | | | | | |
| Cost | cost/task, monthly spend | | | | |
| Business KPI | | | monthly | | |

### Loop-back triggers

| Trigger | Evidence | Loop back to | Owner | Release path |
|---------|----------|--------------|-------|--------------|
| Quality below threshold | online eval report | 02 / 03 | | 04 regression → 05 pipeline |
| Knowledge stale `[R]` | freshness / miss rate | 02 | | |
| Model deprecation / better model | provider notice / benchmark | `migration` cycle | | shadow → canary |
| KPI not moving | KPI report | 01 (re-frame) | | |
| New use case | request | new 01 | | |

### Monthly health report

```text
Period:
SLOs:               met / missed (which, error budget left)
Online quality:     per case type vs threshold; judge–SME agreement
Proxies:            feedback, edits, escalations, refusals, citations [R], task success [A]
Drift:              inputs / knowledge [R] / model-provider / tools [A] / usage
KPI & value:        KPI vs baseline, adoption, value vs cost
Cost:               cost/task, spend vs budget, optimizations done
Safety:             incidents, guardrail trends, new attack patterns
Eval set:           items added, held-out refresh status
Changes shipped:    (from change log)
Deprecations:       pinned models and dates
Decisions / asks:
```
