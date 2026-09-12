#!/usr/bin/env python3
"""sdd.py -- the mechanical half of the constitution -> specify -> plan -> implement pipeline.

Everything in here is a check a language model is bad at doing reliably by eye:
counting markers, comparing versions, keeping two files agreeing about a status.
Stdlib only, no network, no config. Run `sdd.py doctor` for a health summary.

Layout it operates on (see LAYOUT.md):

    .specify/
      memory/constitution.md
      specs/requirements.md
      specs/README.md          <- the component index
      specs/<component>.md     <- one per component
      toolkit/                 <- this file + protocol docs, vendored by `init`
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "1.0.0"

STATUSES = ("Not started", "Draft", "Ready", "Implemented")
IMPLEMENTABLE = ("Draft", "Ready")

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
FIELD_RE = re.compile(r"^\*\*(?P<key>[A-Za-z][A-Za-z ]*)\*\*:\s*(?P<val>.*?)\s*$", re.M)
COMPONENT_ID_RE = re.compile(r"\bC-\d{3}\b")

# --- [!UNCLEAR] protocol (see UNCLEAR-PROTOCOL.md) ---------------------------
UNCLEAR_BLOCK_RE = re.compile(
    r"^>\s*\[!UNCLEAR\]\s*(?P<id>U-\d{3})\s*(?:[-—–]\s*)?(?P<q>.*)$", re.M
)
UNCLEAR_INLINE_RE = re.compile(r"\[!UNCLEAR:(?P<id>U-\d{3})\]")
UNCLEAR_ANY_RE = re.compile(r"\[!UNCLEAR")
UNCLEAR_FIELD_RE = re.compile(r"^>\s*\*\*(?P<key>[A-Za-z ]+)\*\*:\s*(?P<val>.*?)\s*$")

ERROR, WARN, INFO = "ERROR", "WARN", "INFO"


# --------------------------------------------------------------------------- #
# model
# --------------------------------------------------------------------------- #
@dataclass
class Finding:
    code: str
    severity: str
    location: str
    message: str
    fix: str = ""

    def render(self) -> str:
        head = f"{self.severity:5} {self.code}  {self.location}\n       {self.message}"
        return head + (f"\n       fix: {self.fix}" if self.fix else "")


@dataclass
class Unclear:
    id: str
    question: str
    blocks: str
    options: str
    raised: str
    path: Path
    line: int

    @property
    def blocking(self) -> bool:
        return self.blocks.strip().lower() not in ("", "none", "nothing", "n/a")


@dataclass
class Artifact:
    path: Path
    text: str
    fields: dict
    unclears: list = field(default_factory=list)
    inline_refs: set = field(default_factory=set)

    @property
    def version(self) -> str:
        return self.fields.get("Version", "")

    @property
    def status(self) -> str:
        return self.fields.get("Status", "")

    @property
    def cid(self) -> str:
        return self.fields.get("ID", "")

    @property
    def amended(self) -> str:
        return self.fields.get("Last Amended", "")


@dataclass
class Row:
    cid: str
    component: str
    status: str
    spec: str
    version: str
    notes: str
    group: str
    line: int
    raw: str


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def today() -> str:
    return _dt.date.today().isoformat()


def die(msg: str, code: int = 2):
    print(f"sdd: {msg}", file=sys.stderr)
    raise SystemExit(code)


def find_root(start: Path | None = None) -> Path:
    """Locate the .specify/ directory by walking upward from cwd."""
    cur = (start or Path.cwd()).resolve()
    for cand in [cur, *cur.parents]:
        if (cand / ".specify").is_dir():
            return cand / ".specify"
    die("no .specify/ directory found here or in any parent. Run `sdd.py init` first.")


def parse_fields(text: str) -> dict:
    """Read the `**Key**: value` header block that opens every artifact.

    Only the block before the first `## ` heading counts, so a `**Status**:`
    mentioned in prose further down can never be mistaken for the header.
    """
    head = re.split(r"^## ", text, maxsplit=1, flags=re.M)[0]
    return {m.group("key").strip(): m.group("val").strip() for m in FIELD_RE.finditer(head)}


def parse_unclears(text: str, path: Path) -> tuple[list, set, list]:
    """Return (blocks, inline_refs, findings-for-malformed-markers)."""
    lines = text.splitlines()
    blocks, bad = [], []

    for m in UNCLEAR_BLOCK_RE.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        meta = {}
        for ln in lines[line_no:]:
            if not ln.lstrip().startswith(">"):
                break
            fm = UNCLEAR_FIELD_RE.match(ln.strip())
            if fm:
                meta[fm.group("key").strip().lower()] = fm.group("val").strip()
        blocks.append(
            Unclear(
                id=m.group("id"),
                question=m.group("q").strip(),
                blocks=meta.get("blocks", ""),
                options=meta.get("options", ""),
                raised=meta.get("raised", ""),
                path=path,
                line=line_no,
            )
        )

    for u in blocks:
        if not u.question:
            bad.append(Finding("E006", ERROR, f"{path}:{u.line}",
                               f"{u.id} has no question text.",
                               "Write the open question on the same line as the marker."))
        if not u.blocks:
            bad.append(Finding("E006", ERROR, f"{path}:{u.line}",
                               f"{u.id} has no **Blocks**: line.",
                               "Add `> **Blocks**: <sections/components>` or `none` if informational."))

    seen = {}
    for u in blocks:
        if u.id in seen:
            bad.append(Finding("E006", ERROR, f"{path}:{u.line}",
                               f"duplicate marker id {u.id} (also at line {seen[u.id]}).",
                               "Marker ids must be unique within a file."))
        seen[u.id] = u.line

    refs = {m.group("id") for m in UNCLEAR_INLINE_RE.finditer(text)}
    for ref in sorted(refs - set(seen)):
        bad.append(Finding("E006", ERROR, str(path),
                           f"inline [!UNCLEAR:{ref}] has no matching block in this file.",
                           f"Add the `> [!UNCLEAR] {ref} — ...` block, or drop the reference."))

    # A bare `[!UNCLEAR]` with no id and not part of a well-formed block.
    for i, ln in enumerate(lines, 1):
        if UNCLEAR_ANY_RE.search(ln) and not UNCLEAR_BLOCK_RE.match(ln) and not UNCLEAR_INLINE_RE.search(ln):
            bad.append(Finding("E006", ERROR, f"{path}:{i}",
                               "malformed [!UNCLEAR] marker (no U-NNN id).",
                               "Use `> [!UNCLEAR] U-NNN — question` or inline `[!UNCLEAR:U-NNN]`."))

    return blocks, refs, bad


def load_artifact(path: Path) -> Artifact | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    blocks, refs, _ = parse_unclears(text, path)
    return Artifact(path=path, text=text, fields=parse_fields(text), unclears=blocks, inline_refs=refs)


def split_row(line: str) -> list:
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def parse_index(index_path: Path) -> tuple[list, list]:
    """Parse every markdown table in the component index into Rows."""
    if not index_path.is_file():
        return [], [Finding("E004", ERROR, str(index_path),
                            "component index is missing.",
                            "Run the `specify` skill to generate it.")]
    rows, findings = [], []
    group, header = "", None
    for i, line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if s.startswith("#"):
            group, header = s.lstrip("#").strip(), None
            continue
        if not s.startswith("|"):
            header = None
            continue
        cells = split_row(s)
        low = [c.lower() for c in cells]
        if "component" in low and "status" in low:
            header = low
            continue
        if header is None or set("".join(cells)) <= set("-: "):
            continue

        def cell(name, default=""):
            return cells[header.index(name)] if name in header and header.index(name) < len(cells) else default

        comp = cell("component")
        if not comp:
            continue
        rows.append(Row(cid=cell("id"), component=comp, status=cell("status"), spec=cell("spec"),
                        version=cell("version"), notes=cell("notes"), group=group, line=i, raw=s))

    for r in rows:
        if r.status not in STATUSES:
            findings.append(Finding("E003", ERROR, f"{index_path}:{r.line}",
                                    f"{r.component!r} has status {r.status!r}.",
                                    f"Use one of: {', '.join(STATUSES)}."))
        if r.cid and not COMPONENT_ID_RE.fullmatch(r.cid):
            findings.append(Finding("E003", ERROR, f"{index_path}:{r.line}",
                                    f"{r.component!r} has id {r.cid!r}, expected C-NNN.", ""))

    ids = [r.cid for r in rows if r.cid]
    for dup in {i for i in ids if ids.count(i) > 1}:
        findings.append(Finding("E010", ERROR, str(index_path),
                                f"component id {dup} is used by more than one row.", ""))
    return rows, findings


def spec_path_for(root: Path, row: Row) -> Path | None:
    """Resolve a row's Spec cell (a markdown link, a bare filename, or empty)."""
    m = re.search(r"\]\(([^)]+)\)", row.spec) or re.search(r"([\w.-]+\.md)", row.spec)
    if not m:
        return None
    return (root / "specs" / m.group(1).split("/")[-1]).resolve()


