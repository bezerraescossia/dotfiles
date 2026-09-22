# Phase 05: Deployment

> Put the evaluated configuration in front of real users safely. Validate it under production conditions, roll it out gradually against pre-set rollback criteria, and hand over a system that can be operated.

**CRISP-ML(Q) origin:** *Model Deployment*. What changes for GenAI:
- The deployable unit is a **configuration**, not just a model: model IDs, prompt versions, index version, tools, and limits. Prompt and model changes go through the same release pipeline as code.
- **Runtime guardrails**, **cost caps** and **rate limits** become part of the deployment itself.
- **Fallback** means switching to another model or provider, degrading gracefully, or handing off to a human.
- **Governance** covers the authority boundaries from the spec: what the system may do, and what needs human approval.
- **Inference hardware** matters only when self-hosting. With managed APIs, the questions are quotas, provisioned throughput, and region.

**Scope boundaries**
- **This phase owns:** serving and integration, runtime guardrails, resilience, **observability instrumentation** (the canary needs it), the release pipeline, shadow/canary/A/B tests, user acceptance, and the operations handover.
- **[Phase 04](04-evaluation.md) owns:** offline evaluation and the deployment decision this phase carries out.
- **[Phase 06](06-monitoring-maintenance.md) owns:** ongoing monitoring, drift handling, and maintenance after the full rollout.

**Inputs from Phase 04:** evaluation report and deployment decision (with conditions), automated regression suite, fallback quality, load & cost results, online metrics to watch. From Phase 03: frozen configuration, system card, authority map `[A]`. From Phase 02: sensitivity & access-control plan, freshness policy `[R]`. From Phase 01: business KPI, baseline, stakeholder map.

## How this file is used

Every task below is **executable with `/genai`**. The roles work as in [Phase 02](02-context-engineering.md): HUMAN (*AI prepares / You do / AI turns into / Review rules / Done when*), AI (*Plan / Build / Review rules / Done when*), DECISION (*Brief / Options / Decision record*).

Artifacts go to `.genai/artifacts/05-deployment/`; infrastructure, application and pipeline code live in the project repo. **This phase touches production.** An AI task's plan must name every production-affecting step, and you approve it before anything is deployed. Rollouts and rollbacks are triggered by the named owner, never by the AI on its own.

## Tags

No whole task is optional. Items tagged `[R]` (retrieval), `[A]` (tools/agents) or `[SH]` (self-hosted models) apply only when that tag is on — 02.0 sets `[R]`, 03.0 sets `[A]`, and 03.4b sets `[SH]`.

## Task graph

| Task | Title | Role | Depends on | S | M-L |
|------|-------|------|------------|---|-----|
| 05.0 | Handoff review & release plan | HUMAN | 04.12 | 1h | 3h |
| 05.1 | Serving architecture & infrastructure | AI | 05.0 | 3h | 10h |
| 05.2 | Application integration | AI | 05.1 | 4h | 12h |
| 05.3 | Runtime guardrails & controls | AI | 05.2 | 3h | 8h |
| 05.4 | Resilience & fallback | AI | 05.2 | 2h | 6h |
| 05.5 | Observability instrumentation | AI | 05.2 | 3h | 8h |
| 05.6 | Security & compliance review | HUMAN | 05.3, 05.4, 05.5 | 2h | 6h |
| 05.7 | Release pipeline (CI/CD for configs) | AI | 05.5 | 3h | 8h |
| 05.8 | Shadow mode | HUMAN | 05.6, 05.7 | 2h | 5h |
| 05.9 | Gradual rollout (canary / A/B) | HUMAN | 05.8 | 3h | 8h |
| 05.10 | User acceptance & enablement | HUMAN | 05.8 | 2h | 6h |
| 05.11 | Governance & operations handover | HUMAN | 05.9, 05.10 | 2h | 5h |
| 05.12 | Launch decision → Phase 06 | DECISION | 05.11 | 1h | 2h |
| | **Total** | | | **~31h (~4 days)** | **~87h (~2 weeks)** |

