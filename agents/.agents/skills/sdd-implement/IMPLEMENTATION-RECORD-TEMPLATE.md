# Implementation record template

**Version**: 1.0.0

`implement` Step 7 appends this to the bottom of the component's spec. It is the
audit trail: six weeks on, this is what answers "why is the code different from
what the spec section above says?" without anyone re-deriving it from git.

Append it; never replace the sections above it. On a re-implementation, add a new
dated block rather than editing the previous one.

---

```markdown
## Implementation record

### [YYYY-MM-DD]

**Built at**: [concrete paths -- `libs/common/config/loader.py`,
`libs/common/config/tests/test_loader.py`]

**Entry points**: [what a caller imports or invokes, e.g. `from common.config
import ConfigLoader`]

**Spec version implemented**: [the spec's version at the time of the build, e.g.
1.0.0 -- so a later reader can tell whether the code predates a later amendment]

**Constitution version**: [e.g. 1.2.0 -- or "none loaded"]

#### Test-first evidence

[Required when a Test-First principle applied. The red-phase output, trimmed to
the failure lines. This is the evidence the sequence actually happened -- a
report claiming red-green with no output is a claim, not evidence.]

```
$ uv run pytest libs/common/config/tests -q
E   ImportError: cannot import name 'ConfigLoader' from 'common.config'
5 failed in 0.31s
```

[If Test-First did not apply, say so and say what you did instead:
"No constitution loaded; tests were written from the Acceptance Criteria without
the red-before-green requirement. This was a default, not an enforced rule."]

#### Acceptance criteria coverage

| Criterion | Test | Result |
|---|---|---|
| AC-001 | `test_env_source_wins_over_file` | pass |
| AC-002 | `test_strict_missing_key_raises` | pass |
| AC-003 | `test_non_strict_returns_default` | pass |
| AC-004 | `test_reload_failure_keeps_previous_snapshot` | pass |
| AC-005 | `test_secret_value_absent_from_debug_log` | pass |

[Every AC in the spec gets a row. An AC with no test is a gap -- name it here and
in the report rather than leaving the table looking complete.]

#### Gates

| Gate | Command | Result |
|---|---|---|
| Full test suite | `uv run pytest -q` | 142 passed |
| Lint | `uv run ruff check .` | clean |
| Format | `uv run ruff format --check .` | clean |
| Types | `uv run mypy libs/common` | clean |
| Secrets in logs/errors | read every new logging and error path | none found |

[State failures as failures, with the output. A gate that could not be run says
so and why -- never omit the row.]

#### Ambiguities resolved during implementation

[From Step 4. Only the ones with behavioral consequence -- the obvious choices
don't belong here.]

| What | Decided | By |
|---|---|---|
| `reload()` on a source that returns empty vs. errors | Empty is a valid snapshot; only a raised error preserves the previous one | user, this session |

#### Deviations from the spec

[Anything built differently from what the sections above describe, and why. Each
deviation must say whether the spec was updated to match -- and if the Interface
changed, this stage owed a MAJOR bump.]

| Spec said | Built as | Why | Spec updated? |
|---|---|---|---|
| `reload() -> None` | `reload() -> ReloadResult` | callers need to know which source failed; returning it avoids a second call | yes -- Interface updated, MAJOR bump, C-005 marked stale |

[If there were none: "None -- built as specified."]

#### Dependency drift observed

[Where a dependency's spec disagreed with its actual code. The code was built
against; this is the finding for `plan` to reconcile.]

| Dependency | Spec says | Code does | Built against |
|---|---|---|---|
| C-004 Token Counter @0.3.0 | `count(text, model)` | `count(text, *, model, encoding=None)` | the code |

[If there was none: "None."]

#### New runtime dependencies

| Dependency | Version | What it replaces | What was rejected, and why |
|---|---|---|---|
| pydantic | 2.9 | ~200 lines of hand-rolled source validation with worse errors | stdlib dataclasses + manual checks |

[If there were none: "None."]

#### Deferred doc updates applied

[The spec's `Related doc updates once implemented` section, discharged now.]

- `docs/explanation/configuration.md` — env precedence documented. Done.

[If the section was empty: "None pending."]
```

---

## Rules

- **Evidence, not claims.** "Tests failed first" is a claim; the pasted failure
  output is evidence. Paste it.
- **Failures stay visible.** A gate that failed is recorded as failed, with its
  output. Rewriting this section to look clean defeats the only purpose it has.
- **Deviations are mandatory reading for the next stage.** A deviation that changed
  the Interface means every spec pinning this component is now stale — say so here
  and pass `--stale` on the bump.
- **One block per implementation pass.** Re-implementations append a new dated
  block; the history is the point.