def parse_deps(art: Artifact) -> list:
    """Dependencies declared as `- C-001 Name @1.2.0 -- what's needed`."""
    m = re.search(r"^## Dependencies\s*$(.*?)(?=^## |\Z)", art.text, re.M | re.S)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        cid = COMPONENT_ID_RE.search(line)
        if not cid:
            continue
        pin = re.search(r"@(\d+\.\d+\.\d+)", line)
        out.append((cid.group(0), pin.group(1) if pin else None, line.strip()))
    return out


def bump_semver(current: str, level: str) -> str:
    m = SEMVER_RE.match(current or "")
    major, minor, patch = (int(g) for g in m.groups()) if m else (0, 0, 0)
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


# --------------------------------------------------------------------------- #
# collection
# --------------------------------------------------------------------------- #
def collect(root: Path) -> dict:
    constitution = load_artifact(root / "memory" / "constitution.md")
    requirements = load_artifact(root / "specs" / "requirements.md")
    index_path = root / "specs" / "README.md"
    rows, findings = parse_index(index_path)

    specs, by_id = {}, {}
    for p in sorted((root / "specs").glob("*.md")):
        if p.name in ("README.md", "requirements.md"):
            continue
        art = load_artifact(p)
        specs[p.resolve()] = art
        if art.cid:
            by_id[art.cid] = art

    return dict(root=root, constitution=constitution, requirements=requirements,
                index=load_artifact(index_path), index_path=index_path, rows=rows,
                specs=specs, by_id=by_id, index_findings=findings)


