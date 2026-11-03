---
name: correct
description: >-
  Find the mistakes agents keep repeating in this repo and make each one impossible to repeat:
  architecture first, then types, then a lint or check whose error names the fix, then a test, then
  an agent hook, and docs last. Proves every new check fails on a real past mistake and keeps a
  rule table of what enforces each rule. Use for /correct, when the user says agents keep making
  the same mistake, or right after the user corrects you for something a rule already covered.
disable-model-invocation: true
---

# Correct

The user keeps correcting agents in this repo for the same mistakes. Change the repo so the next
agent cannot make them.

Assume every contributor is an agent that sees only the files it opened, copies the nearest
example, and takes the shortest path that compiles. Design the repo so a change that looks right
from one file is right for the whole repo.

Talk to the user in their language.

## 1. Find the mistake classes

Collect evidence before proposing anything. Look in:

- `git log` for reverts, `fix:` commits that undo a recent change, and commits that touch the
  same lines twice in a short time;
- review comments on recent PRs (`gh pr list --state merged` + `gh api .../comments` on GitHub,
  `az repos pr list` + threads on Azure DevOps);
- agent instruction files (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/`, memory or feedback files):
  every "never do X" / "always do Y" line is a correction someone already had to make;
- comments that explain a workaround, `TODO`/`HACK` notes, and dead code an agent would copy;
- what the user just corrected in this session, if that is what triggered the run.

Group the mistakes into classes. **A class counts once it has happened twice**; one-off mistakes
are not worth a rule. For each class keep the evidence: commit hashes, PR links, file:line.

## 2. Pick the highest level that works

For each class, walk down this list and stop at the first level that makes the mistake impossible
or loud:

1. **Architecture: eliminate it.** One owner per piece of state, one supported way per task.
   Hide internals so the wrong import fails. Replace hand-synced lists with one source of truth.
   Delete the old way and the dead code an agent would copy.
2. **Types: make the bad state unwritable.** Branded types, exhaustive unions, required fields,
   narrower signatures.
3. **Lint or CI check: fail loudly, with the fix in the message.** The error names the file,
   type or function to use instead ("use `fetchJson` from `lib/http.ts`, not `fetch`"). If the
   bad pattern is already common, fail only when a change adds more (a ratchet), not on the
   existing count.
4. **Test the behaviour.** Fix or delete any test that still passes when the behaviour it checks
   breaks, or that fails when only the internals change.
5. **Agent hook: block it at the tool call.** For mistakes that live outside the code (wrong
   command, wrong directory, skipped step), a Claude Code `PreToolUse` hook or the equivalent in
   other agents can refuse the call and say what to do instead.
6. **Docs or agent rules: last, only for judgment calls.** Nothing fails when an agent skips them.

## 3. Get the go-ahead

Show the user the plan before changing anything:

```
| Class | Evidence | Level | Why not higher |
| --- | --- | --- | --- |
| <mistake> | <2+ commits / PRs / file:line> | <level> | <what blocked the level above> |
```

Then ask once (with a choice tool if there is one): fix all, pick which classes, or stop at the
plan. Most frequent classes first.

## 4. Fix and prove

One commit per class, only on a branch, never on the default branch.

**Prove each new check fails on a real past mistake.** Re-apply the bad diff from the evidence
(`git show <hash> | git apply` in a scratch worktree, or rewrite the offending line), run the
check, and show its failing output. A check you have not seen fail does not count. Then show it
passing on the fixed code.

Run the same command locally that CI runs. An exception goes on the offending line with a reason,
an expiry date, and a human's name who approved it.

## 5. Keep the rule table

In the agent instruction file (`CLAUDE.md` or `AGENTS.md`), keep a table pairing each rule with
what enforces it:

```
| Rule | Enforced by |
| --- | --- |
| Use `fetchJson`, never raw `fetch` | lint `no-raw-fetch` (eslint.config.js) |
| Config edits go through `config/schema.ts` | type: `Config` is readonly |
| Pick a date format | judgment (docs only) |
```

When the user corrects you later: fix the mistake and add the rule. If the rule was already in the
table and nothing enforced it, that is a repeat: move it up a level in the same change. Delete a
rule once its mistake can no longer happen.

## 6. Report

For each class: its evidence, the level picked, why a higher level did not work, the commit, and
the failing output from step 4. Then list classes found but not fixed, and why.

---

Adapted from Lauren Tan's [`correct`](https://github.com/cursor/plugins/tree/main/pstack/skills/correct)
(pstack), MIT.
