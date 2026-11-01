"""Draws the launch art for Daruma Bash (GameZone pilot, kumpulangames remake).

Run:  python make-art.py
Outputs PNGs into ../assets/art/ plus a contact sheet (preview.png) next to this script.

House rules (carried over from the factory generators):
  * one outline, 1px, warm dark brown INK - never black
  * flat fills, three tones per material; the dusk sky is the one painted exception
  * anything that is a character gets a face; colour is identity, posture is state
  * sprites authored 1:1 at the size DarumaScreen draws them (daruma 228x74, pedestal 320x64,
    arrow 92, floor tile 64), so a 1px ink line still reads as a line
  * the tower draws daruma-1..5 in stack order, so each colour keeps its identity as the tower
    shrinks and regrows

Everything is drawn fresh: nothing here ships from the original game's export.
"""

import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "art")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- palette

INK = (0x4C, 0x32, 0x20)  # warm dark brown, matched to DarumaScreen.OUTLINE (0.30,0.18,0.11)

DUSK_TOP = (74, 52, 116)
DUSK_MID = (168, 78, 120)
DUSK_LOW = (244, 158, 112)

HILL_FAR = (58, 38, 84)
HILL_NEAR = (44, 28, 66)

WOOD = (196, 138, 84)
WOOD_DARK = (150, 98, 56)
WOOD_LIGHT = (224, 174, 116)

STRAW = (236, 214, 168)
STRAW_DARK = (200, 168, 118)

CREAM = (255, 243, 214)
CREAM_DARK = (236, 214, 168)

GOLD = (255, 200, 62)
GOLD_DARK = (216, 150, 28)
GOLD_LIGHT = (255, 238, 150)

WHITE = (255, 255, 255)
PUPIL = (0x2A, 0x1E, 0x14)

# Colour is identity: each tower layer is one daruma in its own coat.
DARUMA = [
    ((232, 66, 62), (176, 40, 44), (255, 124, 108)),    # 1 red
    ((62, 182, 172), (38, 130, 124), (120, 224, 214)),  # 2 teal
    ((255, 200, 62), (216, 150, 28), (255, 238, 150)),  # 3 gold
    ((86, 140, 232), (52, 98, 178), (140, 180, 255)),   # 4 blue
    ((120, 190, 74), (84, 144, 52), (164, 224, 116)),   # 5 green
]

FLAG = [(232, 66, 62), (62, 182, 172), (255, 200, 62), (120, 190, 74), (86, 140, 232)]


def blank(w, h=None):
    return Image.new("RGBA", (w, h or w), (0, 0, 0, 0))


def save(img, name):
    img.save(os.path.join(OUT, name))
    print(f"  {name:14s} {img.width}x{img.height}")
    return img


# ---------------------------------------------------------------- faces

def eyes(d, cx, cy, spread=8, r=5, look=0, happy=False):
    if happy:
        for s in (-1, 1):
            d.arc([cx + s * spread - r, cy - r, cx + s * spread + r, cy + r + 1],
                  start=200, end=340, fill=INK, width=2)
        return
    for s in (-1, 1):
        ex = cx + s * spread
        d.ellipse([ex - r, cy - r, ex + r, cy + r], fill=WHITE, outline=INK)
        d.ellipse([ex - r * 0.45 + look, cy - r * 0.45, ex + r * 0.45 + look, cy + r * 0.45],
                  fill=PUPIL)
        d.ellipse([ex - r * 0.35 + look, cy - r * 0.45, ex - r * 0.05 + look, cy - r * 0.1],
                  fill=WHITE)


def blush(d, cx, cy, spread=10, r=4, colour=(255, 150, 140)):
    for s in (-1, 1):
        d.ellipse([cx + s * spread - r, cy - r * 0.6, cx + s * spread + r, cy + r * 0.6],
                  fill=colour)


def mouth(d, cx, cy, w=8, h=5, open_=False):
    if open_:
        d.ellipse([cx - 3, cy - 2, cx + 3, cy + 4], fill=INK)
    else:
        d.arc([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], start=20, end=160,
              fill=INK, width=2)


