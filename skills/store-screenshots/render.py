#!/usr/bin/env python3
"""
Render an App Store screenshot set from screenshots/set.json.

Each shot is laid out in HTML/CSS and photographed by headless Chrome at the
exact App Store Connect size, so there is no crop/resize step and the app's
own pixels are never redrawn by a model. The same page measures itself
(headline lines, edges, contrast, fonts) and the result is the gate.

  python3 render.py screenshots/set.json            # all shots + sheet
  python3 render.py screenshots/set.json --only 2   # one shot (1-based)

Stdlib only. Needs Google Chrome / Chromium.
"""

import argparse
import html
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unicodedata
import zlib

SIZES = {
    "6.9": (1320, 2868), "6.7": (1290, 2796), "6.5": (1242, 2688),
    "ipad-13": (2064, 2752), "android": (1080, 1920),
}
LAYOUTS = ("poster", "breakout", "bleed")

# Phrases that claim proof. Allowed only when set.json marks it real ("proof": [...]).
PROOF = re.compile(
    r"#1\b|no\.?\s*1\b|best app|editor'?s choice|award|million|5[ -]?star|★|top[- ]rated|trusted by",
    re.I,
)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")

CHROME_CANDIDATES = [
    os.environ.get("CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]

PAGE = """<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8">
{font_css}
<style>
  :root {{
    --W: {W}px; --H: {H}px; --pad: {pad}px;
    --ground: {ground}; --ink: {ink}; --accent: {accent};
    --family: {family}; --weight: {weight}; --tracking: {tracking};
    --size: {size}px;
  }}
  * {{ box-sizing: border-box; margin: 0; }}
  html, body {{ width: var(--W); height: var(--H); overflow: hidden; background: var(--ground); }}
  .canvas {{ position: relative; width: var(--W); height: var(--H); overflow: hidden; background: var(--ground); }}
  h1 {{
    position: absolute; left: var(--pad); right: var(--pad); top: {top}px;
    font-family: var(--family); font-weight: var(--weight); font-size: var(--size);
    line-height: 0.98; letter-spacing: var(--tracking); color: var(--ink);
    text-align: {align}; text-transform: {transform}; text-wrap: balance;
    line-break: strict;
  }}
  /* Break CJK headlines at phrase/word boundaries, not mid-word. */
  h1:lang(ja) {{ word-break: auto-phrase; }}
  h1:lang(ko) {{ word-break: keep-all; }}
  .device {{
    position: absolute; left: 50%; transform: translateX(-50%);
    width: {dev_w}px; padding: {bezel}px; border-radius: {dev_r}px;
    background: #0b0b0c; box-shadow: inset 0 0 0 {rim}px #2a2a2d;
  }}
  .device .screen {{ position: relative; border-radius: {scr_r}px; overflow: hidden; background: #000; }}
  .device img {{ display: block; width: 100%; }}
  .island {{
    position: absolute; top: {isl_top}px; left: 50%; transform: translateX(-50%);
    width: {isl_w}px; height: {isl_h}px; border-radius: 999px; background: #000;
  }}
  .bleed {{
    position: absolute; width: {bleed_w}px; left: {bleed_x}px;
    border-radius: {scr_r}px; overflow: hidden;
  }}
  .bleed img {{ display: block; width: 100%; }}
  /* The one thing that truly floats, so the one shadow. */
  .panel {{
    position: absolute; left: 50%; transform: translateX(-50%);
    background-repeat: no-repeat; border-radius: {panel_r}px;
    box-shadow: 0 {sh_y}px {sh_b}px rgba(0,0,0,.28);
  }}
</style></head>
<body><div class="canvas">
  <h1 id="headline">{headline}</h1>
  {stage}
</div>
<script>
(async () => {{
  const W = {W}, H = {H}, PAD = {pad};
  const img = document.querySelector('.screen img, .bleed img');
  // img.decode() can hang under --virtual-time-budget; onload does not.
  await Promise.all([document.fonts.ready, new Promise(r => img.complete ? r() : (img.onload = img.onerror = r))]);

  const h1 = document.getElementById('headline');
  const hb = h1.getBoundingClientRect();
  const holder = document.querySelector('.device, .bleed');
  holder.style.top = Math.round(hb.bottom + {gap}) + 'px';
  // A short headline lifts the device; grow it so it still bleeds off the bottom edge.
  const d = holder.getBoundingClientRect();
  if (d.bottom < H + 40) holder.style.width = (d.width * (H + 40 - d.top) / d.height) + 'px';

  const crop = {crop};
  if (crop) {{
    const scr = document.querySelector('.screen').getBoundingClientRect();
    const k = scr.width / img.naturalWidth;          // screenshot px -> canvas px
    const scale = {panel_w} / (crop.w * k);           // enlarge to panel width
    const p = document.querySelector('.panel');
    p.style.width = Math.round(crop.w * k * scale) + 'px';
    p.style.height = Math.round(crop.h * k * scale) + 'px';
    p.style.top = Math.round(scr.top + crop.y * k - (crop.h * k * (scale - 1)) / 2) + 'px';
    p.style.backgroundImage = `url("${{img.src}}")`;
    p.style.backgroundSize = `${{img.naturalWidth * k * scale}}px auto`;
    p.style.backgroundPosition = `${{-crop.x * k * scale}}px ${{-crop.y * k * scale}}px`;
  }}

  const lh = parseFloat(getComputedStyle(h1).lineHeight);
  const range = document.createRange(); range.selectNodeContents(h1);
  const tb = range.getBoundingClientRect();  // the ink, not the box: catches a word overflowing
  const lum = c => {{
    const v = c.match(/\\d+(\\.\\d+)?/g).slice(0, 3).map(n => {{
      n /= 255; return n <= 0.03928 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4;
    }});
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
  }};
  const a = lum(getComputedStyle(h1).color), b = lum(getComputedStyle(document.body).backgroundColor);
  const fam = getComputedStyle(h1).fontFamily.split(',')[0].replace(/["']/g, '').trim();
  document.body.dataset.report = JSON.stringify({{
    lines: Math.round(hb.height / lh),
    left: Math.round(tb.left), right: Math.round(W - tb.right),
    headlineBottom: Math.round(hb.bottom),
    contrast: +((Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)).toFixed(2),
    font: fam, fontLoaded: fam.startsWith('-') || document.fonts.check(`{weight} 100px "${{fam}}"`),
    imgLoaded: img.naturalWidth > 0,
  }});
}})();
</script></body></html>
"""

SHEET = """<!doctype html><html><head><meta charset="utf-8"><style>
  * {{ margin: 0; box-sizing: border-box; }}
  body {{ width: {W}px; height: {H}px; display: grid; grid-template-rows: 1fr 1fr; }}
  section {{ display: flex; gap: 28px; align-items: center; padding: 0 48px; }}
  .light {{ background: #f2f2f7; }} .dark {{ background: #000; }}
  img {{ width: {tw}px; border-radius: 22px; display: block; }}
</style></head><body>
<section class="light">{imgs}</section><section class="dark">{imgs}</section>
</body></html>"""


def find_chrome():
    for c in CHROME_CANDIDATES:
        if c and os.path.exists(c):
            return c
    sys.exit("Chrome/Chromium not found. Set CHROME=/path/to/chrome.")


def chrome(binary, url, W, H, *, screenshot=None):
    args = [
        binary, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", "--virtual-time-budget=8000",
        "--allow-file-access-from-files",
    ]
    if not screenshot:
        out = subprocess.run(args + [f"--window-size={W},{H}", "--dump-dom", url],
                             capture_output=True, text=True, timeout=90)
        return out.stdout
    # New headless keeps a band of window chrome: the viewport is shorter than
    # --window-size and the screenshot's bottom rows are blank. Grow the window
    # by that band, then crop it off.
    band = chrome_band(binary)
    subprocess.run(args + [f"--window-size={W},{H + band}", f"--screenshot={screenshot}", url],
                   capture_output=True, timeout=90)
    if band:
        crop_png_top(screenshot, H)


def crop_png_top(path, H):
    """Keep the first H rows of a non-interlaced PNG. PNG row filters only look
    at the row above, so the first H filtered rows stay valid as they are."""
    with open(path, "rb") as f:
        data = f.read()
    chunks, i, idat = [], 8, b""
    while i < len(data):
        n, kind = struct.unpack(">I4s", data[i:i + 8])
        body = data[i + 8:i + 8 + n]
        if kind == b"IDAT":
            idat += body
        elif kind != b"IEND":
            chunks.append((kind, body))
        i += 12 + n
    w, _, depth, ctype = struct.unpack(">IIBB", chunks[0][1][:10])
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    stride = 1 + (w * channels * depth + 7) // 8
    rows = zlib.decompress(idat)[: H * stride]
    chunks[0] = (b"IHDR", struct.pack(">II", w, H) + chunks[0][1][8:])

    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))

    out = data[:8] + b"".join(chunk(k, b) for k, b in chunks)
    out += chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(out)


