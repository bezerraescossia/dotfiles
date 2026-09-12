---
name: specify
description: Interview the user about a product's business need, translate it into LLM/agentic/ML capabilities, derive the architecture decisions that support them, and write .specify/specs/requirements.md (business context, capability table, architecture decision log) plus .specify/specs/README.md (the component index that becomes the pipeline's work queue). Carries no fixed tech stack or business assumptions -- always interviews fresh. Raises [!UNCLEAR] markers rather than guessing at deferred decisions. Versioned; amendments bump semver and record what they invalidated. Use when starting a new product, or when an existing one's business requirements have materially changed.
argument-hint: "[optional: the product or the change to fold in]"
---

# Specify

Second stage: `constitution` → **`specify`** → `plan` → `implement`.

Produces two artifacts in `.specify/specs/`:

- **`requirements.md`** — business context, the capabilities it translates to
  (`CAP-NNN`), and the architecture decisions that support them (`AD-NNN`), each
  with its rationale. A decision log scoped to one product.
- **`README.md`** — the component index: every component implied by those
  decisions, with a stable `C-NNN` id and a status. This is the work queue `plan`
  and `implement` consume.

It does **not** write individual component specs (that is `plan`, one at a time)
and writes no code.

**It carries no assumptions about what any project's business need or tech stack
should be — including this one's.** Do not reuse a stack, a capability list, or a
component breakdown from earlier context about a *different* product. Interview
fresh every time. This is not a style preference: a carried-over stack is an
architecture decision made for the wrong product, and it will be cited as settled
by every downstream stage.

---

## Step 0 — Bootstrap the toolkit

```bash
test -f .specify/toolkit/sdd.py && echo vendored || \
for c in ~/.agents/sdd/sdd.py ~/.claude/sdd/sdd.py; do \
  [ -f "$c" ] && python3 "$c" init . && break; done
python3 .specify/toolkit/sdd.py doctor
```

If no candidate path resolves, stop and say so. Then read
`.specify/toolkit/UNCLEAR-PROTOCOL.md`, `ARTIFACT-CONTRACT.md` and `LAYOUT.md` —
binding on this stage.

## Step 1 — Load state and pick the mode

```bash
python3 .specify/toolkit/sdd.py doctor
python3 .specify/toolkit/sdd.py index      # if an index already exists
```

- **Neither artifact exists** → first pass for this product.
- **Both exist** → **amendment**. Read both in full, including their Sync Impact
  Reports. Preserve every `CAP`/`AD`/component the user isn't asking to change.
  Add what's new. Where something existing now contradicts a newly stated
  requirement, **flag it — never silently delete it**: a component removed from
  the index whose code already exists becomes untracked code, which is worse than
  a component marked as superseded.
- **One exists without the other** → inconsistent state. Say so and reconstruct
  the missing one from the one that exists plus the interview, rather than
  starting over.

Also load `.specify/memory/constitution.md`. It constrains Step 4 directly — a
principle mandating a testing discipline, a language, or a data-handling rule is
an architecture decision already made, and must be recorded as such rather than
re-asked. If there is no constitution, proceed, but say so in the report and
recommend running `constitution` — a later constitution can invalidate decisions
made here.

## Step 2 — Scope guard

This stage produces `requirements.md` and `README.md`. Nothing else.

If the interview surfaces a request to write a component spec, generate code, or
make a one-off implementation decision unrelated to architecture, **don't**. Record
it under `Next Actions` and let `plan` or `implement` own it. Scope creep here is
expensive in a specific way: a design decision made during a business interview
gets recorded with business-level rationale, and nobody later can tell it was
never actually designed.

Spec granularity — component-level, one spec per cohesive unit — is a fixed
convention of this pipeline, not something to re-interview. If the constitution
says otherwise, the constitution wins.

## Step 3 — Interview

Go in rounds. `AskUserQuestion` for concrete choices (batch up to 4 per call, each
option carrying a real one-line tradeoff); plain text for anything needing the
user's own words. Skip anything an existing `requirements.md` already answers.

**Round A — Business & product context** (open-ended, no options):
- What problem does this solve, and for whom — internal team, external customers,
  developers consuming an API?
- What does success look like, concretely enough to measure?
- Hard constraints already fixed: must integrate with X, must comply with Y,
  budget, timeline, team size, existing systems it cannot break?
- What is explicitly **not** in this first milestone?

**Round B — Capability shape.** This is the actual business→system translation.
Each answer maps onto a `CAP-NNN` row that later becomes components.
- Conversational (multi-turn) or one-shot/batch?
- Does it need to *take actions* — call tools/APIs, run a multi-step agentic loop
  — or only produce a response?
- Does it need to retrieve from a knowledge base or private documents (RAG)?
- Structured output (routing, classification, extraction) vs. free-form generation?
- Human-in-the-loop approval before any action executes?
- Real-time (a user is waiting) or background?
- Persistent memory across sessions, or is each interaction independent?
- Traffic shape: steady, bursty, occasional batch? Rough volume?
- What happens when the model is wrong — who notices, and what does it cost?

**Round C — Data, safety & compliance:**
- What data sources and types are involved — documents, databases, uploads,
  third-party APIs?
- Sensitive or regulated data (PII, health, financial)? Domain-specific moderation
  or disclaimer obligations?
- Audit or compliance logging beyond general observability?
- What must never leave the environment or reach a third-party API?

