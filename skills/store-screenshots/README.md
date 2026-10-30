# store-screenshots

English · [繁體中文](README.zh-TW.md)

App Store and Google Play screenshot sets for Claude Code. It reads your app's code to find the
benefits that sell it, plans what each screenshot must say, waits for your approval, then renders
every shot at the exact store size from your real app screens.

![Example set on light and dark](../../docs/images/store-screenshots-sheet.webp)

*The example set (mock app) as it appears in search results, light and dark.*

## How it works

1. **Read the app.** Screens, models, paywall, onboarding; the live listing too if the app is
   already in the store.
2. **Benefits.** 3-5 user benefits, each with evidence in the code. You confirm them.
3. **Screens.** Your simulator screenshots are rated Great / Usable / Retake and paired with the
   benefits; missing ones can be captured by deep link.
4. **Idea and direction.** One idea only this app has, and one of four directions: field,
   chapters, close-up, statement.
5. **Storyboard (stop).** A table of every shot: what it must make the viewer believe, the code
   evidence, headline, screen, layout. Nothing is rendered until you say yes; `render.py`
   refuses to run before that.
6. **Shot 1 (stop).** Rendered alone for your approval, then the rest.
7. **Gate and critique.** Two-line headlines, contrast, edges, fonts, no emoji, no unconfirmed
   "#1" claims; then a scored look at the set as it appears in search results.

Use it in Claude Code: `/store-screenshots`, or `/store-screenshots https://apps.apple.com/...`.

## Sizes and languages

iPhone 6.9" / 6.7" / 6.5", iPad 13", Google Play phone. Headlines can be a `{locale: text}` map;
`--locale ja` renders `final/ja/`, with Japanese and Korean broken at phrase and word boundaries.

## Where it comes from

A redesign of
[adamlyttleapps/claude-skill-aso-appstore-screenshots](https://github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots)
with the art-direction discipline of [leonxlnx/taste-skill](https://github.com/leonxlnx/taste-skill),
plus ideas from [hypersocialinc/shots](https://github.com/hypersocialinc/shots) (listing lookup,
competitor language, localization) and
[LeeHueeng/store-screenshots](https://github.com/LeeHueeng/store-screenshots) (HTML device frames,
deep-link capture, one sample first).

| Original | Here |
| --- | --- |
| Pillow scaffold, then Nano Banana redraws it, then crop/resize | HTML/CSS rendered by headless Chrome at the exact size; the app's pixels are never redrawn |
| Breakout panel imagined by an image model | Breakout is a real crop of the screenshot, enlarged |
| Fixed look: solid colour, centred uppercase verb | Four directions, chosen against an idea from the app |
| Generates right after the benefits | A storyboard you approve first, enforced by the renderer |
| State spread across memory files | One `screenshots/set.json` in the project |
| English only, iPhone 6.7" | Any locale; iPhone, iPad, Google Play |
| Needs Gemini MCP, SF Pro font file, Pillow | Python 3 stdlib + Chrome |

## Try it

```bash
cd examples/store-screenshots   # from the repo root
python3 ../../skills/store-screenshots/render.py set.json               # final/*.png + sheet.png
python3 ../../skills/store-screenshots/render.py set.json --locale ja   # final/ja/
```

MIT. See the repo LICENSE.
