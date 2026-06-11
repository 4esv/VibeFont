"""Toolchain smoke tests: prove every link in the image -> font chain works.

# NOTE: These test capability, not features. If they pass, the env can
# rasterize an image, trace it to vector paths, and compile a valid TTF.
"""

import io

import numpy as np
import potrace
import pytest
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

UPM = 1000


def test_pillow_renders_bitmap():
    img = Image.new("L", (100, 100), 0)
    ImageDraw.Draw(img).rectangle([25, 25, 75, 75], fill=255)
    assert np.asarray(img).max() == 255


def test_potrace_traces_bitmap_to_curves():
    data = np.zeros((100, 100), dtype=np.uint8)
    data[25:75, 25:75] = 1
    path = potrace.Bitmap(data).trace()
    curves = list(path)
    assert len(curves) == 1  # one closed contour for the square


def test_fontbuilder_compiles_valid_ttf():
    fb = FontBuilder(UPM, isTTF=True)
    glyph_order = [".notdef", "A"]
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap({ord("A"): "A"})

    pen = TTGlyphPen(None)
    pen.moveTo((100, 0))
    pen.lineTo((100, 700))
    pen.lineTo((500, 700))
    pen.lineTo((500, 0))
    pen.closePath()
    square = pen.glyph()

    empty = TTGlyphPen(None).glyph()
    fb.setupGlyf({".notdef": empty, "A": square})
    fb.setupHorizontalMetrics({".notdef": (600, 0), "A": (600, 100)})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({"familyName": "VibeFontSmoke", "styleName": "Regular"})
    fb.setupOS2()
    fb.setupPost()

    buf = io.BytesIO()
    fb.save(buf)
    buf.seek(0)

    font = TTFont(buf)
    assert font.getGlyphOrder() == glyph_order
    assert font.getBestCmap()[ord("A")] == "A"


def test_pathops_removes_overlaps():
    pathops = pytest.importorskip("pathops")
    path = pathops.Path()
    pen = path.getPen()
    for origin in (0, 50):  # two overlapping squares
        pen.moveTo((origin, origin))
        pen.lineTo((origin + 100, origin))
        pen.lineTo((origin + 100, origin + 100))
        pen.lineTo((origin, origin + 100))
        pen.closePath()
    path.simplify()
    assert len(list(path.contours)) == 1
