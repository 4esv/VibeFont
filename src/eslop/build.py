"""Build the Eslop families: TTF + WOFF2 + proof sheets.

    uv run python -m eslop.build [--family KEY ...] [--out DIR]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from eslop import compile as comp
from eslop.proof import render_overview, render_proof
from eslop.skeletons import EXPECTED, GLYPHS, VARIANTS
from eslop.specimen import write_specimen
from eslop.styles import BUILD_ORDER, FAMILIES, realize


def build_family(key: str, out_dir: Path) -> Path:
    fam = FAMILIES[key]
    realized = {}
    for char, gdef in GLYPHS.items():
        gdef = VARIANTS.get((key, char), gdef)
        realized[char] = realize(fam, char, gdef)
    ttf, _ = comp.compile_family(fam, realized, out_dir / "fonts")
    return ttf


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--family", action="append", choices=BUILD_ORDER)
    ap.add_argument("--out", type=Path, default=Path("assets/output/eslop"))
    ap.add_argument("--no-proof", action="store_true")
    args = ap.parse_args(argv)

    missing = sorted(set(EXPECTED) - set(GLYPHS))
    if missing:
        print(f"MISSING {len(missing)} glyphs: {''.join(missing)}")

    charset = "".join(sorted(GLYPHS, key=ord))
    built: list[tuple[str, Path]] = []
    for key in args.family or BUILD_ORDER:
        fam = FAMILIES[key]
        ttf = build_family(key, args.out)
        built.append((fam.name, ttf))
        if not args.no_proof:
            render_proof(ttf, f"{fam.name} — {fam.tagline}", charset,
                         args.out / "proofs" / f"{key}.png")
        print(f"built {ttf}")

    if not args.no_proof and len(built) > 1:
        render_overview(built, args.out / "proofs" / "overview.png")
        print(f"overview {args.out / 'proofs' / 'overview.png'}")

    if set(args.family or BUILD_ORDER) == set(BUILD_ORDER):
        write_specimen(args.out / "fonts" / "specimen.html")
        print(f"specimen {args.out / 'fonts' / 'specimen.html'}")


if __name__ == "__main__":
    main()