def check_artifact_header(art: Artifact, required: tuple) -> list:
    out = []
    for f in required:
        if not art.fields.get(f):
            out.append(Finding("E001", ERROR, str(art.path),
                               f"header is missing **{f}**.",
                               "Every versioned artifact carries ID/Version/Status/Ratified/Last Amended "
                               "per ARTIFACT-CONTRACT.md."))
    v = art.fields.get("Version", "")
    if v and not SEMVER_RE.match(v):
        out.append(Finding("E002", ERROR, str(art.path), f"**Version** {v!r} is not MAJOR.MINOR.PATCH.", ""))
    for datefield in ("Ratified", "Last Amended"):
        d = art.fields.get(datefield, "")
        if d and not re.match(r"^\d{4}-\d{2}-\d{2}$", d) and "TODO" not in d:
            out.append(Finding("E002", WARN, str(art.path),
                               f"**{datefield}** {d!r} is not an ISO date (YYYY-MM-DD).", ""))
    return out


def run_check(root: Path, strict: bool = False) -> list:
    st = collect(root)
    findings = list(st["index_findings"])

    for art, required in (
        (st["constitution"], ("Version", "Ratified", "Last Amended")),
        (st["requirements"], ("Version", "Ratified", "Last Amended")),
        (st["index"], ("Version", "Ratified", "Last Amended")),
    ):
        if art is None:
            continue
        findings += check_artifact_header(art, required)
        findings += parse_unclears(art.text, art.path)[2]

    if st["constitution"] is None:
        findings.append(Finding("W010", WARN, str(root / "memory" / "constitution.md"),
                                "no constitution. plan/implement have no gates to check against.",
                                "Run the `constitution` skill."))
    if st["requirements"] is None:
        findings.append(Finding("E004", ERROR, str(root / "specs" / "requirements.md"),
                                "no requirements.md -- nothing anchors the component index.",
                                "Run the `specify` skill."))

    # Marker syntax is checked in every spec file, linked or not -- a malformed
    # marker in an orphan is still a marker nobody can act on.
    for sp, art in st["specs"].items():
        findings += parse_unclears(art.text, art.path)[2]

    linked = set()
    for row in st["rows"]:
        sp = spec_path_for(root, row)
        if row.status == "Not started":
            if sp:
                findings.append(Finding("W003", WARN, f"{st['index_path']}:{row.line}",
                                        f"{row.component!r} is 'Not started' but links a spec file.",
                                        "Set the status to Draft, or clear the Spec cell."))
            continue
        if not sp:
            findings.append(Finding("E004", ERROR, f"{st['index_path']}:{row.line}",
                                    f"{row.component!r} is {row.status!r} but has no Spec link.", ""))
            continue
        linked.add(sp)
        art = st["specs"].get(sp)
        if art is None:
            findings.append(Finding("E004", ERROR, f"{st['index_path']}:{row.line}",
                                    f"{row.component!r} links {sp.name}, which does not exist.", ""))
            continue

        findings += check_artifact_header(art, ("ID", "Version", "Status", "Ratified", "Last Amended"))

        if art.status and art.status != row.status:
            findings.append(Finding("E005", ERROR, f"{st['index_path']}:{row.line}",
                                    f"{row.component!r}: index says {row.status!r}, "
                                    f"{sp.name} header says {art.status!r}.",
                                    "Use `sdd.py status <component> <status>` -- it writes both."))
        if row.version and art.version and row.version != art.version:
            findings.append(Finding("E005", ERROR, f"{st['index_path']}:{row.line}",
                                    f"{row.component!r}: index version {row.version}, "
                                    f"spec version {art.version}.",
                                    "Use `sdd.py bump` -- it writes both."))
        if row.cid and art.cid and row.cid != art.cid:
            findings.append(Finding("E005", ERROR, str(sp),
                                    f"id mismatch: index {row.cid}, spec {art.cid}.", ""))

        blocking = [u for u in art.unclears if u.blocking]
        if blocking and row.status in ("Ready", "Implemented"):
            findings.append(Finding("E007", ERROR, str(sp),
                                    f"status is {row.status!r} with {len(blocking)} blocking "
                                    f"[!UNCLEAR] marker(s): {', '.join(u.id for u in blocking)}.",
                                    "Resolve them, or move the status back to Draft. "
                                    "Nothing unclear is implementable."))

        for dep_id, pin, raw in parse_deps(art):
            dep_row = next((r for r in st["rows"] if r.cid == dep_id), None)
            if dep_row is None:
                findings.append(Finding("E009", ERROR, str(sp),
                                        f"depends on {dep_id}, which is not in the index.",
                                        "Add the component to the index, or fix the id."))
                continue
            if row.status == "Implemented" and dep_row.status != "Implemented":
                findings.append(Finding("E008", ERROR, str(sp),
                                        f"is Implemented but dependency {dep_id} "
                                        f"({dep_row.component}) is {dep_row.status!r}.", ""))
            dep_art = st["by_id"].get(dep_id)
            if pin and dep_art and dep_art.version:
                if pin.split(".")[0] != dep_art.version.split(".")[0]:
                    findings.append(Finding("E011", ERROR, str(sp),
                                            f"pins {dep_id}@{pin} but {dep_id} is now "
                                            f"{dep_art.version} -- a MAJOR bump means its interface "
                                            f"changed incompatibly.",
                                            "Re-read the dependency's spec, update this one, and bump it."))
                elif pin != dep_art.version:
                    findings.append(Finding("W011", WARN, str(sp),
                                            f"pins {dep_id}@{pin}, current is {dep_art.version}.",
                                            "Re-read the dependency and re-pin if anything you use changed."))

    for sp, art in st["specs"].items():
        if sp not in linked:
            findings.append(Finding("W004", WARN, str(sp),
                                    "spec file is not referenced by any row in the index.",
                                    "Add its row to specs/README.md, or delete the orphan."))

    findings += check_staleness(st)
    if not strict:
        findings = [f for f in findings if f.severity != INFO]
    return findings


