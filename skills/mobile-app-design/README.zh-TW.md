# mobile-app-design

[English](README.md) · 繁體中文

用同一份 `DESIGN.md` 設計、實作、檢查原生 iOS（SwiftUI）和 Android（Jetpack Compose）的畫面。每個畫面都要畫出所有狀態（載入中、空的、錯誤、載入完成、大字、深色），兩個平台各用自己的導覽和元件，再用一份「版面穩定」檢查把每個畫面走一遍：從 skeleton 換成內容、重新整理、捲動中，東西都不能跳。

規則來自 Apple Human Interface Guidelines、Material 3、Android Compose 官方文件，加上真的上架過一個 App 學到的事：圖片和價格先留好位置、載入中控制項照樣顯示、清單用真正的 ID、重新整理時舊資料留在畫面上、不要用動畫蓋掉位移。

驗證在模擬器上做：用 debug 參數讓所有請求停在載入中，拍載入中和載入完成兩張，用 `shift_check.py` 比對，列出每張移動了的卡片、圖片區塊和控制項。合格與不合格的參考圖在 [examples/](examples/sheet.png)。

![合格與不合格](examples/sheet.png)

在 Claude Code 裡用 `/mobile-app-design`，或直接說「清單載入時會跳」。

MIT。
