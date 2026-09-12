---
name: teach
description: Teach the user one concept -- always alongside the alternatives it competes with and when each one wins -- until they can make the decision, then leave a lesson at ~/Work/lessons-learned/<topic>/LESSON.md and spaced-repetition cards at QUESTIONS.md. Use when the user asks to be taught or to genuinely understand something -- "teach me X", "I don't understand these options", "what are the tradeoffs between A and B", "explain X properly" -- and especially when a decision is blocked because the alternatives aren't understood. Not for ordinary code explanations or a one-line factual answer.
---

# Teach

One concept, one session. The session is over when the user can **make the decision
and defend it**, not when the explanation is finished.

A concept taught alone is a definition. A concept taught next to what it competes
with, and the conditions under which each one wins, is a decision the user can
actually make — so **every lesson carries a decision section**, including the ones
asked for as a bare noun.

Every run leaves two artifacts:

| File | What it is |
|---|---|
| `~/Work/lessons-learned/<topic>/LESSON.md` | The explanation, re-readable in six months by someone who wasn't in this conversation. |
| `~/Work/lessons-learned/<topic>/QUESTIONS.md` | `repeater` cards, drilled with spaced repetition. |

Both are written in **pt-BR**, technical terms kept in English and italicised —
matching the user's existing deck at `~/Work/cards/agent-engineering.md`.

---

## 0. Frame it: what, why now, and what it competes with

Three things to pin down, mostly by inference rather than by asking:

- **The concept — exactly one.** If three were asked about, teach the one that
  unblocks the user now and say plainly that the others are separate sessions.
- **Why now.** The decision, the error, the design that made this urgent. When the
  session came out of an SDD `[!UNCLEAR]` marker or an architecture decision, that
  marker's **Options** are the spine of the lesson; read the artifact it lives in
  before teaching anything.
- **The family it belongs to.** See below — this one is never optional.

A lesson that exists to unblock a choice is a different lesson from a survey of a
topic. If *why now* genuinely cannot be inferred, that is the one question worth
asking before starting.

### Every concept is an answer to a question other things also answer

A topic named as a noun — "teach me *diataxis*" — is still a decision. Diátaxis is
one answer to "how do I structure documentation?", and the user cannot judge it
without knowing what the other answers are and when each wins. Teaching the named
thing alone produces someone who can define it and still cannot choose it.

So **always reconstruct the decision**, whether or not the question was phrased as
one:

1. **Name the question** the concept answers, in the user's words, not the
   vendor's. *Diátaxis* → "como organizar a documentação de um projeto?"
