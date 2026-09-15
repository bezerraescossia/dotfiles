---
name: teach
description: Research one concept -- always alongside the alternatives it competes with and when each one wins -- and write it up as a lesson inside the project it belongs to, at .specify/lessons/<topic>.md, falling back to ~/Work/lessons-learned/<topic>.md outside a repo -- with spaced-repetition cards appended to the one shared deck at ~/Work/lessons-learned/QUESTIONS.md. The explanation goes in the file, not in the chat. Use when the user asks to be taught or to genuinely understand something -- "teach me X", "I don't understand these options", "what are the tradeoffs between A and B", "explain X properly" -- and especially when a decision is blocked because the alternatives aren't understood. Not for ordinary code explanations or a one-line factual answer.
---

# Teach

One concept, one session. The lesson is done when someone reading **only the file**
could make the decision and defend it — not when the explanation is finished.

A concept taught alone is a definition. A concept taught next to what it competes
with, and the conditions under which each one wins, is a decision the user can
actually make — so **every lesson carries a decision section**, including the ones
asked for as a bare noun.

**The explanation lives in the file, never in the chat reply.** Do not deliver the
lesson, an outline of it, a summary of it, or a preview of the options table in the
conversation. Research it, write it, and report where it landed (section 5).
Questions are still welcome in the chat — clarifying ones, not teaching ones.

Every run leaves two artifacts, and they live in **different places on purpose**:

| File | What it is |
|---|---|
| `<projeto>/.specify/lessons/<topic>.md` | The explanation, beside the code whose decision prompted it and committed with it. One flat file per lesson — never a folder. Section 3 resolves the directory. |
| `~/Work/lessons-learned/QUESTIONS.md` | The single global deck of `repeater` cards — every lesson from every project, each under its own `## <topic>` heading. Appended to, never rewritten. |

The lesson is project context: it explains a decision the repo now carries, so it belongs
to the repo. The cards are a daily habit: one deck means one `repeater drill`, and a
project you archive next year doesn't quietly take its cards out of rotation with it.

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
- **What the project has already settled.** When a `.specify/` was found, read
  `memory/constitution.md`, `specs/requirements.md` and the spec that raised the
  marker *before* teaching. A NON-NEGOTIABLE principle or a decided `AD-NNN` can
  already foreclose one of the options — and an option this project cannot take is
  a row in the table **marked as foreclosed, with the principle or `AD` cited**,
  never a recommendation and never silently dropped. The user still needs to know
  it exists and why it is off the table here.
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

## 1. Get the facts right before writing a word

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
not verify goes in the file flagged as uncertain — a hedge the user can see is
worth far more than confidence they cannot check.

## 2. Calibrate, once

Resolve the lessons directory first — section 3's block, which sets `$lessons` and
is needed here before it is needed there. Then look at what has already been taught,
in **two** places, because lessons are spread across projects while the deck is
global:

```bash
ls "$lessons"/*.md 2>/dev/null                      # this project's lessons
grep -n '^## \|^<!-- lição' ~/Work/lessons-learned/QUESTIONS.md
```

The deck's headings and their pointer comments are the index of every lesson
anywhere, including the ones in other repos. An adjacent lesson is the best
available evidence of what the user already knows; read it, build on it, and link
it with `[[slug]]` instead of re-teaching it.

Then at most **one** calibration question, and only if the answer would genuinely
change how you write it. Ask anything that is genuinely unclear — which of three
topics they meant, which decision this is for, which stack it applies to — but do
not interview them about what they want taught, and do not quiz them.

## 3. Write the lesson

### Where it goes

The lesson belongs to the project whose decision prompted it. Resolve the
directory before writing anything — the walk upward mirrors `sdd.py`'s own
`find_root()`, so `teach` lands in the same project every other stage does:

```bash
d=$(pwd); lessons=""
while [ "$d" != "/" ]; do
  [ -d "$d/.specify" ] && { lessons="$d/.specify/lessons"; break; }
  d=$(dirname "$d")
done
[ -z "$lessons" ] && r=$(git rev-parse --show-toplevel 2>/dev/null) && [ -n "$r" ] \
  && lessons="$r/.specify/lessons"
[ -z "$lessons" ] && lessons="$HOME/Work/lessons-learned"
mkdir -p "$lessons"
echo "$lessons"
```

1. **A `.specify/` here or in any parent** → `<projeto>/.specify/lessons/`.
2. **A git repo without the pipeline** → create `.specify/lessons/` at the git root
   anyway. The lesson still belongs with that code.
