---
name: plan
description: Write or refine one component's detailed spec at .specify/specs/<component>.md -- Purpose, Interface, Dependencies (version-pinned), Data touched, Behavior & edge cases, Errors, Out of scope, Acceptance criteria. With no argument, picks the first "Not started" component from the index; with an argument, plans that one. Interviews only what genuinely needs deciding, raises [!UNCLEAR] rather than guessing, checks the draft against every constitution principle before writing, then self-reviews against a quality checklist. Versioned and gated by sdd.py. Use for "plan X", "spec out X", "what's next to plan".
argument-hint: "[component name or C-NNN id]"
---

# Plan

Third stage: `constitution` → `specify` → **`plan`** → `implement`.

Turns one row of the component index into a full, implementable spec. This is
where a component's interface, behavior and edge cases actually get decided — the
step between "we know this needs to exist" and "we're building it".

It writes no code, and never specs a component other than the one it is targeting.

**The Acceptance Criteria section is the output that matters most.** Everything
else describes the component; that section is what `implement` turns into failing
tests before any code exists. A vague criterion there produces a vague test, which
produces an implementation that passes without being correct. Treat it as the
deliverable, not the closing formality.

---

## Step 0 — Bootstrap the toolkit

```bash
test -f .specify/toolkit/sdd.py && echo vendored || \
for c in ~/.agents/sdd/sdd.py ~/.claude/sdd/sdd.py; do \
  [ -f "$c" ] && python3 "$c" init . && break; done
python3 .specify/toolkit/sdd.py check
```

If no candidate path resolves, stop and say so. Read
`.specify/toolkit/UNCLEAR-PROTOCOL.md` and `ARTIFACT-CONTRACT.md` — binding here.

If `check` reports errors, **fix them before planning anything**. Planning on top
of an index that already disagrees with its specs produces a spec that inherits
the inconsistency.

## Step 1 — Resolve the target component

```bash
python3 .specify/toolkit/sdd.py index
```

- **With an argument**: match it against `C-NNN` ids and component names,
  case-insensitively, substring allowed ("router" matches "LLM Router"). If it
  matches more than one row or none, **ask** — never guess. Planning the wrong
  component wastes an entire interview.
- **With no argument**: take the first row whose status is `Not started`, in index
  order. That order is the build order `specify` established.
- **If that component's Notes name a dependency that is itself `Not started`**:
  say so and recommend planning the dependency first. Its interface is the contract
  this spec has to be written against, and inventing it here means writing the same
  spec twice.
- **If the index doesn't exist**: stop. There is nothing to plan against — run
  `specify` first.
- **If a spec already exists for it** (`Draft`, `Ready`, or `Implemented`): this is
  a refinement, not a fresh write. Read the existing file in full and preserve
  everything not being changed. For an `Implemented` one, be explicit: changing the
  spec of built code means the code is now out of date, and say so.

## Step 2 — Load context

Read, in this order, everything that exists:

1. **`.specify/memory/constitution.md`** — the gates. Note every NON-NEGOTIABLE
   principle and its `Gate:` line specifically; Step 5 checks against them.
2. **`.specify/specs/requirements.md`** — the `CAP` this component serves and the
   `AD` rows that constrain it. Cite them by id in the spec rather than restating
   them; a restated decision is a decision that can drift.
3. **`.specify/specs/README.md`** — the target's Notes cell, and the status of
   everything it depends on or that depends on it.
4. **The spec of every component this one depends on** — its `## Interface` section
   is the actual contract. Record the version you read in the pin (`@1.2.0`); that
   pin is what lets `sdd.py check` tell you later that the dependency moved.
5. **If a dependency is already `Implemented`, read its code too.** A spec can drift
   from what got built. Where they disagree, the code is truth and the drift is a
   finding worth reporting.

If a needed dependency is still `Not started`, do **not** invent its interface.
Either plan it first (recommended, per Step 1) or raise an `[!UNCLEAR]` blocking
the sections that depend on it.

## Step 3 — Identify what actually needs deciding

Most of a spec is derivable from Step 2. Purpose follows from the Notes cell and
the `CAP`. Dependencies are whatever interfaces it must call. Types often follow
sibling components already spec'd. **Draft all of that directly — do not interview
the user about things already determined.** An interview that asks what the
documents already answer teaches the user that this stage doesn't read them.

What genuinely needs a decision is a small number of things, typically 2–5:

- **Interface choices with a real tradeoff** — sync vs. async; what the caller
  passes vs. what is inferred; one call vs. split into steps; batch vs. single.
- **Behavior under failure** — what retries and how many times, what surfaces
  immediately, what the caller is responsible for vs. what this component owns.
- **Division of responsibility with a neighbouring component** — who computes vs.
  who persists, who validates vs. who acts. This is consistently the most
  load-bearing decision in a component spec and the one most often skipped, because
  both answers look reasonable in isolation and only conflict later.
- **Scope boundaries** — what is explicitly out, especially a natural extension
  that isn't needed yet.
- **Concurrency and idempotency** — can two calls overlap, and what happens if the
  same call arrives twice.
- **Thresholds and limits** with no defensible default — timeouts, page sizes,
  retry counts, token budgets.

Ask about exactly these. `AskUserQuestion` where there are 2–4 concrete options
with a real tradeoff each; plain text where the answer needs the user's own words.
Don't walk a generic checklist of every section the template has.

**When a decision is deferred rather than made**, raise an `[!UNCLEAR]` per
`UNCLEAR-PROTOCOL.md` — scoped to the sections it actually blocks, with the options
you offered. Do not pick the option you'd have recommended and write it as settled.
A spec carrying an honest blocking marker is strictly more useful than one carrying
an invented answer, because the marker stops `implement` and the invention doesn't.

