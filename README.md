# SammyLin/skills

Agent skills I use and trust, in one place. Each lives in `skills/<name>/` with its own `SKILL.md`.

| Skill | What it does | Origin |
| --- | --- | --- |
| [`store-screenshots`](skills/store-screenshots/) | App Store / Google Play screenshot sets: benefits, an idea from the app, deterministic HTML render at exact store sizes, a gate and a critique. Localized. | Own; redesigned from [adamlyttleapps](https://github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots) with ideas from [taste-skill](https://github.com/leonxlnx/taste-skill), [shots](https://github.com/hypersocialinc/shots), [store-screenshots](https://github.com/LeeHueeng/store-screenshots) |
| [`humanizer`](skills/humanizer/) | Removes signs of AI-generated writing from text (Wikipedia's "Signs of AI writing"). | [blader/humanizer](https://github.com/blader/humanizer), MIT, vendored unchanged |

## Install

```bash
npx skills add SammyLin/skills                         # all skills, this project
npx skills add SammyLin/skills --global                # all skills, every project
npx skills add SammyLin/skills -s store-screenshots      # one skill
npx skills add . -l                                                         # list, from a local clone
```

Or as a Claude Code plugin: `/plugin marketplace add SammyLin/skills`.

## Adding a skill

1. `skills/<name>/SKILL.md` with `name` and `description` frontmatter; scripts beside it.
2. A row in the table above.
3. Someone else's skill: only if its licence allows it; keep its `LICENSE` in its folder and credit
   the origin here.

## Licence

MIT (see `LICENSE`). Vendored skills keep their own licence in their folder.
