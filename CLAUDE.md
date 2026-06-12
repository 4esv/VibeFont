# VibeFont

Builds installable TTFs from drawn sample-sheet images: segment → trace
(potrace) → derive missing letters from traced parts → compile (fonttools).

## Commands

```sh
uv sync          # install (uv manages Python >= 3.12)
uv run pytest    # toolchain smoke tests + end-to-end pipeline test
uv run vibefont assets/input/font-sample.png \
  --line hambu --line rgevons --line HAMBU --line RGEVONS
```

Outputs go to `assets/output/` (gitignored); curated results are tracked in
`assets/samples/`.

## Skills

- `make-font` — run the pipeline, read proofs, diagnose segmentation failures.
- `glyph-recipes` — write/tune the per-letter derivation recipes in
  `src/vibefont/recipes.py`.

After any recipe or pipeline change: rebuild, then **Read the output images**
(`proof.png`, `font-sample-comparison.png`) and judge the letterforms —
passing tests prove the font compiles, not that it looks right.