- Hours are **your hands-on effort**. **Calendar time is dominated by the rollout**: shadow mode and each canary/A/B stage need enough traffic and days to be meaningful, often **1–4 weeks elapsed**. 05.1 and 05.2 vary the most, depending on the existing platform and the integration targets.
- **S**: internal users, managed model API, existing platform, one integration. **M-L**: customer-facing, several integrations, per-user permissions, self-hosting or strict compliance.

---

## Tasks

### 05.0 Handoff review & release plan

```yaml task
id: "05.0"
title: Handoff review & release plan
role: HUMAN
depends_on: ["04.12"]
estimate: {S: 1, M-L: 3}
artifact: release-plan.md
optional_tag: null
sets_tags: []
```

**AI prepares** (`05.0-prep.md`)
- A **re-read summary** of the evaluation report and the **deployment decision**, listing every condition it carries (e.g. human review of all outputs, limited user group)
- A **draft staged rollout**: shadow → internal users → small % of traffic → wider → 100%, with a proposed minimum duration and volume per stage
- **Draft go / hold / rollback criteria** per stage, derived from the Phase 04 weak spots: quality proxies, guardrail hit rate, error rate, latency, cost per task, user feedback, the business KPI
- An **owner list to fill**: release owner, on-call, and who may trigger a rollback
- A **communication plan draft** for the Phase 01 stakeholders

**You do**
- [ ] Confirm the stages, their durations and their traffic shares
- [ ] Fix the **go / hold / rollback criteria in advance**, with numbers
- [ ] Name the release owner, the on-call, and who may trigger a rollback
- [ ] Agree the communication plan with the stakeholders
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `release-plan.md`: the stage table (template below), the conditions carried from 04.12 with their owners, the named roles, and the communication plan.

**Review rules**
- Every stage has **numeric** go / hold / rollback criteria, fixed before the rollout starts.
- Every condition from the 04.12 decision appears with an owner and a lifting criterion.
- The rollback trigger names a **person or role**, and rollback needs no AI involvement.
- Each stage has a minimum duration **and** a minimum volume, so a quiet week can't pass as success.
- The KPI measurement plan for the A/B stage is stated.

**Done when** you approve the release plan, and the owners have accepted their roles.

---

### 05.1 Serving architecture & infrastructure

```yaml task
id: "05.1"
title: Serving architecture & infrastructure
role: AI
depends_on: ["05.0"]
estimate: {S: 3, M-L: 10}
artifact: serving-architecture.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): inference hardware.*

**Plan** (`05.1-plan.md`): the target architecture, the IaC tool and repo location, **every resource that will be created and what it costs**, the environments, and the approvals it needs from you (cloud account, spend, provisioned throughput commitments).

**Build**
- [ ] Confirm the hosting paradigm from 03.4b: managed API vs self-hosted `[SH]`
- [ ] Choose the **inference mode** for each use: real-time, streaming, async, or **batch** (cheaper when no one is waiting)
- [ ] Size the capacity for the 04.8 peak load:
  - [ ] Managed: quotas and limits, **provisioned vs on-demand throughput**, cross-region options
  - [ ] `[SH]` Instance/GPU type, autoscaling policy, cold-start behavior, and model-loading time
- [ ] Deploy the vector store / index serving with the right capacity, backups, and a way to swap index versions `[R]`
- [ ] Set up separate **environments** (dev / staging / prod) with the same configuration shape
- [ ] Define everything as **infrastructure as code**. Keep secrets (API keys, credentials) in a secrets manager, never in prompts or code
- [ ] Make sure the model is referenced by a **pinned version**, not a floating alias the provider can silently update

**AI writes** `serving-architecture.md`: the architecture and its IaC repo paths, the capacity sizing with the 04.8 numbers behind it, the environment layout, the secrets handling, the pinned model references, and the monthly infrastructure cost.

**Review rules**
- Every resource is defined **as code**, and the artifact says how to recreate the environment from scratch.
- Capacity is sized against the **measured** 04.8 peak, not a guess.
- No secret appears in code, prompts, logs or the artifact. Say where secrets live.
- Models are referenced by pinned version everywhere, including the fallback and the judge.
- Staging matches prod in shape, and the differences that remain are listed.
- Nothing was deployed to production beyond what the approved plan named.

**Done when** you approve the architecture, and staging is up.

---

### 05.2 Application integration

```yaml task
id: "05.2"
title: Application integration
role: AI
depends_on: ["05.1"]
estimate: {S: 4, M-L: 12}
artifact: integration.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): integration with existing systems.*

