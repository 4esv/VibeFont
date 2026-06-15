"""The five Eslop families and the skeleton -> outline realization pipeline.

One shared skeleton library goes in; five different fonts come out. Each
family is a parameter set: stroke weight, cap/join style, metric targets
(a piecewise-linear y remap keeps cap/x-height/descender honest at any
weight), slab serifs, monospace fitting, and Friendly's bottom-weighted
wobble.
"""

from __future__ import annotations

import math
import random
import zlib
from dataclasses import dataclass, field

import pathops

from eslop import geometry
from eslop.skeleton import ASC, BASE, CAP, DESC, XH

REF_STROKE = 80.0
MONO_MIN_SB = 26.0


@dataclass(frozen=True)
class Family:
    key: str
    name: str
    tagline: str
    stroke: float
    cap: float = 700.0
    asc: float = 720.0
    desc: float = -220.0
    xh: float | None = None        # x-height target; None = follow cap band
    width_scale: float = 1.0
    cap_style: str = "square"
    join_style: str = "miter"
    serifs: bool = False
    serif_len: float = 2.35        # slab width / stroke
    serif_thick: float = 0.80      # slab height / stroke
    arm_serif_len: float = 2.0
    bottom_weight: float = 0.0     # extra stroke weight at the baseline
    wobble_amp: float = 0.0
    wobble_len: float = 130.0
    bounce: float = 0.0            # per-glyph baseline shuffle
    mono_advance: int | None = None
    sb: dict = field(default_factory=dict)
    word_space: int = 240
    weight_class: int = 400
    kern_scale: float = 1.0
    is_mono: bool = False


FAMILIES = {
    "billboard": Family(
        key="billboard", name="Eslop Billboard",
        tagline="Display. Maximum ink, minimum apology.",
        stroke=160, width_scale=1.05, weight_class=900, kern_scale=1.25,
        sb={"straight": 20, "round": 8, "diag": 0, "open": 8, "tight": 0},
        word_space=210,
    ),
    "default": Family(
        key="default", name="Eslop Default",
        tagline="Sans. The one it was going to pick anyway.",
        stroke=82,
        sb={"straight": 36, "round": 22, "diag": 8, "open": 18, "tight": 6},
        word_space=240,
    ),
    "serious": Family(
        key="serious", name="Eslop Serious",
        tagline="Slab serif. For when the stakes feel real.",
        stroke=70, serifs=True,
        sb={"straight": 16, "round": 24, "diag": 8, "open": 18, "tight": 4},
        word_space=250,
    ),
    "code": Family(
        key="code", name="Eslop Code",
        tagline="Monospace. Every glyph is equal here.",
        stroke=84, cap_style="round", join_style="round",
        mono_advance=600, is_mono=True, kern_scale=0.0,
        sb={}, word_space=600,
    ),
    "friendly": Family(
        key="friendly", name="Eslop Friendly",
        tagline="Comic. Bottom-heavy on purpose, honest.",
        stroke=86, cap=678, asc=724, desc=-206, xh=502,
        bottom_weight=0.26, wobble_amp=10.0, wobble_len=300, bounce=9,
        kern_scale=0.5,
        sb={"straight": 46, "round": 34, "diag": 22, "open": 32, "tight": 16},
        word_space=300,
    ),
}

BUILD_ORDER = ["billboard", "default", "serious", "code", "friendly"]


# ----------------------------------------------------------- y metric remap

def _band_map(fam: Family):
    """Piecewise-linear y remap, reference space -> family metric space.

    Skeletons are authored for an 80-unit stroke; this squeezes/stretches
    centerlines so outline extremes land on the family's cap/x/descender
    lines at its own stroke weight. Knots sit at the metric lines;
    overshoot keeps slope 1 above the cap knot.
    """
    w = fam.stroke
    knots_r = [DESC, BASE, CAP, CAP + 12, ASC]
    knots_t = [fam.desc + w / 2, w / 2, fam.cap - w / 2,
               fam.cap - w / 2 + 12, fam.asc - w / 2]
    if fam.xh is not None:
        knots_r.insert(2, XH)
        knots_t.insert(2, fam.xh - w / 2)
    pairs = list(zip(knots_r, knots_t))

    def f(y: float) -> float:
        if y <= pairs[0][0]:
            r0, t0 = pairs[0]
            r1, t1 = pairs[1]
            return t0 + (y - r0) * (t1 - t0) / (r1 - r0)
        for (r0, t0), (r1, t1) in zip(pairs, pairs[1:]):
            if y <= r1:
                return t0 + (y - r0) * (t1 - t0) / (r1 - r0)
        r0, t0 = pairs[-2]
        r1, t1 = pairs[-1]
        return t1 + (y - r1) * (t1 - t0) / (r1 - r0)

    return f


