# Phase 02: Context Engineering

> Turn the knowledge found in Phase 01 into context the model can use reliably, legally, and within budget. Build the eval data the later phases depend on.

**CRISP-ML(Q) origin:** *Data Engineering*. Feature selection, class balancing and normalization mostly drop out. In their place:
- Parsing, chunking and indexing
- Access control
- Designing what goes into the context window
- Curating eval data

"Unit tests for data" still applies, to the documents and to retrieval quality.

**Scope boundaries**
- **This phase owns:** the knowledge pipeline, **retrieval component tests**, the **context design and token budget**, and the eval data.
- **[Phase 03](03-model-selection-customization.md) owns:** prompt wording, few-shot examples, tool definitions, and model choice.
- **[Phase 04](04-evaluation.md) owns:** end-to-end evaluation (answers, groundedness, safety).

**Inputs from Phase 01:** light data check, workflow map (including hidden state), metrics sheet, seed eval set, slice spec, security scoping matrix, rough cost model.

## How this file is used

Every task below is **executable with `/genai`**. The fenced `yaml task` block is read by the checker, and the prose sections are the playbook.

| Role | Loop |
|------|------|
| **HUMAN** | **AI prepares** a prep kit → **You do** the work and drop raw notes in `.genai/inbox/` → **AI turns** the notes **into** the artifact → AI checks it against the **Review rules** → you approve (**Done when**) |
| **AI** | AI writes a **Plan** (what it will build, where, how it is tested, what it needs from you) → you approve it → AI **builds** in the project repo and records the result → AI checks it against the **Review rules** → you approve (**Done when**) |
| **DECISION** | AI writes a **Brief** with the **Options** and a clearly labeled recommendation → you decide → the **Decision record** goes into `.genai/decisions.md` |

Artifacts, prep kits (`<id>-prep.md`), plans (`<id>-plan.md`) and DECISION briefs (`<id>-brief.md`) are written to `.genai/artifacts/02-context-engineering/`. **Code lives in the project repo**, not in `.genai/`. The artifact records the paths, the commands run, and the measured results.

## The `[R]` tag

Tasks tagged **`[R]`** apply only **if the slice needs retrieval**, meaning the model needs knowledge that is not already in the user's input. **02.0 settles the tag** (`set 02.0 done --tag R=yes|no`). When it is off, the `[R]` tasks show as `n/a` and the checker refuses to start them. Items tagged `[R]` or `[if ACLs apply]` inside an untagged task work the same way: skip them and say so.

## Task graph

| Task | Title | Role | Depends on | S | M-L |
|------|-------|------|------------|---|-----|
| 02.0 | Handoff review & retrieval decision | DECISION | 01.9 | 1h | 3h |
| 02.1 | Source inventory & access | HUMAN | 02.0 | 3h | 8h |
| 02.2 | Data profiling & quality | AI | 02.1 | 4h | 12h |
| 02.3 | Sensitivity, PII & access control | HUMAN | 02.2 | 3h | 8h |
| 02.9 | Eval data | HUMAN | 02.2, 02.3 | 4h | 12h |
| 02.4 | Ingestion & parsing pipeline `[R]` | AI | 02.3 | 6h | 16h |
| 02.5 | Chunking & enrichment `[R]` | AI | 02.4, 02.9 | 3h | 8h |
| 02.6 | Indexing & retrieval `[R]` | AI | 02.5 | 4h | 10h |
| 02.7 | Freshness & lifecycle `[R]` | HUMAN | 02.6 | 2h | 5h |
| 02.8 | Context design & token budget | AI | 02.3, 02.6 | 3h | 8h |
| 02.10 | Retrieval component tests `[R]` | AI | 02.6, 02.9 | 3h | 8h |
| 02.11 | Phase gate → Phase 03 | DECISION | 02.7, 02.8, 02.9, 02.10 | 1h | 2h |
| | **Total, with retrieval** | | | **~37h (~5 days)** | **~100h (~2.5 weeks)** |
| | **Total, without retrieval** (`[R]` off) | | | **~19h (~2.5 days)** | **~53h (~1.5 weeks)** |

- Hours are **your hands-on effort**. 02.2 and 02.4 vary the most, depending on how messy the formats are (scans, tables, mixed languages).
- **S**: small project (a few sources, one format family, a single permission level).
- **M-L**: medium/large project (many sources and formats, document-level permissions, regulated data).
- 02.9 is listed before the `[R]` chain because the chunking comparison in 02.5 needs the eval set.

