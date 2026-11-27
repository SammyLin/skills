# pr-evidence

[English](README.md) · 繁體中文

把「這個改動真的有效」的證據直接放進 GitHub PR。

依工作性質挑最有力的證據：有操作、會動的用 **GIF**；靜態畫面改動用**改前、改後截圖**；
沒有畫面的用**文字說明加 log**。可以從 iOS 模擬器、Android 模擬器或瀏覽器錄影，
用 ffmpeg 轉成 GitHub 顯示得了的 GIF（兩段式調色盤，控制在 8 MB 以下），再放進 PR。

GitHub 沒有上傳圖片到 PR 的 API，所以檔案 commit 到 PR 分支的 `docs/pr/<PR 號>/`，
用 commit SHA 的連結嵌進 PR 說明。merge 前再加一個 commit 刪掉：squash merge 之後 main 不會有這些檔案，
PR 裡的圖片照樣看得到，因為 GitHub 會保留 PR 的每個 commit。

- `scripts/to-gif.sh`：影片轉 GIF（8 MB 以下）
- `scripts/attach.sh`：把檔案 commit 到 PR 分支，印出要貼的 Markdown
- `scripts/detach.sh`：merge 前移除

需要 `ffmpeg`、`gh`，以及要錄的平台的 Xcode 或 Android SDK。在 Claude Code 裡用 `/pr-evidence`，
或說「PR 附 GIF」。

MIT.
