# Phase 04: Evaluation

> Decide with evidence whether the frozen configuration from Phase 03 meets the Phase 01 success criteria, beats the heuristic benchmark, and is safe, before real users see it. This phase ends with the **deployment decision**.

**CRISP-ML(Q) origin:** *ML Model Evaluation (offline testing)*. Open-ended outputs have no single test-set accuracy, so the method changes:
- **Performance on the test set** becomes rubrics plus an **LLM judge calibrated against human labels**, with results per case type.
- **Robustness to noisy inputs** becomes **red-teaming**: prompt injection, jailbreaks, data exfiltration, excessive agency.
- **Explainability** becomes **traceability**: which sources were retrieved, which tools were called, and why.
- **The deployment decision** rests on the documented thresholds, including cost and latency.

**Scope boundaries**
- **This phase owns:** offline evaluation on the **held-out** set, judge calibration, full red-teaming, load/cost tests, offline user review, the regression suite, and the deployment decision.
- **[Phase 03](03-model-selection-customization.md) owns:** iteration on the **dev** set. When failures are found here, the fixes are made in Phase 03 or Phase 02.
- **[Phase 05](05-deployment.md) owns:** online tests (shadow, canary, A/B) and user acceptance with real traffic.

**Inputs from Phase 03:** frozen configuration, system card, dev eval harness, draft LLM-judge rubrics, robustness smoke-test report, known risks to red-team. From Phase 02: the **held-out** eval set, sensitivity plan, retrieval test report `[R]`. From Phase 01: metrics sheet and thresholds, heuristic benchmark, baseline, risk profile, security scoping matrix, spec (proof section).

## How this file is used

Every task below is **executable with `/genai`**. The roles work as in [Phase 02](02-context-engineering.md): HUMAN (*AI prepares / You do / AI turns into / Review rules / Done when*), AI (*Plan / Build / Review rules / Done when*), DECISION (*Brief / Options / Decision record*).

Artifacts go to `.genai/artifacts/04-evaluation/`; harness code, attack sets and the regression suite live in the project repo. **This is the only phase that may open the held-out set**, and every use of it is counted in the artifacts.

## Optional tags

| Tag | Applies when | Set by | Tasks |
|-----|--------------|--------|-------|
| `[R]` | The slice uses retrieval | 02.0 | 04.4 |
| `[A]` | The model calls tools or acts across several steps | 03.0 | 04.7 |

Items tagged `[R]`, `[A]` or `[FT]` inside other tasks apply only in those cases.

## Task graph

| Task | Title | Role | Depends on | S | M-L |
|------|-------|------|------------|---|-----|
| 04.0 | Handoff review & evaluation plan | HUMAN | 03.13 | 1h | 3h |
| 04.1 | Held-out set readiness | AI | 04.0 | 1h | 3h |
| 04.2 | LLM-judge calibration | HUMAN | 04.1 | 4h | 10h |
| 04.3 | Held-out quality run | AI | 04.2 | 2h | 6h |
| 04.4 | Groundedness & citations `[R]` | AI | 04.2 | 2h | 5h |
| 04.5 | Safety & red-teaming | AI | 04.1 | 4h | 12h |
| 04.6 | Robustness & degradation | AI | 04.1 | 2h | 5h |
| 04.7 | Trajectory evaluation `[A]` | AI | 04.2 | 3h | 8h |
| 04.8 | Load, latency & cost | AI | 04.0 | 2h | 5h |
| 04.9 | Offline user review | HUMAN | 04.3 | 3h | 8h |
| 04.10 | Error analysis & fix loop | AI | 04.3, 04.4, 04.5, 04.6, 04.7, 04.8, 04.9 | 2h | 6h |
| 04.11 | Regression suite | AI | 04.10 | 2h | 4h |
| 04.12 | Evaluation report & deployment decision | DECISION | 04.11 | 2h | 4h |
| | **Core** (no optional tags) | | | **~25h (~3 days)** | **~66h (~1.5 weeks)** |
| | + `[R]` | | | +2h | +5h |
| | + `[A]` | | | +3h | +8h |
| | **Everything** | | | **~30h (~4 days)** | **~79h (~2 weeks)** |