**Plan** (`05.2-plan.md`): the API contract, which systems and UI surfaces are touched, the identity-propagation design, the UX states to build, and what it needs from you (access to the host application, design review, a test tenant).

**Build**
- [ ] Define the **API contract**: request/response schemas, streaming, timeouts, error codes, versioning
- [ ] Integrate with the systems of record and the UI **where the workflow happens** (from the Phase 01 workflow map), not in a separate tool nobody opens
- [ ] **Pass the user's identity through the whole chain**: authentication → retrieval ACL filter `[R]` → tool permissions `[A]`. The system must never act with more rights than the user has
- [ ] Design the **UX for GenAI states**: streaming/progress, "I don't know", citations/sources `[R]`, low-confidence warnings, fallback/degraded notices, and the hand-off to a human
- [ ] Build the **human approval UI** for Locked actions `[A]`: show what will happen, and let the user approve or reject, with an audit log
- [ ] Make writes to other systems **idempotent** (safe retries) `[A]`
- [ ] Add integration tests for the full path in staging

**AI writes** `integration.md`: the API contract, the integration points with their repo paths, the identity-propagation design with the enforcement point at each hop, the UX states, the approval UI, and the staging test results.

**Review rules**
- Identity propagation is **tested**, including a negative test: user A cannot reach user B's data `[if ACLs apply]`.
- The integration sits in the workflow the Phase 01 map describes. If it doesn't, say why.
- Every GenAI state has a UI treatment, including "I don't know" and degraded mode.
- Locked actions cannot be executed without the approval UI, and the audit log records them `[A]`.
- Full-path integration tests pass **in staging**, and the artifact names the run.

**Done when** you approve the integration, and the staging tests pass.

---

### 05.3 Runtime guardrails & controls

```yaml task
id: "05.3"
title: Runtime guardrails & controls
role: AI
depends_on: ["05.2"]
estimate: {S: 3, M-L: 8}
artifact: guardrail-inventory.md
optional_tag: null
sets_tags: []
```

**Plan** (`05.3-plan.md`): the guardrails to build, the caps and their proposed values (marked as proposals for you to set), the kill-switch mechanism, and how false positives will be measured.

**Build**
- [ ] **Input guardrails**: PII detection/redaction, prompt-injection detection, topic/scope filters, input size limits
- [ ] **Output guardrails**: PII and secret leakage, toxicity / policy filters, **schema validation**, and a citation/grounding check if it is cheap enough `[R]`
- [ ] **Rate limits** per user/tenant, and **cost caps** per request, per user, and per day, with alerts before a cap is hit
- [ ] Enforce the agent **limits** at runtime: max steps, timeouts, budget per task `[A]`
- [ ] Add a **kill switch / feature flag** to turn the feature (or a single tool `[A]`) off instantly, without a deploy
- [ ] Decide what the user sees when a guardrail blocks: a clear message, not a silent failure
- [ ] Measure each guardrail's **false-positive rate** on the Phase 04 held-out results, so it doesn't block legitimate use

**AI writes** `guardrail-inventory.md` (template below): every control with its trigger, action, user message, measured false-positive rate and owner, plus the kill-switch procedure and who may use it.

**Review rules**
- Every 04.5 red-team finding with a "guardrail" mitigation has a **live control** here, and the artifact maps one to the other.
- Cap and limit values are **yours**, not AI defaults.
- False-positive rates are **measured** on the 04.3 outputs, and a noisy guardrail is reported rather than shipped quietly.
- The kill switch was **tested** in staging, and it works without a deploy.
- A blocked request gives the user a clear message, and the trace records the hit.

**Done when** you approve the inventory, and the kill switch has been tested.

