# Spec-driven development pipeline

**Version**: 1.1.0

Four skills that take a product from "we have a business need" to working code,
where every decision is written down before it is built, and nothing undecided
gets built at all.

```
constitution  ──▶  specify  ──▶  plan  ──▶  implement
     │               │            │            │
 the rules      what & why    one component  one component
 (governance)   (capabilities,  in detail     in code
                 architecture,  (interface,   (tests first,
                 components)    criteria)      gated)
```

| Stage | Writes | Runs |
|---|---|---|
| `constitution` | `.specify/memory/constitution.md` | Once per project, amended as governance changes. |
| `specify` | `.specify/specs/requirements.md`, `.specify/specs/README.md` | Once per product, amended when the business need changes. |
| `plan` | `.specify/specs/<component>.md` | Once per component. |
| `implement` | Code, tests, an implementation record in the spec | Once per component, after its gate passes. |

Two skills sit outside the pipeline, for the two ways a stage stalls:

| Skill | Use when |
|---|---|
| `grill-me` | The design is under-examined. A relentless breadth-first interview that surfaces every decision hanging off every other one. |
| `teach` | A decision is blocked because its options aren't understood. Teaches one concept, then writes a lesson and `repeater` cards to `~/Work/lessons-learned/<topic>/`. |

An `[!UNCLEAR]` marker you cannot answer is a `teach` session, not a guess.

## The two rules that make it work

**1. Nothing marked `[!UNCLEAR]` gets implemented.**

Every stage that meets an undecided point writes a marker instead of a guess:

```markdown
> [!UNCLEAR] U-007 — Does the router retry, or does the caller?
> **Blocks**: Interface, Behavior & edge cases
> **Options**: A) router retries with backoff  B) caller owns retry
> **Raised**: 2026-09-12 (plan)
```

A blocking marker stops the spec reaching `Ready` and makes `sdd.py gate` fail, so
`implement` refuses to build. The failure is the feature — it is the difference
between a decision the user made and a decision an agent invented while trying to
be helpful. See `../sdd/UNCLEAR-PROTOCOL.md`.

**2. Every artifact is versioned, and every change says what it invalidated.**

Each file carries `**Version**`, `**Ratified**`, `**Last Amended**`, and each
amendment prepends a Sync Impact Report naming the downstream files now owed a
re-read. `sdd.py check` keeps flagging them until someone actually re-reads them.
See `../sdd/ARTIFACT-CONTRACT.md`.

## The toolkit

The mechanical checks — status/version agreement, marker gating, dependency
readiness, version-pin drift, staleness debt — live in `../sdd/sdd.py`, vendored
into each project at `.specify/toolkit/sdd.py` so every stage runs it from one
stable path.

```bash
python3 ~/.agents/sdd/sdd.py init .    # scaffold a project
python3 .specify/toolkit/sdd.py doctor # where does this project stand?
python3 .specify/toolkit/sdd.py index  # the work queue
python3 .specify/toolkit/sdd.py check  # do the artifacts agree? exit 1 if not
python3 .specify/toolkit/sdd.py unclear
python3 .specify/toolkit/sdd.py gate "LLM Router"
```

Every stage ends with `check` and is not finished until it exits 0.

## A typical run

```bash
/constitution                  # 3-7 principles, each with a Gate line
/specify                       # interview → requirements.md + component index
/plan                          # first Not-started component → a Draft spec
                               # ...answer the [!UNCLEAR] markers it raises
/teach "quem é dono do retry"  # can't answer one? learn the tradeoff, then answer
/plan "LLM Router"             # refine; markers resolve; status → Ready
/implement                     # gate passes → tests first → code → Implemented
/plan                          # next component, informed by what that surfaced
```

## Files

```
.agents/
├── sdd/                            # shared toolkit (vendored into projects)
│   ├── sdd.py
│   ├── LAYOUT.md                   # directories, ids, statuses
│   ├── ARTIFACT-CONTRACT.md        # versioning, Sync Impact Reports, pinning
│   └── UNCLEAR-PROTOCOL.md         # [!UNCLEAR] grammar and gates
└── skills/
    ├── constitution/{SKILL.md, CONSTITUTION-TEMPLATE.md}
    ├── specify/{SKILL.md, REQUIREMENTS-TEMPLATE.md, INDEX-TEMPLATE.md,
    │            ARCHITECTURE-DECISIONS.md}
    ├── plan/{SKILL.md, SPEC-TEMPLATE.md, SPEC-QUALITY-CHECKLIST.md}
    ├── implement/{SKILL.md, IMPLEMENTATION-RECORD-TEMPLATE.md}
    ├── grill-me/SKILL.md
    └── teach/SKILL.md
```

Every SKILL.md ends with a **failure modes** table: the specific ways that stage
goes wrong, and the required behaviour instead. When a stage misbehaves, that table
is the first place to look — and the right place to add what you learned.

## Deployment

`agents/.agents/` is the single source. `claude/.claude/skills` and
`claude/.claude/sdd` are relative symlinks into it, so both stow packages deploy
the same files to `~/.agents/` and `~/.claude/` with no copy to keep in sync.

```
claude/.claude/skills -> ../../agents/.agents/skills
claude/.claude/sdd    -> ../../agents/.agents/sdd
```

Edit under `agents/.agents/`; never under `claude/.claude/`.