---

## Tasks

### 02.0 Handoff review & retrieval decision

```yaml task
id: "02.0"
title: Handoff review & retrieval decision
role: DECISION
depends_on: ["01.9"]
estimate: {S: 1, M-L: 3}
artifact: null
optional_tag: null
sets_tags: ["R"]
```

**Brief** (`02.0-brief.md`), built by re-reading the Phase 01 slice spec, metrics sheet, data check and security scoping matrix:
- What the slice must answer or do, and **which of it the user's own input already contains**
- The knowledge the model would need that is *not* in the input, including the **hidden state** from the workflow map
- Whether the access requested in Phase 01 has actually been granted, and what is still missing
- The spec's **invariants and forbidden examples that touch data** (e.g. "never show another customer's data")
- The cost and latency consequences of retrieval, from the Phase 01 cost model

**Options**
- **Retrieval needed** (`--tag R=yes`): the knowledge is external to the input. 02.4–02.7 and 02.10 apply.
- **No retrieval** (`--tag R=no`): everything the model needs arrives in the request, or fits in the prompt. Those tasks become `n/a`.
- **Back to 01.8**: the spec doesn't say enough to tell. Reset it with `--cascade`.

End the brief with **AI recommendation:** `<option>`, followed by its reasoning.

**Decision record**: a `## 02.0` entry in `decisions.md` with the retrieval verdict, the data-related invariants, and any access still outstanding. Then `set 02.0 done --tag R=yes|no`.

---

### 02.1 Source inventory & access

```yaml task
id: "02.1"
title: Source inventory & access
role: HUMAN
depends_on: ["02.0"]
estimate: {S: 3, M-L: 8}
artifact: source-inventory.md
optional_tag: null
sets_tags: []
```

**AI prepares** (`02.1-prep.md`)
- A **draft inventory** of every source the slice needs, taken from the Phase 01 data check and the workflow map, with each field the notes can't fill marked `GAP`. Include the **hidden state** (chat threads, personal notes, tribal knowledge)
- A **per-source questionnaire** for the owners: system, format, volume, update frequency, access method (API / export / DB), license and retention rules
- An **access request list**: which service credentials are needed, from whom, and for which environment
- A **scoping question list**: where sources overlap, which one is authoritative; which sources are in or out for this slice
- A **capture plan template** for knowledge that exists only in people's heads (SME write-up, FAQ, interview notes)

**You do**
- [ ] Get the questionnaire answered by each source owner
- [ ] Mark the **authoritative source** where several sources overlap
- [ ] Decide which sources are **in or out** for this slice. Keep it minimal, but cover the required proof set
- [ ] Request **service credentials / API access** for the pipeline, not personal accounts
- [ ] Decide, for head-only knowledge, whether it will be captured or marked out of scope
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `source-inventory.md`: the inventory table (template below), the in/out decision per source with its reason, the access status per source, and the capture plan for head-only knowledge.

**Review rules**
- Every source records an **owner**, an **access method**, and its **license/retention** rules. "Unknown" is allowed only when it is flagged.
- Where sources overlap, exactly one is marked **authoritative**.
- The in/out decision is justified against the slice's required proof set.
- Access is recorded as **granted, requested, or missing** — never assumed.
- Hidden state from the Phase 01 workflow map appears here, captured or explicitly out of scope.

**Done when** you approve the inventory, and every in-scope source is either accessible or has a named blocker.

---

### 02.2 Data profiling & quality