---

### 05.4 Resilience & fallback

```yaml task
id: "05.4"
title: Resilience & fallback
role: AI
depends_on: ["05.2"]
estimate: {S: 2, M-L: 6}
artifact: resilience-design.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): fallback strategies.*

**Plan** (`05.4-plan.md`): the failure modes to handle, the fault-injection tests to run **in staging**, and the acceptance bar for each degraded mode.

**Build**
- [ ] Handle retries with exponential backoff for transient errors and throttling
- [ ] Add **circuit breakers** to stop sending traffic to a failing dependency
- [ ] Route to the **fallback model** (quality known from 04.6) when the primary is down or throttled
- [ ] Define **graceful degradation** per dependency:
  - [ ] Retrieval down: answer with a limited scope, or disable the feature `[R]`
  - [ ] A tool down: disable that capability, and tell the user `[A]`
- [ ] Always have a **human hand-off path** for when the system can't help
- [ ] **Test failover in staging**: kill the primary model, the retrieval, and the tools, and check the behavior matches the design

**AI writes** `resilience-design.md`: the retry/backoff and circuit-breaker settings, the fallback routing rules, the degradation behavior per dependency, the hand-off path, and the **failover test results** with run ids.

**Review rules**
- Every dependency in the architecture has a defined degraded mode, including "disable the feature".
- Failover was tested by **inducing** each failure in staging, not designed on paper.
- The fallback model's quality (from 04.6) is stated next to the routing rule, so the degraded quality is known.
- Retries cannot amplify load or cost. Show the bound.
- The human hand-off works from every degraded mode.

**Done when** you approve the design, and the failover tests pass in staging.

---

### 05.5 Observability instrumentation

```yaml task
id: "05.5"
title: Observability instrumentation
role: AI
depends_on: ["05.2"]
estimate: {S: 3, M-L: 8}
artifact: observability.md
optional_tag: null
sets_tags: []
```

**Plan** (`05.5-plan.md`): the trace schema (from 03.8), the storage and retention design against the 02.3 sensitivity plan, the dashboards and alerts to build, and the replay interface Phase 06 needs.

**Build**
- [ ] **Trace every request**, recording:
  - [ ] Config version (model ID, prompt version, index version)
  - [ ] Retrieved chunk IDs `[R]`
  - [ ] Tool calls and their results `[A]`
  - [ ] Guardrail hits
  - [ ] Tokens, latency, and cost
  - [ ] The final output
- [ ] **Log in line with the sensitivity plan**: redact PII, set a retention period, restrict who can see the logs
- [ ] Build **dashboards**: traffic, error rate, latency p50/p95, cost per task and per day, guardrail hit rate, fallback rate, and quality proxies (refusal rate, citation rate, feedback)
- [ ] Set **alerts** on the rollback criteria from the release plan, and on the cost caps
- [ ] Capture **user feedback** (thumbs, corrections, "report a problem"), linked to the trace ID
- [ ] Make it possible to **replay** a sampled trace through the Phase 04 regression suite / judge. Phase 06 depends on this

**AI writes** `observability.md`: the trace schema (template below), where traces are stored with their retention and access rules, the dashboard links, the alert list mapped to the release-plan criteria, the feedback capture, and the replay procedure with a demonstration run.

**Review rules**
- The trace carries everything the release-plan criteria and Phase 06 need. Map each criterion to a field.
- Logging matches the 02.3 sensitivity plan: redaction, retention and access are stated and enforced. Show a redaction test.
- Every rollback criterion has an **alert**, and the alert points to a runbook (05.11).
- Feedback is linked to the trace id, so a complaint can be investigated.
- **Replay works**: a sampled trace was actually replayed through the regression suite.

**Done when** you approve the instrumentation, and a replayed trace produces a score.

---

### 05.6 Security & compliance review

```yaml task
id: "05.6"
title: Security & compliance review
role: HUMAN
depends_on: ["05.3", "05.4", "05.5"]
estimate: {S: 2, M-L: 6}
artifact: security-signoff.md
optional_tag: null
sets_tags: []
```

**AI prepares** (`05.6-prep.md`)
- A **review pack**: endpoints, authentication, network paths, secrets handling, and the guardrail inventory
- The **actual data-flow map**, traced from the code: what reaches the model provider, the logs, and third parties — next to what the 02.3 plan assumed, with the differences highlighted
- A **provider-agreement checklist**: data-processing agreement, data-usage and retention terms, against what Phase 01/03 assumed
- The **audit-logging evidence** for consequential actions and approvals `[A]`
- A **compliance paperwork checklist** (e.g. DPIA, AI risk assessment, records of processing), with the parts that can be pre-filled from existing artifacts

**You do**
- [ ] Get the security review done
- [ ] Confirm the data flows and the provider agreements with whoever owns them
- [ ] Complete the compliance paperwork required in your org
- [ ] Get **sign-off** from the security / compliance contacts
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `security-signoff.md`: the findings with their severity and fix status, the confirmed data flows, the provider agreement status, the paperwork completed, and the sign-off with names and dates.

**Review rules**
- The data-flow map is derived from the **code**, and every difference from the 02.3 plan is resolved or accepted in writing.
- Every finding has a severity, an owner and a status. Open high findings block the rollout.
- Provider agreements are confirmed, not assumed.
- Audit logging for consequential actions is **demonstrated** `[A]`.
- Sign-off carries names and dates. "Verbally agreed" is a gap.

**Done when** you approve the record, and the security/compliance contacts have signed off.

---

### 05.7 Release pipeline (CI/CD for configurations)

```yaml task
id: "05.7"
title: Release pipeline (CI/CD for configurations)
role: AI
depends_on: ["05.5"]
estimate: {S: 3, M-L: 8}
artifact: release-pipeline.md
optional_tag: null
sets_tags: []
```

**Plan** (`05.7-plan.md`): the pipeline stages, where the regression gate runs, the promotion path, the rollback mechanism, and the permissions it needs.

**Build**
- [ ] Treat **prompts, model IDs, params, index versions, tool definitions and guardrail configs as versioned config**, deployed through the pipeline and never edited by hand in production
- [ ] Run the **Phase 04 regression suite as a blocking gate** on every change
- [ ] Promote the **same artifacts** dev → staging → prod
- [ ] Set up **one-step rollback** to the previous known-good configuration, and test it
- [ ] Record every release: what changed, the regression results, and who approved it

**AI writes** `release-pipeline.md`: the pipeline definition and its repo path, what the gate blocks on, the promotion path, the rollback procedure **with its test result**, and the release record format.

**Review rules**
- A prompt or model change **cannot** reach production without passing the gate. Show a blocked run.
- Rollback was **executed** in staging, and the artifact records how long it took.
- The same artifact is promoted between environments — no rebuild per environment.
- Every release writes a record with the regression results and the approver.
- Hand edits in production are impossible, or the remaining path is named as a risk with a mitigation.

**Done when** you approve the pipeline, and a test release plus a rollback have both run.

---

### 05.8 Shadow mode

```yaml task
id: "05.8"
title: Shadow mode
role: HUMAN
depends_on: ["05.6", "05.7"]
estimate: {S: 2, M-L: 5}
artifact: shadow-results.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): evaluate in production conditions.*

