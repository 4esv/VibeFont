"""Compile traced outlines into a TTF with fontTools' FontBuilder."""

from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import newTable
from fontTools.ttLib.removeOverlaps import removeOverlaps

from vibefont.trace import Outline

UPM = 1000
CU2QU_MAX_ERR = 1.0  # font units; cubic -> quadratic conversion tolerance


def _notdef_glyph():
    pen = TTGlyphPen(None)
    for x0, y0, x1, y1 in ((50, 0, 550, 700), (100, 50, 500, 650)):
        pen.moveTo((x0, y0))
        pen.lineTo((x1, y0))
        pen.lineTo((x1, y1))
        pen.lineTo((x0, y1))
        pen.closePath()
    return pen.glyph()


def build_font(outlines: list[Outline], family: str, cap_height: int,
               x_height: int, out: Path) -> None:
    # Letters keep their own character as glyph name (valid AGL for A-Z a-z).
    agl = {".": "period", ",": "comma", "-": "hyphen"}
    names = {o.char: agl.get(o.char, o.char) for o in outlines}
    order = [".notdef", "space", *names.values()]

    glyf = {".notdef": _notdef_glyph(), "space": TTGlyphPen(None).glyph()}
    metrics = {".notdef": (600, 50), "space": (250, 0)}
    for o in outlines:
        tt_pen = TTGlyphPen(None)
        o.draw(Cu2QuPen(tt_pen, CU2QU_MAX_ERR))
        glyf[names[o.char]] = tt_pen.glyph()
        metrics[names[o.char]] = (round(o.advance), round(o.lsb))

    ascent = round(max(o.top for o in outlines))
    descent = round(min(min(o.bottom for o in outlines), 0))

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({ord(" "): "space",
                          **{ord(c): n for c, n in names.items()}})
    fb.setupGlyf(glyf)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ascent, descent=descent)
    # NOTE: Font Book refuses fonts without the full name-record set
    # (unique ID, full name, version, PostScript name), not just family+style.
    version = "1.000"
    ps_name = f"{family.replace(' ', '')}-Regular"
    fb.setupNameTable({
        "familyName": family,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{version};VIBE;{ps_name}",
        "fullName": f"{family} Regular",
        "version": f"Version {version}",
        "psName": ps_name,
        "copyright": "Traced from a sample sheet by vibefont.",
        "manufacturer": "VibeFont",
    })
    fb.setupOS2(sTypoAscender=ascent, sTypoDescender=descent,
                sTypoLineGap=0, usWinAscent=ascent, usWinDescent=-descent,
                sCapHeight=cap_height, sxHeight=x_height,
                fsSelection=0x40, fsType=0, achVendID="VIBE",
                ulUnicodeRange1=1 << 0,   # Basic Latin
                ulCodePageRange1=1 << 0)  # Latin 1
    fb.setupPost()

    font = fb.font
    font["head"].lowestRecPPEM = 6
    # Unhinted TTF: ask rasterizers for smoothing at all sizes.
    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x0F}
    font["gasp"] = gasp
    # Re-draws every contour through skia-pathops: dedupes overlaps and
    # normalizes winding direction, whatever orientation potrace emitted.
    removeOverlaps(font)
    out.parent.mkdir(parents=True, exist_ok=True)
    font.save(out)