```yaml task
id: "02.2"
title: Data profiling & quality
role: AI
depends_on: ["02.1"]
estimate: {S: 4, M-L: 12}
artifact: data-sheet.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): document the statistical properties of the data.*

**Plan** (`02.2-plan.md`): the sampling method per source (representative, **not just the tidy ones**), the profiling script and where it will live in the repo, what it measures, and what it needs from you (credentials, an export, a VPN session).

**Build**
- [ ] Pull a representative sample from each source
- [ ] Profile it: document count, length distribution, formats, languages, structure (headings, tables, images, scans)
- [ ] Look for quality problems:
  - [ ] Duplicates and near-duplicates
  - [ ] Outdated or **conflicting versions** of the same fact
  - [ ] Broken extraction (tables, multi-column PDFs, scanned pages, embedded images)
  - [ ] Missing metadata (date, owner, version)
  - [ ] Content gaps: eval questions the sources cannot answer
- [ ] Check coverage against the **seed eval set** from Phase 01: can each question be answered from the sources?
- [ ] Record how the data is generated and maintained (who writes it, and when it changes) — ask if the notes don't say
- [ ] Propose **data quality requirements** (e.g. "no document older than X", "tables must survive parsing")
- [ ] Keep the **hard samples** (the worst PDFs, scans, tables) as a fixture set. 02.4 tests parsers against them

**AI writes** `data-sheet.md` (template below) per source, plus the repo paths of the profiling script and the hard-sample fixtures.

**Review rules**
- Every number comes from a **run** that is named in the artifact (script, date, sample size). Nothing is estimated.
- The sample is representative, and the method is stated. A convenience sample is labeled as one.
- Coverage against the seed eval set is reported item by item, not as an overall impression.
- The hard samples are stored in the repo, so 02.4 and CI can re-use them.
- Quality requirements are testable. Each one is marked as a proposal until you accept it.

**Done when** you approve the data sheet and its quality requirements.

---

### 02.3 Sensitivity, PII & access control

```yaml task
id: "02.3"
title: Sensitivity, PII & access control
role: HUMAN
depends_on: ["02.2"]
estimate: {S: 3, M-L: 8}
artifact: sensitivity-plan.md
optional_tag: null
sets_tags: []
```

**AI prepares** (`02.3-prep.md`)
- A **draft classification** of each source (public / internal / confidential / regulated), from the data sheet and the Phase 01 data check
- A **PII and secret scan** of the samples from 02.2, with a proposed strategy per finding: exclude, redact, mask, or pseudonymize
- The **permission-model question**: must retrieval respect each user's entitlements (document-level ACLs)? `[R]`
- A **compliance checklist** to walk with security/legal: data residency, retention, deletion obligations (e.g. right to be forgotten)
- A **provider-policy summary**: what may be sent to the model provider under its data-usage policy, and what may be logged
- The **diff to the Phase 01 security scoping matrix**: what this phase found that it didn't know

**You do**
- [ ] Confirm or correct the classification with the data owners
- [ ] Agree each PII/secret strategy
- [ ] Decide the permission model, and get it confirmed by whoever owns entitlements `[R]`
- [ ] Review residency, retention and deletion with security/legal
- [ ] Agree what may leave the org and what may be logged
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `sensitivity-plan.md`: the classification table, the PII/secret handling strategy per finding, the permission model, the residency/retention/deletion obligations with owners, the provider and logging rules, and the updated security scoping matrix.

**Review rules**
- Every source has a classification, and every PII/secret finding has a strategy and an owner.
- The permission model is explicit, including the "no ACLs needed" case and why `[R]`.
- What may be sent to the provider and what may be logged are written as **rules a pipeline can enforce**, not principles.
- Legal/compliance sign-off is recorded with a name and a date, or flagged as outstanding.
- The Phase 01 security scoping matrix is updated, and the changes are listed.

**Done when** you approve the plan, and the security/compliance contact has signed off where that is required.

---

### 02.4 Ingestion & parsing pipeline `[R]`

```yaml task
id: "02.4"
title: Ingestion & parsing pipeline
role: AI
depends_on: ["02.3"]
estimate: {S: 6, M-L: 16}
artifact: ingestion-pipeline.md
optional_tag: R
sets_tags: []
```

**Plan** (`02.4-plan.md`): the parser per format, the pipeline's shape and repo location, the versioning tool (e.g. DVC + git), the data tests, and what it needs from you (credentials, storage, a budget for OCR).

**Build**
- [ ] Choose a parser for each format (PDF, HTML, Office, tables, OCR for scans). **Test it on the hard samples from 02.2**
- [ ] Clean the content: strip boilerplate (headers, footers, navigation) and normalize whitespace and encoding
- [ ] Keep the structure: headings, lists, and tables (as markdown/structured text)
- [ ] Extract and attach **metadata**: source, URL/ID, title, section path, date, version, owner, **ACL**
- [ ] Apply the PII strategy from 02.3 inside the pipeline
- [ ] Make the pipeline **reproducible and idempotent**: re-running it gives the same output, with no duplicates
- [ ] **Version** the raw data, the processed data, and the pipeline config
- [ ] Add **data unit tests**: schema, required metadata present, no empty docs, no PII leaks, parse-quality checks on the known hard samples
- [ ] Wire the data tests into CI

**AI writes** `ingestion-pipeline.md`: repo paths, how to run it, the parser choice per format **with the measured comparison on the hard samples**, the versioning scheme, the test list with the latest run result, and known parse failures.

**Review rules**
- Parser choices are backed by a **measured** comparison on the 02.2 hard samples, not by reputation.
- Running the pipeline twice produces identical output. Say how that was verified.
- Every processed document carries the metadata 02.6 and 05.2 need, including its ACL `[if ACLs apply]`.
- The PII strategy from 02.3 is enforced **in the pipeline**, and a test proves it.
- The data tests fail loudly on a bad input. Show a deliberate failure.
- Raw data, processed data and config are versioned, and the artifact says how to restore a given version.

**Done when** you approve the pipeline record, and the data tests pass in CI.

---

### 02.9 Eval data

```yaml task
id: "02.9"
title: Eval data
role: HUMAN
depends_on: ["02.2", "02.3"]
estimate: {S: 4, M-L: 12}
artifact: eval-set.md
optional_tag: null
sets_tags: []
```

*CRISP-ML(Q): data splits.*

**AI prepares** (`02.9-prep.md`)
- A **candidate item list** expanded from the Phase 01 seed eval set with real inputs (tickets, logs, recorded questions) found in the 01.2 artifacts and the 02.2 samples
- The **case-type coverage matrix** from the slice spec: normal, edge, failure, forbidden, plus **unanswerable** items (the right behavior is "I don't know"), **access-restricted** items `[if ACLs apply]`, and items affected by stale or conflicting sources
- A **labeling guide** for the SMEs: what a good answer is, the rubric wording, and how to record the relevant source docs `[R]`
- A **proposed dev / held-out split** (the held-out set is used only in Phase 04), and the storage/versioning layout next to the data
- An **agreement-check sample** for the subjective items, to be labeled by two people

**You do**
- [ ] Collect the real inputs, and add the missing case types
- [ ] Have SMEs label the items, and spot-check agreement between labelers on the subjective ones
- [ ] Confirm the split, keeping the **held-out set sealed**
- [ ] Put the labeled items and your notes in `.genai/inbox/`

**AI turns into** `eval-set.md` (the item inventory, per case type, with the repo path and version of the actual data files, the labeling guide, the agreement result and the changelog). Each item follows the template below.

**Review rules**
- Items come from **real** inputs. Invented items are marked as such, and are a minority.
- Every case type in the spec is covered, and the counts per type are stated. Unanswerable items exist.
- Access-restricted items exist whenever ACLs apply `[if ACLs apply]`.
- The **held-out split is sealed**: the artifact says where it is and who may open it (only Phase 04).
- The eval set is versioned next to the data, with a changelog.
- Labeler agreement is measured on the subjective items, and a low score sends the rubric back for rewording.

**Done when** you approve the eval set, the split is recorded, and the held-out portion is sealed.

---

### 02.5 Chunking & enrichment `[R]`

```yaml task
id: "02.5"
title: Chunking & enrichment
role: AI
depends_on: ["02.4", "02.9"]
estimate: {S: 3, M-L: 8}
artifact: chunking-strategy.md
optional_tag: R
sets_tags: []
```

**Plan** (`02.5-plan.md`): the **2–3 strategies** that will be compared, the metric used to compare them (the dev-set retrieval measure from 02.10), and the cost of building each one.

**Build**
- [ ] Pick a chunking strategy per document type: **structure-aware** (by section or heading) rather than fixed-size wherever possible
- [ ] Set chunk size and overlap, taking into account the embedding model's limits and the token budget from 02.8
- [ ] Keep context around each chunk: section path, parent document, neighboring chunks (for parent/child retrieval)
- [ ] Optionally add enrichment: a contextual header or summary per chunk, keywords, entities, questions the chunk answers
- [ ] **Compare the strategies on the dev eval set** instead of picking one by intuition
- [ ] Record the chosen strategy, the numbers behind it, and its build cost

**AI writes** `chunking-strategy.md`: the comparison table (strategy → recall@k / precision@k / cost / build time), the chosen strategy and why, and the repo path of the chunker.

**Review rules**
- At least two strategies were **measured** on the dev set. A single-strategy artifact fails this rule.
- The comparison names the eval-set version and the retrieval configuration used, so it can be reproduced.
- Chunk size and overlap are justified against the embedding model's limit and the 02.8 budget.
- Enrichment that costs tokens or money is justified by its measured gain.
- The **held-out set was not touched**.

**Done when** you approve the strategy record.

---

### 02.6 Indexing & retrieval `[R]`

```yaml task
id: "02.6"
title: Indexing & retrieval
role: AI
depends_on: ["02.5"]
estimate: {S: 4, M-L: 10}
artifact: retrieval-config.md
optional_tag: R
sets_tags: []
```

**Plan** (`02.6-plan.md`): the candidate embedding models and retrieval approaches, the index technology, the expected cost of embedding the corpus, and what it needs from you (a provider account, a spend approval, an index host).

**Build**
- [ ] Choose an embedding model on language/domain fit, dimensions, cost, and hosting constraints. **Pin its version**
- [ ] Choose a retrieval approach: lexical (BM25), vector, or **hybrid**, plus metadata filters (date, source, ACL)
- [ ] Decide on a reranker: add it only if the 02.10 tests show it pays for its latency and cost
- [ ] Set top-k and a score threshold. Define what happens when **nothing relevant** is found (the "I don't know" path)
- [ ] Enforce **ACL filtering at query time**, not after generation `[if ACLs apply]`
- [ ] Make the index build reproducible from the versioned processed data
- [ ] Plan re-indexing: incremental updates, deletions, and a full re-embed when the embedding model changes

**AI writes** `retrieval-config.md`: the pinned embedding model and index settings, the retrieval approach with the measured reason for it, top-k and threshold with the evidence, the ACL filter design, the rebuild and re-index procedure, and the embedding cost.

**Review rules**
- The embedding model ID is **pinned**, and the artifact says what a version change forces (a full re-embed).
- Top-k, the threshold, and the reranker decision each cite a **measurement**, not a default.
- ACL filtering happens **at query time**, and the artifact says how `[if ACLs apply]`.
- The index can be rebuilt from versioned data with one documented command.
- The "nothing relevant" path is defined and reachable.

**Done when** you approve the configuration record, and the index rebuilds from scratch.

---

### 02.7 Freshness & lifecycle `[R]`

```yaml task
id: "02.7"
title: Freshness & lifecycle
role: HUMAN
depends_on: ["02.6"]
estimate: {S: 2, M-L: 5}
artifact: freshness-policy.md
optional_tag: R
sets_tags: []
```

**AI prepares** (`02.7-prep.md`)
- A **draft staleness SLA per source**, proposed from the update frequencies in the source inventory, each marked as a proposal
- The **update mechanisms** available for each source (scheduled sync, change detection, event-driven), with their cost and lag
- The **deletion and revocation question list**: how a deleted document or a revoked entitlement reaches the index, and who must be asked
- A **pipeline ownership question**: who owns its health after launch (Phase 06 monitors it)

**You do**
- [ ] Agree the staleness SLA per source with its owner
- [ ] Choose the update mechanism per source
- [ ] Confirm how deletions and access revocations **propagate**
- [ ] Name the owner of the pipeline's health after launch
- [ ] Put your notes in `.genai/inbox/`

**AI turns into** `freshness-policy.md`: the SLA and mechanism per source, the deletion/revocation path, the index snapshot versioning scheme (so any answer traces to the index version that produced it), and the named owner.

**Review rules**
- Every in-scope source has an SLA **agreed with its owner**, not proposed by the AI.
- Deletions and access revocations have a propagation path, with a maximum lag.
- Index snapshots are versioned, and an answer can be traced back to one.
- The post-launch owner is a **named person or team**. "TBD" is a blocker for Phase 06.

**Done when** you approve the policy, and the owners have agreed their SLAs.

---

### 02.8 Context design & token budget

```yaml task
id: "02.8"
title: Context design & token budget
role: AI
depends_on: ["02.3", "02.6"]
estimate: {S: 3, M-L: 8}
artifact: context-design.md
optional_tag: null
sets_tags: []
```

**Plan** (`02.8-plan.md`): which components the context will have, how the token counts will be **measured** (tokenizer, sample inputs), and the target context window to check against.

**Build**
- [ ] List every **component of the context window**:
  - [ ] Instructions (only the slot is decided here; the wording is Phase 03's job)
  - [ ] User input
  - [ ] Retrieved chunks `[R]`
  - [ ] Structured data (records, API results)
  - [ ] Tool outputs
  - [ ] Conversation history / memory
- [ ] Set the **memory policy**: how much history to keep, when to summarize, and what persists across sessions (and whether that is allowed under 02.3)
- [ ] Shape tool outputs and structured data: keep only the fields the model needs, truncate, and use consistent formats
- [ ] Fix the **order** of components, and how sources are labeled so the model can cite them (provenance format)
- [ ] Mark **untrusted content** (retrieved docs, tool outputs, user input) so it is kept separate from instructions. This is a prompt-injection defense
- [ ] Set a **token budget** per component, measured on real samples. Check it against the target context window and the Phase 01 cost model
- [ ] Define **overflow behavior**: what gets dropped, summarized, or refused when the budget is exceeded

**AI writes** `context-design.md`: the context budget table (template below), the memory policy, the provenance format, the untrusted-content marking, and the cost per request at the expected volume.

**Review rules**
- Token counts are **measured with the real tokenizer** on real samples, and the p50/p95 are given, not just an average.
- The total fits the target context window with headroom, and the cost per task fits the Phase 01 cost model. If it doesn't, that is stated as a blocker, not smoothed over.
- Every untrusted component is marked as untrusted, and the mechanism is described.
- Overflow behavior is defined for every component, and it never silently drops the instructions.
- The memory policy complies with the 02.3 retention rules.

**Done when** you approve the context design and its budget.

---

### 02.10 Retrieval component tests `[R]`

```yaml task
id: "02.10"
title: Retrieval component tests
role: AI
depends_on: ["02.6", "02.9"]
estimate: {S: 3, M-L: 8}
artifact: retrieval-test-report.md
optional_tag: R
sets_tags: []
```

*CRISP-ML(Q): unit tests for data.*

**Plan** (`02.10-plan.md`): the metrics, the thresholds proposed for each (marked as proposals for you to agree), the test harness's repo location, and the CI wiring.

**Build**
- [ ] Measure retrieval on the **dev** set: recall@k, precision@k, MRR/nDCG
- [ ] Compare against a **lexical-only baseline**, a form of the Phase 01 heuristic benchmark
- [ ] Test the **"nothing relevant" path**: unanswerable questions must fall below the threshold
- [ ] Test for **ACL leakage**: restricted queries return no unauthorized chunks `[if ACLs apply]`
- [ ] Test **freshness**: an updated or deleted doc is reflected within the SLA
- [ ] Iterate on chunking and retrieval (02.5–02.6) until the thresholds are met, or record why they cannot be
- [ ] Add the tests to CI, so they run again whenever the pipeline, the chunking, or the embedding model changes

**AI writes** `retrieval-test-report.md`: the metric table with the run ids, the comparison against the lexical baseline, the result of each special test, the iterations made to 02.5/02.6 and their effect, and the CI job.

**Review rules**
- Every number names the **run, eval-set version, and configuration** that produced it.
- The lexical baseline was actually run. Hybrid or vector retrieval that doesn't beat it is reported as such.
- ACL leakage is **zero**, or the task cannot pass `[if ACLs apply]`.
- Unmet thresholds are reported with the reason and the options, never quietly lowered.
- The tests run in CI, and the artifact names the job.
- The **held-out set was not touched**.

**Done when** you approve the report, and the tests run in CI.

---

### 02.11 Phase gate → Phase 03

```yaml task
id: "02.11"
title: Phase gate → Phase 03
role: DECISION
depends_on: ["02.7", "02.8", "02.9", "02.10"]
estimate: {S: 1, M-L: 2}
artifact: null
optional_tag: null
sets_tags: []
```

**Brief** (`02.11-brief.md`)
- The **exit gate walk-through** below, item by item, citing artifacts
- Open data issues and known gaps, and how they limit the slice
- The **handoff to [Phase 03](03-model-selection-customization.md)**: context design, token budget, dev eval set, retrieval config `[R]`, and known failure modes
- Any change to the Phase 01 cost model that the measured budget forces

**Options**
- **Continue**: the gate passes, or its failures are accepted as known limits. Proceed to 03.0.
- **Continue with conditions**: name them and their owners.
- **Back to task X**: a gate item fails in a way Phase 02 must fix. Reset it with `--cascade`.
- **Back to Phase 01**: the data makes the chosen slice impossible (e.g. the knowledge doesn't exist). Reset 01.6 or 01.8 with `--cascade`.

End the brief with **AI recommendation:** `<option>`, followed by its reasoning.

**Decision record**: a `## 02.11` entry in `decisions.md`, with the accepted gaps, the conditions and their owners, and who signed off.

