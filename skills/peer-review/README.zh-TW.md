# peer-review

[English](README.md) · 繁體中文

從某個基準點（沒指定就用 `main`）開始，把改動分成「規範」和「需求」兩條線各自審查，而且換一個 model 來審。改寫自 Matt Pocock 的 [`code-review`](https://github.com/mattpocock/skills)；「指控要實際跑過」的規則取自 pstack 的 [`interrogate`](https://github.com/cursor/plugins/tree/main/pstack/skills/interrogate)。

| | code-review | peer-review |
| --- | --- | --- |
| 誰來審 | 自己開的 sub-agent | 另一個 model：先找 Antigravity，再找 Codex 或 Claude（不是你自己的那個）；都失敗才用自己的 sub-agent |
| 需求從哪來 | `/setup-matt-pocock-skills` 設定好的 issue tracker | 看 `origin` 判斷：GitHub 用 `gh` 抓 issue，Azure DevOps 用 `az` 抓 work item |
| 沒給基準點 | 問你 | 直接用 `main` |
| 報告 | 兩條線並排 | 一樣並排，另外標出每條線是誰審的，並抽查引用的行數是否存在 |
| 速度 | reviewer 自己去拉 diff | 1500 行以內的 diff 直接附在 brief 裡；每個 reviewer 最多 15 分鐘，逾時就換下一個（只防卡死；400 行的 diff 實測約 1 到 2 分鐘）；不到 30 行時兩條線合成一次呼叫；重現步驟最多跑 3 條，同時跑 |
| 「實作有錯」的指控 | 照 reviewer 說的列出 | 必須附重現指令，在暫用 worktree 實際跑過，分成已證實、已推翻、僅是懷疑三類 |

Fowler 程式碼異味清單，以及「兩條線不合併排名」的規則，都跟原作一樣。

在 Claude Code 或 Codex 裡輸入 `/peer-review`，或直接說「從 main 開始做 peer review」。

MIT 授權。改寫自 Matt Pocock 的 skills（MIT）。
