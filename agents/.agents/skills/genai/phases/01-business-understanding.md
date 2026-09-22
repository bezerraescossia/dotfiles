# Phase 01: Business Understanding

> Understand the business problem before choosing a solution. Decide whether GenAI is relevant at all, what success looks like, what could go wrong, and which small slice is worth building first.

**CRISP-ML(Q) origin:** *Business and Data Understanding*. For GenAI, this phase keeps only a **light data check** (does the knowledge exist, and can we use it?). Deep profiling moves to [Phase 02](02-context-engineering.md). The CRISP-ML(Q) proof of concept is replaced by the **smallest testable slice** plus its spec.

## How this file is used

Every task below is **executable with `/genai`**. The fenced `yaml task` block is read by the checker, and the prose sections are the playbook.

| Role | Loop |
|------|------|
| **HUMAN** | **AI prepares** a prep kit → **You do** the work and drop raw notes in `.genai/inbox/` → **AI turns** the notes **into** the artifact → AI checks it against the **Review rules** → you approve (**Done when**) |
| **DECISION** | AI writes a **Brief** with the **Options** and a clearly labeled recommendation → you decide → the **Decision record** goes into `.genai/decisions.md` |

Artifacts and prep kits are written to `.genai/artifacts/01-business-understanding/`. A prep kit is named `<id>-prep.md`, and a DECISION brief is named `<id>-brief.md`.

## Task graph

| Task | Title | Role | Depends on | S | M-L |
|------|-------|------|------------|---|-----|
| 01.0 | Kickoff & stakeholder map | HUMAN | – | 2h | 4h |
| 01.1 | Outcome frame | HUMAN | 01.0 | 3h | 6h |
| 01.2 | Discover the real workflow | HUMAN | 01.0 | 8h | 20h |
| 01.3 | GenAI fit, feasibility & data check | HUMAN | 01.1, 01.2 | 3.5h | 9h |
| 01.3b | Continue with GenAI? | DECISION | 01.3 | 0.5h | 1h |
| 01.4 | Success metrics, benchmark & baseline | HUMAN | 01.3b | 4h | 10h |
| 01.5 | Assumptions & risk | HUMAN | 01.4 | 4h | 10h |
| 01.6 | Candidate slices | HUMAN | 01.5 | 1.5h | 4h |
| 01.7 | Choose the slice | DECISION | 01.6 | 0.5h | 1h |
| 01.8 | Slice spec | HUMAN | 01.7 | 4h | 10h |
| 01.9 | Go / pivot / stop | DECISION | 01.8 | 2h | 4h |
| | **Total** | | | **~33h (~4 days)** | **~79h (~2 weeks)** |

- Hours are **your hands-on effort**. Calendar time is usually longer because it depends on when stakeholders are available.
- **S**: small project (single team, one workflow, ~1–2 week engagement).
- **M-L**: medium/large project (several teams or workflows, regulated data, integrations).
- 01.1 and 01.2 can run in parallel.

---

## Tasks

### 01.0 Kickoff & stakeholder map

```yaml task
id: "01.0"
title: Kickoff & stakeholder map
role: HUMAN
depends_on: []
estimate: {S: 2, M-L: 4}
artifact: stakeholder-map.md
optional_tag: null
```

**AI prepares** (`01.0-prep.md`). First ask the user for whatever context exists (brief, emails, a one-paragraph description), or read it from `inbox/`. Then write:
- A **kickoff agenda** (45–60 min) whose goal is to leave with the **decision this phase must support**
- A **stakeholder checklist** of roles to identify: sponsor, final decision-maker, end users, practitioners doing the work today, SMEs, data owners, security / legal / compliance
- **Interview guides**, one per stakeholder type (sponsor, practitioner, data owner, compliance), with open questions about the problem, not about AI
- The **documents to request** before 01.2: tickets, runbooks, forms, reports, dashboards
- The **questions to leave the kickoff with answered**: communication cadence, the review date for the exit decision, and who signs off

**You do**
- [ ] Run the kickoff and the first stakeholder conversations
- [ ] Put your notes or transcripts in `.genai/inbox/` (any format)

**AI turns into** `stakeholder-map.md`:
- The stakeholder table: name/role, interest, influence, what they need from the project, availability
- The **decision this phase must support**, in one sentence
- Cadence, review date, sign-off owners
- Documents requested, and who will provide them
- **Gaps**: every role or answer your notes don't cover

