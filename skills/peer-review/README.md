# peer-review

English · [繁體中文](README.zh-TW.md)

Reviews the changes since a fixed point (default `main`) on two separate axes, Standards and Spec,
with a different model as the reviewer. Based on Matt Pocock's
[`code-review`](https://github.com/mattpocock/skills); the run-the-repro rule comes from
pstack's [`interrogate`](https://github.com/cursor/plugins/tree/main/pstack/skills/interrogate).

| | code-review | peer-review |
| --- | --- | --- |
| Who reviews | Your own sub-agents | Another model: Antigravity first, then Codex or Claude (whichever you are not); your own sub-agents only if those fail |
| Spec source | The issue tracker set up by `/setup-matt-pocock-skills` | Detected from `origin`: `gh` for GitHub issues, `az` for Azure DevOps work items |
| No fixed point given | Asks | Uses `main` |
| Report | Two axes side by side | Same, plus who reviewed each axis, and cited lines spot-checked |
| Speed | Reviewers fetch the diff themselves | Diff pasted into the brief (up to 1500 lines); each reviewer killed after 15 min (a hang guard; a 400-line diff takes 1-2 min) and the next one tried; one call for both axes under 30 lines; at most 3 repros, run in parallel |
| Bug claims | Taken as the reviewer wrote them | Spec bugs need a repro; it is run in a scratch worktree and the finding is kept as proven, disproved, or a suspicion |

The Fowler smell baseline and the "never rerank across axes" rule are unchanged.

Use it in Claude Code or Codex: `/peer-review`, or say "peer-review since main".

MIT. Adapted from Matt Pocock's skills (MIT).
