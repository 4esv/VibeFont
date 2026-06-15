"""Per-family glyph overrides: (family_key, char) -> glyph definition."""

import copy

from eslop.skeleton import arc, bar, chain, dot, glyph, pline, ring, stem
from eslop.skeletons.lower import GLYPHS as _lower
from eslop.skeletons.symbols import GLYPHS as _symbols
from eslop.skeletons.upper import GLYPHS as _upper


def thinner(gdef, w):
    """Same skeleton, lighter strokes (counters clog at heavy weights)."""
    g = copy.deepcopy(gdef)
    for s in g["strokes"]:
        if "cmds" in s:
            s["w"] = w
    return g


VARIANTS = {}

# Billboard: symbol-tier glyphs whose counters can't survive stroke 160
VARIANTS[("billboard", "@")] = thinner(_symbols["@"], 0.70)
VARIANTS[("billboard", "%")] = thinner(_symbols["%"], 0.70)
VARIANTS[("billboard", "&")] = thinner(_symbols["&"], 0.85)
VARIANTS[("billboard", "*")] = thinner(_symbols["*"], 0.72)

# Code: narrow letters get tails/serifs so they don't swim in the cell,
# the zero gets a dot, and the densest glyphs get lighter strokes.
VARIANTS[("code", "i")] = glyph(
    stem(160, 40, 440), dot(160, 570),
    bar(40, 60, 260), pline((60, 440), (160, 440)),
    space=("straight", "straight"))

VARIANTS[("code", "l")] = glyph(
    chain(pline((100, 680), (100, 160)), arc(220, 160, 120, 132, 180, 300)),
    space=("straight", "straight"))

VARIANTS[("code", "I")] = glyph(
    stem(160, 40, 660), bar(660, 60, 260), bar(40, 60, 260),
    space=("straight", "straight"))

VARIANTS[("code", "0")] = glyph(
    ring(250, 350, 210, 322), dot(250, 350, 60),
    space=("round", "round"))

VARIANTS[("code", "@")] = thinner(_symbols["@"], 0.72)
VARIANTS[("code", "a")] = thinner(_lower["a"], 0.90)

# Friendly: bottom-weight + wobble eat counters in the densest glyphs,
# and the dyslexia brief wants l distinct from I.
VARIANTS[("friendly", "B")] = thinner(_upper["B"], 0.88)
VARIANTS[("friendly", "a")] = thinner(_lower["a"], 0.90)
VARIANTS[("friendly", "g")] = thinner(_lower["g"], 0.90)
VARIANTS[("friendly", "@")] = thinner(_symbols["@"], 0.75)
VARIANTS[("friendly", "%")] = thinner(_symbols["%"], 0.90)
VARIANTS[("friendly", "l")] = glyph(
    chain(pline((100, 680), (100, 160)), arc(220, 160, 120, 132, 180, 300)),
    space=("straight", "open"))
