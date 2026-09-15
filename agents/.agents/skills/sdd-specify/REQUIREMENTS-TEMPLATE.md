# requirements.md template

**Version**: 1.0.0

Write `.specify/specs/requirements.md` in exactly this structure. The `**Field**:`
header block and the id schemes are parsed by `sdd.py` — don't restyle them.

---

```markdown
# [PRODUCT NAME] Requirements

**Version**: 0.1.0
**Ratified**: [YYYY-MM-DD]
**Last Amended**: [YYYY-MM-DD]
**Constitution**: [version checked against, e.g. 1.2.0 -- or "none"]

## Business Context

**Problem**: [What is wrong today, for whom. Plain language, no solution in it.]

**Users**: [Who uses it, and in what situation.]

**Success**: [What "it worked" means, concretely enough to measure. If there is a
number, put the number here.]

**Constraints**: [Fixed before this project started -- systems it must integrate
with, regulation, budget, timeline, team size.]

**Not in this milestone**: [Explicitly out. This section prevents more rework than
any other, because it is what stops a capability being half-built "while we're in
there".]

## Capabilities

What the system must be able to do, derived from the business context. Each row
is the reason one or more components exist.

| ID | Capability | Business driver | Components |
|---|---|---|---|
| CAP-001 | [e.g. Answer questions grounded in the customer's own documents] | [which business problem this serves] | C-004, C-005, C-007 |
| CAP-002 | [...] | [...] | [...] |

Rules:
- Every capability traces to something in Business Context. No orphan capabilities.
- Every component in the index traces to at least one capability or one AD.
- The Components column is filled in after Step 4, once ids are assigned.

## Data & Compliance

[Only if Round C surfaced anything. Data sources and types; sensitive classes and
how they are handled; what may never leave the environment or reach a third-party
API; retention and audit obligations. If nothing applies, say "None identified"
and why -- an empty section reads as an oversight.]

## Architecture Decisions

One row per decision actually asked about and answered. A decision nobody made
does not belong here.

| ID | Area | Decision | Rationale | Source |
|---|---|---|---|---|
| AD-001 | Language / framework | Python 3.12, uv | [why, including what was given up] | interview |
| AD-002 | Testing | pytest + eval harness on a named held-out set | mandated by Constitution III | constitution 1.2.0 |
| AD-003 | RAG backend | Postgres + pgvector | [why, including what was given up] | interview |

Rules:
- **Rationale states the tradeoff accepted**, not just the benefit. "Postgres +
  pgvector -- one datastore instead of two; accepted weaker hybrid search because
  the corpus is under 100k chunks" is a rationale. "Postgres is good" is not.
- **Source** is `interview`, `constitution <version>`, or `evidence: <file>`.
- Areas deliberately not asked about are listed under Skipped below, not omitted
  silently.

### Areas skipped

| Area | Why it didn't apply |
|---|---|
| Streaming | Nothing is real-time -- all scoring is nightly batch (CAP-002). |
| Async work | Every request completes inside one HTTP call. |

## Open questions

[Every [!UNCLEAR] block in this file lives here, so the user can see them in one
place. Per UNCLEAR-PROTOCOL.md. Delete the section when there are none.]

> [!UNCLEAR] U-001 — Is multi-tenant isolation required at launch, or after the
> first enterprise customer?
> **Blocks**: AD-005 (app database), C-002, C-006
> **Options**: A) row-level isolation now — costs ~1 week, no migration later
>              B) single tenant now — ships sooner, needs a data migration later
> **Raised**: 2026-09-12 (specify)

## Clarifications

[Appended as [!UNCLEAR] markers are resolved. Never edited or removed -- this is
the record of what was decided and why, and it is the first thing anyone reads
when asking "why is it like this?".]

### Session [YYYY-MM-DD]

- **U-001** — Multi-tenant isolation at launch? → Row-level isolation from day
  one. *Rationale*: the first two prospects are enterprise; a later migration
  would land mid-pilot.
```

---

## Writing rules

- **No implementation detail in Business Context or Capabilities.** Those sections
  must stay true regardless of how it gets built. The moment a framework name
  appears there, the document has stopped being a requirements document.
- **Every number is sourced.** "Under 200ms P95" is a requirement; "fast" is not.
  If the user didn't give a number and one matters, that is an `[!UNCLEAR]`.
- **Ids never change.** `CAP-003` means the same thing for the life of the project.
  Removing a capability retires its id; it is never reassigned.
- **Amendments are additive first.** Preserve every row the user isn't changing.
  Where a new requirement contradicts an old row, mark the old row and surface
  the conflict -- don't quietly rewrite it.