STALE_RE = re.compile(r"^\s*Stale downstream:\s*(?P<list>.+?)\s*$", re.M)
SYNC_VER_RE = re.compile(r"^\s*Version:\s*\S+\s*(?:->|→)\s*(?P<to>\d+\.\d+\.\d+)", re.M)
SYNC_DATE_RE = re.compile(r"^\s*Date:\s*(?P<d>\d{4}-\d{2}-\d{2})", re.M)


def check_staleness(st: dict) -> list:
    """A Sync Impact Report naming stale downstream files is a promise to go fix them."""
    out = []
    arts = [a for a in (st["constitution"], st["requirements"], st["index"],
                        *st["specs"].values()) if a]
    for art in arts:
        head = art.text[:4000]
        m = SYNC_DATE_RE.search(head)
        if not m:
            continue
        when = m.group("d")
        for sm in STALE_RE.finditer(head):
            names = [n.strip() for n in sm.group("list").split(",") if n.strip()]
            for name in names:
                if name.lower() in ("none", "n/a", "-"):
                    continue
                base, _, marked_ver = name.partition("@")
                base = base.strip().split("/")[-1]
                target = next((a for a in arts if a.path.name == base), None)
                if target is None:
                    out.append(Finding("W005", WARN, str(art.path),
                                       f"Sync Impact Report names {base!r}, which does not exist.", ""))
                    continue
                if marked_ver:
                    # Outstanding while the target is still on the version it had
                    # when it was marked -- date-independent, so same-day edits work.
                    outstanding = target.version == marked_ver
                    detail = (f"still at v{target.version}, the version it had when "
                              f"{art.path.name} marked it stale on {when}")
                else:
                    outstanding = bool(target.amended) and target.amended < when
                    detail = (f"its Last Amended is still {target.amended}, before "
                              f"{art.path.name} marked it stale on {when}")
                if outstanding:
                    out.append(Finding("W006", WARN, str(target.path),
                                       f"marked stale by {art.path.name}: {detail}.",
                                       "Re-read it against the upstream change and bump it -- "
                                       "`--summary \"re-read against <file> v<X.Y.Z>; no change needed\"` "
                                       "if nothing had to change."))
    return out


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def cmd_init(args) -> int:
    project = Path(args.path).resolve()
    root = project / ".specify"
    src = Path(__file__).resolve().parent

    for d in (root / "memory", root / "specs", root / "toolkit"):
        d.mkdir(parents=True, exist_ok=True)

    copied = []
    for f in sorted(src.glob("*")):
        if f.is_file() and (f.suffix in (".py", ".md")):
            dest = root / "toolkit" / f.name
            if dest.exists() and not args.force:
                continue
            if dest.resolve() == f.resolve():
                continue  # re-running the already-vendored copy against its own project
            shutil.copy2(f, dest)
            copied.append(dest.name)

    print(f"root: {root}")
    print(f"toolkit: {'copied ' + ', '.join(copied) if copied else 'already present (use --force to refresh)'}")
    for label, p in (("constitution", root / "memory" / "constitution.md"),
                     ("requirements", root / "specs" / "requirements.md"),
                     ("index", root / "specs" / "README.md")):
        print(f"{label:13}: {'present' if p.exists() else 'MISSING -- run the matching skill'}")
    return 0


