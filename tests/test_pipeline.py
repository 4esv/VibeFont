"""End-to-end pipeline test against the real sample sheet.

# NOTE: needs assets/input/font-sample.png (untracked asset); skipped if absent.
"""

import string
from pathlib import Path

import pytest
from fontTools.ttLib import TTFont

from vibefont.build import build_font
from vibefont.recipes import derive_missing
from vibefont.segment import segment
from vibefont.trace import trace_glyph

SAMPLE = Path("assets/input/font-sample.png")
LINES = ["hambu", "rgevons", "HAMBU", "RGEVONS"]

pytestmark = pytest.mark.skipif(not SAMPLE.exists(),
                                reason="sample sheet not present")


@pytest.fixture(scope="module")
def font(tmp_path_factory):
    sheet = segment(SAMPLE, LINES)
    assert len(sheet.boxes) == sum(len(line) for line in LINES)

    caps = [b.baseline - b.top for b in sheet.boxes if b.char.isupper()]
    scale = 700 / (sum(caps) / len(caps))
    seen = set()
    outlines = []
    for box in sheet.boxes:
        if box.char not in seen:
            seen.add(box.char)
            outlines.append(trace_glyph(sheet.ink, box, scale, 60, 60))
    for ink, box in derive_missing(sheet,
                                   [c for c in string.ascii_letters + ".,-"
                                    if c not in seen]):
        outlines.append(trace_glyph(ink, box, scale, 60, 60))
    assert all(o.contours for o in outlines)

    g = next(o for o in outlines if o.char == "g")
    assert g.bottom < -150  # descender survived the y-flip

    ttf = tmp_path_factory.mktemp("font") / "out.ttf"
    build_font(outlines, "Pipeline Test", 700, 450, ttf)
    return TTFont(ttf)


def test_full_upper_and_lower_case(font):
    cmap = font.getBestCmap()
    assert {ord(c) for c in string.ascii_letters} <= set(cmap)
    glyf = font["glyf"]
    assert glyf[cmap[ord("g")]].numberOfContours >= 2  # bowl + counters
    for c in string.ascii_letters:
        assert glyf[cmap[ord(c)]].numberOfContours > 0, c


def test_installable_metadata(font):
    # NOTE: the records Font Book validation requires beyond family+style.
    name = font["name"]
    for name_id in (1, 2, 3, 4, 5, 6):
        assert name.getDebugName(name_id), f"name ID {name_id} missing"
    assert font["OS/2"].fsSelection & 0x40  # REGULAR
    assert font["OS/2"].ulCodePageRange1 & 1  # Latin 1
    assert "gasp" in font