**Review rules**
- There is a named **sponsor** and a named **final decision-maker**. If either is missing, flag it as a blocker.
- The decision to support is a real decision (e.g. "fund a pilot or not"), not a topic.
- Practitioners who do the work today are included, not just managers.
- Nothing is invented: every name and fact traces back to your notes.

**Done when** you approve the stakeholder map, and the sponsor, the decision-maker, and the decision to support are all recorded.

---

### 01.1 Outcome frame

```yaml task
id: "01.1"
title: Outcome frame
role: HUMAN
depends_on: ["01.0"]
estimate: {S: 3, M-L: 6}
artifact: outcome-frame.md
optional_tag: null
```

*Source: L47 — Outcomes before output.*

**AI prepares** (`01.1-prep.md`)
- A **draft outcome frame** filled from the 01.0 artifacts, with every unsupported field marked `GAP`
- A **conversation guide** for the sponsor/decision-maker, to fill the gaps: who benefits, the current behavior, the desired change, constraints, non-goals
- A **constraint prompt list**: production impact, response time, audit & authority preservation, runtime dependencies, accessibility
- A **solution-leakage watch list** for this project: the tools, models or UI forms stakeholders have already mentioned

**You do**
- [ ] Hold the conversation(s) and fill the gaps
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `outcome-frame.md` (template below): User / Situation / Current behavior / Desired change / Constraints / Non-goals, and the leakage check.

**Review rules**
- **No solution leakage.** The frame names no model, vector DB, framework, architecture, UI form, or cadence ("weekly AI summary"). A technology may appear only as a real compatibility constraint, with the reason written down.
- The **desired change** describes a change in behavior or outcome for the user (e.g. "users understand account changes before approval"), not an output of the system.
- Each constraint is concrete. Numbers are given where they exist, and the ones still needed are marked.
- The **non-goals** list at least one thing that must *not* change.

**Done when** you approve the frame, and it is confirmed by the sponsor and the decision-maker (say how it was confirmed).

---

### 01.2 Discover the real workflow

```yaml task
id: "01.2"
title: Discover the real workflow
role: HUMAN
depends_on: ["01.0"]
estimate: {S: 8, M-L: 20}
artifact: workflow-map.md
optional_tag: null
```

*Source: L48 — Discover the real workflow.*

**AI prepares** (`01.2-prep.md`)
- An **observation / shadowing protocol**: what to watch for (waits, copy-paste, side channels, approvals, error recovery, "steps people have stopped noticing"), and how to take notes
- A **practitioner interview guide** built on "walk me through the last time you did X", not on hypotheticals
- An **artifact collection checklist**: tickets, runbooks, logs, forms, outputs, system events
- A **consent note** for recording sessions
- A **draft workflow skeleton** from the 01.0 notes, with every step marked `inference`

**You do**
- [ ] Collect the artifacts
- [ ] Observe, shadow, or record real sessions (not demos)
- [ ] Interview practitioners about how the work *actually* happens
- [ ] Put notes, transcripts, and artifact exports in `.genai/inbox/`

**AI turns into** `workflow-map.md`: the workflow as **ordered actions with evidence**. For each step, record:
- the **evidence level**: direct behavior / artifact / reported / inference
- **friction**
- **hidden state**
- **authority**
- **exceptions**

Include the waits, side channels, approvals, error recovery, and the justified **variants**.

**Review rules**
- Every step carries an evidence level. **Only direct behavior and artifacts prove current behavior**, so flag any conclusion that rests only on "reported" or "inference" steps.
- Hidden state (facts kept in memory, chat, personal notes) is recorded explicitly. The knowledge check in 01.3 depends on it.
- Exceptions and error recovery are mapped, not just the happy path.
- The map describes what *is* done, not what *should* be done.

**Done when** you approve the map, and practitioners have walked through it and confirmed it (say who).

---

### 01.3 GenAI fit, feasibility & data check

```yaml task
id: "01.3"
title: GenAI fit, feasibility & data check
role: HUMAN
depends_on: ["01.1", "01.2"]
estimate: {S: 3.5, M-L: 9}
artifact: fit-feasibility.md
optional_tag: null
```

*Source: CRISP-ML(Q) feasibility; AWS Generative AI Lens, Scoping.*

**AI prepares** (`01.3-prep.md`), working from the outcome frame and the workflow map:
- A **relevance analysis**: could rules, search, or classic ML solve this? Argue each alternative honestly
- **Model-need questions**: modality; off-the-shelf vs customized (prompting, RAG, fine-tuning); single model vs orchestrated/agentic
- A **data check questionnaire** for data owners, about the knowledge the model would need (including hidden state from 01.2): where it lives, owner, access rights, licensing, retention, sensitivity (PII, confidential, regulated), volume, formats, change frequency
- A **feasibility checklist**, technical (integrations, latency budget, systems of record) and organizational (skills, ownership after launch, change management, budget owner)
- A **rough cost model**: the formula and the assumptions to confirm (prompt/context length × volume × model tier price, retrieval, orchestration steps), plus the load/peak questions and a hosting-paradigm comparison

