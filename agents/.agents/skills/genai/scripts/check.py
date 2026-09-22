#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""State checker for the /genai pipeline.

Task definitions come from the fenced ```yaml task blocks in ../phases/*.md,
recurring operations checklists from the ```yaml cycle blocks in the same files.
Project state lives in <project>/.genai/state.yaml.

    uv run check.py init --name "Acme claims" --size S
    uv run check.py check                  # exit 1 on any violation
    uv run check.py status                 # graph, blockers, estimated vs actual
    uv run check.py next                   # active + unblocked tasks, in default order
    uv run check.py set 01.0 prepared      # move a task (transition + deps enforced)
    uv run check.py set 01.0 done --hours 2.5
    uv run check.py set 02.0 done --tag R=no   # a DECISION that settles an optional tag
    uv run check.py set 01.2 skipped --reason "workflow already documented in X"
    uv run check.py set 01.1 todo --cascade   # reopen; resets done dependants to todo
    uv run check.py project stopped        # active | stopped | operating | completed
    uv run check.py cycle start monthly    # recurring ops work, once the project operates
    uv run check.py cycle list
    uv run check.py cycle close ops/2026-09-19-monthly.md --hours 3
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).resolve().parent.parent
PHASES_DIR = SKILL_DIR / "phases"
TEMPLATES_DIR = SKILL_DIR / "templates"

ROLES = {"HUMAN", "AI", "DECISION"}
SIZES = {"S", "M-L"}
PROJECT_STATUSES = {"active", "stopped", "operating", "completed"}
ACTIVE = {"prepared", "in-progress", "review"}
SATISFIED = {"done", "skipped"}
# A task whose optional tag was decided "no" is not applicable to this project.
NOT_APPLICABLE = "n/a"

# Allowed transitions per role. Any task may also be reopened to "todo".
TRANSITIONS = {
    "HUMAN": {
        "todo": {"prepared", "skipped"},
        "prepared": {"in-progress", "skipped"},
        "in-progress": {"review", "skipped"},
        "review": {"done", "in-progress"},
        "done": set(),
        "skipped": set(),
    },
    "AI": {
        "todo": {"prepared", "skipped"},
        "prepared": {"in-progress", "skipped"},
        "in-progress": {"review"},
        "review": {"done", "in-progress"},
        "done": set(),
        "skipped": set(),
    },
    "DECISION": {
        "todo": {"prepared"},
        "prepared": {"done"},
        "done": set(),
    },
}

TASK_BLOCK = re.compile(r"^```yaml task\s*\n(.*?)^```", re.MULTILINE | re.DOTALL)
# A cycle block is followed by the checklist it copies into the ops file, running to the
# next heading, the next cycle block, or a horizontal rule — whichever comes first.
CYCLE_BLOCK = re.compile(
    r"^```yaml cycle\s*\n(.*?)^```\n(.*?)(?=^#{1,6} |^```yaml cycle\s*$|^---\s*$|\Z)",
    re.MULTILINE | re.DOTALL,
)


@dataclass
class Task:
    id: str
    title: str
    role: str
    depends_on: list[str]
    estimate: dict[str, float]
    artifacts: list[str]
    optional_tag: str | None
    sets_tags: list[str]  # optional tags this DECISION settles
    phase: str  # phase file stem, e.g. "01-business-understanding"
    order: int


@dataclass
class Cycle:
    kind: str
    title: str
    estimate: dict[str, float]
    checklist: str


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)

    def add(self, msg: str) -> None:
        self.errors.append(msg)


# ---------------------------------------------------------------- loading


