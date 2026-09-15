# Spec quality checklist

**Version**: 1.0.0

`plan` Step 6 walks this against the draft before anything is written. For each
failing item: quote the offending text, fix it, re-check. Three passes maximum;
report anything still failing rather than shipping it quietly.

This is a self-review, not paperwork. Two items on it — testable acceptance
criteria and a real interface — account for most of what makes `implement` go
wrong, so spend the time there.

## Traceability

- [ ] The component's `Serves:` names at least one `CAP-NNN` that exists in
      `requirements.md`.
- [ ] Every architecture constraint is cited as `AD-NNN`, not restated in prose.
- [ ] Nothing in the spec contradicts a cited `AD` or `CAP`. (If it does, that is
      a `specify` amendment, not a spec edit — surface it.)
- [ ] Every dependency is in the component index, with a `@version` pin.

## Purpose and boundaries

- [ ] Purpose says what the component **owns**, in 2–4 sentences.
- [ ] Purpose says what it deliberately does **not** own, where a neighbour could
      plausibly grow into it.
- [ ] `Out of scope` lists the extensions a reader would otherwise assume are
      included. Each is surprising enough to be worth a line.
- [ ] Division of responsibility with each neighbouring component is unambiguous:
      for every piece of state and every computation, exactly one component owns it.

## Interface

- [ ] Concrete signatures — names, parameter types, return types, raised errors.
      No prose descriptions standing in for a signature.
- [ ] A reader could call every method from this section alone, without reading
      the rest of the document.
- [ ] No method exists that the Purpose or a cited `CAP` doesn't require.
      (Speculative surface belongs in `Out of scope`.)
- [ ] Sync vs. async is explicit for every operation that could be either.
- [ ] Where a value could be passed in or inferred, the spec says which.

## Behavior

- [ ] Empty and malformed input are covered.
- [ ] Every dependency failure mode is covered: timeout, error response,
      unavailable.
- [ ] Concurrency is addressed: can two calls overlap, and what happens if they do.
- [ ] Idempotency is addressed: what happens if the same call arrives twice.
- [ ] Partial failure is addressed: what state is left behind if it fails halfway.
- [ ] Every error in the Errors table says whether it is handled here or surfaced
      to the caller — and the caller's obligation is stated for the surfaced ones.

## Acceptance criteria

- [ ] Every criterion has an `AC-NNN` id.
- [ ] Every criterion names a concrete input and a checkable outcome. You can
      picture the assertion.
- [ ] No criterion uses "gracefully", "correctly", "appropriately", "as expected",
      "reasonable", or "properly" — each of those hides the actual requirement.
- [ ] Failure paths are covered, not just the happy path.
- [ ] Every public interface method has at least one criterion.
- [ ] Every NON-NEGOTIABLE constitution principle that applies to this component
      has a criterion that would fail if it were violated.
- [ ] Every stated threshold, limit, or timeout appears in a criterion as a number.
- [ ] A test writer with only this section and the Interface could write the whole
      test file. **This is the item that matters most — if it fails, fix it before
      any other.**

## Constitution

- [ ] Every principle in the constitution has a row in the Constitution check
      table. None skipped.
- [ ] No row reads `Violation` against a NON-NEGOTIABLE principle. (If one does,
      stop — resolve it with the user, don't write the file.)
- [ ] Every `Deviation` row has a Complexity entry naming what was rejected and why.
- [ ] Each principle's own `Gate:` line was the thing actually checked, not a
      paraphrase of the principle.

## Unclear markers

- [ ] Every open decision is a marker, not a plausible-looking guess.
- [ ] Every marker has a unique `U-NNN`, a question someone can answer, and a
      `**Blocks**:` line.
- [ ] `**Blocks**` is scoped honestly — naming the sections genuinely affected,
      not the whole spec out of caution, and not `none` out of convenience.
- [ ] Every marker offers concrete options where options exist.
- [ ] No marker restates a question the constitution or `requirements.md` already
      answers. (Go read them again before raising one.)
- [ ] Every marker will appear in the stage's final report.

## Mechanics

- [ ] Header block is complete: `ID`, `Version`, `Status`, `Ratified`,
      `Last Amended`.
- [ ] `Status` is `Draft` while any blocking marker remains.
- [ ] Filename is kebab-case of the component name, flat in `specs/`.
- [ ] `Related doc updates once implemented` lists everything this spec's decisions
      make wrong elsewhere — or is empty because nothing is.
- [ ] `python3 .specify/toolkit/sdd.py check` exits 0.
