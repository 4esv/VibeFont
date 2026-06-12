---
name: make-font
description: Build an installable TTF from a glyph sample-sheet image with the vibefont pipeline. Use when the user wants to make a font, trace a drawing or sample sheet into a font, fix segmentation errors, or review proof output.
---

# Make a font from a sample sheet

## Workflow

1. Confirm the sample image follows the sheet conventions below. If not, fix the image first — the pipeline has no tolerance modes.
2. Run the pipeline:
   ```sh
   uv run vibefont <image> --line <row1> --line <row2> ... [--family "Name"]
   ```
   One `--line` per text row, in top-to-bottom order, text exactly as drawn.
3. Read all three outputs in `assets/output/` (use the Read tool — they are images):
   - `font-sample-comparison.png` — original sheet above, font re-rendering below. Traced glyphs should be near-identical; differences here mean tracing or metrics problems.
   - `proof.png` — full A–Z a–z `.,-` typed with the font's own metrics. This is where derived-glyph and spacing problems show.
   - `<Family>-Regular.ttf` — the installable font.
4. Report what was traced vs derived (the CLI prints counts) and what looks off in the proof. Iterate with the **glyph-recipes** skill for derived-letter fixes.

## Sample sheet conventions

`segment.py` finds glyphs by these rules — violations fail loudly:

- **Ink is near-black**: every RGB channel < 128. Anything where at least one channel stays bright (light gray grid, saturated guide colors) is treated as not-ink.
- **Guides are light or colored**: baselines, grids, and zone strips must keep `max(R,G,B) >= 128`. A colored baseline guide (channel spread > 80) spanning ≥ ⅓ of the row width is used as the row's baseline; otherwise the median glyph bottom is.
- **Rows are separated by fully ink-free horizontal bands.** Descenders from one row must not overlap the next row's ascenders.
- **Glyphs within a row are separated by fully ink-free vertical gaps.** No touching or kerned-together letters.
- Specks under 400 px² of ink are ignored; dots on i/j must exceed that or sit within the letter's horizontal span.

Coverage: the `hambu rgevons HAMBU RGEVONS` sheet ("hamburgevons") carries every structural part — stems/serifs (h n u), bowls (o b), arches (n h), diagonals (v V A), arms/bars (r e E), tails (g R). Letters not on the sheet are derived by recipes in `src/vibefont/recipes.py`. A sample with more letters needs fewer recipes; a sample with fewer needs more.

## Failure modes

- `found N text rows, expected M` — row count mismatch: a descender bridges two rows, or a guide line is dark enough to read as ink. Check the image at the reported y range.
- `row y0-y1: found N glyphs, expected '...'` — glyph count mismatch in that row: letters touch (merge), or a glyph broke into pieces (split — common with disconnected i/j dots below the area threshold). The `--line` text must match the drawn glyphs one-to-one.
- Glyph looks filled/inverted in the proof — winding/overlap issue; `build_font` runs `removeOverlaps`, so this usually traces back to stray ink in the source crop.
- Derived letter looks wrong — recipe constants are tuned to the reference sample's proportions (cap 530 px, x-height 339 px). A new sample at different proportions needs recipe adjustment: see the **glyph-recipes** skill.

## Verifying the font file

```sh
uv run python -c "from fontTools.ttLib import TTFont; f = TTFont('assets/output/<Family>-Regular.ttf'); print(sorted(chr(c) for c in f.getBestCmap()))"
```

`uv run pytest` runs the end-to-end pipeline test against the reference sample plus toolchain smoke tests.
