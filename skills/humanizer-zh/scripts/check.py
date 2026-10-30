#!/usr/bin/env python3
"""
humanizer-zh 機械檢查：抓字串比對就能確定的 AI 痕跡，判斷交給模型。

  python3 check.py 稿件.md          # 檢查檔案
  python3 check.py - < 稿件.txt     # 從標準輸入讀
  python3 check.py --self-test      # 跑內建測試

抓的東西（對應 SKILL.md 的模式編號）：
  標點  中文句子裡的半形 , . ? ! : ; 與直／彎引號（核心規則、模式 35）
  破折  夾在中文裡的西式 — 或 –（模式 14）；數字區間 1939–1945 不算
  殘留  utm_source=chatgpt.com、turn0search0、citeturn、【1†source】、[oaicite:0]、
        未填的 [產品名稱]／（請填寫）（模式 45）
  驚嘆  連續驚嘆號（模式 44）
  簡體  常見簡體字（模式 34）
  用語  references/zh-cn-glossary.md 裡的中國用語與商業黑話（模式 34）
  詞彙  模式 7 的高頻 AI 詞彙，只報數量（成群出現才是訊號）

程式碼區塊、行內程式碼與 frontmatter 不檢查。只用標準函式庫。
有任何「標點／破折／殘留／驚嘆／簡體」命中時結束碼為 1；「用語」要看語境
（引文、專有名詞、作者刻意用的詞可以留），只列出不影響結束碼。
"""

import re
import sys
from pathlib import Path

GLOSSARY = Path(__file__).resolve().parent.parent / "references" / "zh-cn-glossary.md"

CJK = r"[㐀-鿿豈-﫿]"
HALF_PUNCT = re.compile(rf"(?<={CJK})[,.?!:;](?!\d)|[,?!:;](?={CJK})")
QUOTES = re.compile(rf"(?<={CJK})[\"“”‘’]|[\"“”‘’](?={CJK})")
# 中文破折號「——」是兩個 U+2014，合法；單個 — 或 – 貼著中文才算西式。
SINGLE_DASH = r"(?:(?<!—)—(?!—)|–)"
DASH = re.compile(rf"(?<={CJK})\s*{SINGLE_DASH}|{SINGLE_DASH}\s*(?={CJK})")
BANG = re.compile(r"[！!]{2,}")
RESIDUE = re.compile(
    r"utm_source=chatgpt\.com|[?&]ref=chatgpt\.com|\bturn\d+(?:search|news|view|image)\d+\b"
    r"|citeturn\w*|【\d+†[^】]*】|\[oaicite:\d+\]"
    r"|\[(?:在此|請)?(?:插入|填入|輸入)?(?:產品|公司|品牌|姓名|名稱|日期|網址|連結)[^\]\n]{0,8}\]"
    r"|[（(]請填寫[）)]"
)
# 繁體不會出現的高頻簡體字。ponytail: 只收常見字，不是完整繁簡表；要完整就接 OpenCC。
SIMPLIFIED = re.compile("[这们说时为发对开关见现进过还没问题学会经个来么样认让请谁该给长门间听写东车书买卖热钱电话术网络软视频数据库优质统]")
AI_WORDS = (
    "此外 值得注意的是 值得一提的是 深入探討 全面 顯著 致力於 旨在 打造 賦能 助力 聚焦 涵蓋 凸顯 彰顯 "
    "體現 驅動 引領 重塑 開啟新篇章 里程碑 不可或缺 蓬勃發展 日新月異 格局 態勢 綜上所述 悄然"
).split()


def load_glossary():
    """(詞, 建議, 要看語境) from the glossary tables and the 商業黑話 line."""
    terms = []
    if not GLOSSARY.exists():
        return terms
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) == 2 and not set(cells[0]) <= set("-: ") and cells[0] != "中國用語":
            contextual = "（" in cells[0]
            left = re.sub(r"（[^）]*）", "", cells[0])
            for t in re.split(r"[／/]", left):
                if t.strip():
                    terms.append((t.strip(), cells[1], contextual))
        elif line.startswith("「") and "整批換成" in line:
            for t in re.findall(r"[^「」、（）]+(?=[、」（])", line.split("」")[0] + "」"):
                terms.append((t.strip(), "平實說法或刪掉", True))
    return terms