## Step 4 — Draft

Use **`SPEC-TEMPLATE.md`** (next to this SKILL.md). Follow its header block and
section names exactly — `sdd.py` parses `## Dependencies` and the header fields.

Include component-specific sections beyond the core ones where the interview
actually decided something that needs them — a resolution algorithm, a state
machine, a config shape, a retry ladder. Not every spec needs the same sections.

## Step 5 — Constitution check

Before writing anything to disk, check the draft against every principle, using its
`Gate:` line as the test. Record the result as a table in the spec itself (the
template has the section), so `implement` can see what was checked rather than
assuming it was.

Concretely, for the common principles:

- Are the Acceptance Criteria specific enough to write a **failing test** from,
  before any implementation exists? (Test-First)
- Does the Interface avoid surface not required by the Purpose or by a cited `CAP`?
  (Simplicity/YAGNI)
- Does anything here put a secret, token, or credential somewhere it could be
  logged, persisted, or included in an error message? (Security)
- Does this introduce a runtime dependency, and is the justification written down?
  (Minimal Dependencies)
- For ML/LLM components: is the eval set named, and the threshold a number?
  (Evaluation Rigor)

**If the draft conflicts with a NON-NEGOTIABLE principle, do not quietly adjust it
and move on.** Surface the conflict to the user explicitly and resolve it before
writing. A constitution conflict is the highest-severity finding this pipeline
has — it means either the design is wrong or the constitution is, and only the user
can say which.

A departure from a non-NON-NEGOTIABLE principle is allowed, and must be recorded in
the spec's `Complexity / deviations` row with what was considered instead.

## Step 6 — Self-review

Walk **`SPEC-QUALITY-CHECKLIST.md`** (next to this SKILL.md) against the draft.
For each failing item, quote the offending section, fix it, and re-check. Up to
three passes; anything still failing after three is reported to the user rather
than quietly shipped.

This step catches, reliably, the two things that otherwise reach `implement`:
acceptance criteria that can't be turned into a test, and an interface that
describes intent rather than shape.

## Step 7 — Write, version, update the index

```bash
# new spec
python3 .specify/toolkit/sdd.py bump .specify/specs/<slug>.md \
  --level minor --summary "initial draft" --stale none
python3 .specify/toolkit/sdd.py status "<Component>" Draft

# promoting a complete, marker-free spec
python3 .specify/toolkit/sdd.py status "<Component>" Ready
```

- Filename is kebab-case of the component name (`LLM Router` → `llm-router.md`),
  flat in `specs/`.
- `sdd.py status` writes the index row and the spec header together and **refuses**
  to promote to `Ready` while blocking markers remain. That refusal is the feature.
- A spec with blocking `[!UNCLEAR]` markers stays `Draft`. Say so in the report.
- On a **refinement** of an existing spec, pick the level honestly: MAJOR if an
  interface signature changed or a behavior already built against is now different,
  and `--stale` must then name every spec that pins this one.

## Step 8 — Verify, then report

```bash
python3 .specify/toolkit/sdd.py check
python3 .specify/toolkit/sdd.py gate "<Component>"
```

**Not done until `check` exits 0.** `gate` is expected to fail if markers remain —
that is the correct state for a `Draft` with open questions, and the report should
say so plainly rather than hiding it.

Report:

- The component's purpose in one or two sentences.
- Each decision made in Step 3, the options, and why this one.
- The constitution check result, including any deviation recorded and its
  justification.
- Every `[!UNCLEAR]` raised, in `UNCLEAR-PROTOCOL.md`'s shape — question, options,
  recommendation — so the user can close them by replying.
- Any drift found between a dependency's spec and its actual code.
- Checklist items still failing after three passes.
- **Next Actions**: any unmet dependency; that the spec is `Draft` and moves to
  `Ready` once markers are closed; and that `implement` starts from the Acceptance
  Criteria, not from the Interface.

## Failure modes this stage must not produce

| Failure | What it looks like | Required behaviour |
|---|---|---|
| Invented dependency interface | A `Not started` dependency's API written as though it were decided. | Plan the dependency first, or raise a blocking `[!UNCLEAR]`. Never invent. |
| Untestable acceptance criteria | "Handles errors gracefully." | Every criterion is given/when/then with a concrete input and a checkable outcome. Step 6 catches these; don't ship past it. |
| Prose interface | "The component exposes a method to fetch documents." | Actual signatures — names, parameter types, return types, exception types. |
| Silent constitution violation | Draft conflicts with a NON-NEGOTIABLE, spec is adjusted and nobody is told. | Surface it; resolve it with the user before writing. |
| Guessed deferral | A decision the user deferred, written as settled. | `[!UNCLEAR]`, scoped to what it blocks. |
| Unpinned dependency | `## Dependencies` names a component with no `@version`. | Always pin. The pin is what makes drift detectable later. |
| Speculative interface | Methods "we'll probably need". | Every method traces to the Purpose or a cited `CAP`. If it doesn't, it goes in `Out of scope`. |
| Restated decisions | An `AD` copied into the spec and then edited. | Cite `AD-NNN`. One source of truth per decision. |
| Refinement by regeneration | An existing spec rewritten, losing sections nobody asked to change. | Read it fully; amend in place; diff before writing. |
| Planning two components | "While I was in there I also spec'd its dependency." | One component per invocation. Name the others in Next Actions. |
| Hand-edited index | Status or Version cell changed with an editor. | `sdd.py status` / `sdd.py bump`, always. |
| Reporting success over a failing check | "Done!" while `check` exits 1. | Run it; fix; run it again. |
