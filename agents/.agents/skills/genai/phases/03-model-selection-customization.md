# Phase 03: Model Selection & Customization

> Choose the model(s), and customize them only as far as the Phase 01 metrics require. Always climb the cheapest rung of the customization ladder first.

**CRISP-ML(Q) origin:** *ML Model Engineering*. The model is usually a **purchased dependency**, not something you train, so the work shifts:
- Algorithm selection becomes **model selection**: quality, cost, latency, policy, and vendor risk.
- Training becomes the **customization ladder**:
  1. Prompting
  2. Context/retrieval tuning
  3. Tools/agents
  4. Fine-tuning
- Reproducibility means pinned model IDs, versioned prompts and sampling settings, and several samples per case. Random seeds are unreliable.
- Model cards become a **system card** for the application.

**Scope boundaries**
- **This phase owns:** model choice, prompt wording, few-shot examples, tool definitions, orchestration, fine-tuning, and a dev eval harness for iterating.
- **[Phase 02](02-context-engineering.md) owns (inputs here):** the knowledge pipeline, the context design and the token budget.
- **[Phase 04](04-evaluation.md) owns:** the formal evaluation on the **held-out** set, LLM-judge calibration, and full red-teaming.

**Inputs from Phase 02:** context design and token budget, dev eval set, retrieval config and test report `[R]`, known failure modes, updated sensitivity plan. From Phase 01: metrics sheet and thresholds, heuristic benchmark, slice spec (invariants, examples, Locked/Bounded/Delegated), rough cost model.

## How this file is used

Every task below is **executable with `/genai`**. The fenced `yaml task` block is read by the checker, and the prose sections are the playbook. The roles work exactly as in [Phase 02](02-context-engineering.md): HUMAN (*AI prepares / You do / AI turns into / Review rules / Done when*), AI (*Plan / Build / Review rules / Done when*), DECISION (*Brief / Options / Decision record*).

Artifacts, prep kits, plans and briefs go to `.genai/artifacts/03-model-selection-customization/`. **Prompts, harness and code live in the project repo, versioned in git.** The artifact records paths, run ids and measured results.

## Optional tags

| Tag | Applies when | Set by | Tasks |
|-----|--------------|--------|-------|
| `[R]` | The slice uses retrieval | 02.0 | 03.6 |
| `[A]` | The model calls tools or acts across several steps | 03.0 | 03.7, 03.8 |
| `[SH]` | The model is self-hosted rather than a managed API | 03.4b | (items inside Phase 05 tasks) |
| `[FT]` | The escalation gate decides fine-tuning is justified | 03.9 | 03.10 |

Tasks whose tag is off show as `n/a`, and the checker refuses to start them. Items tagged inside an applicable task work the same way: skip them, and say so.

## Task graph

| Task | Title | Role | Depends on | S | M-L |
|------|-------|------|------------|---|-----|
| 03.0 | Handoff review & agentic scope | DECISION | 02.11 | 1h | 2h |
| 03.1 | Model requirements | HUMAN | 03.0 | 2h | 4h |
| 03.2 | Candidate shortlist | AI | 03.1 | 2h | 4h |
| 03.3 | Dev eval harness | AI | 03.0 | 4h | 10h |
| 03.4 | Baseline bake-off | AI | 03.2, 03.3 | 2.5h | 7h |
| 03.4b | Choose primary & fallback | DECISION | 03.4 | 0.5h | 1h |
| 03.5 | Prompt engineering | AI | 03.4b | 4h | 10h |
| 03.6 | Context/retrieval tuning `[R]` | AI | 03.5 | 2h | 6h |
| 03.7 | Tool design `[A]` | AI | 03.5 | 3h | 8h |
| 03.8 | Orchestration & authority `[A]` | AI | 03.7 | 3h | 8h |
| 03.9 | Escalation gate: fine-tune or not | DECISION | 03.6, 03.8 | 1h | 2h |
| 03.10 | Fine-tuning `[FT]` | AI | 03.9 | 8h | 24h |
| 03.11 | Robustness smoke tests | AI | 03.10 | 2h | 4h |
| 03.12 | Configuration freeze & system card | AI | 03.11 | 2h | 4h |
| 03.13 | Phase gate → Phase 04 | DECISION | 03.12 | 1h | 2h |
| | **Core** (no optional tags) | | | **~22h (~3 days)** | **~50h (~1.5 weeks)** |
| | + `[R]` | | | +2h | +6h |
| | + `[A]` | | | +6h | +16h |
| | + `[FT]` | | | +8h | +24h |
| | **Everything** | | | **~38h (~5 days)** | **~96h (~2.5 weeks)** |

