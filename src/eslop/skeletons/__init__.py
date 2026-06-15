"""The shared skeleton library: every glyph, authored once as centerline
strokes in the reference space (see eslop.skeleton docstring)."""

from eslop.skeleton import glyph
from eslop.skeletons.digits import GLYPHS as _digits
from eslop.skeletons.lower import GLYPHS as _lower
from eslop.skeletons.punct import GLYPHS as _punct
from eslop.skeletons.symbols import GLYPHS as _symbols
from eslop.skeletons.upper import GLYPHS as _upper

GLYPHS = {" ": glyph()} | _upper | _lower | _digits | _punct | _symbols

# Slab serifs belong to letters; on punctuation and symbols the auto-serif
# detector decorates quote tails and # stems with little tables.
for _g in (*_punct.values(), *_symbols.values()):
    _g["serifs"] = False
_digits["7"]["strokes"][0]["serif_end"] = "none"   # no slab on the 7's toe
_digits["4"]["strokes"][1]["serif_start"] = "none"  # stem top floats mid-air

from eslop.skeletons.variants import VARIANTS  # noqa: E402

# full printable ASCII plus the typographic extras a website wants
EXPECTED = "".join(chr(c) for c in range(0x20, 0x7F)) + "–—‘’“”…•"
