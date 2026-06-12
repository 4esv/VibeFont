"""Compile traced outlines into a TTF with fontTools' FontBuilder."""

from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.filterPen import FilterPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import newTable
from fontTools.ttLib.removeOverlaps import removeOverlaps
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables.O_S_2f_2 import Panose

from vibefont.trace import Outline

UPM = 1000
CU2QU_MAX_ERR = 1.0  # font units; cubic -> quadratic conversion tolerance

# Conservative kerns for the classic problem pairs (diagonal caps, T/F/P
# overhangs, punctuation tucked under overhangs). Font units at UPM 1000;
# pairs whose glyphs are missing from a build are silently skipped.
KERN_PAIRS = {
    ("A", "V"): -75, ("V", "A"): -75, ("A", "W"): -55, ("W", "A"): -55,
    ("A", "T"): -70, ("T", "A"): -70, ("A", "Y"): -75, ("Y", "A"): -70,
    ("F", "A"): -45, ("P", "A"): -55,
    ("L", "T"): -65, ("L", "V"): -75, ("L", "W"): -60, ("L", "Y"): -70,
    ("T", "o"): -80, ("T", "e"): -80, ("T", "a"): -75, ("T", "c"): -80,
    ("T", "u"): -70, ("T", "w"): -65, ("T", "y"): -65, ("T", "r"): -55,
    ("T", "s"): -65, ("T", "i"): -30,
    ("V", "o"): -60, ("V", "a"): -55, ("V", "e"): -60, ("V", "u"): -45,
    ("V", "r"): -45,
    ("W", "o"): -40, ("W", "a"): -35, ("W", "e"): -40, ("W", "u"): -30,
    ("Y", "o"): -70, ("Y", "a"): -65, ("Y", "e"): -70, ("Y", "u"): -55,
    ("Y", "p"): -55, ("Y", "v"): -50,
    ("A", "v"): -40, ("A", "w"): -35, ("A", "y"): -40,
    ("v", "a"): -15, ("w", "a"): -10, ("y", "a"): -15,
    ("a", "v"): -15, ("a", "w"): -10, ("a", "y"): -15,
    ("P", "."): -85, ("P", ","): -85, ("T", "."): -80, ("T", ","): -80,
    ("V", "."): -90, ("V", ","): -90, ("W", "."): -65, ("W", ","): -65,
    ("Y", "."): -90, ("Y", ","): -90, ("F", "."): -75, ("F", ","): -75,
    ("r", "."): -55, ("r", ","): -55, ("v", "."): -55, ("v", ","): -55,
    ("w", "."): -50, ("w", ","): -50, ("y", "."): -55, ("y", ","): -55,
}


class _DropDegeneratePen(FilterPen):
    """Drops zero-length segments (every point coincident with the current
    point); pathops can emit them and some rasterizers stumble on them."""

    def __init__(self, out_pen):
        super().__init__(out_pen)
        self._cur = None

    def moveTo(self, pt):
        self._cur = pt
        super().moveTo(pt)

    def lineTo(self, pt):
        if pt == self._cur:
            return
        self._cur = pt
        super().lineTo(pt)

    def qCurveTo(self, *points):
        # NOTE: a trailing None means an all-off-curve TrueType contour;
        # those are never degenerate, pass them through untouched.
        if points[-1] is not None:
            if all(p == self._cur for p in points):
                return
            self._cur = points[-1]
        super().qCurveTo(*points)


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
    # NBSP maps to the same glyph as space: guarantees identical advance
    # widths and satisfies the whitespace coverage every checker expects.
    fb.setupCharacterMap({ord(" "): "space", 0x00A0: "space",
                          **{ord(c): n for c, n in names.items()}})
    fb.setupGlyf(glyf)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ascent, descent=descent)
    # NOTE: Font Book refuses fonts without the full name-record set
    # (unique ID, full name, version, PostScript name), not just family+style.
    # Windows-platform records only: Mac records are legacy and flagged by
    # fontbakery's adobefonts checks.
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
        "licenseDescription": "MIT License",
    }, mac=False)
    # Classification: IBM class 1.2 (Oldstyle Serifs / Garalde) and the
    # matching PANOSE digits -- Latin Text, cove serif, book weight,
    # old-style proportion, medium contrast.
    panose = Panose()
    panose.bFamilyType = 2
    panose.bSerifStyle = 2
    panose.bWeight = 5
    panose.bProportion = 2
    panose.bContrast = 6
    panose.bStrokeVariation = 3
    panose.bArmStyle = 5
    panose.bLetterForm = 2
    panose.bMidline = 3
    panose.bXHeight = 3
    # version 4: USE_TYPO_METRICS lives in fsSelection bit 7, undefined below
    fb.setupOS2(version=4, sTypoAscender=ascent, sTypoDescender=descent,
                sTypoLineGap=0, usWinAscent=ascent, usWinDescent=-descent,
                sCapHeight=cap_height, sxHeight=x_height,
                usWeightClass=400, usWidthClass=5,
                sFamilyClass=0x0102, panose=panose,
                # bit 6 REGULAR | bit 7 USE_TYPO_METRICS
                fsSelection=0x40 | 0x80, fsType=0, achVendID="VIBE",
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
    # ... and enable smart dropout control (the standard unhinted-font prep:
    # SCANCTRL on, SCANTYPE 4 -- what gftools fix-nonhinting injects).
    prep = newTable("prep")
    prep.program = ttProgram.Program()
    prep.program.fromAssembly(
        ["PUSHW[]", "511", "SCANCTRL[]", "PUSHB[]", "4", "SCANTYPE[]"])
    font["prep"] = prep
    # Re-draws every contour through skia-pathops: dedupes overlaps and
    # normalizes winding direction, whatever orientation potrace emitted.
    removeOverlaps(font)
    _strip_degenerate_segments(font)
    _fit_win_metrics(font, ascent, descent)
    fea = _kern_feature(names)
    if fea:
        addOpenTypeFeaturesFromString(font, fea)
    out.parent.mkdir(parents=True, exist_ok=True)
    font.save(out)


def _strip_degenerate_segments(font) -> None:
    glyf = font["glyf"]
    for name in font.getGlyphOrder():
        glyph = glyf[name]
        if glyph.numberOfContours <= 0:
            continue
        pen = TTGlyphPen(None)
        glyph.draw(_DropDegeneratePen(pen), glyf)
        glyf[name] = pen.glyph()


def _fit_win_metrics(font, ascent: int, descent: int) -> None:
    """usWin metrics must cover the real glyph extremes, which drift from
    the design values during cu2qu conversion and overlap removal."""
    glyf = font["glyf"]
    y_min, y_max = 0, 0
    for name in font.getGlyphOrder():
        glyph = glyf[name]
        if glyph.numberOfContours == 0:
            continue
        glyph.recalcBounds(glyf)
        y_min = min(y_min, glyph.yMin)
        y_max = max(y_max, glyph.yMax)
    os2 = font["OS/2"]
    os2.usWinAscent = max(y_max, ascent)
    os2.usWinDescent = max(-y_min, -descent)


def _kern_feature(names: dict[str, str]) -> str:
    rules = [f"pos {names[a]} {names[b]} {v};"
             for (a, b), v in KERN_PAIRS.items()
             if a in names and b in names]
    if not rules:
        return ""
    return ("languagesystem DFLT dflt;\n"
            "languagesystem latn dflt;\n"
            "feature kern {\n  " + "\n  ".join(rules) + "\n} kern;\n")
