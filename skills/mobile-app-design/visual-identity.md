# Visual identity

## Find the direction

Start from the brief, not from a palette you like. Pull 3–5 words from it (who, where, what it
feels like to use) and turn each into a decision:

| Lever | Decide |
|---|---|
| Colour | Background temperature, one accent with one meaning, how much colour the content carries |
| Type | System font or one bundled family; weight contrast; how big the biggest number is |
| Shape | Corner radius family (sharp / soft / pill), stroke vs fill, density |
| Surface | Flat, layered with elevation, or tinted panels; how cards separate from the page |
| Imagery | Product photos, icons, an illustration style or a mascot, or none |
| Motion | Snappy or soft; what moves at all |

Propose 2–3 directions that differ on at least three levers. For each: a token list (colours as
hex with light and dark values, type scale, radius, spacing) and one rendered home screen at
phone size (HTML or SwiftUI preview screenshot). The owner picks; record the pick and the date in
DESIGN.md.

## Stay out of these looks

They read as a default, not as this app. Unless the owner asks for one by name, don't use:

- **Warm cream / ivory / parchment page backgrounds** (near-white with a yellow-red cast, e.g.
  `#FAF9F5`, `#F0EEE6`, `#FBF6EE`, `#F5F0E8`), with sand or beige chips and warm-grey text.
- **Clay, terracotta, burnt-orange or coral accents** (`#D97757`, `#CC785C`, `#C96442`,
  `#E5674F` and neighbours) as the primary action colour, especially on cream.
- **Warm near-black ink on cream** (`#141413`, `#2A211C`) as the whole text system.
- **Serif display headings over sans body** in a calm "editorial" layout of big margins and
  little colour.
- Soft hand-drawn spot illustrations, olive or sage secondary colours, and plain white rounded
  cards with a faint warm shadow as the only surface.
- Also overused: purple-to-blue gradients, glassmorphism everywhere, neon on black.

`palette_check.py` flags the first two families in theme files (Swift, Kotlin, XML, CSS, JSON).
A flagged colour can stay only if DESIGN.md says the owner chose it.

## Safe starting points (pick, then make it yours)

Not a menu to copy; examples of directions that do not collapse into the looks above.

| Direction | Page / surface | Ink | Accent | Shape |
|---|---|---|---|---|
| Cool clinical | `#F4F6F8` / `#FFFFFF` | `#0E1726` | cobalt `#2F5BFF` | 12 radius, flat, hairline dividers |
| Bold retail | `#FFFFFF` / `#F2F2F2` | `#111111` | signal red `#E3001B` + yellow tag `#FFD400` | 8 radius, heavy weights, big prices |
| Dark data | `#0B0D10` / `#16191E` | `#EDEFF2` | mint `#3DDC97` | 10 radius, monospaced figures |
| Fresh green | `#F5FAF7` / `#FFFFFF` | `#10231A` | `#0A8F5B` | pill buttons, 16 radius |

Check every text/background pair for contrast (4.5:1 body, 3:1 large text and icons) in light
and dark.