def load_tasks() -> tuple[dict[str, Task], list[str], Report]:
    """Parse every task block. Returns tasks, non-executable phase stems, and definition errors."""
    rep = Report()
    tasks: dict[str, Task] = {}
    not_executable: list[str] = []
    order = 0
    for path in sorted(PHASES_DIR.glob("*.md")):
        blocks = TASK_BLOCK.findall(path.read_text(encoding="utf-8"))
        if not blocks:
            not_executable.append(path.stem)
            continue
        for raw in blocks:
            try:
                d = yaml.safe_load(raw)
            except yaml.YAMLError as e:
                rep.add(f"{path.name}: invalid task YAML: {e}")
                continue
            tid = str(d.get("id", ""))
            if not tid:
                rep.add(f"{path.name}: task block without id")
                continue
            if tid in tasks:
                rep.add(f"{path.name}: duplicate task id {tid}")
                continue
            role = d.get("role")
            if role not in ROLES:
                rep.add(f"{tid}: role must be one of {sorted(ROLES)}, got {role!r}")
            art = d.get("artifact")
            artifacts = [] if art is None else ([art] if isinstance(art, str) else list(art))
            if role in {"HUMAN", "AI"} and not artifacts:
                rep.add(f"{tid}: {role} task must declare an artifact")
            est = d.get("estimate") or {}
            sets = d.get("sets_tags") or []
            sets = [sets] if isinstance(sets, str) else [str(x) for x in sets]
            if sets and role != "DECISION":
                rep.add(f"{tid}: only a DECISION may set tags, got {role}")
            tasks[tid] = Task(
                id=tid,
                title=str(d.get("title", "")),
                role=role,
                depends_on=[str(x) for x in d.get("depends_on") or []],
                estimate={k: float(v) for k, v in est.items()},
                artifacts=artifacts,
                optional_tag=d.get("optional_tag"),
                sets_tags=sets,
                phase=path.stem,
                order=order,
            )
            order += 1
    for t in tasks.values():
        for dep in t.depends_on:
            if dep not in tasks:
                rep.add(f"{t.id}: depends on unknown task {dep}")
    deciders = tag_deciders(tasks)
    seen: dict[str, str] = {}
    for t in sorted(tasks.values(), key=lambda t: t.order):
        for tag in t.sets_tags:
            if tag in seen:
                rep.add(f"{t.id}: tag [{tag}] is already set by {seen[tag]}")
            seen[tag] = t.id
        if t.optional_tag and t.optional_tag not in deciders:
            rep.add(f"{t.id}: optional tag [{t.optional_tag}] has no DECISION that sets it")
    _check_cycles(tasks, rep)
    return tasks, not_executable, rep


def load_cycles() -> tuple[dict[str, Cycle], Report]:
    """Parse every ```yaml cycle block and the checklist that follows it."""
    rep = Report()
    cycles: dict[str, Cycle] = {}
    for path in sorted(PHASES_DIR.glob("*.md")):
        for raw, body in CYCLE_BLOCK.findall(path.read_text(encoding="utf-8")):
            try:
                d = yaml.safe_load(raw) or {}
            except yaml.YAMLError as e:
                rep.add(f"{path.name}: invalid cycle YAML: {e}")
                continue
            kind = str(d.get("kind", ""))
            if not kind:
                rep.add(f"{path.name}: cycle block without kind")
                continue
            if kind in cycles:
                rep.add(f"{path.name}: duplicate cycle kind {kind}")
                continue
            est = d.get("estimate") or {}
            cycles[kind] = Cycle(
                kind=kind,
                title=str(d.get("title", kind)),
                estimate={k: float(v) for k, v in est.items()},
                checklist=body.strip("\n"),
            )
    return cycles, rep


# ---------------------------------------------------------------- tags


def tag_deciders(tasks: dict[str, Task]) -> dict[str, str]:
    """tag -> id of the DECISION that settles it."""
    return {tag: t.id for t in sorted(tasks.values(), key=lambda t: t.order) for tag in t.sets_tags}


def tag_value(state: dict, tag: str) -> bool | None:
    return (state["project"].get("tags") or {}).get(tag)


def _check_cycles(tasks: dict[str, Task], rep: Report) -> None:
    state: dict[str, int] = {}

    def visit(tid: str, stack: list[str]) -> None:
        if state.get(tid) == 2 or tid not in tasks:
            return
        if state.get(tid) == 1:
            rep.add(f"dependency cycle: {' -> '.join(stack + [tid])}")
            return
        state[tid] = 1
        for dep in tasks[tid].depends_on:
            visit(dep, stack + [tid])
        state[tid] = 2

    for tid in tasks:
        visit(tid, [])


def genai_dir(root: Path) -> Path:
    return root / ".genai"


