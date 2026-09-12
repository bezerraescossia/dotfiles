# Architecture decision areas (Round D reference)

**Version**: 1.0.0

The menu for `specify` Step 3, Round D. **Ask only what Rounds A–C made relevant**,
and say out loud which areas you skipped and why. Every area you do ask about
becomes one `AD-NNN` row in `requirements.md` with its rationale.

For each: name the decision, offer 2–4 options, and state a *real* tradeoff for each
— the thing that goes wrong if you pick it. "Option B is more scalable" is not a
tradeoff; "Option B survives a provider outage, at the cost of a second set of
prompts to keep in sync" is.

## Always relevant

| Area | The decision | Options and the tradeoff each carries |
|---|---|---|
| **Language / framework** | Runtime for the service(s) | **Python** — best LLM ecosystem fit, most examples; slowest raw runtime. **Node/TypeScript** — one language with a JS frontend; thinner ML tooling. **Go** — best performance and deployment story; the thinnest LLM tooling of the three. |
| **LLM provider strategy** | Single vs. multi-provider | **Single** — simplest, one set of prompts, one failure surface; a provider outage is your outage. **Multi-provider router with fallback** — survives an outage; every prompt must be tuned and evaluated per provider, and quality differs silently. **+ local fallback** — works offline and caps cost; a large quality cliff users will notice. |
| **App database** | Persistence | **None** — stateless, trivial to scale; no conversation history, no usage record, no audit trail. **Relational** — conversations, usage, audit in one place; an operational component with migrations to own. |
| **Auth** | Who is calling | **API key** — service-to-service, simple; no per-user attribution, so no per-user limits or audit. **User identity (OAuth/JWT)** — real attribution and per-user policy; an identity provider to integrate and tokens to refresh. **Both** — necessary once humans and services both call it; two code paths to keep aligned. |
| **Secrets** | Management | **env/`.env`** — zero setup; secrets live in plaintext on every machine that runs it. **Secrets manager** — rotation and audit; infrastructure and a startup dependency. |
| **Observability** | Depth | **Logs only** — enough to debug one service by hand. **+ metrics** — you can see degradation before users report it; dashboards to maintain. **+ distributed tracing** — effectively required once a request crosses more than one service; instrumentation cost on every call path. |
| **Testing / eval** | Beyond unit tests | **Unit only** — fast; prompt and retrieval regressions are invisible. **+ an eval harness with a named held-out set** — catches quality regressions; an eval set to build and defend from contamination. Note: if the constitution mandates one, this is already decided. |
| **CI/CD** | Scope | **CI only** — cheap, catches regressions. **+ deploy to a dev target** — the thing is actually runnable by others. **+ a cloud deploy path** — real delivery; real infrastructure ownership. |
| **Environments** | Profiles | **dev only** — fastest. **dev + prod** — the usual minimum once anyone but you uses it. **dev + staging + prod** — safe rollouts; three sets of config and secrets. |
| **Repo layout** | Structure | **Monorepo** — atomic cross-component changes, one CI. **Polyrepo** — independent release cadence; cross-cutting changes need coordinated PRs. |
| **Deployment target** | Where it runs | **Local containers** — simplest. **Local K8s** — matches production shape; substantial local complexity. **A cloud target** — real, and the operational bill starts. |
| **Package manager** | Per language | Pick the modern default for the chosen language and say which, so `implement` doesn't have to guess. |

## Conditional — ask only if the named capability exists

| Area | Ask when | Options and the tradeoff each carries |
|---|---|---|
| **RAG backend** | Round B needs retrieval | **pgvector** — one datastore to run if you already have Postgres; weaker at very large scale and hybrid search. **A dedicated vector DB** — better recall tooling and filtering; another service to run, back up, and pay for. **An embedded store** (sqlite-vec, FAISS on disk) — no infrastructure at all; no concurrent writers, no horizontal scale. |
| **Chunking & embedding** | Round B needs retrieval | Decide chunk strategy and embedding model *now* — they are the hardest things to change later, because changing either means re-embedding the whole corpus. Record the model name and dimensionality in the `AD`. |
| **Caching** | Cost or latency was raised in Round A/B | **None** — always correct, always pays full price. **In-memory** — free and effective for one instance; wrong the moment there are two. **Shared cache (Redis/memcached)** — correct across instances; a service to run and a staleness policy to decide. |
| **Streaming** | Something is real-time | **SSE** — simplest, works through most proxies, one direction only. **WebSockets** — needed if the client must signal mid-stream (cancel, interrupt); more connection state and more proxy trouble. |
| **Async work** | Round B has background or long-running work | **Inline/synchronous** — simplest; ties up a request worker and caps you at the HTTP timeout. **Queue + worker** — survives restarts and long jobs; a broker, a status surface, and retry/poison-message semantics to design. |
| **Guardrails** | Round C raised safety, moderation, or regulated output | **Custom lightweight checks** — fast, cheap, predictable; only catches what you thought of. **An established framework** — broader coverage; a dependency and its own false positives. **LLM-as-judge** — catches the open-ended cases; adds cost and latency to every request, and can itself be wrong. |
| **Human-in-the-loop** | Round B requires approval before action | Decide where the boundary sits: approve *before* the action, or act and allow undo. The second is far cheaper to build and unacceptable for irreversible actions — say which actions are irreversible. |
| **Service topology** | Always worth one question; the answer usually is "single" | **Single service** — one deploy, one log stream, function calls; scales as one unit. **A few services split by workload** — independent scaling of the expensive part (e.g. ingestion vs. serving); network calls, partial failure, and shared-contract drift. **Full microservices** — real isolation; a large, permanent operational cost. |
| **Model/prompt versioning** | An LLM is in the request path | How is a prompt change versioned, evaluated, and rolled back? Untracked prompt edits are the most common silent regression in LLM products. |
| **Data retention** | Round C raised PII or regulation | What is stored, for how long, and what deletes it. A retention rule with no deletion mechanism is not a rule. |

## The topology question specifically

If the user leans toward more services than "single", state the concrete costs
before recording the decision — not after:

- Every service is another CI pipeline, another deploy, another set of manifests,
  another secret store entry, another on-call surface.
- A function call becomes a network call: it can now be slow, time out, or half-fail.
- Local debugging stops being "run it" and becomes "run the compose file and hope".
- A shared type becomes a contract two repositories must agree on.

Then record the decision the user makes, with those costs named in the rationale, so
the next person can see the tradeoff was made deliberately.
