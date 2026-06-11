"""Lerp Gothic — a textura blackletter built almost entirely out of lerp.

Every glyph is a skeleton of strokes. Straight strokes are sampled with
lerp(a, b, t); curved strokes use De Casteljau, i.e. lerps of lerps. A
broad-nib pen (a short line segment at a fixed angle) is stamped at each
sample point, which is what gives vertical stems their weight and
diagonal joins their hairlines — same mechanics as a real calligraphy nib.

Pipeline per glyph: stamp nib -> Pillow bitmap -> potrace -> cu2qu -> TTF.

Usage: uv run python scripts/lerp_gothic.py
"""

import math
from pathlib import Path

import numpy as np
import potrace
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from PIL import Image, ImageDraw

# ── design space ────────────────────────────────────────────────────────────
UPM = 1000
XH = 520            # x-height
ASC = 750           # ascender
DSC = -250          # descender
Y_MAX, Y_MIN = 880, -380   # render canvas range (font units)
MX = 120            # left render margin

NIB_ANGLE = math.radians(40)
NIB_LEN = 130       # broad edge length
NIB_THICK = 20      # ink thickness of the edge
STEP = 3            # lerp sampling step along strokes

X1, X2, X3 = 90, 320, 550   # stem positions
RSB = 60            # right side bearing


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def decasteljau(pts, t):
    while len(pts) > 1:
        pts = [lerp(p, q, t) for p, q in zip(pts, pts[1:])]
    return pts[0]


# ── strokes: polylines and Bézier curves, all sampled via lerp ──────────────
def sample(stroke):
    if stroke[0] == "C":  # ("C", p0, p1, ..., pn) Bézier via De Casteljau
        pts = stroke[1:]
        approx = sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))
        n = max(2, int(approx / STEP))
        return [decasteljau(list(pts), i / n) for i in range(n + 1)]
    out = []
    for p, q in zip(stroke, stroke[1:]):
        n = max(1, int(math.dist(p, q) / STEP))
        out += [lerp(p, q, i / n) for i in range(n + 1)]
    return out


# ── skeleton helpers ────────────────────────────────────────────────────────
def stem(x, ytop, ybot):
    return [(x, ytop), (x, ybot)]


def head(x, y):  # diamond entry stroke at top of a stem
    return [(x - 60, y + 55), (x + 20, y - 25)]


def foot(x, y):  # diamond exit stroke at bottom of a stem
    return [(x - 20, y + 25), (x + 60, y - 55)]


def join(xl, yl, xr, yr):  # diagonal connector (thins out near nib angle)
    return [(xl, yl), (xr, yr)]


def dot(x, y):  # diamond dot (i, j, period)
    return [(x - 38, y + 38), (x + 38, y - 38)]


def two_stem(ytopl=XH, ytopr=XH):
    """n-like frame: two stems w/ entry+exit, joined at the top."""
    return [
        stem(X1, ytopl, 0), head(X1, ytopl), foot(X1, 0),
        stem(X2, ytopr - 60, 0), join(X1 + 10, ytopl - 15, X2 + 15, ytopr - 35),
        foot(X2, 0),
    ]


def bowl(ybot_join=65):
    """o-like closed counter between X1 and X2."""
    return [
        stem(X1, XH - 65, ybot_join), head(X1, XH - 65),
        stem(X2, XH - 10, ybot_join + 45),
        join(X1 + 10, XH - 80, X2 + 15, XH - 25),
        join(X1 - 10, ybot_join - 10, X2 + 10, ybot_join + 35),
        foot(X2, ybot_join + 45),
    ]