def load_state(root: Path) -> dict:
    path = genai_dir(root) / "state.yaml"
    if not path.exists():
        sys.exit(f"no {path} — run `init` first")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data.setdefault("project", {})
    data["project"].setdefault("tags", {})
    data["tasks"] = {str(k): (v or {}) for k, v in (data.get("tasks") or {}).items()}
    data["ops"] = list(data.get("ops") or [])
    return data


def save_state(root: Path, data: dict) -> None:
    path = genai_dir(root) / "state.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def status_of(state: dict, tid: str) -> str:
    return state["tasks"].get(tid, {}).get("status", "todo")


def eff_status(tasks: dict[str, Task], state: dict, tid: str) -> str:
    """Status, with a task whose optional tag was decided 'no' reported as n/a."""
    t = tasks.get(tid)
    if t and t.optional_tag and tag_value(state, t.optional_tag) is False:
        return NOT_APPLICABLE
    return status_of(state, tid)


# ---------------------------------------------------------------- checks


def unmet_deps(tasks: dict[str, Task], t: Task, state: dict) -> list[str]:
    return [
        d for d in t.depends_on
        if eff_status(tasks, state, d) not in SATISFIED | {NOT_APPLICABLE}
    ]


def blocker_text(tasks: dict[str, Task], state: dict, deps: list[str]) -> str:
    parts = []
    for d in deps:
        kind = "pending DECISION" if tasks[d].role == "DECISION" else status_of(state, d)
        parts.append(f"{d} ({kind})")
    return ", ".join(parts)


def tag_blocker(tasks: dict[str, Task], state: dict, t: Task) -> str | None:
    """Why this task cannot run yet because of its optional tag."""
    if not t.optional_tag:
        return None
    val = tag_value(state, t.optional_tag)
    decider = tag_deciders(tasks).get(t.optional_tag, "?")
    if val is None:
        return f"tag [{t.optional_tag}] undecided (set by {decider})"
    if val is False:
        return f"tag [{t.optional_tag}] is off — task is {NOT_APPLICABLE}"
    return None


def validate(root: Path, tasks: dict[str, Task], state: dict, rep: Report) -> None:
    proj = state["project"]
    if proj.get("size") not in SIZES:
        rep.add(f"project.size must be one of {sorted(SIZES)}, got {proj.get('size')!r}")
    pstatus = proj.get("status", "active")
    if pstatus not in PROJECT_STATUSES:
        rep.add(f"project.status must be one of {sorted(PROJECT_STATUSES)}, got {pstatus!r}")

    decisions = genai_dir(root) / "decisions.md"
    decisions_text = decisions.read_text(encoding="utf-8") if decisions.exists() else ""

    deciders = tag_deciders(tasks)
    for tag, val in (proj.get("tags") or {}).items():
        if tag not in deciders:
            rep.add(f"project.tags: unknown tag [{tag}] — no task sets it")
        elif not isinstance(val, bool):
            rep.add(f"project.tags[{tag}] must be true or false, got {val!r}")

    for tid, entry in state["tasks"].items():
        if tid not in tasks:
            rep.add(f"{tid}: in state.yaml but not an executable task")
            continue
        t = tasks[tid]
        st = entry.get("status", "todo")
        if st not in TRANSITIONS[t.role]:
            rep.add(f"{tid}: status {st!r} is not valid for a {t.role} task")
            continue
        if st != "todo":
            missing = unmet_deps(tasks, t, state)
            if missing:
                rep.add(f"{tid}: is {st} but blocked by {blocker_text(tasks, state, missing)}")
            blocked = tag_blocker(tasks, state, t)
            if blocked:
                rep.add(f"{tid}: is {st} but {blocked}")
        if st == "done" and t.role == "DECISION":
            for tag in t.sets_tags:
                if not isinstance(tag_value(state, tag), bool):
                    rep.add(f"{tid}: done but tag [{tag}] is not set — use `set {tid} done --tag {tag}=yes|no`")
        if st == "skipped" and not str(entry.get("skip_reason") or "").strip():
            rep.add(f"{tid}: skipped without a skip_reason")
        if st == "done" and t.role in {"HUMAN", "AI"}:
            for a in t.artifacts:
                p = genai_dir(root) / "artifacts" / t.phase / a
                if not p.exists():
                    rep.add(f"{tid}: done but artifact missing: {p.relative_to(root)}")
        if st == "done" and t.role == "DECISION":
            if not re.search(rf"^## {re.escape(tid)}\b", decisions_text, re.MULTILINE):
                rep.add(f"{tid}: DECISION done but no '## {tid}' entry in decisions.md")
        hours = entry.get("actual_hours")
        if hours not in (None, ""):
            try:
                float(hours)
            except (TypeError, ValueError):
                rep.add(f"{tid}: actual_hours must be a number, got {hours!r}")
        if pstatus in {"stopped", "operating"} and st in ACTIVE:
            rep.add(f"{tid}: is {st} but the project is {pstatus}")

    for c in state.get("ops") or []:
        f = str(c.get("file") or "")
        if not f:
            rep.add("ops: entry without a file")
        elif not (root / f).exists():
            rep.add(f"ops: {f} is recorded but missing")


