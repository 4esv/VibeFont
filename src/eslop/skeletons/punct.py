"""Punctuation skeletons: marks, quotes, brackets, dashes."""

from eslop.skeleton import (arc, bar, chain, dot, glyph, pline, stem, stroke)

GLYPHS = {}

GLYPHS["."] = glyph(dot(58, 58, 58), lsb=30, rsb=30)

GLYPHS[","] = glyph(
    dot(58, 70, 55),
    stroke(pline((75, 50), (30, -80)), w=0.8),
    lsb=30, rsb=30)

GLYPHS[":"] = glyph(dot(58, 58, 58), dot(58, 382, 58), lsb=30, rsb=30)

GLYPHS[";"] = glyph(
    dot(58, 70, 55), dot(58, 382, 58),
    stroke(pline((75, 50), (30, -80)), w=0.8),
    lsb=30, rsb=30)

GLYPHS["!"] = glyph(
    stem(40, 280, 660), dot(40, 70, 58),
    lsb=34, rsb=34)

GLYPHS["?"] = glyph(
    chain(arc(190, 490, 150, 182, 180, 0),
          [("M", 340, 490), ("C", 340, 400, 280, 380, 230, 350)],
          pline((230, 350), (210, 280))),
    dot(204, 70, 58),
    lsb=24, rsb=24)

GLYPHS["'"] = glyph(stem(40, 530, 672), lsb=26, rsb=26)

GLYPHS['"'] = glyph(stem(40, 530, 672), stem(240, 530, 672),
                    lsb=26, rsb=26)

GLYPHS["-"] = glyph(bar(290, 40, 280), lsb=30, rsb=30)

GLYPHS["–"] = glyph(bar(290, 40, 440), lsb=26, rsb=26)   # en dash

GLYPHS["—"] = glyph(bar(290, 40, 840), lsb=22, rsb=22)   # em dash

GLYPHS["_"] = glyph(bar(-80, 40, 520), lsb=10, rsb=10)

GLYPHS["("] = glyph(arc(290, 250, 170, 430, 105, 255), lsb=28, rsb=12)

GLYPHS[")"] = glyph(arc(80, 250, 170, 430, 75, -75), lsb=12, rsb=28)

GLYPHS["["] = glyph(
    pline((220, 680), (60, 680), (60, -160), (220, -160)),
    lsb=28, rsb=12)

GLYPHS["]"] = glyph(
    pline((60, 680), (220, 680), (220, -160), (60, -160)),
    lsb=12, rsb=28)

GLYPHS["{"] = glyph(
    chain(arc(260, 572, 120, 108, 90, 180),
          pline((140, 572), (140, 330)),
          arc(40, 330, 100, 70, 0, -90),
          arc(40, 190, 100, 70, 90, 0),
          pline((140, 190), (140, -52)),
          arc(260, -52, 120, 108, 180, 270)),
    lsb=24, rsb=16)

GLYPHS["}"] = glyph(
    chain(arc(40, 572, 120, 108, 90, 0),
          pline((160, 572), (160, 330)),
          arc(260, 330, 100, 70, 180, 270),
          arc(260, 190, 100, 70, 90, 180),
          pline((160, 190), (160, -52)),
          arc(40, -52, 120, 108, 0, -90)),
    lsb=16, rsb=24)

GLYPHS["/"] = glyph(pline((40, -140), (340, 700)), lsb=10, rsb=10)

GLYPHS["\\"] = glyph(pline((40, 700), (340, -140)), lsb=10, rsb=10)

GLYPHS["|"] = glyph(stem(40, -140, 700), lsb=40, rsb=40)

# curly quotes: a dot with a little tail, comma-shaped
GLYPHS["‘"] = glyph(                                     # ‘
    dot(54, 560, 50),
    stroke(pline((40, 582), (84, 690)), w=0.8),
    lsb=26, rsb=26)

GLYPHS["’"] = glyph(                                     # ’
    dot(50, 660, 50),
    stroke(pline((66, 638), (22, 530)), w=0.8),
    lsb=26, rsb=26)

GLYPHS["“"] = glyph(                                     # “
    dot(54, 560, 50), stroke(pline((40, 582), (84, 690)), w=0.8),
    dot(284, 560, 50), stroke(pline((270, 582), (314, 690)), w=0.8),
    lsb=26, rsb=26)

GLYPHS["”"] = glyph(                                     # ”
    dot(50, 660, 50), stroke(pline((66, 638), (22, 530)), w=0.8),
    dot(280, 660, 50), stroke(pline((296, 638), (252, 530)), w=0.8),
    lsb=26, rsb=26)

GLYPHS["…"] = glyph(                                     # …
    dot(48, 58, 48), dot(258, 58, 48), dot(468, 58, 48),
    lsb=30, rsb=30)

GLYPHS["•"] = glyph(dot(120, 280, 110), lsb=40, rsb=40)  # •
