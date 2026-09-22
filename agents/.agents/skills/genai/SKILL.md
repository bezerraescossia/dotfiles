---
name: genai
description: Run the GenAI Delivery Framework (CRISP-ML(Q)-based, phases 01–06) on a project, one task at a time. Each task has a role -- HUMAN (AI prepares a kit, the user does the fieldwork, AI turns their raw notes into the artifact and reviews it against the task's rules, the user approves), DECISION (AI writes a brief with options and a labeled recommendation, the user decides, it goes to the decision log), or AI. State lives in the project's .genai/ and is enforced by scripts/check.py, which refuses any transition past unmet dependencies or a pending decision. Use when the user runs /genai, or asks to start, continue, or check a GenAI project with this framework ("next task", "where are we", "kick off the project"). All six phases are executable; when the pipeline is finished the project moves to `operating` and the work continues as recurring cycles.
argument-hint: "init | status | next [task-id] | skip <task-id> \"<reason>\" | cycle start|list|close"
---

# /genai

Runs the framework in `phases/` (next to this file) as a pipeline. **The phase files are the playbooks.** Each task's fenced `yaml task` block holds its id, role, dependencies, estimate and artifact. Its prose sections say what to do:
- HUMAN tasks: *AI prepares / You do / AI turns into / Review rules / Done when*
- AI tasks: *Plan / Build / AI writes / Review rules / Done when*
- DECISION tasks: *Brief / Options / Decision record*

Read the task's section fresh every time you work on it. Don't work from memory.

All six phase files carry task blocks, so all six are executable. Phase 06 also carries fenced `yaml cycle` blocks: the recurring operations work that starts once the pipeline is finished.

## The checker

```bash
CHECK="uv run -q ~/.claude/skills/genai/scripts/check.py"
$CHECK status | next | check
$CHECK set <id> <status> [--hours N] [--reason "..."] [--cascade] [--tag NAME=yes|no]
$CHECK project active|stopped|operating|completed
$CHECK cycle list [--kinds] | start <kind> | close <file|kind> [--hours N]
```

- **Always change state through `$CHECK set` / `$CHECK project`. Never edit `state.yaml` by hand.**
- `set` validates the whole resulting state and **refuses to save** it if anything is wrong: an unmet dependency, a pending DECISION upstream, a missing artifact, a missing decision-log entry, or a skip with no reason. A refusal is the pipeline working. Report it, and fix the cause. Never work around it.
- A task absent from `state.yaml` is `todo`.
- `project operating` is refused while any task is unfinished. It is the consequence of 06.10, not a shortcut past the pipeline.

Statuses:
- HUMAN: `todo → prepared → in-progress → review → done` (review → in-progress when changes are needed, `skipped` with a reason)
- AI: the same chain, read as `plan → build → review`. An AI task can't go straight from `in-progress` to `skipped` — reopen it to `todo` first.
- DECISION: `todo → prepared → done`. A DECISION can never be skipped.
- Any task can be reopened to `todo`. Use `--cascade` to reset the tasks that depend on it.

## Optional tags

Four tags mark work that only some projects need: `[R]` retrieval, `[A]` tools/agents, `[FT]` fine-tuning, `[SH]` self-hosted models. A tagged task applies only when its tag is on.

Each tag is settled by one DECISION, in the same call that closes it:

| Tag | Settled by | Call |
|---|---|---|
| `[R]` | 02.0 Handoff review & retrieval decision | `set 02.0 done --tag R=yes\|no` |
| `[A]` | 03.0 Handoff review & agentic scope | `set 03.0 done --tag A=yes\|no` |
| `[SH]` | 03.4b Choose primary & fallback | `set 03.4b done --tag SH=yes\|no` |
| `[FT]` | 03.9 Escalation gate: fine-tune or not | `set 03.9 done --tag FT=yes\|no` |

Until the tag is settled, its tasks are blocked. When it is off, they show as `n/a`, the checker refuses to start them, and you don't skip them by hand. Items marked `[R]`, `[A]`, `[FT]` or `[SH]` **inside** an untagged task work the same way: leave them out and say so in the artifact.

## Project layout

```
.genai/
├── state.yaml        # written only by check.py
├── decisions.md      # decision log, one "## <id> — <title> (date)" entry per DECISION
├── artifacts/<phase>/  # <id>-prep.md, <id>-plan.md, <id>-brief.md, approved artifacts
├── ops/              # <date>-<kind>.md, one per cycle run (Phase 06, written by check.py)
├── inbox/            # the user's raw notes/transcripts — git-ignored
└── .gitignore        # contains inbox/
```

---

## `init`

1. If `.genai/state.yaml` exists, say so and run `status` instead.
2. Ask for the project name and the size with `AskUserQuestion`:
   - **S**: single team, one workflow, ~1–2 week engagement
   - **M-L**: several teams or workflows, regulated data, integrations
3. `$CHECK init --name "<name>" --size <S|M-L>`
4. Tell the user that `.genai/inbox/` is git-ignored because raw notes are often sensitive, and that the rest of `.genai/` is meant to be committed. Then offer `next`.

## `status`

Run `$CHECK status`. Summarize in a few lines: tasks done/total, estimated vs actual hours, what is active, what is blocked and by what (especially pending DECISIONs), and what is ready.

## `skip <id> "<reason>"`

`$CHECK set <id> skipped --reason "<reason>"`. Skipping is for tasks that don't apply, e.g. optional-tag tasks. If the user wants to skip a DECISION, refuse and explain why: decisions are the gates.

## `next [id]`

**Resolve the target.**
- With an id, use it.
- Without one, run `$CHECK next`:
  - one `ACTIVE` task: continue it
  - several `ACTIVE` tasks: ask which one
  - none active: take the first `READY` task, but say which other tasks are also ready (e.g. 01.1 and 01.2 can run in parallel)
  - nothing ready: say why, from `status`

**Then advance that task by one stage of its loop:**

### HUMAN task

| Current status | Do this | Then |
|---|---|---|
| `todo` | **Prepare.** Read the task's *AI prepares* section, every approved artifact it builds on, and any context in `inbox/`. If context the kit needs is missing, ask for it first. Write `artifacts/<phase>/<id>-prep.md`: practical material the user will actually take into a meeting (agendas, interview guides, questions, checklists, draft tables with `GAP` marks). | `set <id> prepared`. Show a short summary of the kit and the *You do* list, and tell the user to drop notes in `.genai/inbox/` and run `/genai next` when done. |
| `prepared` | Ask whether they have started or finished the fieldwork. If notes are already in `inbox/`, go straight on to the `in-progress` row. | `set <id> in-progress` |
| `in-progress` | **Turn the notes into the artifact.** Read the relevant new files in `inbox/`. If there are none, say you're waiting and stop. Write the artifact(s) named in the task block, following *AI turns into* and the phase file's templates. **Every fact must trace to the notes or to an approved artifact.** Where they don't cover something, write `GAP: <what is missing>` instead of filling it in. Start each artifact with a header: task id, date, sources used (inbox file names), status `draft`. Then **review** the draft against every *Review rules* item. | `set <id> review`. Present the review as a pass/fail list per rule, plus the `GAP`s. |
| `review` | The user approves, or asks for changes. **Changes** that can be made from the notes: edit the artifact and review it again. Changes that need **new fieldwork**: `set <id> in-progress`. **Approval** must be explicit. Any open `GAP` must either be resolved, or accepted by the user and moved into a `Known gaps` section. Set the artifact header status to `approved`. Ask for the actual hours spent (optional). | `set <id> done [--hours N]`. Report what is now unblocked. |

### DECISION task

| Current status | Do this | Then |
|---|---|---|
| `todo` | **Brief.** Write `artifacts/<phase>/<id>-brief.md` following the task's *Brief* section. Every claim cites the artifact it comes from. List the *Options*, each with its consequences. End with **AI recommendation: `<option>`** and the reasoning, labeled as the AI's view. | `set <id> prepared`. Put the decision to the user with `AskUserQuestion`, one option per choice, with your recommendation first and marked. |
| `prepared` | **Record.** Add a `## <id> — <title> (date)` entry to `decisions.md` using the template in that file: the decision, the options, whether the AI recommendation was followed, the rationale **in the user's words**, evidence, conditions, and who decided. Then `set <id> done`, with `--tag NAME=yes\|no` when this decision settles an optional tag. | **Only after that**, apply the consequences in the task's *Decision record* section: <br>• **stop / not GenAI**: `project stopped` <br>• **loop back to task X**: `set X todo --cascade`. This also resets this decision, and a new log entry is appended when it is decided again <br>• **06.10 start operations**: `project operating`. The pipeline is done, and the work continues as cycles <br>• **retire**: `project completed` |

### AI task

The AI does the work; the user reviews it. **Code, queries, dashboards and pipelines go in the project repo**, not in `.genai/`. The artifact is the record: the paths, the commands run, and the measured results.

| Current status | Do this | Then |
|---|---|---|
| `todo` | **Plan.** Read the task's *Plan* section and every approved artifact it builds on. Write `artifacts/<phase>/<id>-plan.md`: what will be built, where in the repo, how it will be tested, and what you need from the user (access, credentials, a sample, a decision). If something needed is missing, ask before planning around it. | `set <id> prepared`. Show the plan and ask for approval before building. |
| `prepared` | The user approves the plan, or corrects it. Rewrite the plan if they correct it, and ask again. | `set <id> in-progress` once they approve. |
| `in-progress` | **Build.** Work through the *Build* checklist, skipping any item whose tag is off and saying so. Then write the artifact(s) named in the task block, following *AI writes*. **Every number in the artifact comes from a run you actually did** — a measurement you didn't take is a `GAP`, never an estimate presented as a result. Then **review** the draft against every *Review rules* item. | `set <id> review`. Present the review as a pass/fail list per rule, plus the `GAP`s, plus what you built and where. |
| `review` | The user approves, or asks for changes. **Changes**: `set <id> in-progress`, build again, review again. **Approval** must be explicit. Any open `GAP` must be resolved or accepted and moved into a `Known gaps` section. Set the artifact header status to `approved`. | `set <id> done [--hours N]`. Report what is now unblocked. |

After **every** state change, `set` has already validated the state. Finish by showing a one-line status for the task and what's next.

---

## `cycle start|list|close`

Once 06.10 has moved the project to `operating`, the pipeline is finished and the recurring work runs as **cycles**, defined by the `yaml cycle` blocks in `06-monitoring-maintenance.md`: `monthly`, `quarterly`, `migration`, `change`, `incident`.

- **`cycle list`** — the runs so far, open and closed. `--kinds` lists the available kinds instead.
- **`cycle start <kind>`** — `$CHECK cycle start <kind>` copies that cycle's checklist into `.genai/ops/<date>-<kind>.md` with `## Findings` and `## Actions & loop-backs` sections. Then work the checklist with the user, reading Phase 06 fresh for each item, and write what you find into that file. One open cycle per kind; the checker refuses a second.
- **`cycle close <file|kind>`** — `$CHECK cycle close <file> [--hours N]` once the findings and the actions are recorded.

**Cycles never change the task graph.** Every action found in a cycle routes through the 06.8 loop-back table:
- A fix that an earlier phase owns runs as a **`change` cycle**: the owning phase's work → the 04.11 regression suite → the 05.7 release pipeline.
- Only a real **re-frame** (a new slice, a changed outcome) reopens the pipeline: `project active`, then `set <task> todo --cascade`.
- A **new use case** is a new Phase 01, in its own `.genai/`, not a widened scope here.

---

## Hard rules

1. **Never invent fieldwork.** An artifact contains only what the user's notes or approved artifacts support. Anything missing becomes a `GAP`, never a plausible default.
2. **Never mark a task done without explicit approval** of that artifact or decision in this conversation.
3. **Never make a DECISION for the user.** Recommend, clearly labeled. The decision and its rationale are theirs.
4. **Never bypass the checker.** No hand edits to `state.yaml`, and no workarounds for a refusal.
5. **Inbox content stays in `.genai/`.** Don't copy raw notes into commits, other files, or external tools. Artifacts summarize. They don't paste transcripts.
6. **One task, one stage per `next`.** Don't chain several tasks in one run, even when it would be quick.
7. **Never fake a measurement.** An AI task's artifact reports results from runs that actually happened. An untested build is not `review`-ready.
8. **Never widen an operating project.** A cycle finding becomes a `change` cycle or a re-frame, never an unlogged edit to production or to the task graph.

## Failure modes

| Failure | What it looks like | Required behavior |
|---|---|---|
| Guessed fieldwork | The workflow map lists steps nobody observed or reported. | Only notes-backed content. Everything else is `GAP` or labeled `inference`. |
| Recommendation passed off as a decision | "We'll continue with GenAI" written into decisions.md without the user choosing. | Put the options to the user. Record their choice and their words. |
| A generic prep kit | An interview guide that could belong to any project. | Build the kit from this project's approved artifacts and context. Ask for context if there is none. |
| Skipping the review | The draft is presented without checking the *Review rules*. | Show the rule-by-rule pass/fail list every time. |
| Silent approval | The status moves to done because the user said "looks fine" about something else. | Ask explicitly: "Approve `<artifact>`?" |
| Working around a refusal | `set` refuses, and the state is edited by hand. | Report the violation and fix its cause (artifact, decision entry, dependency). |
| Raw notes leaking | Transcript passages pasted into artifacts or commits. | Summarize, and cite the inbox file name. |
| Running ahead | Preparing 01.4 while 01.3b is pending, "to save time". | The checker blocks it, and so should you. Pending decisions gate everything after them. |
| Reported, not run | An AI task's artifact gives a latency or a judge score that was estimated, not measured. | Run it, or write `GAP`. Numbers trace to a command in the artifact. |
| Tagged work done anyway | Building the retrieval tasks before 02.0 settled `[R]`, or while it is off. | The tag gates them. Settle it with the DECISION, and leave `n/a` tasks alone. |
| A cycle that edits production | An incident "fixed" by changing the prompt outside the pipeline. | Kill switch or rollback, then a `change` cycle through regression and the release pipeline. |
