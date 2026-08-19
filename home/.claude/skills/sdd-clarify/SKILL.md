---
name: sdd-clarify
description: Identifies underspecified areas in a feature spec by asking up to 5 targeted clarification questions, and encodes the answers directly back into specs/NNN-feature/spec.md.
user_invocable: true
---

# Specification Clarifier

This skill guides Claude to detect and reduce ambiguity or missing decisions in an existing feature specification, recording clarifications directly in the spec file.

**Position in the SDD pipeline**: Specify → **Clarify** (optional) → Plan. This is expected to run — and complete — before `sdd-plan`. If the user explicitly says they're skipping clarification (e.g. an exploratory spike), you may proceed, but must warn that the risk of downstream rework increases. Input: `specs/NNN-feature/spec.md` (required — if missing, tell the user to run `sdd-specify` first; do not create a new spec here). Output: the same file, updated in place.

---

## Step 1: Load Context

1. Load `specs/NNN-feature/spec.md`. If ambiguous which feature, ask, or use the most recently modified `specs/` directory that has a `spec.md`.
2. If it exists, load `docs/constitution.md` for governance constraints.

## Step 2: Scan for Ambiguity

Perform a structured coverage scan against this taxonomy. For each category, mark internally: Clear / Partial / Missing.

- **Functional Scope & Behavior**: core user goals & success criteria, explicit out-of-scope declarations, role/persona differentiation.
- **Domain & Data Model**: entities/attributes/relationships, identity & uniqueness rules, lifecycle/state transitions, scale assumptions.
- **Interaction & UX Flow**: critical journeys/sequences, error/empty/loading states, accessibility or localization notes.
- **Non-Functional Quality**: performance (latency/throughput targets), scalability, reliability/availability, observability, security & privacy, compliance.
- **Integration & External Dependencies**: external services/APIs and failure modes, import/export formats, protocol/versioning assumptions.
- **Edge Cases & Failure Handling**: negative scenarios, rate limiting/throttling, conflict resolution (e.g. concurrent edits).
- **Constraints & Tradeoffs**: technical constraints, explicit tradeoffs or rejected alternatives.
- **Terminology & Consistency**: canonical glossary terms, avoided synonyms/deprecated terms.
- **Completion Signals**: acceptance-criteria testability, measurable definition-of-done indicators.
- **Misc / Placeholders**: TODO markers/unresolved decisions, ambiguous unquantified adjectives ("robust", "intuitive").

For each Partial or Missing category, note it as a candidate question — unless the clarification wouldn't materially change implementation or validation strategy, or is better deferred to planning.

## Step 3: Build a Prioritized Question Queue (internal, max 5)

Each question must be answerable with either a short multiple-choice selection (2-5 mutually exclusive options) or a short-phrase answer (≤5 words). Only include questions whose answers materially impact architecture, data modeling, task breakdown, test design, UX behavior, operational readiness, or compliance validation. Balance category coverage — don't ask two low-impact questions while a high-impact area (e.g. security posture) stays unresolved. If more than 5 categories remain unresolved, pick the top 5 by an (impact × uncertainty) heuristic.

## Step 4: Ask One at a Time (interactive loop)

Present exactly **one** question at a time:

- Lead with `**Question:**` followed by a full interrogative sentence ending in `?`. Never use a topic label, section heading, or requirement ID as the question itself — a label like "Acceptance device/runtime matrix (FR-023)" is invalid. The optional requirement ID may only appear parenthesized *after* the `?`.
- Add one plain-language "why it matters" sentence right after the question.
- For multiple-choice: analyze the options, state your **recommended** one with 1-2 sentences of reasoning (`**Recommended:** Option [X] - <reasoning>`), then render all options as a Markdown table (`Option | Description`), ending with `You can reply with the option letter, accept the recommendation by saying "yes", or provide your own short answer.`
- For short-answer: state your **suggested** answer with brief reasoning (`**Suggested:** <answer> - <reasoning>`), then `Format: short answer (<=5 words). You can accept by saying "yes", or provide your own.`
- If the user says "yes"/"recommended"/"suggested", use your stated answer. Otherwise validate the reply maps to an option or fits the length constraint; if ambiguous, ask a quick disambiguation (doesn't count as a new question).
- Stop asking when all critical ambiguities are resolved, the user signals completion ("done", "good", "no more"), or 5 questions have been asked. Never reveal queued questions in advance.
- If no valid questions exist at the start, report immediately that no critical ambiguities were found and suggest proceeding.

## Step 5: Integrate Each Accepted Answer Immediately

After each accepted answer (don't batch — write after every single one):

1. On the first integration this session, add a `## Clarifications` section (right after the highest-level overview section) with a `### Session YYYY-MM-DD` subheading.
2. Append `- Q: <question> → A: <final answer>` under it.
3. Apply the clarification to the most relevant section(s): functional ambiguity → Functional Requirements; interaction/actor distinction → User Stories; data shape → Key Entities (add fields/types/relationships); non-functional constraint → Success Criteria (turn a vague adjective into a metric); edge case/negative flow → Edge Cases; terminology conflict → normalize the term across the spec (keep the old term once, parenthesized, only if necessary).
4. If the clarification invalidates an earlier ambiguous statement, replace it — don't leave contradictory text behind.
5. Save the spec file after each integration. Preserve formatting and heading hierarchy; don't reorder unrelated sections.

## Step 6: Re-validate

- Exactly one bullet per accepted answer, no duplicates; total asked ≤ 5.
- No lingering vague placeholder the new answer was meant to resolve; no contradictory earlier statement remains.
- Consistent terminology across all updated sections.
- If `specs/NNN-feature/checklists/requirements.md` exists, re-check each checkbox item against the updated spec and toggle only the ones whose state actually changed (leave everything else untouched to avoid noisy diffs). Track newly-passing, regressions, and still-unchecked items.

## Step 7: Closing

Report: number of questions asked/answered, path to the updated spec, sections touched, checklist before/after pass counts (if applicable) with any regressions flagged, and a coverage summary table (category → Resolved/Deferred/Clear/Outstanding). If Outstanding or Deferred items remain, say so explicitly and suggest whether to proceed to `sdd-plan` or run `sdd-clarify` again later.

## Behavior Rules

- If no meaningful ambiguity is found, say so plainly and suggest proceeding — don't force questions.
- Never exceed 5 total asked questions (retries on the same question don't count as new ones).
- Avoid speculative tech-stack questions unless their absence blocks functional clarity — that's `sdd-plan`'s job.
- Respect early termination signals ("stop", "done", "proceed").