2. **Find the real alternatives** — at least two named ones a practitioner would
   recognize, plus the **status quo** (what happens if they change nothing: an ad
   hoc `README` that grows, the framework's default, the thing the team does today).
   The status quo row is frequently the right answer and is the one people forget
   to consider.
3. **Verify the alternatives exist and are current** before naming them. An
   invented or long-dead alternative is worse than none — it teaches a fake map.
   This is search work, not memory work; see section 1.

Alternatives must be genuine contenders on the same question. "Não documentar" is
a status quo row, not a strawman; a tool that solves a different problem entirely
is not an alternative and padding the table with one is dishonest.

## 1. Get the facts right before opening your mouth

Pretrained knowledge is a draft, not a source. In order of weight:

1. **The user's own repository and artifacts.** Read them. A lesson grounded in
   their code outranks any generic treatment of the same idea.
2. **Primary material** — the spec, the official docs, the library source, the paper.
3. **Recognized practitioner writing**, when the question is about practice.
4. Your own knowledge — for stable, textbook material only.

**Search (`WebSearch`/`WebFetch`) is mandatory** when the topic touches a specific
library, tool, version, API, or anything phrased as "current best practice", and
**whenever you are naming the alternatives** for the decision section — that map is
the part of the lesson most likely to be confabulated, and a wrong map is worse
than an admitted gap. Stable concepts (backpressure, idempotency, CAP, B-trees)
don't need a search for the mechanism — but the moment you are about to state a
number, a default, a limit, a version, or a rival's name, verify it.

Every source you actually opened goes in the lesson's `## Fontes`, with one line on
what was taken from it. **Never cite a URL you did not fetch.** Anything you could
not verify is taught flagged as uncertain and flagged in the file too — a hedge the
user can see is worth far more than confidence they cannot check.

## 2. Calibrate, once

Run `ls ~/Work/lessons-learned/` first. An adjacent lesson is the best available
evidence of what the user already knows; read it, build on it, and link it with
`[[slug]]` instead of re-teaching it.

Then at most **one** calibration question, and only if the answer would genuinely
change how you explain. This skill is `grill-me`'s opposite: here you do the
talking, and the testing comes at the end.

## 3. Teach — in the conversation, not in a file

Deliver the whole explanation in the chat first. The file records a lesson that
happened; it does not replace one.

1. **The problem first.** Every concept is an answer to a question. Teach the
   question. The user should feel the pain before hearing the name of the cure.
2. **The mechanism.** How it works one level below the buzzword. If you cannot say
   mechanically what it does, you do not understand it well enough to teach it.
3. **One concrete example, from their world** — their repo, their decision, their
   data. Generic `foo`/`bar` is the sound of a lesson not landing.
4. **Name the tradeoff axis.** Nearly every "which option?" is one axis wearing a
   costume (latency vs. cost, coupling vs. duplication, who owns failure). Name the
   axis and the options stop needing to be memorized — they become derivable.
5. **The options table — always, not only when the user framed a choice:**

   ```markdown
   | Opção | Como funciona | Ganha | Custa | Escolha quando |
   |---|---|---|---|---|
   ```

   Every **Escolha quando** cell states an *observable condition* — "quando o
   caller já tem seu próprio orçamento de latência" — never "quando fizer sentido".
   That column is the roadmap: the user should be able to read only it and decide.
   The table carries the taught concept, the real alternatives, and the status quo
   row from section 0 — one row each, judged on the same criteria.
6. **Recommend, for their case, with the reason — and say what would change your
   mind.** A teacher who refuses to recommend leaves the user exactly as stuck as
   they started.
7. **Mark what is contested.** Where practitioners genuinely disagree, say so and
   say why. Where a question is settled, say that too. Confidence is information.

Depth over coverage: three things understood beat nine things listed. Write prose,
not an outline of headings with a sentence under each.

## 4. Check before you write

Ask **2–3 retrieval questions and wait for answers.** This step is not optional and
does not happen after the files are written.

- **Free recall, not multiple choice.** Recognition impersonates understanding and
  then dies in the first drill.
- **At least one application question**: "dado <a situação real do usuário>, qual
  você escolheria, e o que mudaria sua resposta?"
- **At least one question probes the decision map**: "em que situação você *não*
  usaria isto, e o que usaria no lugar?" Someone who cannot answer that learned a
  definition, not a decision.
- **Grade honestly and specifically.** "Quase lá" teaches nothing — say which part
  is wrong and why.
- A miss on something fundamental means **teach that part again, now**. Do not
  write files over a hole in the lesson.

What the user got wrong is the most valuable output of the session: it decides what
the lesson emphasizes and which cards get written.

## 5. Write the lesson

```
~/Work/lessons-learned/<topico-em-kebab-case>/LESSON.md
```

**Check for an existing lesson on this topic first**, by meaning and not by exact
slug — `agentes-react` and `padrao-react` are the same lesson. If one exists,
**extend it**: add to its sections, add a dated line to the header, and leave what
is already written alone. Never create a rival file on the same subject.

```markdown
# <Conceito>

**Ensinado em**: <YYYY-MM-DD>
**Por que**: <a decisão ou problema que motivou esta aula>
**Relacionado**: [[outra-licao]]

## O problema
<a pergunta que o conceito responde>

## Como funciona
<o mecanismo, um nível abaixo do jargão>

## A decisão
<A pergunta que este conceito responde, e que outras coisas também respondem.
Uma seção obrigatória, mesmo quando a aula foi pedida como um substantivo solto.>

| Opção | Como funciona | Ganha | Custa | Escolha quando |
|---|---|---|---|---|
| <o conceito ensinado> | | | | |
| <alternativa real 1> | | | | |
| <alternativa real 2> | | | | |
| <manter como está hoje> | | | | |

## Recomendação
<a escolha para o caso do usuário, o porquê, e o que mudaria essa escolha>

## Armadilhas
<os erros cometidos na checagem da seção 4, escritos como aviso>

## Não confunda com
<os vizinhos próximos que costumam ser confundidos com isto>

## Fontes
- <URL> — <o que foi tirado daqui>
```

The lesson stands alone: no "como discutimos", no "a opção acima", nothing that
depends on this conversation still being in scroll-back.

## 6. Write the cards

`QUESTIONS.md`, beside the lesson. `repeater`'s format, exactly:

```
Q: <pergunta>
A: <resposta>
---
Q: <pergunta>
A: <resposta>
```

`Q:` and `A:` start a line; answers may span several lines and use markdown. A line
of exactly `---` separates cards; none is needed after the last. Verify with:

```bash
repeater check --plain ~/Work/lessons-learned/<topico>
```

"Cards found" must equal the number written. If it doesn't, the format is wrong —
fix it before reporting.

**Append only.** If the file exists, read it and add the new cards at the end.
Never edit, reorder or reformat cards already there: they carry review history in
`repeater`'s database, and a rewritten card is a new card with its schedule reset.
Dedupe against what is already in the file — a question already asked is not asked
again; write a distinct, deeper card instead.

| Card rule | Why |
|---|---|
| One fact per card. | A card with five things to recall is five cards you always half-fail. |
| Standalone. | No "a opção acima", no dependence on card order — drills shuffle. |
| Prefer *por quê* and *quando* over *o quê*. | Definition cards are cheap and change no decision. "Quando escolher X em vez de Y?" is the card that pays off. |
| One card per **Escolha quando** row of the decision table — the alternatives and the status quo included, not only the taught concept. | That is the whole point of the lesson. |
| At least one card asks when *not* to use the taught concept, and what wins instead. | Knowing where a tool stops is what separates choosing it from defaulting to it. |
| Every mistake from section 4 becomes a card. | Non-negotiable — the known gap is the highest-value card in the deck. |
| No yes/no answers. | They are guessable, so they measure nothing. |
| The answer must be short enough to grade yourself honestly. | If you can't tell whether you got it right, the card is broken. |
| 5–10 cards per session. | More is not retention, it's a chore that gets abandoned. |

## 7. Close the session

Report, briefly:

- The decision the user arrived with, answered in one line. That is what this was for.
- The two paths written, and the card count.
- How to drill:

```bash
repeater drill ~/Work/lessons-learned/<topico>   # só esta aula
repeater drill ~/Work/lessons-learned            # tudo
```

## Failure modes

| Failure | Required behaviour instead |
|---|---|
| Writing the files without teaching and checking in the conversation first. | Sections 3 and 4 come first, always — unless the user explicitly says "just write it". |
| Listing options with pros and cons but no "escolha quando" and no recommendation. | Both are mandatory. Balanced-sounding paralysis is the exact failure this skill exists to prevent. |
| Teaching a concept the user named as a noun as though it had no rivals — "teach me *diataxis*" answered with only Diátaxis. | Reconstruct the question it answers, name the real alternatives and the status quo, and fill the decision section. This is never optional and never inferred from how the request was phrased. |
| Naming alternatives from memory, or padding the table with things that answer a different question. | Verify each one exists and is current (section 1). Two honest alternatives beat five invented ones, and the status quo row is always one of them. |
| Teaching a survey when the user was blocked on a decision. | Re-read *why now*. The options in the marker are the spine of the lesson. |
| Citing a source you didn't fetch, or stating a version, default or limit from memory. | Fetch it, or teach it flagged as uncertain — in the chat *and* in `## Fontes`. |
| Multiple-choice comprehension questions. | Free recall. Recognition is not retention. |
| Proceeding to the files after the user missed something fundamental. | Teach that part again first. |
| Rewriting or reordering an existing `QUESTIONS.md`. | Append only. Existing cards carry review history. |
| A second lesson file on a topic already covered. | Find it by meaning and extend it. |
| Twenty cards "to be thorough". | 5–10, weighted toward what the user actually got wrong. |
| A lesson that only makes sense with this conversation in scroll-back. | It must read standalone in six months. |
| Interviewing the user about what they want taught. | One calibration question at most. `grill-me` is the skill for interviewing; this one is for teaching. |
