# VibeFont
Computer, make font.

Builds fonts from images + descriptions. Glyph images go in, traced vector
outlines come out, [fonttools](https://github.com/fonttools/fonttools)
compiles them into a working TTF/OTF.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python ≥ 3.12.

```sh
uv sync
uv run pytest   # toolchain smoke tests
uv run vibefont # CLI stub
```

## Pipeline

```
image ──► rasterize (Pillow) ──► trace (potrace) ──► fit to UPM ──► glyphs (fonttools pens) ──► TTF
                                                          ▲
description ──► glyph set, metrics, naming ───────────────┘
```

Nothing past the smoke tests is implemented yet.

## Layout

```
src/vibefont/   package + CLI entry point
tests/          toolchain smoke tests
assets/input/   source glyph images
assets/output/  built fonts (gitignored)
```

## Toolchain

| dep          | role                                        |
|--------------|---------------------------------------------|
| fonttools    | font compilation, pens, UFO, woff, unicode  |
| skia-pathops | overlap removal / path booleans             |
| potracer     | bitmap → vector tracing (pure Python)       |
| Pillow       | image loading + rasterization               |
| numpy        | bitmap buffers between Pillow and potrace   |
