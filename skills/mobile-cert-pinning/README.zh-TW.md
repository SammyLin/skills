# mobile-cert-pinning

[English](README.md) · 繁體中文

幫原生 iOS 和 Android App 連自家後台的連線做憑證綁定（SSL pinning）。這樣即使手機裝了 Proxyman、Charles 或 mitmproxy 的憑證，也看不到、改不了 API 的內容。

綁的是你的憑證供應商可能使用的每一家 CA 的根憑證公鑰（附上 Cloudflare 的完整清單）。iOS 用 `NSPinnedDomains`，Android 用 network security config，兩邊共用同一份清單。`check_pins.py` 會檢查這些事：

- 兩邊的清單一致
- `debug-overrides` 沒有不小心把綁定關掉
- Android 的綁定還沒快到期
- 每個網址現在的憑證鏈還對得上

每天由 CI 跑一次，憑證供應商換 CA 時，會在使用者連不上之前先通知你。

上架前會正反兩面都驗證：正確的清單連得上、故意放錯的公鑰會被擋，實機開抓包工具時只看得到握手失敗。

也可以檢查現有的 App：哪些網址在哪個平台有綁、還缺什麼。

在 Claude Code 裡用 `/mobile-cert-pinning`，或直接說「幫 App 加 SSL pinning」「不要讓人抓包看 API」「檢查我們的 App 有沒有綁憑證」。

MIT。
