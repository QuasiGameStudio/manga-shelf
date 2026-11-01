"""Generates the art for Bucket Catch (bright garden / sky theme).

Run:  python make-art.py
Outputs PNGs into ../assets/art/ and a preview contact sheet next to this script.

Design rules:
  * author at logical resolution, upscale with NEAREST so blocks stay square
  * light everything from the same direction (top-left)
  * tileable textures wrap at the edges so a tiled strip has no seams
  * the two object families must be tellable apart at a glance and by colour alone:
    fruit is warm red/green/gold, the obstacle is cold slate grey
"""

import math
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "art")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- palette

SKY_TOP = (108, 190, 244)
SKY_MID = (162, 216, 250)
SKY_LOW = (214, 240, 255)

GRASS = (104, 182, 68)
GRASS_DARK = (94, 170, 62)
GRASS_LIGHT = (122, 202, 84)
GRASS_BLADE = (82, 156, 54)
GRASS_SOIL = (124, 92, 62)

WOOD = (196, 138, 84)
WOOD_DARK = (150, 98, 56)
WOOD_LIGHT = (224, 174, 116)
WOOD_EDGE = (104, 66, 42)
METAL = (176, 184, 196)
METAL_DARK = (120, 130, 146)
METAL_LIGHT = (226, 232, 240)

APPLE = (232, 66, 62)
APPLE_DARK = (176, 40, 44)
APPLE_LIGHT = (255, 124, 108)

BERRY = (226, 52, 84)
BERRY_DARK = (168, 30, 60)
BERRY_LIGHT = (255, 120, 140)
SEED = (255, 226, 132)

GOLD = (255, 200, 62)
GOLD_DARK = (216, 150, 28)
GOLD_LIGHT = (255, 238, 150)

SLATE = (108, 116, 138)
SLATE_DARK = (72, 78, 96)
SLATE_LIGHT = (150, 158, 178)
SLATE_EDGE = (44, 48, 62)
WARN = (238, 96, 56)

LEAF = (86, 174, 88)
LEAF_DARK = (52, 130, 62)

CREAM = (255, 243, 214)
BROWN = (138, 90, 59)
BROWN_DARK = (104, 66, 42)

BUTTON_BG = (122, 196, 86)
BUTTON_EDGE = (52, 112, 48)
BUTTON_TOP = (168, 226, 126)

WHITE = (255, 255, 255)


def hnoise(x, y, seed=0):
    n = (x * 374761393 + y * 668265263 + seed * 1013904223) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65536.0


def upscale(img, factor):
    return img.resize((img.width * factor, img.height * factor), Image.NEAREST)


def save(img, name, factor=1):
    path = os.path.join(OUT, name)
    upscale(img, factor).save(path)
    print(f"  {name:20s} {img.width}x{img.height} -> x{factor}")
    return path


# ---------------------------------------------------------------- backdrop

def sky(width=32, height=256):
    """Vertical gradient, stretched over the whole window and filtered linearly.

    Authored small on purpose: it is a smooth gradient, so the only thing that matters is that
    the colour ramp is right - upscaling it with a linear filter keeps it band-free.
    """
    img = Image.new("RGB", (width, height))
    px = img.load()
    for y in range(height):
        t = y / (height - 1.0)
        if t < 0.55:
            k = t / 0.55
            c = tuple(int(SKY_TOP[i] + (SKY_MID[i] - SKY_TOP[i]) * k) for i in range(3))
        else:
            k = (t - 0.55) / 0.45
            c = tuple(int(SKY_MID[i] + (SKY_LOW[i] - SKY_MID[i]) * k) for i in range(3))
        for x in range(width):
            px[x, y] = c
    return img


