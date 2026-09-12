---
name: implement
description: Implement one component whose index status is Draft or Ready. Runs sdd.py gate first -- refusing to build anything carrying a blocking [!UNCLEAR] marker, or whose dependencies aren't Implemented yet -- then writes failing tests from the spec's Acceptance Criteria before any implementation exists (if the constitution mandates Test-First), runs the constitution's quality and security gates, records what was built in the spec, moves the status to Implemented, and applies the spec's deferred doc updates. With no argument, picks the first Draft/Ready component in index order. Use for "implement X", "build X", "what's ready to implement".
argument-hint: "[component name or C-NNN id]"
---

# Implement

Last stage: `constitution` → `specify` → `plan` → **`implement`**.

Turns one `Draft`/`Ready` component spec into working code. Everything before this
was deciding what to build and why; this is the only stage that writes code.

**One component per invocation**, even when several are eligible — the pipeline is
incremental on purpose: what building one component surfaces is meant to inform
the next one's spec. Other eligible components are named in the final report, not
built in the same pass.

---

## Step 0 — Bootstrap the toolkit

```bash
test -f .specify/toolkit/sdd.py && echo vendored || \
for c in ~/.agents/sdd/sdd.py ~/.claude/sdd/sdd.py; do \
  [ -f "$c" ] && python3 "$c" init . && break; done
python3 .specify/toolkit/sdd.py index
```

If no candidate path resolves, stop and say so. Do not implement with the gate
switched off — the gate is the only thing standing between an `[!UNCLEAR]` marker
and code that silently encodes a guess as a decision.

Read `.specify/toolkit/UNCLEAR-PROTOCOL.md` and `ARTIFACT-CONTRACT.md`.

## Step 1 — Resolve the target component

- **With an argument**: match against `C-NNN` ids and component names,
  case-insensitively. If it doesn't resolve to exactly one row, ask.
  - Status `Not started` → there is no spec. Say so, suggest `plan`. **Do not
    improvise one** — a spec written by the stage that implements it is not a
    spec, it is a description of whatever got written.
  - Status `Implemented` → confirm with the user that this is a deliberate
    re-implementation (the spec changed) before touching anything.
- **With no argument**: take the first `Draft` or `Ready` row in index order.
- **Nothing eligible, or no index**: say so; suggest `plan`.

## Step 2 — Run the gate. This is not optional.

```bash
python3 .specify/toolkit/sdd.py gate "<Component>"
```

The gate checks, in one command, every precondition this stage has:

| Check | Why it blocks |
|---|---|
| A spec exists | Nothing to build against. |
| Status is `Draft`/`Ready` | Nothing to build, or already built. |
| No blocking `[!UNCLEAR]` in the spec | **Nothing unclear gets implemented.** Building past a marker means encoding a guess as a decision, in code, where it is hardest to find later. |
| No blocking `[!UNCLEAR]` in `constitution.md` or `requirements.md` | An unsettled principle or capability is upstream of every component. |
| Every dependency is `Implemented` | A dependency that exists only as a spec has no real interface to build against. |
| Dependency pins are not a MAJOR behind | The dependency's interface changed incompatibly since this spec was written. |
| `sdd.py check` is clean | The artifacts disagree with each other; fix that first. |

**If the gate fails, stop.** Report exactly which check failed and what closes it:

- Blocking markers → list each one with its question, options, and your
  recommendation, in `UNCLEAR-PROTOCOL.md`'s shape. The user can answer inline;
  then `plan` resolves the marker and bumps the spec, and this stage runs again.
- Unimplemented dependency → name it and suggest `plan`/`implement` on it first.
  **Never stub an invented interface and carry on.**
- Stale pin → the dependency must be re-read and this spec re-pinned by `plan`.

Do not re-run the gate with a workaround. Do not use `--force` on `sdd.py status`
to get past it. The gate failing is the pipeline working.

## Step 3 — Load context

