"""Command-line entry point.

# TODO: image -> glyph pipeline (trace, fit, build) lands here.
"""

import sys

from vibefont import __version__


def main() -> int:
    print(f"vibefont {__version__} — pipeline not implemented yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
