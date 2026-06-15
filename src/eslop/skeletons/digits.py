"""Digit 0-9 skeletons. Lining figures at cap height. The 1 gets a flag
and a foot bar so it can never be confused with l or I."""

from eslop.skeleton import arc, bar, chain, glyph, pline, ring, stem

GLYPHS = {}

GLYPHS["0"] = glyph(
    ring(240, 350, 200, 322),
    space=("round", "round"))

GLYPHS["1"] = glyph(
    pline((60, 550), (180, 670), (180, 40)),
    bar(40, 60, 300),
    space=("open", "open"))

GLYPHS["2"] = glyph(
    chain(arc(240, 520, 180, 152, 160, 0),
          pline((420, 520), (40, 40), (440, 40))),
    space=("round", "open"))

GLYPHS["3"] = glyph(
    chain(arc(230, 505, 175, 167, 140, -90),
          arc(230, 183, 205, 155, 90, -130)),
    space=("open", "round"))

GLYPHS["4"] = glyph(
    pline((320, 660), (60, 200), (480, 200)),
    pline((320, 460), (320, 40)),
    space=("diag", "open"))

GLYPHS["5"] = glyph(
    chain(pline((400, 660), (100, 660), (90, 379)),
          arc(230, 235, 195, 207, 136, -140)),
    space=("open", "round"))

GLYPHS["6"] = glyph(
    arc(330, 390, 280, 282, 95, 200),
    ring(255, 225, 205, 197),
    space=("round", "round"))

GLYPHS["7"] = glyph(
    pline((40, 660), (440, 660), (160, 40)),
    space=("open", "diag"))

GLYPHS["8"] = glyph(
    ring(245, 500, 165, 172),
    ring(245, 190, 200, 162),
    space=("round", "round"))

GLYPHS["9"] = glyph(
    arc(170, 310, 280, 282, 275, 380),
    ring(245, 475, 205, 197),
    space=("round", "round"))
