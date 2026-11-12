# mobile-app-design

English · [繁體中文](README.zh-TW.md)

Designs a native iOS (SwiftUI) and Android (Jetpack Compose) app as a whole, in order: a short
brief, the screen map and primary flows, a visual identity of the app's own, tokens and
components written into `DESIGN.md`, then every screen with its hierarchy and all of its states
(loaded, loading, empty, error, first run, large text, dark), interaction, motion and copy.
Each platform keeps its own navigation and controls (Apple HIG, Material 3).

For the look it proposes two or three directions, each as tokens plus a rendered home screen,
and you pick. It steers clear of overused default looks (warm cream pages with clay-orange
accents, serif-over-sans editorial calm, purple gradients); `palette_check.py` flags those
colours in your theme files.

Pair it with [`mobile-layout-stability`](../mobile-layout-stability/) once screens are built.

Use it in Claude Code: `/mobile-app-design`, or say "design this app" / "give it its own look".

MIT.
