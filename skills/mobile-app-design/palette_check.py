#!/usr/bin/env python3
"""Flag overused default-looking colours in theme files (see visual-identity.md).

    python3 palette_check.py ios/Sources/Design/Theme.swift android/.../Color.kt
    python3 palette_check.py --selfcheck

Finds hex colours (#RRGGBB, 0xRRGGBB, 0xFFRRGGBB, Color(0xFF...)) and reports two families:
  cream    near-white page colours with a warm yellow-red cast
  clay     terracotta / burnt-orange / coral accents
Exit 0 = clean, 1 = something flagged, 2 = no file read. Stdlib only.
"""
import colorsys
import re
import sys

HEX = re.compile(r"(?:#|0x(?:FF)?)([0-9A-Fa-f]{6})\b")


def family(hex6):
    r, g, b = (int(hex6[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    hue = h * 360
    if l >= 0.88 and 20 <= hue <= 55 and 0.15 <= s <= 0.75 and r - b >= 4 / 255:
        return "cream"
    if 4 <= hue <= 28 and s >= 0.35 and 0.42 <= l <= 0.72:
        return "clay"
    return None


def scan(path):
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for n, line in enumerate(f, 1):
            for m in HEX.finditer(line):
                fam = family(m.group(1))
                if fam:
                    out.append(f"{path}:{n}: {fam} #{m.group(1).upper()}  {line.strip()[:80]}")
    return out


def selfcheck():
    for c in ("FAF9F5", "F0EEE6", "FBF6EE", "F5F0E8", "FBF7F2"):
        assert family(c) == "cream", c
    for c in ("D97757", "CC785C", "C96442", "E5674F"):
        assert family(c) == "clay", c
    for c in ("FFFFFF", "F4F6F8", "F2F2F2", "2F5BFF", "E3001B", "0A8F5B", "FFD400", "111111", "FCEBB6", "FFF1C2"):
        assert family(c) is None, c
    print("palette_check selfcheck ok")


def main(argv):
    if argv == ["--selfcheck"]:
        selfcheck()
        return 0
    if not argv:
        print(__doc__)
        return 2
    hits, read = [], 0
    for p in argv:
        try:
            hits += scan(p)
            read += 1
        except OSError as e:
            print(f"skip {p}: {e}", file=sys.stderr)
    if not read:
        return 2
    print("\n".join(hits) if hits else "OK: no overused default colours")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