_band = None


def chrome_band(binary):
    global _band
    if _band is None:
        page = "data:text/html,<script>document.title=innerHeight</script>"
        dom = chrome(binary, page, 400, 1000)
        m = re.search(r"<title>(\d+)</title>", dom)
        _band = 1000 - int(m.group(1)) if m else 0
    return _band


def headline_for(shot, locale):
    """headline is a string, or {locale: text} for localized sets."""
    h = shot["headline"]
    if isinstance(h, str):
        return h
    if locale:
        if locale not in h:
            sys.exit(f"{shot['slug']}: no headline for locale '{locale}'")
        return h[locale]
    return next(iter(h.values()))


def page_for(spec, shot, W, H, locale=None):
    scale = W / 1290
    px = lambda n: round(n * scale)
    t, pal = spec.get("type", {}), spec["palette"]
    layout = shot.get("layout", "poster")
    if layout not in LAYOUTS:
        sys.exit(f"{shot['slug']}: layout must be one of {LAYOUTS}")
    src = "file://" + os.path.abspath(shot["screenshot"])
    dev_w = px(1100)  # wide enough that the device always bleeds off the bottom

    if layout == "bleed":
        stage = f'<div class="bleed"><img src="{html.escape(src)}"></div>'
    else:
        stage = (
            f'<div class="device"><div class="screen"><img src="{html.escape(src)}">'
            f'<div class="island"></div></div></div>'
        )
    crop = shot.get("breakout") if layout == "breakout" else None
    if layout == "breakout":
        if not crop:
            sys.exit(f"{shot['slug']}: breakout layout needs breakout {{x,y,w,h}} in screenshot pixels")
        stage += '<div class="panel"></div>'

    return PAGE.format(
        W=W, H=H, pad=px(t.get("pad", 96)),
        ground=shot.get("ground", pal["ground"]), ink=shot.get("ink", pal["ink"]),
        accent=pal.get("accent", pal["ink"]),
        family=t.get("family", "-apple-system, 'SF Pro Display', system-ui, sans-serif"),
        font_css=t.get("css", ""),
        weight=t.get("weight", 800), tracking=t.get("tracking", "-0.035em"),
        size=px(shot.get("size", t.get("size", 150))),
        top=px(t.get("top", 190)),
        align=t.get("align", "left"),
        transform="uppercase" if t.get("case") == "upper" else "none",
        headline=html.escape(headline_for(shot, locale)),
        lang=locale or spec.get("locale", "en"),
        stage=stage, gap=px(t.get("gap", 88)),
        dev_w=dev_w, bezel=px(16), dev_r=px(168), rim=px(4), scr_r=px(152),
        isl_top=px(34), isl_w=px(300), isl_h=px(88),
        bleed_w=px(shot.get("bleed_width", 1180)),
        bleed_x=px(shot.get("bleed_x", 220)),
        panel_w=px(shot.get("panel_width", 1180)), panel_r=px(36),
        sh_y=px(30), sh_b=px(90),
        crop=json.dumps(crop) if crop else "null",
    )


