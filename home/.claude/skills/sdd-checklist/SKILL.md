---
name: sdd-checklist
description: Generates a custom, domain-specific quality checklist for a feature — "unit tests for English" that validate the requirements' completeness, clarity, and consistency, not the implementation.
user_invocable: true
---

# Checklist Generator (Requirements Quality)

**Core concept**: a checklist produced by this skill is a **unit test suite for requirements writing**, not a test plan for the implementation.

- ❌ NOT "Verify the button clicks correctly" / "Test error handling works" / "Confirm the API returns 200"
- ❌ NOT checking whether code matches the spec
- ✅ "Are visual hierarchy requirements defined for all card types?" (completeness)
- ✅ "Is 'prominent display' quantified with specific sizing/positioning?" (clarity)
- ✅ "Are hover-state requirements consistent across all interactive elements?" (consistency)

If the spec is code written in English, the checklist is its unit test suite: it tests whether the requirements are well-written, complete, unambiguous, and ready for implementation — not whether the implementation works.

**Position in the SDD pipeline**: optional, can run any time after `sdd-specify` (and typically also after `sdd-plan`/`sdd-tasks`, for domains like performance or security that only become concrete once the plan exists). Output: `specs/NNN-feature/checklists/[domain].md`.

**Ownership**: a checklist generated here is a reviewer-owned artifact. `[x]` means the reviewer judged the requirements-quality criterion satisfied — it does **not** mean implementation work is complete. This command only ever generates or appends items; it must never mark an item `[x]` itself. (Note: `checklists/requirements.md`, produced by `sdd-specify`/`sdd-clarify`, is a separate built-in spec-quality checklist — this exception doesn't apply to the custom checklists generated here.)

---

## Step 1: Clarify Intent (up to 3 questions, dynamic)

Derive up to three contextual clarifying questions from the user's request plus signals already visible in spec/plan/tasks — no pre-baked catalog. Skip any question already unambiguous from what the user said.

1. Extract signals: domain keywords (auth, latency, UX, API...), risk indicators ("critical", "must", "compliance"), stakeholder hints ("QA", "review", "security team"), explicit deliverables ("a11y", "rollback", "contracts").
2. Cluster into up to 4 candidate focus areas, ranked by relevance.
3. Identify probable audience & timing (author, reviewer, QA, release) if not explicit.
4. Detect missing dimensions: scope breadth, depth/rigor, risk emphasis, exclusion boundaries, measurable acceptance criteria.
5. Ask from these archetypes as needed: scope refinement, risk prioritization, depth calibration ("lightweight pre-commit list or a formal release gate?"), audience framing, boundary exclusion, scenario-class gap ("no recovery flows detected — are rollback/partial-failure paths in scope?").

If presenting options, use a compact table (`Option | Candidate | Why It Matters`), max A-E. Never ask the user to restate what they already said. If ≥2 scenario classes (Alternate/Exception/Recovery/Non-Functional) remain unclear after the first round, you may ask up to 2 more (max 5 total), each with a one-line justification. Defaults when interaction isn't possible: Depth = Standard, Audience = Reviewer (PR) if code-related else Author, Focus = top 2 relevance clusters.

## Step 2: Load Feature Context

Read from `specs/NNN-feature/`: `spec.md` (requirements and scope), `plan.md` if it exists (technical details, dependencies), `tasks.md` if it exists (implementation tasks). Load only what's relevant to the active focus areas — summarize rather than dumping full files.

## Step 3: Generate the Checklist

- Create `specs/NNN-feature/checklists/` if needed.
- Filename: short and descriptive, `[domain].md` (e.g. `ux.md`, `api.md`, `security.md`).
- If the file doesn't exist: create it, numbering items from `CHK001`. If it exists: **append**, continuing from the last ID used — never delete or replace existing content.
- Leave every newly generated item unchecked (`[ ]`) — checkbox state belongs to the reviewer.

**Core principle — test the requirements, not the implementation.** Every item must evaluate the requirements themselves for:
- **Completeness** — are all necessary requirements present?
- **Clarity** — are they unambiguous and specific?
- **Consistency** — do they align with each other?
- **Measurability** — can they be objectively verified?
- **Coverage** — are all scenarios/edge cases addressed?

Group items under category headings such as: Requirement Completeness, Requirement Clarity, Requirement Consistency, Acceptance Criteria Quality, Scenario Coverage, Edge Case Coverage, Non-Functional Requirements, Dependencies & Assumptions, Ambiguities & Conflicts.

**Item format**: a question about requirement quality, referencing what's written (or missing) in the spec/plan, tagged with its quality dimension in brackets, and — for ≥80% of items — a traceability reference: `[Spec §X.Y]` when checking an existing requirement, or `[Gap]` / `[Ambiguity]` / `[Conflict]` / `[Assumption]` when checking for something missing.

Examples:
- "Are error handling requirements defined for all API failure modes? [Gap]"
- "Is 'fast loading' quantified with specific timing thresholds? [Clarity, Spec §NFR-2]"
- "Do navigation requirements align across all pages? [Consistency, Spec §FR-10]"
- "Are requirements defined for zero-state scenarios (no items)? [Coverage, Edge Case]"
- "Can 'balanced visual weight' be objectively verified? [Measurability, Spec §FR-2]"

**Absolutely prohibited** (these test implementation, not requirements): items starting with "Verify"/"Test"/"Confirm"/"Check" + a behavior; references to code execution, clicks, navigation, rendering; "displays correctly"/"works properly".

**Consolidation**: if raw candidate items exceed ~40, prioritize by risk/impact; merge near-duplicates; collapse more than 5 low-impact edge cases into a single item ("Are edge cases X, Y, Z addressed in requirements? [Coverage]").

## Step 4: Report

Output the full checklist file path, item count, and whether this run created a new file or appended to one. Summarize the focus areas selected, depth level, audience/timing, and any explicit must-have items the user requested. Mention that multiple checklists can coexist per feature (`ux.md`, `security.md`, ...) and suggest cleaning up obsolete ones when a feature is done.
