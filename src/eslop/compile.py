"""Realized outlines -> installable TTF + WOFF2 via fontTools FontBuilder."""

from __future__ import annotations

from pathlib import Path

from fontTools import agl
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import newTable
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables.O_S_2f_2 import Panose

from eslop import __version__
from eslop.styles import Family, Realized

UPM = 1000
TYPO_ASC, TYPO_DESC, TYPO_GAP = 760, -240, 0

# The classic problem pairs (diagonal caps, T/F/P overhangs, punctuation
# tucked under overhangs). Values are for the Regular sans; each family
# scales them by kern_scale (0 for the monospace).
KERN_PAIRS = {
    ("A", "V"): -38, ("V", "A"): -38, ("A", "W"): -28, ("W", "A"): -28,
    ("A", "T"): -34, ("T", "A"): -34, ("A", "Y"): -40, ("Y", "A"): -36,
    ("F", "A"): -22, ("P", "A"): -28, ("F", "a"): -14,
    ("L", "T"): -34, ("L", "V"): -38, ("L", "W"): -30, ("L", "Y"): -36,
    ("L", "O"): -14, ("D", "A"): -12, ("O", "A"): -12,
    ("T", "o"): -38, ("T", "e"): -38, ("T", "a"): -34, ("T", "c"): -38,
    ("T", "u"): -32, ("T", "w"): -30, ("T", "y"): -30, ("T", "r"): -26,
    ("T", "s"): -30, ("T", "i"): -10, ("T", "-"): -40,
    ("V", "o"): -30, ("V", "a"): -28, ("V", "e"): -30, ("V", "u"): -22,
    ("V", "r"): -22, ("V", "-"): -30,
    ("W", "o"): -20, ("W", "a"): -16, ("W", "e"): -20, ("W", "u"): -14,
    ("Y", "o"): -34, ("Y", "a"): -32, ("Y", "e"): -34, ("Y", "u"): -28,
    ("Y", "p"): -28, ("Y", "v"): -24, ("Y", "-"): -36,
    ("A", "v"): -20, ("A", "w"): -16, ("A", "y"): -20, ("A", "t"): -12,
    ("P", "."): -52, ("P", ","): -52, ("T", "."): -44, ("T", ","): -44,
    ("V", "."): -50, ("V", ","): -50, ("W", "."): -36, ("W", ","): -36,
    ("Y", "."): -50, ("Y", ","): -50, ("F", "."): -42, ("F", ","): -42,
    ("r", "."): -28, ("r", ","): -28, ("v", "."): -30, ("v", ","): -30,
    ("w", "."): -28, ("w", ","): -28, ("y", "."): -30, ("y", ","): -30,
    ("f", "’"): 10, ("f", ")"): 6,
    ("‘", "‘"): -20, ("’", "’"): -20,
    ("o", "v"): -10, ("o", "x"): -10, ("o", "y"): -10,
    ("r", "a"): -10, ("r", "c"): -10, ("r", "d"): -12, ("r", "e"): -10,
    ("r", "g"): -10, ("r", "o"): -10, ("r", "q"): -12,
    ("x", "o"): -10, ("v", "o"): -10, ("y", "o"): -10,
    ("K", "o"): -16, ("K", "e"): -16, ("K", "y"): -18, ("K", "u"): -10,
    ("R", "T"): -12, ("R", "V"): -14, ("R", "W"): -10, ("R", "Y"): -16,
}


def glyph_name(char: str) -> str:
    return agl.UV2AGL.get(ord(char), f"uni{ord(char):04X}")


def _notdef_glyph(fam: Family):
    pen = TTGlyphPen(None)
    w = round(fam.stroke * 0.9)
    pen.moveTo((60, 0))
    pen.lineTo((540, 0))
    pen.lineTo((540, 700))
    pen.lineTo((60, 700))
    pen.closePath()
    # inner rect wound the other way cuts the hole
    pen.moveTo((60 + w, w))
    pen.lineTo((60 + w, 700 - w))
    pen.lineTo((540 - w, 700 - w))
    pen.lineTo((540 - w, w))
    pen.closePath()
    return pen.glyph()


def _tt_glyph(realized: Realized):
    pen = TTGlyphPen(None)
    for op, args in realized.ops:
        getattr(pen, op)(*args)
    return pen.glyph()


def _panose(fam: Family) -> Panose:
    p = Panose()
    p.bFamilyType = 2          # Latin Text
    p.bSerifStyle = 9 if fam.serifs else (15 if fam.key == "friendly" else 11)
    p.bWeight = 10 if fam.weight_class >= 900 else 5
    p.bProportion = 9 if fam.is_mono else 3
    p.bContrast = 2            # monoline: no contrast
    p.bStrokeVariation = 2
    p.bArmStyle = 5
    p.bLetterForm = 2
    p.bMidline = 4
    p.bXHeight = 4
    return p