def gate(spec, shot, rep, W, locale=None):
    """Return (fails, warns). Mirrors the house rules in SKILL.md."""
    fails, warns = [], []
    text = headline_for(shot, locale)
    real_proof = [p.lower() for p in spec.get("proof", [])]
    if not rep:
        return ["page did not report (Chrome failed or timed out)"], warns
    if not rep["imgLoaded"]:
        fails.append(f"screenshot not loaded: {shot['screenshot']}")
    if rep["lines"] > 2:
        fails.append(f"headline is {rep['lines']} lines (max 2): cut words, then lower size")
    if min(rep["left"], rep["right"]) < round(W * 0.05):
        fails.append("headline touches the edge")
    if rep["contrast"] < 4.5:
        fails.append(f"ink/ground contrast {rep['contrast']} < 4.5")
    if not rep["fontLoaded"]:
        fails.append(f"font '{rep['font']}' did not load (falling back)")
    if EMOJI.search(text):
        fails.append("emoji in headline")
    m = PROOF.search(text)
    if m and not any(m.group(0).lower() in p for p in real_proof):
        fails.append(f"proof claim '{m.group(0)}' not listed in set.json proof[]")
    # CJK and full-width characters set about twice as wide as Latin ones.
    width = sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)
    if width > 40:
        warns.append(f"headline {width} width units (aim ≤ 32; a CJK character counts 2)")
    if rep["headlineBottom"] > W * 0.62:
        warns.append("headline block is tall; device starts low")
    return fails, warns


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--only", type=int, help="render one shot (1-based)")
    ap.add_argument("--locale", help="render this locale of {locale: text} headlines (output: final/<locale>/)")
    ap.add_argument("--out", help="output dir (default: <spec dir>/final)")
    a = ap.parse_args()

    spec_dir = os.path.dirname(os.path.abspath(a.spec))
    with open(a.spec) as f:
        spec = json.load(f)
    # The storyboard stop in SKILL.md, enforced: no image before the user approves the plan.
    if spec.get("storyboard_approved") is not True:
        sys.exit("Storyboard not approved: show the user the storyboard (SKILL.md step 5) and set "
                 '"storyboard_approved": true in set.json only after they say yes.')
    os.chdir(spec_dir)  # screenshot paths in set.json are relative to it
    W, H = SIZES[str(spec.get("size", "6.9"))]
    out_dir = os.path.abspath(a.out or os.path.join("final", a.locale or ""))
    os.makedirs(out_dir, exist_ok=True)
    binary = find_chrome()

    shots = spec["shots"]
    todo = [a.only - 1] if a.only else range(len(shots))
    total_fail = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i in todo:
            shot = shots[i]
            page = os.path.join(tmp, f"{i}.html")
            with open(page, "w") as f:
                f.write(page_for(spec, shot, W, H, a.locale))
            png = os.path.join(out_dir, f"{i + 1:02d}-{shot['slug']}.png")
            chrome(binary, "file://" + page, W, H, screenshot=png)
            m = re.search(r'data-report="([^"]*)"', chrome(binary, "file://" + page, W, H))
            rep = json.loads(html.unescape(m.group(1))) if m else None
            fails, warns = gate(spec, shot, rep, W, a.locale)
            total_fail += len(fails)
            status = "FAIL" if fails else "ok"
            print(f"[{status}] {os.path.relpath(png)}  {W}x{H}" + (f"  lines={rep['lines']} contrast={rep['contrast']}" if rep else ""))
            for x in fails:
                print(f"   FAIL {x}")
            for x in warns:
                print(f"   WARN {x}")

        # Thumbnail sheet: the set as it appears in search results, on light and dark.
        finals = sorted(f for f in os.listdir(out_dir) if re.match(r"\d\d-.*\.png$", f))
        if finals:
            tw = 300
            sw = 48 * 2 + len(finals) * tw + (len(finals) - 1) * 28
            sh = 2 * (round(tw * H / W) + 80)
            imgs = "".join(f'<img src="file://{os.path.join(out_dir, f)}">' for f in finals)
            sheet = os.path.join(tmp, "sheet.html")
            with open(sheet, "w") as f:
                f.write(SHEET.format(W=sw, H=sh, tw=tw, imgs=imgs))
            sheet_png = os.path.join(out_dir, "..", f"sheet-{a.locale}.png") if a.locale else os.path.join(spec_dir, "sheet.png")
            chrome(binary, "file://" + sheet, sw, sh, screenshot=sheet_png)
            print(f"sheet: {os.path.relpath(sheet_png)}")

    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
