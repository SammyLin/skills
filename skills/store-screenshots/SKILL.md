---
name: store-screenshots
description: >-
  Design and render App Store / Google Play screenshot sets that convert and do not look AI-made.
  Reads the app's codebase to find the user benefits that sell it, plans what each screenshot must
  convey as a storyboard, and renders nothing until the user approves that storyboard. Every shot is
  rendered deterministically in HTML/CSS via headless Chrome at exact store sizes (no image model
  redrawing the UI), gated against house rules (two-line headlines, contrast, no fake proof, no
  emoji, no gradients) and critiqued as it appears in search results. Use when the user asks for
  App Store / Google Play / ASO screenshots, store listing images (上架圖), or wants existing
  screenshots redesigned.
user-invocable: true
argument-hint: "[App Store URL | screenshots folder | 'translate <locale>']"
---

# Store screenshots

An App Store set built on autopilot looks like every other set: a saturated background, a
centred all-caps verb, a phone, sparkles, a "#1 app" claim, and a UI that an image model quietly
redrew with wrong numbers. Nothing in it is wrong and nothing in it was decided.

This skill makes the decisions on purpose and checks them:

1. **Benefits first.** The words decide whether anyone taps Download. Do this phase properly.
2. **An idea from the app itself,** not from the category, held against the nearest competitor.
3. **Real pixels only.** The app's own screenshots, placed and cropped by `render.py`. A breakout
   panel is a real crop of the screenshot, enlarged. Nothing is invented or redrawn.
4. **A gate and a look.** `render.py` measures each shot and fails what breaks the rules; then you
   look at `sheet.png` (the set at search-result size, light and dark) and critique it.

`<skill>` below is this skill's folder. Work happens in the app project's `screenshots/` folder.
Needs Python 3 (stdlib only) and Google Chrome / Chromium (`CHROME=` to override the path).

## Two stops before any image

These are hard rules. Do not run `render.py` past them, not even "just to show an idea".

1. **Storyboard stop (step 5).** Nothing is rendered until the user has approved the storyboard:
   what every shot conveys, its headline, its screen and its layout. A "yes" to the benefits is not
   a yes to the storyboard.
2. **First-shot stop (step 6).** Render shot 1 alone, show it, and render the rest only after the
   user says yes to it.

Any later change to a shot's message, headline or screen goes back to the user as that row of the
storyboard before it is rendered again. Approval of one step never carries over to the next.

## State lives in `screenshots/set.json`

Everything this skill learns or decides goes into one file in the project, so a new conversation
resumes by reading it. **Start every run by reading `screenshots/set.json` if it exists** and
present a short status (benefits confirmed? screenshots assessed? direction chosen? which shots
pass the gate?). Then let the user resume or jump to any phase. Write to it after every confirmed
decision; never keep state only in the conversation.

```json
{
  "app": "Binder",
  "audience": "Trading card collectors who sell on eBay",
  "inventory": ["..."],
  "idea": "The binder page becomes the price board.",
  "direction": "field",
  "storyboard_approved": false,
  "size": "6.9",
  "palette": { "ground": "#0F3D2E", "ink": "#F3EFE4", "accent": "#E8B931" },
  "type": { "family": "-apple-system, 'SF Pro Display', sans-serif", "weight": 800 },
  "proof": [],
  "assessments": { "sim/home.png": "Great: full list, real prices, clean status bar" },
  "shots": [
    { "slug": "know-value", "headline": "Know what your binder is worth",
      "screenshot": "sim/home.png", "layout": "poster", "status": "approved" }
  ]
}
```

Paths in `set.json` are relative to the `screenshots/` folder.

## 1. Read the app

Explore the codebase: screens and components (what can a user actually do), models (the domain),
paywall and IAP (what is premium), onboarding (what the app shows first), app name, bundle ID,
README and any store metadata. Then **inventory the subject**: eight to twelve things that belong
to this app and no competitor. Its name and what the name means, the one number it shows that
nobody else does, the object its users hold (the card, the plant, the receipt), the moment of day
it is opened, the constraint it lives with (offline, one tap, no account), its real colours and
icons from the asset catalog. This list is where the idea comes from.

**If the app is already live** (the user passes an App Store URL, or one is in the README), pull
the listing with the free iTunes lookup API, no key needed:

