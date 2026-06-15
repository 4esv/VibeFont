"""Lowercase a-z skeletons.

x-height flat tops at 440, round at 452; ascenders 680 (t stops at 580);
descenders -180 flat, -192 round. Double-storey a, single-storey g —
distinct silhouettes for b/d/p/q matter to the dyslexia-friendly family.
"""

from eslop.skeleton import (arc, bar, chain, dot, glyph, pline, ring, stem,
                            stroke)

GLYPHS = {}

GLYPHS["a"] = glyph(
    stem(380, 40, 440),
    arc(222, 330, 158, 122, 0, 165),
    ring(222, 172, 162, 146),
    space=("round", "straight"))

GLYPHS["b"] = glyph(
    stem(40, 40, 680),
    ring(250, 240, 210, 212),
    space=("straight", "round"))

GLYPHS["c"] = glyph(
    arc(250, 240, 210, 212, 45, 315),
    space=("round", "open"))

GLYPHS["d"] = glyph(
    stem(460, 40, 680),
    ring(250, 240, 210, 212),
    space=("round", "straight"))

GLYPHS["e"] = glyph(
    arc(240, 240, 200, 212, 8, 320),
    bar(270, 42, 438),
    space=("round", "open"))

GLYPHS["f"] = glyph(
    chain(pline((120, 40), (120, 560)), arc(240, 560, 120, 120, 180, 90)),
    bar(440, 40, 280),
    space=("straight", "open"))

GLYPHS["g"] = glyph(
    ring(250, 240, 210, 212),
    pline((460, 440), (460, -40)),
    arc(310, -40, 150, 152, 0, -180),
    space=("round", "straight"))

GLYPHS["h"] = glyph(
    stem(40, 40, 680),
    chain(arc(200, 290, 160, 162, 180, 0), pline((360, 290), (360, 40))),
    space=("straight", "straight"))

GLYPHS["i"] = glyph(
    stem(40, 40, 440), dot(40, 570),
    space=("straight", "straight"))

GLYPHS["j"] = glyph(
    chain(pline((100, 440), (100, -60)), arc(-10, -60, 110, 132, 0, -180)),
    dot(100, 570),
    lsb=-40, rsb=30)

GLYPHS["k"] = glyph(
    stem(40, 40, 680),
    pline((40, 260), (330, 440)),
    pline((130, 316), (360, 40)),
    space=("straight", "diag"))

GLYPHS["l"] = glyph(stem(40, 40, 680), space=("straight", "straight"))

GLYPHS["m"] = glyph(
    stem(40, 40, 440),
    chain(arc(160, 310, 120, 142, 180, 0), pline((280, 310), (280, 40))),
    chain(arc(400, 310, 120, 142, 180, 0), pline((520, 310), (520, 40))),
    space=("straight", "straight"))

GLYPHS["n"] = glyph(
    stem(40, 40, 440),
    chain(arc(200, 290, 160, 162, 180, 0), pline((360, 290), (360, 40))),
    space=("straight", "straight"))

GLYPHS["o"] = glyph(
    ring(240, 240, 200, 212),
    space=("round", "round"))

GLYPHS["p"] = glyph(
    pline((40, 440), (40, -180)),
    ring(250, 240, 210, 212),
    space=("straight", "round"))

GLYPHS["q"] = glyph(
    pline((460, 440), (460, -180)),
    ring(250, 240, 210, 212),
    space=("round", "straight"))

GLYPHS["r"] = glyph(
    stem(40, 40, 440),
    arc(160, 320, 120, 132, 180, 30),
    space=("straight", "open"))

GLYPHS["s"] = glyph(
    chain(arc(190, 355, 150, 97, 35, 270),
          arc(190, 143, 158, 115, 90, -145)),
    space=("round", "round"))

GLYPHS["t"] = glyph(
    chain(pline((140, 580), (140, 160)), arc(260, 160, 120, 132, 180, 310)),
    bar(440, 40, 280),
    space=("straight", "open"))

GLYPHS["u"] = glyph(
    chain(pline((40, 440), (40, 202)), arc(200, 202, 160, 174, 180, 360)),
    pline((360, 440), (360, 40)),
    space=("straight", "straight"))

GLYPHS["v"] = glyph(
    pline((40, 440), (200, 40), (360, 440)),
    space=("diag", "diag"))

GLYPHS["w"] = glyph(
    pline((40, 440), (150, 40), (260, 360), (370, 40), (480, 440)),
    space=("diag", "diag"))

GLYPHS["x"] = glyph(
    pline((40, 440), (360, 40)), pline((360, 440), (40, 40)),
    space=("diag", "diag"))

GLYPHS["y"] = glyph(
    pline((40, 440), (212, 52)),
    pline((400, 440), (150, -124)),
    space=("diag", "diag"))

GLYPHS["z"] = glyph(
    pline((40, 440), (360, 440), (40, 40), (360, 40)),
    space=("open", "open"))
