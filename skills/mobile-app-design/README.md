# mobile-app-design

English · [繁體中文](README.zh-TW.md)

Designs, builds and audits native iOS (SwiftUI) and Android (Jetpack Compose) screens from one
`DESIGN.md`. Every screen is drawn in all of its states (loading, empty, error, loaded, large
text, dark), each platform keeps its own navigation and controls, and a layout-stability audit
walks every screen so nothing jumps between the skeleton and the content, on refresh, or while
you scroll.

Rules come from Apple's Human Interface Guidelines, Material 3 and the Android Compose docs, plus
what shipping a real app (a deals app with skeleton rows, a quick-return header and async
prices) taught: reserve image and price sizes, keep controls rendered while loading, key lists by
real IDs, keep data on screen during refresh, and never cover a shift with an animation.

It verifies on a simulator: a debug flag holds every request in loading, then `shift_check.py`
compares the loading and loaded screenshots and lists every card, photo block or control that
moved. Reference images of a pass and a fail are in [examples/](examples/sheet.png).

![pass and fail](examples/sheet.png)

Use it in Claude Code: `/mobile-app-design`, or say "the list jumps when it loads".

MIT.