**AI prepares** (`05.8-prep.md`)
- The **shadow setup**: how real traffic is mirrored without showing outputs to users (or showing them only to reviewers), and what it costs per day
- The **comparison plan**: against the current workflow's outcomes and the Phase 04 expectations, plus a **distribution-shift check** between the eval set and real inputs
- A **sampling and spot-check protocol** for SMEs, with the sample size and the schedule
- The **go/fix criteria** from the release plan, restated for this stage
- A note on **how long** shadow mode must run to be meaningful (volume and days)

**You do**
- [ ] Turn shadow mode on, and let it run for the agreed period
- [ ] Have SMEs spot-check the sampled traces
- [ ] Put the observations, the sample results and your notes in `.genai/inbox/`

**AI turns into** `shadow-results.md`: the replayed/judged quality on shadow traces, the **distribution shift** against the eval set, the real latency, cost per task and guardrail hit rates, the surprising real inputs found, and the go/fix recommendation against the stage criteria.

**Review rules**
- No shadow output reached a user. Say how that was guaranteed.
- The shadow period met the **minimum duration and volume** in the release plan.
- The distribution shift is quantified, and a large one sends items back to the eval set before the canary.
- Real cost and latency are compared with the 04.8 projections, and differences are explained.
- Surprising inputs are added to the **dev** set (and queued for a future held-out refresh), not silently discarded.

