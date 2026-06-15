"""Centerline strokes -> filled glyph outlines.

Two expansion back-ends share one output contract (a pathops.Path of the
filled glyph): skia's native stroker for constant-width families, and
hand-built variable-width capsule unions for Eslop Friendly, whose
bottom-weighted wobbly strokes the stroker can't express.

Coordinate convention: skeleton coordinates are stroke CENTERLINES.
Square/round caps both extend w/2 past the endpoint, so a stem whose
centerline ends at y=660 produces ink up to y=700 at stroke width 80 —
the cap-height line. Every metric convention in skeletons/ relies on it.
"""

from __future__ import annotations

import math

import pathops

# cubic Bezier quadrant handle factor (circle approximation)
K = 0.5522847498307936

FLATTEN_STEP = 12.0  # target chord length (font units) when flattening curves
MITER_LIMIT = 2.5    # acute apexes (A, V, W) fall back to a flat bevel cut

CAPS = {
    "butt": pathops.LineCap.BUTT_CAP,
    "round": pathops.LineCap.ROUND_CAP,
    "square": pathops.LineCap.SQUARE_CAP,
}
JOINS = {
    "miter": pathops.LineJoin.MITER_JOIN,
    "round": pathops.LineJoin.ROUND_JOIN,
    "bevel": pathops.LineJoin.BEVEL_JOIN,
}


# ---------------------------------------------------------------- flattening

def _eval_cubic(p0, c1, c2, p1, t):
    mt = 1 - t
    a, b, c, d = mt * mt * mt, 3 * mt * mt * t, 3 * mt * t * t, t * t * t
    return (a * p0[0] + b * c1[0] + c * c2[0] + d * p1[0],
            a * p0[1] + b * c1[1] + c * c2[1] + d * p1[1])


def _eval_quad(p0, c, p1, t):
    mt = 1 - t
    a, b, cc = mt * mt, 2 * mt * t, t * t
    return (a * p0[0] + b * c[0] + cc * p1[0],
            a * p0[1] + b * c[1] + cc * p1[1])


def _steps(*pts):
    length = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    return max(4, min(64, math.ceil(length / FLATTEN_STEP)))


def flatten(cmds):
    """Flatten an M/L/Q/C/Z command list -> (points, closed)."""
    pts: list[tuple[float, float]] = []
    closed = False
    for cmd in cmds:
        op = cmd[0]
        if op == "M":
            pts.append((cmd[1], cmd[2]))
        elif op == "L":
            pts.append((cmd[1], cmd[2]))
        elif op == "Q":
            p0, c, p1 = pts[-1], (cmd[1], cmd[2]), (cmd[3], cmd[4])
            n = _steps(p0, c, p1)
            pts.extend(_eval_quad(p0, c, p1, i / n) for i in range(1, n + 1))
        elif op == "C":
            p0 = pts[-1]
            c1, c2, p1 = (cmd[1], cmd[2]), (cmd[3], cmd[4]), (cmd[5], cmd[6])
            n = _steps(p0, c1, c2, p1)
            pts.extend(_eval_cubic(p0, c1, c2, p1, i / n)
                       for i in range(1, n + 1))
        elif op == "Z":
            closed = True
        else:
            raise ValueError(f"unknown command {op!r}")
    if closed and math.dist(pts[0], pts[-1]) < 1e-6:
        pts.pop()
    return pts, closed


# ------------------------------------------------------------ skia back-end

def _draw_cmds(path: pathops.Path, cmds) -> None:
    for cmd in cmds:
        op = cmd[0]
        if op == "M":
            path.moveTo(cmd[1], cmd[2])
        elif op == "L":
            path.lineTo(cmd[1], cmd[2])
        elif op == "Q":
            path.quadTo(*cmd[1:])
        elif op == "C":
            path.cubicTo(*cmd[1:])
        elif op == "Z":
            path.close()


def stroke_cmds(cmds, width: float, cap: str, join: str) -> pathops.Path:
    """Expand one centerline stroke into its filled region."""
    p = pathops.Path()
    _draw_cmds(p, cmds)
    p.stroke(width, CAPS[cap], JOINS[join], MITER_LIMIT)
    return p


# --------------------------------------------------------- capsule back-end

def capsule_polys(points, widths, closed):
    """Variable-width stroke as overlapping quads + round-join circles.

    Round caps/joins everywhere: a circle of the local half-width sits at
    every vertex, so weight changes along the stroke blend smoothly.
    """
    polys = []
    n = len(points)
    pairs = [(i, i + 1) for i in range(n - 1)]
    if closed:
        pairs.append((n - 1, 0))
    for i, j in pairs:
        (x0, y0), (x1, y1) = points[i], points[j]
        dx, dy = x1 - x0, y1 - y0
        seg = math.hypot(dx, dy)
        if seg < 1e-6:
            continue
        nx, ny = -dy / seg, dx / seg
        r0, r1 = widths[i] / 2, widths[j] / 2
        polys.append([(x0 + nx * r0, y0 + ny * r0),
                      (x1 + nx * r1, y1 + ny * r1),
                      (x1 - nx * r1, y1 - ny * r1),
                      (x0 - nx * r0, y0 - ny * r0)])
    for (x, y), w in zip(points, widths):
        polys.append(circle_poly(x, y, w / 2))
    return polys