```bash
curl -s "https://itunes.apple.com/lookup?id=<numeric id from the URL>&country=us"
```

It returns name, subtitle-like description, genre, rating, review count and the current
screenshot URLs. Read the current screenshots: they are the "before". For 3-5 direct competitors
(`https://itunes.apple.com/search?term=<category words>&entity=software&limit=10`), note what their
first three screenshots claim and how they look; the gap is where this set should stand. Keep a
short **language bank** in `set.json`: the words users and competitors actually use (from the
description, reviews, competitor headlines). Apple indexes text in screenshots, so a headline in
the market's own words also helps search; never stuff keywords at the cost of reading well.

Ask only what the code and listing cannot answer: who it is for, the #1 reason people download it,
what the best reviews say. Do not ask questions you can answer yourself.

## 2. Benefits (the most important phase)

Draft 3-5 benefits as the set's argument: one claim per shot, in order, each proved by a screen.

- **Found in the code, with evidence.** Each benefit names the screen, model or job that makes it
  true (`PortfolioView.swift`, a nightly sync, an offline cache). Carry that evidence into the
  storyboard.
- **What the user gets, not what the app does.** "Know what your binder is worth", not "Portfolio
  tracking".
- **Specific beats generic.** If you can swap in a competitor's name and it still reads true, it is
  a category line; go back to the inventory.
- **Lead with a verb or the outcome,** whichever is stronger. Uppercase verb-first headlines are one
  option, not a law.
- **About 32 characters, two lines at most** at the set's type size. Count before proposing.
- **Proof is never invented.** No "#1", "award-winning", "millions of users", stars or "trusted by"
  unless the user confirms it is true; then list it in `set.json` `proof[]`. The gate fails
  unlisted claims.
- **Order matters.** Search results show the first three shots. Shot 1 carries the single biggest
  reason to download; shots 1-3 must work without the rest. A useful arc: **value** (the outcome,
  the new state of the user), **flow** (the screen that delivers it), then **trust** (privacy,
  offline, no account, or real proof the user confirmed) — never invented trust.

Present them as `n. Headline — why it converts`. Let the user reorder, reword, cut. Push back on
generic choices with the reason. Do not continue until the user confirms. Save to `set.json`.

## 3. Screenshots: assess, coach, pair

Use screenshots the user already has (folder, files or glob). If there are none, capture them
yourself rather than asking the user to tap through the app:

1. Clean status bar first: `xcrun simctl status_bar booted override --time 9:41
   --batteryState charged --batteryLevel 100 --cellularBars 4` (`clear` it afterwards).
2. Navigate by **deep link** when the app has a URL scheme (`CFBundleURLTypes` in Info.plist, the
   router): `xcrun simctl openurl booted "myapp://portfolio"`, wait a second, then
   `xcrun simctl io booted screenshot screenshots/sim/portfolio.png`. Without a scheme, use `idb`
   (`idb ui describe-all`, `idb ui tap X Y`) or Maestro if installed; offer to add per-tab deep
   links to the app if neither exists. Android: `adb shell am start -d <uri>` and
   `adb exec-out screencap -p > file.png`.
3. Read each capture to confirm it is the intended screen before moving on.

Ask the user to drive the simulator only when all of that fails. Read every screenshot. Rate each **Great**,
**Usable** or **Retake** with what it shows, what works and what does not. Flag empty states,
sparse lists, placeholder data ("Test Item 1"), debug UI, cluttered status bars, login, settings
and onboarding screens, mixed light and dark mode.

For each Retake, and for each benefit with no good screen, say exactly what to capture: which
screen, what data (6+ list items, a chart going up, realistic names and prices), which appearance
(one mode for the whole set), and a clean status bar (`xcrun simctl status_bar booted override
--time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4`).

Pair each benefit with its best Great/Usable screenshot: relevance first, then visual richness,
then legibility at thumbnail size; avoid reusing a screen. Present pairings with one line of
reasoning each, let the user swap, save assessments and pairings to `set.json`.

## 4. The idea and the direction

Write this sentence and fill both blanks from the inventory:

> In this set, **[something only this app has]** becomes **[the device the direction uses]**.

Run the **competitor test**: put the nearest competitor in the sentence. If it still works, the
idea belongs to the category; try again. "Clean and modern" is not an idea.