1. **`.specify/memory/constitution.md`** — every NON-NEGOTIABLE principle is a hard
   gate, and its `Gate:` line is the literal test. If there is no constitution,
   proceed but say so in the report, and say which defaults you applied instead.
2. **The target's spec** — the contract. Read all of it, including the Constitution
   check table (so you know what `plan` already verified) and the Clarifications log
   (so you know which decisions were deliberate and why).
3. **`.specify/specs/requirements.md`** — the `CAP` this serves, for edge cases the
   spec didn't spell out.
4. **Every dependency's actual code** — not just its spec. A spec can drift from
   what got built, and **the code is truth**. Where they disagree, build against the
   code and report the drift; it is a finding for `plan`, not something to fix
   silently here.
5. **A sibling already-implemented component** — for this repo's real conventions:
   test layout, fixture style, error handling, logging, package structure. Match
   what exists rather than importing habits from elsewhere.

## Step 4 — Resolve residual ambiguity before writing anything

`plan` settles the design; some gaps still only become visible with the code in
front of you. Two kinds, handled differently:

- **No behavioral consequence** — which stdlib helper performs a step the spec
  already decided on, a variable name, file placement. Make the obvious choice
  consistent with the codebase. Note it in a comment only if it's non-obvious.
  Do not interrupt the user for this.
- **Materially affects behavior, contradicts another part of the spec, expands
  scope, or requires a design decision the spec didn't make** — **stop and ask**,
  with `AskUserQuestion` where there are concrete options. This is the entire point
  of the step: implementation must not quietly re-decide what specification was
  supposed to settle.

Also surface, rather than silently resolving, any edge case the Acceptance Criteria
don't cover but that the tests will need anyway — an obvious failure path visible
from the code but absent from the spec. Confirm the expected behavior with the user
before encoding it as a test, and note in the report that the spec should gain a
criterion for it.

If the answer is deferred rather than given: that is a new `[!UNCLEAR]` in the spec,
raised via `plan`, and this stage stops. It does not become a TODO comment in code.

## Step 5 — Implement, Test-First if the constitution requires it

If the constitution has a Test-First (or equivalent) NON-NEGOTIABLE principle,
follow this order exactly. The sequencing *is* the principle:

1. **Write the tests** from the Acceptance Criteria — one test per `AC-NNN` where
   natural, grouped where that reads better, each naming the criterion it covers.
   Add the edge cases confirmed in Step 4. Use this repo's existing test
   conventions (fixtures, fake/mock style, directory layout) from the sibling
   component read in Step 3.
2. **Run them. Confirm they fail, and fail for the right reason** — missing
   implementation, not a typo, a bad import, or a fixture error. A test that passes
   with no implementation is a broken test, and a test that fails for the wrong
   reason proves nothing. Fix those before continuing, and **keep the failure
   output** — it goes in the report as evidence the red phase actually happened.
3. **Now write the implementation**, against the Interface and Behavior sections,
   until the tests pass. Nothing beyond what the spec calls for.
4. **Refactor with the tests green throughout.**

If no constitution is loaded, or it has no such principle: still write tests from
the Acceptance Criteria, without the strict red-before-green requirement — and say
in the report that this was a default you applied, not a rule anything mandated.

Build only the scaffolding this component actually needs to exist — a new service's
manifest, `src/`, `tests/`, following the repo's existing package layout, if this is
the first component in that service. Not the service's eventual shape speculatively.

## Step 6 — Quality and security gates

Run what the constitution's `Gate:` lines name. Treat a NON-NEGOTIABLE gate as
blocking and a strong-default gate as worth doing unless there's a stated reason not
to. At minimum:

