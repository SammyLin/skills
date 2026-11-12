#!/usr/bin/env python3
"""
Render an App Store screenshot set from screenshots/set.json.

Each shot is laid out in HTML/CSS and photographed by headless Chrome at the
exact App Store Connect size, so there is no crop/resize step and the app's
own pixels are never redrawn by a model. The same page measures itself
(headline lines, edges, contrast, fonts) and the result is the gate.

  python3 render.py screenshots/set.json            # all shots + sheet
  python3 render.py screenshots/set.json --only 2   # one shot (1-based)
  python3 render.py screenshots/set.json --style shopping-checklist,notification-reminder
                                                    # same set in named styles (styles/*.json),
                                                    # one folder per style + a comparison sheet

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
STYLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles")
PROPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "props")
MOTIFS = ("discount", "alert", "checklist", "compare")

# Feature motifs, 100x100. Filled: accent shape with white details. Outline: accent strokes.
MOTIF_SVG = {
    "discount": ('<path d="M34 10H90V90H34L8 50Z"/>', '<circle cx="34" cy="50" r="8" class="d"/>'),
    "alert": ('<path d="M50 8C31 8 22 24 22 42V62L12 76H88L78 62V42C78 24 69 8 50 8Z"/>',
              '<circle cx="50" cy="88" r="8"/>'),
    "checklist": ('<rect x="10" y="10" width="80" height="80" rx="16"/>',
                  '<polyline points="28,52 44,68 74,34" class="d"/>'),
    "compare": ('<rect x="10" y="40" width="32" height="50" rx="6"/><rect x="58" y="10" width="32" height="80" rx="6"/>', ''),
}

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
  .canvas {{ position: relative; width: var(--W); height: var(--H); overflow: hidden; background: {bg_css}; }}
  .circle {{ position: absolute; border-radius: 50%; }}
  .prop {{ position: absolute; display: block; }}
  .prop svg {{ display: block; width: 100%; height: auto; overflow: visible; }}
  .swash {{ position: absolute; left: var(--pad); height: {sw_h}px; overflow: visible; transform-origin: left center; }}
  .underline {{ position: absolute; left: var(--pad); height: {ul_h}px; width: {ul_w}px;
               border-radius: {ul_h}px; background: var(--accent); }}
  .motif {{ position: absolute; right: var(--pad); top: {motif_top}px; width: {motif_w}px; height: {motif_w}px; }}
  .motif.filled * {{ fill: var(--accent); stroke: none; }}
  .motif.filled .d {{ fill: #fff; stroke: #fff; stroke-width: 9; stroke-linecap: round; stroke-linejoin: round; }}
  .motif.filled polyline.d {{ fill: none; }}
  .motif.outline * {{ fill: none; stroke: var(--accent); stroke-width: 8; stroke-linecap: round; stroke-linejoin: round; }}
  .shot {{ position: absolute; left: 50%; transform: translateX(-50%); width: {shot_w}px;
          border-radius: {shot_r}px; box-shadow: 0 {shot_sy}px {shot_sb}px rgba(15,26,45,{shot_a}); }}
  .shot .screen {{ position: relative; border-radius: {shot_r}px; overflow: hidden; }}
  .shot img {{ display: block; width: 100%; }}
  h1 {{
    position: absolute; left: var(--pad); right: {h1_right}px; top: {top}px;
    font-family: var(--family); font-weight: var(--weight); font-size: var(--size);
    line-height: 0.98; letter-spacing: var(--tracking); color: var(--ink);
    text-align: {align}; text-transform: {transform}; text-wrap: balance;
    transform: rotate({h_rot}deg); transform-origin: left bottom;
    line-break: strict;
  }}
  /* Break CJK headlines at phrase/word boundaries, not mid-word. */
  h1:lang(ja) {{ word-break: auto-phrase; }}
  h1:lang(ko) {{ word-break: keep-all; }}
  /* Chinese: break after punctuation (，、) first; only a line that still overflows breaks mid-phrase. */
  h1:lang(zh) {{ word-break: keep-all; overflow-wrap: anywhere; }}
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
  {deco}
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
  let below = hb.bottom;
  const ul = document.querySelector('.underline');
  if (ul) {{ ul.style.top = Math.round(hb.bottom + {ul_gap}) + 'px'; below = ul.getBoundingClientRect().bottom; }}
  const sw = document.querySelector('.swash');
  if (sw) {{
    const r0 = document.createRange(); r0.selectNodeContents(h1);
    const tw0 = r0.getBoundingClientRect().width;
    sw.style.width = Math.round(Math.min(tw0 * 1.02, W - 2 * PAD)) + 'px';
    sw.style.top = Math.round(hb.bottom + {ul_gap}) + 'px';
    sw.style.transform = 'rotate({h_rot}deg)';
    below = sw.getBoundingClientRect().bottom;
  }}
  const holder = document.querySelector('.device, .bleed, .shot');
  holder.style.top = Math.round(below + {gap}) + 'px';
  const d = holder.getBoundingClientRect();
  if (holder.classList.contains('shot') || holder.classList.contains('anchored')) {{
    // Framed-less screen keeps its width (style shot_width); a short headline anchors it to the
    // bottom so it bleeds by a fixed amount instead of floating.
    const bleed = Math.round(H * {bleed_frac});  // per shot: "bleed" sinks the screen further off the bottom
    if (d.bottom < H + bleed) holder.style.top = Math.round(H + bleed - d.height) + 'px';
  }} else if (d.bottom < H + 40) {{
    // A short headline lifts the device; grow it so it still bleeds off the bottom edge.
    holder.style.width = (d.width * (H + 40 - d.top) / d.height) + 'px';
  }}

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
    lines: Math.round(h1.offsetHeight / lh),  // layout height: a rotated headline's box is taller
    left: Math.round(tb.left), right: Math.round(W - tb.right),
    headlineBottom: Math.round(hb.bottom),
    shotTop: Math.round(holder.getBoundingClientRect().top),
    overlap: holder.getBoundingClientRect().top < below,
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


def load_style(name):
    """A named style from styles/<name>.json, or None."""
    if not name:
        return None
    if isinstance(name, dict):
        return name
    path = os.path.join(STYLES_DIR, f"{name}.json")
    if not os.path.exists(path):
        have = ", ".join(sorted(f[:-5] for f in os.listdir(STYLES_DIR) if f.endswith(".json")))
        sys.exit(f"unknown style '{name}' (have: {have})")
    with open(path) as f:
        return json.load(f)


def page_for(spec, shot, W, H, locale=None, style=None):
    scale = W / 1290
    px = lambda n: round(n * scale)
    t = spec.get("type", {})
    style = style or load_style(shot.get("style") or spec.get("style"))
    pal = dict(spec.get("palette", {}))
    bg = None
    if style:  # a style brings its own colours; set.json palette is ignored for it
        bg = style["background"]
        pal = {"ground": bg[0] if isinstance(bg, list) else bg, "ink": style["ink"], "accent": style["accent"]}
    layout = shot.get("layout", "poster")
    if layout not in LAYOUTS:
        sys.exit(f"{shot['slug']}: layout must be one of {LAYOUTS}")
    src = "file://" + os.path.abspath(shot["screenshot"])
    dev_w = px(1100)  # wide enough that the device always bleeds off the bottom
    frame = shot.get("frame") or (style or {}).get("frame") or spec.get("frame", "device")

    if layout == "bleed":
        stage = f'<div class="bleed"><img src="{html.escape(src)}"></div>'
    elif style and style.get("device_width"):  # fixed-width device anchored to the bottom
        dev_w = round(W * style["device_width"])
        stage = (
            f'<div class="device anchored"><div class="screen"><img src="{html.escape(src)}">'
            f'<div class="island"></div></div></div>'
        )
    elif frame == "screen":  # no bezel: the screenshot itself, rounded, soft shadow
        stage = f'<div class="shot"><div class="screen"><img src="{html.escape(src)}"></div></div>'
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

    # Decoration comes only from a style file: background, circles, underline, feature motif.
    deco, feature = "", shot.get("feature")
    for c in (style or {}).get("circles", []):
        r = c["r"] * W
        deco += (f'<div class="circle" style="left:{c["cx"] * W - r:.0f}px;top:{c["cy"] * H - r:.0f}px;'
                 f'width:{2 * r:.0f}px;height:{2 * r:.0f}px;background:{c["color"]}"></div>')
    if style and style.get("underline") is True:
        deco += '<div class="underline"></div>'
    # Props: illustrations from props/*.svg placed in canvas fractions, behind the screenshot.
    for pr in (style or {}).get("props", []):
        if pr.get("slot") == "accent" and shot.get("prop"):  # per-shot illustration in the style's accent slot
            pr = {**pr, "src": shot["prop"]}
        if pr.get("slot") == "accent" and shot.get("prop") == "none":
            continue
        path = os.path.join(PROPS_DIR, pr["src"] + ".svg")
        if not os.path.exists(path):
            sys.exit(f"style prop '{pr['src']}' not found in props/")
        with open(path) as f:
            svg = re.sub(r"<\?xml[^>]*>", "", f.read())
        deco += (f'<div class="prop" style="left:{pr["x"] * W:.0f}px;top:{pr["y"] * H:.0f}px;'
                 f'width:{pr["w"] * W:.0f}px;transform:rotate({pr.get("rotate", 0)}deg);'
                 f'opacity:{pr.get("opacity", 1)};color:{pr.get("color", "currentColor")}">{svg}</div>')
    if style and style.get("underline") == "swash":
        c = style.get("underline_color", pal["accent"])
        deco += (f'<svg class="swash" viewBox="0 0 400 30" preserveAspectRatio="none">'
                 f'<path d="M4 22C110 8 260 6 396 14" stroke="{c}" stroke-width="12" '
                 f'stroke-linecap="round" fill="none"/></svg>')
    motif_w = px(150)
    has_motif = bool(style and style.get("motif") and feature in MOTIFS)
    if feature and feature not in MOTIFS + ("none",):
        sys.exit(f"{shot['slug']}: feature must be one of {MOTIFS + ('none',)}")
    if has_motif:
        a, b = MOTIF_SVG[feature]
        deco += f'<svg class="motif {style["motif"]}" viewBox="0 0 100 100">{a}{b}</svg>'
    size = px(shot.get("size", (style or {}).get("size", t.get("size", 150))))
    top = px((style or {}).get("top", t.get("top", 190)))
    shot_w = round(W * (style or {}).get("shot_width", 0.84))
    bg_css = (f"linear-gradient(180deg, {bg[0]}, {bg[1]})" if isinstance(bg, list) else pal["ground"])

    return PAGE.format(
        W=W, H=H, pad=px(t.get("pad", 96)),
        bg_css=bg_css, deco=deco,
        h1_right=px(t.get("pad", 96)) + (motif_w + px(40) if has_motif else 0),
        motif_w=motif_w, motif_top=top + round((size * 0.98 - motif_w) / 2),
        ul_w=px(300), ul_h=px(14), ul_gap=px(28), sw_h=px(34),
        h_rot=(style or {}).get("headline_rotate", 0),
        bleed_frac=shot.get("bleed", 0.035),
        shot_w=shot_w, shot_r=round(shot_w * 0.085), shot_sy=px(24), shot_sb=px(70),
        shot_a=(style or {}).get("shadow", 0.10),
        ground=shot.get("ground", pal["ground"]), ink=shot.get("ink", pal["ink"]),
        accent=pal.get("accent", pal["ink"]),
        family=t.get("family", "-apple-system, 'SF Pro Display', system-ui, sans-serif"),
        font_css=t.get("css", ""),
        weight=(style or {}).get("weight", t.get("weight", 800)), tracking=t.get("tracking", "-0.035em"),
        size=size,
        top=top,
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
    if rep.get("overlap"):
        fails.append("screenshot overlaps the headline block")
    if rep["headlineBottom"] > W * 0.62:
        warns.append("headline block is tall; device starts low")
    return fails, warns


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--only", type=int, help="render one shot (1-based)")
    ap.add_argument("--locale", help="render this locale of {locale: text} headlines (output: final/<locale>/)")
    ap.add_argument("--out", help="output dir (default: <spec dir>/final)")
    ap.add_argument("--style", help="comma list of styles from styles/*.json ('both' = shopping-checklist,"
                                    "notification-reminder); each renders to <out>/<style>/")
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
    base_out = os.path.abspath(a.out or os.path.join("final", a.locale or ""))
    binary = find_chrome()
    names = (a.style or "").replace("both", "shopping-checklist,notification-reminder")
    variants = [(n, load_style(n)) for n in names.split(",") if n] or [(None, None)]
    total_fail = 0
    for style_name, style in variants:
        out_dir = os.path.join(base_out, style_name) if style_name else base_out
        os.makedirs(out_dir, exist_ok=True)
        total_fail += render_set(spec, a, W, H, binary, out_dir, spec_dir, style, style_name)
    if len(variants) > 1:
        print("compare: " + ", ".join(os.path.relpath(os.path.join(base_out, n, "sheet.png")) for n, _ in variants))
    sys.exit(1 if total_fail else 0)


def render_set(spec, a, W, H, binary, out_dir, spec_dir, style, style_name):

    shots = spec["shots"]
    todo = [a.only - 1] if a.only else range(len(shots))
    total_fail, layout = 0, []
    with tempfile.TemporaryDirectory() as tmp:
        for i in todo:
            shot = shots[i]
            page = os.path.join(tmp, f"{i}.html")
            with open(page, "w") as f:
                f.write(page_for(spec, shot, W, H, a.locale, style))
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
            layout.append({"png": os.path.relpath(png, spec_dir), "slug": shot["slug"],
                           "headline": headline_for(shot, a.locale), "screenshot": shot["screenshot"],
                           "layout": shot.get("layout", "poster"), "feature": shot.get("feature"),
                           "style": style_name or spec.get("style"), "size": [W, H], "measured": rep,
                           "fails": fails, "warns": warns})

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
            if style_name:
                sheet_png = os.path.join(out_dir, "sheet.png")
            else:
                sheet_png = os.path.join(out_dir, "..", f"sheet-{a.locale}.png") if a.locale else os.path.join(spec_dir, "sheet.png")
            chrome(binary, "file://" + sheet, sw, sh, screenshot=sheet_png)
            print(f"sheet: {os.path.relpath(sheet_png)}")

    # What was rendered and measured, per shot: the record to review and edit set.json from.
    with open(os.path.join(out_dir, "layout.json"), "w") as f:
        json.dump(layout, f, ensure_ascii=False, indent=2)
    return total_fail


if __name__ == "__main__":
    main()