def _all_unclears(root: Path) -> list:
    st = collect(root)
    arts = [a for a in (st["constitution"], st["requirements"], st["index"],
                        *st["specs"].values()) if a]
    return [u for a in arts for u in a.unclears]


def cmd_unclear(args) -> int:
    root = find_root()
    items = _all_unclears(root)
    if args.blocking_only:
        items = [u for u in items if u.blocking]
    if args.json:
        print(json.dumps([{"id": u.id, "file": str(u.path), "line": u.line, "question": u.question,
                           "blocks": u.blocks, "options": u.options, "raised": u.raised,
                           "blocking": u.blocking} for u in items], indent=2))
    elif not items:
        print("no [!UNCLEAR] markers outstanding.")
    else:
        by_file = {}
        for u in items:
            by_file.setdefault(u.path, []).append(u)
        for path, us in by_file.items():
            print(f"\n{path}")
            for u in sorted(us, key=lambda x: x.line):
                flag = "BLOCKING" if u.blocking else "info"
                print(f"  {u.id} [{flag}] line {u.line}: {u.question}")
                if u.blocks:
                    print(f"        blocks : {u.blocks}")
                if u.options:
                    print(f"        options: {u.options}")
        print(f"\n{len(items)} marker(s); {sum(1 for u in items if u.blocking)} blocking.")
    return 1 if any(u.blocking for u in items) else 0


def _resolve_row(st: dict, name: str) -> tuple:
    """Match a component by id, exact name, or unique case-insensitive substring."""
    rows = st["rows"]
    exact = [r for r in rows if r.cid.lower() == name.lower() or r.component.lower() == name.lower()]
    if len(exact) == 1:
        return exact[0], None
    part = [r for r in rows if name.lower() in r.component.lower()]
    if len(part) == 1:
        return part[0], None
    if not part:
        return None, f"no component matches {name!r}. Known: " + ", ".join(r.component for r in rows)
    return None, (f"{name!r} is ambiguous: " + ", ".join(r.component for r in part) +
                  ". Use the exact name or its C-NNN id.")