**You do**
- [ ] Get the questionnaires answered (data owners, IT, the budget owner)
- [ ] Confirm or correct the cost assumptions
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `fit-feasibility.md`:
- The relevance verdict, with its reasoning
- The model-need answers
- The data check table
- Feasibility findings
- The cost model with a low / expected / high range
- The preferred hosting paradigm and why

**Review rules**
- The relevance verdict includes the **strongest case for not using GenAI**.
- Each data source records its owner, its access rights, and its sensitivity. "Unknown" is allowed only when it is flagged.
- Every cost-model number is either sourced or labeled as an assumption.
- Missing knowledge (it exists nowhere, or only in people's heads) is called out explicitly.

**Done when** you approve the note. It is the evidence for 01.3b.

---

### 01.3b Continue with GenAI?

```yaml task
id: "01.3b"
title: Continue with GenAI?
role: DECISION
depends_on: ["01.3"]
estimate: {S: 0.5, M-L: 1}
artifact: null
optional_tag: null
```

**Brief** (`01.3b-brief.md`): the fit verdict, the strongest alternative to GenAI, the data check result, the feasibility risks, and the cost range. Each point cites the artifact it comes from.

**Options**
- **Continue**: GenAI is relevant and feasible. Proceed to 01.4.
- **Reframe**: the problem is real, but the framing is wrong. Loop back to 01.1, and reset the tasks after it to `todo`.
- **Not GenAI**: solve it with rules, search, or classic ML. Stop this pipeline, and record the recommended alternative.
- **Stop**: not worth solving now (infeasible, no data, cost too high).

End the brief with **AI recommendation:** `<option>`, followed by its reasoning.

**Decision record**: add a `## 01.3b` entry to `decisions.md`. For *Not GenAI* or *Stop*, set the project status to `stopped`.

---

### 01.4 Success metrics, benchmark & baseline

```yaml task
id: "01.4"
title: Success metrics, benchmark & baseline
role: HUMAN
depends_on: ["01.3b"]
estimate: {S: 4, M-L: 10}
artifact: [metrics.md, seed-eval-set.md]
optional_tag: null
```

*Source: CRISP-ML(Q) KPIs; AWS Generative AI Lens (GENPERF01-BP02).*

**AI prepares** (`01.4-prep.md`)
- **Candidate KPIs**, derived from the outcome frame's desired change, each with a definition, a data source, and how it is measured
- **Quality metrics**: accuracy/groundedness, completeness, and tone/toxicity, with the org's AI policy questions listed
- **Operational thresholds to agree**: latency, throughput, cost per task
- A **baseline measurement plan**: what to measure in the current workflow (time, error rate, cost, volume), where from, and for how long
- **Heuristic benchmark candidates** (rules, keyword search, templates) that GenAI must beat
- A **seed eval set sampling plan**: pull real examples from the 01.2 artifacts, covering normal and edge cases. Include a labeling guide for SMEs

**You do**
- [ ] Agree the KPIs and targets with the decision-maker
- [ ] Measure the baseline
- [ ] Collect and label the seed examples
- [ ] Put your notes, measurements, and examples in `.genai/inbox/`

**AI turns into** `metrics.md` (the metrics sheet: KPI, quality metrics, thresholds, baseline, heuristic benchmark) and `seed-eval-set.md` (the examples with their case types).

**Review rules**
- Every metric has a **number**, a **source**, and a **measurement method**. Words like "fast" or "accurate" are not metrics.
- The baseline was **measured**, not estimated. If it was estimated, flag it.
- The heuristic benchmark is concrete enough to run.
- The seed eval set comes from **real** inputs and covers more than the happy path.

**Done when** you approve the sheet, and the decision-maker has agreed the targets.

---

### 01.5 Assumptions & risk

```yaml task
id: "01.5"
title: Assumptions & risk
role: HUMAN
depends_on: ["01.4"]
estimate: {S: 4, M-L: 10}
artifact: assumptions-risk.md
optional_tag: null
```

*Source: L49 — Map assumptions and risk; AWS Generative AI Lens, Scoping.*

**AI prepares** (`01.5-prep.md`)
- An **assumption list** extracted from every artifact so far (user, data, model, workflow, adoption, cost), with each assumption rewritten to be **falsifiable**
- **Proposed scores** for Impact / Uncertainty / Irreversibility (1–5), each with a one-line rationale for you to correct, ranked by **I × U + Irr**
- A **risk profile** draft: technology risks (hallucination, prompt injection, data leakage, model availability) and business risks (adoption, ROI, compliance, reputation)
- A pre-filled **Generative AI Security Scoping Matrix** (scope 1–5) for each use case
- A list of responsible-AI, privacy, and regulatory concerns, each needing an owner
- **Test designs** for the top 3 assumptions: the claim, a realistic sample, and an observable result

**You do**
- [ ] Correct the scores (the scoring is your judgment)
- [ ] Assign owners to the concerns
- [ ] Review the risks with security/compliance
- [ ] Run the riskiest assumption's test if it is cheap
- [ ] Put your notes and results in `.genai/inbox/`

**AI turns into** `assumptions-risk.md`: the scored assumption table (template below), the risk profile, the security scoping matrix, the concerns with owners, and the test design and result for the riskiest assumption.

**Review rules**
- Every assumption can be **proven false** by an observable result.
- The scores are the user's. Say where they differ from the AI's proposal.
- The riskiest assumption has a test design. If it was run, the evidence replaces the assumption.
- Every concern has an owner.

**Done when** you approve the table and the risk profile.

---

### 01.6 Candidate slices

```yaml task
id: "01.6"
title: Candidate slices
role: HUMAN
depends_on: ["01.5"]
estimate: {S: 1.5, M-L: 4}
artifact: candidate-slices.md
optional_tag: null
```

*Source: L50 — Choose the smallest testable slice.*

**AI prepares** (`01.6-prep.md`)
- The **required proof set**: the high-risk assumptions from 01.5 that the slice must test
- **3–5 candidate slices**, each with the proofs it covers
- An **eligibility check**: drop any candidate that removes the uncertainty being tested or skips the risky part of the workflow
- A **comparison table** for the eligible slices, pre-filled: outcome value, uncertainty reduction, effort, consequence risk

**You do**
- [ ] Challenge, adjust, or add candidates (with the team if useful)
- [ ] Correct the comparison
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `candidate-slices.md`: the proof set, the candidates, the eligibility results, and the comparison table (template below).

**Review rules**
- Every eligible slice covers the whole required proof set.
- **Anti-patterns are rejected**: UI-only builds, happy path only, demos with no repeatable measurement, platform-first investment.
- For each slice, the table says **which decision it would change**.

**Done when** you approve the candidate list. It is the evidence for 01.7.

---

### 01.7 Choose the slice

```yaml task
id: "01.7"
title: Choose the slice
role: DECISION
depends_on: ["01.6"]
estimate: {S: 0.5, M-L: 1}
artifact: null
optional_tag: null
```

**Brief** (`01.7-brief.md`): the comparison table, the proofs each slice covers, effort vs uncertainty reduction, and consequence risk.

**Options**: the eligible slices from `candidate-slices.md`, or **back to 01.5/01.6** if none is acceptable.

End the brief with **AI recommendation:** `<slice>`, followed by its reasoning.

**Decision record**: a `## 01.7` entry in `decisions.md`, giving the chosen slice, the decision it will change, and how its result will be read.

---

### 01.8 Slice spec

```yaml task
id: "01.8"
title: Slice spec
role: HUMAN
depends_on: ["01.7"]
estimate: {S: 4, M-L: 10}
artifact: slice-spec.md
optional_tag: null
```

*Source: L51 — Write specifications that preserve judgment.*

**AI prepares** (`01.8-prep.md`): a **draft spec** built from every artifact so far:
- **Outcome**: from the outcome frame
- **Invariants**: from the constraints and the risk profile
- **Examples**: normal, edge, failure, and **forbidden** cases, taken from the workflow map and the seed eval set
- **Non-goals**
- **Proof**: the verification levels, i.e. unit, wire, journey, and a replay set from the seed eval set
- **Proposed Locked / Bounded / Delegated** classifications for every decision, each marked as a proposal
- **Questions for you**: every place where the draft had to guess

**You do**
- [ ] Review the draft, alone or in a workshop with the stakeholders
- [ ] Decide each classification
- [ ] Answer the questions
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `slice-spec.md`: the final spec, plus the decision classification table (template below).

**Review rules**
- The examples are **concrete** (real inputs and expected behavior), not adjectives.
- Every **high risk** from 01.5 has an invariant or a forbidden example.
- Every decision is classified **by the user**. No proposal remains unconfirmed.
- **Locked**: non-negotiable. **Bounded**: has explicit limits. **Delegated**: the owner must explain their choice.

**Done when** you approve the spec.

---

### 01.9 Go / pivot / stop

```yaml task
id: "01.9"
title: Go / pivot / stop
role: DECISION
depends_on: ["01.8"]
estimate: {S: 2, M-L: 4}
artifact: null
optional_tag: null
```

**Brief** (`01.9-brief.md`):
- A **readout** for the stakeholders: outcome, workflow findings, metrics, top risks, slice, spec
- The **exit gate walk-through** (below), item by item, citing the artifacts
- The open questions, with owners
- The conditions a *go* should carry

**Options**
- **Go**: hand off to Phase 02.
- **Go with conditions**: say what the conditions are.
- **Pivot**: name the task to loop back to. Reset it and the tasks after it to `todo`.
- **Stop**: set the project status to `stopped`.

End the brief with **AI recommendation:** `<option>`, followed by its reasoning.

**Decision record**: a `## 01.9` entry in `decisions.md`, with the rationale, the conditions, the open questions and their owners, and who signed off.

---

## Quality assurance

### Requirements & constraints

- The outcome is measurable: a business KPI with a target, a baseline, and a heuristic benchmark to beat.
- Constraints are explicit (latency, cost per task, audit/authority, compliance), and each named technology has a stated reason.
- The knowledge the solution needs exists, and it is legal to use.
- The slice spec states what is locked, what is bounded, and what is delegated.

### Risks → QA measures

| Risk | QA measure | Task |
|------|------------|------|
| Unclear or unmeasurable success criteria | KPI + quality metrics + thresholds agreed with the decision-maker, and a baseline measured | 01.4 |
| GenAI not actually needed (rules/search would do) | Relevance check + an early gate + a non-LLM heuristic benchmark | 01.3, 01.3b, 01.4 |
| Solution-first framing | Outcome frame with a solution-leakage review and sponsor confirmation | 01.1 |
| Automating an imagined workflow | Evidence-labeled workflow map, validated with practitioners | 01.2 |
| Required knowledge missing, inaccessible, or not allowed | Light data check (existence, owner, rights, sensitivity) | 01.3 |
| Project infeasible (technically, organizationally, or financially) | Feasibility checks + rough cost model at the expected load | 01.3 |
| Security/compliance exposure misjudged | Security scoping matrix + responsible-AI concerns, each with an owner | 01.5 |
| Building on an untested critical assumption | Scored assumption table, with the riskiest one tested first | 01.5 |
| First build proves nothing | Slice eligibility check against the required proof set | 01.6, 01.7 |
| Builders over- or under-constrained | Spec with Locked / Bounded / Delegated decisions and forbidden examples | 01.8 |
| AI fills a gap with a guess | Gaps marked `GAP`, and review rules require every fact to trace to your notes | all |

### Exit gate (walked in 01.9)

- [ ] The outcome frame is approved, names no solution, and is confirmed by the sponsor.
- [ ] The workflow map is validated, and each step is labeled with its evidence level.
- [ ] GenAI fit, feasibility, the data check and the rough cost are assessed, and 01.3b decided *Continue*.
- [ ] The KPI, quality metrics, baseline, heuristic benchmark and seed eval set exist.
- [ ] The riskiest assumption is identified, with a test designed or already run.
- [ ] The slice is chosen (01.7), along with the decision it will change.
- [ ] The slice spec is approved.
- [ ] A **go / pivot / stop** decision is logged (01.9).

---

## Templates

### Outcome frame

```text
User:              
Situation:         
Current behavior:  
Desired change:    
Constraints:       (production impact, latency, audit/authority, runtime deps, accessibility)
Non-goals:         
Leakage check:     [ ] no solution, model, framework, or UI named without a stated constraint
```

### Assumption table

| Assumption (falsifiable) | Impact | Uncertainty | Irreversibility | Score (I×U+Irr) | Test | Result / decision |
|--------------------------|--------|-------------|-----------------|-----------------|------|-------------------|
| | | | | | | |

### Slice comparison

| Slice | Proofs covered | Outcome value | Uncertainty reduction | Effort | Consequence risk | Eligible? | Decision it changes |
|-------|----------------|---------------|-----------------------|--------|------------------|-----------|---------------------|
| | | | | | | | |

### Decision classification

| Decision | Locked / Bounded / Delegated | Limit or rationale |
|----------|------------------------------|--------------------|
| | | |
