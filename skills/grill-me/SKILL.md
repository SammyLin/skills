---
name: grill-me
description: >-
  Stress-test a plan, design or decision by asking the user only about the decisions that matter,
  settling the rest with stated defaults, and recording the big ones as docs (an ADR, glossary
  terms) as they are made. Use when the user says "grill me", wants a plan challenged before
  building, or asks to think a design through. Lighter than a relentless interview: a few rounds,
  a few questions each, then done.
---

# Grill me

Reach a shared understanding of the plan before anything is built, without wearing the user out.
A relentless interview asks about every branch; this one asks only where a wrong guess would be
expensive, and decides the rest out loud so the user can overrule it at a glance.

Talk to the user in their language.

## 1. Map, then sort

Read what exists first: the plan as stated, the code it touches, `GLOSSARY.md` and `docs/adr/` if
present. Finding facts is your job; never ask the user something you can look up. Use a sub-agent
for a wide search so the conversation keeps moving.

Then list every open decision the plan contains, and sort each one:

**Major** (ask the user) when at least one is true:

- **Hard to reverse.** Changing it later means a migration, a rewrite, a broken contract or lost
  data: the schema, the data model, a public API, the auth model, the hosting or a vendor with
  lock-in.
- **Touches people, money or safety.** What users see or lose, pricing and billing, security,
  privacy, legal or compliance.
- **Blocks other decisions.** Several later choices depend on it.
- **A real fork with no safe default.** Reasonable people would pick differently and the plan
  does not say which.
- **Contradicts something.** The plan disagrees with the code, an existing ADR, the glossary, or
  itself.

**Minor** (decide it yourself) is everything else: naming, file layout, library choice inside an
existing stack, copy, styling, error messages, defaults that are cheap to change later.

When unsure, it is minor. A wrong minor default costs one edit; a pointless question costs the
user's attention.

## 2. Ask in short rounds, as choices

Ask the major decisions whose prerequisites are settled, **at most four per round**, most
consequential first. The user should answer by picking, not by typing.

**With a choice tool** (Claude Code: `AskUserQuestion`; any agent's equivalent), one call per
round, one question per major decision:

- **Stand alone.** The dialog may hide everything you wrote before it, so each question names the
  decision and the fact that makes it matter ("The orders table is shared with billing: should
  refunds…"), in one or two sentences.
- **2-4 options**, each a real choice with its cost in the description. Your recommendation is
  the first option, its label ending in "(Recommended)". Do not add an "Other" option; the tool
  adds one for free text.
- **Short header** (a few words) naming the decision, so the user sees at a glance what each tab is.
- **`preview`** when options are concrete artifacts worth comparing side by side: two schemas, two
  API shapes, two folder layouts.
- **`multiSelect`** only when the choices genuinely combine (which platforms to support), never
  for either/or decisions.
- **Defaults.** Before the call, list the minor decisions you are settling yourself in a short
  text block. If the round has a free slot, use it for one question: "Use these defaults: <the
  list in one line>?" with options "Use them (Recommended)" and "I want to change some". If the
  user wants changes, ask which in the next round.

**Without a choice tool**, write the round as numbered questions with lettered options so the user
can answer in one line ("1A 2B 3A"):

```
**1 · <title>**: <the decision and why it matters>
  A. <option> (Recommended): <cost>
  B. <option>: <cost>

**2 · <title>**: ...

**Defaults I'll use unless you say otherwise**
- <decision>: <default>
```

Either way, never put in one round a question whose answer depends on another question still
open in the same round; it waits for the next round.

Each answer can make a minor decision major or settle several at once. Re-sort after every round.
Aim to be done in **three rounds or fewer**. If major questions are still coming after three, say
so and ask whether to continue or proceed with your recommendations.

Do not:

- re-ask anything the user already answered or the code already shows;
- ask about the same decision twice in different words;
- invent edge cases for their own sake. Raise an edge case only when it changes a major decision.

## 3. Write down what was decided

As major decisions settle, record them; do not batch these to the end.

- **ADR** in `docs/adr/` only when the decision is hard to reverse, would surprise a future reader,
  and came from a real trade-off. All three; otherwise skip it. Format: [ADR-FORMAT.md](ADR-FORMAT.md).
  Most sessions produce zero or one ADR.
- **Glossary** in `GLOSSARY.md` only for a term that actually caused confusion in this session
  (two words for one thing, one word for two things), or that the code and the user use
  differently. Format: [GLOSSARY-FORMAT.md](GLOSSARY-FORMAT.md). No implementation details there.

Create these files lazily, only when there is something to write. Minor defaults are not
documented anywhere except the summary below. If the project keeps no docs and the user does not
want them, skip this step.

## 4. Close

When no major decision is open, finish with one summary:

```
**Decided**
- <major decision>: <answer>   (ADR 0003 if one was written)

**Defaults**
- <minor decision>: <default>

**Still open, not blocking**
- <anything deliberately left for later>
```

Then ask for the go-ahead the same way as the rounds: with a choice tool, one question ("Build
with this plan?") with options such as "Yes, start (Recommended)", "Change something first" and
"Stop here, plan only"; without one, a one-line question. Do not start building until the user
picks yes.

---

Adapted from Matt Pocock's [`grill-with-docs`](https://github.com/mattpocock/skills) (`grilling` +
`domain-modeling`), MIT. The ADR and glossary formats are his, unchanged.