def cmd_gate(args) -> int:
    """The hard precondition for `implement`. Exit 0 means: safe to build."""
    root = find_root()
    st = collect(root)
    row, err = _resolve_row(st, args.component)
    if err:
        die(err)

    checks, blockers = [], 0

    def record(ok, label, detail=""):
        nonlocal blockers
        if not ok:
            blockers += 1
        checks.append(("PASS" if ok else "FAIL", label, detail if not ok else ""))

    sp = spec_path_for(root, row)
    art = st["specs"].get(sp) if sp else None
    record(art is not None, "spec exists",
           "" if art else f"{row.component} has no spec file -- run `plan` first.")
    record(row.status in IMPLEMENTABLE, f"status is Draft or Ready (is {row.status!r})",
           "" if row.status in IMPLEMENTABLE else
           ("nothing to implement -- run `plan`." if row.status == "Not started"
            else "already Implemented; confirm this is a deliberate re-implementation."))

    if art:
        blocking = [u for u in art.unclears if u.blocking]
        record(not blocking, "no blocking [!UNCLEAR] in this spec",
               "; ".join(f"{u.id}: {u.question} (blocks {u.blocks})" for u in blocking))

    for label, up in (("constitution", st["constitution"]), ("requirements.md", st["requirements"])):
        if up:
            bl = [u for u in up.unclears if u.blocking]
            record(not bl, f"no blocking [!UNCLEAR] in {label}",
                   "; ".join(f"{u.id}: {u.question}" for u in bl))

    if art:
        deps = parse_deps(art)
        if not deps:
            checks.append(("INFO", "no declared dependencies", ""))
        for dep_id, pin, _ in deps:
            dep_row = next((r for r in st["rows"] if r.cid == dep_id), None)
            if dep_row is None:
                record(False, f"dependency {dep_id} is in the index", "unknown component id")
                continue
            record(dep_row.status == "Implemented",
                   f"dependency {dep_id} ({dep_row.component}) is Implemented",
                   "" if dep_row.status == "Implemented" else
                   f"it is {dep_row.status!r} -- build against code, never an invented interface.")
            dep_art = st["by_id"].get(dep_id)
            if pin and dep_art and dep_art.version and pin.split(".")[0] != dep_art.version.split(".")[0]:
                record(False, f"dependency pin {dep_id}@{pin} is current",
                       f"{dep_id} is now {dep_art.version}; re-read its spec before building.")

    errs = [f for f in run_check(root) if f.severity == ERROR]
    record(not errs, "`sdd.py check` is clean",
           f"{len(errs)} error(s) -- run `sdd.py check` for detail.")

    width = max(len(c[1]) for c in checks)
    for state, label, detail in checks:
        print(f"  [{state}] {label.ljust(width)}  {detail}".rstrip())
    verdict = "GATE PASSED" if blockers == 0 else f"GATE FAILED ({blockers} blocker(s))"
    print(f"\n{verdict} -- {row.component}")
    return 0 if blockers == 0 else 1


def _find_artifact_by_name(start: Path, name: str) -> Artifact | None:
    """Locate a sibling artifact by filename, anywhere under .specify/."""
    try:
        root = find_root(start)
    except SystemExit:
        return None
    base = name.split("/")[-1].split("@")[0]
    for cand in (root / "specs" / base, root / "memory" / base):
        if cand.is_file():
            return load_artifact(cand)
    return None


SYNC_BLOCK_RE = re.compile(r"\A<!--\s*\nSync Impact Report.*?-->\n*", re.S)


