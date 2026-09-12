# The artifact contract

**Version**: 1.0.0

Every file this pipeline writes under `.specify/` is a **versioned artifact**. The
contract below is what lets a later agent — or the user, six weeks on — open one
file and know how current it is, what it last changed, and what that change
invalidated, without reconstructing the history from git.

## 1. The header block

Immediately after the `# Title`, before any `## ` section:

```markdown
# Spec: LLM Router

**ID**: C-002
**Version**: 0.3.0
**Status**: Ready
**Ratified**: 2026-09-02
**Last Amended**: 2026-09-12
```

| Field | Applies to | Rule |
|---|---|---|
| `ID` | component specs | `C-NNN`, assigned by `specify` when the component enters the index, never reused or renumbered. |
| `Version` | all | `MAJOR.MINOR.PATCH`. Starts at `0.1.0` for a first draft, `1.0.0` when it first reaches `Ready`. |
| `Status` | component specs | One of `Not started`, `Draft`, `Ready`, `Implemented`. |
| `Ratified` | all | ISO date the artifact first existed. Never changes. |
| `Last Amended` | all | ISO date of the most recent change. `sdd.py bump` stamps it. |

`sdd.py` reads this block only from the region **before the first `## ` heading**,
so the words "Status" or "Version" appearing in prose further down can never be
mistaken for a header field.

## 2. Semantic versioning, defined per artifact

The bump level is not a judgement call about size. It is a statement about **what
downstream work is now invalid**.

| Level | Means | Examples |
|---|---|---|
| **MAJOR** | Something already written elsewhere against this artifact is now wrong. | A principle removed or redefined; a spec's interface signature changed or removed; a capability dropped from `requirements.md`; an architecture decision reversed. |
| **MINOR** | Something new was added, or an open question was answered. Existing downstream work stays valid. | A new principle; a new component in the index; a new method on an interface; a `[!UNCLEAR]` resolved; a new acceptance criterion. |
| **PATCH** | Nothing that anyone could have built against changed. | Wording, typos, a clarified rationale, a formatting fix, a status-only move. |

If you cannot decide between two levels, pick the higher one and say why in the
Sync Impact Report. An over-declared MAJOR costs one re-read; an under-declared one
costs silently-wrong code.

## 3. The Sync Impact Report

Every amendment prepends an HTML comment to the very top of the file, above the
title. `sdd.py bump` writes it; do not hand-write it.

```html
<!--
Sync Impact Report
Date: 2026-09-12
Version: 0.2.0 -> 0.3.0 (MINOR)
Changed: U-007 resolved -- router owns retry (3 attempts, exponential backoff)
Stale downstream: chat-endpoint.md@1.1.0, requirements.md@0.4.0
-->
```

`Stale downstream` is the load-bearing field, and it is a **promise, not a note**.
Naming a file there means: that file was written against an older version of this
one and is owed a re-read.

Pass plain filenames to `--stale`; `sdd.py bump` stamps each one with the version
it holds at that moment (`chat-endpoint.md@1.1.0`). `sdd.py check` then reports
`W006` against that file for exactly as long as it is *still on that version* — so
the debt is tracked per-version rather than per-date, and two amendments on the
same day can't hide each other.

Discharging it means one of two things, both of which end in a bump on the
downstream file:

- It genuinely needed changing → change it and bump (level per the table above).
- It did not → bump `patch` with `--summary "re-read against <file> v<X.Y.Z>; no change needed"`.

Only the previous report is replaced on a new bump. The full history is git's job;
the header answers "is this current?" at a glance, which git does not.

### What to list as stale

- Amending `constitution.md` → every `Draft`/`Ready` spec whose Constitution Check
  touched the changed principle. Every `Implemented` one too, if the change is MAJOR.
- Amending `requirements.md` → every component in the index derived from the changed
  capability or decision.
- Amending a component spec, MAJOR → every spec whose `## Dependencies` cites it.
- Amending a component spec, MINOR/PATCH → usually `none`.

## 4. Dependency pinning

A component spec declares its dependencies with the version it was written against:

```markdown
## Dependencies
- C-001 Config Loader @1.0.0 — needs `load(key)` and `reload()`
- C-004 Token Counter @0.3.0 — needs `count(text, model)`
```

The `@X.Y.Z` pin is what makes drift detectable:

- Pinned MAJOR ≠ current MAJOR → `sdd.py check` reports **E011** (error). The
  dependency's interface changed incompatibly; this spec must be re-read and
  re-pinned before anything is built against it.
- Pinned version ≠ current, same MAJOR → **W011** (warning). Probably additive;
  confirm nothing you rely on moved, then re-pin.

## 5. Write discipline

Artifact writes come in units. A unit is: **write the content, bump the version,
update the index.** `sdd.py bump` and `sdd.py status` each cover two of those three
so they cannot drift apart — always prefer them over editing both files by hand.

If part of a unit fails, say so in the report rather than leaving the artifacts
half-updated and reporting success. Half-updated state is exactly what
`sdd.py check` exists to catch, so the honest recovery is cheap: run it, fix what
it names, run it again.

## 6. Commands

```bash
sdd.py bump <file> --level minor --summary "what changed" --stale "a.md,b.md"
sdd.py status <component> Ready     # index + spec header together; refuses on blocking markers
sdd.py check                        # every rule in this document, mechanically
sdd.py doctor                       # one-screen summary
```
