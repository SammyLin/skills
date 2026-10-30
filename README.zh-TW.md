# SammyLin/skills

[English](README.md) · 繁體中文

我自己在用、信得過的 agent skill，集中放在這裡。每個 skill 放在 `skills/<名稱>/`，各有一份 `SKILL.md`，資料夾名稱就是 skill 名稱。

## 我的 skill

說明文件有英文與繁體中文兩版；你用哪種語言跟它說話，它就用哪種語言回覆。

| Skill | 用途 | 來源 |
| --- | --- | --- |
| [`store-screenshots`](skills/store-screenshots/) | App Store 與 Google Play 上架圖：從程式碼找出使用者利益，先給你確認分鏡表才產圖，用 App 真實畫面產出商店規格尺寸，附檢查與評分，支援多語系。 | 改寫自 [adamlyttleapps](https://github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots)，參考 [taste-skill](https://github.com/leonxlnx/taste-skill)、[shots](https://github.com/hypersocialinc/shots)、[store-screenshots](https://github.com/LeeHueeng/store-screenshots) |
| [`humanizer-zh`](skills/humanizer-zh/) | 把中文文字的 AI 味拿掉，寫給台灣讀者：49 種模式、全形標點、中國用語對照，加上機械檢查腳本。 | 以 [nagameTW/formosa-humanizer](https://github.com/nagameTW/formosa-humanizer) 為基礎，MIT |

## 收錄的 skill

原樣複製，保留各自的授權。taste-skill classics 都要點名才會執行（例如 `/minimalist-ui`），不會自動啟動。

| Skill | 用途 | 來源 |
| --- | --- | --- |
| [`humanizer`](skills/humanizer/) | 去除英文文字的 AI 寫作痕跡，依據維基百科「Signs of AI writing」。 | [blader/humanizer](https://github.com/blader/humanizer) |
| [`high-end-visual-design`](skills/high-end-visual-design/) | 沉穩精緻的介面：柔和對比、大量留白、彈性動畫。 | [taste-skill-classics](https://github.com/Leonxlnx/taste-skill-classics) |
| [`minimalist-ui`](skills/minimalist-ui/) | 編輯感的產品介面，色彩克制、結構俐落。 | taste-skill-classics |
| [`industrial-brutalist-ui`](skills/industrial-brutalist-ui/) | 硬派機械風：瑞士字體、強烈對比、實驗性版面。 | taste-skill-classics |
| [`gpt-taste`](skills/gpt-taste/) | 給 GPT 與 Codex 的嚴格版：版面變化、AIDA 結構、GSAP 動畫。 | taste-skill-classics |
| [`stitch-design-taste`](skills/stitch-design-taste/) | Google Stitch 用的規則，可另外匯出 `DESIGN.md`。 | taste-skill-classics |
| [`design-taste-frontend-v2-experimental`](skills/design-taste-frontend-v2-experimental/) | v2 之前的預設版本：單一檔案，用參數調整風格。 | taste-skill-classics |
| [`design-taste-frontend-v1`](skills/design-taste-frontend-v1/) | 最早的 taste-skill。 | taste-skill-classics |

## 安裝

```bash
npx skills add SammyLin/skills --global                        # 全部，所有專案都能用
npx skills add SammyLin/skills -s store-screenshots --global   # 只裝一個
npx skills add SammyLin/skills -l                              # 列出有哪些
```

也可以當 Claude Code 外掛安裝：`/plugin marketplace add SammyLin/skills`。

## 更新

每台電腦在有新的 push 之後跑：

```bash
npx skills update -g
```

要改 skill 請改這個 repo 的副本，不要改安裝好的那份，下次更新會被覆蓋。

## 新增 skill

1. 建立 `skills/<名稱>/SKILL.md`，frontmatter 要有 `name` 與 `description`，資料夾名稱要等於 `name`。
2. 在這份與 `README.md` 的表格各加一列。
3. 自己寫的 skill：附上 `README.md` 與 `README.zh-TW.md`。
4. 別人的 skill：授權允許才收，`LICENSE` 放在它的資料夾裡，並註明出處。

## 授權

MIT（見 `LICENSE`）。收錄的 skill 保留各自資料夾裡的授權。
