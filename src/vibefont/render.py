"""Re-render the sample layout with the built font and compose a
side-by-side comparison sheet."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from vibefont.build import UPM
from vibefont.segment import SampleSheet

COMPARISON_WIDTH = 1600


def render_recreation(sheet: SampleSheet, font_path: Path, scale: float,
                      lsb: float, out: Path) -> Image.Image:
    """Draw every glyph at its measured position in the source sheet.

    ``scale`` is the pipeline's font-units-per-image-pixel factor, so an em
    is UPM/scale px tall and positions line up 1:1 with the original.
    """
    em_px = UPM / scale
    font = ImageFont.truetype(font_path, size=em_px)
    img = Image.new("RGB", sheet.size, "white")
    draw = ImageDraw.Draw(img)
    for box in sheet.boxes:
        # anchor "ls" puts the pen origin at (x, baseline); shift left by the
        # lsb so the ink lands where the source ink was measured.
        draw.text((box.left - lsb / scale, box.baseline), box.char,
                  font=font, fill="black", anchor="ls")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return img


def proof_sheet(font_path: Path, lines: list[str], out: Path,
                em_px: int = 160) -> None:
    """Type ``lines`` with the font's own metrics — the install-and-use view."""
    font = ImageFont.truetype(font_path, size=em_px)
    pad, leading = em_px // 2, round(em_px * 1.4)
    width = round(max(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(
        line, font=font) for line in lines)) + 2 * pad
    img = Image.new("RGB", (width, leading * len(lines) + pad), "white")
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        draw.text((pad, pad + leading * (i + 1) - em_px // 2), line,
                  font=font, fill="black", anchor="ls")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def comparison_sheet(original: Path, recreation: Image.Image,
                     out: Path) -> None:
    """Original on top, recreation below, downscaled for review."""
    top = Image.open(original).convert("RGB")
    gap = 24
    sheet = Image.new(
        "RGB", (top.width, top.height * 2 + gap), "dimgray")
    sheet.paste(top, (0, 0))
    sheet.paste(recreation, (0, top.height + gap))
    ratio = COMPARISON_WIDTH / sheet.width
    sheet = sheet.resize((COMPARISON_WIDTH, round(sheet.height * ratio)),
                         Image.LANCZOS)
    sheet.save(out)
