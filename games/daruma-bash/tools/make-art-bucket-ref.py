"""Draws the mockup art for Bucket Catch (ladder tier 1).

Run:  python make-art.py
Outputs PNGs into ../assets/art/mockup/ and a contact sheet next to this script.

This game already ships, so the real sprites in ../assets/art/ are load-bearing: the Java loads them
by name and a clobbered file breaks a working build. Everything here therefore writes to
../assets/art/mockup/ and is drawn fresh rather than upscaled from the shipped low-res set — the
mockup is authored 1:1 at the size CatchScreen draws it (bucket 144x128, fruit 54x54), which is also
the size at which a 1px ink line still reads as a line.

The shipped generator is preserved unchanged as make-art-shipped.py. Run that one, not this one, if
you ever need to regenerate the game's own art.

Design rules (from design/mockup-brief.md):
  * one outline, 1px, warm dark brown INK - never black
  * flat fills, three tones per material, no gradients
  * anything that is a character gets a face; colour is identity, posture is state
  * contact shadow under anything standing on the grass
  * the palette is copied from the shipped make-art.py, so the mockup is the same garden
"""

import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "art", "mockup")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- palette

INK = (0x4C, 0x32, 0x20)  # warm dark brown, matched to CatchScreen.OUTLINE (0.30,0.18,0.11)

SKY_TOP = (108, 190, 244)
SKY_MID = (162, 216, 250)
SKY_LOW = (214, 240, 255)

GRASS = (104, 182, 68)
GRASS_DARK = (94, 170, 62)
GRASS_LIGHT = (122, 202, 84)
GRASS_BLADE = (82, 156, 54)
GRASS_SOIL = (124, 92, 62)
GRASS_SOIL_DARK = (104, 76, 50)

WOOD = (196, 138, 84)
WOOD_DARK = (150, 98, 56)
WOOD_LIGHT = (224, 174, 116)

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

LEAF = (86, 174, 88)
LEAF_DARK = (52, 130, 62)

CREAM = (255, 243, 214)
CREAM_DARK = (236, 214, 168)
BROWN = (138, 90, 59)
BROWN_DARK = (104, 66, 42)

WHITE = (255, 255, 255)
PUPIL = (0x2A, 0x1E, 0x14)


def blank(w, h=None):
    return Image.new("RGBA", (w, h or w), (0, 0, 0, 0))


def save(img, name):
    img.save(os.path.join(OUT, name))
    print(f"  {name:20s} {img.width}x{img.height}")
    return img


# ---------------------------------------------------------------- faces
#
# One pair of eyes, three moods, used by every sprite. Keeping them in one function is what stops
# the bucket and the fruit drifting into different art styles: the catchlight sits at the same
# clock position (upper-left) on everything, so the whole screen is lit from the same corner.

def eyes(d, cx, cy, spread=8, r=5, look=0, closed=False, happy=False):
    if happy:
        # Closed arcs curving up: the "delighted" shape. No pupil, so it cannot read as a stare.
        for s in (-1, 1):
            d.arc([cx + s * spread - r, cy - r, cx + s * spread + r, cy + r + 1],
                  start=200, end=340, fill=INK, width=2)
        return
    if closed:
        for s in (-1, 1):
            d.line([cx + s * spread - r, cy, cx + s * spread + r, cy], fill=INK, width=2)
        return
    for s in (-1, 1):
        ex = cx + s * spread
        d.ellipse([ex - r, cy - r, ex + r, cy + r], fill=WHITE, outline=INK)
        d.ellipse([ex - r * 0.45 + look, cy - r * 0.45, ex + r * 0.45 + look, cy + r * 0.45],
                  fill=PUPIL)
        # Catchlight, always upper-left.
        d.ellipse([ex - r * 0.35 + look, cy - r * 0.45, ex - r * 0.05 + look, cy - r * 0.1],
                  fill=WHITE)


def blush(d, cx, cy, spread=10, r=4, colour=(255, 150, 140)):
    for s in (-1, 1):
        d.ellipse([cx + s * spread - r, cy - r * 0.6, cx + s * spread + r, cy + r * 0.6],
                  fill=colour)


