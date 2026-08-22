---
name: python-project-init
description: Scaffold a new Python project from the default python-default Copier template (uv, monolith src/ layout, ruff, mypy, pytest, taskipy, pre-commit, git guardrails).
user_invocable: true
---

# Python Project Init Skill

Scaffold a brand-new Python project from the standalone Copier template at
`~/.templates/python-default`, then activate the tooling it ships with.

The template itself has no Claude Code dependency — it can be rendered with
plain `copier copy` from any shell. This skill is a thin wrapper: it collects
the answers, runs Copier, then finishes the setup steps that are naturally
interactive (installing deps, installing git hooks, verifying everything
works).

## Use When

- Starting a brand-new Python project/library from scratch
- The project needs the full stack: uv, ruff, mypy, pytest, pre-commit, CI

Not for retrofitting hooks onto an existing project — use
`Skill(pre-commit-setup)` for that instead.

## Workflow

### 1. Collect answers

Ask the user (or infer sensible defaults from context) for:

- `project_name` — human-readable name
- `description` — one-line description
- `python_version` — defaults to `3.13`

`project_slug`, `author_name`, and `author_email` all have working defaults
in `copier.yml` (derived from `project_name`, or from the user's git config)
— only ask about them if the derived value looks wrong.

### 2. Render the template

```bash
copier copy ~/.templates/python-default <destination-dir>
```

If scaffolding into the current (already-created, e.g. via `gh repo create`)
directory:

```bash
copier copy ~/.templates/python-default .
```

Copier prompts interactively for any answer not passed with `--data`. To
pass answers non-interactively:

```bash
copier copy ~/.templates/python-default . \
  --data project_name="My Project" \
  --data description="What it does" \
  --data python_version="3.13"
```

### 3. Install dependencies and activate hooks

```bash
uv sync
uv run pre-commit install
```

### 4. Verify

```bash
uv run task check          # lint + typecheck + test
uv run pre-commit run --all-files
```

## What the Template Includes

- **uv** for dependency and Python-version management (`.python-version`,
  `pyproject.toml` with `[dependency-groups] dev`); `[tool.uv] package = false`
  since this is a monolith, not a single distributable package
- **`src/` as a monolith container** — one directory per initiative/epic
  (e.g. `src/corrective-rag/`), not a single `src/<package_name>/`; see
  `src/README.md` in the generated project
- **ruff** (expanded rule set: `E, F, I, UP, B, SIM`) for lint + format
- **mypy** (default/non-strict mode) for type checking
- **pytest** + **pytest-cov** for testing
- **taskipy** shortcuts (`uv run task <name>`): `test`, `test-cov`, `lint`,
  `format`, `typecheck`, `check`, `precommit`
- **pre-commit** config wired to the hooks above
- **GitHub Actions** CI (`.github/workflows/ci.yml`) running pre-commit +
  tests on push/PR
- **`.claude/settings.json`** with a `PreToolUse` hook
  (`.claude/hooks/block-dangerous-git.sh`) blocking destructive git commands
  (`push --force`, `reset --hard`, `clean -f`/`-fd`, `branch -D`,
  `checkout .`/`restore .`) — plain `git push` is still allowed
- `README.md`, `.gitignore`, `.editorconfig` — no `LICENSE` (add the right
  one per-project) and no `git init` (assumes the repo already exists)

## Updating the Template Later

Because this is Copier (not Cookiecutter), changes made to
`~/.templates/python-default` after a project was generated can be
backported into that project with:

```bash
copier update
```

run from inside the generated project (requires the project's `.copier-answers.yml`,
which Copier writes automatically on the initial `copier copy`).

## Related Skills

- `Skill(pre-commit-setup)` — add/update pre-commit hooks on an existing project