Then choose one direction for the whole set. Pick the one that carries the idea, not the most
familiar one, and state why in one line:

| Direction | What it does | Suits |
| --- | --- | --- |
| **field** | One ground colour on every shot, left-aligned headline, device bleeding off the bottom. Breakouts where a panel proves the claim. | Most apps. The safe strong default. |
| **chapters** | Each shot changes the whole field colour, taken from the app's own palette (3-5 colours, same ink). The swipe becomes a sequence. | Apps with a real multi-colour palette or distinct modes. |
| **close-up** | Mostly `bleed`: no device frame, the app screen huge and cropped by the canvas edge. The UI is the picture. | Rich, dense UIs (maps, charts, photos, editors). |
| **statement** | `"align": "center"`, larger type, shorter words; device sits lower. One idea per shot, said loud. | Simple apps with one sharp promise per screen. |

Layouts per shot: `poster` (device under the headline), `breakout` (poster plus one real panel
cropped from the screenshot, enlarged to near canvas width, the one element allowed a shadow
because it truly floats), `bleed` (no frame, oversized screen off the right and bottom edges).
Neighbouring shots should not all share one layout unless the direction is `field`.

**Palette:** one ground, one ink, one accent. Take it from the app (asset catalog tint, brand
colours, the dominant colour of its screens), set so the app's screens pop against the ground.
Avoid white or pale grey grounds (they vanish in the store), avoid a ground that matches the app
UI's own background, and avoid the assistant palette (violet/indigo, cream with terracotta) unless
it is truly the brand. State the choice with one line of reasoning; the user can override.

**Type:** one family. Default is the system face (SF Pro via `-apple-system`), weight 800,
tracking -0.035em. A brand font goes in `type.family` with its stylesheet `<link>` in `type.css`;
the gate fails if it does not load. Sentence case reads more premium; `"case": "upper"` is
available when the brand shouts.

## 5. Storyboard (stop: wait for approval)

Before any image exists, show the whole plan as one table, one row per shot, in store order. This
is where the user decides what each screenshot says, so write it in the user's language and make
every row concrete:

```
Idea: The binder page becomes the price board.
Direction: field · ground #0F3D2E, ink #F3EFE4 · iPhone 6.9" · locales: en, zh-TW

| # | What this shot must make the viewer believe | Evidence in the code | Headline | Screen | Layout |
|---|---|---|---|---|---|
| 1 | My whole collection has a live value | PortfolioView.swift: totalValue, daily refresh | Know what your binder is worth | sim/home.png | poster |
| 2 | I see gains without doing anything | PriceSyncJob.swift runs at 6:00 | See the total, every morning | sim/home.png | breakout: value card |
| 3 | Every single card is priced | CardRow shows marketPrice | Every card, priced | sim/list.png | bleed |
```

- **What the viewer must believe** is the user benefit in plain words, not a feature name.
- **Evidence** names the file, screen or data that makes the benefit true. A benefit with no
  evidence in the code is a promise the app does not keep; drop it or ask the user.
- Below the table, list anything uncertain: proof claims awaiting confirmation, screens that need
  a retake, sample data visible on a screen.

Then ask plainly whether to render shot 1, and stop. Accept edits row by row and show the updated
table again. Only an explicit yes (OK, go, 可以, 好) moves on; record it in `set.json` as
`"storyboard_approved": true` and reset it to `false` whenever a row changes.

If the user wants to see directions as pictures before choosing, that is a request to render:
after the storyboard is approved, write shot 1 in two or three variants (`set.field.json`,
`set.closeup.json`, ...), render each with `--only 1 --out variants/<name>`, show them side by
side, let the user pick, delete the variant files.

## 6. Render (stop: shot 1 first)

```bash
python3 <skill>/render.py screenshots/set.json            # all shots + sheet.png
python3 <skill>/render.py screenshots/set.json --only 2   # just shot 2
```

Output: `screenshots/final/NN-slug.png` at the exact size, plus `screenshots/sheet.png`.

| `size` | Display | Pixels |
| --- | --- | --- |
| `6.9` (default) | iPhone 6.9" | 1320 × 2868 |
| `6.7` | iPhone 6.7" | 1290 × 2796 |
| `6.5` | iPhone 6.5" | 1242 × 2688 |
| `ipad-13` | iPad 13" | 2064 × 2752 |
| `android` | Google Play phone | 1080 × 1920 |

