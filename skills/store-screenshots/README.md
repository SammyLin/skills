# store-screenshots

Claude Code skill for App Store screenshot sets. A redesign of
[adamlyttleapps/claude-skill-aso-appstore-screenshots](https://github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots)
with the art-direction discipline of [leonxlnx/taste-skill](https://github.com/leonxlnx/taste-skill),
plus ideas from [hypersocialinc/shots](https://github.com/hypersocialinc/shots) (listing lookup, competitor
language, localization) and [LeeHueeng/store-screenshots](https://github.com/LeeHueeng/store-screenshots)
(HTML device frames, deep-link auto capture, one-sample-first).

What changed from the original:

| Original | Here |
| --- | --- |
| Pillow scaffold, then Nano Banana redraws it (3 variants), then crop/resize | HTML/CSS rendered by headless Chrome at exact App Store size; the app's pixels are never redrawn |
| Breakout panel imagined by an image model | Breakout is a real crop of the screenshot, enlarged |
| Fixed look: solid colour, centred uppercase verb | Four directions (field, chapters, close-up, statement), chosen against an idea from the app |
| State spread across memory files | One `screenshots/set.json` in the project |
| Review by eye | Gate (two-line headlines, edges, contrast, font load, no emoji, no unlisted proof claims) plus a scored critique of the set at search-result size |
| English only | `{locale: text}` headlines, `--locale ja` renders `final/ja/` with CJK-aware line breaks |
| iPhone 6.7" | iPhone 6.9/6.7/6.5", iPad 13", Google Play phone |
| Needs Gemini MCP, SF Pro font file, Pillow | Python 3 stdlib + Chrome |

Use in Claude Code: `/store-screenshots` (or `/store-screenshots https://apps.apple.com/...`).

## Try it

```bash
cd examples/store-screenshots   # from the repo root
python3 ../../skills/store-screenshots/render.py set.json               # final/*.png + sheet.png
python3 ../../skills/store-screenshots/render.py set.json --locale ja   # final/ja/
```

MIT. See the repo LICENSE.
