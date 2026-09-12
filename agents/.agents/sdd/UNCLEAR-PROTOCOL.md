# The `[!UNCLEAR]` protocol

**Version**: 1.0.0

One rule sits above everything else in this pipeline:

> **Nothing marked `[!UNCLEAR]` gets implemented.**

A product under development always carries decisions that are provisional, deferred,
or simply not yet made. The failure mode this protocol exists to prevent is the
quiet one: an agent meets an undecided point, picks something plausible, writes it
down as though it were settled, and three artifacts later nobody can tell which
lines were decided and which were invented. `[!UNCLEAR]` makes that distinction
survive in the file itself, and `sdd.py` makes it mechanically enforceable.

## Grammar

### Block form — the declaration

Every open question is declared exactly once, as a blockquote, in the artifact
whose content it affects:

```markdown
> [!UNCLEAR] U-007 — Does the router retry, or does the caller own retries?
> **Blocks**: Interface, Behavior & edge cases
> **Options**: A) router retries with backoff  B) caller owns retry, router is one-shot
> **Raised**: 2026-09-12 (plan)
```

| Part | Rule |
|---|---|
| `U-NNN` | Zero-padded, unique **within its file**. Never renumber a marker — ids appear in Clarifications logs and Sync Impact Reports after resolution. |
| Question | One line, on the marker line itself. A question someone could actually answer — not "TBD". |
| `**Blocks**` | **Required.** What cannot be built while this is open. `none` means informational. Anything else makes the marker *blocking*. |
| `**Options**` | Optional but strongly preferred — a marker with concrete options is one the user can close in a single reply. |
| `**Raised**` | ISO date and the stage that raised it. |

### Inline form — the reference

Where the undecided thing would otherwise be written as fact, reference the block
instead of inventing a value:

```markdown
| Retry policy | [!UNCLEAR:U-007] |
```

Every inline reference must have a matching block in the same file; a block may
stand alone with no inline reference.

## Blocking vs. informational

`**Blocks**: none` is for a question whose answer changes nothing that is being
built now — a future extension, a pricing question, a decision the user has
explicitly deferred past this milestone. It is recorded so it isn't forgotten, and
it gates nothing.

Anything else is **blocking**, and blocking means exactly this:

- The artifact cannot move to `Ready` or `Implemented` (`sdd.py status` refuses;
  `sdd.py check` reports E007 if it happens some other way).
- `sdd.py gate <component>` fails, so `implement` must not start.
- A blocking marker in `constitution.md` or `requirements.md` blocks **every**
  component, not just one — an unsettled principle or capability is upstream of
  all of them.

Choose the scope honestly. A marker about an error-message string is not blocking
the whole interface; a marker about who owns retries is.

## When to raise one instead of deciding

Raise a marker when the answer is the **user's to give** and getting it wrong would
cost real rework:

- A tradeoff with no dominant option (sync vs. async, who owns state, what the
  caller passes vs. what is inferred).
- A scope boundary — whether something is in this milestone at all.
- A business rule, threshold, or policy value with no defensible default.
- A division of responsibility between two components.
- Anything touching money, data retention, privacy, or an external commitment.

Do **not** raise one for:

- A choice with an obvious conventional default and no behavioral consequence
  (which stdlib helper, naming, file layout). Decide it, note it if non-obvious.
- Something already answered by the constitution, `requirements.md`, or a
  dependency's spec. Go read them first — a marker raised over a settled question
  is worse than no marker, because it teaches the reader the file is unreliable.
- Something you can answer by looking at the repository. Facts are yours to find;
  only *decisions* belong to the user.

**Prefer asking now over marking.** If you are mid-interview with the user, ask.
A marker is what you write when the question is real, the user is not available
to answer it in this pass, and you must not fabricate the answer to keep going.

## Resolution

Resolving a marker is four edits, in this order, in one pass:

1. **Replace the inline references** with the decided content. Not a note saying it
   was decided — the actual interface, value, or behavior.
2. **Delete the block.** Markers are not archived in place; the log below is the
   archive.
3. **Append to the artifact's `## Clarifications` log**, creating it if absent:

   ```markdown
   ## Clarifications

   ### Session 2026-09-12
   - **U-007** — Does the router retry, or does the caller? → Router retries,
     3 attempts with exponential backoff. *Rationale*: callers are request
     handlers with no budget for their own backoff loop.
   ```
4. **Bump the version** with `sdd.py bump`, naming the marker in `--summary` and
   listing any downstream artifact the answer invalidates in `--stale`.

Resolving a blocking marker is at least a **MINOR** bump — the artifact now says
something it did not say before. If the resolution contradicts what a downstream
artifact already assumed, it is **MAJOR**.

## Surfacing markers to the user

Never end a stage by silently leaving blocking markers in a file. The stage's final
report must list every marker it raised, in this shape, so the user can close them
by replying:

```
Blocking decisions I need from you:

  U-007 (llm-router.md) — Does the router retry, or does the caller?
        A) Router retries with backoff — callers stay simple, router owns the
           latency budget.
        B) Caller owns retry — router stays one-shot and trivially testable.
        Recommendation: A.
```

## Commands

```bash
sdd.py unclear                  # every marker, grouped by file; exit 1 if any block
sdd.py unclear --blocking-only  # just the gating ones
sdd.py unclear --json           # for programmatic use
sdd.py gate <component>         # includes the marker gate for that component
```