def brows(d, cx, cy, spread=20, w=14):
    # Determined little slants: a daruma about to be knocked over anyway can still look stern.
    for s in (-1, 1):
        bx = cx + s * spread
        d.line([bx - s * w // 2, cy + 3, bx + s * w // 2, cy - 4], fill=INK, width=2)


# ---------------------------------------------------------------- background

def background():
    """Dusk festival sky: the one painted-gradient exception, plus hills, bunting, lanterns."""
    w, h = 1280, 720
    img = blank(w, h)
    d = ImageDraw.Draw(img)
    horizon = 520
    for y in range(h):
        t = min(1.0, y / horizon)
        if t < 0.5:
            k = t / 0.5
            row = tuple(int(a + (b - a) * k) for a, b in zip(DUSK_TOP, DUSK_MID))
        else:
            k = (t - 0.5) / 0.5
            row = tuple(int(a + (b - a) * k) for a, b in zip(DUSK_MID, DUSK_LOW))
        d.line([0, y, w, y], fill=row + (255,))

    # Sun, low over the horizon.
    sx, sy, sr = 950, 430, 58
    d.ellipse([sx - sr - 16, sy - sr - 16, sx + sr + 16, sy + sr + 16],
              fill=GOLD_LIGHT + (70,))
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=GOLD)
    d.ellipse([sx - sr + 10, sy - sr + 10, sx - 6, sy + 4], fill=GOLD_LIGHT)

    # Hill silhouettes: two flat bands, far then near.
    for base, amp, step, fill in ((horizon - 40, 60, 320, HILL_FAR),
                                  (horizon - 8, 40, 274, HILL_NEAR)):
        pts = [(0, h)]
        for x in range(0, w + 8, 8):
            y = base - abs(math.sin(x / step)) * amp
            pts.append((x, y))
        pts.append((w, h))
        d.polygon(pts, fill=fill)

    # Bunting: a sagging rope of festival flags across the upper third.
    d.line([0, 58, w, 34], fill=INK, width=2)
    for i, x in enumerate(range(30, w, 106)):
        top = 58 - int((58 - 34) * (x / w))
        pts = [(x, top + 2), (x + 74, top - 8), (x + 37, top + 58)]
        d.polygon(pts, fill=FLAG[i % len(FLAG)], outline=INK)

    # Two paper lanterns hanging in from the corners.
    for lx, rope_h in ((150, 74), (1128, 96)):
        d.line([lx, 0, lx, rope_h], fill=INK, width=2)
        ry = rope_h
        d.ellipse([lx - 34, ry, lx + 34, ry + 74], fill=(232, 66, 62), outline=INK)
        d.rectangle([lx - 34, ry + 22, lx + 34, ry + 33], fill=GOLD, outline=INK)
        d.line([lx, ry + 74, lx, ry + 88], fill=GOLD, width=3)
    return img


# ---------------------------------------------------------------- floor + pedestal

def floor_tile():
    """Wood decking. Only full-width/height features inside, so the repeat wrap is invisible."""
    tile = 64
    img = blank(tile, tile)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, tile - 1, tile - 1], fill=WOOD)
    for x in (0, 32):  # plank seams at the tile edges and the middle
        d.line([x, 0, x, tile], fill=WOOD_DARK)
        d.line([x + 1, 0, x + 1, tile], fill=WOOD_DARK)
    for y in (12, 27, 44, 58):
        d.line([0, y, tile, y], fill=WOOD_LIGHT)
    for y in (19, 36, 52):
        d.line([0, y, tile, y], fill=WOOD_DARK)
    d.ellipse([12, 8, 16, 12], fill=WOOD_DARK)
    d.ellipse([44, 40, 48, 44], fill=WOOD_DARK)
    return img


def pedestal():
    """The straw mat stand the tower rests on."""
    w, h = 320, 64
    img = blank(w, h)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([2, 2, w - 3, h - 3], radius=18, fill=STRAW, outline=INK)
    for x in range(14, w - 12, 18):
        d.line([x, 8, x + 3, h - 10], fill=STRAW_DARK)
    d.line([4, 12, w - 5, 12], fill=(248, 232, 190), width=3)
    d.line([4, h - 12, w - 5, h - 12], fill=STRAW_DARK, width=3)
    d.rounded_rectangle([2, 2, w - 3, h - 3], radius=18, outline=INK)
    return img


# ---------------------------------------------------------------- the darumas

DW, DH = 228, 74