- Hours are **your hands-on effort**. 03.5 varies the most. Time-box it, and let the error analysis decide when to stop.
- The `[FT]` hours are hands-on time. Training runs, compute cost, and waiting for labeling come on top.
- **S**: small project (one task, single-turn, 3–4 candidate models). **M-L**: several tasks, multi-turn or agentic, stricter compliance, several model tiers.

---

## Tasks

### 03.0 Handoff review & agentic scope

```yaml task
id: "03.0"
title: Handoff review & agentic scope
role: DECISION
depends_on: ["02.11"]
estimate: {S: 1, M-L: 2}
artifact: null
optional_tag: null
sets_tags: ["A"]
```

**Brief** (`03.0-brief.md`), built from the Phase 02 handoff and the Phase 01 spec:
- The **targets for this phase**: the quality, latency and cost-per-task thresholds from the metrics sheet, quoted exactly
- The context design, token budget and **known failure modes** inherited from Phase 02
- Confirmation that the **held-out set stays locked**, and that only the dev set is used here
- The **agentic question**: does the slice need the model to call tools or act across several steps, or can the code decide every step? Argue the read-only and single-call case honestly
- What experiment tracking will be used (where every run is logged)

**Options**
- **Tools/agents needed** (`--tag A=yes`): 03.7 and 03.8 apply.
- **No tools** (`--tag A=no`): a single call or a fixed chain written in code. Those tasks become `n/a`.
- **Back to 02.11**: the handoff is incomplete (e.g. no dev set, no budget).

End the brief with **AI recommendation:** `<option>`, followed by its reasoning. Prefer the simplest option that the spec allows.

**Decision record**: a `## 03.0` entry in `decisions.md` with the agreed targets, the agentic verdict and its reasoning. Then `set 03.0 done --tag A=yes|no`.

---

### 03.1 Model requirements

```yaml task
id: "03.1"
title: Model requirements
role: HUMAN
depends_on: ["03.0"]
estimate: {S: 2, M-L: 4}
artifact: model-requirements.md
optional_tag: null
sets_tags: []
```

**AI prepares** (`03.1-prep.md`)
- **Draft hard filters** (pass/fail), each traced to a Phase 01 constraint or a Phase 02 plan:
  - Modality (text, image, audio, documents)
  - **Context window** ≥ the Phase 02 token budget total
  - Languages and domain
  - Structured output / tool calling support `[A]`
  - Hosting paradigm (managed API vs self-hosted) and region / **data residency**
  - Provider **data-usage policy** (training on your data, retention) vs the sensitivity plan
  - Licensing (for open-weight models) and compliance requirements
- **Proposed scored criteria with weights**: quality on the dev set, latency (p50/p95), cost per task, throughput/rate limits, vendor maturity, deprecation risk
- A **"good enough" line per criterion**, so the choice is not "the biggest model"
- The questions only you can answer: procurement constraints, existing vendor agreements, internal policy

**You do**
- [ ] Confirm or correct each hard filter, and add the ones only you know about
- [ ] Set the **weights** and the "good enough" levels — this is your judgment, not the AI's
- [ ] Check the filters with security/procurement where they apply
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `model-requirements.md`: the hard filters with their source, the weighted criteria, and the "good enough" level per criterion.

**Review rules**
- Every hard filter traces to a **constraint written in an approved artifact**, not to preference.
- The context-window filter uses the **measured** Phase 02 budget total.
- The weights are yours. Say where they differ from the AI's proposal.
- Each criterion has a "good enough" level, so a smaller model can win.
- The data-usage and residency filters match the 02.3 sensitivity plan.

**Done when** you approve the requirements.

---

### 03.2 Candidate shortlist

```yaml task
id: "03.2"
title: Candidate shortlist
role: AI
depends_on: ["03.1"]
estimate: {S: 2, M-L: 4}
artifact: candidate-shortlist.md
optional_tag: null
sets_tags: []
```

**Plan** (`03.2-plan.md`): where the candidate facts will come from (provider docs and pricing pages, consulted fresh, never from memory), and which accounts or quotas you must provide for a candidate to be testable.

