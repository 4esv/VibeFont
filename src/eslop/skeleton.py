"""Authoring DSL for glyph skeletons.

All coordinates are stroke CENTERLINES in the reference space: 1000 UPM,
reference stroke width 80, outline = centerline +- 40 in every direction
(square/round caps extend half a stroke past endpoints).

Vertical landmarks (centerline values; outline lands 40 beyond):

    ascender top      680   (outline  720)
    cap round top     672   (outline  712, overshoot)
    cap flat top      660   (outline  700)
    t-height          580   (outline  620)
    x round top       452   (outline  492, overshoot)
    x flat top        440   (outline  480)
    H crossbar        350
    baseline flat      40   (outline    0)
    baseline round     28   (outline  -12, overshoot)
    descender flat   -180   (outline -220)
    descender round  -192   (outline -232, overshoot)

Horizontal: leftmost centerline x = 40 (outline starts at 0). Spacing is
applied later from per-glyph side classes, so absolute x only sets shape.
"""

from __future__ import annotations

import math

# landmark constants for skeleton authors
ASC = 680
CAPR = 672    # cap-height round overshoot
CAP = 660     # cap-height flat
THIGH = 580   # ascender of t
XR = 452      # x-height round overshoot
XH = 440      # x-height flat
BASE = 40     # baseline flat
BASER = 28    # baseline round overshoot
DESC = -180   # descender flat
DESCR = -192  # descender round overshoot
LEFT = 40


# ------------------------------------------------------------------ strokes

def stroke(cmds, w=1.0, serif_start="auto", serif_end="auto"):
    """Wrap a command list with per-stroke options (width multiplier,
    serif behaviour at each open end: 'auto' | 'none')."""
    return {"cmds": list(cmds), "w": w,
            "serif_start": serif_start, "serif_end": serif_end}


def dot(x, y, r=52):
    """A filled circle (i/j dots, punctuation). r is in reference units and
    scales with the family stroke weight."""
    return {"dot": (x, y, r)}


# ----------------------------------------------------------------- builders

def line(x0, y0, x1, y1):
    return [("M", x0, y0), ("L", x1, y1)]


def stem(x, y0=BASE, y1=CAP):
    return line(x, y0, x, y1)


def bar(y, x0, x1):
    return line(x0, y, x1, y)


def pline(*pts):
    return [("M", *pts[0])] + [("L", *p) for p in pts[1:]]


def ring(cx, cy, rx, ry):
    """Closed ellipse centerline (O, o, 0)."""
    return arc(cx, cy, rx, ry, 0, 360) + [("Z",)]


def arc(cx, cy, rx, ry, a0, a1):
    """Elliptical arc in degrees, counter-clockwise when a1 > a0.
    Emitted as cubic segments of at most 90 degrees each."""
    sweep = a1 - a0
    n = max(1, math.ceil(abs(sweep) / 90))
    step = math.radians(sweep / n)
    t0 = math.radians(a0)
    k = 4 / 3 * math.tan(step / 4)

    def pt(t):
        return (cx + rx * math.cos(t), cy + ry * math.sin(t))

    def tan_vec(t):
        return (-rx * math.sin(t), ry * math.cos(t))

    cmds = [("M", *pt(t0))]
    for i in range(n):
        ta, tb = t0 + i * step, t0 + (i + 1) * step
        pa, pb = pt(ta), pt(tb)
        da, db = tan_vec(ta), tan_vec(tb)
        cmds.append(("C",
                     pa[0] + k * da[0], pa[1] + k * da[1],
                     pb[0] - k * db[0], pb[1] - k * db[1],
                     pb[0], pb[1]))
    return cmds


def chain(*segments):
    """Join command lists whose ends meet into one continuous stroke."""
    out = list(segments[0])
    for seg in segments[1:]:
        head, rest = seg[0], seg[1:]
        if head[0] != "M":
            raise ValueError("chain segments must start with M")
        px, py = _last_point(out)
        if math.dist((px, py), (head[1], head[2])) > 2.0:
            raise ValueError(
                f"chain gap: ({px:.0f},{py:.0f}) -> ({head[1]:.0f},{head[2]:.0f})")
        out.extend(rest)
    return out


def _last_point(cmds):
    for cmd in reversed(cmds):
        if cmd[0] in ("M", "L"):
            return cmd[1], cmd[2]
        if cmd[0] in ("Q", "C"):
            return cmd[-2], cmd[-1]
    raise ValueError("empty command list")


def glyph(*strokes, space=("straight", "straight"), lsb=None, rsb=None,
          adv=None, serifs=True):
    """Assemble a glyph definition.

    space: (left, right) side classes - 'straight' | 'round' | 'diag' |
    'open' | 'tight'; lsb/rsb override with explicit unit values.
    """
    norm = []
    for s in strokes:
        if isinstance(s, dict):
            norm.append(s)
        else:
            norm.append(stroke(s))
    return {"strokes": norm, "space": space, "lsb": lsb, "rsb": rsb,
            "adv": adv, "serifs": serifs}