def daruma(index):
    base, dark, light = DARUMA[index % len(DARUMA)]
    img = blank(DW, DH)
    d = ImageDraw.Draw(img)

    # Barrel body: rounded slab, lit from the upper-left like everything else on screen.
    d.rounded_rectangle([3, 3, DW - 4, DH - 4], radius=30, fill=base, outline=INK)
    # Dark right shoulder, then re-fill the interior so the shading stays inside the silhouette.
    d.pieslice([DW - 118, 3, DW - 2, DH - 2], start=-90, end=90, fill=dark)
    d.rounded_rectangle([10, 10, DW - 11, DH - 11], radius=24, fill=base)
    d.rounded_rectangle([3, 3, DW - 4, DH - 4], radius=30, outline=INK)
    # Light wash on the left cheek, again clipped back inside the silhouette.
    d.pieslice([2, 2, 128, DH - 2], start=90, end=270, fill=light)
    d.rounded_rectangle([10, 10, DW - 11, DH - 11], radius=24, fill=None, outline=base)
    d.rounded_rectangle([3, 3, DW - 4, DH - 4], radius=30, outline=INK)

    # Top and bottom rolls: dark bands so the stacked kegs read with visible edges.
    d.line([26, 14, DW - 26, 14], fill=dark, width=2)
    d.line([26, 12, DW - 26, 12], fill=light, width=2)
    d.line([26, DH - 14, DW - 26, DH - 14], fill=dark, width=2)

    # The daruma face: cream mask, stern brows, round eyes, tight mouth, blush.
    d.ellipse([DW // 2 - 62, 12, DW // 2 + 62, DH - 6], fill=CREAM, outline=INK)
    brows(d, DW // 2, 24, spread=24, w=16)
    eyes(d, DW // 2, 36, spread=16, r=6)
    mouth(d, DW // 2, 54, w=12, h=6)
    blush(d, DW // 2, 50, spread=34, r=7)
    return img


# ---------------------------------------------------------------- cue + extras

def arrow():
    """Right-pointing cue arrow with a soft gold halo - the screen mirrors it for left swipes."""
    s = 92
    img = blank(s)
    d = ImageDraw.Draw(img)
    d.ellipse([2, 2, s - 3, s - 3], fill=GOLD + (110,))
    d.ellipse([8, 8, s - 9, s - 9], fill=GOLD_LIGHT + (120,))
    d.polygon([(22, 36), (52, 36), (52, 22), (74, 46), (52, 70), (52, 56), (22, 56)],
              fill=GOLD, outline=INK)
    d.line([24, 38, 50, 38], fill=GOLD_LIGHT, width=2)
    return img


def hammer():
    """A wooden mallet, spare polish for impact moments; the screen draws its swing procedurally."""
    w, h = 96, 96
    img = blank(w, h)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([10, 14, 86, 52], radius=12, fill=WOOD, outline=INK)
    d.rounded_rectangle([16, 20, 80, 30], radius=6, fill=WOOD_LIGHT)
    d.rectangle([10, 44, 86, 52], fill=WOOD_DARK)
    d.rounded_rectangle([10, 14, 86, 52], radius=12, outline=INK)
    d.rounded_rectangle([42, 50, 56, 90], radius=6, fill=WOOD_LIGHT, outline=INK)
    d.line([46, 54, 46, 86], fill=WOOD_DARK)
    return img


def ninepatch(fill, border_bottom=None):
    """64px panel/button ninepatch; 14px corners inside 28px patch margins, so stretch stays safe."""
    s = 64
    img = blank(s)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([1, 1, s - 2, s - 2], radius=14, fill=fill, outline=INK)
    d.line([16, 6, s - 17, 6], fill=GOLD_LIGHT if fill == GOLD else WHITE)
    if border_bottom is not None:
        d.line([16, s - 8, s - 17, s - 8], fill=border_bottom, width=3)
    return img


def _blob(size, circles, fill, ink=INK):
    """Union of ellipses with a single 1px ink edge (the factory trick, kept for future clouds)."""
    m = Image.new("L", size, 0)
    dm = ImageDraw.Draw(m)
    for box in circles:
        dm.ellipse(box, fill=255)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    img.paste(Image.new("RGBA", size, fill + (255,)), (0, 0), m)
    if ink is not None:
        edge = ImageChops.subtract(m, m.filter(ImageFilter.MinFilter(3)))
        img.paste(Image.new("RGBA", size, ink + (255,)), (0, 0), edge)
    return img, m


def cloud(w=132, h=60):
    """Inkless cream cloud: an outline up here would compete with the sprites down below."""
    img, _ = _blob((w, h), [(4, 24, 60, 56), (26, 10, 92, 54), (60, 20, 126, 56),
                            (18, 30, 108, 58)], CREAM, ink=None)
    return img


# ---------------------------------------------------------------- main

def main():
    print("Daruma Bash art ->", os.path.normpath(OUT))
    save(background(), "bg.png")
    save(floor_tile(), "floor.png")
    save(pedestal(), "pedestal.png")
    for i in range(5):
        save(daruma(i), f"daruma-{i + 1}.png")
    save(arrow(), "arrow.png")
    save(hammer(), "hammer.png")
    save(ninepatch(CREAM), "panel.png")
    save(ninepatch(GOLD, border_bottom=GOLD_DARK), "button.png")
    save(cloud(), "cloud.png")

    # Contact sheet on the dusk field: the sprites as they will actually sit in the scene.
    names = ["pedestal.png", "daruma-1.png", "daruma-2.png", "daruma-3.png", "daruma-4.png",
             "daruma-5.png", "arrow.png", "hammer.png", "floor.png", "panel.png", "button.png"]
    imgs = [Image.open(os.path.join(OUT, n)).convert("RGBA") for n in names]
    cell_w, cell_h, cols = 260, 140, 3
    rows = (len(imgs) + cols - 1) // cols
    sheet = background().crop((0, 90, cell_w * cols, 90 + cell_h * rows))
    for i, im in enumerate(imgs):
        scale = min((cell_w - 24) / im.width, (cell_h - 26) / im.height, 1.0)
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))),
                       Image.NEAREST)
        x = (i % cols) * cell_w + (cell_w - im.width) // 2
        y = (i // cols) * cell_h + (cell_h - im.height) // 2
        sheet.alpha_composite(im, (x, y))
    sheet.save(os.path.join(HERE, "preview.png"))
    print(f"  preview.png    contact sheet {sheet.width}x{sheet.height}")


if __name__ == "__main__":
    main()