def cmd_bump(args) -> int:
    path = Path(args.file).resolve()
    if not path.is_file():
        die(f"{path} does not exist.")
    text = path.read_text(encoding="utf-8")
    fields = parse_fields(text)
    old = fields.get("Version", "0.0.0")
    new = bump_semver(old, args.level)

    body = SYNC_BLOCK_RE.sub("", text)

    def set_field(src, key, val):
        pat = re.compile(rf"^\*\*{re.escape(key)}\*\*:.*$", re.M)
        return pat.sub(f"**{key}**: {val}", src, count=1) if pat.search(src) else src

    body = set_field(body, "Version", new)
    body = set_field(body, "Last Amended", today())
    if not parse_fields(body).get("Ratified"):
        body = set_field(body, "Ratified", today())

    stale = [s.strip() for s in (args.stale or "").split(",") if s.strip()] or ["none"]
    # Stamp each target with the version it has *now*. The debt is outstanding for
    # exactly as long as that version is still current -- which is what makes this
    # work for two edits on the same day, where dates cannot tell them apart.
    stamped = []
    for name in stale:
        if name.lower() in ("none", "n/a", "-"):
            stamped.append(name)
            continue
        if "@" in name:
            stamped.append(name)
            continue
        target = _find_artifact_by_name(path.parent, name)
        tv = target.version if target else ""
        stamped.append(f"{name}@{tv}" if tv else name)
    stale = stamped
    report = (
        "<!--\n"
        "Sync Impact Report\n"
        f"Date: {today()}\n"
        f"Version: {old} -> {new} ({args.level.upper()})\n"
        f"Changed: {args.summary}\n"
        f"Stale downstream: {', '.join(stale)}\n"
        "-->\n"
    )
    path.write_text(report + body, encoding="utf-8")

    # Keep the index's Version cell in step with the spec header.
    try:
        root = find_root(path.parent)
        st = collect(root)
        cid = parse_fields(body).get("ID", "")
        row = next((r for r in st["rows"] if r.cid and r.cid == cid), None)
        if row and row.version:
            idx = st["index_path"]
            lines = idx.read_text(encoding="utf-8").splitlines()
            cells = split_row(lines[row.line - 1])
            hdr, _ = _index_header(idx)
            if hdr and "version" in hdr and hdr.index("version") < len(cells):
                cells[hdr.index("version")] = new
                lines[row.line - 1] = "| " + " | ".join(cells) + " |"
                idx.write_text("\n".join(lines) + "\n", encoding="utf-8")
                print(f"index: version cell for {row.component} -> {new}")
    except SystemExit:
        pass

    print(f"{path.name}: {old} -> {new} ({args.level})")
    print(f"stale downstream: {', '.join(stale)}")
    if stale != ["none"]:
        print("Those files are now owed a re-read. `sdd.py check` keeps flagging each one "
              "until it is bumped past the version stamped above.")
    return 0


def _index_header(idx: Path) -> tuple:
    for i, line in enumerate(idx.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if s.startswith("|"):
            low = [c.lower() for c in split_row(s)]
            if "component" in low and "status" in low:
                return low, i
    return None, 0


def cmd_status(args) -> int:
    if args.status not in STATUSES:
        die(f"{args.status!r} is not a status. Use one of: {', '.join(STATUSES)}")
    root = find_root()
    st = collect(root)
    row, err = _resolve_row(st, args.component)
    if err:
        die(err)

    sp = spec_path_for(root, row)
    art = st["specs"].get(sp) if sp else None

    if args.status in ("Ready", "Implemented") and art:
        blocking = [u for u in art.unclears if u.blocking]
        if blocking and not args.force:
            print(f"refused: {row.component} still has blocking [!UNCLEAR]: "
                  f"{', '.join(u.id for u in blocking)}", file=sys.stderr)
            print("Nothing unclear is implementable. Resolve them first.", file=sys.stderr)
            return 1

    idx = st["index_path"]
    lines = idx.read_text(encoding="utf-8").splitlines()
    hdr, _ = _index_header(idx)
    cells = split_row(lines[row.line - 1])
    if hdr and "status" in hdr and hdr.index("status") < len(cells):
        cells[hdr.index("status")] = args.status
        lines[row.line - 1] = "| " + " | ".join(cells) + " |"
        idx.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"index: {row.component} {row.status!r} -> {args.status!r}")

    if art:
        new_text = re.sub(r"^\*\*Status\*\*:.*$", f"**Status**: {args.status}", art.text, count=1, flags=re.M)
        sp.write_text(new_text, encoding="utf-8")
        print(f"{sp.name}: header status -> {args.status}")
    else:
        print("note: no spec file to update (status changed in the index only).")
    return 0


