# SammyLin/skills

[English](README.md) · 繁體中文

我自己在用、信得過的 agent skill，集中放在這裡。每個 skill 放在 `skills/<名稱>/`，各有一份 `SKILL.md`，資料夾名稱就是 skill 名稱。

## 我的 skill

說明文件有英文與繁體中文兩版；你用哪種語言跟它說話，它就用哪種語言回覆。

| Skill | 用途 | 來源 |
| --- | --- | --- |
| [`store-screenshots`](skills/store-screenshots/) | App Store 與 Google Play 上架圖：從程式碼找出使用者利益，先給你確認分鏡表才產圖，用 App 真實畫面產出商店規格尺寸，附檢查與評分，支援多語系。 | 改寫自 [adamlyttleapps](https://github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots)，參考 [taste-skill](https://github.com/leonxlnx/taste-skill)、[shots](https://github.com/hypersocialinc/shots)、[store-screenshots](https://github.com/LeeHueeng/store-screenshots) |
| [`humanizer-zh`](skills/humanizer-zh/) | 把中文文字的 AI 味拿掉，寫給台灣讀者：49 種模式、全形標點、中國用語對照，加上機械檢查腳本。 | 以 [nagameTW/formosa-humanizer](https://github.com/nagameTW/formosa-humanizer) 為基礎，MIT |
| [`grill-me`](skills/grill-me/) | 開工前拷問計畫：只問重大決策（難以回頭、影響使用者／金錢／安全、卡住其他決策、前後矛盾），其他直接給預設值，用選擇題介面點選回答，值得記錄的才寫 ADR。 | 改寫自 Matt Pocock 的 [`grill-with-docs`](https://github.com/mattpocock/skills)，MIT |

### 成品範例

**store-screenshots**：範例上架圖在搜尋結果裡的樣子，上排淺色、下排深色（示範用的假 App）。

![store-screenshots 範例](docs/images/store-screenshots-sheet-zh-TW.webp)

## 收錄的 skill

原樣複製，保留各自的授權。taste-skill classics 都要點名才會執行（例如 `/minimalist-ui`），不會自動啟動。

| Skill | 用途 | 來源 |
| --- | --- | --- |
| [`ip-as-logo`](skills/ip-as-logo/) | 極簡、可愛、能直接當 logo 的吉祥物角色：先提三個方向，再產六張候選，角色從左下角探出來。 | [s1dashu/ip-as-logo-skill](https://github.com/s1dashu/ip-as-logo-skill) |
| [`humanizer`](skills/humanizer/) | 去除英文文字的 AI 寫作痕跡，依據維基百科「Signs of AI writing」。 | [blader/humanizer](https://github.com/blader/humanizer) |
| [`high-end-visual-design`](skills/high-end-visual-design/) | 沉穩精緻的介面：柔和對比、大量留白、彈性動畫。 | [taste-skill-classics](https://github.com/Leonxlnx/taste-skill-classics) |
| [`minimalist-ui`](skills/minimalist-ui/) | 編輯感的產品介面，色彩克制、結構俐落。 | taste-skill-classics |
| [`industrial-brutalist-ui`](skills/industrial-brutalist-ui/) | 硬派機械風：瑞士字體、強烈對比、實驗性版面。 | taste-skill-classics |
| [`gpt-taste`](skills/gpt-taste/) | 給 GPT 與 Codex 的嚴格版：版面變化、AIDA 結構、GSAP 動畫。 | taste-skill-classics |
| [`stitch-design-taste`](skills/stitch-design-taste/) | Google Stitch 用的規則，可另外匯出 `DESIGN.md`。 | taste-skill-classics |
| [`design-taste-frontend-v2-experimental`](skills/design-taste-frontend-v2-experimental/) | v2 之前的預設版本：單一檔案，用參數調整風格。 | taste-skill-classics |
| [`design-taste-frontend-v1`](skills/design-taste-frontend-v1/) | 最早的 taste-skill。 | taste-skill-classics |

### 成品範例

**ip-as-logo**（取自上游 repo）：

![ip-as-logo 範例](skills/ip-as-logo/assets/ip-as-logo-wall.webp)

**taste-skill classics**：同一份需求（Harbor，家庭共用的購物清單與晚餐規劃 App）分別用各 skill 做出的頁面，1440px 寬、前 1800px。這些頁面是為這份 README 做的，不是上游作者的作品。

<table>
<tr><td width="50%"><img src="docs/images/taste-high-end-visual-design.webp" alt="high-end-visual-design"><br><code>high-end-visual-design</code> · 沉穩精緻</td><td width="50%"><img src="docs/images/taste-minimalist-ui.webp" alt="minimalist-ui"><br><code>minimalist-ui</code> · 編輯感極簡</td></tr>
<tr><td width="50%"><img src="docs/images/taste-industrial-brutalist-ui.webp" alt="industrial-brutalist-ui"><br><code>industrial-brutalist-ui</code> · 硬派機械風</td><td width="50%"><img src="docs/images/taste-gpt-taste.webp" alt="gpt-taste"><br><code>gpt-taste</code> · GPT 嚴格版</td></tr>
<tr><td width="50%"><img src="docs/images/taste-stitch-design-taste.webp" alt="stitch-design-taste"><br><code>stitch-design-taste</code> · Stitch 設計系統</td><td width="50%"><img src="docs/images/taste-design-taste-frontend-v2-experimental.webp" alt="design-taste-frontend-v2-experimental"><br><code>design-taste-frontend-v2-experimental</code> · taste v2 實驗版</td></tr>
<tr><td width="50%"><img src="docs/images/taste-design-taste-frontend-v1.webp" alt="design-taste-frontend-v1"><br><code>design-taste-frontend-v1</code> · taste v1</td></tr>
</table>

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
4. 會產出視覺成品的 skill：在 `docs/images/` 放一張範例圖，中英文 README 都要附上（圖放在 `skills/` 之外，安裝時才不會一起裝）。
5. 別人的 skill：授權允許才收，`LICENSE` 放在它的資料夾裡，並註明出處。

## 授權

MIT（見 `LICENSE`）。收錄的 skill 保留各自資料夾裡的授權。
