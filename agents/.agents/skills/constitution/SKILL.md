---
name: constitution
description: Create or amend .specify/memory/constitution.md -- the small set of non-negotiable principles that gate everything specify/plan/implement produce afterwards. Infers candidate principles from real repository evidence, presents each as a hypothesis, interviews the user for what evidence can't answer, and writes each principle with an explicit Gate stating how downstream stages verify it. Adds CRISP-ML(Q) principle categories (reproducibility, experiment tracking, data governance, model risk, evaluation rigor, monitoring) when the repo shows ML/LLM signal. Versioned; every amendment bumps semver and records what it invalidated. Use when starting a project, when governance rules change, or when asked to "set the rules"/"write the constitution".
argument-hint: "[optional: a principle or area to add or amend]"
---

# Constitution

First stage of the pipeline: `constitution` → `specify` → `plan` → `implement`.

Produces exactly one artifact: `.specify/memory/constitution.md` — a short set of
principles that every later stage is mechanically checked against. It writes no
specs and no code.

A constitution earns its place only if it **changes decisions**. Three principles
that reject a real design are worth more than twelve that everyone nods at. The
whole quality bar here is one question, applied to every candidate principle:

> Could a reviewer point at a specific diff, spec, or plan and say "this violates
> it" — and would two reviewers agree?

If not, the principle is decoration. Rewrite it or drop it.

---

## Step 0 — Bootstrap the toolkit (every stage does this)

The mechanical checks live in `sdd.py`, vendored into the project so every stage
runs it from one stable path.

```bash
test -f .specify/toolkit/sdd.py && echo vendored || \
for c in ~/.agents/sdd/sdd.py ~/.claude/sdd/sdd.py; do \
  [ -f "$c" ] && python3 "$c" init . && break; done
python3 .specify/toolkit/sdd.py doctor
```

If none of the candidate paths resolve, **stop and say so**. Do not continue with
the checks silently switched off — a pipeline that looks checked but isn't is worse
than one that is visibly not.

Then read `.specify/toolkit/UNCLEAR-PROTOCOL.md` and
`.specify/toolkit/ARTIFACT-CONTRACT.md`. They are binding on this stage, not
background reading.

## Step 1 — Determine the mode

```bash
python3 .specify/toolkit/sdd.py doctor
```

- **No `constitution.md`** → first pass. Go to Step 2.
- **It exists** → this is an **amendment**. Read it **in full** first, including
  its Sync Impact Report. Preserve every principle the user is not asking to
  change. Never regenerate the file from scratch — an amendment that silently
  drops a principle is the single most damaging failure this stage has, because
  every downstream gate that principle was enforcing disappears with it.
- **It exists and the user gave no argument** → don't assume they want a rewrite.
  Ask what changed, or offer to review it against the repo as it stands now.

## Step 2 — Gather evidence before asking anything

Facts are yours to find; only decisions are the user's. Look for what the project
*already does*, so the interview is about confirming and sharpening rather than
inventing:

| Look at | Tells you about |
|---|---|
| `README`, `CONTRIBUTING`, `docs/` | Stated conventions, intended audience |
| Linter/formatter/type-checker config | Quality bar already enforced, and the exact commands for a Gate line |
| CI config | What actually blocks a merge today |
| Test directories, fixtures, coverage config | Testing posture in practice |
| Lockfiles, package manifests | Dependency discipline, pinning, runtime |
| Existing module boundaries | Architectural style already in play |
| `.env.example`, secrets handling, auth code | Security posture |
| Model artifacts (`.pkl`/`.pt`/`.onnx`/`.safetensors`), `notebooks/`, training scripts, `prompts/`, `evals/`, MLflow/W&B/Comet config, DVC/lakeFS config, ML framework deps | **ML/LLM signal** — see Step 3b |

Record what you found and what you did **not** find. A greenfield repo simply yields
little evidence; that is not a problem, it just means more of Step 3 is interview.

**Every inference is a hypothesis until the user confirms it.** Present them that
way — "CI runs `ruff` and `mypy` on every PR, so I'd propose a Code Quality
principle gated on those two commands; confirm?" — and never write an unconfirmed
inference into the file as settled fact.

## Step 3 — Interview for what evidence can't answer

Short blocks, 3–5 questions per turn, most-blocking first. Use `AskUserQuestion`
where there are 2–4 concrete options with a real tradeoff; plain text where the
answer needs the user's own words.

### 3a — Core categories (every project)

1. **Testing** — Is test-first mandatory, or tests-alongside acceptable? Which
   kinds are expected (unit, contract, integration, end-to-end)?
2. **Simplicity / scope** — Appetite for upfront abstraction vs. YAGNI. Is there a
   hard ceiling (number of services, dependencies, layers)?
3. **Architecture** — Any style that is non-negotiable (library-first, modular
   monolith, CLI-first)? Coupling constraints?
4. **Observability** — Structured logging, metrics, tracing: mandatory from day one
   or added when needed?
5. **Security & secrets** — What must never be logged, persisted, or committed? Any
   regulatory obligation (GDPR, HIPAA, SOC 2, PCI)?
6. **Versioning & compatibility** — How are breaking changes handled and signalled?
7. **Dependencies** — What justifies adding a runtime dependency?

### 3b — CRISP-ML(Q) categories (add when Step 2 found ML/LLM signal, or the user confirms a model is involved)