**Done when** you approve the results, and the stage criteria are met or the fixes are agreed.

---

### 05.9 Gradual rollout (canary / A/B)

```yaml task
id: "05.9"
title: Gradual rollout (canary / A/B)
role: HUMAN
depends_on: ["05.8"]
estimate: {S: 3, M-L: 8}
artifact: rollout-log.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): online testing, deployment strategy.*

**AI prepares** (`05.9-prep.md`)
- A **per-stage checklist** from the release plan: audience, traffic share, duration, volume, and the go / hold / rollback criteria
- The **A/B design** against the current workflow on the Phase 01 **business KPI**: assignment, sample size, and how long it must run to decide
- The **leading indicators** to watch daily: user feedback, guardrail hits, fallback rate, cost per task, escalations to humans
- A **rollback drill reminder**: who triggers it, and what happens to in-flight work
- The **conditions from 04.12** that stay in force, and what evidence would justify lifting them

**You do**
- [ ] Promote stage by stage through the pipeline, following the release plan
- [ ] At each stage, check the criteria and **write down the decision** (go / hold / rollback)
- [ ] Run the A/B test with enough traffic and time to decide
- [ ] **Roll back** as soon as a criterion is breached, investigate, and re-promote only through the pipeline
- [ ] Keep the 04.12 conditions in force until the evidence justifies lifting them
- [ ] Put the stage numbers, decisions and notes in `.genai/inbox/`

**AI turns into** `rollout-log.md`: one entry per stage (dates, traffic, the criteria with their measured values, the decision and who made it), the A/B result on the KPI with its confidence, the incidents and rollbacks, and the status of each 04.12 condition.

**Review rules**
- Every stage records its **measured** criteria values and an explicit decision with a named owner.
- A stage that ran shorter than planned is flagged, not averaged away.
- The A/B result reports the KPI **against the Phase 01 baseline**, with the sample size and the confidence — and says plainly when it is inconclusive.
- Every rollback is recorded with its cause and what changed before re-promotion.
- Conditions from 04.12 are still enforced, or their lifting is recorded with the evidence and who approved it.

**Done when** you approve the log, and the current stage's criteria are met.

---

### 05.10 User acceptance & enablement

```yaml task
id: "05.10"
title: User acceptance & enablement
role: HUMAN
depends_on: ["05.8"]
estimate: {S: 2, M-L: 6}
artifact: [uat-findings.md, user-guide.md]
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): user acceptance & usability.*

**AI prepares** (`05.10-prep.md`)
- A **UAT protocol**: real users, real tasks, taken from the Phase 01 workflow map, with the friction points it should remove
- **Over-trust and under-trust probes**: tasks with a planted wrong output to see whether users catch it, and observation of work redone by hand
- A **draft user guide**: what the system does and doesn't do, the known limitations from the system card, how to check an output, how to report problems
- A **change-management briefing** for workflow owners and managers
- The consent note for observation sessions

**You do**
- [ ] Run UAT with real users on real tasks
- [ ] Watch for over-trust (accepting wrong outputs) and under-trust (redoing everything by hand)
- [ ] Brief the workflow owners and managers
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `uat-findings.md` (what fitted the workflow, the friction removed or added, over/under-trust observations, and the findings routed as fixes, eval items or known limitations) and `user-guide.md` (the published guide).

**Review rules**
- UAT used **real tasks** from the workflow map, with practitioners, not a demo script.
- Over-trust was actively probed, and the result is reported even when it is uncomfortable.
- The user guide's limitations match the system card, in the users' language.
- Every finding is routed: fix, eval item, or known limitation with an owner.
- The guide says how to report a problem, and that path exists.