# ---------------------------------------------------------------- commands


def cmd_init(args) -> int:
    root = Path(args.root)
    g = genai_dir(root)
    if (g / "state.yaml").exists():
        print(f"{g}/state.yaml already exists — not overwriting")
        return 1
    if args.size not in SIZES:
        print(f"--size must be one of {sorted(SIZES)}")
        return 1
    tasks, _, rep = load_tasks()
    _, crep = load_cycles()
    rep.errors.extend(crep.errors)
    if rep.errors:
        print("\n".join(rep.errors))
        return 1
    (g / "inbox").mkdir(parents=True, exist_ok=True)
    (g / "ops").mkdir(parents=True, exist_ok=True)
    for phase in sorted({t.phase for t in tasks.values()}):
        (g / "artifacts" / phase).mkdir(parents=True, exist_ok=True)
    shutil.copy(TEMPLATES_DIR / "decisions.md", g / "decisions.md")
    shutil.copy(TEMPLATES_DIR / "gitignore", g / ".gitignore")
    state = yaml.safe_load((TEMPLATES_DIR / "state.yaml").read_text(encoding="utf-8"))
    state["project"].update(
        name=args.name, size=args.size, status="active", created=dt.date.today().isoformat()
    )
    save_state(root, state)
    print(f"initialized {g} (size {args.size})")
    return cmd_next(args)


def cmd_check(args) -> int:
    root = Path(args.root)
    tasks, _, rep = load_tasks()
    _, crep = load_cycles()
    rep.errors.extend(crep.errors)
    state = load_state(root)
    validate(root, tasks, state, rep)
    if rep.errors:
        print(f"FAIL — {len(rep.errors)} violation(s):")
        for e in rep.errors:
            print(f"  - {e}")
        return 1
    print("OK")
    return 0


def _fmt_h(x: float | None) -> str:
    return "–" if x is None else f"{x:g}h"