- Lint and format clean (this repo's tooling — check a sibling component for the
  exact commands, don't guess).
- Type checks pass, if the repo has them.
- Full test suite passes, not just the new tests. A green new test beside a broken
  neighbour is not done.
- **No secret, token, credential, or PII value is logged, printed, included in an
  exception message, or persisted in plaintext** anywhere in the new code. Read
  every new logging and error path for this specifically — it is the one gate that
  cannot be caught by running something.
- Every new runtime dependency is justified in the report: what it replaces, what
  was considered instead. Do this even if the constitution doesn't demand it.

If a gate fails and you cannot fix it, **report it as failing**. Do not report
completion over a failing gate, and do not weaken a test to make one pass.

## Step 7 — Record, version, update status

1. **Append the Implementation record** to the spec, using
   **`IMPLEMENTATION-RECORD-TEMPLATE.md`** (next to this SKILL.md). This is the
   audit trail: what was built where, the red-green evidence, every deviation from
   the spec and why.
2. **Apply the spec's `Related doc updates once implemented` section now.** This is
   exactly the moment those deferred fixes were waiting for; skipping it is how a
   README ends up describing a system that hasn't existed for three components.
3. **Bump and promote:**

   ```bash
   python3 .specify/toolkit/sdd.py bump .specify/specs/<slug>.md \
     --level minor --summary "implemented; record added; retry ladder widened to 3 attempts" \
     --stale none
   python3 .specify/toolkit/sdd.py status "<Component>" Implemented
   ```

   If implementation surfaced a genuine interface change from what the spec said,
   that is a **MAJOR** bump, and `--stale` must name every spec that pins this one.
   Update the Interface section to match what was actually built — a spec that
   disagrees with shipped code is worse than no spec, because the next component
   will be written against the fiction.

4. Update the index Notes cell to point at where the code actually lives.

## Step 8 — Verify, then report

```bash
python3 .specify/toolkit/sdd.py check
python3 .specify/toolkit/sdd.py index
```

**Not done until `check` exits 0.**

Report:

- What was built and where — files, entry points.
- Test results, with the **red-phase output** quoted if Test-First applied, and
  confirmation the sequence was actually followed.
- Every ambiguity resolved in Step 4, and how.
- Every quality and security gate, and its result. Failures stated as failures.
- Every deviation from the spec, and why — plus whether it needed a version bump.
- Any drift found between a dependency's spec and its code.
- New runtime dependencies, with justification.
- Deferred doc updates applied.
- **Next Actions**: other `Draft`/`Ready` components still waiting; anything now
  unblocked by this one landing; any spec that should gain an acceptance criterion
  for an edge case this pass surfaced.

## Failure modes this stage must not produce

| Failure | What it looks like | Required behaviour |
|---|---|---|
| Building past a blocking marker | Gate fails, a plausible answer gets chosen, code ships encoding a guess. | Stop. Report the marker with options. The gate failing is the pipeline working. |
| Stubbing an unbuilt dependency | An invented interface for a `Draft` dependency, "to be replaced later". | Stop. Implement the dependency first. |
| Test-after dressed as test-first | Tests written from the finished implementation. | Write tests first, run them, keep the failure output, put it in the report. |
| Tests failing for the wrong reason | Red phase is an import error, counted as a pass of step 2. | Read the failure. It must be "no implementation", not "no module". |
| Weakening a test to go green | An assertion loosened until it passes. | Fix the code, or report the failure. Never the test. |
| Silent spec drift | Built interface differs from the spec; the spec is left alone. | Update the Interface, bump MAJOR, mark dependants stale. |
| Implementing two components | "It was small, so I did its dependency too." | One per invocation. Name the rest in Next Actions. |
| Scope expansion | Methods, config, or abstraction the spec didn't ask for. | Build the spec. Extra ideas go in Next Actions. |
| Secrets in logs or errors | A token in an exception message or a DEBUG line. | Read every new logging and error path before reporting done. |
| Skipping the deferred doc updates | Step 7.2 quietly dropped. | Apply them, and list them in the report. |
| Green new test, red suite | Only the new tests were run. | Run the whole suite. |
| Reporting success over a failing gate | "Done!" while lint, types, tests, or `check` fail. | Report the failure plainly, with the output. |
