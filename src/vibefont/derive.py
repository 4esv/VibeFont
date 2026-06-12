"""Derive missing letters by composing bitmap parts of traced ones.

The hamburgevons sample carries every structural element of the alphabet:
stems and serifs (h n u), bowls (o b), arches (n h), diagonals (v V A),
arms and bars (r e E), tails (g R). Each missing letter is assembled from
those parts on a pixel canvas, then retraced like a genuine glyph, which
merges the seams into clean outlines.

Coordinates inside recipes are image pixels relative to the glyph's own
left edge (x, rightward) and baseline (y, UPWARD — unlike image rows).
"""

from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw

from vibefont.segment import GlyphBox, SampleSheet


@dataclass(frozen=True)
class Metrics:
    xh: float    # x-height, px above baseline
    cap: float
    asc: float
    desc: float  # depth below baseline, positive
    stem: float  # lowercase stem weight
    cstem: float  # capital stem weight

    @classmethod
    def measure(cls, sheet: SampleSheet) -> "Metrics":
        box = {b.char: b for b in sheet.boxes}

        def rise(chars):
            return float(np.median([box[c].baseline - box[c].top
                                    for c in chars if c in box]))

        def stem_w(ch, y_rel):
            b = box[ch]
            row = sheet.ink[round(b.baseline - y_rel), b.left:b.right]
            edges = np.diff(np.r_[0, row.astype(np.int8), 0])
            runs = list(zip(np.flatnonzero(edges == 1),
                            np.flatnonzero(edges == -1)))
            return float(runs[0][1] - runs[0][0])

        xh = rise("amuevons")
        cap = rise("HMBU")
        return cls(
            xh=xh, cap=cap,
            asc=rise("hb"),
            desc=float(box["g"].bottom - box["g"].baseline) if "g" in box
            else cap * 0.42,
            stem=stem_w("n", xh * 0.5),
            cstem=stem_w("R", cap * 0.5),
        )


@dataclass
class Piece:
    """A bitmap snippet. ``base`` is the row index of the baseline measured
    from the top of the array (may lie outside the array)."""

    ink: np.ndarray
    base: float

    @property
    def height(self) -> int:
        return self.ink.shape[0]

    @property
    def width(self) -> int:
        return self.ink.shape[1]

    def flip_h(self) -> "Piece":
        return Piece(self.ink[:, ::-1].copy(), self.base)

    def flip_v(self) -> "Piece":
        return Piece(self.ink[::-1].copy(), self.height - 1 - self.base)

    def rot180(self) -> "Piece":
        return self.flip_h().flip_v()

    def rot90cw(self) -> "Piece":
        """Baseline is meaningless after rotation; re-anchor before pasting."""
        ink = np.rot90(self.ink, -1).copy()
        return Piece(ink, ink.shape[0] - 1)

    def with_base(self, base: float) -> "Piece":
        return Piece(self.ink, base)

    def scaled(self, sx: float, sy: float | None = None) -> "Piece":
        sy = sx if sy is None else sy
        w = max(1, round(self.width * sx))
        h = max(1, round(self.height * sy))
        img = Image.fromarray(self.ink.astype(np.uint8) * 255)
        return Piece(np.asarray(img.resize((w, h), Image.LANCZOS)) > 127,
                     self.base * sy)

    def vstretch(self, new_height: int, keep: int = 70,
                 anchor: str = "bottom") -> "Piece":
        """3-slice vertical resize: keep ``keep`` rows at each end intact
        (serifs, joins) and stretch only the straight middle. ``anchor``
        names the end whose baseline-relative position stays fixed —
        "bottom" grows the piece upward, "top" grows it downward."""
        h = self.height
        if new_height == h:
            return self
        mid_h = new_height - 2 * keep
        mid = Image.fromarray(self.ink[keep:h - keep].astype(np.uint8) * 255)
        mid = np.asarray(mid.resize((self.width, mid_h), Image.LANCZOS)) > 127
        ink = np.concatenate([self.ink[:keep], mid, self.ink[h - keep:]])
        base = (self.base if anchor == "top"
                else new_height - (h - self.base))
        return Piece(ink, base)


class Glyph:
    """Composition canvas for one derived glyph."""

    def __init__(self, m: Metrics, width: float):
        h = round(m.asc + m.desc + 240)
        self.base = round(m.asc + 120)  # baseline row
        self.ink = np.zeros((h, round(width)), bool)

    def _rows(self, y0: float, y1: float) -> tuple[int, int]:
        return round(self.base - y1), round(self.base - y0)

    def paste(self, piece: Piece, x: float, dy: float = 0) -> "Glyph":
        r0 = round(self.base - dy - piece.base)
        c0 = round(x)
        h, w = self.ink.shape
        pr0, pc0 = max(-r0, 0), max(-c0, 0)
        pr1 = min(piece.height, h - r0)
        pc1 = min(piece.width, w - c0)
        if pr1 > pr0 and pc1 > pc0:
            self.ink[r0 + pr0:r0 + pr1, c0 + pc0:c0 + pc1] |= \
                piece.ink[pr0:pr1, pc0:pc1]
        return self

    def erase(self, x0: float, y0: float, x1: float, y1: float) -> "Glyph":
        r0, r1 = self._rows(y0, y1)
        self.ink[max(r0, 0):max(r1, 0),
                 max(round(x0), 0):max(round(x1), 0)] = False
        return self

    def _poly(self, pts, value: bool) -> "Glyph":
        img = Image.fromarray(self.ink.astype(np.uint8) * 255)
        ImageDraw.Draw(img).polygon(
            [(x, self.base - y) for x, y in pts], fill=255 if value else 0)
        self.ink = np.asarray(img) > 127
        return self

    def fill_poly(self, pts) -> "Glyph":
        return self._poly(pts, True)

    def erase_poly(self, pts) -> "Glyph":
        return self._poly(pts, False)

    def fill_ellipse(self, cx: float, cy: float, rx: float,
                     ry: float | None = None) -> "Glyph":
        ry = rx if ry is None else ry
        img = Image.fromarray(self.ink.astype(np.uint8) * 255)
        ImageDraw.Draw(img).ellipse(
            [cx - rx, self.base - cy - ry, cx + rx, self.base - cy + ry],
            fill=255)
        self.ink = np.asarray(img) > 127
        return self

    def result(self, char: str) -> tuple[np.ndarray, GlyphBox]:
        ys = np.flatnonzero(self.ink.any(axis=1))
        xs = np.flatnonzero(self.ink.any(axis=0))
        box = GlyphBox(char, int(xs[0]), int(ys[0]),
                       int(xs[-1]) + 1, int(ys[-1]) + 1, float(self.base))
        return self.ink, box


class Parts:
    """Cuts pieces out of the traced sample sheet."""

    def __init__(self, sheet: SampleSheet):
        self.ink = sheet.ink
        self.box = {b.char: b for b in sheet.boxes}

    def cut(self, ch: str, x0: float = 0, x1: float | None = None,
            y0: float | None = None, y1: float | None = None) -> Piece:
        b = self.box[ch]
        x1 = b.width if x1 is None else x1
        top = b.top if y1 is None else round(b.baseline - y1)
        bot = b.bottom if y0 is None else round(b.baseline - y0)
        top = max(top, 0)
        crop = self.ink[top:bot,
                        b.left + round(x0):b.left + round(x1)].copy()
        return Piece(crop, b.baseline - top)

    def width(self, ch: str) -> int:
        return self.box[ch].width