def mouth(d, cx, cy, w=8, h=5, open_=False, happy=False):
    if happy:
        d.arc([cx - w, cy - h, cx + w, cy + h + 2], start=15, end=165, fill=INK, width=2)
    elif open_:
        d.ellipse([cx - 3, cy - 2, cx + 3, cy + 4], fill=INK)
    else:
        d.arc([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], start=20, end=160,
              fill=INK, width=2)


# ---------------------------------------------------------------- the bucket
#
# The bucket is the player. Its mouth is the target line, so the rim is drawn bright metal against
# the sky and the inside is near-black: at a glance the top edge is the catch line, not the middle of
# the sprite. The handle arc above it is the second cue that this is a bucket and not a box.
#
# The face sits on the body, under the rim, because the mouth of the bucket is where the fruit goes —
# a face in the opening would fight the thing the player is aiming at.

BW, BH = 144, 128


def bucket(happy=False):
    img = blank(BW, BH)
    d = ImageDraw.Draw(img)

    # Handle first: ink stroke, then metal over it, leaving 1px of ink on each side.
    d.arc([22, 4, 122, 76], start=180, end=360, fill=INK, width=9)
    d.arc([22, 4, 122, 76], start=180, end=360, fill=METAL, width=7)
    d.arc([24, 6, 120, 74], start=196, end=344, fill=METAL_LIGHT, width=2)

    # Body: a trapezoid, wider at the rim than at the base.
    d.polygon([(12, 44), (132, 44), (118, 122), (26, 122)], fill=WOOD, outline=INK)

    # Staves follow the taper so the pail reads as coopered rather than as a printed panel.
    for sx in (38, 52, 66, 80, 94, 108):
        bot = 26 + int((sx - 12) * (92.0 / 120.0))
        d.line([sx, 46, bot, 121], fill=WOOD_DARK)

    # Lit left edge, shaded right edge: the three-tone ramp doing the roundness.
    d.polygon([(13, 45), (24, 45), (36, 121), (27, 121)], fill=WOOD_LIGHT)
    d.polygon([(120, 45), (131, 45), (117, 121), (110, 121)], fill=WOOD_DARK)

    # One metal band, low on the body, clear of the face.
    d.polygon([(21, 96), (123, 96), (122, 106), (22, 106)], fill=METAL, outline=INK)
    d.line([23, 97, 121, 97], fill=METAL_LIGHT, width=2)
    d.line([23, 105, 121, 105], fill=METAL_DARK)

    # Rim: bright ring, then the dark opening. The opening is opaque so fruit can be composited
    # behind the near rim and still be visibly "in" the bucket.
    d.ellipse([6, 26, 138, 60], fill=METAL, outline=INK)
    d.ellipse([12, 31, 132, 55], fill=(96, 66, 44))
    d.ellipse([17, 34, 127, 52], fill=(58, 40, 28))
    d.arc([6, 26, 138, 60], start=180, end=360, fill=METAL_LIGHT, width=2)
    d.arc([6, 26, 138, 60], start=0, end=180, fill=METAL_DARK, width=1)

    # Face.
    if happy:
        eyes(d, BW // 2, 70, spread=23, r=10, happy=True)
        mouth(d, BW // 2, 84, w=13, h=7, happy=True)
        blush(d, BW // 2, 84, spread=38, r=7)
    else:
        eyes(d, BW // 2, 70, spread=23, r=9)
        mouth(d, BW // 2, 88, w=10, h=5)
        blush(d, BW // 2, 84, spread=38, r=6, colour=(246, 176, 150))
    return img


# ---------------------------------------------------------------- fruit
#
# All three are 54x54, the size CatchScreen draws a drop. Colour is identity: apple red, berry
# crimson, bonus gold. Faces are open-eyed and level while falling — nothing is happy until it is
# caught, so the reward state never leaks onto the screen early.

FW = FH = 54


def apple():
    img = blank(FW, FH)
    d = ImageDraw.Draw(img)

    # Silhouette: two shoulders over a round body, the notch between them being the apple's tell.
    d.ellipse([5, 12, 49, 50], fill=APPLE, outline=INK)
    d.ellipse([6, 14, 30, 34], fill=APPLE)
    d.ellipse([24, 14, 48, 34], fill=APPLE)

    # Three tones: dark underside, base body, light upper-left.
    d.ellipse([8, 36, 46, 51], fill=APPLE_DARK)
    d.ellipse([7, 15, 47, 47], fill=APPLE)
    d.ellipse([10, 18, 32, 36], fill=APPLE_LIGHT)
    d.ellipse([12, 20, 22, 27], fill=(255, 186, 172))

    # Stem and leaf.
    d.line([27, 15, 27, 8], fill=BROWN_DARK, width=2)
    d.ellipse([28, 4, 42, 13], fill=LEAF, outline=LEAF_DARK)

    # Re-stroke the silhouette so the shading never eats the outline.
    d.arc([5, 12, 49, 50], start=100, end=440, fill=INK)

    eyes(d, 27, 32, spread=8, r=5)
    mouth(d, 27, 41, w=6, h=4)
    return img


def strawberry():
    img = blank(FW, FH)
    d = ImageDraw.Draw(img)

    d.polygon([(6, 16), (48, 16), (43, 34), (27, 52), (11, 34)], fill=BERRY, outline=INK)
    d.ellipse([5, 8, 49, 30], fill=BERRY, outline=INK)
    d.ellipse([8, 24, 46, 44], fill=BERRY_DARK)
    d.ellipse([9, 12, 45, 36], fill=BERRY)
    d.ellipse([11, 13, 28, 24], fill=BERRY_LIGHT)

    # Seeds, small enough to read as texture rather than as eyes.
    for sx, sy in ((13, 26), (22, 24), (33, 26), (42, 27), (17, 36), (28, 34), (38, 37),
                   (23, 44)):
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=SEED)

    # Calyx: a green star over the shoulders.
    d.polygon([(5, 12), (16, 16), (27, 8), (38, 16), (49, 12), (40, 22), (14, 22)],
              fill=LEAF, outline=LEAF_DARK)
    d.line([27, 6, 27, 14], fill=LEAF_DARK, width=2)

    eyes(d, 27, 31, spread=8, r=5)
    mouth(d, 27, 40, w=6, h=4)
    return img


def star():
    img = blank(FW, FH)
    d = ImageDraw.Draw(img)
    cx, cy, outer, inner = 27.0, 28.0, 25.0, 10.5
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = outer if i % 2 == 0 else inner
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    d.polygon(pts, fill=GOLD, outline=INK)

    # One facet, lit from the same corner as everything else.
    d.polygon([(cx, cy - 17), (cx + 7, cy - 2), (cx, cy + 3), (cx - 7, cy - 2)],
              fill=GOLD_LIGHT)
    d.polygon([(cx, cy + 3), (cx + 7, cy - 2), (cx + 5, cy + 9), (cx, cy + 12)],
              fill=GOLD_DARK)

    eyes(d, 27, 26, spread=7, r=4)
    mouth(d, 27, 35, w=5, h=4)
    return img


def apple_settled():
    """The missed fruit, sitting on the grass.

    Same apple, same red, squashed by a few pixels with the stem flopped over: posture is the state.
    Eyes open and level, small round mouth — it is fine, it is not pleased. Nothing here is a strike,
    because tier 1 has no fail state: a fruit that gets past the bucket has simply landed.
    """
    img = blank(FW, FH)
    d = ImageDraw.Draw(img)

    d.ellipse([4, 20, 50, 50], fill=APPLE, outline=INK)
    d.ellipse([5, 21, 30, 38], fill=APPLE)
    d.ellipse([24, 21, 49, 38], fill=APPLE)
    d.ellipse([7, 40, 47, 51], fill=APPLE_DARK)
    d.ellipse([6, 23, 48, 47], fill=APPLE)
    d.ellipse([9, 25, 31, 41], fill=APPLE_LIGHT)
    d.ellipse([11, 27, 21, 33], fill=(255, 186, 172))

    # Stem flopped over: the one asymmetry that says "this one is not going anywhere".
    d.line([26, 21, 36, 15], fill=BROWN_DARK, width=2)
    d.ellipse([33, 9, 46, 17], fill=LEAF, outline=LEAF_DARK)

    d.arc([4, 20, 50, 50], start=100, end=440, fill=INK)

    eyes(d, 27, 35, spread=9, r=4, look=1)
    # A flat little line, not an "o": an open mouth at this size reads as a wince, and a wince is a
    # fail state. This fruit is fine.
    d.line([23, 44, 31, 44], fill=INK, width=2)
    return img


# ---------------------------------------------------------------- effects

def _blob(size, circles, fill, ink=INK):
    """Union of ellipses with a single 1px ink edge.

    Drawing eight outlined circles and then filling them again leaves seams where the arcs overlap,
    and the result reads as a ring of coins. A mask, an erode-by-one and a subtract give exactly one
    1px edge around the whole cloud, which is what "one outline" means for a shape that is not a
    single polygon.
    """
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


def puff(size=112):
    """The catch puff: dust thrown out sideways, drawn behind the bucket so only the outside shows.

    Low and wide with a couple of wisps curling up, deliberately not a closed ring — a ring of equal
    circles reads as a flower, and a flower on the ground in a fruit game is a lie. Dust hugs the
    surface it was kicked off, which is also why the same sprite works at the rim and on the grass.
    """
    c = size / 2.0
    body = [(-46, -4, -14, 34), (-28, -12, 12, 36), (-4, -8, 36, 38), (14, -2, 46, 34),
            (-30, -26, -6, 0), (2, -30, 24, -6), (24, -22, 40, -4)]
    img, _ = _blob((size, size),
                   [(c + a, c + b, c + cc, c + d) for a, b, cc, d in body],
                   (252, 249, 240))

    # A second, tighter union a few pixels up and left: the lit top of the cloud, so it has a form
    # rather than being a flat white smear.
    lit = [(-40, -6, -18, 22), (-24, -12, 8, 28), (-2, -10, 30, 30), (16, -4, 40, 26)]
    hi, _ = _blob((size, size), [(c + a, c + b, c + cc, c + d) for a, b, cc, d in lit],
                  (255, 255, 255), ink=None)
    img.alpha_composite(hi)

    d = ImageDraw.Draw(img)
    # Sparks: the little bit of "yes" the puff needs to be read as good news.
    for dx, dy, r in ((0, -44, 4), (46, -30, 3), (-48, 30, 3), (34, 42, 3)):
        d.polygon([(c + dx, c + dy - r * 2), (c + dx + r * 0.6, c + dy),
                   (c + dx, c + dy + r * 2), (c + dx - r * 0.6, c + dy)], fill=GOLD)
    return img


def cloud(w=132, h=60):
    """Background only: no ink, because an outlined cloud competes with the fruit for attention.

    Same union trick as the puff, so the underside shadow can sit inside one clean silhouette.
    """
    img, _ = _blob((w, h), [(4, 24, 60, 56), (26, 10, 92, 54), (60, 20, 126, 56),
                            (18, 30, 108, 58)], WHITE, ink=None)
    shade, _ = _blob((w, h), [(10, 40, 122, 58)], (226, 240, 252), ink=None)
    img.alpha_composite(shade)
    lit, _ = _blob((w, h), [(6, 24, 58, 48), (28, 12, 90, 48), (62, 22, 124, 48)],
                   WHITE, ink=None)
    img.alpha_composite(lit)
    return img


def tuft(w=44, h=26):
    """A clump of grass blades, so the ground line is not a bare edge."""
    img = blank(w, h)
    d = ImageDraw.Draw(img)
    for x, top, lean in ((8, 4, -3), (16, 0, 0), (24, 6, 3), (33, 3, 2)):
        d.line([x, h - 1, x + lean, top], fill=GRASS_BLADE, width=3)
        d.line([x, h - 1, x + lean, top], fill=GRASS_DARK, width=1)
    d.line([4, h - 2, w - 5, h - 2], fill=GRASS_DARK, width=2)
    return img


# ---------------------------------------------------------------- HUD + cursor
#
# Pictures only. Tier 1 is Band A: a five-year-old reads nothing, so the score is a row of fruit and
# the bonus is a row of stars, and the count is how many of them are lit.

def pip(size=36):
    img = blank(size)
    d = ImageDraw.Draw(img)
    d.ellipse([5, 9, 31, 33], fill=APPLE, outline=INK)
    d.ellipse([6, 10, 17, 22], fill=APPLE_LIGHT)
    d.line([18, 10, 18, 4], fill=BROWN_DARK, width=2)
    d.ellipse([19, 1, 31, 8], fill=LEAF, outline=LEAF_DARK)
    return img


def slot(size=36):
    """An empty HUD socket: cream disc, 1px ink ring, nothing inside.

    The first pass faded the fruit sprite to 22% instead, and a washed-out apple reads as a pale
    apple - a different fruit - not as an empty place. An empty socket cannot be misread.
    """
    img = blank(size)
    d = ImageDraw.Draw(img)
    d.ellipse([5, 5, size - 5, size - 5], fill=CREAM_DARK, outline=INK)
    # Deeper than the cream HUD band it sits on, or an empty slot and a filled one are the same value
    # and the count stops being countable.
    d.ellipse([9, 9, size - 9, size - 9], fill=(226, 198, 150))
    return img


def star_pip(size=36):
    img = blank(size)
    d = ImageDraw.Draw(img)
    cx, cy, outer, inner = size / 2.0, size / 2.0 + 1, size / 2.0 - 2, 6.5
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = outer if i % 2 == 0 else inner
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    d.polygon(pts, fill=GOLD, outline=INK)
    d.polygon([(cx, cy - 10), (cx + 4, cy - 1), (cx, cy + 2), (cx - 4, cy - 1)],
              fill=GOLD_LIGHT)
    return img


def cursor(w=44, h=58):
    """The pointer, drawn as an object so it survives being pasted onto grass.

    Chunky, cream-filled, ink-outlined: the default OS arrow is black and would be the only black
    thing on the screen, which the house style forbids. Drawn at 44x58 rather than the usual 32x44
    because at the smaller size it disappeared into the bucket's dark mouth when it sat near the rim -
    the one thing on screen that must never be missed.
    """
    img = blank(w, h)
    d = ImageDraw.Draw(img)
    d.polygon([(4, 3), (4, 46), (15, 35), (23, 55), (32, 51), (24, 32), (38, 31)],
              fill=CREAM, outline=INK)
    d.polygon([(7, 8), (7, 39), (16, 30), (22, 46), (27, 45), (19, 28), (32, 27)],
              fill=WHITE)
    return img


# ---------------------------------------------------------------- main

def main():
    print("Bucket Catch mockup art ->", os.path.normpath(OUT))
    save(bucket(), "bucket.png")
    save(bucket(happy=True), "bucket_happy.png")
    save(apple(), "apple.png")
    save(strawberry(), "strawberry.png")
    save(star(), "star.png")
    save(apple_settled(), "apple_settled.png")
    save(puff(), "puff.png")
    save(cloud(), "cloud.png")
    save(tuft(), "tuft.png")
    save(pip(), "pip.png")
    save(slot(), "slot.png")
    save(star_pip(), "star_pip.png")
    save(slot(), "star_slot.png")
    save(cursor(), "cursor.png")

    # Contact sheet. Same idea as the shipped generator's preview, but on a sky field so the 1px ink
    # line can be judged against the colour it will actually sit on.
    names = ["bucket.png", "bucket_happy.png", "apple.png", "strawberry.png", "star.png",
             "apple_settled.png", "puff.png", "pip.png", "star_pip.png", "cursor.png",
             "tuft.png", "cloud.png"]
    imgs = [Image.open(os.path.join(OUT, n)).convert("RGBA") for n in names]
    cell_w, cell_h = 200, 200
    sheet = Image.new("RGBA", (cell_w * 6, cell_h * 2), (162, 216, 250, 255))
    for i, im in enumerate(imgs):
        scale = min((cell_w - 24) / im.width, (cell_h - 40) / im.height, 1.6)
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.NEAREST)
        x = (i % 6) * cell_w + (cell_w - im.width) // 2
        y = (i // 6) * cell_h + (cell_h - im.height) // 2
        sheet.alpha_composite(im, (x, y))
    sheet.save(os.path.join(HERE, "preview.png"))
    print("  preview.png (contact sheet, 1200x400)")


if __name__ == "__main__":
    main()
