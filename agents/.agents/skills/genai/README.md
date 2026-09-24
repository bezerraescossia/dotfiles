# GenAI Delivery Framework

A repeatable personal process for building Generative AI applications. It is based on **[CRISP-ML(Q)](https://ml-ops.org/content/crisp-ml)**, adapted for GenAI: most projects use a model they buy rather than train, and they must handle non-deterministic outputs, per-request cost, and agent authority.

## How it works

- Each phase is a checklist of **tasks** with time estimates.
- Each phase ends with a **Quality assurance** block, following the CRISP-ML(Q) method:
  - **Requirements & constraints**
  - **Risks → QA measures**
  - **Exit gate**: what must be true before moving on
- Phases are iterative. If a gate fails, go back to the phase that owns the problem. The first pass through phases 02–04 builds the **smallest testable slice** chosen in phase 01.

## Phases

| # | Phase | CRISP-ML(Q) origin | Executable with `/genai` |
|---|-------|--------------------|--------------------------|
| 01 | [Business Understanding](phases/01-business-understanding.md) | Business & Data Understanding | Yes |
| 02 | [Context Engineering](phases/02-context-engineering.md) | Data Engineering | Yes |
| 03 | [Model Selection & Customization](phases/03-model-selection-customization.md) | ML Model Engineering | Yes |
| 04 | [Evaluation](phases/04-evaluation.md) | ML Model Evaluation | Yes |
| 05 | [Deployment](phases/05-deployment.md) | Model Deployment | Yes |
| 06 | [Monitoring & Maintenance](phases/06-monitoring-maintenance.md) | Monitoring & Maintenance | Yes — setup tasks, then recurring cycles |

Phases 01–06 run as one pipeline. When its last decision (06.10) passes, the project moves to `operating`: the task graph is done, and the work continues as the **cycles** defined in Phase 06 — `monthly`, `quarterly`, `migration`, `change`, `incident`.

## Running it with `/genai`

The framework is also a Claude Code skill ([`SKILL.md`](SKILL.md)). It runs a project **one task at a time**, and each task has a role:

| Role | Loop |
|------|------|
| **HUMAN** | AI prepares a kit (agenda, interview guide, draft tables) → you do the fieldwork and drop raw notes in `.genai/inbox/` → AI turns the notes into the artifact, marks `GAP`s instead of guessing, and reviews it against the task's rules → you approve |
| **DECISION** | AI writes a brief with the options and a labeled recommendation → you decide → the entry goes into `.genai/decisions.md`. Everything downstream is blocked until then |
| **AI** | AI writes a **plan** (what it will build, where, how it is tested) → you approve → AI **builds** in the project repo and records the paths, commands and measured results in the artifact → AI checks it against the task's rules → you approve |

```text
/genai init                      # create .genai/, choose size S or M-L
/genai next [task-id]            # move the current task one stage forward
/genai status                    # task graph, blockers, estimated vs actual hours
/genai skip <task-id> "<reason>" # a task that doesn't apply (never a DECISION)
/genai cycle start <kind>        # a recurring ops run, once the project is operating
/genai cycle list                # cycle runs so far (--kinds for the kinds available)
/genai cycle close <file|kind>   # close it, with --hours N
```

**Optional tags.** `[R]` retrieval, `[A]` tools/agents, `[FT]` fine-tuning and `[SH]` self-hosted mark work only some projects need. Each is settled by one DECISION — 02.0 sets `[R]`, 03.0 sets `[A]`, 03.4b sets `[SH]`, 03.9 sets `[FT]` — in the call that closes it: `set 02.0 done --tag R=no`. While a tag is off, its tasks show as `n/a` and the checker refuses to start them.

State is kept in `.genai/state.yaml` and changed only through [`scripts/check.py`](scripts/check.py). It refuses any change that would leave the state invalid: unmet dependencies, a pending decision upstream, a missing artifact or decision-log entry, or a skip with no reason. `.genai/inbox/` is git-ignored because raw notes are often sensitive.

A task is defined by its fenced `yaml task` block (`id`, `title`, `role`, `depends_on`, `estimate`, `artifact`, `optional_tag`, `sets_tags`) plus the prose sections its role needs. A cycle is defined by a `yaml cycle` block (`kind`, `title`, `estimate`) followed by the checklist that `cycle start` copies into `.genai/ops/`. See Phase 01 for the task pattern and Phase 06 for cycles.

## Effort overview

These are hands-on hours from each phase's estimate table. **S** = small project, **M-L** = medium/large project. Calendar time is longer: it depends on stakeholder and SME availability, and on the rollout and canary periods in Phase 05.

| # | Phase | Core S | Core M-L | With all optional steps S | With all optional steps M-L |
|---|-------|--------|----------|---------------------------|-----------------------------|
| 01 | Business Understanding | 34h | 82h | 34h | 82h |
| 02 | Context Engineering | 19h | 53h | 37h `[R]` | 100h `[R]` |
| 03 | Model Selection & Customization | 22h | 50h | 38h `[R][A][FT]` | 96h `[R][A][FT]` |
| 04 | Evaluation | 25h | 66h | 30h `[R][A]` | 79h `[R][A]` |
| 05 | Deployment | 31h | 87h | 31h | 87h |
| 06 | Monitoring & Maintenance (setup) | 17h | 41h | 17h | 41h |
| | **To launch + monitoring setup** | **~148h (~4 weeks)** | **~379h (~9–10 weeks)** | **~187h (~5 weeks)** | **~485h (~12 weeks)** |
| 06 | Monitoring & Maintenance (ongoing) | ~11h/month | ~29h/month | ~11h/month | ~29h/month |

Optional tags: `[R]` retrieval, `[A]` tools/agents, `[FT]` fine-tuning, `[SH]` self-hosted models. A real project picks the tags that apply, so its total falls between the core and full columns. Loop-backs between phases add rework on top.

## Main adaptations from CRISP-ML(Q)

- **Business Understanding** adds real-workflow discovery, assumption/risk mapping, and a judgment-preserving spec. Data understanding shrinks to a light check. Once the slice is chosen, it also settles the repo, language/framework, package manager and folder structure once, so later phases don't each improvise their own.
- **Data Engineering → Context Engineering.** The work is ingestion, chunking, metadata, retrieval and eval data, not features for training.
- **Model Engineering → Selection & Customization.** Customization is tried roughly in order: prompting → RAG → tools/agents → fine-tuning. Reproducibility means pinned model IDs and versioned prompts, not random seeds.
- **Evaluation** has no single accuracy number. It uses rubrics, an LLM judge calibrated against human labels, groundedness checks, and red-teaming.
- **Deployment** adds guardrails, cost caps, and fallback to another model or to a human. Rollouts apply to prompt and model versions as well as code.
- **Monitoring** watches for new kinds of drift: provider model changes, shifts in what users ask, and stale knowledge. "Retraining" usually means updating the prompt, the knowledge base, or the eval set.

## References

- [CRISP-ML(Q)](https://ml-ops.org/content/crisp-ml): process model and quality assurance method
- AI Engineering from Scratch, Forward-Deployed AI Engineer path:
  - [L47 Outcomes before output](https://aiengineeringfromscratch.com/lesson?path=phases%2F14-agent-engineering%2F47-outcomes-before-output&learningPath=forward-deployed-ai-engineer)
  - [L48 Discover the real workflow](https://aiengineeringfromscratch.com/lesson?path=phases%2F14-agent-engineering%2F48-discover-the-real-workflow&learningPath=forward-deployed-ai-engineer)
  - [L49 Map assumptions and risk](https://aiengineeringfromscratch.com/lesson?path=phases%2F14-agent-engineering%2F49-map-assumptions-and-risk&learningPath=forward-deployed-ai-engineer)
  - [L50 Choose the smallest testable slice](https://aiengineeringfromscratch.com/lesson?path=phases%2F14-agent-engineering%2F50-choose-the-smallest-testable-slice&learningPath=forward-deployed-ai-engineer)
  - [L51 Write specifications that preserve judgment](https://aiengineeringfromscratch.com/lesson?path=phases%2F14-agent-engineering%2F51-write-specifications-that-preserve-judgment&learningPath=forward-deployed-ai-engineer)
- [AWS Well-Architected Generative AI Lens](https://docs.aws.amazon.com/pdfs/wellarchitected/latest/generative-ai-lens/generative-ai-lens.pdf#generative-ai-lifecycle): secondary source for GenAI-specific best practices
