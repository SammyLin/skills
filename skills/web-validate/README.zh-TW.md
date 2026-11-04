# web-validate

[English](README.md) · 繁體中文

在真的瀏覽器（[agent-browser](https://github.com/vercel-labs/agent-browser)）裡檢查部署後的網頁，帶回截圖當證據。公開網頁可以，需要登入、而 agent 登不進去或不該自己登的網頁也可以（有 passkey 或 MFA 的公司 SSO、帳號密碼）。

它不會自己登入。你只要手動在一個瀏覽器 profile 裡登入一次，agent 每次複製一份來用；身分提供者那邊已經有登入狀態，按「Sign in」就直接通過，不會卡在 passkey。

每次執行都會先跑設定檢查，所以新電腦會一步一步帶你設定：

1. 有沒有裝 agent-browser（沒有就問你要不要幫你裝，連同它用的瀏覽器）
2. 網站在不在 `~/.config/web-validate/sites.json` 裡（沒有就問你網址和登入頁；這份清單只留在你的電腦上，不進任何 repo）
3. 需要登入的網站，profile 是不是登入狀態（打開一個看得到的瀏覽器讓你登入，再確認成功）；不用登入的網站跳過這步

接著預設只讀不寫地驗證，每張截圖都先看過才當證據，貼到 GitHub 或 Azure DevOps 的項目上，最後刪掉它複製的 profile。

在 Claude Code 裡用 `/web-validate`，或直接說「上 dev 看一下」。

每個人用自己的帳號登入。profile 資料夾就是你的登入狀態，不要給別人。

MIT。