def prose_lines(text):
    """Yield (line number, line) outside frontmatter and code fences, inline code blanked."""
    lines = text.splitlines()
    i, fence = 0, None
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                i = j + 1
                break
    for n in range(i, len(lines)):
        line = lines[n]
        m = re.match(r"\s*(```|~~~)", line)
        if m:
            fence = None if fence == m.group(1) else (fence or m.group(1))
            continue
        if fence:
            continue
        yield n + 1, re.sub(r"`[^`]*`", lambda x: " " * len(x.group(0)), line)


def check(text, glossary):
    hits = []  # (line, col, kind, snippet, blocking)
    words = {}

    def add(n, line, m, kind, blocking=True, note=""):
        s = max(0, m.start() - 6)
        snippet = line[s:m.end() + 6].strip() + (f"  → {note}" if note else "")
        hits.append((n, m.start() + 1, kind, snippet, blocking))

    for n, line in prose_lines(text):
        url_free = re.sub(r"https?://\S+", lambda x: " " * len(x.group(0)), line)
        for m in HALF_PUNCT.finditer(url_free):
            add(n, line, m, "標點")
        for m in QUOTES.finditer(url_free):
            add(n, line, m, "標點", note="改用「」")
        for m in DASH.finditer(url_free):
            add(n, line, m, "破折")
        for m in BANG.finditer(line):
            add(n, line, m, "驚嘆")
        for m in RESIDUE.finditer(line):
            add(n, line, m, "殘留")
        for m in SIMPLIFIED.finditer(url_free):
            add(n, line, m, "簡體")
        for term, sug, contextual in glossary:
            for m in re.finditer(re.escape(term), url_free):
                add(n, line, m, "用語", False, f"{sug}" + ("（依語境）" if contextual else ""))
        for w in AI_WORDS:
            c = url_free.count(w)
            if c:
                words[w] = words.get(w, 0) + c
    return hits, words


def report(hits, words):
    for n, col, kind, snippet, _ in sorted(hits):
        print(f"{n}:{col}  [{kind}]  {snippet}")
    blocking = sum(1 for h in hits if h[4])
    soft = len(hits) - blocking
    if words:
        listed = "、".join(f"{w}×{c}" for w, c in sorted(words.items(), key=lambda x: -x[1]))
        print(f"AI 詞彙 {sum(words.values())} 次：{listed}")
    print(f"必修 {blocking} 處，需判斷 {soft} 處。")
    return 1 if blocking else 0


def self_test():
    g = load_glossary()
    assert any(t == "視頻" for t, _, _ in g) and any(t == "賦能" for t, _, _ in g), "glossary not parsed"
    bad = (
        "這個功能還不穩定,建議先測試.確認後再上線?\n"
        "他說\"很好\"。這很重要—真的。\n"
        "見 https://a.com/x?utm_source=chatgpt.com 與 turn0search0。\n"
        "太棒了！！！請洽 [產品名稱]（請填寫）\n"
        "这个视频很好。\n"
    )
    hits, _ = check(bad, g)
    kinds = {h[2] for h in hits}
    assert {"標點", "破折", "殘留", "驚嘆", "簡體"} <= kinds, kinds
    good = (
        "---\ntitle: a, b.\n---\n"
        "這個功能還不穩定，建議先測試。確認後再上線嗎？\n"
        "他說「很好」。版本 1.5 在 1939–1945 年間、網址 https://a.com/?q=1,2 不算。\n"
        "```\nprint('a,b.')\n```\n"
        "用 `a,b.` 呼叫，抗戰——八年。\n"
    )
    hits, _ = check(good, g)
    assert not [h for h in hits if h[4]], hits
    hits, _ = check("我們透過雲端服務器處理。", g)
    assert [h for h in hits if h[2] == "用語" and "伺服器" in h[3]], hits
    print("self-test ok")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--self-test":
        return self_test()
    text = sys.stdin.read() if sys.argv[1] == "-" else Path(sys.argv[1]).read_text(encoding="utf-8")
    sys.exit(report(*check(text, load_glossary())))


if __name__ == "__main__":
    main()