def compile_family(fam: Family, realized: dict[str, Realized],
                   out_dir: Path) -> tuple[Path, Path]:
    names = {c: glyph_name(c) for c in realized}
    order = [".notdef"] + [names[c] for c in sorted(realized, key=ord)]

    glyf = {".notdef": _notdef_glyph(fam)}
    metrics = {".notdef": (600, 60)}
    for c, r in realized.items():
        glyf[names[c]] = _tt_glyph(r)
        metrics[names[c]] = (r.advance, r.lsb if r.ops else 0)

    y_min = min((r.ymin for r in realized.values() if r.ops), default=0)
    y_max = max((r.ymax for r in realized.values() if r.ops), default=0)
    win_asc = max(y_max, TYPO_ASC)
    win_desc = max(-y_min, -TYPO_DESC)

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    cmap = {ord(c): n for c, n in names.items()}
    cmap[0x00A0] = names[" "]  # NBSP shares the space glyph
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf)
    # lsb must equal the glyph's actual xMin; rounding during outline
    # recording can drift a unit or two, so read it back from glyf.
    for n, (adv, _) in metrics.items():
        g = fb.font["glyf"][n]
        metrics[n] = (adv, g.xMin if g.numberOfContours else 0)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=win_asc, descent=-win_desc)

    ps_name = f"{fam.name.replace(' ', '')}-Regular"
    fb.setupNameTable({
        "familyName": fam.name,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{__version__};ESLP;{ps_name}",
        "fullName": f"{fam.name} Regular",
        "version": f"Version {__version__}",
        "psName": ps_name,
        "copyright": ("Copyright 2026 the Eslop project. "
                      "Drawn from scratch by Claude, an AI, "
                      "with no eyes and considerable optimism."),
        "manufacturer": "Eslop Type Foundry",
        "designer": "Claude (an AI by Anthropic)",
        "description": f"{fam.tagline} Part of Eslop, a five-style family "
                       "designed entirely by a language model. The flaws "
                       "are load-bearing.",
        "licenseDescription": ("This Font Software is licensed under the SIL "
                               "Open Font License, Version 1.1."),
        "licenseInfoURL": "https://openfontlicense.org",
        "sampleText": "Sphinx of black quartz, judge my vow.",
    }, mac=False)

    avg = round(sum(r.advance for r in realized.values()) / len(realized))
    fb.setupOS2(
        version=4,
        sTypoAscender=TYPO_ASC, sTypoDescender=TYPO_DESC,
        sTypoLineGap=TYPO_GAP,
        usWinAscent=win_asc, usWinDescent=win_desc,
        sCapHeight=round(fam.cap), sxHeight=round(fam.xh or 480),
        usWeightClass=fam.weight_class, usWidthClass=5,
        xAvgCharWidth=avg,
        sFamilyClass=0x0501 if fam.serifs else 0x0800,
        panose=_panose(fam),
        fsSelection=0x40 | 0x80,  # REGULAR | USE_TYPO_METRICS
        fsType=0,                 # installable, embeddable, free
        achVendID="ESLP",
        ulUnicodeRange1=(1 << 0) | (1 << 1) | (1 << 31),
        ulCodePageRange1=1 << 0,
    )
    fb.setupPost(isFixedPitch=1 if fam.is_mono else 0)

    font = fb.font
    font["head"].lowestRecPPEM = 6
    # Unhinted TTF: smoothing at all sizes + smart dropout control.
    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x0F}
    font["gasp"] = gasp
    prep = newTable("prep")
    prep.program = ttProgram.Program()
    prep.program.fromAssembly(
        ["PUSHW[]", "511", "SCANCTRL[]", "PUSHB[]", "4", "SCANTYPE[]"])
    font["prep"] = prep

    if fam.kern_scale > 0:
        fea = _kern_feature(names, fam.kern_scale)
        if fea:
            addOpenTypeFeaturesFromString(font, fea)

    out_dir.mkdir(parents=True, exist_ok=True)
    ttf = out_dir / f"{fam.name.replace(' ', '')}-Regular.ttf"
    font.save(ttf)
    font.flavor = "woff2"
    woff2 = ttf.with_suffix(".woff2")
    font.save(woff2)
    return ttf, woff2


def _kern_feature(names: dict[str, str], scale: float) -> str:
    rules = []
    for (a, b), v in KERN_PAIRS.items():
        if a in names and b in names:
            val = round(v * scale)
            if val:
                rules.append(f"pos {names[a]} {names[b]} {val};")
    if not rules:
        return ""
    return ("languagesystem DFLT dflt;\n"
            "languagesystem latn dflt;\n"
            "feature kern {\n  " + "\n  ".join(rules) + "\n} kern;\n")
