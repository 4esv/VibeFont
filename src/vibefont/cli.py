"""Command-line entry point: image + text lines -> TTF + comparison sheet."""

import argparse
import statistics
import string
import sys
from pathlib import Path

from vibefont import __version__
from vibefont.build import build_font
from vibefont.recipes import derive_missing
from vibefont.render import comparison_sheet, proof_sheet, render_recreation
from vibefont.segment import segment
from vibefont.trace import trace_glyph

FULL_SET = string.ascii_letters + ".,-"
PROOF_LINES = [
    "ABCDEFGHIJKLM",
    "NOPQRSTUVWXYZ",
    "abcdefghijklm",
    "nopqrstuvwxyz .,-",
    "The quick brown fox",
    "jumps over the lazy dog.",
]

CAP_HEIGHT = 700  # font units the measured cap height maps to
X_HEIGHT_FALLBACK = 470  # used when the sample has no capitals
# TODO: derive per-glyph sidebearings (round vs flat) instead of a constant.
SIDEBEARING = 60

# Lowercase letters whose top sits at the x-height line.
X_HEIGHT_CHARS = set("aceimnorsuvwxz")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="vibefont",
        description="Trace a glyph sample sheet into a working TTF.")
    parser.add_argument("image", type=Path, help="sample sheet image")
    parser.add_argument("--line", action="append", required=True,
                        dest="lines", metavar="TEXT",
                        help="text of one sheet row (repeat per row)")
    parser.add_argument("--family", default="Vibe Serif")
    parser.add_argument("--out-dir", type=Path, default=Path("assets/output"))
    parser.add_argument("--version", action="version",
                        version=f"vibefont {__version__}")
    args = parser.parse_args()

    sheet = segment(args.image, args.lines)

    cap_px = [b.baseline - b.top for b in sheet.boxes if b.char.isupper()]
    x_px = [b.baseline - b.top for b in sheet.boxes
            if b.char in X_HEIGHT_CHARS]
    if cap_px:
        scale = CAP_HEIGHT / statistics.median(cap_px)
    else:
        scale = X_HEIGHT_FALLBACK / statistics.median(x_px)
    x_height = round(statistics.median(x_px) * scale) if x_px else 0

    seen = set()
    outlines = []
    for box in sheet.boxes:
        if box.char in seen:
            continue
        seen.add(box.char)
        outlines.append(trace_glyph(sheet.ink, box, scale,
                                    SIDEBEARING, SIDEBEARING))
    traced = len(outlines)

    missing = [c for c in FULL_SET if c not in seen]
    for ink, box in derive_missing(sheet, missing):
        outlines.append(trace_glyph(ink, box, scale,
                                    SIDEBEARING, SIDEBEARING))

    slug = args.family.replace(" ", "")
    ttf = args.out_dir / f"{slug}-Regular.ttf"
    build_font(outlines, args.family, CAP_HEIGHT, x_height, ttf)

    recreation = render_recreation(sheet, ttf, scale, SIDEBEARING,
                                   args.out_dir / "font-sample-recreated.png")
    comparison_sheet(args.image, recreation,
                     args.out_dir / "font-sample-comparison.png")
    proof_sheet(ttf, PROOF_LINES, args.out_dir / "proof.png")

    print(f"{traced} glyphs traced, {len(outlines) - traced} derived")
    print(f"scale: {scale:.4f} units/px, x-height: {x_height}")
    print(f"font:  {ttf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