**Build**
- [ ] Pick **3–5 candidates** across tiers: frontier, mid-tier, and small/fast or open-weight
- [ ] Apply the hard filters, and record **why each excluded model failed**
- [ ] For each candidate, check against current provider documentation:
  - [ ] Availability in your provider/region
  - [ ] Quotas and rate limits at the expected load (from the Phase 01 cost model)
  - [ ] Pricing (input/output tokens, caching, batch discounts)
  - [ ] **Deprecation schedule** and version-pinning options
- [ ] Include at least one candidate from a **different provider or family**, as a fallback option
- [ ] Confirm access: which candidates can actually be called today, and what is missing for the others

**AI writes** `candidate-shortlist.md`: the candidate table with pinned model IDs, the filter results with reasons, prices and limits **with the date and the source URL for each figure**, and the access status per candidate.

**Review rules**
- Every price, limit and deprecation date carries a **source and a date**. Nothing from memory.
- Excluded models are listed with the filter they failed.
- At least one candidate comes from a different provider/family.
- Model IDs are the **pinned** ones, not floating aliases.
- Candidates that cannot be called yet are flagged, with what is needed.

**Done when** you approve the shortlist.

---

### 03.3 Dev eval harness

```yaml task
id: "03.3"
title: Dev eval harness
role: AI
depends_on: ["03.0"]
estimate: {S: 4, M-L: 10}
artifact: eval-harness.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): define quality metrics, collect metadata.*

**Plan** (`03.3-plan.md`): the harness's repo location and shape, the automatic checks it will implement, the experiment log format, the expected token spend of a full dev run, and what it needs from you (API keys, a spend cap).

**Build**
- [ ] Script a runner that executes a configuration (model + prompt + params + context config) over the **dev** set
- [ ] Implement **automatic checks first**: output format/schema, required citations present, exact/contains match where possible, refusal on unanswerable or forbidden items
- [ ] Draft **LLM-judge rubrics** for subjective criteria (correctness, groundedness, tone). Calibration against humans happens in Phase 04, so treat these scores as directional
- [ ] Capture **latency and token usage/cost** per item
- [ ] Run **N samples per item** (e.g. 3) on a subset, to measure variance from non-determinism
- [ ] Log every run's **metadata**: model ID and version, prompt version, sampling params, context/retrieval config, eval set version, date, and results
- [ ] Report results **per case type** (normal / edge / failure / forbidden / unanswerable), not just as an average
- [ ] Guard the harness against the held-out split: it must refuse to load it

**AI writes** `eval-harness.md`: repo paths, how to run it, the checks implemented, the rubric drafts, the experiment log location and format (template below), and the measured cost of one full dev run.

**Review rules**
- The harness **refuses to load the held-out split**. Show the guard.
- Automatic checks come first; the judge only scores what they can't.
- Every run writes a complete log entry. Show one real entry.
- Results are reported per case type, with the sample count per type.
- The cost of a dev run is measured and stated, so iterations can be budgeted.

**Done when** you approve the harness, and a full dev run completes and logs its results.

---

### 03.4 Baseline bake-off

```yaml task
id: "03.4"
title: Baseline bake-off
role: AI
depends_on: ["03.2", "03.3"]
estimate: {S: 2.5, M-L: 7}
artifact: model-selection-matrix.md
optional_tag: null
sets_tags: []
```

**Plan** (`03.4-plan.md`): the baseline prompt, the run matrix (candidates × samples), the estimated spend, and the confirmation you must give before the money is spent.

**Build**
- [ ] Write a **simple baseline prompt**: plain instructions, no tricks
- [ ] Run every candidate with the **same** baseline prompt and context on the dev set
- [ ] Compare quality (per case type), latency p50/p95, cost per task, and failure patterns
- [ ] Compare against the **heuristic benchmark** from Phase 01. If no candidate beats it, stop and say so — that is a finding for 03.4b, not something to fix with a better prompt
- [ ] Check whether routing by difficulty (a small model for easy cases, a large one for hard ones) is supported by a clear split in the dev data
- [ ] Fill the selection matrix (template below) with the measured numbers and the weighted scores

**AI writes** `model-selection-matrix.md`: the matrix, the run ids behind every cell, the failure patterns per candidate, the heuristic-benchmark comparison, and the routing analysis.

**Review rules**
- Every candidate ran the **same** prompt, context and eval-set version. Any deviation is stated.
- Every cell traces to a run id in the experiment log.
- The heuristic benchmark was run, and the comparison is explicit.
- Latency and cost are **measured**, not taken from a price page.
- The matrix states a weighted score per candidate using the 03.1 weights, and no candidate is recommended here — that is 03.4b's job.

**Done when** you approve the matrix.

---

### 03.4b Choose primary & fallback

```yaml task
id: "03.4b"
title: Choose primary & fallback
role: DECISION
depends_on: ["03.4"]
estimate: {S: 0.5, M-L: 1}
artifact: null
optional_tag: null
sets_tags: ["SH"]
```

**Brief** (`03.4b-brief.md`): the selection matrix, the weighted scores, the failure patterns, the cost and latency at the expected load, deprecation risk per candidate, and the hosting consequence of each choice (managed API vs self-hosted, with its operational cost).

**Options**
- Each candidate that passes the hard filters, as **primary**, paired with a **fallback from a different provider or family**
- **Route by difficulty**: a small model plus a large one, if 03.4 found a clear split
- **Back to 03.2**: no candidate is good enough; widen the shortlist
- **Back to Phase 01**: nothing beats the heuristic benchmark. Reset 01.6/01.8 with `--cascade`, or stop the project

End the brief with **AI recommendation:** `<primary> + <fallback>`, followed by its reasoning.

**Decision record**: a `## 03.4b` entry in `decisions.md` with the chosen primary and fallback (pinned IDs), the hosting paradigm, and the evidence. Then `set 03.4b done --tag SH=yes|no`, where `yes` means self-hosted.