- Hours are **your hands-on effort**. 04.2 and 04.5 vary the most. Calendar time also depends on when SMEs are available for labeling and review.
- 04.10 counts **one** fix loop. Each extra round trip to Phase 02/03 adds that phase's rework time plus a re-run here.
- **S**: single task, low-risk data, internal users. **M-L**: several tasks, regulated or customer-facing, agentic, stricter sign-off.

---

## Tasks

### 04.0 Handoff review & evaluation plan

```yaml task
id: "04.0"
title: Handoff review & evaluation plan
role: HUMAN
depends_on: ["03.13"]
estimate: {S: 1, M-L: 3}
artifact: evaluation-plan.md
optional_tag: null
sets_tags: []
```

**AI prepares** (`04.0-prep.md`)
- A **re-read summary** of the Phase 03 handoff note, the system card and the known risks
- A **freeze check**: is the configuration to be evaluated the frozen one (pinned model IDs, prompt versions, index/tool versions)? Any drift is listed
- A **draft evaluation plan** (template below): every **claim to prove**, taken from the spec's *proof* section and the Phase 01 thresholds (quality, safety, latency, cost), each with a proposed metric, threshold, method and sample size
- A **proposed blocker/known-limitation split** per claim, marked as a proposal
- The questions only you can answer: who signs off, what security/compliance require, how much SME time is available

**You do**
- [ ] Confirm or correct each claim, metric, threshold, method and sample size — **before anything is run**
- [ ] Decide what counts as a **blocker** (it stops deployment) and what is an acceptable **known limitation**
- [ ] Confirm the sign-off path with the decision-maker and security/compliance
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `evaluation-plan.md`: the plan table, the blocker/limitation rules, the sign-off path, and the configuration under evaluation with its pinned versions.

**Review rules**
- Every claim traces to the spec's proof section or to the Phase 01 metrics sheet.
- Each claim has a metric, a **threshold**, a method and a **sample size**, fixed before any run. This is what stops the goalposts moving.
- The configuration under evaluation is the **frozen** one. Any drift from 03.12 is a blocker.
- The blocker/limitation split is yours, not the AI's proposal.
- The plan says who signs off on the result.

**Done when** you approve the plan, and the thresholds are agreed with the decision-maker.

---

### 04.1 Held-out set readiness

