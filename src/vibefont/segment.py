"""Locate glyphs in a sample-sheet image.

The sheet convention: text rows on baseline guides, glyphs separated by
clear horizontal gaps. Ink is near-black; guides (baselines, grids, zone
strips) are light or saturated colors, so at least one RGB channel stays
bright and ``max(R,G,B) < INK_THRESHOLD`` isolates the ink cleanly.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

INK_THRESHOLD = 128
# NOTE: guide-line intersections can survive the ink mask as 1-2px specks;
# anything below this area is noise, not a glyph.
MIN_GLYPH_AREA = 400
# Channel spread (max-min) above which a non-ink pixel counts as a colored
# guide line rather than background/grid.
GUIDE_SPREAD = 80


@dataclass(frozen=True)
class GlyphBox:
    """Tight ink bbox of one glyph, in image pixels (y down)."""

    char: str
    left: int
    top: int
    right: int
    bottom: int
    baseline: float  # image y of this row's baseline

    @property
    def width(self) -> int:
        return self.right - self.left


@dataclass
class SampleSheet:
    size: tuple[int, int]  # (width, height) of the source image
    ink: np.ndarray  # bool HxW, True = ink
    boxes: list[GlyphBox]


def _runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """[(start, end)) spans of True in a 1-D bool array."""
    edges = np.diff(np.r_[0, mask.astype(np.int8), 0])
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))


def _baseline(rgb: np.ndarray, ink: np.ndarray, band: tuple[int, int],
              bottoms: list[int]) -> float:
    """Baseline y for one text band: the colored guide line if drawn, else
    the median glyph bottom."""
    y0, y1 = band
    seg = rgb[y0:y1].astype(int)
    spread = seg.max(axis=2) - seg.min(axis=2)
    guide = (~ink[y0:y1]) & (spread > GUIDE_SPREAD)
    rows = np.flatnonzero(guide.sum(axis=1) > rgb.shape[1] // 3)
    if rows.size:
        return y0 + float(rows.mean())
    return float(np.median(bottoms))


def segment(image: Path, lines: list[str]) -> SampleSheet:
    """Split the sheet into per-glyph boxes matched against ``lines``."""
    rgb = np.asarray(Image.open(image).convert("RGB"))
    ink = rgb.max(axis=2) < INK_THRESHOLD

    bands = _runs(ink.any(axis=1))
    if len(bands) != len(lines):
        raise ValueError(f"found {len(bands)} text rows, expected {len(lines)}")

    boxes: list[GlyphBox] = []
    for (y0, y1), line in zip(bands, lines):
        band_ink = ink[y0:y1]
        spans = [(x0, x1) for x0, x1 in _runs(band_ink.any(axis=0))
                 if band_ink[:, x0:x1].sum() >= MIN_GLYPH_AREA]
        if len(spans) != len(line):
            raise ValueError(
                f"row {y0}-{y1}: found {len(spans)} glyphs, expected {line!r}")
        row = []
        for ch, (x0, x1) in zip(line, spans):
            ys = np.flatnonzero(band_ink[:, x0:x1].any(axis=1))
            row.append((ch, x0, y0 + ys[0], x1, y0 + ys[-1] + 1))
        baseline = _baseline(rgb, ink, (y0, y1), [b[4] for b in row])
        boxes += [GlyphBox(ch, x0, top, x1, bot, baseline)
                  for ch, x0, top, x1, bot in row]

    return SampleSheet((rgb.shape[1], rgb.shape[0]), ink, boxes)
