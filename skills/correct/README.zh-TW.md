# correct

[English](README.md) · 繁體中文

找出 agent 在這個 repo 裡一犯再犯的錯，從能擋住的最高層級下手，讓它沒辦法再犯：架構、型別、錯誤訊息直接寫出修法的 lint、測試、agent hook，最後才寫文件。改寫自 Lauren Tan 在 pstack 裡的 [`correct`](https://github.com/cursor/plugins/tree/main/pstack/skills/correct)。

| | pstack correct | correct |
| --- | --- | --- |
| 證據來源 | commit、revert、review、agent 規則檔 | 一樣，另外寫明要用哪些 `git`、`gh`、`az` 指令去查 |
| 層級 | 架構、型別/lint、測試、文件 | 在文件之前多一層 agent hook（`PreToolUse`） |
| 動手前 | 直接修 | 先列出「錯誤類型／證據／層級」表，等你點頭 |
| 證明 | 新檢查必須擋得住一次真實的舊錯 | 一樣，做法是在暫用 worktree 重新套回當年的錯誤 diff |
| commit | 每類一個 | 一樣，而且開分支，不直接 commit 到預設分支 |

在 Claude Code 或 Codex 裡輸入 `/correct`。

MIT 授權。改寫自 Lauren Tan 的 pstack（MIT）。