```yaml task
id: "04.1"
title: Held-out set readiness
role: AI
depends_on: ["04.0"]
estimate: {S: 1, M-L: 3}
artifact: heldout-readiness.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): test set.*

**Plan** (`04.1-plan.md`): how contamination will be checked (exact and near-duplicate matching against prompts, few-shot examples, fine-tuning data `[FT]`, and the dev set), and how representativeness will be measured.

**Build**
- [ ] Check for **contamination**: no held-out item appears in prompts, few-shot examples, fine-tuning data `[FT]`, or the dev set
- [ ] Check that it is **representative**: the mix of case types and topics matches real traffic (from the Phase 01 workflow artifacts)
- [ ] Check there are **enough items per case type** for a meaningful result. Add fresh, real items where it is thin — from the 02.9 sources, never invented
- [ ] If the held-out set has been used before, record **how many times**. After repeated use, refresh it with new items so it isn't tuned to by accident
- [ ] **Freeze** the version used for this evaluation, and record its hash/version

**AI writes** `heldout-readiness.md`: the contamination check method and result, the case-type and topic distribution against expected traffic, the item counts per case type with the power implication, the **use counter**, and the frozen version id.

**Review rules**
- The contamination check is a **run**, with its method and result stated — not an assurance.
- The distribution comparison against real traffic is shown, and any skew is called out.
- Item counts per case type are stated, and thin types are flagged as a confidence limit.
- Items added here come from real sources, and are marked as new.
- The use counter is updated, and the frozen version id is recorded.

**Done when** you approve the readiness note, and the held-out version is frozen.

---

### 04.2 LLM-judge calibration

```yaml task
id: "04.2"
title: LLM-judge calibration
role: HUMAN
depends_on: ["04.1"]
estimate: {S: 4, M-L: 10}
artifact: judge-calibration.md
optional_tag: null
sets_tags: []
```

**AI prepares** (`04.2-prep.md`)
- A **calibration sample** (e.g. 50–100 outputs) produced with the frozen configuration, ready for labeling
- The **labeling interface**: the Phase 03 rubrics per criterion, with instructions, and a subset assigned to **two labelers** for human–human agreement
- A **judge setup proposal**: a judge model from a **different family** than the one being evaluated, pinned, with its prompt
- The **acceptance thresholds** for agreement per criterion, marked as proposals
- A **bias-test design**: position, verbosity and self-preference

**You do**
- [ ] Have SMEs label the calibration sample with the rubrics
- [ ] Label the shared subset with two people, for **human–human agreement**
- [ ] Agree the acceptance threshold per criterion
- [ ] Put the labels and your notes in `.genai/inbox/`

**AI turns into** `judge-calibration.md`: human–human agreement per criterion, **judge–human agreement** (% agreement, Cohen's kappa), the bias test results, the rubric/judge-prompt iterations made, which criteria are judge-scored and which stay **human-scored**, and the pinned judge model ID and prompt version.

**Review rules**
- **Human–human agreement is measured first.** If people can't agree, the rubric is fixed before the judge is blamed.
- Judge–human agreement is reported per criterion, with the kappa, not only overall.
- Position, verbosity and self-preference bias were tested, and the judge comes from a different model family than the one under evaluation — or the reason it doesn't is stated.
- Criteria that miss the acceptance threshold are marked **human-scored** for the rest of the phase.
- The judge model ID and prompt version are **pinned**. The judge is part of the measuring instrument.

**Done when** you approve the calibration record, and every criterion is marked judge-scored or human-scored.

---

### 04.3 Held-out quality run

```yaml task
id: "04.3"
title: Held-out quality run
role: AI
depends_on: ["04.2"]
estimate: {S: 2, M-L: 6}
artifact: heldout-results.md
optional_tag: null
sets_tags: []
```

**Plan** (`04.3-plan.md`): the run matrix (N samples per item), how confidence intervals will be computed, the human-scoring workload it will generate, and the spend.

**Build**
- [ ] Run the frozen configuration on the held-out set, with **N samples per item**
- [ ] Score with the automatic checks, the calibrated judge, and human scoring where 04.2 requires it
- [ ] Report **per case type** (normal / edge / failure / forbidden / unanswerable / access-restricted), with **confidence intervals**, not a single average
- [ ] Compare against:
  - [ ] The Phase 01 **thresholds**
  - [ ] The **heuristic benchmark** (it must be beaten)
  - [ ] The **current-workflow baseline**
  - [ ] The Phase 03 dev results — a large drop from dev means overfitting
- [ ] Measure the **variance** across samples, and flag unstable items
- [ ] Increment the held-out **use counter**

**AI writes** `heldout-results.md`: the results per case type with confidence intervals and run ids, the four comparisons, the variance analysis with the unstable items listed, and the pass/fail against each claim in the evaluation plan.

**Review rules**
- Results are per case type **with confidence intervals**, and the sample size per type is stated.
- The dev-to-held-out drop is reported explicitly, and a large one is called overfitting rather than noise.
- The heuristic benchmark and the workflow baseline were both run or cited with their measurement date.
- Human-scored criteria were scored by humans, not silently by the judge.
- The use counter is incremented in `heldout-readiness.md`.
- Failing claims are reported plainly against the plan's thresholds. No threshold is renegotiated here.

**Done when** you approve the results.

---

### 04.4 Groundedness & citations `[R]`

```yaml task
id: "04.4"
title: Groundedness & citations
role: AI
depends_on: ["04.2"]
estimate: {S: 2, M-L: 5}
artifact: groundedness-results.md
optional_tag: R
sets_tags: []
```

**Plan** (`04.4-plan.md`): how claims will be split and checked (automatic, judge, or human), the sample, and the definition of an unsupported claim.

**Build**
- [ ] Split the answers into claims, and check that each claim is **supported by the retrieved context**
- [ ] Measure **citation accuracy**: each cited source actually supports the claim it is attached to
- [ ] Measure the **hallucination rate**: unsupported claims per answer
- [ ] Check **unanswerable** items: the system declines or says "I don't know" instead of making up an answer
- [ ] Check **access-restricted** items end to end: no content from unauthorized sources appears in answers `[if ACLs apply]`

**AI writes** `groundedness-results.md`: the groundedness and citation-accuracy rates with confidence intervals, the hallucination rate per case type, the unanswerable behavior, the ACL results, and examples of each failure mode.

**Review rules**
- Every rate names its scoring method and its sample size, and judge-scored rates use the **calibrated** judge.
- Unsupported claims are listed as examples, not only counted.
- Unanswerable items are reported separately: answering them at all is a failure.
- **Any** leak on an access-restricted item is a blocker, whatever the rate `[if ACLs apply]`.

**Done when** you approve the results.

---

### 04.5 Safety & red-teaming

```yaml task
id: "04.5"
title: Safety & red-teaming
role: AI
depends_on: ["04.1"]
estimate: {S: 4, M-L: 12}
artifact: red-team-log.md
optional_tag: null
sets_tags: []
```

**Plan** (`04.5-plan.md`): the threat list, the attack budget per category, the environment the attacks run in (**never production**), and what it needs from you (a test tenant, seeded fake PII, permission to attempt exfiltration against test data).

**Build**
- [ ] Build the **threat list** from the Phase 01 risk profile and the security scoping matrix. Use the OWASP Top 10 for LLM Applications as a checklist
- [ ] Attack the system:
  - [ ] **Direct prompt injection** and jailbreaks from the user input
  - [ ] **Indirect injection** through retrieved documents `[R]`, tool outputs `[A]`, and uploads
  - [ ] **Data exfiltration**: PII, secrets, the system prompt, other users' data
  - [ ] **Harmful / toxic / off-policy** outputs, as the org's AI policy defines them
  - [ ] **Misuse**: off-topic use, abuse of the system's capabilities
  - [ ] **Excessive agency**: getting the system to make unapproved or out-of-bounds tool calls `[A]`
  - [ ] **Denial of wallet**: inputs that inflate tokens, loops, or cost
- [ ] Check **bias/fairness**: compare quality across relevant user groups, languages, and phrasings
- [ ] Record every successful attack with its severity, and propose **blocker or known limitation** per the 04.0 rules
- [ ] Add every attack case to the regression suite (04.11)

**AI writes** `red-team-log.md` (template below): every attempt with its vector, result, severity and mitigation; the coverage against the threat list and OWASP; and the bias/fairness comparison.

**Review rules**
- The log covers **every** threat-list category, including the ones where nothing was found.
- Successful attacks are reproducible: the log records the exact input and conditions.
- Severity uses the 04.0 blocker rules, and the blocker/limitation call is put to you rather than assumed.
- All attacks ran against a **test environment with test data**. Say which one.
- Every attack case is in the regression suite, or marked for 04.11 to add.

**Done when** you approve the log, and every successful attack is marked blocker or known limitation.

---

### 04.6 Robustness & degradation

```yaml task
id: "04.6"
title: Robustness & degradation
role: AI
depends_on: ["04.1"]
estimate: {S: 2, M-L: 5}
artifact: robustness-results.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): robustness.*

