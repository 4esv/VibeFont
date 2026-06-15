"""Proof sheets: render the built TTFs with PIL so the letterforms can be
judged by eye (passing tests prove the font compiles, not that it looks
right)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

MARGIN = 60
GUIDE = (235, 235, 235)

PANGRAMS = [
    "Sphinx of black quartz, judge my vow.",
    "Jackdaws love my big sphinx of quartz!",
]
MIXED = "Grumpy wizards make toxic brew? 0123456789"
QUOTES = "“It’s ‘slop’ — lovingly so…” (eslop@example.com) #1 *free*"
PARAGRAPH = (
    "Eslop is a family of fonts designed entirely by an AI. Every curve "
    "you see was chosen by a transformer that has never held a pen, read "
    "a sign across a street, or squinted. The spacing is optical in the "
    "sense that numbers were involved. It is given away for free because "
    "charging money would invite questions.")


def _wrap(text: str, font, max_width: int, draw) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_proof(font_path: Path, title: str, charset: str,
                 out: Path, width: int = 2200) -> None:
    sections: list[tuple[int, str]] = [(110, title), (0, "")]
    letters = [c for c in charset if c.isalpha()]
    upper = "".join(c for c in letters if c.isupper())
    lower = "".join(c for c in letters if c.islower())
    digits = "".join(c for c in charset if c.isdigit())
    other = "".join(c for c in sorted(charset, key=ord)
                    if not c.isalnum() and not c.isspace())
    half = (len(other) + 1) // 2
    sections += [(96, upper), (96, lower), (96, digits + " " + other[:half]),
                 (96, other[half:]), (0, "")]
    sections += [(64, p) for p in PANGRAMS]
    sections += [(64, MIXED), (64, QUOTES), (0, "")]

    img = Image.new("RGB", (width, 6000), "white")
    draw = ImageDraw.Draw(img)
    y = MARGIN
    for size, text in sections:
        if not text:
            y += 40
            continue
        font = ImageFont.truetype(str(font_path), size=size)
        line_h = round(size * 1.35)
        for chunk in _wrap(text, font, width - 2 * MARGIN, draw) or [""]:
            baseline = y + size
            draw.line([(MARGIN, baseline), (width - MARGIN, baseline)],
                      fill=GUIDE)
            draw.text((MARGIN, baseline), chunk, font=font, fill="black",
                      anchor="ls")
            y = y + line_h
        y += 14

    para_font = ImageFont.truetype(str(font_path), size=34)
    for line in _wrap(PARAGRAPH, para_font, width - 2 * MARGIN, draw):
        draw.text((MARGIN, y + 34), line, font=para_font, fill="black",
                  anchor="ls")
        y += 48
    y += 40

    for size in (18, 24, 32, 48):
        f = ImageFont.truetype(str(font_path), size=size)
        draw.text((MARGIN, y + size), "Hamburgevons 0123 — waterfall",
                  font=f, fill="black", anchor="ls")
        y += round(size * 1.4)

    img = img.crop((0, 0, width, y + MARGIN))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def render_overview(entries: list[tuple[str, Path]], out: Path,
                    width: int = 2200) -> None:
    """One sheet, every family: name + pangram + lowercase, stacked."""
    rows = []
    for name, path in entries:
        rows.append((path, 76, name))
        rows.append((path, 64, PANGRAMS[0]))
        rows.append((path, 64, "abcdefghijklmnopqrstuvwxyz 0123456789"))
        rows.append((None, 0, ""))
    img = Image.new("RGB", (width, 4000), "white")
    draw = ImageDraw.Draw(img)
    y = MARGIN
    for path, size, text in rows:
        if path is None:
            y += 70
            continue
        font = ImageFont.truetype(str(path), size=size)
        draw.text((MARGIN, y + size), text, font=font, fill="black",
                  anchor="ls")
        y += round(size * 1.45)
    img = img.crop((0, 0, width, y + MARGIN))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