def cloud(width=96, height=44):
    """A soft cloud: overlapping ellipses, no outline, so it stays in the background."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    blobs = ((4, 20, 40, 42), (22, 10, 66, 40), (44, 16, 90, 42), (16, 24, 80, 42))
    for box in blobs:
        d.ellipse(box, fill=(255, 255, 255, 255))
    # Shade the underside a touch so it reads as a solid puff rather than a flat blob.
    d.ellipse((18, 28, 82, 42), fill=(232, 244, 255, 255))
    d.ellipse((4, 24, 40, 40), fill=(255, 255, 255, 255))
    d.ellipse((22, 14, 66, 40), fill=(255, 255, 255, 255))
    d.ellipse((44, 20, 90, 40), fill=(255, 255, 255, 255))
    return img


def grass_tile(size=64):
    """Tileable grass, same treatment as the maze lawn so both games share a look."""
    img = Image.new("RGB", (size, size))
    px = img.load()
    for y in range(size):
        for x in range(size):
            n = hnoise(x, y, 1)
            c = GRASS
            if n > 0.90:
                c = GRASS_LIGHT
            elif n < 0.10:
                c = GRASS_DARK
            px[x, y] = c

    for i in range(7):
        cx = int(hnoise(i, 31, 9) * size)
        cy = int(hnoise(i, 37, 11) * size)
        for j in range(14):
            ox = int(hnoise(i * 13 + j, 41, 13) * 7) - 3
            oy = int(hnoise(i * 17 + j, 43, 15) * 5) - 2
            if hnoise(i * 19 + j, 47, 17) > 0.45:
                px[(cx + ox) % size, (cy + oy) % size] = GRASS_LIGHT

    for i in range(30):
        bx = int(hnoise(i, 7, 3) * size)
        by = int(hnoise(i, 11, 5) * size)
        height = 3 + int(hnoise(i, 13, 7) * 2)
        for k in range(height):
            yy = (by + k) % size
            xx = (bx + (1 if k == height - 1 else 0)) % size
            px[xx, yy] = GRASS_LIGHT if k >= height - 2 else GRASS_BLADE
        px[(bx + 1) % size, (by + height) % size] = GRASS_BLADE
    return img


# ---------------------------------------------------------------- 9-patch panels

def panel_tile(size=32, radius=10, border=3):
    """Rounded panel for 9-patch stretching: cream card with a soft brown edge."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=BROWN_DARK)
    d.rounded_rectangle((border, border, size - 1 - border, size - 1 - border),
                        radius=max(1, radius - border), fill=BROWN)
    d.rounded_rectangle((border + 2, border + 2, size - 3 - border, size - 3 - border),
                        radius=max(1, radius - border - 2), fill=CREAM)
    d.rounded_rectangle((border + 4, border + 4, size - 5 - border, size - 5 - border),
                        radius=max(1, radius - border - 4), fill=CREAM)
    d.line((radius, border + 3, size - radius - 1, border + 3), fill=WHITE)
    return img


