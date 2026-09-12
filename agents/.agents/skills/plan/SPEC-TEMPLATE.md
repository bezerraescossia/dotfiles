# Component spec template

**Version**: 1.0.0

Write `.specify/specs/<slug>.md` in this structure. The header block and the
`## Dependencies` heading are parsed by `sdd.py` — keep them exactly as shown.
Sections marked *(as needed)* are included only when the component has something
real to put in them; delete them otherwise rather than writing "N/A".

---

```markdown
# Spec: [Component Name]

**ID**: C-NNN
**Version**: 0.1.0
**Status**: Draft
**Ratified**: [YYYY-MM-DD]
**Last Amended**: [YYYY-MM-DD]
**Location**: [path the code will live at, e.g. libs/common/config]
**Serves**: [CAP-001, CAP-003]
**Constrained by**: [AD-002, AD-005]
**Used by**: [C-005 Chat Endpoint, C-007 Batch Scorer -- or "nothing yet"]

## Purpose

[Why this exists and what it is responsible for. 2-4 sentences. Say what it owns
and, just as importantly, what it deliberately does not own -- the boundary is
what stops the neighbouring component from growing into it.]

## Interface

[Actual signatures, not prose. Names, parameter types, return types, raised
exceptions. This is the contract another component's spec will pin a version
against, so it must be readable as a contract.]

```python
class ConfigLoader:
    def __init__(self, sources: Sequence[Source], *, strict: bool = True) -> None: ...

    def get(self, key: str, default: T | None = None) -> T:
        """Raises MissingKeyError if strict and the key is absent."""

    def reload(self) -> ReloadResult:
        """Re-reads every source. Never partially applies: on any source failure
        the previous snapshot stays live and the error is returned, not raised."""
