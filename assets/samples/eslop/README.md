# Eslop

Five fonts, one transformer, zero supervision.

Eslop is a font family designed entirely by an AI (Claude, by Anthropic):
every glyph skeleton, stroke, serif, kern pair, and questionable optical
decision. It is tongue-in-cheek but genuinely usable — full printable
ASCII plus typographic extras (curly quotes, en/em dashes, ellipsis,
bullet), correct metadata, installable on macOS/Windows/Linux, web-ready
WOFF2.

The flaws are not bugs; they are provenance.

## The family

| Font | Style | Personality |
| --- | --- | --- |
| **Eslop Billboard** | Ultra-black display | Maximum ink, minimum apology. |
| **Eslop Default** | Geometric sans | The one it was going to pick anyway. |
| **Eslop Serious** | Slab serif | For when the stakes feel real. |
| **Eslop Code** | Monospace | Every glyph is equal here. Exactly 600 units equal. |
| **Eslop Friendly** | Comic, dyslexia-friendly | Bottom-heavy on purpose, honest. |

Eslop Friendly borrows the evidence-backed parts of dyslexia-friendly
type design: bottom-weighted strokes, wide letter and word spacing, a
large x-height, a flagged-and-footed 1 distinct from l and I, and —
because every glyph is wobbled by its own fixed random seed — b/d/p/q
are not mirror images of each other.

## Install

Double-click a `.ttf`, click install. For the web, use the `.woff2`
files and the `@font-face` blocks in `specimen.html`.

## License

SIL Open Font License 1.1 (see `OFL.txt`). Free for any use, including
commercial; embedding allowed (`fsType 0`).

## Provenance

Built programmatically with fontTools + skia-pathops from centerline
skeletons authored in a 1000 UPM reference space; one shared skeleton
library is re-rendered through five parameter sets (weight, metric
remapping, auto-slab serifs, monospace fitting, seeded wobble). Source
lives in `src/eslop/` of this repository. Rebuild everything with:

```sh
uv run python -m eslop.build
```