def circle_poly(cx, cy, r, n=36):
    step = 2 * math.pi / n
    return [(cx + r * math.cos(i * step), cy + r * math.sin(i * step))
            for i in range(n)]


def _signed_area(poly):
    s = 0.0
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        s += x0 * y1 - x1 * y0
    return s / 2


def add_polygon(path: pathops.Path, poly) -> None:
    if _signed_area(poly) < 0:
        poly = poly[::-1]
    path.moveTo(*poly[0])
    for pt in poly[1:]:
        path.lineTo(*pt)
    path.close()


def add_circle(path: pathops.Path, cx, cy, r) -> None:
    """Filled circle as eight quadratic segments (TTF holds no cubics)."""
    n = 8
    step = math.pi / n  # half-segment angle
    ctrl_r = r / math.cos(step)
    path.moveTo(cx + r, cy)
    for i in range(1, n + 1):
        a_ctrl = (2 * i - 1) * step
        a_on = 2 * i * step
        path.quadTo(cx + ctrl_r * math.cos(a_ctrl),
                    cy + ctrl_r * math.sin(a_ctrl),
                    cx + r * math.cos(a_on),
                    cy + r * math.sin(a_on))
    path.close()


# -------------------------------------------------------------------- union

def union(path: pathops.Path) -> pathops.Path:
    path.fillType = pathops.FillType.WINDING
    path.convertConicsToQuads(0.25)
    # skia can refuse near-degenerate input; snapping coordinates to a
    # grid (progressively coarser) shakes the geometry loose.
    last = None
    for quantum in (None, 0.25, 1.0):
        p = path if quantum is None else _snapped(path, quantum)
        try:
            out = pathops.simplify(p, fix_winding=True)
            out.convertConicsToQuads(0.25)
            return out
        except pathops.PathOpsError as e:
            last = e
    raise last


def _snapped(path: pathops.Path, quantum: float) -> pathops.Path:
    from fontTools.pens.recordingPen import RecordingPen

    rp = RecordingPen()
    path.draw(rp)
    out = pathops.Path()
    out.fillType = path.fillType
    pen = out.getPen()
    q = quantum
    for op, args in rp.value:
        snapped = tuple(
            pt if pt is None else (round(pt[0] / q) * q, round(pt[1] / q) * q)
            for pt in args)
        getattr(pen, op)(*snapped)
    return out


# ---------------------------------------------------------------- recording

def record(path: pathops.Path, dx: float = 0.0, dy: float = 0.0,
           prune: bool = False):
    """pathops.Path -> [(op, args)] pen ops, translated and rounded.

    Rounding to font-unit ints happens here so degenerate zero-length
    lines can be dropped before they ever reach a glyph table.
    """
    from fontTools.pens.recordingPen import RecordingPen

    rp = RecordingPen()
    path.draw(rp)
    out = []
    cur = None
    for op, args in rp.value:
        pts = tuple(
            pt if pt is None
            else (round(pt[0] + dx), round(pt[1] + dy))
            for pt in args)
        if op == "lineTo" and pts[0] == cur:
            continue
        if op in ("lineTo", "moveTo"):
            cur = pts[0]
        elif op == "qCurveTo" and pts[-1] is not None:
            cur = pts[-1]
        out.append((op, pts))
    if prune:
        out = _prune_collinear(out)
    return out


def _prune_collinear(ops, tol=0.6):
    """Collapse nearly-collinear runs of lineTo points (capsule unions of
    36-gon circles produce hundreds of them)."""
    # split into contours
    contours, cur = [], []
    for op, args in ops:
        if op == "moveTo":
            cur = [(op, args)]
            contours.append(cur)
        else:
            cur.append((op, args))
    out = []
    for contour in contours:
        if not all(op in ("moveTo", "lineTo", "closePath")
                   for op, _ in contour):
            out.extend(contour)
            continue
        pts = [args[0] for op, args in contour if op != "closePath"]
        keep = _prune_ring(pts, tol)
        out.append(("moveTo", (keep[0],)))
        out.extend(("lineTo", (p,)) for p in keep[1:])
        out.append(("closePath", ()))
    return out


def _prune_ring(pts, tol):
    changed = True
    pts = list(pts)
    while changed and len(pts) > 4:
        changed = False
        kept = []
        n = len(pts)
        i = 0
        while i < n:
            a = kept[-1] if kept else pts[i - 1]
            b, c = pts[i], pts[(i + 1) % n]
            if _point_line_dist(b, a, c) < tol:
                changed = True
            else:
                kept.append(b)
            i += 1
        if len(kept) >= 4:
            pts = kept
        else:
            break
    return pts


def _point_line_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    seg = math.hypot(ax, ay)
    if seg < 1e-9:
        return math.dist(p, a)
    return abs(ax * (p[1] - a[1]) - ay * (p[0] - a[0])) / seg
