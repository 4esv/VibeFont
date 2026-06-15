"""Eslop toolchain tests: the five families compile into complete,
well-attributed, installable TTFs. (Letterform quality is judged from the
proof sheets, not here.)"""

import pytest
from fontTools.ttLib import TTFont

from eslop.build import build_family
from eslop.skeletons import EXPECTED, GLYPHS
from eslop.styles import BUILD_ORDER, FAMILIES


def test_full_charset_authored():
    missing = sorted(set(EXPECTED) - set(GLYPHS))
    assert not missing, f"unauthored glyphs: {missing}"


@pytest.fixture(scope="module", params=BUILD_ORDER)
def built(request, tmp_path_factory):
    out = tmp_path_factory.mktemp("eslop")
    ttf = build_family(request.param, out)
    return request.param, TTFont(ttf)


def test_cmap_covers_charset(built):
    _, font = built
    cmap = font.getBestCmap()
    missing = [c for c in EXPECTED if ord(c) not in cmap]
    assert not missing, f"cmap missing: {missing}"
    assert 0x00A0 in cmap  # NBSP


def test_installable_and_attributed(built):
    key, font = built
    os2 = font["OS/2"]
    assert os2.fsType == 0
    assert os2.fsSelection & 0x80  # USE_TYPO_METRICS
    name = font["name"]
    family = name.getDebugName(1)
    assert family == FAMILIES[key].name
    for name_id in (2, 4, 6, 13):
        assert name.getDebugName(name_id), f"name ID {name_id} missing"
    assert name.getDebugName(6).startswith("Eslop")
    assert " " not in name.getDebugName(6)  # PostScript name


def test_win_metrics_cover_extremes(built):
    _, font = built
    glyf, os2 = font["glyf"], font["OS/2"]
    y_min, y_max = 0, 0
    for gname in font.getGlyphOrder():
        g = glyf[gname]
        if g.numberOfContours > 0:
            g.recalcBounds(glyf)
            y_min, y_max = min(y_min, g.yMin), max(y_max, g.yMax)
    assert os2.usWinAscent >= y_max
    assert os2.usWinDescent >= -y_min


def test_no_degenerate_contours(built):
    _, font = built
    glyf = font["glyf"]
    for gname in font.getGlyphOrder():
        g = glyf[gname]
        if g.numberOfContours <= 0:
            continue
        start = 0
        for end in g.endPtsOfContours:
            assert end - start + 1 >= 3, f"{gname}: contour < 3 points"
            start = end + 1


def test_code_is_truly_monospace():
    out_dir = None
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as td:
        font = TTFont(build_family("code", Path(td)))
        advances = {font["hmtx"][g][0] for g in font.getGlyphOrder()}
        assert advances == {600}, f"advances vary: {sorted(advances)}"
        assert font["post"].isFixedPitch == 1
        assert font["OS/2"].panose.bProportion == 9


def test_kerning_in_proportional_families():
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as td:
        font = TTFont(build_family("default", Path(td)))
        assert "GPOS" in font
        font_mono = TTFont(build_family("code", Path(td)))
        assert "GPOS" not in font_mono
