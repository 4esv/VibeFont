"""Uppercase A-Z skeletons.

Conventions: centerlines, ref stroke 80. Flat cap tops at 660, round at
672; baseline 40/28. Leftmost centerline 40. Target outline widths:
narrow (E F L 440-460), medium (H N U T 520-540), round (O Q 600),
wide (M 640, W 660+).
"""

from eslop.skeleton import (arc, bar, chain, glyph, pline, ring, stem,
                            stroke)

GLYPHS = {}

GLYPHS["A"] = glyph(
    pline((40, 40), (280, 660), (520, 40)),
    bar(220, 148, 412),
    space=("diag", "diag"))

GLYPHS["B"] = glyph(
    stem(40),
    chain(pline((40, 660), (230, 660)), arc(230, 536, 170, 124, 90, -90),
          pline((230, 412), (40, 412))),
    chain(pline((40, 412), (250, 412)), arc(250, 226, 195, 186, 90, -90),
          pline((250, 40), (40, 40))),
    space=("straight", "round"))

GLYPHS["C"] = glyph(
    arc(315, 350, 275, 322, 45, 315),
    space=("round", "open"))

GLYPHS["D"] = glyph(
    stem(40),
    chain(pline((40, 660), (250, 660)), arc(250, 350, 270, 310, 90, -90),
          pline((250, 40), (40, 40))),
    space=("straight", "round"))

GLYPHS["E"] = glyph(
    stem(40),
    bar(660, 40, 420), bar(350, 40, 390), bar(40, 40, 420),
    space=("straight", "open"))

GLYPHS["F"] = glyph(
    stem(40),
    bar(660, 40, 420), bar(350, 40, 380),
    space=("straight", "open"))

GLYPHS["G"] = glyph(
    arc(315, 350, 275, 322, 48, 318),
    pline((520, 300), (520, 118)),
    bar(300, 330, 520),
    space=("round", "straight"))

GLYPHS["H"] = glyph(
    stem(40), stem(500), bar(350, 40, 500),
    space=("straight", "straight"))

GLYPHS["I"] = glyph(stem(40), space=("straight", "straight"))

GLYPHS["J"] = glyph(
    chain(pline((280, 660), (280, 160)), arc(160, 160, 120, 132, 0, -180)),
    space=("open", "straight"))

GLYPHS["K"] = glyph(
    stem(40),
    pline((40, 330), (460, 660)),
    pline((150, 416), (500, 40)),
    space=("straight", "diag"))

GLYPHS["L"] = glyph(
    stem(40), bar(40, 40, 420),
    space=("straight", "open"))

GLYPHS["M"] = glyph(
    stem(40), stem(600),
    stroke(pline((40, 660), (320, 120)), serif_end="none"),
    stroke(pline((600, 660), (320, 120)), serif_end="none"),
    space=("straight", "straight"))

GLYPHS["N"] = glyph(
    stem(40), stem(480),
    pline((40, 660), (480, 40)),
    space=("straight", "straight"))

GLYPHS["O"] = glyph(
    ring(300, 350, 260, 322),
    space=("round", "round"))

GLYPHS["P"] = glyph(
    stem(40),
    chain(pline((40, 660), (245, 660)), arc(245, 485, 185, 175, 90, -90),
          pline((245, 310), (40, 310))),
    space=("straight", "round"))

GLYPHS["Q"] = glyph(
    ring(300, 350, 260, 322),
    pline((400, 140), (560, -60)),
    space=("round", "round"))

GLYPHS["R"] = glyph(
    stem(40),
    chain(pline((40, 660), (245, 660)), arc(245, 485, 185, 175, 90, -90),
          pline((245, 310), (40, 310))),
    pline((230, 310), (480, 40)),
    space=("straight", "diag"))

GLYPHS["S"] = glyph(
    chain(arc(245, 505, 205, 167, 35, 270),
          arc(245, 183, 215, 155, 90, -145)),
    space=("round", "round"))

GLYPHS["T"] = glyph(
    bar(660, 40, 480), stem(260, 40, 660),
    space=("open", "open"))

GLYPHS["U"] = glyph(
    chain(pline((40, 660), (40, 240)), arc(260, 240, 220, 212, 180, 360),
          pline((480, 240), (480, 660))),
    space=("straight", "straight"))

GLYPHS["V"] = glyph(
    pline((40, 660), (280, 40), (520, 660)),
    space=("diag", "diag"))

GLYPHS["W"] = glyph(
    pline((40, 660), (190, 40), (330, 560), (470, 40), (620, 660)),
    space=("diag", "diag"))

GLYPHS["X"] = glyph(
    pline((40, 660), (480, 40)), pline((480, 660), (40, 40)),
    space=("diag", "diag"))

GLYPHS["Y"] = glyph(
    pline((40, 660), (260, 370)), pline((480, 660), (260, 370)),
    stem(260, 40, 370),
    space=("diag", "diag"))

GLYPHS["Z"] = glyph(
    pline((40, 660), (440, 660), (40, 40), (440, 40)),
    space=("open", "open"))