def cmd_status(args) -> int:
    root = Path(args.root)
    tasks, not_exec, rep = load_tasks()
    state = load_state(root)
    proj = state["project"]
    size = proj.get("size")
    print(f"Project: {proj.get('name') or '(unnamed)'} · size {size} · status {proj.get('status', 'active')}")
    deciders = tag_deciders(tasks)
    if deciders:
        shown = []
        for tag, decider in deciders.items():
            val = tag_value(state, tag)
            shown.append(f"[{tag}] {'on' if val else 'off' if val is False else f'undecided ({decider})'}")
        print("Tags: " + " · ".join(shown))
    by_phase: dict[str, list[Task]] = {}
    for t in sorted(tasks.values(), key=lambda t: t.order):
        by_phase.setdefault(t.phase, []).append(t)
    for phase, ts in by_phase.items():
        print(f"\n## {phase}")
        print(f"{'Task':<7}{'Role':<10}{'Status':<13}{'Est':>6}{'Actual':>8}  Title / blocked by")
        est_total = act_total = 0.0
        for t in ts:
            entry = state["tasks"].get(t.id, {})
            st = eff_status(tasks, state, t.id)
            est = t.estimate.get(size) if size else None
            act = entry.get("actual_hours")
            act = float(act) if act not in (None, "") else None
            if st not in {"skipped", NOT_APPLICABLE} and est is not None:
                est_total += est
            if act is not None:
                act_total += act
            note = t.title
            if t.optional_tag:
                note += f"  [{t.optional_tag}]"
            missing = unmet_deps(tasks, t, state)
            if st == "todo" and missing:
                note += f"  ⛔ {blocker_text(tasks, state, missing)}"
            if st == "todo" and not missing:
                blocked = tag_blocker(tasks, state, t)
                if blocked:
                    note += f"  ⛔ {blocked}"
            if st == "skipped":
                note += f"  (skipped: {entry.get('skip_reason')})"
            if t.sets_tags:
                note += f"  → sets {', '.join(f'[{x}]' for x in t.sets_tags)}"
            print(f"{t.id:<7}{t.role:<10}{st:<13}{_fmt_h(est):>6}{_fmt_h(act):>8}  {note}")
        done = sum(1 for t in ts if eff_status(tasks, state, t.id) in SATISFIED | {NOT_APPLICABLE})
        print(f"{'':<30}{_fmt_h(est_total):>6}{_fmt_h(act_total):>8}  {done}/{len(ts)} tasks done")
    for phase in not_exec:
        print(f"\n## {phase} — not yet executable")
    open_cycles = [c for c in state["ops"] if not c.get("closed")]
    if state["ops"]:
        print(f"\n## operations — {len(state['ops'])} cycle(s), {len(open_cycles)} open")
        for c in state["ops"]:
            mark = "open " if not c.get("closed") else "closed"
            print(f"  {mark}  {c.get('kind','?'):<10} {c.get('file')}")
    validate(root, tasks, state, rep)
    if rep.errors:
        print(f"\n⚠ check fails with {len(rep.errors)} violation(s) — run `check`")
    return 0


def cmd_next(args) -> int:
    root = Path(args.root)
    tasks, not_exec, _ = load_tasks()
    state = load_state(root)
    pstatus = state["project"].get("status", "active")
    if pstatus == "operating":
        open_cycles = [c for c in state["ops"] if not c.get("closed")]
        print("project is operating — the task pipeline is done")
        for c in open_cycles:
            print(f"OPEN CYCLE  {c.get('kind')}  {c.get('file')}")
        if not open_cycles:
            print("no open cycle — start one with `cycle start <kind>` (see `cycle list --kinds`)")
        return 0
    if pstatus != "active":
        print(f"project is {pstatus} — nothing to do")
        return 0
    ordered = sorted(tasks.values(), key=lambda t: t.order)
    active = [t for t in ordered if eff_status(tasks, state, t.id) in ACTIVE]
    ready = [
        t for t in ordered
        if eff_status(tasks, state, t.id) == "todo"
        and not unmet_deps(tasks, t, state)
        and not tag_blocker(tasks, state, t)
    ]
    for t in active:
        print(f"ACTIVE  {t.id}  {t.role:<9} {status_of(state, t.id):<12} {t.title}")
    for t in ready:
        print(f"READY   {t.id}  {t.role:<9} {'todo':<12} {t.title}")
    if not active and not ready:
        if all(eff_status(tasks, state, t.id) in SATISFIED | {NOT_APPLICABLE} for t in ordered):
            msg = "all executable tasks are done"
            if not_exec:
                msg += f"; next phase ({not_exec[0]}) is not yet executable"
            print(msg)
        else:
            print("nothing unblocked — see `status`")
    return 0


