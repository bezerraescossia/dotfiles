# Spec-Driven Development (SDD) Pipeline

Eight skills that take a project — new or existing — from "no formal spec" to "implemented feature," mirroring [github/spec-kit](https://github.com/github/spec-kit)'s actual command set (`/speckit.constitution`, `/speckit.specify`, `/speckit.clarify`, `/speckit.plan`, `/speckit.checklist`, `/speckit.tasks`, `/speckit.analyze`, `/speckit.implement`).

spec-kit itself has no separate brownfield/greenfield pipeline — "Iterative Enhancement" (brownfield) is just the same commands run again against an existing codebase, not a different flow. These skills follow that: there's one pipeline, and `sdd-constitution`/`sdd-plan` simply use whatever real evidence the repository already offers (existing code, config, conventions) instead of asking the user to redecide it, falling back to direct questions only for what can't be inferred.

## Directory conventions

- `docs/constitution.md` — the project's governance principles, global, persists across features.
- `specs/NNN-feature-name/` — documents for one specific feature:
  - `spec.md`, `plan.md`, `tasks.md`, and, when relevant, `research.md` / `data-model.md` / `contracts/` / `quickstart.md`
  - `checklists/requirements.md` (built-in spec-quality checklist) and `checklists/[domain].md` (custom, reviewer-owned)

## Pipeline

```
sdd-constitution → sdd-specify → sdd-clarify → sdd-plan → sdd-checklist → sdd-tasks → sdd-analyze → sdd-implement
                                  (optional)                (optional)                (optional)
```

1. **sdd-constitution** establishes (or amends) the project's non-negotiable governance principles → `docs/constitution.md`. Runs first; everything downstream must comply with it.
2. **sdd-specify** turns a natural-language feature description into a structured spec (what/why, no tech stack) → `specs/NNN-feature/spec.md`.
3. **sdd-clarify** *(optional but recommended)* asks up to 5 targeted questions to resolve ambiguity in the spec before planning starts, and writes the answers back into it.
4. **sdd-plan** defines the feature's stack and architecture, validated against the constitution → `specs/NNN-feature/plan.md` (+ `research.md`/`data-model.md`/`contracts/`/`quickstart.md` as needed).
5. **sdd-checklist** *(optional, can run any time after step 2)* generates a domain-specific "unit tests for English" checklist — validates requirement quality, not implementation.
6. **sdd-tasks** breaks the plan into dependency-ordered, per-user-story tasks → `specs/NNN-feature/tasks.md`.
7. **sdd-analyze** *(optional, read-only)* cross-checks spec/plan/tasks for inconsistencies, gaps, and constitution violations before implementation starts.
8. **sdd-implement** executes `tasks.md` phase by phase, checking off completed tasks, and produces the actual code.

## Skills

| Skill | Reads | Writes |
|---|---|---|
| `sdd-constitution` | repo context (code, configs, README) if available | `docs/constitution.md` |
| `sdd-specify` | `docs/constitution.md`, natural-language description | `specs/NNN-feature/spec.md`, `specs/NNN-feature/checklists/requirements.md` |
| `sdd-clarify` | `specs/NNN-feature/spec.md` | same file, updated in place |
| `sdd-plan` | `specs/NNN-feature/spec.md`, `docs/constitution.md` | `specs/NNN-feature/plan.md` (+ optional `research.md`/`data-model.md`/`contracts/`/`quickstart.md`) |
| `sdd-checklist` | `specs/NNN-feature/{spec,plan,tasks}.md` | `specs/NNN-feature/checklists/[domain].md` |
| `sdd-tasks` | `specs/NNN-feature/plan.md`, `specs/NNN-feature/spec.md` | `specs/NNN-feature/tasks.md` |
| `sdd-analyze` | `specs/NNN-feature/{spec,plan,tasks}.md`, `docs/constitution.md` | nothing (read-only report) |
| `sdd-implement` | `specs/NNN-feature/tasks.md` and all other feature artifacts | source code, `specs/NNN-feature/tasks.md` (checkbox state) |
