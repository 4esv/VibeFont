---
name: glyph-recipes
description: Write or tune derivation recipes in src/vibefont/recipes.py — the functions that assemble letters missing from the sample sheet out of traced parts. Use when a derived glyph looks wrong in the proof, when adding coverage for new characters, or when adapting recipes to a new sample's proportions.
---

# Glyph derivation recipes

A recipe builds one missing letter as a pixel bitmap from parts cut out of the traced sample, then the pipeline retraces it like a genuine glyph — retracing merges paste seams into clean outlines. Recipes live in `src/vibefont/recipes.py`; the toolkit is `src/vibefont/derive.py`.

## Coordinate system — read this first

Recipe coordinates are **image pixels**, x rightward from the glyph's own left edge, **y UP from the baseline** (unlike image rows). Negative y is below the baseline (descenders). The reference sample measures: cap height 530, x-height 339, lowercase stem 55, capital stem 64. Recipes written against one sample's pixel grid do not transfer to another sample unscaled — re-measure via `Metrics` and scale.

## Toolkit

```python
m: Metrics   # m.xh, m.cap, m.asc, m.desc (positive depth), m.stem, m.cstem
p: Parts     # cuts pieces out of the traced sheet

p.cut(ch, x0=0, x1=None, y0=None, y1=None)  # -> Piece; x relative to glyph
                                            #    left, y relative to baseline
piece.flip_h() / .flip_v() / .rot180()
piece.scaled(sx, sy=None)                   # LANCZOS resize, keeps baseline
piece.vstretch(new_height, keep=70, anchor="bottom")
    # 3-slice resize: top/bottom `keep` rows stay intact (serifs, joins),
    # only the straight middle stretches. anchor names the fixed end.

g = Glyph(m, width)                         # blank canvas, baseline placed
g.paste(piece, x, dy=0)                     # OR ink onto canvas
g.erase(x0, y0, x1, y1)                     # clear a rect
g.fill_poly([(x, y), ...]) / g.erase_poly(...)
g.fill_ellipse(cx, cy, rx, ry=None)         # dots, ball terminals
return g                                    # recipe returns the Glyph
```

Register the recipe in the `RECIPES` dict at the bottom of `recipes.py`, and add the character to `FULL_SET` in `cli.py` if it isn't covered there.

## Craft rules (learned the hard way — see existing recipes)

- **Cut serif slabs shallow.** A tall cut drags along offset fragments of neighboring strokes that ride every later transform. Cut just the slab (`lc_x`, `cap_X`).
- **Cut below head flags before `vstretch`**, or the flag smears through the stretched middle (`lc_t`, `lc_f`).
- **Don't rotate serifed strokes.** Rotating v to make k's leg scrambles its serifs into a bar — draw diagonals with `fill_poly` and dress them with pasted serifs and feet (`lc_k`, `lc_x`, `cap_X`).
- **Overlap joins generously.** Run strokes into the serif slab or stem so the seam can't pinch or notch; retracing merges the overlap (`cap_K` arm, `cap_D` bridges).
- **Mind overshoot.** Round parts (O, o) extend past the flat extremes; trim when pasting against flat strokes (`cap_D`).
- **Prefer solid-apex parts at junctions.** Y uses lowercase v scaled up, not V cropped, because v's apex is a solid point that lands on the stem without a gap (`cap_Y`).
- Scale E-derived bars by `m.xh / m.cap` when reusing capital arms in lowercase (`lc_z`).

## Iteration loop

1. Edit the recipe.
2. Rebuild: `uv run vibefont assets/input/font-sample.png --line hambu --line rgevons --line HAMBU --line RGEVONS`
3. Read `assets/output/proof.png` and compare the glyph against its traced neighbors: weight, serif shapes, alignment at baseline/x-height/cap, sidebearings.
4. Repeat. Two or three rounds per glyph is normal; these are design decisions, not derivations.

Judge against the letterform logic of the source design: stroke contrast and weight must match the traced letters, serifs must match their nearest structural relative, and curves should come from real bowls or arcs in the sample — drawn polygons are for straight diagonals only.