def _map_cmds(cmds, fx, fy):
    out = []
    for cmd in cmds:
        op, coords = cmd[0], cmd[1:]
        mapped = []
        for i in range(0, len(coords), 2):
            mapped.extend((fx(coords[i]), fy(coords[i + 1])))
        out.append((op, *mapped))
    return out


# ------------------------------------------------------------------- wobble

def _wobble(pts, closed, char, idx, fam: Family):
    if fam.wobble_amp <= 0 or len(pts) < 2:
        return pts
    rng = random.Random(zlib.crc32(f"{char}:{idx}".encode()))
    phases = [rng.uniform(0, 2 * math.pi) for _ in range(4)]
    seglens = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seglens) + (math.dist(pts[-1], pts[0]) if closed else 0)
    if total < 1e-6:
        return pts
    amp = fam.wobble_amp * min(1.0, total / 160 + 0.35)
    if closed:
        k1 = max(1, round(total / fam.wobble_len))
        f1 = 2 * math.pi * k1 / total
        f2 = 2 * f1
    else:
        f1 = 2 * math.pi / fam.wobble_len
        f2 = 2 * math.pi / (fam.wobble_len * 0.61)
    out, s = [], 0.0
    for i, p in enumerate(pts):
        if i > 0:
            s += seglens[i - 1]
        ox = amp * (0.72 * math.sin(f1 * s + phases[0])
                    + 0.28 * math.sin(f2 * s + phases[1]))
        oy = amp * (0.72 * math.sin(f1 * s + phases[2])
                    + 0.28 * math.sin(f2 * s + phases[3]))
        out.append((p[0] + ox, p[1] + oy))
    return out


def _local_width(y, fam: Family, mult=1.0):
    base = fam.stroke * mult
    if fam.bottom_weight <= 0:
        return base
    t = max(0.0, min(1.25, 1.0 - y / fam.cap))
    return base * (1.0 + fam.bottom_weight * t)


# ------------------------------------------------------------------- serifs

def _trim_diagonal_caps(cmds, w):
    """Square caps on diagonal terminals poke past the cap line and the
    baseline: the cap corner reaches (|ux|+|uy|)*w/2 past the endpoint
    instead of w/2. Pull each diagonal endpoint back along the stroke so
    the corner lands where a flat terminal would."""
    if any(c[0] == "Z" for c in cmds):
        return cmds
    out = list(cmds)
    for at_start in (True, False):
        (px, py), (tx, ty) = _terminal(out, at_start)
        if not (0.45 <= abs(ty) <= 0.99):
            continue
        delta = (w / 2) * (abs(tx) + abs(ty) - 1) / abs(ty)
        nx, ny = px - tx * delta, py - ty * delta
        idx = 0 if at_start else len(out) - 1
        cmd = out[idx]
        out[idx] = (cmd[0], nx, ny) if at_start else (*cmd[:-2], nx, ny)
    return out


def _terminal(cmds, at_start):
    """(point, outward unit tangent) at one end of an open stroke."""
    pts = []
    for cmd in cmds:
        op, coords = cmd[0], cmd[1:]
        for i in range(0, len(coords), 2):
            pts.append((coords[i], coords[i + 1]))
    if at_start:
        p, q = pts[0], next((pt for pt in pts[1:] if math.dist(pt, pts[0]) > 1), pts[-1])
    else:
        p, q = pts[-1], next((pt for pt in reversed(pts[:-1])
                              if math.dist(pt, pts[-1]) > 1), pts[0])
    d = math.dist(p, q)
    return p, ((p[0] - q[0]) / d, (p[1] - q[1]) / d)


def _slab_height_ok(py, fam: Family) -> bool:
    """Slabs belong at the feet and heads of strokes — baseline, cap/
    ascender, and descender bands. A vertical terminal anywhere else
    (an S spine, a 9's tail, an x-height entry) stays bare; mid-glyph
    slabs read as censor bars."""
    return (-30 <= py <= 130
            or fam.cap - 80 <= py <= fam.asc + 30
            or fam.desc - 30 <= py <= fam.desc + 130)


def _serif_polys(strokes_cmds, fam: Family):
    polys = []
    w = fam.stroke
    half = w / 2
    slab_half = w * fam.serif_len / 2
    thick = w * fam.serif_thick
    arm_half = w * fam.arm_serif_len / 2
    for cmds, mult, s_start, s_end in strokes_cmds:
        if any(c[0] == "Z" for c in cmds):
            continue
        for at_start, setting in ((True, s_start), (False, s_end)):
            if setting == "none":
                continue
            (px, py), (tx, ty) = _terminal(cmds, at_start)
            if abs(ty) >= 0.72 and _slab_height_ok(py, fam):
                y0 = py - half if ty < 0 else py + half - thick
                polys.append([(px - slab_half, y0), (px + slab_half, y0),
                              (px + slab_half, y0 + thick),
                              (px - slab_half, y0 + thick)])
            elif setting == "arm" and abs(tx) >= 0.8:
                x0 = px - half if tx < 0 else px + half - thick
                polys.append([(x0, py - arm_half), (x0 + thick, py - arm_half),
                              (x0 + thick, py + arm_half),
                              (x0, py + arm_half)])
    return polys


