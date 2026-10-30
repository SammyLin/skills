# humanizer-zh

English · [繁體中文](README.zh-TW.md)

Rewrites AI-generated Chinese so it reads like a person in Taiwan wrote it. Built on
[nagameTW/formosa-humanizer](https://github.com/nagameTW/formosa-humanizer), which keeps the
49 AI-writing patterns, full-width punctuation protection, the mainland-term glossary and the
prompt-injection boundary. The skill itself is written in Chinese, because it edits Chinese text.

This version adds `scripts/check.py`, which catches what string matching can decide so the model
can spend its attention on what needs judgement. The rewrite loop runs it before rewriting to find
problems, and again on the final text, where every "must fix" has to be gone.

| Kind | What it flags | Exit code |
| --- | --- | --- |
| Punctuation | Half-width `, . ? ! : ;` and straight or curly quotes inside Chinese sentences | must fix |
| Dash | A single `—` or `–` touching Chinese (the paired Chinese dash `——` and ranges like 1939–1945 pass) | must fix |
| Residue | `utm_source=chatgpt.com`, `turn0search0`, `citeturn`, `【1†source】`, unfilled `[產品名稱]` | must fix |
| Exclamation | `！！`, `!!` | must fix |
| Simplified | Common simplified characters | must fix |
| Terms | Mainland terms and business jargon from the glossary | judgement (quotes and proper nouns may stay) |
| AI words | Words like 賦能 and 彰顯; counted only | for reference |

```bash
python3 scripts/check.py draft.md
python3 scripts/check.py --self-test
```

Use it in Claude Code: `/humanizer-zh`, or say "幫我把這段去 AI 味" ("take the AI flavour out of
this").

MIT. The original authors' copyright and credits are in `NOTICE`.