3. **Neither** → `~/Work/lessons-learned/`, as before.

```
$lessons/<topico-em-kebab-case>.md
```

A flat file in that directory. No directory per lesson, no `LESSON.md`: the slug is
the filename, and it is also the `[[slug]]` other lessons link to and the
`## <slug>` heading its cards live under in the global deck.

Cases 1 and 2 put the lesson under version control. It gets committed and read by
whoever opens the project later — which is the point, and also the bar: it has to
stand on its own for someone who was never in this conversation.

**Check for an existing lesson on this topic first**, by meaning and not by exact
slug — `agentes-react` and `padrao-react` are the same lesson.

- **In this project** → **extend it**: add to its sections, add a dated line to the
  header, leave what is already written alone. Never a rival file on the same subject.
- **In another project** (found via the deck's pointer comments) → it cannot be
  extended in place; that file belongs to that repo. Read it, link it `[[slug]]`,
  and write **only what is specific to this project** — the constraint here, the
  decision here, why the answer differs. Re-teaching what that file already says is
  how two lessons start contradicting each other.

The bar for what goes in the file — all of it, in prose, not an outline of headings
with a sentence under each:

1. **The problem first.** Every concept is an answer to a question. Write the
   question. The reader should feel the pain before hearing the name of the cure.
2. **The mechanism.** How it works one level below the buzzword. If you cannot say
   mechanically what it does, you do not understand it well enough to write it.
3. **One concrete example, from their world** — their repo, their decision, their
   data. Generic `foo`/`bar` is the sound of a lesson not landing.
4. **Name the tradeoff axis.** Nearly every "which option?" is one axis wearing a
   costume (latency vs. cost, coupling vs. duplication, who owns failure). Name the
   axis and the options stop needing to be memorized — they become derivable.
5. **The decision section — always, not only when the user framed a choice.** It
   is a narrow two-column map followed by one subsection per option. The map carries
   the taught concept, the real alternatives, and the status quo row from section 0
   — one row each, judged on the same criteria. Every **Escolha quando** states an
   *observable condition* — "quando o caller já tem seu próprio orçamento de
   latência" — never "quando fizer sentido". That column is the roadmap: the user
   should be able to read only it and decide. The prose that used to be crammed
   into `Ganha`/`Custa` cells goes in the per-option subsections, where it has room.
6. **Recommend, for their case, with the reason — and say what would change your
   mind.** A lesson that refuses to recommend leaves the user exactly as stuck as
   they started.
7. **Mark what is contested.** Where practitioners genuinely disagree, say so and
   say why. Where a question is settled, say that too. Confidence is information.

Depth over coverage: three things understood beat nine things listed.

### Tables must fit the screen

The lesson is read in `nvim`, where a table row longer than the window wraps and
the whole table collapses into unreadable fragments — a five-column table of full
sentences renders as garbage no matter how the renderer is configured. So:

- **At most two columns**, and the whole row under ~100 characters.
- **Cells are labels, not sentences** — a few words, no commas doing the work of a
  period. Anything that needs a sentence belongs in prose under the table.
- Tables are for *scanning between* options. Explaining one option is prose.

Check it before reporting, on the lesson and on the deck:

```bash
awk 'length($0) > 100 && /^\|/ {print FILENAME":"FNR" — "length($0)" cols"}' \
  "$lessons"/<topico>.md
```

Any line it prints is a broken table row. Split the content out into prose; do not
"fix" it by shortening the words while keeping five columns.

```markdown
# <Conceito>

**Ensinado em**: <YYYY-MM-DD>
**Projeto**: <nome do repo — ou `nenhum` quando a aula é global>
**Por que**: <a decisão ou problema que motivou esta aula. Quando veio de um
marcador, nomeie-o: `U-007 (llm-router.md) — quem é dono do retry?`>
**Relacionado**: [[outra-licao]]

## O problema
<a pergunta que o conceito responde>

## Como funciona
<o mecanismo, um nível abaixo do jargão>

## A decisão
<A pergunta que este conceito responde, e que outras coisas também respondem.
Uma seção obrigatória, mesmo quando a aula foi pedida como um substantivo solto.>

| Opção | Escolha quando |
|---|---|
| <o conceito ensinado> | <condição observável, poucas palavras> |
| <alternativa real 1> | <condição observável, poucas palavras> |
| <alternativa real 2> | <condição observável, poucas palavras> |
| <manter como está hoje> | <condição observável, poucas palavras> |

<Uma opção que o `constitution.md` ou um `AD-NNN` já fecha para este projeto
continua na tabela, com a condição trocada por `fechada: P-IV` ou `fechada:
AD-014`. O usuário precisa saber que ela existe e por que não está disponível
aqui.>

### <Opção> — uma subseção por linha da tabela, na mesma ordem

**Como funciona**: <o mecanismo desta opção, uma ou duas frases>
**Ganha**: <o que ela compra, em prosa>
**Custa**: <o preço, em prosa — incluindo o caso em que ele não se paga>
**Escolha quando**: <a condição da tabela, agora com o porquê por trás dela>

## Recomendação
<a escolha para o caso do usuário, o porquê, e o que mudaria essa escolha>

## Armadilhas
<onde as pessoas tropeçam na prática: o erro comum, por que ele é tentador, e o
que fazer no lugar. Vem da pesquisa da seção 1, não de suposição.>

## Não confunda com
<os vizinhos próximos que costumam ser confundidos com isto>

## Fontes
- <URL> — <o que foi tirado daqui>
```

The lesson stands alone: no "como discutimos", no "a opção acima", nothing that
depends on this conversation still being in scroll-back.

## 4. Write the cards

One deck for every lesson of every project, at `~/Work/lessons-learned/QUESTIONS.md`
— **always there, never inside `.specify/`**, however the lesson's path resolved.
Never a second `QUESTIONS.md` anywhere. Each lesson owns one `## <slug>` section —
the same slug as its `.md` file — opening with a comment pointing at where that
lesson lives:

```
## <topico-em-kebab-case>
<!-- lição: <caminho absoluto do arquivo da aula> -->

Q: <pergunta>

A: <resposta>

---

Q: <pergunta>

A: <resposta>

---

## <outro-topico>
<!-- lição: <caminho absoluto do arquivo da aula> -->

Q: <pergunta>

A: <resposta>
```

Those comments are the index of every lesson you have written anywhere — section 2
reads them back. Keep the path absolute and correct; a pointer that lies is worse
than none.

**Slugs collide across projects.** If `## <slug>` already exists in the deck and
its pointer names a *different* file, qualify the new one with the project:
`## retry-ownership (ai-service)`. Never merge two projects' cards under one heading.

**A card can outlive its lesson.** The repo may be archived, moved or deleted while
the deck goes on being drilled, so no card may depend on opening the lesson to be
answerable — no "conforme a aula", no "a tabela da lição". The pointer is for
finding context later, never a part of the answer.

`Q:` and `A:` start a line; answers may span several lines and use markdown. A line
of exactly `---` separates cards. **Always leave a blank line between `Q:` and its
`A:`, and around every `---`** — `repeater` parses it either way, but the spaced
form is what this deck is written in and mixing the two makes the file unreadable.
Close a lesson's section with a `---` before the next `## ` heading.

Verify with:

```bash
repeater check --plain ~/Work/lessons-learned/QUESTIONS.md
```

"Cards found" must equal the whole deck — every card already in the file plus the
ones just written. Count before appending and after; if the difference isn't the
number of new cards, the format is wrong — fix it before reporting.

**Append only, to the end of the file.** Read the file first. If the lesson is new,
add its `## <slug>` heading and cards at the bottom; if you are extending an
existing lesson, append under that lesson's existing heading. Never edit, reorder
or reformat cards already there — not other lessons' and not this one's: they carry
review history in `repeater`'s database, and a rewritten card is a new card with
its schedule reset. Dedupe against the whole file, not just this lesson's section —
a question already asked is not asked again; write a distinct, deeper card instead.

| Card rule | Why |
|---|---|
| One fact per card. | A card with five things to recall is five cards you always half-fail. |
| Standalone. | No "a opção acima", no dependence on card order — drills shuffle. |
| Prefer *por quê* and *quando* over *o quê*. | Definition cards are cheap and change no decision. "Quando escolher X em vez de Y?" is the card that pays off. |
| One card per **Escolha quando** row of the decision table — the alternatives and the status quo included, not only the taught concept. | That is the whole point of the lesson. |
| At least one card asks when *not* to use the taught concept, and what wins instead. | Knowing where a tool stops is what separates choosing it from defaulting to it. |
| At least one card comes from `## Armadilhas`. | The pitfall is where the knowledge actually gets tested. |
| No yes/no answers. | They are guessable, so they measure nothing. |
| The answer must be short enough to grade yourself honestly. | If you can't tell whether you got it right, the card is broken. |
| 5–10 cards per session. | More is not retention, it's a chore that gets abandoned. |

## 5. Close the session

The reply is a receipt, not a lesson. At most:

- The decision the user arrived with, answered in **one line** — no reasoning, no
  options, no preview of the table. That lives in the file.
- The lesson's path, and the number of cards appended to the deck.
- Anything you could not verify, named in one line so they know what to distrust.
- **When the session came from an `[!UNCLEAR]` marker**, the resolution line ready
  to paste — `UNCLEAR-PROTOCOL.md`'s `## Clarifications` shape, with the decision
  left blank because it is the user's to make:

```
Para fechar U-007 em llm-router.md:
- **U-007** — Quem é dono do retry? → <sua decisão>. *Rationale*: ver
  .specify/lessons/retry-ownership.md
```

- How to drill:

```bash
repeater drill ~/Work/lessons-learned/QUESTIONS.md   # o deck inteiro
```

### `teach` never writes to a pipeline artifact

It reads `constitution.md`, `requirements.md` and the specs freely. It does not
touch them. No spec edit, no marker deleted, no `## Clarifications` entry appended,
no `sdd.py bump`, no `sdd.py status`.

Two reasons, and both hold even when the answer seems obvious: at the moment the
lesson is written **the user has not decided yet** — that is the entire point of the
session — and resolving a marker is a versioned edit that belongs to the stage that
owns the file, which knows whether the answer is a MINOR or a MAJOR and what it
makes stale. `teach` hands over the line; `plan` or `implement` writes it.

## Failure modes

| Failure | Required behaviour instead |
|---|---|
| Explaining the concept in the chat — the mechanism, the options, a "quick summary", a preview of the table. | The file is the deliverable. The reply is section 5's receipt and nothing more. |
| Quizzing the user, or grading them, in the conversation. | Drilling is `repeater`'s job, from the cards. `grill-me` is the skill for testing. |
| Listing options with pros and cons but no "escolha quando" and no recommendation. | Both are mandatory. Balanced-sounding paralysis is the exact failure this skill exists to prevent. |
| Writing up a concept the user named as a noun as though it had no rivals — "teach me *diataxis*" answered with only Diátaxis. | Reconstruct the question it answers, name the real alternatives and the status quo, and fill the decision section. This is never optional and never inferred from how the request was phrased. |
| Naming alternatives from memory, or padding the table with things that answer a different question. | Verify each one exists and is current (section 1). Two honest alternatives beat five invented ones, and the status quo row is always one of them. |
| Writing a survey when the user was blocked on a decision. | Re-read *why now*. The options in the marker are the spine of the lesson. |
| Citing a source you didn't fetch, or stating a version, default or limit from memory. | Fetch it, or write it flagged as uncertain — in `## Fontes` and in the closing receipt. |
| Rewriting, reordering or reformatting cards already in `QUESTIONS.md` — any lesson's. | Append only, at the end. Existing cards carry review history. |
| A folder per lesson, a `LESSON.md`, or a `QUESTIONS.md` beside the lesson. | One flat `<topico>.md` in the root, and one shared deck at `~/Work/lessons-learned/QUESTIONS.md`. |
| Cards written without the blank lines around `Q:`/`A:` and `---`. | The deck is written in the spaced form; match it. |
| A second lesson file on a topic already covered. | Find it by meaning and extend it. |
| A table with three or more columns, or cells holding full sentences. | Two columns, rows under ~100 characters, cells as labels. The explanation goes in prose under the table — a wide table renders as garbage in `nvim`. |
| Twenty cards "to be thorough". | 5–10, weighted toward the decision table and the pitfalls. |
| Writing to `~/Work/lessons-learned/` when a `.specify/` or a git root was found. | Run section 3's resolution block. The global directory is the last fallback, not the default. |
| Editing a spec, deleting a marker, appending to `## Clarifications`, or running `sdd.py bump`/`status`. | Read the pipeline, never write it. Report the resolution line and let `plan`/`implement` apply it. |
| Recommending an option the constitution or a decided `AD-NNN` already forecloses — or dropping it from the table without saying why. | Keep the row, mark it `fechada: P-IV` / `fechada: AD-014`, and recommend among what is actually available. |
| A lesson that only makes sense with this conversation in scroll-back. | It must read standalone in six months. |
| Interviewing the user about what they want taught. | One calibration question at most, and only when the answer changes what you write. |