def cmd_set(args) -> int:
    root = Path(args.root)
    tasks, _, rep = load_tasks()
    state = load_state(root)
    tid, new = args.task, args.status
    if tid not in tasks:
        print(f"unknown or non-executable task {tid}")
        return 1
    t = tasks[tid]
    cur = status_of(state, tid)
    if tag_value(state, t.optional_tag or "") is False:
        print(f"{tid}: {tag_blocker(tasks, state, t)} — nothing to do")
        return 1
    if new != "todo" and new not in TRANSITIONS[t.role].get(cur, set()):
        allowed = sorted(TRANSITIONS[t.role].get(cur, set()) | {"todo"})
        print(f"{tid} ({t.role}): {cur} → {new} not allowed; allowed: {allowed}")
        return 1
    if cur == "todo" and new != "todo":
        missing = unmet_deps(tasks, t, state)
        if missing:
            print(f"{tid}: blocked by {blocker_text(tasks, state, missing)}")
            return 1
        blocked = tag_blocker(tasks, state, t)
        if blocked:
            print(f"{tid}: {blocked}")
            return 1
        if state["project"].get("status", "active") != "active":
            print(f"project is {state['project'].get('status')} — cannot start tasks")
            return 1
    if new == "skipped" and not (args.reason or "").strip():
        print("skipping requires --reason")
        return 1

    tags = dict(state["project"].get("tags") or {})
    for raw in args.tag or []:
        name, _, val = raw.partition("=")
        name, val = name.strip(), val.strip().lower()
        if name not in t.sets_tags:
            print(f"{tid} does not set tag [{name}]; it sets {t.sets_tags or 'nothing'}")
            return 1
        if val not in {"yes", "no", "true", "false"}:
            print(f"--tag {name}=<yes|no>, got {val!r}")
            return 1
        tags[name] = val in {"yes", "true"}
    if new == "todo":
        for name in t.sets_tags:
            tags.pop(name, None)
    state["project"]["tags"] = tags

    today = dt.date.today().isoformat()
    entry = state["tasks"].setdefault(tid, {})
    entry["status"] = new
    if new == "todo":
        for k in ("started", "completed", "skip_reason"):
            entry.pop(k, None)
        if args.cascade:
            _reset_dependants(tasks, state, tid)
    else:
        entry.setdefault("started", today)
    if new in SATISFIED:
        entry["completed"] = today
    if args.hours is not None:
        entry["actual_hours"] = args.hours
    if args.reason:
        entry["skip_reason"] = args.reason
    if not _commit(root, tasks, state, rep):
        return 1
    print(f"{tid}: {cur} → {new}")
    for name in t.sets_tags:
        val = tag_value(state, name)
        print(f"  tag [{name}] → {'on' if val else 'off' if val is False else 'cleared'}")
    return 0


def _commit(root: Path, tasks: dict[str, Task], state: dict, rep: Report) -> bool:
    """Validate the proposed state; save it only if the whole state is valid."""
    validate(root, tasks, state, rep)
    if rep.errors:
        print(f"REFUSED — state not saved, {len(rep.errors)} violation(s):")
        for e in rep.errors:
            print(f"  - {e}")
        return False
    save_state(root, state)
    return True


def _reset_dependants(tasks: dict[str, Task], state: dict, tid: str) -> None:
    for t in tasks.values():
        if tid in t.depends_on and status_of(state, t.id) != "todo":
            entry = state["tasks"][t.id]
            entry["status"] = "todo"
            for k in ("started", "completed", "skip_reason"):
                entry.pop(k, None)
            print(f"  reset {t.id} → todo (depends on {tid})")
            _reset_dependants(tasks, state, t.id)


def cmd_project(args) -> int:
    root = Path(args.root)
    if args.status not in PROJECT_STATUSES:
        print(f"status must be one of {sorted(PROJECT_STATUSES)}")
        return 1
    tasks, _, rep = load_tasks()
    state = load_state(root)
    if args.status == "operating":
        left = [
            t.id for t in sorted(tasks.values(), key=lambda t: t.order)
            if eff_status(tasks, state, t.id) not in SATISFIED | {NOT_APPLICABLE}
        ]
        if left:
            print(f"cannot operate with {len(left)} unfinished task(s): {', '.join(left[:5])}…")
            return 1
    state["project"]["status"] = args.status
    if not _commit(root, tasks, state, rep):
        return 1
    print(f"project → {args.status}")
    return 0


# ---------------------------------------------------------------- cycles


