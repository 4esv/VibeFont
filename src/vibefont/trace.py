"""Trace glyph bitmaps into outline drawings in font units."""

from dataclasses import dataclass

import numpy as np
import potrace

from vibefont.segment import GlyphBox

PAD = 2  # px of clear margin around each crop so contours never touch the edge

# Per-glyph sidebearings in font units (lsb, rsb), measured from the ink
# bbox (serif tips included). Optical classes, loosest to tightest: serifed
# stems carry the most air, rounds less (curves recede from the extremes),
# diagonals and bar-armed letters the least (their corners already retreat).
# Values follow old-style serif letterfit at UPM 1000 / cap 700.
_STEM = (30, 30)
SIDEBEARINGS = {
    "h": _STEM, "m": _STEM, "n": _STEM, "u": _STEM, "i": _STEM, "l": _STEM,
    "b": (30, 20), "p": (30, 20), "d": (20, 30), "q": (20, 30),
    "o": (18, 18), "e": (18, 20), "c": (18, 24), "g": (18, 20),
    "a": (20, 28), "r": (30, 16), "f": (12, 10), "t": (14, 16),
    "s": (22, 22), "v": (10, 10), "w": (10, 10), "y": (10, 10),
    "x": (12, 12), "k": (30, 12), "z": (18, 18), "j": (16, 30),
    "H": (32, 32), "I": (32, 32), "M": (32, 32), "N": (32, 32),
    "U": (32, 32), "B": (32, 20), "D": (32, 22), "E": (32, 20),
    "F": (32, 16), "L": (32, 14), "P": (32, 20), "R": (32, 18),
    "O": (20, 20), "Q": (20, 20), "C": (20, 24), "G": (20, 28),
    "S": (24, 24), "A": (10, 10), "V": (10, 10), "W": (10, 10),
    "X": (14, 14), "Y": (10, 10), "K": (32, 12), "T": (14, 14),
    "Z": (18, 18), "J": (14, 32),
    ".": (80, 80), ",": (80, 80), "-": (45, 45),
}


def bearings(char: str) -> tuple[int, int]:
    return SIDEBEARINGS.get(char, (30, 30))


@dataclass(frozen=True)
class Outline:
    """A traced glyph: cubic contours, ready to replay into any cubic pen.

    Coordinates are font units, y up, origin at (glyph ink left - lsb,
    baseline).
    """

    char: str
    contours: list[list[tuple]]  # [("moveTo"|"lineTo"|"curveTo", pts...), ...]
    lsb: float
    rsb: float
    advance: float
    top: float  # ink extremes, font units relative to baseline
    bottom: float

    def draw(self, pen) -> None:
        for contour in self.contours:
            for op, *pts in contour:
                getattr(pen, op)(*pts)
            pen.closePath()


def trace_glyph(ink: np.ndarray, box: GlyphBox, scale: float,
                lsb: float, rsb: float) -> Outline:
    y0, x0 = max(box.top - PAD, 0), max(box.left - PAD, 0)
    crop = ink[y0:box.bottom + PAD, x0:box.right + PAD]
    # NOTE: potracer inverts bitmaps internally (image convention: dark =
    # ink), so ink pixels must go in as False or it traces the background.
    path = potrace.Bitmap(~crop).trace(turdsize=10, alphamax=1.0)

    def pt(p) -> tuple[float, float]:
        return ((x0 + p.x - box.left) * scale + lsb,
                (box.baseline - (y0 + p.y)) * scale)

    contours = []
    for curve in path:
        ops = [("moveTo", pt(curve.start_point))]
        for seg in curve:
            if seg.is_corner:
                ops.append(("lineTo", pt(seg.c)))
                ops.append(("lineTo", pt(seg.end_point)))
            else:
                ops.append(("curveTo", pt(seg.c1), pt(seg.c2),
                            pt(seg.end_point)))
        contours.append(ops)

    return Outline(
        char=box.char,
        contours=contours,
        lsb=lsb,
        rsb=rsb,
        advance=lsb + box.width * scale + rsb,
        top=(box.baseline - box.top) * scale,
        bottom=(box.baseline - box.bottom) * scale,
    )