# ── glyph skeletons ─────────────────────────────────────────────────────────
GLYPHS = {
    "a": bowl() + [stem(X2, XH + 30, 0), head(X2, XH + 30), foot(X2, 0)],
    "b": [stem(X1, ASC, 0), head(X1, ASC),
          join(X1 + 10, XH - 30, X2 + 10, XH - 80), stem(X2, XH - 80, 90),
          join(X1 - 5, 75, X2 + 10, 130), foot(X2, 90)],
    "c": [stem(X1, XH - 65, 65), head(X1, XH - 65), foot(X1, 65),
          join(X1 + 10, XH - 80, X2 + 20, XH - 25), dot(X2 + 10, XH - 70),
          join(X1 + 30, 25, X2 + 30, 80)],
    "d": [stem(X1, XH - 65, 65), head(X1, XH - 65),
          join(X1 + 10, XH - 80, X2 + 15, XH - 25),
          join(X1 - 10, 55, X2 + 10, 100),
          stem(X2, XH + 40, 100), ["C", (X2, XH + 40), (X2 - 30, ASC - 60), (X1 + 60, ASC - 80)],
          foot(X2, 100)],
    "e": [stem(X1, XH - 65, 65), head(X1, XH - 65), foot(X1, 65),
          join(X1 + 10, XH - 80, X2 + 20, XH - 25),
          join(X1 + 20, 250, X2 + 25, 320),
          join(X1 + 30, 25, X2 + 30, 80)],
    "f": [stem(X1 + 40, ASC - 40, 0), foot(X1 + 40, 0),
          ["C", (X1 + 40, ASC - 40), (X1 + 70, ASC + 30), (X2 - 20, ASC - 20)],
          [(X1 - 60, 505), (X2 - 30, 505)]],
    "g": bowl(120) + [stem(X2, XH + 30, -120), head(X2, XH + 30),
                      ["C", (X2, -120), (X2 - 40, -250), (X1 + 30, -210)]],
    "h": [stem(X1, ASC, 0), head(X1, ASC), foot(X1, 0),
          join(X1 + 10, XH - 15, X2 + 15, XH - 95),
          stem(X2, XH - 120, -90), foot(X2, -90)],
    "i": [stem(X1, XH, 0), head(X1, XH), foot(X1, 0), dot(X1, 650)],
    "j": [stem(X1, XH, -140), head(X1, XH), dot(X1, 650),
          ["C", (X1, -140), (X1 - 30, -260), (X1 - 130, -210)]],
    "k": [stem(X1, ASC, 0), head(X1, ASC), foot(X1, 0),
          join(X1 + 10, 320, X2 - 20, 490), dot(X2 - 10, 470),
          [(X1 + 70, 300), (X2 + 10, 60)], foot(X2 + 10, 60)],
    "l": [stem(X1, ASC, 0), head(X1, ASC), foot(X1, 0)],
    "m": two_stem() + [stem(X3, XH - 60, 0), join(X2 + 10, XH - 50, X3 + 15, XH - 95),
                       foot(X3, 0)],
    "n": two_stem(),
    "o": bowl(),
    "p": [stem(X1, XH, DSC + 30), head(X1, XH), foot(X1, DSC + 30),
          join(X1 + 10, XH - 15, X2 + 15, XH - 60), stem(X2, XH - 60, 90),
          join(X1 - 5, 60, X2 + 10, 130), foot(X2, 90)],
    "q": bowl(110) + [stem(X2, XH + 20, DSC + 30), foot(X2, DSC + 30)],
    "r": [stem(X1, XH, 0), head(X1, XH), foot(X1, 0),
          join(X1 + 10, XH - 15, X2 - 10, XH - 60), dot(X2 - 10, XH - 110)],
    "s": [[(X1 + 50, 505), (X2 - 10, 505)], dot(X2 + 10, XH - 30),
          [(X1 + 30, 505), (X1 + 30, 300)],
          [(X1 + 30, 300), (X2 - 10, 300)],
          [(X2 - 10, 300), (X2 - 10, 80)],
          [(X2 - 30, 80), (X1 + 10, 80)], dot(X1 - 5, 110)],
    "t": [stem(X1 + 40, 620, 0), foot(X1 + 40, 0),
          [(X1 - 60, 505), (X2 - 30, 505)]],
    "u": [stem(X1, XH, 65), head(X1, XH),
          join(X1 - 10, 55, X2 + 10, 100),
          stem(X2, XH, 100), head(X2, XH), foot(X2, 100)],
    "v": [stem(X1, XH, 90), head(X1, XH),
          join(X1 - 10, 80, X2 - 40, 30),
          ["C", (X2 - 40, 30), (X2 + 60, 120), (X2 + 20, XH - 60)],
          dot(X2 + 10, XH - 30)],
    "w": [stem(X1, XH, 90), head(X1, XH),
          join(X1 - 10, 80, X2 - 60, 30),
          stem(X2 - 30, XH, 60), head(X2 - 30, XH),
          join(X2 - 40, 50, X3 - 80, 30),
          ["C", (X3 - 80, 30), (X3 + 20, 120), (X3 - 20, XH - 60)],
          dot(X3 - 30, XH - 30)],
    "x": [[(X1 - 20, XH - 30), (X2 + 20, 50)], head(X1 - 20, XH - 30), foot(X2 + 20, 50),
          [(X2 + 20, XH - 30), (X1 - 20, 50)]],
    "y": [stem(X1, XH, 65), head(X1, XH),
          join(X1 - 10, 55, X2 + 10, 100),
          stem(X2, XH, -140), head(X2, XH),
          ["C", (X2, -140), (X2 - 30, -260), (X2 - 130, -210)]],
    "z": [[(X1 - 30, 505), (X2 + 10, 505)],
          [(X2 + 10, 505), (X1, 60)],
          [(X1 - 30, 60), (X2 + 20, 60)], dot(X2 + 30, 90)],
    "period": [dot(X1, 50)],
}

ADV_OVERRIDE = {"period": 240}


