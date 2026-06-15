"""Symbol skeletons: math, commercial, and the weird keyboard residents."""

from eslop.skeleton import (arc, bar, chain, dot, glyph, pline, ring, stem,
                            stroke)

GLYPHS = {}

GLYPHS["@"] = glyph(
    ring(300, 220, 270, 300),
    ring(315, 272, 78, 86),
    chain(pline((400, 352), (400, 178)), arc(468, 178, 68, 68, 180, 300)),
    lsb=24, rsb=24)

GLYPHS["#"] = glyph(
    pline((150, 560), (110, 120)), pline((330, 560), (290, 120)),
    bar(450, 40, 400), bar(230, 40, 400),
    lsb=24, rsb=24)

GLYPHS["$"] = glyph(
    chain(arc(245, 505, 205, 167, 35, 270),
          arc(245, 183, 215, 155, 90, -145)),
    pline((245, 710), (245, -10)),
    space=("round", "round"))

GLYPHS["%"] = glyph(
    ring(150, 555, 108, 112),
    ring(420, 145, 108, 112),
    pline((60, 40), (500, 660)),
    lsb=20, rsb=20)

GLYPHS["&"] = glyph(
    ring(200, 510, 115, 140),
    ring(215, 205, 175, 177),
    pline((180, 360), (540, 40)),
    lsb=20, rsb=14)

GLYPHS["*"] = glyph(
    pline((180, 370), (180, 670)),
    pline((50, 445), (310, 595)),
    pline((310, 445), (50, 595)),
    lsb=28, rsb=28)

GLYPHS["+"] = glyph(
    bar(290, 40, 360), pline((200, 130), (200, 450)),
    lsb=36, rsb=36)

GLYPHS["="] = glyph(
    bar(425, 40, 360), bar(165, 40, 360),
    lsb=36, rsb=36)

GLYPHS["<"] = glyph(
    pline((360, 540), (40, 290), (360, 40)),
    lsb=36, rsb=36)

GLYPHS[">"] = glyph(
    pline((40, 540), (360, 290), (40, 40)),
    lsb=36, rsb=36)

GLYPHS["~"] = glyph(
    [("M", 40, 260), ("C", 110, 370, 190, 370, 230, 295),
     ("C", 270, 220, 350, 220, 420, 330)],
    lsb=34, rsb=34)

GLYPHS["^"] = glyph(
    pline((40, 440), (180, 680), (320, 440)),
    lsb=30, rsb=30)

GLYPHS["`"] = glyph(
    stroke(pline((40, 680), (150, 555)), w=0.9),
    lsb=30, rsb=30)