For another device, copy `set.json` with a different `size` and render with `--out final/<device>`.
Use that device's own captures; an iPad set should show iPad screens (`bleed` suits them best).

**Render shot 1 first** (`--only 1`), fix it until it passes the gate, show it, and stop. Render
the rest only after the user says yes to shot 1.

Per-shot keys: `headline`, `screenshot`, `layout`, and optional `size` (headline px at 1290 width,
default 150), `ground` / `ink` (field colour override for `chapters`), `breakout`
`{x, y, w, h}` in the screenshot's own pixels (read the screenshot to pick the panel; take a
whole card or section, never a lone button), `panel_width`, `bleed_x`, `bleed_width`.
Set-level `type` keys: `family`, `css`, `weight`, `tracking`, `case`, `align`, `size`, `top`,
`gap`, `pad`.

**Localize** by turning a headline into a map and rendering per locale:

```json
"headline": { "en": "Know what your binder is worth", "zh-TW": "一眼看懂卡冊值多少", "ja": "カードの価値が一目で" }
```

```bash
python3 <skill>/render.py screenshots/set.json --locale ja   # final/ja/*.png + final/sheet-ja.png
```

Translate the job of each headline, not the words: same claim, the market's own phrasing, still
two lines. Japanese breaks at phrases and Korean at words automatically. When the app itself is
localized, capture each language's screens and copy `set.json` per locale (`set.ja.json`) pointing
at them, so the UI matches the headline.

## 7. Gate

`render.py` prints `[ok]` or `[FAIL]` per shot and exits non-zero on any FAIL. It fails:

- a headline over **two lines** (cut words first, then lower `size`);
- a headline closer than 5% to either edge;
- ink/ground contrast under 4.5;
- a font that did not load, or a screenshot that did not load;
- emoji in a headline;
- a proof claim not listed in `proof[]`.

It warns on headlines over 40 characters and on headline blocks that push the device low. Fix
every FAIL. Treat every WARN as wrong unless you can defend it in one sentence.

House rules the renderer enforces by construction, so do not work around them: no gradients, no
glows, no shadow on anything at rest (only the breakout panel has one), no decorative shapes,
sparkles, arrows or blobs, no pill badge or small label above the headline, no styled accent word
in the headline (one face, one colour), no invented UI.

## 8. Look

Passing the gate means nothing banned was measured, not that the set is good. Read
`screenshots/sheet.png`, then each final at full size. Make each pass on its own:

1. **One second.** At thumbnail size, what is the one thing you see in shot 1? If it is "a phone",
   there is no focal point. Can a stranger say what the app does from shots 1-3 alone?
2. **Squint.** Each shot should reduce to two masses: the headline and the screen.
3. **Cover the name.** Could this set belong to a competitor? Then the idea is not in it.
4. **The swipe.** Do the shots read as one series (same type, same frame, same margins) with a new
   reason on each? Is any claim repeated?
5. **Light and dark.** Does the ground hold on both rows of the sheet?
6. **Collisions and crops.** Anything over the headline? A breakout that cuts a card mid-row? Text
   on the screen too small to mean anything at this size (then pick a breakout or `bleed`)?
7. **Truth.** Every number and name on screen is what the app really shows.

Score it: **design 40%, clarity 30%, idea 20%, copy 10%**, each 1-10. Caps: any gate FAIL caps
the set at 6.0; a set that passes the competitor test caps idea at 6; a shot 1 that fails the
one-second pass caps clarity at 6. Write the round down:

```
ROUND n
Seen in one second: ...
Idea: ...
Scores: design _ · clarity _ · idea _ · copy _ → overall _._
Top three fixes: ...
```

Fix the top three, render, look again. Three rounds at most. Then show the user the sheet and the
finals; let them approve, request changes per shot, or swap directions. Mark approved shots
`"status": "approved"` in `set.json`.

## 9. Report

Tell the user, briefly: the idea sentence and the direction with its reason; the final round's
scores and what still falls short; the files in `screenshots/final/` and which App Store Connect
slot they fit (the 6.9" set is accepted for all smaller iPhones; render other sizes only if asked);
any sample data visible on screen that should be real before shipping. Do not claim a check you
did not run.