**Done when** you approve the findings, and the user guide is published.

---

### 05.11 Governance & operations handover

```yaml task
id: "05.11"
title: Governance & operations handover
role: HUMAN
depends_on: ["05.9", "05.10"]
estimate: {S: 2, M-L: 5}
artifact: [runbooks.md, governance.md]
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): model governance.*

**AI prepares** (`05.11-prep.md`)
- A **registry entry draft**: config versions, system card, owner, data sources, risk level, approvals
- **Draft runbooks** (template below) for the likely incidents: provider outage / throttling, quality drop, harmful or wrong output reported, data or PII leak, prompt injection in the wild, cost spike, and a tool misfiring `[A]` — each built from the real alerts and dashboards from 05.5
- An **on-call and incident-process draft**, including who may use the kill switch
- A **RACI draft** for changes: who may change prompts, models, sources, tools and guardrails, and who approves
- A **deprecation watch list**: every pinned model version (primary, fallback, judge, embedding `[R]`) with its retirement date

**You do**
- [ ] Register the system in the model/system registry
- [ ] Walk the runbooks with the people who will use them, and correct them
- [ ] Set up on-call and the incident process
- [ ] Agree the RACI with the owners
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `runbooks.md` (one runbook per incident type) and `governance.md` (the registry entry, the on-call rota and incident process, the RACI, and the deprecation watch list with dates).

**Review rules**
- Every alert from 05.5 points to a runbook, and every runbook names its detection signal.
- Runbooks were **walked with the people who will run them**, and their corrections are in.
- The RACI names people or roles for every change type, including prompts.
- The kill switch has a named authority and a written trigger condition.
- Every pinned model version has a retirement date, or "unknown" flagged for the Phase 06 deprecation watch.

**Done when** you approve the runbooks and the governance record, and on-call is live.

---

### 05.12 Launch decision → Phase 06

```yaml task
id: "05.12"
title: Launch decision → Phase 06
role: DECISION
depends_on: ["05.11"]
estimate: {S: 1, M-L: 2}
artifact: null
optional_tag: null
sets_tags: []
```

**Brief** (`05.12-brief.md`)
- The **exit gate walk-through** below, item by item, citing artifacts
- The rollout status: stages passed, the KPI result, and the open conditions
- The open issues to hand to Phase 06, each with an owner
- The **handoff to [Phase 06](06-monitoring-maintenance.md)**: dashboards, alerts, tracing and replay, feedback capture, runbooks, on-call, RACI, the KPI baseline from the A/B test, and the open issues

**Options**
- **Full rollout**: go to 100%, per the release plan.
- **Hold at the current stage**: name the reason and what would change it.
- **Roll back and fix**: reset the owning task with `--cascade`.
- **Stop**: the system doesn't deliver the KPI, or a blocker cannot be mitigated.

End the brief with **AI recommendation:** `<option>`, followed by its reasoning.

**Decision record**: a `## 05.12` entry in `decisions.md` with the decision, the KPI evidence, the conditions still in force, the open issues with owners, and who signed off.

---

## Quality assurance

### Requirements & constraints

- The **deployed configuration is identical** to the evaluated one (same pinned versions), or any change has passed the regression suite.
- The user's identity and permissions are enforced end to end: retrieval ACL `[R]`, tool permissions `[A]`.
- Guardrails, rate limits, cost caps, agent limits `[A]`, and the kill switch are live and tested.
- Failover to the fallback model, graceful degradation, and human hand-off were tested in staging.
- Every request is traced, logs follow the sensitivity plan, and user feedback is linked to traces.
- Every change goes through the pipeline with the regression gate, and rollback has been tested.
- The rollout followed its pre-set criteria, and the business KPI was measured against the current workflow.
- Security/compliance sign-off, runbooks, on-call, and the RACI are in place.

### Risks → QA measures

