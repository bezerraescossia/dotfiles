---
name: sdd-plan
description: Generates the technical implementation plan (stack, architecture, project structure) for a feature from its spec and the project constitution, at specs/NNN-feature/plan.md.
user_invocable: true
---

# Implementation Plan Generator (Technical Plan)

This skill guides Claude to act as a Senior Software Architect. The goal is to turn a feature specification (what/why) into a concrete technical plan (stack, dependencies, project structure), validated against the project's non-negotiable constitution.

**Position in the SDD pipeline**: Specify → Clarify (optional) → **Plan** → Checklist (optional) → Tasks. Required input: `specs/NNN-feature/spec.md` and `docs/constitution.md`. Output: `specs/NNN-feature/plan.md` plus, when relevant, `research.md`, `data-model.md`, `contracts/`, and `quickstart.md` in the same directory — consumed next by `sdd-tasks`.

---

## Step 1: Load Context

1. Identify the feature: if the user doesn't specify one, look in `specs/` for the most recent directory without a `plan.md`, or ask.
2. Read `specs/NNN-feature/spec.md` (required — without it, stop and ask the user to run `sdd-specify` first).
3. Read `docs/constitution.md` (required for the Constitution Check). If it doesn't exist, warn the user there's no governance gate defined and suggest running `sdd-constitution`; you may proceed without it, but say so explicitly in the plan.

## Step 2: Fill the Technical Context

Fill every Technical Context field with real evidence, never assumption — the same fidelity-to-evidence rule used across this pipeline:

- Where a stack already exists (dependency manifests, an existing directory tree), inspect it directly (`package.json`, `pyproject.toml`/`requirements.txt`, `go.mod`, `Cargo.toml`, `pom.xml`/`build.gradle`, etc.) and treat what you find as binding, not optional.
- Where no stack is decided yet, whatever the constitution already fixes as a technology constraint is binding. For the rest, ask the user directly (via `AskUserQuestion` or short question blocks) — don't choose the stack unilaterally.
- Anything still open after asking becomes an explicit `NEEDS CLARIFICATION` in the document — never a silent assumption.

## Step 3: Generate `plan.md`

Write `specs/NNN-feature/plan.md` following this structure (based on spec-kit's `plan-template.md`):

```markdown
# Implementation Plan: [FEATURE]

**Branch**: `[NNN-feature-name]` | **Date**: [DATE] | **Spec**: specs/NNN-feature/spec.md

## Summary

[Primary requirement extracted from the spec + technical approach in 2-3 sentences]

## Technical Context

**Language/Version**: [...]
**Primary Dependencies**: [...]
**Storage**: [...or N/A]
**Testing**: [...]
**Target Platform**: [...]
**Project Type**: [single project / web app / mobile+api / cli / lib / other]
**Performance Goals**: [...or NEEDS CLARIFICATION]
**Constraints**: [...or NEEDS CLARIFICATION]
**Scale/Scope**: [...or NEEDS CLARIFICATION]

## Constitution Check

*Gate: must pass before detailing the project structure below.*

| Principle (docs/constitution.md) | Assessment | Note |
|---|---|---|
| [Principle name] | Pass / Violation | [justification if Violation] |

If any `Violation` lacks an acceptable justification, **do not proceed** — go back to the spec or the technical design until it's resolved, or record the exception in Complexity Tracking below with explicit rationale.

## Project Structure

### Documentation (this feature)

```text
specs/NNN-feature/
├── plan.md
├── spec.md
├── research.md      # if any NEEDS CLARIFICATION item needs resolving
├── data-model.md     # if the feature involves meaningful data entities
├── contracts/         # if the feature exposes an interface to users or other systems
├── quickstart.md      # runnable validation scenarios proving the feature works end-to-end
└── tasks.md           # generated later by sdd-tasks
```

### Source Code (repository root)

[The REAL, concrete directory tree — never leave generic labels like "Option 1/2/3" in the final result. In an existing codebase, reflect the layout already in place; in a new one, use the layout decided in the Technical Context.]

**Structure Decision**: [1-2 sentences justifying the chosen structure]

## Complexity Tracking

> Fill in ONLY if the Constitution Check recorded a violation above.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|---------------------------------------|
| [...] | [...] | [...] |
```

## Step 4: Phase 0 — Research (conditional)

If any `NEEDS CLARIFICATION` remains in the Technical Context, generate `research.md`:

1. For each unknown, dispatch a research task ("Research {unknown} for {feature context}"); for each technology choice, a best-practices task ("Find best practices for {tech} in {domain}").
2. Consolidate findings using the format: `Decision` / `Rationale` / `Alternatives considered`.

The final `plan.md` must not contain any `NEEDS CLARIFICATION` without a corresponding resolved entry here.

## Step 5: Phase 1 — Design & Contracts (conditional)

Prerequisite: `research.md` complete (if it was needed).

1. **`data-model.md`**: if the spec has a non-trivial "Key Entities" section, extract entity names, fields, relationships, and validation/state-transition rules derived from the functional requirements.
2. **`contracts/`**: if the project exposes an interface to users or other systems (public API for a library, command schema for a CLI, endpoints for a web service, a grammar for a parser, a UI contract for an app), document it in the format appropriate to the project type. Skip for purely internal projects (build scripts, one-off tools).
3. **`quickstart.md`**: a runnable validation guide proving the feature works end-to-end — prerequisites, setup commands, run/test commands, expected outcomes. Reference `contracts/` and `data-model.md` instead of duplicating them. Do not include full implementation code or complete test suites — that belongs in `tasks.md` and the implementation phase itself.

## Step 6: Closing

Report to the user: the `plan.md` path, the Constitution Check result (pass/violations), any auxiliary artifacts generated, and the suggested next step (`sdd-checklist` if a requirements-quality pass on a specific domain is warranted, otherwise `sdd-tasks` to break the plan into actionable tasks).
