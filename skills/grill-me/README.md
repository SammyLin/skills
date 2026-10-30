# grill-me

English · [繁體中文](README.zh-TW.md)

Stress-tests a plan before you build it, without the interrogation. Based on Matt Pocock's
[`grill-with-docs`](https://github.com/mattpocock/skills), which asks about every branch of the
design tree until nothing is left; this version asks only about the decisions that matter.

| | grill-with-docs | grill-me |
| --- | --- | --- |
| What it asks | Every open decision, until the tree is empty | Only major ones: hard to reverse; touching users, money or security; blocking others; a real fork; a contradiction |
| Everything else | Also asked | Decided with a stated default you can overrule at a glance |
| Round size | The whole frontier | At most four questions, aiming for three rounds or fewer |
| How you answer | Type a reply to each question | Pick from options in Claude Code's question dialog, recommendation first (numbered options as a fallback) |
| Edge cases | Invented to probe the model | Raised only when they change a major decision |
| Docs | Glossary updated for every term, ADRs when warranted | ADR only for hard-to-reverse trade-offs; glossary only for terms that actually caused confusion |
| End | When the tree is empty | A summary of decisions, defaults and open items, then it waits for your yes |

Use it in Claude Code: `/grill-me`, or say "grill me on this plan".

MIT. Adapted from Matt Pocock's skills (MIT); the ADR and glossary formats are his, unchanged.
