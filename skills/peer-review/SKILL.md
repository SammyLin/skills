---
name: peer-review
description: >-
  Review the changes since a fixed point (commit, branch, tag; default main) along two axes,
  Standards (does the code follow this repo's documented coding standards?) and Spec (does it match
  what the originating GitHub issue or Azure DevOps work item asked for?), with a different model
  as the reviewer: Antigravity first, then Codex or Claude (whichever you are not), your own fresh
  sub-agents only as a fallback. Use when the user wants to review a branch, a PR or
  work-in-progress changes, asks to "review since X", or wants a second model to check the work.
---

# Peer review

Two-axis review of the diff between `HEAD` and a fixed point:

- **Standards**: does the code conform to this repo's documented coding standards?
- **Spec**: does the code faithfully implement the originating issue / work item?

Each axis is reviewed by **a different model from the one that wrote the code**, so the review
doesn't share the author's blind spots. The two axes run in parallel and separately, then this
skill puts their reports side by side.

Talk to the user in their language.

## 1. Pin the fixed point

Use whatever the user named (SHA, branch, tag, `HEAD~5`, ...). If they named nothing, use `main`
(`master` if `main` doesn't exist) and say so in one line.

Confirm it resolves (`git rev-parse <fixed-point>`) and that `git diff <fixed-point>...HEAD`
(three-dot: against the merge-base) is non-empty. A bad ref or empty diff fails here, not inside
two reviewers. Note the commit list: `git log <fixed-point>..HEAD --oneline`.

## 2. Detect the host

Read `git remote get-url origin`:

- `github.com` → **GitHub**, use `gh`. Issue refs look like `#123`, `Closes #45`.
- `dev.azure.com` or `*.visualstudio.com` → **Azure DevOps**, use `az`. Work-item refs look like
  `AB#123`, `#123`, or a `workitems` link; also check the branch name (`feature/123-...`).
- Anything else, or the CLI isn't logged in: skip fetching and go to the user/file sources below.

## 3. Find the spec

In this order:

1. Refs in the commit messages and branch name, fetched with the host's CLI:
   - GitHub: `gh issue view <n> --comments` (or `gh pr view <n>` if the ref is a PR).
   - Azure DevOps: `az boards work-item show --id <n> --output json`; the spec is
     `System.Title`, `System.Description` and `Microsoft.VSTS.Common.AcceptanceCriteria`
     (strip the HTML). If a PR exists for the branch, `az repos pr list --source-branch <branch>`
     shows its description and linked work items.
2. A path the user passed.
3. A spec file under `docs/`, `specs/` or `.scratch/` matching the branch or feature.
4. Nothing found: ask the user where it is. If there is none, the Spec axis is skipped and the
   report says "no spec available".

## 4. Find the standards

Every file in the repo that documents how code should be written: `CODING_STANDARDS.md` and
`CONTRIBUTING.md` when they exist, plus `CLAUDE.md`, `AGENTS.md`, `.editorconfig`-style docs, lint
configs' comments, style sections of the README.

On top of that, the Standards axis always carries the **smell baseline** below: a fixed set of
Fowler code smells (_Refactoring_, ch.3) that applies even when the repo documents nothing.

- **The repo overrides.** A documented repo standard always wins; where it endorses something the
  baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a
  hard violation. Skip anything tooling already enforces.

Each smell reads _what it is_ → _how to fix_:

- **Mysterious Name**: a function, variable or type whose name doesn't reveal what it does or holds.
  → rename it; if no honest name comes, the design's murky.
- **Duplicated Code**: the same logic shape in more than one hunk or file of the change. → extract
  the shared shape, call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. → move it
  onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together. → bundle them into one
  type, pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept. → give the
  concept its own small type.
- **Repeated Switches**: the same `switch`/`if`-cascade on the same type recurs across the change.
  → polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files. → gather what
  changes together into one module.
- **Divergent Change**: one file or module edited for several unrelated reasons. → split so each
  changes for one reason.
- **Speculative Generality**: abstraction, parameters or hooks for needs the spec doesn't have. →
  delete it; inline until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the
  walk behind one method on the first object.
- **Middle Man**: a class or function that mostly delegates onward. → cut it, call the target
  direct.
- **Refused Bequest**: a subclass or implementer that ignores most of what it inherits. → drop the
  inheritance, use composition.

## 5. Pick the reviewer

Use a model other than yourself, through the bundled script (next to this file). It knows each
CLI's read-only flags, tries reviewers in order, and checks the reviewer's own exit code:

| You are | 1st | 2nd | 3rd |
| --- | --- | --- | --- |
| Claude | Antigravity (`agy`) | Codex | |
| Codex | Antigravity (`agy`) | Claude | |
| Antigravity | Codex | Claude | |
| anything else | Antigravity (`agy`) | Codex | Claude |

```bash
<skill-dir>/run-reviewer.sh --self <claude|codex|agy|other> "$BRIEF" "$OUT"
```

- Last stdout line `reviewer=<name>`, exit 0: the review is in `$OUT`.
- `reviewer=none`, exit 1: every external reviewer failed; reasons are on stderr and in
  `$OUT.<name>.err`. Run that axis in your own sub-agent with a fresh context.
- Exit 2: your call was wrong (bad args, empty brief, not in a repo). Fix it and rerun.
- A `WARNING: repo changed` line means a reviewer touched the repo: tell the user, show
  `git status`.

Don't build the reviewer commands yourself and don't wrap the script in `timeout` (macOS has none;
it exits 127 and nothing runs). Never review an axis yourself in the main context.

## 6. Run both axes in parallel

Write each brief to its own temp file, start the script once per axis at the same time (in the
background), and wait for both. A review can take several minutes. Each brief is
self-contained: the reviewer sees nothing but the brief and the repo.

**Standards brief:**

- The diff command and commit list.
- The standards files from step 4, **plus the smell baseline pasted in full**.
- "Do not edit any file. Report, per file/hunk where relevant, (a) every place the diff violates a
  documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot:
  name it and quote the hunk. Distinguish hard violations from judgement calls: documented-standard
  breaches can be hard, but baseline smells are always judgement calls, and a documented repo
  standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec brief:**

- The diff command and commit list.
- The spec contents (fetched text, not just an ID: the reviewer may not have `gh`/`az` access).
- "Do not edit any file. Report: (a) requirements the spec asked for that are missing or partial;
  (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look
  implemented but where the implementation looks wrong. Quote the spec line for each finding.
  Under 400 words."

No spec: skip the Spec axis.

## 7. Aggregate

Present the reports under `## Standards` and `## Spec`, verbatim or lightly cleaned, each headed by
who reviewed it (`Reviewed by Codex`, or `Reviewed by Claude sub-agent — Codex failed: <reason>`),
and any rerun or fallback that happened along the way, with its reason.
Do **not** merge or rerank findings across axes.

Before passing a finding on, spot-check that the file and line it cites exist in the diff; mark any
that don't as `(unverified)` rather than silently dropping them.

End with one line: findings per axis, and the worst issue _within each axis_. Don't pick a single
winner across axes.

## Why two axes

A change can pass one and fail the other:

- Follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Does exactly what the issue asked but breaks the conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.
