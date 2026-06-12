"""Trace glyph bitmaps into outline drawings in font units."""

from dataclasses import dataclass

import numpy as np
import potrace

from vibefont.segment import GlyphBox

PAD = 2  # px of clear margin around each crop so contours never touch the edge


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