**Plan** (`04.6-plan.md`): the perturbation set, how dependencies will be degraded (fault injection in a test environment), and the acceptance bar for each degraded mode.

**Build**
- [ ] Test **input perturbations**: paraphrases, typos, other languages, unusual formatting, very long inputs
- [ ] Test **degraded dependencies**:
  - [ ] Retrieval returns nothing or is slow `[R]`
  - [ ] Tools time out or error `[A]`
  - [ ] The primary model is unavailable
- [ ] Run the **fallback model** on the held-out set, and record its quality, so the degraded mode is known and acceptable
- [ ] Check **overflow** behavior at the token-budget edges

**AI writes** `robustness-results.md`: the quality delta per perturbation, the behavior under each degraded dependency against the 03.8 design, the fallback model's held-out quality, and the overflow results.

**Review rules**
- Perturbation results are reported as a **delta against the 04.3 baseline**, on the same items.
- Every degraded mode was actually induced (fault injection), not reasoned about.
- The fallback model's held-out quality is measured, and the artifact says whether that degraded mode is acceptable against the thresholds.
- The held-out use counter includes these runs.

**Done when** you approve the results.

---

### 04.7 Trajectory evaluation `[A]`

```yaml task
id: "04.7"
title: Trajectory evaluation
role: AI
depends_on: ["04.2"]
estimate: {S: 3, M-L: 8}
artifact: trajectory-results.md
optional_tag: A
sets_tags: []
```

