# grill-me

English · [繁體中文](README.zh-TW.md)

Stress-tests a plan before you build it. Based on Matt Pocock's
[`grill-with-docs`](https://github.com/mattpocock/skills): it still asks about everything that
shapes the result, but you answer by picking options, the small stuff is decided for you out loud,
and it follows up on what each of your answers changes.

| | grill-with-docs | grill-me |
| --- | --- | --- |
| What it asks | Every open decision, until the tree is empty | Major decisions first (hard to reverse; users, money or security; blocking; a real fork; a contradiction), then medium ones (scope, behaviour users notice, trade-offs with a cost) |
| Small stuff | Also asked | Names, file layout, internal structure, styling that follows the existing design: decided with a stated default |
| How you answer | Type a reply to each question | Pick from options in Claude Code's question dialog, recommendation first (numbered options as a fallback) |
| Round size | The whole frontier | At most four questions per round; no round limit, a check-in after five |
| After each answer | Moves to the next branch | Looks at what the answer introduced (a new cost for users, new branches, dropped work) and asks about it |
| Edge cases | Invented to probe the model | Asked when they change what users see or what gets built |
| Docs | Glossary updated for every term, ADRs when warranted | ADR only for hard-to-reverse trade-offs; glossary only for terms that actually caused confusion |
| End | When the tree is empty | A required summary (decided, defaults, trade-offs you accepted, not in this version), then it waits for your yes |

Use it in Claude Code: `/grill-me`, or say "grill me on this plan".

MIT. Adapted from Matt Pocock's skills (MIT); the ADR and glossary formats are his, unchanged.