---

## Quality assurance

### Requirements & constraints

- The data meets the quality requirements in the data sheet, and the sources cover the eval set (or the gaps are recorded).
- Every chunk and context item can be traced to its source, version, and ACL.
- The pipeline and index can be rebuilt from versioned inputs.
- The data sent to the model provider and to logs complies with the sensitivity plan.
- The context fits the token budget, and its cost is within the Phase 01 cost model.
- Retrieval meets the agreed thresholds on the dev set `[R]`.
- The eval set is versioned, and its held-out split has not been used for tuning.

### Risks → QA measures

| Risk | QA measure | Task |
|------|------------|------|
| Error propagation from bad parsing (lost tables, garbled scans) | Parser tests on known hard samples + data unit tests | 02.2, 02.4 |
| Data inconsistency: conflicting or outdated versions | Authoritative source marked, version metadata, staleness SLA | 02.1, 02.2, 02.7 |
| Pipeline can't be reproduced | Idempotent pipeline, versioned data/config/index, pinned embedding model | 02.4, 02.6 |
| PII or secrets leak to the provider, logs, or answers | Sensitivity plan, redaction in the pipeline, PII data tests | 02.3, 02.4 |
| Retrieval returns content the user may not see | ACL metadata + query-time filtering + leakage tests | 02.3, 02.6, 02.10 |
| Relevant knowledge not retrieved (bad chunking/retrieval) | Strategy comparison + recall@k thresholds vs lexical baseline | 02.5, 02.6, 02.10 |
| Model answers when it should say "I don't know" | Score threshold + unanswerable eval items | 02.6, 02.9, 02.10 |
| Prompt injection through documents or tool outputs | Untrusted content marked and kept apart from instructions | 02.8 |
| Context overflow or cost blow-up | Token budget per component + overflow behavior | 02.8 |
| Stale answers after the source changes | Freshness SLA, deletion propagation, freshness test | 02.7, 02.10 |
| Eval set overfitted or unrepresentative | Real-sourced items, all case types, dev/held-out split, versioned | 02.9 |
| Embedding model change silently degrades retrieval | Pinned version, full re-embed plan, retrieval tests in CI | 02.6, 02.10 |
| Held-out set contaminated during tuning | Sealed split; 02.5/02.6/02.10 review rules forbid touching it | 02.9, 02.10 |