**Plan** (`04.7-plan.md`): the trace sample, the trajectory metrics, and how approval gates and limits will be provoked.

**Build**
- [ ] Evaluate **traces**, not just final answers:
  - [ ] Task success rate
  - [ ] Tool-call correctness (right tool, right arguments)
  - [ ] Unnecessary or repeated calls
  - [ ] Number of steps and cost per task
- [ ] Check that **approval gates fire** for every Locked action, and for every action triggered by untrusted content
- [ ] Check that **limits hold**: max steps, timeouts, budget per task
- [ ] Check **recovery**: correct behavior after a tool error, and a clean hand-off to a human when stuck

**AI writes** `trajectory-results.md`: the metrics with run ids, an approval-gate table (Locked action → attempt → gate fired yes/no), the limit tests with the values reached, and the recovery results.

**Review rules**
- Every Locked action from the authority map was **attempted**, and the gate fired. A gate that did not fire is a blocker.
- Limits were tested by exceeding them, not by reading the config.
- Unnecessary-call and step-count numbers are measured and compared with the 03.8 budget.
- Recovery was tested with **induced** tool errors.

**Done when** you approve the results.

---

### 04.8 Load, latency & cost

```yaml task
id: "04.8"
title: Load, latency & cost
role: AI
depends_on: ["04.0"]
estimate: {S: 2, M-L: 5}
artifact: load-cost-results.md
optional_tag: null
sets_tags: []
```

**Plan** (`04.8-plan.md`): the load profile (expected and peak, from the Phase 01 estimate), the test environment, the expected spend of the test, and the approval that needs.

**Build**
- [ ] Load-test at the **expected concurrency and at peak**
- [ ] Measure latency p50 / p95 / p99, plus time-to-first-token if the UX streams
- [ ] Check **rate limits and quotas**: throttling behavior, retry/backoff, whether fallback triggers
- [ ] Measure **cost per task at volume**, and project it to monthly cost. Compare against the Phase 01 cost model

**AI writes** `load-cost-results.md`: the latency percentiles at each load level, the throttling behavior observed, the measured cost per task with the volume it was measured at, the monthly projection, and the comparison with the Phase 01 cost model.

**Review rules**
- Load figures come from a **real test run**, and the artifact names the environment and its differences from production.
- p95 at **peak** is compared with the Phase 01 latency constraint, not only p50 at expected load.
- Throttling was actually hit, or the artifact says why it could not be.
- The monthly projection states its volume assumption, and any overrun against the cost model is called out.

**Done when** you approve the results.

---

### 04.9 Offline user review