def cmd_index(args) -> int:
    root = find_root()
    st = collect(root)
    if args.json:
        print(json.dumps([r.__dict__ for r in st["rows"]], indent=2, default=str))
        return 0
    if not st["rows"]:
        print("component index is empty.")
        return 0
    w = max(len(r.component) for r in st["rows"])
    group = None
    for r in st["rows"]:
        if r.group != group:
            group = r.group
            print(f"\n{group}")
        sp = spec_path_for(root, r)
        art = st["specs"].get(sp) if sp else None
        n_block = sum(1 for u in art.unclears if u.blocking) if art else 0
        mark = f"  [{n_block} blocking UNCLEAR]" if n_block else ""
        ver = f" v{art.version}" if art and art.version else ""
        print(f"  {(r.cid or '----'):6} {r.component.ljust(w)}  {r.status:12}{ver}{mark}")
    nxt = next((r for r in st["rows"] if r.status == "Not started"), None)
    rdy = next((r for r in st["rows"] if r.status in IMPLEMENTABLE), None)
    print()
    print(f"next to plan     : {nxt.component if nxt else '-- none'}")
    print(f"next to implement: {rdy.component if rdy else '-- none'}")
    return 0


def cmd_check(args) -> int:
    root = find_root()
    findings = run_check(root, strict=args.strict)
    if args.json:
        print(json.dumps([f.__dict__ for f in findings], indent=2))
    else:
        order = {ERROR: 0, WARN: 1, INFO: 2}
        for f in sorted(findings, key=lambda x: (order[x.severity], x.location)):
            print(f.render())
            print()
        n_err = sum(1 for f in findings if f.severity == ERROR)
        n_warn = sum(1 for f in findings if f.severity == WARN)
        print(f"{n_err} error(s), {n_warn} warning(s).")
        if not findings:
            print("artifacts are consistent.")
    return 1 if any(f.severity == ERROR for f in findings) else 0


def cmd_doctor(args) -> int:
    root = find_root()
    st = collect(root)
    print(f"specify root : {root}")
    print(f"toolkit      : {'vendored' if (root / 'toolkit' / 'sdd.py').exists() else 'NOT vendored (run init)'}")
    for label, art in (("constitution", st["constitution"]), ("requirements", st["requirements"])):
        print(f"{label:13}: " + (f"v{art.version or '?'} (amended {art.amended or '?'})" if art else "MISSING"))
    counts = {s: sum(1 for r in st["rows"] if r.status == s) for s in STATUSES}
    print(f"components   : {len(st['rows'])} -- " + ", ".join(f"{k}: {v}" for k, v in counts.items()))
    us = _all_unclears(root)
    print(f"unclear      : {len(us)} marker(s), {sum(1 for u in us if u.blocking)} blocking")
    findings = run_check(root)
    print(f"check        : {sum(1 for f in findings if f.severity == ERROR)} error(s), "
          f"{sum(1 for f in findings if f.severity == WARN)} warning(s)")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="sdd.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"sdd.py {VERSION}")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="create .specify/ and vendor the toolkit into it")
    s.add_argument("path", nargs="?", default=".")
    s.add_argument("--force", action="store_true", help="overwrite an already-vendored toolkit")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("check", help="full consistency check; exit 1 on any ERROR")
    s.add_argument("--json", action="store_true")
    s.add_argument("--strict", action="store_true", help="include INFO findings")
    s.set_defaults(func=cmd_check)

    s = sub.add_parser("unclear", help="list [!UNCLEAR] markers; exit 1 if any are blocking")
    s.add_argument("--blocking-only", action="store_true")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_unclear)

    s = sub.add_parser("gate", help="can this component be implemented right now?")
    s.add_argument("component")
    s.set_defaults(func=cmd_gate)

    s = sub.add_parser("bump", help="bump a version, stamp the date, write a Sync Impact Report")
    s.add_argument("file")
    s.add_argument("--level", required=True, choices=("major", "minor", "patch"))
    s.add_argument("--summary", required=True, help="what changed, one line")
    s.add_argument("--stale", default="", help="comma-separated downstream files now owed a re-read")
    s.set_defaults(func=cmd_bump)

    s = sub.add_parser("status", help="move a component's status in the index and its spec together")
    s.add_argument("component")
    s.add_argument("status")
    s.add_argument("--force", action="store_true", help="allow Ready/Implemented despite blocking markers")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("index", help="show the component index with live spec state")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_index)

    s = sub.add_parser("doctor", help="one-screen health summary")
    s.set_defaults(func=cmd_doctor)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
