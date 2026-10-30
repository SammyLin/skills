# humanizer-zh

[English](README.md) · 繁體中文

把 AI 寫的中文改得像台灣人寫的。以 [nagameTW/formosa-humanizer](https://github.com/nagameTW/formosa-humanizer) 為基礎：49 種 AI 寫作模式、中文全形標點保護、中國用語對照、提示注入防護都沿用原作。

這一版加了 `scripts/check.py`，把字串比對就能確定的痕跡交給程式抓，模型專心處理需要判斷的部分。改寫前先跑一次找問題，定稿後再跑一次確認「必修」歸零。

| 類別 | 抓什麼 | 結束碼 |
| --- | --- | --- |
| 標點 | 中文句子裡的半形 `, . ? ! : ;` 與直／彎引號 | 必修 |
| 破折 | 貼著中文的單個 `—` 或 `–`（「——」與 1939–1945 不算） | 必修 |
| 殘留 | `utm_source=chatgpt.com`、`turn0search0`、`citeturn`、`【1†source】`、`[產品名稱]` | 必修 |
| 驚嘆 | `！！`、`!!` | 必修 |
| 簡體 | 常見簡體字 | 必修 |
| 用語 | 對照表裡的中國用語與商業黑話 | 需判斷 |
| 詞彙 | 「賦能」「彰顯」這類高頻 AI 詞，只報次數 | 參考 |

```bash
python3 scripts/check.py 稿件.md
python3 scripts/check.py --self-test
```

在 Claude Code 裡：`/humanizer-zh`，或直接說「幫我把這段去 AI 味」。

授權：MIT。原作著作權與致謝見 `NOTICE`。