```yaml task
id: "04.9"
title: Offline user review
role: HUMAN
depends_on: ["04.3"]
estimate: {S: 3, M-L: 8}
artifact: user-review.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): explainable & trustworthy.*

**AI prepares** (`04.9-prep.md`)
- An **output sample** for review, stratified by case type, with the trace (sources `[R]`, tool calls `[A]`, reasoning) shown next to each answer
- A **blind side-by-side pack** against the current workflow's output, where that output exists
- A **review guide**: would you act on this output, what would you check first, what would make you distrust it
- A **traceability checklist**: can a reviewer see why the answer was given
- A **scheduling and consent note** for the sessions

**You do**
- [ ] Run the review with end users / SMEs, blind where possible
- [ ] Rate **usefulness** and **trust**
- [ ] Collect the failure modes users care about that the metrics missed
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `user-review.md`: the usefulness and trust ratings, the blind side-by-side result, the traceability findings, and the **new failure modes to feed back into the eval set**.

**Review rules**
- The side-by-side was **blind**, or the artifact says why it could not be.
- Ratings are reported with the reviewer count and their roles. Practitioners, not only managers.
- Every new failure mode users raised is written down, even when the metrics look good.
- New eval items produced here are added to the **dev** set, never to the held-out set mid-evaluation.
- Quotes are summarized, not pasted from raw notes.

**Done when** you approve the findings, and the new failure modes are recorded.

---

### 04.10 Error analysis & fix loop

```yaml task
id: "04.10"
title: Error analysis & fix loop
role: AI
depends_on: ["04.3", "04.4", "04.5", "04.6", "04.7", "04.8", "04.9"]
estimate: {S: 2, M-L: 6}
artifact: error-analysis.md
optional_tag: null
sets_tags: []
```

**Plan** (`04.10-plan.md`): how failures from 04.3–04.9 will be grouped, and the rule for confirming a fix (dev first, held-out only for the final confirmation).

**Build**
- [ ] Group all the failures from 04.3–04.9 into categories, and trace each one to its **owning phase**:
  - [ ] Data or retrieval → Phase 02
  - [ ] Prompt, model, tools, or fine-tuning → Phase 03
  - [ ] The spec or the outcome itself was wrong → Phase 01
- [ ] For each category, put the choice to you: **fix** (return to that phase) or **accept** as a known limitation, with a mitigation (e.g. human review)
- [ ] After fixes, confirm on the **dev** set first. Re-run the held-out set only for the final confirmation, and **count the uses**
- [ ] Update the system card's known limitations

**AI writes** `error-analysis.md`: the category table (category → count → owning phase → evidence → fix/accept → mitigation → owner), the re-run results after any fix, and the updated known-limitations list.

**Review rules**
- Every category names an **owning phase** and the evidence behind that attribution.
- **Fix or accept is your call**, recorded per category. No category is left undecided.
- A fix that is material reopens the owning task with `--cascade` rather than being patched inside this phase.
- Fixes were confirmed on the dev set first, and each held-out re-run is counted.
- The system card's known limitations match this table exactly.

**Done when** you approve the analysis, and every category is marked fix or accept.

---

### 04.11 Regression suite

```yaml task
id: "04.11"
title: Regression suite
role: AI
depends_on: ["04.10"]
estimate: {S: 2, M-L: 4}
artifact: regression-suite.md
optional_tag: null
sets_tags: []
```

**Plan** (`04.11-plan.md`): what goes into the suite, how it is split into fast and full runs, where it lives in the repo, and how CI will call it.

**Build**
- [ ] Package everything into an **automated suite**: the eval items, red-team attacks, robustness cases, trajectory checks `[A]`, and the calibrated judge
- [ ] Turn the thresholds into **pass/fail gates**
- [ ] Make it run in CI on every change to prompts, models, index/pipeline, or tools
- [ ] Make it runnable against **production traces** later (Phase 06)
- [ ] Version the suite together with the eval set

**AI writes** `regression-suite.md`: what the suite covers, the gates and their thresholds, the repo path and CI job, the runtime and cost per run, and the replay interface Phase 06 will use.

**Review rules**
- Every 04.5 attack and every accepted limitation from 04.10 has a case in the suite.
- The gates use the **04.0 thresholds**, and a deliberately broken configuration fails them. Show that run.
- The suite runs in CI on prompt, model, index and tool changes, and the artifact names the job.
- The suite can replay **production traces**, ready for Phase 06.
- Its runtime and cost per run are measured, so it can be run often.

**Done when** you approve the suite, and it passes in CI against the frozen configuration.

---

### 04.12 Evaluation report & deployment decision

```yaml task
id: "04.12"
title: Evaluation report & deployment decision
role: DECISION
depends_on: ["04.11"]
estimate: {S: 2, M-L: 4}
artifact: null
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): make the deployment decision.*

**Brief** (`04.12-brief.md`) — the **evaluation report** (template below), claim by claim: the result vs the threshold, with evidence, confidence and known limitations. It also contains:
- The **exit gate walk-through** below, item by item
- The open blockers, and the accepted limitations with their mitigations
- The conditions a *go* should carry (e.g. human review of every output, a limited user group)
- What Phase 05 must watch online, derived from the weakest results here

**Options**
- **Go**: deploy per Phase 05.
- **Go with conditions**: name each condition and its owner.
- **Back to phase X**: reset the owning task with `--cascade`.
- **Stop**: the thresholds cannot be met, or a blocker cannot be mitigated.

End the brief with **AI recommendation:** `<option>`, followed by its reasoning.

**Decision record**: a `## 04.12` entry in `decisions.md` with the decision, the conditions, the accepted limitations, the sign-off from the decision-maker and, where required, from security/compliance, and the online metrics handed to Phase 05.

