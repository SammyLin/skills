# DESIGN.md template

One file at the app repo root. Both platforms follow it; when the app and this file disagree,
fix one of them the same day. Record who decided what and when, so a later agent does not undo it.

```markdown
# Design System: <App name>
Decided: <date>, <who>.

## 0. Brief
- Who, the one job, how often, where (one hand in an aisle, at a desk), what makes it different

## Identity
- Direction chosen: <name, 3-5 words from the brief>; rejected: <the other directions, one line why>
- Any colour palette_check.py flags that the owner chose on purpose

## 1. Principles
- <how dense a screen is, e.g. 4–5 items visible on one phone screen>
- <every important action has text, not only an icon>
- <what each accent colour means, one meaning each>

## 2. Colour (tokens, light / dark)
- Background, Surface, Ink, Ink 2, Muted, Faint
- Accent (primary buttons, selected tab), Accent soft (badges)
- Warning soft + text, Positive (only where it means "done / on")
- Skeleton (a little darker than Background; loading is never blank white)

## 3. Typography
- Font: system (SF Pro / Roboto, CJK system font) or <bundled font>
- Sizes: page title, panel title, body, caption, price (tabular digits)
- Scales with Dynamic Type / font scale; caps per component

## 4. Components (sizes are the contract for skeletons)
- Primary button: <shape, height>   Secondary button: <shape, height>
- Card: <radius, padding, shadow, spacing between cards>
- List row: <image size, line count, badge row height>
- Segment control, chips, search bar: <height>
- Skeleton: <shared component name>; spinner only for actions the user started

## 5. Screens
Screen map (tabs, pushes, sheets) and the 2-3 primary flows. For each screen: purpose, header controls (fixed), content blocks in order, each block's
loading / empty / error copy.

## 6. Motion
- What animates (user-caused changes), what never does (data arriving)
- Reduce Motion / remove animations behaviour

## 7. Platform differences
- Anything Android does differently from iOS, and why

## 8. Banned
- <emoji in UI, hairline borders, colours outside the tokens, icon-only primary actions, ...>
- The overused looks in visual-identity.md, unless chosen above
```
