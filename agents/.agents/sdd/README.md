# SDD toolkit

**Version**: 1.0.0

The shared half of the `constitution` → `specify` → `plan` → `implement` skills:
one script and three protocol documents that all four stages depend on.

| File | What it is |
|---|---|
| `sdd.py` | Every check the pipeline makes mechanically rather than by eye. Stdlib only, no network, no config. |
| `LAYOUT.md` | Directory layout, identifier schemes, component statuses. |
| `ARTIFACT-CONTRACT.md` | Versioning: header block, semver rules, Sync Impact Reports, dependency pinning. |
| `UNCLEAR-PROTOCOL.md` | `[!UNCLEAR]` grammar, blocking rules, resolution. |

## Bootstrapping a project

```bash
python3 ~/.agents/sdd/sdd.py init /path/to/project
```

This creates `.specify/{memory,specs,toolkit}/` and copies this whole directory into
`<project>/.specify/toolkit/`. From then on every stage runs the vendored copy at a
stable path:

```bash
python3 .specify/toolkit/sdd.py <command>
```

Each skill's Step 0 does this automatically if `.specify/toolkit/sdd.py` is absent,
trying these source locations in order:

```
~/.agents/sdd/sdd.py
~/.claude/sdd/sdd.py
<this skill's dir>/../../sdd/sdd.py
```

If none resolve, the stage reports that and stops rather than proceeding with the
checks silently switched off. An unchecked pipeline that looks like a checked one is
the worst outcome available.

## Commands

```bash
sdd.py init [path] [--force]   # scaffold .specify/ and vendor the toolkit
sdd.py doctor                  # one-screen health summary
sdd.py check [--json --strict] # every consistency rule; exit 1 on ERROR
sdd.py unclear [--blocking-only --json]
sdd.py gate <component>        # may this be implemented right now? exit 1 = no
sdd.py index [--json]          # live component index
sdd.py status <component> <status>
sdd.py bump <file> --level major|minor|patch --summary "..." [--stale "a.md,b.md"]
```

## Finding codes

| Code | Severity | Meaning |
|---|---|---|
| `E001` | error | Artifact header is missing a required field. |
| `E002` | error | Version is not semver (or a date is not ISO — warning). |
| `E003` | error | Unknown status, or a malformed component id. |
| `E004` | error | Index references a spec that does not exist, or a required artifact is missing. |
| `E005` | error | Index and spec header disagree about status, version, or id. |
| `E006` | error | Malformed `[!UNCLEAR]` marker: no id, no `Blocks:`, duplicate id, or a dangling inline reference. |
| `E007` | error | Status is `Ready`/`Implemented` while blocking markers remain. |
| `E008` | error | Component is `Implemented` but a dependency is not. |
| `E009` | error | A declared dependency id is not in the index. |
| `E010` | error | Duplicate component id in the index. |
| `E011` | error | Dependency pin is a MAJOR behind the dependency's current version. |
| `W003` | warn | `Not started` row links a spec file. |
| `W004` | warn | Spec file is not referenced by any index row. |
| `W005` | warn | A Sync Impact Report names a stale file that does not exist. |
| `W006` | warn | A file marked stale has not been re-read since. |
| `W010` | warn | No constitution — plan/implement have no gates to check against. |
| `W011` | warn | Dependency pin is behind, same MAJOR. |