**Round D — Architecture decisions.** Fully re-derived per product. Ask only what
Rounds A–C made relevant — skip vector-store questions if there's no RAG, skip
streaming transport if nothing is real-time, skip job queues if everything is
synchronous. Every question you skip, say you skipped and why; a decision that was
never asked about must not appear in the log as though it were made.

The areas, their options, and the tradeoffs to state are in **`ARCHITECTURE-DECISIONS.md`**
(next to this SKILL.md). Read it before this round.

Where the constitution already constrains a decision, say so and record it as an
`AD` sourced to the constitution instead of asking.

### Handling deferral

When the user says "not sure yet", "we'll decide later", or "depends on something
we don't know" — that is an `[!UNCLEAR]` marker, not a prompt to pick a sensible
default. Per `UNCLEAR-PROTOCOL.md`:

- Scope `**Blocks**` honestly. A deferred decision about a Phase 2 capability blocks
  nothing today: `**Blocks**: none`. A deferred decision about the primary datastore
  blocks every component that touches persistence — name them.
- A blocking marker in `requirements.md` blocks **every** component downstream. If
  you're about to write one, say so in the round, so the user can decide whether
  answering now is cheaper than stalling the pipeline.

## Step 4 — Translate and decompose

Map each Round B capability onto concrete components:

| Capability | Typically becomes |
|---|---|
| Retrieval over private documents | ingestion/embedding component + retrieval component + a retrieval-aware endpoint |
| Agentic tool use | orchestration/loop component + one component per external tool integration + a tool-result validator |
| Structured extraction/classification | schema definition + a constrained-decoding or validation component |
| Human-in-the-loop approval | an approval queue/state machine + a notification path + an audit record |
| Background/async work | a queue + a worker + a job-status surface |
| Persistent memory | a conversation store + a retrieval/summarization policy component |

Plus the foundational components implied by the Round D decisions — typically
config, an LLM provider abstraction (only if multi-provider), data access, auth,
logging/observability, guardrails. Add a foundational component only if a Round D
decision actually requires it. A provider abstraction over a single provider is
speculative surface; if the constitution has a simplicity principle, it is also a
violation.

**Ordering is load-bearing.** The index's row order is the build order `plan` and
`implement` follow with no argument. Put foundational and shared components first,
then services, each after everything it depends on. If two components genuinely
depend on each other, that is a decomposition error — split the shared part out
rather than recording a cycle.

Give every component a `C-NNN` id, assigned in index order, never reused. On an
amendment, new components continue from the highest existing id — never renumber.

## Step 5 — Write

Use **`REQUIREMENTS-TEMPLATE.md`** and **`INDEX-TEMPLATE.md`** (next to this
SKILL.md). Follow them exactly; they carry the id schemes and required columns
that `sdd.py` parses.

## Step 6 — Version

```bash
python3 .specify/toolkit/sdd.py bump .specify/specs/requirements.md \
  --level minor --summary "added CAP-004 (batch re-scoring); AD-003 now Postgres+pgvector" \
  --stale "README.md,llm-router.md"
python3 .specify/toolkit/sdd.py bump .specify/specs/README.md \
  --level minor --summary "added C-009 Batch Scorer" --stale none
```

Levels per `ARTIFACT-CONTRACT.md`:

- **MAJOR** — a capability dropped, or an architecture decision reversed. Anything
  already specified or built against it may now be wrong.
- **MINOR** — a capability or component added; an `[!UNCLEAR]` resolved.
- **PATCH** — wording, rationale, formatting.

On a reversed `AD`, `--stale` must name **every** component spec derived from it,
`Implemented` ones included.

## Step 7 — Verify, then report

```bash
python3 .specify/toolkit/sdd.py check
python3 .specify/toolkit/sdd.py index
```

**Not done until `check` exits 0.** Then report:

- One paragraph: the business need and the capability shape it implies.
- The architecture decisions and why — including which areas you skipped and why.
- The component list in build order, with dependencies noted.
- Every `[!UNCLEAR]` raised, in `UNCLEAR-PROTOCOL.md`'s shape, with options and a
  recommendation.
- Anything deferred by the Step 2 scope guard.
- Whether a constitution exists; recommend `constitution` if not.
- **Next**: `plan` writes the first component's spec — name which one it will pick.

## Failure modes this stage must not produce

| Failure | What it looks like | Required behaviour |
|---|---|---|
| Carried-over stack | Components or decisions from a different product appear as settled. | Re-derive Round D every time. If a decision came from context rather than this interview, it is not a decision — ask. |
| Silent component deletion | Amendment drops a component; its code becomes untracked. | Flag the inconsistency, keep the row, let the user decide. |
| Renumbered ids | `C-003` means something different than it did last week. | Ids are permanent. New components continue from the highest. Removed ones stay retired. |
| Guessed deferral | "Not sure yet" becomes a plausible default recorded as a decision. | `[!UNCLEAR]`, scoped honestly, surfaced in the report. |
| Speculative components | A provider abstraction over one provider; a queue for synchronous work. | Every component traces to a `CAP` or an `AD`. No trace, no component. |
| Unasked decisions recorded | An `AD` for an area the interview skipped. | Record only what was asked and answered. Say what you skipped. |
| Dependency cycle in the index | Two components list each other. | Split the shared part into a third component. |
| Business interview turns into design | Interface-level decisions recorded with business rationale. | Scope guard. Defer to `plan`. |
| Unversioned amendment | Files edited, header untouched. | Always `sdd.py bump`. |
| Reporting success over a failing check | "Done!" while `check` exits 1. | Run it; fix; run it again. |
