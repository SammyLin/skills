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

## 2. Ask in short rounds

Ask the major decisions whose prerequisites are settled, **at most four per round**, most
consequential first. Put the minor ones in the same message as a list of defaults the user can
skim. Format:

```
**Q1 · <title>**: <the decision, the options, and what each costs>
→ Recommended: <your answer, one line on why>

**Q2 · <title>**: ...
→ Recommended: ...

**Defaults I'll use unless you say otherwise**
- <decision>: <default>
- ...
```

Word each question so "yes" accepts your recommendation. Do not ask a question whose answer
depends on another question still open in the same round; it waits for the next round.

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

Then stop and wait. Do not start building until the user confirms the summary.

---

Adapted from Matt Pocock's [`grill-with-docs`](https://github.com/mattpocock/skills) (`grilling` +
`domain-modeling`), MIT. The ADR and glossary formats are his, unchanged.