CRISP-ML(Q) is a quality-assurance methodology: for each phase of an ML lifecycle,
name the risk, judge whether it is acceptable as-is, and where it is not, name the
method that mitigates it. That is the same shape as a principle with a Gate — which
is why these belong in the constitution rather than in a separate document.

Ask only what the project's actual shape makes relevant. A prompt-and-tools LLM
application needs evaluation rigor and data governance; it probably needs nothing
about training reproducibility. Skip what doesn't apply, and say you skipped it.

| Category | The risk it governs | Ask |
|---|---|---|
| **Reproducibility** | A result nobody can reproduce is a result nobody can trust or roll back to. | Seeds/determinism mandatory? Environments pinned (lockfile, container)? Data versioned (DVC, lakeFS, dated snapshots)? |
| **Experiment tracking** | Undocumented runs make regressions unattributable. | Which tool is mandatory (MLflow, W&B, Comet, none)? What must every run log — params, metrics, artifacts, data lineage, prompt version? |
| **Evaluation rigor** | Shipping on a metric measured on the wrong set. | Minimum protocol before anything ships: named held-out set, cross-validation, significance testing, human review? Who owns the eval set, and how is contamination prevented? |
| **Data governance** | Regulatory and privacy exposure that code review won't catch. | PII classes present? Retention limits? Access control? What may never leave the environment or reach a third-party API? |
| **Model & prompt risk** | Silent harm from a confidently wrong output. | Fairness/bias review required before shipping? Human-in-the-loop for low-confidence or high-stakes outputs? Explainability obligations? |
| **Versioning & rollback** | No way back from a bad model or prompt. | How are models and prompts versioned? Is shadow deployment or a rollback path mandatory before full rollout? |
| **Monitoring & retraining** | Quality decays invisibly after launch. | What drift/quality signals are mandatory in production, and what threshold triggers action? |

### 3c — Confirm before writing

Present every principle — inferred and interviewed alike — in blocks of 3–5, with
its proposed Gate, and get explicit confirmation, edits, or removal. **Write
nothing to disk before that confirmation.**

If the user defers a decision rather than making it, that is an `[!UNCLEAR]` marker,
not a guess. A blocking marker in the constitution blocks **every** component
downstream — so scope it honestly with `**Blocks**: none` if it genuinely gates
nothing yet, and say so out loud either way.

## Step 4 — Write the file

Read `CONSTITUTION-TEMPLATE.md` (next to this SKILL.md) and follow it exactly.

The template's central rule, repeated here because it is the one most often skipped:
**every principle carries a `Gate:` line** naming how a later stage verifies it. A
principle with no Gate is a principle `plan` and `implement` cannot check, which
means it will be quietly ignored the first time it's inconvenient.

## Step 5 — Version and record the impact

```bash
python3 .specify/toolkit/sdd.py bump .specify/memory/constitution.md \
  --level minor --summary "added Evaluation Rigor (NON-NEGOTIABLE)" \
  --stale "requirements.md,llm-router.md"
```

Level, per `ARTIFACT-CONTRACT.md`:

- **MAJOR** — a principle removed or redefined incompatibly. Work already done under
  the old rule may now be non-compliant.
- **MINOR** — a principle added, or one materially expanded.
- **PATCH** — wording, rationale, formatting.

`--stale` is where amendments earn their keep. On a MAJOR, list **every** spec whose
Constitution Check touched the changed principle, `Implemented` ones included — the
rule changed under code that was already written, and somebody has to look. On a
first pass there is nothing downstream yet: `--stale none`.

If the bump level is genuinely ambiguous, pick the higher one and explain why in the
summary.

## Step 6 — Verify, then report

```bash
python3 .specify/toolkit/sdd.py check
```

**Not done until this exits 0.** If it reports errors, fix them and run it again;
do not report success over a failing check.

Then report:

- Path, new version, and the bump rationale.
- Each principle in one line, with its Gate, and whether it came from repository
  evidence or from the interview.
- Any CRISP-ML(Q) category deliberately skipped, and why.
- Every `[!UNCLEAR]` marker raised, in the shape `UNCLEAR-PROTOCOL.md` specifies —
  question, options, recommendation — so the user can close them by replying.
- Artifacts marked stale and now owed a re-read.
- **Next**: run `specify` to turn the business need into requirements and a
  component index under this constitution.

## Failure modes this stage must not produce

| Failure | What it looks like | Required behaviour |
|---|---|---|
| Silent principle loss | Amendment rewrites the file, a principle vanishes, its gate stops being enforced and nobody notices. | Read the existing file in full; amend, never regenerate. Diff your output against it before writing. |
| Unverifiable principles | "Code should be clean and maintainable." | Every principle has a Gate naming a command, a document section, or a reviewable artifact. No Gate, no principle. |
| Invented evidence | A principle attributed to the repo that the repo doesn't support. | Quote the file or command you found it in, or label it as a proposal. |
| Aspiration written as rule | A MUST the project has never once followed. | Ask directly: "CI doesn't run this today — do you want it as a rule that CI must be changed to meet, or as a SHOULD?" |
| Guessing a deferred decision | User says "not sure yet", a plausible default gets written as settled. | Raise `[!UNCLEAR]`. Never fabricate. |
| Constitution sprawl | Fifteen principles, most of them generic. | Target 3–7. If a candidate wouldn't reject a real design, drop it. |
| Unversioned amendment | File edited, version and dates unchanged. | Always `sdd.py bump`. Never hand-edit the header or the Sync Impact Report. |
| Reporting success over a failing check | "Done!" while `sdd.py check` exits 1. | Run it; fix what it names; run it again. |