---

## Quality assurance

### Requirements & constraints

- The evaluation ran on the **frozen** configuration and the **held-out** set, with the plan fixed beforehand.
- The judge is calibrated against humans, and uncalibrated criteria are human-scored.
- Results are reported per case type, with confidence intervals, and beat the heuristic benchmark and the workflow baseline.
- Every red-team finding is triaged as a blocker or a known limitation with a mitigation.
- Latency and cost at peak fit the Phase 01 constraints.
- The regression suite encodes the thresholds and runs in CI.

### Risks → QA measures

| Risk | QA measure | Task |
|------|------------|------|
| Moving the goalposts after seeing results | Claims, metrics, thresholds and sample sizes fixed in the plan first | 04.0 |
| Test-set contamination or overuse | Contamination check, use counter, refresh policy | 04.1, 04.3, 04.10 |
| Trusting an uncalibrated LLM judge | Human–human then judge–human agreement, bias tests, pinned judge | 04.2 |
| A single average hiding failures | Results per case type with confidence intervals | 04.3, 04.4 |
| Hallucination and wrong citations | Claim-level groundedness and citation accuracy | 04.4 |
| Prompt injection, exfiltration, jailbreaks | Threat list from the risk profile + OWASP, full red-team log | 04.5 |
| `[A]` Excessive agency in production | Approval gates provoked, limits exceeded on purpose, recovery tested | 04.7 |
| Degraded modes never tested until an incident | Fault injection, fallback measured on held-out | 04.6 |
| Cost or latency blow-up at real load | Load test at peak, cost per task at volume vs the cost model | 04.8 |
| Metrics pass but users don't trust the output | Blind side-by-side user review, traceability check | 04.9 |
| Fixes that break something else | Dev-first confirmation, full regression suite as a gate | 04.10, 04.11 |
| A deployment decision without evidence or sign-off | Report claim by claim + recorded sign-off | 04.12 |

### Exit gate (walked in 04.12)

- [ ] The evaluation plan was fixed before the runs, and every claim has a result.
- [ ] The held-out set was contamination-checked and frozen, and its uses are counted.
- [ ] The judge is calibrated, or the criterion is human-scored.
- [ ] Quality meets the thresholds per case type, and beats the heuristic benchmark and the baseline.
- [ ] `[R]` Groundedness, citation accuracy and the unanswerable path meet their thresholds, with no ACL leakage.
- [ ] No open red-team **blocker**; every other finding has a mitigation.
- [ ] `[A]` Approval gates fire, and limits hold.
- [ ] Latency and cost at peak fit the constraints.
- [ ] Users reviewed real outputs, and their failure modes are recorded.
- [ ] The regression suite passes in CI and encodes the thresholds.
- [ ] The evaluation report is written and the deployment decision is signed off.

---

## Templates

### Evaluation plan

| Claim (from spec / metrics) | Metric | Threshold | Method (auto / judge / human) | Sample size | Blocker if failed? |
|-----------------------------|--------|-----------|-------------------------------|-------------|--------------------|
| | | | | | yes / no |

### Judge calibration record

```text
Judge model (pinned) / prompt version:
Rubric criterion:
Calibration sample:   n = __, labeled by __
Human–human agreement:
Judge–human agreement: (% / kappa)
Biases checked:       position / verbosity / self-preference
Acceptance threshold: __   → judge-scored | human-scored
```

### Red-team log

| ID | Threat category | Attack (input / vector) | Result | Severity | Blocker / known limitation | Mitigation | In regression suite? |
|----|-----------------|-------------------------|--------|----------|----------------------------|------------|----------------------|
| | | | | | | | |

### Evaluation report

```text
Configuration:        (frozen config id, system card version)
Held-out set:         version, n items, uses so far
Results per claim:    claim → result vs threshold (CI), pass/fail
Benchmark / baseline: heuristic __ vs system __; current workflow __ vs system __
Red-team:             blockers open: __; known limitations: __
Load & cost:          p95 __ at peak; cost/task __; monthly projection __
User review:          summary
Known limitations:    (and mitigations)
Decision:             go | go with conditions (__) | back to phase __ | stop
Signed off by / date:
```
