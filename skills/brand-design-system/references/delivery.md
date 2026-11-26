# Delivery conventions

## Tokens
Use stable semantic names, explicit color strings and numerical sizes with documented units (CSS px / platform logical units; motion ms). Example structure:

```json
{
  "color": {"brand": {"primary": "#082D5D"}, "semantic": {"primary": "#082D5D", "surface": "#FFFFFF", "text": "#172B45"}},
  "spacing": {"xs": 4, "sm": 8, "md": 12, "lg": 16},
  "radius": {"sm": 8, "md": 12, "lg": 16},
  "typography": {"size": {"body": 16, "title": 20}, "weight": {"regular": 400, "bold": 700}},
  "size": {"touchTarget": 44}, "motion": {"normal": 200}
}
```
Values above are illustrative, not defaults for every brand. Keep CSS variables in sync; prefer generating them from tokens. For native apps map semantic tokens into SwiftUI/Compose rather than copying web units blindly.

## HTML checklist
Use semantic landmarks and sections for brand, color, type, foundations, components and product example. Show the approved logo prominently; embed actual bytes as base64 with the correct MIME type, descriptive alt text, and intrinsic aspect ratio. Include a separately packaged original. Use inline CSS, system fallbacks and inline JS for actual interactions. Avoid external fonts or scripts if promising offline support. Label visual-only controls as examples. Include responsive layouts, focus-visible styles and reduced motion. If no approved logo is accessible, state the blocker; never substitute an unrelated illustration.

## QA checklist
- Approved source and packaged logo hashes match; embedded data decodes to same bytes.
- JSON parses and all referenced tokens exist; CSS matches documented tokens.
- ZIP integrity, paths and standalone HTML checked.
- Visual check at narrow and wide widths where possible; verify controls and keyboard interaction.
- Contrast check for text/background pairs; normal text 4.5:1, large text 3:1 (WCAG AA); note untested cases.
- Explicit list of pending assets and approval status. A PNG wrapped inside SVG is not a vector deliverable.