---

### 03.5 Prompt engineering

```yaml task
id: "03.5"
title: Prompt engineering
role: AI
depends_on: ["03.4b"]
estimate: {S: 4, M-L: 10}
artifact: prompt-record.md
optional_tag: null
sets_tags: []
```

*Rung 1 of the customization ladder.*

**Plan** (`03.5-plan.md`): the prompt structure, the time-box and stopping rule, the error-analysis loop, and the estimated spend of the iterations.

**Build**
- [ ] Structure the system prompt:
  - [ ] Role and task, taken from the outcome frame
  - [ ] The spec's **invariants** and **forbidden** behavior, stated explicitly
  - [ ] How to use the context: cite sources, treat retrieved/tool content as **untrusted data, not instructions** (02.8)
  - [ ] The "I don't know" / refusal behavior
  - [ ] The output format, using **structured output / JSON schema** when a program consumes it
- [ ] Add **few-shot examples** drawn from the dev set, never the held-out set, covering the edge and failure cases
- [ ] Tune the sampling params (temperature etc.) for the task, and record them
- [ ] Run an **error-analysis loop**:
  1. Run the dev set
  2. Group the failures into categories
  3. Fix the largest category
  4. Re-run the full dev set to catch regressions
- [ ] Keep prompts as **versioned templates in git**, with variables for the context slots, not strings scattered through the code
- [ ] Stop when the thresholds are met, or when the gains flatten out. Record what the prompt could not fix — that goes to 03.9

**AI writes** `prompt-record.md`: the prompt template paths and versions, the sampling params, the error-analysis log (iteration → failure category → change → result per case type), the final dev results against the thresholds, and the **unfixed failure categories with their root causes**.

**Review rules**
- The prompt states every **invariant and forbidden behavior** from the spec. List them against the spec, one by one.
- Untrusted content is handled as 02.8 requires.
- Few-shot examples come from the **dev** set only.
- Each iteration re-ran the **full** dev set, so regressions are visible.
- Prompts are versioned files in git, referenced by version in every run.
- The unfixed categories are named with a root cause (knowledge / behavior / latency / cost), ready for 03.9.

**Done when** you approve the prompt record, and the dev results and the remaining gaps are stated against the thresholds.

---

### 03.6 Context/retrieval tuning `[R]`

```yaml task
id: "03.6"
title: Context/retrieval tuning
role: AI
depends_on: ["03.5"]
estimate: {S: 2, M-L: 6}
artifact: retrieval-tuning.md
optional_tag: R
sets_tags: []
```

*Rung 2.*

**Plan** (`03.6-plan.md`): which knobs will be tuned (top-k, reranker, threshold, chunk ordering), how retrieval misses will be distinguished from generation misses, and the spend.

**Build**
- [ ] Using the **end-to-end** dev results, tune top-k, the reranker on/off, the score threshold, and the chunk ordering in context
- [ ] Classify each failure as a **retrieval miss** (the right chunk was not in context) or a **generation miss** (the chunk was there but the model ignored or misused it). Send retrieval misses back to 02.5–02.6
- [ ] Try query rewriting or decomposition only if the error analysis shows the queries don't match how the documents are phrased
- [ ] Re-check the token budget and the cost per task after the changes

