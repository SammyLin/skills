# correct

English · [繁體中文](README.zh-TW.md)

Finds the mistakes agents keep repeating in a repo and makes each one impossible to repeat, at the
highest level that works: architecture, types, a lint whose error names the fix, a test, an agent
hook, and docs last. Based on Lauren Tan's
[`correct`](https://github.com/cursor/plugins/tree/main/pstack/skills/correct) from pstack.

| | pstack correct | correct |
| --- | --- | --- |
| Evidence | Commits, reverts, reviews, agent files | Same, with the exact `git`, `gh` and `az` sources named |
| Levels | Architecture, types/lint, test, docs | Adds an agent-hook level (`PreToolUse`) before docs |
| Before changing code | Fixes right away | Shows a class / evidence / level table and asks for the go-ahead |
| Proof | A check must fail on a real past mistake | Same, done by re-applying the bad diff in a scratch worktree |
| Commits | One per class | Same, on a branch, never the default branch |

Use it in Claude Code or Codex: `/correct`.

MIT. Adapted from Lauren Tan's pstack (MIT).