def button_tile(size=32, radius=10, border=3):
    """Rounded green button for 9-patch stretching: bright grass green with a dark edge."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=BUTTON_EDGE)
    d.rounded_rectangle((border, border, size - 1 - border, size - 1 - border),
                        radius=max(1, radius - border), fill=BUTTON_BG)
    d.rounded_rectangle((border + 1, border + 1, size - 2 - border, size - 2 - border),
                        radius=max(1, radius - border - 1), fill=BUTTON_BG)
    d.line((radius, border + 3, size - radius - 1, border + 3), fill=BUTTON_TOP)
    d.line((radius, border + 4, size - radius - 1, border + 4), fill=BUTTON_TOP)
    return img


# ---------------------------------------------------------------- sprites

def bucket():
    """A wooden pail seen from the front, with a dark opening so the catch line is obvious.

    The mouth is what the player aims with, so the rim is drawn light metal against the sky and
    the inside is nearly black: at a glance the top edge is the target line, not the middle of
    the sprite. The handle arcs above it, which is the second cue that this is a bucket.
    """
    W, H = 36, 32
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Handle, drawn first so the body covers its ends.
    d.arc((3, 1, 32, 19), start=180, end=360, fill=METAL_DARK, width=2)
    d.arc((4, 2, 31, 18), start=180, end=360, fill=METAL, width=1)

    # Body: a trapezoid, wider at the rim than at the base.
    body = [(3, 10), (32, 10), (28, 31), (7, 31)]
    d.polygon(body, fill=WOOD, outline=WOOD_EDGE)

    # Staves: vertical grain lines, following the taper.
    for sx in (8, 13, 18, 23, 27):
        bot_x = 7 + int((sx - 3) * (21.0 / 29.0))
        d.line((sx, 13, bot_x, 30), fill=WOOD_DARK)

    # Lit left edge and shaded right edge, so the pail reads as round.
    d.line((4, 12, 8, 30), fill=WOOD_LIGHT)
    d.line((31, 12, 27, 30), fill=WOOD_DARK)

    # Metal bands.
    d.rectangle((5, 17, 30, 19), fill=METAL)
    d.line((5, 17, 30, 17), fill=METAL_LIGHT)
    d.line((5, 19, 30, 19), fill=METAL_DARK)
    d.rectangle((7, 25, 28, 27), fill=METAL)
    d.line((7, 25, 28, 25), fill=METAL_LIGHT)
    d.line((7, 27, 28, 27), fill=METAL_DARK)

    # Rim ring, then the black opening inside it: the hole is what makes it a bucket.
    d.ellipse((2, 7, 33, 16), fill=METAL, outline=WOOD_EDGE)
    d.ellipse((4, 8, 31, 15), fill=(72, 54, 46))
    d.ellipse((6, 9, 29, 14), fill=(34, 26, 24))
    d.arc((2, 7, 33, 16), start=180, end=360, fill=METAL_LIGHT, width=1)
    d.arc((2, 7, 33, 16), start=0, end=180, fill=METAL_DARK, width=1)
    return img


def apple():
    """A red apple: round body, leaf and stem on top, highlight upper-left."""
    W = H = 18
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((1, 5, 16, 17), fill=APPLE, outline=APPLE_DARK)
    d.ellipse((2, 9, 15, 17), fill=APPLE_DARK)
    d.ellipse((2, 5, 15, 15), fill=APPLE)
    d.ellipse((3, 6, 12, 12), fill=APPLE_LIGHT)
    d.ellipse((4, 6, 9, 9), fill=(255, 176, 164))
    # Stem and leaf.
    d.line((9, 5, 9, 2), fill=(112, 74, 40))
    d.ellipse((10, 1, 16, 5), fill=LEAF, outline=LEAF_DARK)
    return img


def strawberry():
    """A strawberry: heart-shaped body, green calyx, pale seeds."""
    W = H = 18
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(2, 6), (15, 6), (13, 12), (9, 17), (5, 12)], fill=BERRY, outline=BERRY_DARK)
    d.ellipse((1, 3, 16, 10), fill=BERRY)
    d.ellipse((2, 6, 15, 11), fill=BERRY_DARK)
    d.ellipse((2, 4, 14, 9), fill=BERRY)
    d.ellipse((4, 5, 10, 8), fill=BERRY_LIGHT)
    # Seeds.
    for sx, sy in ((6, 8), (10, 8), (8, 11), (5, 12), (12, 12), (8, 14)):
        d.point((sx, sy), fill=SEED)
    # Calyx: a five-point green star over the shoulders.
    d.polygon([(1, 4), (6, 6), (9, 3), (12, 6), (16, 4), (13, 8), (5, 8)],
              fill=LEAF, outline=LEAF_DARK)
    d.line((9, 2, 9, 5), fill=LEAF_DARK)
    return img


def star():
    """The bonus: a golden five-point star, unmistakably not food and not the obstacle."""
    W = H = 18
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, outer, inner = 9.0, 9.5, 8.4, 3.6
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        r = outer if i % 2 == 0 else inner
        points.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    d.polygon(points, fill=GOLD, outline=GOLD_DARK)
    # Inner facet, lit from the upper left.
    d.polygon([(cx, cy - 5.6), (cx + 2.4, cy - 0.4), (cx, cy + 1.6), (cx - 2.4, cy - 0.4)],
              fill=GOLD_LIGHT)
    return img


def rock():
    """The obstacle: a spiky slate boulder with warning-red tips.

    Deliberately the only cold-coloured sprite in the game - everything catchable is warm - and
    the only one with points. Spikes plus red tips read as "do not catch this" before a child can
    read anything, which is the whole job of the art here.
    """
    W = H = 18
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Spikes first, so the body overlaps their bases.
    for x0, x1, tipx, tipy in ((1, 7, 3.5, 2), (5, 13, 9.0, 0), (11, 17, 14.5, 2)):
        d.polygon([(x0, 9), (x1, 9), (tipx, tipy)], fill=SLATE, outline=SLATE_EDGE)
        d.line((tipx, tipy + 1, tipx, tipy + 3), fill=WARN)

    body = [(1, 12), (3, 7), (8, 5), (14, 6), (17, 10), (15, 16), (6, 17), (2, 15)]
    d.polygon(body, fill=SLATE, outline=SLATE_EDGE)
    # Facets: lit top-left, shaded bottom-right.
    d.polygon([(3, 7), (8, 5), (12, 8), (6, 10)], fill=SLATE_LIGHT)
    d.polygon([(12, 8), (17, 10), (15, 16), (9, 15)], fill=SLATE_DARK)
    # Crack and pips.
    d.line((8, 10, 6, 14), fill=SLATE_EDGE)
    d.line((6, 14, 8, 16), fill=SLATE_EDGE)
    d.point((13, 11), fill=SLATE_LIGHT)
    d.point((5, 12), fill=SLATE_LIGHT)
    return img


def ground_strip():
    """The soil lip under the lawn, so the bucket sits on something."""
    W, H = 32, 10
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W - 1, H - 1), fill=GRASS)
    d.rectangle((0, 6, W - 1, H - 1), fill=GRASS_SOIL)
    for x in range(W):
        n = hnoise(x, 3, 61)
        if n > 0.6:
            d.point((x, 5), fill=GRASS_LIGHT)
        if n < 0.25:
            d.point((x, 7), fill=(104, 76, 50))
    return img


# ---------------------------------------------------------------- main

def main():
    print("Bucket Catch art")
    save(sky(), "sky.png")
    save(cloud(), "cloud.png")
    save(grass_tile(), "grass.png")
    save(ground_strip(), "ground.png")
    save(bucket(), "bucket.png", 4)
    save(apple(), "apple.png", 4)
    save(strawberry(), "strawberry.png", 4)
    save(star(), "star.png", 4)
    save(rock(), "rock.png", 4)
    save(panel_tile(), "panel.png", 3)
    save(button_tile(), "button.png", 3)

    # Contact sheet, for eyeballing the set as a whole.
    names = ["bucket.png", "apple.png", "strawberry.png", "star.png", "rock.png",
             "panel.png", "button.png", "grass.png", "ground.png"]
    imgs = [Image.open(os.path.join(OUT, n)).convert("RGBA") for n in names]
    cell = 150
    sheet = Image.new("RGBA", (cell * len(imgs), cell), (162, 216, 250, 255))
    for i, im in enumerate(imgs):
        w, h = im.size
        scale = min((cell - 20) / w, (cell - 20) / h, 1.0)
        if scale != 1.0:
            im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.NEAREST)
        sheet.alpha_composite(im, (i * cell + (cell - im.width) // 2,
                                   (cell - im.height) // 2))
    sheet.save(os.path.join(HERE, "preview.png"))
    print("  preview.png (contact sheet)")


if __name__ == "__main__":
    main()