**AI writes** `retrieval-tuning.md`: the before/after numbers per knob with run ids, the miss classification with counts, anything sent back to Phase 02, and the updated token budget and cost per task.

**Review rules**
- Every knob change is **measured** on the dev set, and losing changes are reverted and reported.
- The retrieval-vs-generation split is quantified, not asserted.
- Changes needed in Phase 02 are recorded as such. If they are material, 02.5/02.6 are reopened with `--cascade` rather than patched here.
- The token budget and cost per task are re-checked against 02.8 and the Phase 01 cost model.
- The **held-out set was not touched**.

**Done when** you approve the tuning record.

---

### 03.7 Tool design `[A]`

```yaml task
id: "03.7"
title: Tool design
role: AI
depends_on: ["03.5"]
estimate: {S: 3, M-L: 8}
artifact: tool-specs.md
optional_tag: A
sets_tags: []
```

*Rung 3.*

**Plan** (`03.7-plan.md`): the minimum tool set, which tools are read-only and which have side effects, the systems each one touches, and what it needs from you (sandbox credentials, test accounts, permission to call a real system).

**Build**
- [ ] Define the **minimum set of tools** the slice needs. **Prefer read-only tools first**
- [ ] For each tool, write:
  - [ ] A clear name, and a description of **when to use it and when not to**
  - [ ] A strict input schema (types, enums, required fields)
  - [ ] An output shaped to the Phase 02 budget (only the needed fields, truncated)
  - [ ] Informative **error messages** the model can recover from
  - [ ] Side effects, idempotency, and whether a retry is safe
- [ ] Test tool selection on the dev set: right tool, right arguments, no unnecessary calls
- [ ] Run every test against a **sandbox**, never production

**AI writes** `tool-specs.md`: one specification per tool (template below), the repo paths, and the measured tool-selection results on the dev set.

**Review rules**
- Every tool with a side effect is justified: why a read-only tool won't do.
- Each spec names its authority class from the spec's Locked / Bounded / Delegated table.
- Output size is bounded and fits the 02.8 budget.
- Tool-selection accuracy is **measured** on the dev set, including unnecessary-call rate.
- No test touched a production system. Say which sandbox was used.

**Done when** you approve the tool specifications.

---

### 03.8 Orchestration & authority `[A]`

```yaml task
id: "03.8"
title: Orchestration & authority
role: AI
depends_on: ["03.7"]
estimate: {S: 3, M-L: 8}
artifact: orchestration-design.md
optional_tag: A
sets_tags: []
```

**Plan** (`03.8-plan.md`): the orchestration patterns considered, the authority mapping approach, the limits to enforce, and the trace format Phase 04 and Phase 06 will consume.

**Build**
- [ ] Choose the **simplest pattern** that works:
  1. A single call
  2. A fixed chain/workflow (the code decides the steps)
  3. An agent loop (the model decides the steps)

  Record why the simpler patterns were not enough
- [ ] Map the spec's **Locked / Bounded / Delegated** decisions to tool permissions:
  - [ ] **Locked** actions: the model never does them, or does them only with **human approval**
  - [ ] **Bounded** actions: allowed within explicit limits (amount, scope, count)
  - [ ] **Delegated** actions: allowed, with the model's reasoning logged
- [ ] Require approval for **any action triggered by untrusted content** (retrieved docs, tool outputs, user uploads)
- [ ] Set **limits**: maximum steps/iterations, timeouts, and a token/cost budget per task
- [ ] Define **failure handling**: retry with backoff, fallback model, and a graceful hand-off to a human
- [ ] Emit **traces**: every step, tool call, argument, and result, for Phase 04 and Phase 06

**AI writes** `orchestration-design.md`: the chosen pattern with the rejection reasons for the simpler ones, the **authority map** (spec decision → tool → Locked/Bounded/Delegated → enforcement point), the limits with their values, the failure handling, and the trace schema.

**Review rules**
- The pattern is the simplest one the evidence allows, and the evidence is shown.
- Every Locked decision in the spec has an enforcement point in **code**, not in the prompt alone.
- Untrusted content cannot trigger a consequential action without approval. Show where that is enforced.
- The limits (steps, timeout, budget) have concrete values, and exceeding one is tested.
- The trace schema carries everything Phase 04 (trajectory eval) and Phase 06 (monitoring) need.

