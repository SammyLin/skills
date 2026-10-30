---
name: grill-me
description: >-
  Stress-test a plan, design or decision by asking the user about every major and medium decision
  as pick-an-option questions, settling only the small stuff with stated defaults, following up on
  the consequences of each answer, and recording the big decisions as docs (an ADR, glossary terms)
  as they are made. Use when the user says "grill me", wants a plan challenged before building, or
  asks to think a design through.
---

# Grill me

Reach a shared understanding of the plan before anything is built. Ask about everything that
shapes the result; decide only the small stuff yourself, out loud, so the user can overrule it at a
glance. Skip the busywork, not the thinking.

Talk to the user in their language.

## 1. Map, then sort

Read what exists first: the plan as stated, the code it touches, `GLOSSARY.md` and `docs/adr/` if
present. Finding facts is your job; never ask the user something you can look up. Use a sub-agent
for a wide search so the conversation keeps moving.

Then list every open decision the plan contains, and sort each into one of three tiers.

**Major** (ask first) when at least one is true:

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

**Medium** (ask after the major ones) when it shapes what gets built, though it can be changed
later:

- **Scope.** What is in this version and what waits: which pages, which platforms, which cases.
- **Behaviour the user will notice.** Flows, empty and error states, what happens on the edges
  (offline, signed out, the list is long, the item was deleted), defaults a user would see.
- **Trade-offs with a cost.** Simple now versus flexible later, speed versus completeness, an
  extra dependency versus more code; a wrong guess that would cost a day or more of rework.
- **Anything the user plausibly has an opinion on** and has not stated.

**Small** (decide it yourself) is only what a reviewer would not look twice at: names, file
layout, internal code structure, a library inside the existing stack, wording that follows the
existing copy, styling that follows the existing design, error message text.

When unsure between medium and small, ask. When unsure between major and medium, treat it as major.

## 2. Ask in rounds, as choices

Each round asks the open questions whose prerequisites are settled, **at most four per round**
(the dialog's limit): major ones first, by consequence; medium ones once the major ones that they
hang on are settled. The user should answer by picking, not by typing.

**With a choice tool** (Claude Code: `AskUserQuestion`; any agent's equivalent), one call per
round, one question per decision:

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

**Without a choice tool**, write the round as numbered questions with lettered options so the user
can answer in one line ("1A 2B 3A"):

```
**1 · <title>**: <the decision and why it matters>
  A. <option> (Recommended): <cost>
  B. <option>: <cost>

**2 · <title>**: ...
```

Either way, never put in one round a question whose answer depends on another question still
open in the same round; it waits for the next round.

### After every round: follow the consequences

An answer does more than close a question. Before the next round, re-map the plan as the user
just changed it and look for what the answer introduced:

- **New costs.** Choosing local storage means data lives on one device and vanishes when site
  data is cleared; choosing "no accounts" means nothing syncs and nothing can be recovered. A new
  cost that touches what users see or lose is a major question in its own right: ask whether it is
  acceptable, with the alternatives.
- **New decisions.** The answer may open branches that did not exist before (a chosen vendor has
  its own limits; a chosen flow has its own edge cases). Sort them into the tiers.
- **Dropped work.** Things that are no longer needed. Say so in one line so the user sees the plan
  shrink, and check that nothing the user asked for went with them.

A round that closes many questions is a reason to look harder at what changed, not a reason to
stop. The session ends only when no major or medium question is open after this check.

There is no round limit. If the session runs past five rounds, say how many questions remain and
offer to continue or to proceed with your recommendations for the rest.

Do not:

- re-ask anything the user already answered or the code already shows;
- ask about the same decision twice in different words;
- turn small decisions into questions to look thorough.

## 3. Write down what was decided

As major decisions settle, record them; do not batch these to the end.

- **ADR** in `docs/adr/` only when the decision is hard to reverse, would surprise a future reader,
  and came from a real trade-off. All three; otherwise skip it. Format: [ADR-FORMAT.md](ADR-FORMAT.md).
- **Glossary** in `GLOSSARY.md` only for a term that actually caused confusion in this session
  (two words for one thing, one word for two things), or that the code and the user use
  differently. Format: [GLOSSARY-FORMAT.md](GLOSSARY-FORMAT.md). No implementation details there.

Create these files lazily, only when there is something to write. Medium decisions and small
defaults are recorded in the summary below, not in docs. If the project keeps no docs and the user
does not want them, skip this step.

## 4. Close

When no major or medium question is open, write this summary in full. It is required before the
go-ahead question; never replace it with a sentence of prose.

```
**Decided**
- <major or medium decision>: <answer>   (ADR 0003 if one was written)

**Defaults (small, my call)**
- <small decision>: <default>

**Trade-offs you accepted**
- <cost an answer introduced>: <what it means for users or for later work>

**Not in this version**
- <anything deliberately left for later, or dropped by an answer>
```

Then ask for the go-ahead the same way as the rounds: with a choice tool, one question ("Build
with this plan?") with options such as "Yes, start (Recommended)", "Change something first" and
"Stop here, plan only"; without one, a one-line question. Do not start building until the user
picks yes.

---

Adapted from Matt Pocock's [`grill-with-docs`](https://github.com/mattpocock/skills) (`grilling` +
`domain-modeling`), MIT. The ADR and glossary formats are his, unchanged.