### Exit gate (walked in 02.11)

- [ ] The source inventory is complete, and pipeline access is granted.
- [ ] The data sheet records the profile, quality requirements and known gaps.
- [ ] The sensitivity & access-control plan is approved (by the security/compliance contact where needed).
- [ ] `[R]` The pipeline and index are reproducible, versioned and covered by data tests.
- [ ] `[R]` Retrieval meets its thresholds on the dev set, with no ACL leakage, and the freshness test passes.
- [ ] The context design and token budget are documented and fit the cost model.
- [ ] The eval set is versioned and split into dev and held-out, with every case type covered.
- [ ] The handoff to Phase 03 is recorded in the 02.11 decision entry.

---

## Templates

### Source inventory

| Source | Owner | System / access | Format | Volume | Update freq. | Sensitivity | Authoritative? | In slice? |
|--------|-------|-----------------|--------|--------|--------------|-------------|----------------|-----------|
| | | | | | | | | |

### Data sheet

```text
Source:
Sample size / method:
Profile:            (count, length distribution, formats, languages, structure)
Quality findings:   (duplicates, conflicts, parse issues, missing metadata)
Coverage gaps:      (eval questions not answerable from sources)
Generation process: (who writes it, how it changes)
Quality requirements:
Run:                (script, date, version)
```

### Context budget

| Component | Source | Trusted? | Order | Max tokens | Overflow behavior |
|-----------|--------|----------|-------|------------|-------------------|
| Instructions | Phase 03 | yes | 1 | | never dropped |
| User input | user | no | | | |
| Retrieved chunks `[R]` | index | no | | | drop lowest score |
| History / memory | session | no | | | summarize oldest |
| Tool outputs | tools | no | | | truncate fields |
| **Total vs window** | | | | | |

### Eval item

```text
id:               
input:            
expected:         (answer or rubric)
relevant_sources: (doc/chunk ids)            [R]
case_type:        normal | edge | failure | forbidden | unanswerable | access-restricted
split:            dev | held-out
labeled_by / date:
```