**Done when** you approve the orchestration design and the authority map.

---

### 03.9 Escalation gate: fine-tune or not

```yaml task
id: "03.9"
title: "Escalation gate: fine-tune or not"
role: DECISION
depends_on: ["03.6", "03.8"]
estimate: {S: 1, M-L: 2}
artifact: null
optional_tag: null
sets_tags: ["FT"]
```

**Brief** (`03.9-brief.md`), using the escalation gate record template:
- The **best result** from rungs 1–3 against each threshold
- Each remaining failure category with its **root cause**:
  - **Missing knowledge** → fix with retrieval/context (back to Phase 02), not fine-tuning
  - **Behavior, format, style, domain language** that prompting can't hold reliably → a fine-tuning candidate
  - **Latency or cost** too high with a large model → a candidate for **distillation** into a smaller model
- The **preconditions**: enough high-quality labeled examples (typically hundreds or more), budget for training and hosting, and a named owner for re-tuning when the base model is deprecated
- The cost of fine-tuning versus its expected gain

**Options**
- **No fine-tuning** (`--tag FT=no`): thresholds are met, or the gaps aren't a fine-tuning problem. 03.10 becomes `n/a`.
- **Fine-tune** (`--tag FT=yes`): the preconditions hold, and the gap is a behavior/format one.
- **Back to Phase 02**: the root cause is missing knowledge. Reset 02.5/02.6 with `--cascade`.
- **Back to 03.5**: prompting was not exhausted.

End the brief with **AI recommendation:** `<option>`, followed by its reasoning.

**Decision record**: a `## 03.9` entry in `decisions.md` with the gate record, the decision and the rationale. Then `set 03.9 done --tag FT=yes|no`.

---

### 03.10 Fine-tuning `[FT]`

```yaml task
id: "03.10"
title: Fine-tuning
role: AI
depends_on: ["03.9"]
estimate: {S: 8, M-L: 24}
artifact: fine-tuning-record.md
optional_tag: FT
sets_tags: []
```

*Rung 4.*

**Plan** (`03.10-plan.md`): the training data's source and size, the method, where training runs, the **expected compute cost**, the hosting consequence, and the explicit spend approval it needs from you.

**Build**
- [ ] Build the training set from labeled examples and approved production-like data. **Exclude the held-out set**, and check that none of its items leaked in
- [ ] Clean and deduplicate the data, apply the sensitivity plan, and split into train and validation
- [ ] Choose the method: PEFT/LoRA (the default), full fine-tuning, or **distillation** from a stronger model
- [ ] Choose where to run it: the provider's managed fine-tuning or self-hosted. Check the effect on hosting cost and on the data-usage policy
- [ ] Train with experiment tracking: base model version, data version, hyperparameters, and training cost
- [ ] Compare against **base model + best prompt** on the dev set. It must clearly win on the targeted failure categories
- [ ] Check for **regressions**: general ability, refusal/safety behavior, and the formats the prompt handled before
- [ ] Record the training data sheet and the training record

**AI writes** `fine-tuning-record.md`: the training data sheet (source, size, dedup, sensitivity handling, split), the method and hyperparameters, the measured training cost, the comparison against base + prompt per case type, the regression results, and the pinned fine-tuned model ID.

**Review rules**
- A **contamination check against the held-out set** was run, and its result is stated.
- The fine-tuned model beats base + best prompt on the **targeted** categories, with the numbers shown.
- Safety and refusal behavior did not regress. Show the comparison.
- Training data complies with the 02.3 sensitivity plan and the provider's data-usage policy.
- Training cost and new hosting cost are measured and folded into the cost model.

**Done when** you approve the record, and the fine-tuned model beats base + prompt with no regressions.

---

### 03.11 Robustness smoke tests

```yaml task
id: "03.11"
title: Robustness smoke tests
role: AI
depends_on: ["03.10"]
estimate: {S: 2, M-L: 4}
artifact: robustness-smoke-report.md
optional_tag: null
sets_tags: []
```

**Plan** (`03.11-plan.md`): the test set for each check below, how a failure will be judged, and the spend.

