# Layout, identifiers and statuses

**Version**: 1.1.0

Everything the pipeline produces lives under one directory at the project root.

```
.specify/
├── memory/
│   └── constitution.md        # governance principles. Global, outlives every feature.
├── specs/
│   ├── requirements.md        # business context, capabilities, architecture decision log
│   ├── README.md              # the component index -- the pipeline's work queue
│   └── <component>.md         # one detailed spec per component
├── lessons/
│   └── <topico>.md            # lessons written by `teach`, when a decision was
│                              # blocked by a concept nobody had a grip on
└── toolkit/
    ├── sdd.py                 # the checker (vendored by `sdd.py init`)
    ├── ARTIFACT-CONTRACT.md   # versioning rules
    ├── UNCLEAR-PROTOCOL.md    # [!UNCLEAR] rules
    └── LAYOUT.md              # this file
```

`lessons/` is for humans, not for the checker: `sdd.py` never reads it, so a lesson
carries no version header, no Sync Impact Report and no id. It gates nothing — it
exists so the reasoning behind a resolved `[!UNCLEAR]` survives next to the decision
it produced. Its spaced-repetition cards do **not** live here; they go to one global
deck outside the project. See the `teach` skill.

The toolkit is **vendored into the project** rather than referenced from the skill
directory, so every stage invokes it at one stable, project-relative path:
`python3 .specify/toolkit/sdd.py`. No `../..` guessing, and the project keeps working
if the skills move.

## Identifiers

| Prefix | Assigned by | Scope | Meaning |
|---|---|---|---|
| `C-NNN` | `specify` | global | Component. Assigned when the component enters the index; never reused, never renumbered, even if the component is dropped. |
| `CAP-NNN` | `specify` | `requirements.md` | Capability — a business need translated into something the system must be able to do. |
| `AD-NNN` | `specify` | `requirements.md` | Architecture decision, with its rationale. Downstream artifacts cite these instead of restating them. |
| `P-N` / roman | `constitution` | `constitution.md` | Principle. |
| `U-NNN` | any stage | per file | An open question. See UNCLEAR-PROTOCOL.md. |
| `AC-NNN` | `plan` | per spec | Acceptance criterion. Tests cite these. |

Stable ids are what let four separate documents refer to the same decision without
restating it — and restating is where contradictions get in.

## Component statuses

| Status | Means | Set by |
|---|---|---|
| `Not started` | In the index, no spec written. | `specify` |
| `Draft` | A spec exists. May still carry blocking `[!UNCLEAR]` markers. **Not** safe to implement without passing the gate. | `plan` |
| `Ready` | Spec is complete, constitution-checked, no blocking markers. | `plan` (or the user) |
| `Implemented` | Code exists, tests pass, the spec's deferred doc updates are applied. | `implement` |

There is deliberately no `Blocked` status. Blockedness is computed, not stored —
`sdd.py gate <component>` derives it from markers, dependency statuses and version
pins, so it can never go stale the way a hand-maintained field does.

Move statuses with `sdd.py status <component> <status>`, which writes the index row
and the spec header together and refuses to promote anything carrying a blocking
marker.

## The component index

`specs/README.md` is the pipeline's work queue. Its table order encodes build order:
foundational and shared components first, then services that depend on them. `plan`
with no argument takes the first `Not started` row; `implement` with no argument
takes the first `Draft`/`Ready` row.

Columns, in this order:

```markdown
| ID | Component | Status | Spec | Version | Notes |
|---|---|---|---|---|---|
| C-001 | Config Loader | Implemented | [config-loader.md](config-loader.md) | 1.0.0 | libs/common/config |
```

Group rows under `## ` headings by service or library. `sdd.py index` renders the
live view — index rows joined against each spec's actual header and marker count.

## File naming

Component spec files are kebab-case of the component name: `LLM Router` →
`llm-router.md`. Flat in `specs/` — no subdirectories, so every link is a bare
filename and cannot rot when something is regrouped in the index.
