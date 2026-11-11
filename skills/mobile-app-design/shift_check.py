#!/usr/bin/env python3
"""Find layout shift between two screenshots of the same screen (loading vs loaded).

    python3 shift_check.py loading.png loaded.png [-o overlay.png] [--ignore-top 120]
    python3 shift_check.py --examples DIR     # draw the reference images and self-check

It finds the long straight edges (card tops and bottoms, search bar, segment control, photo
blocks) in each screenshot and pairs them up. An edge that sits at a different place in the other
shot, or exists in only one of them, is reported, and drawn on the overlay: red = loading only,
cyan = loaded only. Text and skeleton bars are too short to count, so a skeleton that differs from
the text it stands for is fine; a card, photo or control that moves is not.

Exit 0 = no shift, 1 = shift found, 2 = bad input. Needs Pillow.
Heuristic: it compares straight edges only. Use the same device, scroll offset and status bar
(`xcrun simctl status_bar booted override --time 9:41`), or pass --ignore-top.
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    sys.exit("shift_check.py needs Pillow: python3 -m pip install pillow")

WORK_WIDTH = 600   # analyse at this width; reports are converted back to the input's pixels
EDGE = 6           # min brightness step that counts as an edge (cards on a warm bg are subtle)
H_RUN = 0.55       # a horizontal edge must run this share of the width
V_RUN = 0.07       # a vertical edge must run this share of the height
TOL = 2            # px at WORK_WIDTH: closer than this is the same edge
MAX_MOVE = 60      # px at WORK_WIDTH: farther than this is a different edge, not a moved one


def edge_map(img):
    g = img.convert("L")
    w, h = g.size
    g = g.resize((WORK_WIDTH, round(h * WORK_WIDTH / w)), Image.LANCZOS)
    return g.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v >= EDGE else 0)


def long_runs(px, n_lines, n_along, get, min_run):
    """Positions (line indexes) holding an uninterrupted edge run of at least min_run."""
    found = []
    for i in range(n_lines):
        run = best = 0
        for j in range(n_along):
            run = run + 1 if get(px, i, j) else 0
            if run > best:
                best = run
        if best >= min_run:
            found.append(i)
    # Merge neighbouring rows into one edge (antialiasing makes edges 1-3 px thick).
    edges, group = [], []
    for i in found:
        if group and i - group[-1] > 1:
            edges.append(sum(group) / len(group))
            group = []
        group.append(i)
    if group:
        edges.append(sum(group) / len(group))
    return edges


def structure(img, ignore_top):
    e = edge_map(img)
    w, h = e.size
    px = e.load()
    top = round(ignore_top * WORK_WIDTH / img.size[0])
    rows = [y for y in long_runs(px, h, w, lambda p, y, x: p[x, y], int(w * H_RUN)) if y >= top]
    cols = long_runs(px, w, h, lambda p, x, y: y >= top and p[x, y], int(h * V_RUN))
    return e, rows, cols


def pair(a, b):
    """For each edge in a: (pos, nearest pos in b or None)."""
    out = []
    for p in a:
        near = min(b, key=lambda q: abs(q - p), default=None)
        if near is not None and abs(near - p) > MAX_MOVE:
            near = None
        out.append((p, near))
    return out


def compare(loading, loaded, ignore_top=0):
    if loading.size != loaded.size:
        raise ValueError(f"sizes differ: {loading.size} vs {loaded.size}; same device please")
    ea, rows_a, cols_a = structure(loading, ignore_top)
    eb, rows_b, cols_b = structure(loaded, ignore_top)
    k = loading.size[0] / WORK_WIDTH
    issues = []
    for axis, a, b in (("y", rows_a, rows_b), ("x", cols_a, cols_b)):
        kind = "horizontal edge" if axis == "y" else "vertical edge"
        for p, q in pair(a, b):
            if q is None:
                issues.append((axis, p, None, f"{kind} at {axis}={p * k:.0f} only while loading"))
            elif abs(q - p) > TOL:
                issues.append((axis, p, q, f"{kind} moved {axis}={p * k:.0f} -> {q * k:.0f} ({(q - p) * k:+.0f}px)"))
        for q, p in pair(b, a):
            if p is None:
                issues.append((axis, q, None, f"{kind} at {axis}={q * k:.0f} only once loaded (appears late)"))
    return issues, ea, eb


def overlay(loaded, ea, eb, issues, path):
    base = loaded.convert("L").resize(ea.size).point(lambda v: 150 + v * 105 // 255).convert("RGB")
    red = Image.new("RGB", ea.size, (230, 40, 60))
    cyan = Image.new("RGB", ea.size, (0, 170, 210))
    only_a = Image.eval(Image.composite(ea, Image.new("L", ea.size), Image.eval(eb, lambda v: 255 - v)), lambda v: v)
    base.paste(red, mask=only_a)
    base.paste(cyan, mask=Image.eval(Image.composite(eb, Image.new("L", eb.size), Image.eval(ea, lambda v: 255 - v)), lambda v: v))
    d = ImageDraw.Draw(base)
    w, h = base.size
    for axis, p, _q, _msg in issues:
        if axis == "y":
            d.line([(0, p), (14, p)], fill=(230, 40, 60), width=3)
            d.line([(w - 14, p), (w, p)], fill=(230, 40, 60), width=3)
        else:
            d.line([(p, 0), (p, 14)], fill=(230, 40, 60), width=3)
    base.save(path)


# ---------------------------------------------------------------- reference images

S = 2  # draw at @2x of a 390 x 844 pt phone
BG, SURFACE, INK, MUTED, SKEL, CORAL, CHIP, YELLOW = (
    "#FBF6EE", "#FFFFFF", "#2A211C", "#7A6C60", "#EDE3D6", "#E5674F", "#F4ECE1", "#FCEBB6")


def font(size):
    try:
        return ImageFont.load_default(size=size * S)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


def rr(d, box, r, fill):
    d.rounded_rectangle([v * S for v in box], radius=r * S, fill=fill)


def phone(state, bad=False):
    """state: 'loading' or 'loaded'. bad=True draws the usual mistakes into the loading state."""
    img = Image.new("RGB", (390 * S, 844 * S), BG)
    d = ImageDraw.Draw(img)
    d.text((20 * S, 60 * S), "Deals", font=font(30), fill=INK)
    d.text((20 * S, 100 * S), "Store prices - updated 07:00", font=font(13), fill=MUTED)
    controls = not (bad and state == "loading")  # bad: controls only appear after the data
    if controls:
        rr(d, (20, 128, 370, 174), 23, CHIP)
        d.text((40 * S, 142 * S), "Search all products", font=font(15), fill=MUTED)
        rr(d, (20, 186, 370, 230), 22, CHIP)
        rr(d, (22, 188, 194, 228), 20, CORAL if state == "loaded" else SKEL)
        if state == "loaded":
            d.text((48 * S, 199 * S), "In store  73", font=font(14), fill="white")
            d.text((222 * S, 199 * S), "Online  889", font=font(14), fill=INK)
    y = 246 if controls else 128
    card_h = 116 if not (bad and state == "loading") else 96  # bad: skeleton card shorter
    for i in range(5):
        top = y + i * (card_h + 12)
        rr(d, (20, top, 370, top + card_h), 20, SURFACE)
        photo = 92 if not (bad and state == "loading") else 72  # bad: smaller photo block
        if state == "loading":
            rr(d, (32, top + 12, 32 + photo, top + 12 + photo), 12, SKEL)
            for bx, bw, bh, by in ((136, 200, 14, 14), (136, 120, 14, 38), (136, 96, 22, 60), (136, 70, 24, 88 if not bad else 70)):
                rr(d, (bx, top + by, bx + bw, top + by + bh), min(bh / 2, 6) if bh < 24 else 12, SKEL)
        else:
            rr(d, (32, top + 12, 124, top + 104), 12, "#E9D9C6")
            d.text((136 * S, (top + 12) * S), ["Kirkland Mixed Nuts", "Corn Soup 6-pack", "Paper Towels 12 rolls", "Greek Yogurt 2kg", "Olive Oil 3L"][i], font=font(15), fill=INK)
            d.text((136 * S, (top + 34) * S), "1.13 kg", font=font(13), fill=MUTED)
            d.text((136 * S, (top + 56) * S), "$399", font=font(22), fill=INK)
            rr(d, (136, top + 86, 206, top + 110), 12, CORAL)
            d.text((144 * S, (top + 90) * S), "Save $80", font=font(12), fill="white")
            rr(d, (212, top + 86, 272, top + 110), 12, YELLOW)
            d.text((220 * S, (top + 90) * S), "4 days", font=font(12), fill="#8A5A00")
    rr(d, (0, 760, 390, 844), 0, SURFACE)  # tab bar, always there
    return img


def examples(out):
    os.makedirs(out, exist_ok=True)
    loaded = phone("loaded")
    good, bad = phone("loading"), phone("loading", bad=True)
    for name, im in (("loading-good", good), ("loading-bad", bad), ("loaded", loaded)):
        im.save(os.path.join(out, f"{name}.png"))
    results = {}
    for name, im in (("good", good), ("bad", bad)):
        issues, ea, eb = compare(im, loaded)
        overlay(loaded, ea, eb, issues, os.path.join(out, f"overlay-{name}.png"))
        results[name] = issues
    sheet = Image.new("RGB", (5 * 300 + 60, 690), "white")
    for i, name in enumerate(("loading-good", "loaded", "overlay-good", "loading-bad", "overlay-bad")):
        im = Image.open(os.path.join(out, f"{name}.png")).convert("RGB")
        im.thumbnail((300, 650))
        sheet.paste(im, (10 + i * 310, 30))
        ImageDraw.Draw(sheet).text((10 + i * 310, 8), name, fill="black", font=font(8))
    sheet.save(os.path.join(out, "reference.png"))
    assert not results["good"], f"matching skeleton should pass: {results['good']}"
    assert results["bad"], "mismatched skeleton should fail"
    print(f"examples in {out}: good pair 0 issues, bad pair {len(results['bad'])} issues")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("loading", nargs="?")
    ap.add_argument("loaded", nargs="?")
    ap.add_argument("-o", "--overlay", help="write the overlay PNG here")
    ap.add_argument("--ignore-top", type=int, default=0, help="input px to skip at the top (status bar)")
    ap.add_argument("--examples", metavar="DIR", help="draw reference images into DIR and self-check")
    a = ap.parse_args()
    if a.examples:
        examples(a.examples)
        return 0
    if not (a.loading and a.loaded):
        ap.print_usage()
        return 2
    try:
        loading, loaded = Image.open(a.loading), Image.open(a.loaded)
        issues, ea, eb = compare(loading, loaded, a.ignore_top)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if a.overlay:
        overlay(loaded, ea, eb, issues, a.overlay)
    for *_, msg in issues:
        print(msg)
    print("OK: no layout shift" if not issues else f"SHIFT: {len(issues)} edge(s) differ")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