```

## Dependencies

[One line per dependency, in exactly this shape -- sdd.py parses the C-NNN id and
the @version pin, and uses the pin to warn you when the dependency moves.]

- C-001 Config Loader @1.0.0 — needs `get()` for the provider key and `reload()`
- C-004 Token Counter @0.3.0 — needs `count(text, model)` for budget enforcement

[If it has none: write "None." on its own line -- not an empty section.]

## Data touched

[Tables, caches, queues, files, external services this component reads or writes
*directly*. "Directly" matters: something reached through a dependency belongs in
that dependency's spec, not here. Say read, write, or both.]

## Behavior & edge cases

[What happens on: empty input, malformed input, a dependency timing out, a
dependency returning an error, two calls overlapping, the same call arriving
twice, a partial write, a restart mid-operation. Cover the ones that can actually
happen to this component; don't pad with the ones that can't.]

## Errors

| Error | Raised when | Handled here or surfaced |
|---|---|---|
| `MissingKeyError` | strict mode and the key is absent from every source | surfaced -- callers decide whether a missing key is fatal |
| `SourceUnavailable` | a source read fails during `reload()` | handled -- previous snapshot stays live, returned in `ReloadResult` |

## [Component-specific sections, as needed]

[A resolution algorithm, a state machine, a config shape, a retry ladder, a
concurrency model, a prompt contract -- whatever the interview actually decided
that the sections above have no home for. Not every spec needs any of these.]

## Out of scope

[Explicitly excluded, especially the natural-looking extensions. Each line should
answer "why would someone think this belonged here?" -- that is what makes it
useful to the next reader.]

- Secret decryption — the loader returns the reference; C-006 Secrets Client
  resolves it. Keeping decryption out means config can be logged safely.
- Hot-reload on file change — `reload()` is explicit. Watching is C-009's job.

## Acceptance criteria

[The most important section in this document. `implement` writes one failing test
per criterion, from this section alone, before any code exists.

Each criterion: an id, a concrete input, and a checkable outcome. If you cannot
picture the assertion, the criterion is not specific enough yet.]

- **AC-001** — Given sources `[env, file]` and key `MODEL` set in both, when
  `get("MODEL")` is called, then the env value is returned. (Precedence is source
  order, first wins.)
- **AC-002** — Given `strict=True` and key `ABSENT` in no source, when
  `get("ABSENT")` is called, then `MissingKeyError` is raised naming the key.
- **AC-003** — Given `strict=False`, when `get("ABSENT", default=7)` is called,
  then `7` is returned and nothing is raised.
- **AC-004** — Given a loaded snapshot, when `reload()` runs and one source raises,
  then `get()` still returns the previous values and `ReloadResult.errors` names
  the failed source.
- **AC-005** — Given any key whose name matches the secret pattern, when the loader
  logs at DEBUG, then the value does not appear in the log record. (Constitution IV.)

## Constitution check

[Filled in at plan Step 5, before the file is written. One row per principle.]

| Principle | Result | Note |
|---|---|---|
| I. Test-First (NON-NEGOTIABLE) | Pass | AC-001..005 are each directly testable |
| II. Simplicity (NON-NEGOTIABLE) | Pass | no watcher, no decryption -- both in Out of scope |
| IV. Security (NON-NEGOTIABLE) | Pass | AC-005 asserts secret values never reach a log record |
| V. Minimal Dependencies | Deviation | adds `pydantic`; see Complexity below |

### Complexity / deviations

[Fill in only where a row above is `Deviation` or `Violation`. A NON-NEGOTIABLE
violation must never reach this table -- it is resolved with the user before the
spec is written.]

| Deviation | Why it is needed | What was rejected, and why |
|---|---|---|
| Adds `pydantic` | Source schema validation with usable error messages | Hand-rolled validation -- ~200 lines and worse errors, for one avoided dependency already present transitively |

## Open questions

[Every [!UNCLEAR] block for this component. Delete the section when there are
none. Per UNCLEAR-PROTOCOL.md.]

> [!UNCLEAR] U-003 — Does `reload()` block concurrent `get()` calls, or serve the
> old snapshot until the swap completes?
> **Blocks**: Interface, Behavior & edge cases, AC-004
> **Options**: A) lock-free, old snapshot served until atomic swap — no caller ever
>              blocks, brief window where two callers see different config
>              B) read-write lock — strictly consistent, `get()` can block on reload
> **Raised**: 2026-09-12 (plan)

## Clarifications

[Appended as markers resolve. Never edited or removed.]

### Session [YYYY-MM-DD]

- **U-003** — Does `reload()` block `get()`? → Lock-free atomic swap; old snapshot
  served until the new one is complete. *Rationale*: `get()` is on the request
  path and must never block; a sub-millisecond skew window is acceptable because
  no caller compares two keys across a reload.

## Related doc updates once implemented

[Deferred until `implement` runs -- it applies this section as its last step.
Anything this spec's decisions make wrong elsewhere: a README, an ADR, another
component's Notes cell, an overview doc.]

- `docs/explanation/configuration.md` — describes file-only config; add env
  precedence once C-001 lands.

## Implementation record

[Written by `implement`, not by `plan`. Leave the heading out of the draft; the
implementing stage adds it.]
```

---

## Writing rules

- **Interface is signatures, not description.** If a reader cannot call the
  component from this section alone, it is not finished.
- **Every acceptance criterion is one assertion.** "Handles errors gracefully" is
  not a criterion. "Given X, when Y, then Z" with concrete values is.
- **Acceptance criteria cover the failure paths, not only the happy one.** The
  happy path is the one an implementation gets right by accident.
- **Dependencies are always version-pinned.** The pin is what makes drift
  detectable; an unpinned dependency silently rots.
- **Cite, don't restate.** `AD-003` and `CAP-001` are referenced by id. Copying
  their text in creates a second copy that can drift from the first.
- **`Out of scope` earns its place by being surprising.** Listing things nobody
  would have expected here is noise; listing the ones they would is the point.
- **No implementation inside the spec.** How the retry loop is written is
  `implement`'s business. *That* there are three retries with backoff is this
  document's.
