# Constitution template

**Version**: 1.0.0

Write `.specify/memory/constitution.md` in exactly this structure.

---

```markdown
# [PROJECT NAME] Constitution

**Version**: 0.1.0
**Ratified**: [YYYY-MM-DD]
**Last Amended**: [YYYY-MM-DD]

## Core Principles

### I. [Principle Name] (NON-NEGOTIABLE)

[The rule, 1-2 sentences, in MUST / MUST NOT / SHOULD form. State the rule, not
the aspiration behind it.]

**Why**: [What breaks without it. Skip only if genuinely self-evident.]

**Gate**: [How a later stage verifies compliance. A command, a spec section that
must be non-empty, or a specific reviewable property. See the Gate rules below.]

**Source**: [Repository evidence (name the file), or "interview".]

### II. [Principle Name]

[Same shape. Omit "(NON-NEGOTIABLE)" for principles that are strong defaults --
a stage may depart from them with a recorded justification, and must record one.]

## [Optional domain section -- e.g. Data Governance / Model & Prompt Risk /
##  Evaluation Standards / Technology Constraints]

[Include only when the project genuinely needs it. Content that is binding but
doesn't fit the one-rule-per-principle shape -- a table of PII classes and their
handling, a list of approved model providers, mandatory eval sets -- belongs here
rather than being squeezed into a principle.]

## Development Workflow

[Review requirements, quality gates, who approves what, what blocks a merge.
Only what is actually enforced or actually intended to be. Omit the section if
there is nothing real to put in it.]

## Governance

[Amendment process: who may amend, what counts as MAJOR/MINOR/PATCH for this
project if it differs from ARTIFACT-CONTRACT.md's defaults, and the expectation
that every downstream artifact records a Constitution Check.]

Conflicts: where this document and any spec, plan, or code disagree, this
document wins. A stage that finds a conflict surfaces it to the user rather than
resolving it on its own.
```

---

## Gate rules

The `Gate:` line is what makes a principle real. It must name something a later
stage can actually do. Three acceptable shapes:

| Shape | Example |
|---|---|
| **Command** | `Gate: uv run pytest -q passes, and git log shows the test commit preceding the implementation commit.` |
| **Artifact property** | `Gate: every spec's Acceptance Criteria section has >= 1 criterion per public interface method, each phrased given/when/then.` |
| **Reviewable property** | `Gate: no credential, token, or key appears in a log call, an exception message, or a persisted record -- checked by reading every new logging and error path.` |

Unacceptable, because no two reviewers would agree:

- `Gate: code is reviewed for quality.`
- `Gate: the team follows best practices.`
- `Gate: performance is acceptable.`

If you cannot write a Gate for a candidate principle, the principle is not
specific enough yet. Sharpen it until you can, or drop it.

## Content rules

- **Declarative and testable.** MUST / MUST NOT / SHOULD. Never "should ideally",
  "where possible", "as appropriate" -- each of those is an escape hatch that
  makes the gate unenforceable.
- **3-7 principles.** Not a fixed count, but if you are past seven, some of them
  are not load-bearing. A principle that would never reject a real design is
  decoration.
- **NON-NEGOTIABLE is a hard gate.** `plan` refuses to write a spec that violates
  one; `implement` refuses to build one. Mark a principle NON-NEGOTIABLE only if
  you mean the pipeline should stop. Everything else is a strong default: a stage
  may depart from it, but must record the justification in the artifact.
- **Numbering is stable.** Principles keep their roman numeral for life. A removed
  principle leaves its number retired, not reused -- older specs cite it.
- **Unresolved fields become `[!UNCLEAR]` markers**, never invented values. An
  unknown ratification date in an inherited project is
  `[!UNCLEAR:U-001]` with a block explaining it, not a plausible-looking date.
- **No implementation detail.** "Python 3.12 with uv" is an architecture decision
  and belongs in `requirements.md` as an `AD-NNN`, unless it is genuinely
  non-negotiable governance -- in which case it goes in a Technology Constraints
  section, not in a principle.

## Worked example

```markdown
### I. Test-First (NON-NEGOTIABLE)

Every behavioral change MUST have a test that fails before the implementation
exists and passes after. Tests are written from the spec's Acceptance Criteria,
not from the finished code.

**Why**: A test written after the implementation tests what the code does, not
what the spec required -- which is exactly the bug it was supposed to catch.

**Gate**: `implement` runs the new tests before writing any implementation and
records their failure output in its report. `uv run pytest -q` passes at the end.

**Source**: interview.

### II. Evaluation Rigor (NON-NEGOTIABLE)

No prompt or model change MUST ship without being scored on the named held-out
eval set in `evals/`, with the result recorded in MLflow. A regression beyond the
threshold in the component's spec blocks the change.

**Why**: Prompt changes look free and are not; without a fixed eval set,
"it seems better" is the only evidence anyone has.

**Gate**: `implement` runs `uv run python -m evals.run --suite <component>` and
records the score against the threshold in the spec's Acceptance Criteria.

**Source**: repository evidence -- `evals/` and `mlflow.yaml` already present.

### III. Minimal Dependencies

A new runtime dependency SHOULD be added only when it replaces meaningfully more
code than it adds. The justification is recorded in the implementing stage's
report: what it replaces, what was considered instead.

**Why**: Each dependency is a permanent supply-chain and upgrade obligation.

**Gate**: `implement` reports every dependency added, with its justification. A
dependency appearing in a lockfile with no such record is a violation.

**Source**: repository evidence -- lockfile has 11 direct dependencies across
three services.
```