def cmd_cycle(args) -> int:
    root = Path(args.root)
    cycles, rep = load_cycles()
    if rep.errors:
        print("\n".join(rep.errors))
        return 1
    state = load_state(root)
    tasks, _, trep = load_tasks()

    if args.action == "list":
        if args.kinds or not state["ops"]:
            for c in cycles.values():
                est = " · ".join(f"{k} {v:g}h" for k, v in c.estimate.items())
                print(f"{c.kind:<10} {c.title}{'  (' + est + ')' if est else ''}")
            if not state["ops"]:
                print("\nno cycle run yet")
            return 0
        for c in state["ops"]:
            hours = c.get("actual_hours")
            tail = f" · {hours}h" if hours not in (None, "") else ""
            mark = "open" if not c.get("closed") else f"closed {c['closed']}"
            print(f"{c.get('kind','?'):<10} {c.get('file'):<40} started {c.get('started')} · {mark}{tail}")
        return 0

    if args.action == "start":
        if state["project"].get("status") != "operating":
            print(f"project is {state['project'].get('status')} — cycles run only while operating")
            return 1
        if args.kind not in cycles:
            print(f"unknown cycle kind {args.kind!r}; known: {', '.join(sorted(cycles))}")
            return 1
        open_same = [c for c in state["ops"] if c.get("kind") == args.kind and not c.get("closed")]
        if open_same:
            print(f"{args.kind} cycle already open: {open_same[0]['file']} — close it first")
            return 1
        c = cycles[args.kind]
        today = dt.date.today().isoformat()
        ops = genai_dir(root) / "ops"
        ops.mkdir(parents=True, exist_ok=True)
        path = ops / f"{today}-{args.kind}.md"
        n = 2
        while path.exists():
            path = ops / f"{today}-{args.kind}-{n}.md"
            n += 1
        size = state["project"].get("size")
        est = c.estimate.get(size)
        path.write_text(
            f"# {c.title} — {today}\n\n"
            f"kind: {c.kind}  ·  estimate: {_fmt_h(est)}  ·  status: open\n\n"
            f"{c.checklist}\n\n## Findings\n\n## Actions & loop-backs\n",
            encoding="utf-8",
        )
        rel = str(path.relative_to(root))
        state["ops"].append({"kind": c.kind, "file": rel, "started": today, "closed": None})
        if not _commit(root, tasks, state, trep):
            return 1
        print(f"{c.kind} cycle started: {rel}")
        return 0

    # close
    target = args.kind
    matches = [c for c in state["ops"] if not c.get("closed") and (c.get("file") == target or Path(c.get("file", "")).name == Path(target).name or c.get("kind") == target)]
    if not matches:
        print(f"no open cycle matching {target!r}")
        return 1
    if len({c["file"] for c in matches}) > 1:
        print("several open cycles match; pass the file path")
        return 1
    c = matches[0]
    c["closed"] = dt.date.today().isoformat()
    if args.hours is not None:
        c["actual_hours"] = args.hours
    if not _commit(root, tasks, state, trep):
        return 1
    print(f"closed {c['file']}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", default=".", help="project root containing .genai/ (default: .)")
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init")
    i.add_argument("--name", required=True)
    i.add_argument("--size", required=True, choices=sorted(SIZES))
    sub.add_parser("check")
    sub.add_parser("status")
    sub.add_parser("next")
    s = sub.add_parser("set")
    s.add_argument("task")
    s.add_argument("status")
    s.add_argument("--hours", type=float)
    s.add_argument("--reason")
    s.add_argument("--cascade", action="store_true", help="when reopening, reset dependants to todo")
    s.add_argument("--tag", action="append", metavar="NAME=yes|no",
                   help="settle an optional tag this DECISION owns (repeatable)")
    pr = sub.add_parser("project")
    pr.add_argument("status")
    c = sub.add_parser("cycle")
    c.add_argument("action", choices=["start", "close", "list"])
    c.add_argument("kind", nargs="?", help="cycle kind, or the ops file when closing")
    c.add_argument("--hours", type=float)
    c.add_argument("--kinds", action="store_true", help="list the available cycle kinds")
    args = p.parse_args()
    if args.cmd == "cycle" and args.action in {"start", "close"} and not args.kind:
        p.error(f"cycle {args.action} needs a kind" + (" or file" if args.action == "close" else ""))
    return {
        "init": cmd_init,
        "check": cmd_check,
        "status": cmd_status,
        "next": cmd_next,
        "set": cmd_set,
        "project": cmd_project,
        "cycle": cmd_cycle,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
