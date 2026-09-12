# README.md template (the component index)

**Version**: 1.0.0

Write `.specify/specs/README.md` in exactly this structure. `sdd.py` parses the
tables, so the column names and their order are fixed.

---

```markdown
# Component specs — index

**Version**: 0.1.0
**Ratified**: [YYYY-MM-DD]
**Last Amended**: [YYYY-MM-DD]

Governed by [`../memory/constitution.md`](../memory/constitution.md), derived from
[`requirements.md`](requirements.md).

**Workflow**: incremental. Spec one component → implement it → let what that
surfaced inform the next. Status moves `Not started → Draft → Ready → Implemented`.
Row order is build order: `plan` and `implement` with no argument take the first
eligible row from the top.

**Never edit a Status or Version cell by hand.** Use
`sdd.py status <component> <status>` and `sdd.py bump <file> ...` — they write the
index and the spec header together, which is the only way the two stay in
agreement.

## [Foundational / shared library]

| ID | Component | Status | Spec | Version | Notes |
|---|---|---|---|---|---|
| C-001 | Config Loader | Not started |  |  | env + file config; needed by everything |
| C-002 | LLM Client | Not started |  |  | CAP-001; single provider per AD-002 |

## [Service name]

| ID | Component | Status | Spec | Version | Notes |
|---|---|---|---|---|---|
| C-005 | Chat Endpoint | Not started |  |  | CAP-001; depends on C-002, C-004 |

## Cross-cutting overviews

Capabilities that span more than one component and need a short explanation doc
rather than a spec of their own.

| Capability | Spans | Doc | Status |
|---|---|---|---|
| CAP-001 Retrieval-grounded answers | C-003, C-004, C-005 | `docs/explanation/retrieval.md` | Not started |
```

---

## Column rules

| Column | Rule |
|---|---|
| `ID` | `C-NNN`, assigned in index order at creation. Permanent. Never reused, never renumbered. |
| `Component` | The name `plan` and `implement` match against. Keep it distinctive — two components whose names are substrings of each other make the argument form ambiguous, and the tools will refuse rather than guess. |
| `Status` | Exactly one of `Not started`, `Draft`, `Ready`, `Implemented`. |
| `Spec` | Empty while `Not started`; a relative markdown link once a spec exists. |
| `Version` | Empty while `Not started`; mirrors the spec header's version, maintained by `sdd.py bump`. |
| `Notes` | The component's one-line purpose, the `CAP`/`AD` it traces to, and what it depends on. This is what `plan` reads first — a Notes cell saying only "auth stuff" wastes the next stage's whole first step. |

## Ordering rules

Row order **is** build order, and `plan`/`implement` follow it literally.

1. Foundational and shared components first — config, clients, data access.
2. Then each service, in dependency order within its own group.
3. A component appears after everything it depends on. Always.
4. If two components depend on each other, the decomposition is wrong. Extract the
   shared part into a third component rather than recording the cycle — `sdd.py`
   will not detect it for you, and `implement` will deadlock on it.

## Grouping rules

Group by deployable unit (service) or by shared library. Groups are `## ` headings;
`sdd.py index` renders them. Regrouping a component is free — spec files live flat
in `specs/`, so no link breaks when a row moves between groups.