# ── rasterize: stamp the nib along lerped samples ───────────────────────────
def nib_corners(cx, cy):
    dx, dy = math.cos(NIB_ANGLE), math.sin(NIB_ANGLE)
    px, py = -dy, dx
    hl, ht = NIB_LEN / 2, NIB_THICK / 2
    return [
        (cx + dx * hl + px * ht, cy + dy * hl + py * ht),
        (cx + dx * hl - px * ht, cy + dy * hl - py * ht),
        (cx - dx * hl - px * ht, cy - dy * hl - py * ht),
        (cx - dx * hl + px * ht, cy - dy * hl + py * ht),
    ]


def render(strokes):
    w = int(max(x for s in strokes for x, _ in sample(s)) + MX + 150)
    img = Image.new("L", (w, Y_MAX - Y_MIN), 0)
    draw = ImageDraw.Draw(img)
    for stroke in strokes:
        for cx, cy in sample(stroke):
            poly = [(x + MX, Y_MAX - y) for x, y in nib_corners(cx, cy)]
            draw.polygon(poly, fill=255)
    return img


# ── trace: bitmap -> cubic Béziers -> quadratic TTF contours ────────────────
def pt(p):
    return (p.x, p.y) if hasattr(p, "x") else (p[0], p[1])


def trace_to_glyph(img):
    # NOTE: potracer inverts the bitmap internally (image convention: dark =
    # ink), so ink pixels must be False going in. Our render is white-on-black.
    data = np.asarray(img) < 128
    path = potrace.Bitmap(data).trace(turdsize=10, alphamax=1.0, opttolerance=0.3)
    tt_pen = TTGlyphPen(None)
    # NOTE: y-flip from image space inverts potrace's winding; TrueType
    # non-zero filling needs it reversed back or glyphs render inverted.
    pen = Cu2QuPen(tt_pen, max_err=2.0, reverse_direction=True)

    def to_font(p):
        x, y = pt(p)
        return (x - MX, Y_MAX - y)

    for curve in path:
        pen.moveTo(to_font(curve.start_point))
        for seg in curve.segments:
            if seg.is_corner:
                pen.lineTo(to_font(seg.c))
                pen.lineTo(to_font(seg.end_point))
            else:
                pen.curveTo(to_font(seg.c1), to_font(seg.c2), to_font(seg.end_point))
        pen.closePath()
    return tt_pen.glyph()


# ── build font ──────────────────────────────────────────────────────────────
def main():
    out_dir = Path(__file__).resolve().parent.parent / "assets" / "output"
    glyphs, metrics = {}, {}

    empty = TTGlyphPen(None).glyph()
    glyphs[".notdef"] = empty
    metrics[".notdef"] = (500, 0)
    glyphs["space"] = empty
    metrics["space"] = (260, 0)

    for name, strokes in GLYPHS.items():
        g = trace_to_glyph(render(strokes))
        g.recalcBounds(None)
        adv = ADV_OVERRIDE.get(name, g.xMax + RSB)
        glyphs[name] = g
        metrics[name] = (adv, g.xMin)

    order = [".notdef", "space"] + list(GLYPHS)
    cmap = {ord(" "): "space", ord("."): "period"}
    for ch in "abcdefghijklmnopqrstuvwxyz":
        cmap[ord(ch)] = ch
        cmap[ord(ch.upper())] = ch  # NOTE: unicase for now — caps render as lowercase

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASC + 100, descent=DSC - 50)
    fb.setupNameTable({
        "familyName": "Lerp Gothic",
        "styleName": "Regular",
        "psName": "LerpGothic-Regular",
        "version": "Version 0.1.0",
    })
    fb.setupOS2(sTypoAscender=ASC + 100, sTypoDescender=DSC - 50, sTypoLineGap=0,
                usWinAscent=Y_MAX, usWinDescent=-Y_MIN, sxHeight=XH)
    fb.setupPost()

    out_dir.mkdir(parents=True, exist_ok=True)
    ttf = out_dir / "LerpGothic-Regular.ttf"
    fb.save(str(ttf))
    print(f"built {ttf} ({len(order)} glyphs)")
    return ttf


def specimen(ttf, out_png):
    from PIL import ImageFont

    lines = [
        ("lerp gothic", 150),
        ("sphinx of black quartz judge my vow.", 90),
        ("the quick brown fox jumps over the lazy dog.", 64),
    ]
    img = Image.new("L", (2000, 700), 255)
    draw = ImageDraw.Draw(img)
    y = 40
    for text, size in lines:
        font = ImageFont.truetype(str(ttf), size)
        draw.text((50, y), text, font=font, fill=0)
        y += int(size * 1.6)
    img.save(out_png)
    print(f"specimen {out_png}")


if __name__ == "__main__":
    built = main()
    specimen(built, built.parent / "specimen.png")
