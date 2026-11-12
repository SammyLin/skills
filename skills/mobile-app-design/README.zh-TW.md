# mobile-app-design

[English](README.md) · 繁體中文

把原生 iOS（SwiftUI）和 Android（Jetpack Compose）App 當成一個整體來設計，順序是：先寫一段簡短的產品說明，再畫畫面地圖和主要流程，定出 App 自己的視覺識別，把 token 和元件寫進 `DESIGN.md`，最後才是每個畫面的層次和所有狀態（載入完成、載入中、空的、錯誤、第一次使用、大字、深色）、互動、動態和文案。兩個平台各用自己的導覽和元件（Apple HIG、Material 3）。

外觀會先提兩到三個方向，每個都附 token 和一張畫好的首頁，由你挑。它會避開被用到爛的預設風格（暖米白底配陶土橘、襯線標題配無襯線內文的安靜雜誌風、紫藍漸層），`palette_check.py` 會把主題檔裡這類顏色抓出來。

畫面做好之後，搭配 [`mobile-layout-stability`](../mobile-layout-stability/) 檢查畫面跳動。

在 Claude Code 裡用 `/mobile-app-design`，或直接說「幫這個 App 做設計」「給它自己的風格」。

MIT。