| Risk | QA measure | Task |
|------|------------|------|
| Integration failures | API contract, full-path integration tests in staging | 05.2 |
| Poor user acceptance (over- or under-trust) | UX for GenAI states, UAT, user guide, change management | 05.2, 05.10 |
| Service outage (provider down, throttled, quota exhausted) | Capacity sizing, retries/circuit breakers, fallback model, failover test | 05.1, 05.4 |
| Gradual rollout goes wrong | Staged release plan with pre-set criteria, rollout log, rollback | 05.0, 05.9 |
| Deployed configuration ≠ evaluated configuration | Config as code, pinned versions, regression gate | 05.1, 05.7 |
| Provider silently updates the model behind an alias | Pinned version, deprecation watch | 05.1, 05.11 |
| ACL bypass: the system acts with more rights than the user | Identity passed end to end, query-time ACL, tool permissions | 05.2 |
| Harmful, leaking, or malformed output reaches users | Input/output guardrails, schema validation, kill switch | 05.3 |
| Prompt injection in production triggers actions `[A]` | Injection detection, approval UI, agent limits, audit log | 05.2, 05.3 |
| Cost runaway | Rate limits, cost caps with alerts, per-task budget | 05.3, 05.5 |
| PII in logs or sent to unapproved parties | Redacted logging, data-flow review, provider agreements | 05.5, 05.6 |
| No visibility into what happened | Full tracing, dashboards, alerts, replay | 05.5 |
| Unsafe changes to prompts/models after launch | Pipeline-only changes, RACI, regression gate | 05.7, 05.11 |
| Eval set doesn't match real traffic | Shadow mode, real inputs fed back to the eval set | 05.8 |
| Slow or chaotic incident response | Runbooks, on-call, kill switch, incident process | 05.11 |
| The AI changes production on its own | Production steps named in the plan and approved; rollouts and rollbacks triggered by the named owner | all |

### Exit gate (walked in 05.12)

- [ ] The deployed configuration matches the evaluated one, or its changes passed the regression gate.
- [ ] Integration and identity propagation are tested in staging.
- [ ] Guardrails, rate limits, cost caps and the kill switch are live and tested.
- [ ] The failover and degradation tests pass.
- [ ] Tracing, dashboards, alerts and feedback capture are live, and replay works.
- [ ] Security & compliance are signed off.
- [ ] The release pipeline has the regression gate, and rollback has been tested.
- [ ] Shadow mode is done, and its findings are handled.
- [ ] The rollout stages passed their criteria, and the KPI result is recorded.
- [ ] UAT is done and the user guide is published.
- [ ] Runbooks, the registry entry, on-call and the RACI are in place.
- [ ] The launch decision and the Phase 06 handoff are recorded in the 05.12 entry.

---

## Templates

### Release plan

| Stage | Audience / traffic % | Min duration / volume | Go criteria | Rollback criteria | Decision owner |
|-------|----------------------|-----------------------|-------------|-------------------|----------------|
| Shadow | real traffic, hidden | | | | |
| Internal | | | | | |
| Canary | x% | | | | |
| Wider | | | | | |
| Full | 100% | | | | |

### Guardrail & control inventory

| Control | Type (input / output / rate / cost / limit / kill switch) | Action on trigger | User message | False-positive rate | Owner |
|---------|-----------------------------------------------------------|-------------------|--------------|---------------------|-------|
| | | | | | |

### Trace fields

```text
trace_id / timestamp / user (pseudonymized) / tenant
config: model_id, prompt_version, index_version [R], tools_version [A], guardrails_version
input (redacted) / output (redacted)
retrieved chunk ids + scores                              [R]
tool calls: name, args, result, approval                   [A]
guardrail hits / fallback used / degraded mode
tokens in/out, latency (ttft, total), cost
user feedback (linked later)
```

### Runbook

```text
Incident:           (e.g. provider outage, harmful output reported, cost spike)
Detection:          (alert / dashboard / user report)
Severity levels:
Immediate action:   (kill switch? fallback? rollback? rate limit?)
Investigation:      (which traces/dashboards to check)
Communication:      (who to inform, template)
Recovery & verify:
Post-incident:      (add case to regression suite, update runbook)
```