# ------------------------------------------------------------------ realize

@dataclass
class Realized:
    ops: list
    advance: int
    lsb: int
    xmin: int
    xmax: int
    ymin: int
    ymax: int


def _norm_strokes(gdef):
    out = []
    for s in gdef["strokes"]:
        if "dot" in s:
            out.append(("dot", s["dot"]))
        else:
            out.append(("cmds", (s["cmds"], s.get("w", 1.0),
                                 s.get("serif_start", "auto"),
                                 s.get("serif_end", "auto"))))
    return out


def realize(fam: Family, char: str, gdef) -> Realized:
    if not gdef["strokes"]:
        adv = gdef.get("adv") or fam.word_space
        if fam.is_mono:
            adv = fam.mono_advance
        return Realized([], int(adv), 0, 0, 0, 0, 0)

    fy = _band_map(fam)
    ws = fam.width_scale
    dot_scale = fam.stroke / REF_STROKE
    strokes = _norm_strokes(gdef)

    # width-scale x, remap y
    cmds_list, dots = [], []
    for kind, payload in strokes:
        if kind == "dot":
            x, y, r = payload
            dots.append((x * ws, fy(y), r * dot_scale))
        else:
            cmds, mult, s0, s1 = payload
            cmds_list.append((_map_cmds(cmds, lambda x: x * ws, fy),
                              mult, s0, s1))

    # monospace: squeeze wide glyphs into the fixed cell
    if fam.is_mono:
        xs = []
        for cmds, *_ in cmds_list:
            pts, _ = geometry.flatten(cmds)
            xs.extend(p[0] for p in pts)
        xs.extend((d[0] - d[2], d[0] + d[2]) for d in dots)
        xs = [x for item in xs for x in (item if isinstance(item, tuple) else (item,))]
        if xs:
            est = (max(xs) - min(xs)) + fam.stroke
            inner = fam.mono_advance - 2 * MONO_MIN_SB
            if est > inner:
                sx = (inner - fam.stroke) / max(1.0, est - fam.stroke)
                cx = (max(xs) + min(xs)) / 2
                squeeze = lambda x: cx + (x - cx) * sx
                cmds_list = [(_map_cmds(c, squeeze, lambda y: y), m, a, b)
                             for c, m, a, b in cmds_list]
                dots = [(squeeze(x), y, r) for x, y, r in dots]

    path = pathops.Path()

    if fam.bottom_weight > 0 or fam.wobble_amp > 0:
        # capsule back-end: variable width + wobble
        for idx, (cmds, mult, _, _) in enumerate(cmds_list):
            pts, closed = geometry.flatten(cmds)
            pts = _wobble(pts, closed, char, idx, fam)
            widths = [_local_width(p[1], fam, mult) for p in pts]
            for poly in geometry.capsule_polys(pts, widths, closed):
                geometry.add_polygon(path, poly)
        for x, y, r in dots:
            scale = _local_width(y, fam) / fam.stroke
            geometry.add_polygon(path, geometry.circle_poly(x, y, r * scale))
        prune = True
    else:
        cmds_list = [(_trim_diagonal_caps(c, fam.stroke * m), m, a, b)
                     for c, m, a, b in cmds_list]
        for cmds, mult, _, _ in cmds_list:
            path.addPath(geometry.stroke_cmds(
                cmds, fam.stroke * mult, fam.cap_style, fam.join_style))
        for x, y, r in dots:
            geometry.add_circle(path, x, y, r)
        prune = False

    if fam.serifs and gdef.get("serifs", True):
        for poly in _serif_polys(cmds_list, fam):
            geometry.add_polygon(path, poly)

    out = geometry.union(path)
    xmin, ymin, xmax, ymax = out.bounds
    width = xmax - xmin

    if fam.is_mono:
        advance = fam.mono_advance
        lsb = (advance - width) / 2
    else:
        side_l, side_r = gdef.get("space", ("straight", "straight"))
        lsb = gdef["lsb"] if gdef.get("lsb") is not None else fam.sb[side_l]
        rsb = gdef["rsb"] if gdef.get("rsb") is not None else fam.sb[side_r]
        advance = lsb + width + rsb

    dx = lsb - xmin
    dy = 0.0
    if fam.bounce > 0 and (char.isalnum()):
        rng = random.Random(zlib.crc32(f"bounce:{char}".encode()))
        dy = rng.uniform(-1, 1) * fam.bounce

    ops = geometry.record(out, dx, dy, prune=prune)
    return Realized(ops, round(advance), round(xmin + dx),
                    round(xmin + dx), round(xmax + dx),
                    round(ymin + dy), round(ymax + dy))
