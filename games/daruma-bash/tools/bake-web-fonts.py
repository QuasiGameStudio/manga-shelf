#!/usr/bin/env python3
"""Bake the three UI fonts into AngelCode .fnt atlases for the HTML5 build.

The desktop build rasterises Baloo2-ExtraBold.ttf at runtime with gdx-freetype. GWT has no
FreeType backend, so this script reproduces the exact parameters DarumaScreen.loadFonts() uses
(size / border / shadow / colours) and writes one .fnt + .png pair per size into assets/fonts/.

Re-run after changing the typeface or the sizes in DarumaScreen.loadFonts():

    python tools/bake-web-fonts.py

Output is deterministic, so the generated files can be committed.
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(HERE)
ASSET_DIR = os.path.join(GAME, "assets", "fonts")

FACE = "Baloo2-ExtraBold.ttf"

# fill / border / shadow colours, straight out of DarumaScreen's palette
TEXT = (255, 245, 222, 255)        # new Color(1f, 0.96f, 0.87f, 1f)
OUTLINE = (77, 46, 28, 255)        # new Color(0.30f, 0.18f, 0.11f, 1f)
SHADOW = (0, 0, 0, 89)             # new Color(0f, 0f, 0f, 0.35f)

# (basename, pixel size, border width, shadow offset) - mirrors loadFonts()
SPECS = [
    ("daruma-title", 76, 3.5, 2),
    ("daruma-body", 30, 2.0, 1),
    ("daruma-small", 23, 1.5, 1),
]

# Printable ASCII. Every string the game draws is plain ASCII.
CHARS = [chr(c) for c in range(32, 127)]

PAD = 2          # transparent gutter between glyphs in the atlas
MAX_WIDTH = 1024  # atlas row width target before wrapping


def next_pot(value: int) -> int:
    return 1 << max(0, math.ceil(math.log2(value)))


def render_glyph(font: ImageFont.FreeTypeFont, ch: str, stroke: int, shadow: int):
    """Return (image, xoffset, yoffset, xadvance) for one glyph, baseline-relative."""
    box = 400
    origin_x, origin_y = 160, 300  # pen origin; baseline sits at origin_y

    tmp = Image.new("RGBA", (box, box), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tmp)

    if shadow:
        draw.text((origin_x + shadow, origin_y + shadow), ch, font=font, fill=SHADOW,
                  stroke_width=stroke, stroke_fill=SHADOW, anchor="ls")
    draw.text((origin_x, origin_y), ch, font=font, fill=TEXT,
              stroke_width=stroke, stroke_fill=OUTLINE, anchor="ls")

    ink = tmp.getbbox()
    advance = int(round(font.getlength(ch)))
    if ink is None:  # space and friends: no ink, advance only
        return None, 0, 0, advance

    glyph = tmp.crop(ink)
    xoffset = ink[0] - origin_x
    yoffset = (ink[1] - origin_y)  # negative: pixels above the baseline
    return glyph, xoffset, yoffset, advance


def bake(basename: str, size: int, border: float, shadow: int) -> None:
    font_path = os.path.join(ASSET_DIR, FACE)
    face = ImageFont.truetype(font_path, size=size)
    stroke = max(1, int(round(border)))

    ascent, descent = face.getmetrics()
    base = ascent
    line_height = ascent + descent

    glyphs = []
    for ch in CHARS:
        image, xoffset, yoffset, advance = render_glyph(face, ch, stroke, shadow)
        glyphs.append((ch, image, xoffset, yoffset, advance))

    # --- pack: rows of glyphs, left to right, wrapping at MAX_WIDTH -----------------
    placed = []
    x = y = 0
    row_height = 0
    for ch, image, xoffset, yoffset, advance in glyphs:
        if image is None:
            placed.append((ch, None, 0, 0, xoffset, yoffset, advance))
            continue
        w, h = image.size
        if x + w + PAD > MAX_WIDTH:
            x = 0
            y += row_height + PAD
            row_height = 0
        placed.append((ch, image, x, y, xoffset, yoffset, advance))
        x += w + PAD
        row_height = max(row_height, h)

    used_w = min(MAX_WIDTH, max((p[2] + p[1].size[0]) for p in placed if p[1]) + PAD)
    used_h = y + row_height + PAD
    sheet_w, sheet_h = next_pot(used_w), next_pot(used_h)

    atlas = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    for ch, image, gx, gy, *_ in placed:
        if image is not None:
            atlas.paste(image, (gx, gy))

    png_name = basename + ".png"
    atlas.save(os.path.join(ASSET_DIR, png_name))

    # --- descriptor ------------------------------------------------------------------
    lines = [
        f'info face="Baloo 2 ExtraBold" size={size} bold=0 italic=0 charset="" unicode=1 '
        f"stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=1,1 outline={border}",
        f"common lineHeight={line_height} base={base} scaleW={sheet_w} scaleH={sheet_h} "
        f"pages=1 packed=0 alphaChnl=0 redChnl=4 greenChnl=4 blueChnl=4",
        f'page id=0 file="{png_name}"',
        f"chars count={len(placed)}",
    ]
    for ch, image, gx, gy, xoffset, yoffset, advance in placed:
        w, h = image.size if image is not None else (0, 0)
        # yoffset is stored as "distance from the top of the line to the top of the glyph"
        lines.append(
            f"char id={ord(ch)} x={gx} y={gy} width={w} height={h} "
            f"xoffset={xoffset} yoffset={base + yoffset} xadvance={advance} page=0 chnl=15"
        )
    lines.append("kernings count=0")

    with open(os.path.join(ASSET_DIR, basename + ".fnt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"{basename}: {sheet_w}x{sheet_h}, {len(placed)} glyphs, "
          f"lineHeight={line_height} base={base}")


def main() -> None:
    os.makedirs(ASSET_DIR, exist_ok=True)
    for basename, size, border, shadow in SPECS:
        bake(basename, size, border, shadow)


if __name__ == "__main__":
    main()