**Build**
- [ ] **Variance**: re-run a dev subset N times, and flag items with unstable answers
- [ ] **Paraphrase**: reword the inputs, and check the answers stay the same
- [ ] **Basic injection**: plant instructions in retrieved docs, tool outputs, and user input. The model must not follow them, or call tools because of them `[A]`
- [ ] **Overflow**: inputs and histories longer than the budget trigger the defined overflow behavior
- [ ] **Fallback**: run the fallback model on the dev set, so its quality is known before it is ever needed
- [ ] These are **smoke tests**. Full red-teaming happens in [Phase 04](04-evaluation.md)

**AI writes** `robustness-smoke-report.md`: each check with its method, sample size, result and run id, the unstable items, and the fallback model's dev results.

**Review rules**
- Every check ran, or is recorded as not applicable with a reason.
- Injection tests cover **every untrusted channel** in the 02.8 design `[A]`.
- The fallback model's quality is measured, not assumed.
- Failures are listed as known risks for Phase 04 to red-team, not hidden.
- Nothing here touched the **held-out** set.

**Done when** you approve the report.

---

### 03.12 Configuration freeze & system card

```yaml task
id: "03.12"
title: Configuration freeze & system card
role: AI
depends_on: ["03.11"]
estimate: {S: 2, M-L: 4}
artifact: [frozen-config.md, system-card.md]
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): documentation.*

**Plan** (`03.12-plan.md`): what the freeze covers, how it is pinned in git, and how the rebuild will be verified.

**Build**
- [ ] **Freeze** the release-candidate configuration:
  - [ ] Pinned model ID(s): primary, fallback, and fine-tuned if any
  - [ ] Prompt template versions and sampling params
  - [ ] Context/retrieval config and index version `[R]`
  - [ ] Tool and orchestration versions, limits, and the authority map `[A]`
- [ ] Update the **cost model** with the measured cost per task and latency at the expected load
- [ ] Write the **system card** (template below): intended use, out-of-scope uses, models, data sources, customization done, dev results per case type, known limitations, and the safety measures in place
- [ ] Verify the whole configuration can be **rebuilt from git + versioned artifacts**, by rebuilding it

**AI writes** `frozen-config.md` (the pinned configuration, the git ref, and the rebuild procedure with its verification) and `system-card.md`.

**Review rules**
- Every element of the configuration is pinned to a **version or commit**. No floating aliases.
- The rebuild was **performed**, and the artifact says so with the commands used.
- The updated cost per task and latency are measured, and compared with the Phase 01 cost model.
- The system card's known limitations match the unfixed failure categories from 03.5–03.11. Nothing is quietly dropped.
- The card names an owner.

**Done when** you approve the frozen configuration and the system card.

---

### 03.13 Phase gate → Phase 04

```yaml task
id: "03.13"
title: Phase gate → Phase 04
role: DECISION
depends_on: ["03.12"]
estimate: {S: 1, M-L: 2}
artifact: null
optional_tag: null
sets_tags: []
```

**Brief** (`03.13-brief.md`)
- The **exit gate walk-through** below, item by item, citing artifacts
- The open issues and the known failure categories
- The **handoff to [Phase 04](04-evaluation.md)**: the frozen config, system card, eval harness, LLM-judge rubrics (to calibrate), robustness report, and the known risks to red-team
- Whether the dev results justify spending Phase 04's evaluation effort

**Options**
- **Continue**: proceed to 04.0.
- **Continue with conditions**: name them and their owners.
- **Back to task X**: a gate item fails within this phase. Reset it with `--cascade`.
- **Back to Phase 02**: the failures are knowledge or retrieval problems.
- **Stop**: the thresholds cannot be reached at an acceptable cost.

End the brief with **AI recommendation:** `<option>`, followed by its reasoning.

**Decision record**: a `## 03.13` entry in `decisions.md`, with the rationale, the conditions and their owners, and who signed off.

---

## Quality assurance

### Requirements & constraints

- The chosen model(s) pass every hard filter, including context window, data residency, and data-usage policy.
- The dev results meet the Phase 01 quality thresholds and beat the heuristic benchmark.
- Latency and cost per task at the expected load fit the Phase 01 constraints.
- The prompts respect the spec: invariants and forbidden behavior are stated, and untrusted content is kept apart from instructions.
- `[A]` Every tool action respects the authority map, with limits and approvals in place.
- `[FT]` Fine-tuning was justified by the escalation gate, and the fine-tuned model beats base + prompt with no regressions.
- The configuration is frozen, reproducible, and documented in the system card.

### Risks → QA measures

