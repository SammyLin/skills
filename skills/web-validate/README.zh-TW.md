# web-validate

[English](README.md) · 繁體中文

在真的瀏覽器（[agent-browser](https://github.com/vercel-labs/agent-browser)）裡檢查部署後的網頁，帶回截圖當證據。公開網頁可以，需要登入、而 agent 登不進去或不該自己登的網頁也可以（有 passkey 或 MFA 的公司 SSO、帳號密碼）。

它不會自己登入。你只要手動在一個瀏覽器 profile 裡登入一次，agent 每次複製一份來用；身分提供者那邊已經有登入狀態，按「Sign in」就直接通過，不會卡在 passkey。

第一次用的時候做一次設定：需要的話幫你裝 agent-browser，問你會檢查哪些網站（網址、要不要登入），每個登入打開一次看得到的瀏覽器讓你自己登入。這些存在你電腦上的 `~/.config/web-validate/sites.json`，不進任何 repo。之後每次直接開始工作，只有真的出狀況（新網站、登入過期）才會再找你。

它預設只讀不寫地驗證，每張截圖都先看過才當證據，貼到 GitHub 或 Azure DevOps 的項目上。複製的 profile 留在 scratch 目錄，重開機就清掉。

在 Claude Code 裡用 `/web-validate`，或直接說「上 dev 看一下」。

每個人用自己的帳號登入。profile 資料夾就是你的登入狀態，不要給別人。

MIT。