| Risk | QA measure | Task |
|------|------------|------|
| Lack of reproducibility (model changed, prompt edited ad hoc) | Pinned model IDs, versioned prompt templates, experiment log, config freeze | 03.3, 03.5, 03.12 |
| Poor generalization: overfitting prompts/examples to the dev set | Held-out set locked (harness guard), results per case type, paraphrase tests | 03.0, 03.3, 03.11 |
| Inadequate documentation | Selection matrix, gate record, system card | 03.4, 03.9, 03.12 |
| Choosing the biggest model by default (cost/latency blow-up) | Weighted criteria with "good enough" levels, cost per task measured | 03.1, 03.4, 03.4b |
| Vendor outage, deprecation, or lock-in | Deprecation check, fallback from another provider, fallback quality measured | 03.2, 03.4b, 03.11 |
| Non-deterministic outputs | N samples per item, variance check, sampling params tuned and recorded | 03.3, 03.5, 03.11 |
| Output format breaks downstream code | Structured output / schema + automatic format checks | 03.3, 03.5 |
| Retrieval misses blamed on the model (or the reverse) | Retrieval vs generation miss analysis | 03.6 |
| `[A]` Excessive agency (unapproved consequential actions) | Authority map from Locked/Bounded/Delegated, human approval, read-only first | 03.7, 03.8 |
| `[A]` Runaway loops or cost | Step limits, timeouts, per-task budget | 03.8 |
| Prompt injection via context that triggers actions | Untrusted content marked, approval for actions it triggers, injection smoke tests | 03.5, 03.8, 03.11 |
| Fine-tuning used to fix missing knowledge | Root-cause classification at the escalation gate | 03.9 |
| `[FT]` Fine-tuning degrades safety or general ability, or leaks eval data | Regression checks, held-out exclusion check | 03.10 |
| Model facts taken from memory instead of the provider's docs | Every price, limit and date carries a source and a date | 03.2 |

### Exit gate (walked in 03.13)

- [ ] The primary and fallback models are chosen with documented evidence, and both pass the hard filters.
- [ ] Dev results meet the thresholds, per case type, and beat the heuristic benchmark.
- [ ] Measured latency and cost per task fit the constraints at the expected load.
- [ ] Prompts are versioned and every run is logged in the experiment log.
- [ ] `[A]` Tools are specified, the authority map is enforced, and limits are set.
- [ ] The escalation gate is recorded. `[FT]` The fine-tuned model beats base + prompt with no regressions.
- [ ] The robustness smoke tests pass, or their failures are recorded as known risks.
- [ ] The configuration is frozen and the system card is written.
- [ ] The handoff to Phase 04 is recorded in the 03.13 decision entry.

---

## Templates

### Model selection matrix

| Candidate | Hard filters | Quality (dev, per case type) | p50 / p95 latency | Cost / task | Rate limits OK? | Deprecation risk | Weighted score | Decision |
|-----------|--------------|------------------------------|-------------------|-------------|-----------------|------------------|----------------|----------|
| | pass / fail (why) | | | | | | | primary / fallback / rejected |

### Experiment log entry

```text
run_id / date:
model_id (pinned):
prompt_version:
params:            (temperature, max_tokens, ...)
context_config:    (top-k, reranker, budget version)      [R]
tools / orchestration version:                            [A]
eval_set_version:  (dev)
samples_per_item:
results:           (per case type + overall)
latency p50/p95:
cost / task:
notes / failure categories:
```

### Escalation gate record

```text
Best rung reached:    prompting | retrieval tuning | tools/agents
Threshold gaps:       (metric → current vs target)
Remaining failures:   (category → root cause: knowledge | behavior/format | latency/cost)
Preconditions:        labeled examples: __  budget: __  re-tune owner: __
Decision:             FT go / no-go
Rationale:
```

### Tool specification `[A]`

```text
name:
purpose / when to use / when NOT to use:
input schema:
output (fields, max size):
side effects:         none | reversible | irreversible
authority:            Locked (approval) | Bounded (limits: __) | Delegated
idempotent / safe to retry:
error messages:
```

### System card

```text
Intended use:
Out-of-scope uses:
Models:               primary / fallback / fine-tuned (pinned ids)
Data sources:         (from Phase 02 inventory)
Customization:        prompt vX, retrieval config, tools, FT
Dev results:          (per case type, date, eval set version)
Latency / cost:
Known limitations:
Safety measures:      (guardrails, authority map, limits)
Owner / contact:
```
