"""Composes the Bucket Catch mockup from the sprites in ../assets/art/mockup/.

Run:  python make-mockup.py        (after make-art.py)
Outputs ../mockup.png (1280x720) and ../mockup-catch.png (the mechanic strip).

The screen is drawn at the game's own 1280x720 and in the game's own coordinates, so the mockup is a
picture of the build rather than an impression of it: CatchScreen puts the grass line at GROUND_Y=78
from the bottom, which is y=642 here, the bucket's base at 68 from the bottom, which is y=652, and the
catch line at CATCH_Y (74% of the bucket's height), which is y=557. Every number in this file that has
a twin in CatchScreen is named after it; the one deliberate departure is the HUD band, below.

What this screen has to say without a word of text:
  * the bucket is on the cursor's x - so the cursor is drawn, the bucket sits under it, and a dotted
    drop line runs from the falling fruit, past the cursor, into the bucket's mouth. That line is the
    whole verb of tier 1: one number, matched.
  * fruit is in the air at several heights at once, so the player reads "things fall here" rather
    than "one thing fell"
  * a fruit that got past the bucket is on the grass with a little dust and a level face: it landed,
    nothing bad happened. Tier 1 has no fail state and no strike may appear on screen.

House style: one 1px warm-brown ink line, flat fills, contact shadows under everything that stands on
the grass, and a HUD made of pictures because the tier-1 player cannot read.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.normpath(os.path.join(HERE, ".."))
ART = os.path.join(GAME, "assets", "art", "mockup")

W, H = 1280, 720
HUD_H = 96          # the build reserves 118 for a band of text; a picture HUD needs 96, and the
                    # 22px goes back to the sky the player is actually watching
GROUND_Y = 642          # top of the grass, screen coords (game GROUND_Y = 78 from the bottom)
SOIL_H = 14

# Palette, same values as make-art.py.
INK = (0x4C, 0x32, 0x20)
SKY_TOP = (108, 190, 244)
SKY_MID = (158, 209, 245)
SKY_LOW = (214, 240, 255)
GRASS = (104, 182, 68)
GRASS_DARK = (94, 170, 62)
GRASS_LIGHT = (122, 202, 84)
GRASS_SHADE = (72, 140, 48)
GRASS_SOIL = (124, 92, 62)
GRASS_SOIL_DARK = (104, 76, 50)
CREAM = (255, 243, 214)
CREAM_DARK = (236, 214, 168)
GOLD = (255, 200, 62)
WHITE = (255, 255, 255)


def load(name):
    return Image.open(os.path.join(ART, name)).convert("RGBA")


SPRITES = {}


def sprite(name):
    if name not in SPRITES:
        SPRITES[name] = load(name)
    return SPRITES[name]


# ---------------------------------------------------------------- primitives

def paste(canvas, img, cx, bottom=None, top=None, left=None):
    """Paste by centre-x and either bottom or top y: sprite sizes then never leak into layout code."""
    x = int(cx - img.width / 2) if left is None else left
    y = int(bottom - img.height) if bottom is not None else int(top)
    canvas.alpha_composite(img, (x, y))


def shadow(canvas, cx, cy, rx, ry, colour=GRASS_SHADE, alpha=120):
    """Contact shadow: a flat ellipse, no blur, sitting on the ground plane.

    Every sprite that touches the grass gets one, and they all sit at the same y - that shared line is
    what makes the bucket, the fallen apple and the tufts feel like they are on one lawn. The colour
    is a real green, not a translucent grey: grey shadows on grass read as dirt.
    """
    lay = Image.new("RGBA", (rx * 2 + 2, ry * 2 + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.ellipse([1, 1, rx * 2 - 1, ry * 2 - 1], fill=colour + (alpha,))
    canvas.alpha_composite(lay, (int(cx - rx), int(cy - ry)))


def dots(canvas, x, y0, y1, step=13, r=2, colour=INK + (120,)):
    """The drop line: dotted, so it reads as a guide drawn on the scene, not as a solid object.

    The dots are spread evenly between the two ends instead of stepped down from the top, so the last
    one lands exactly on the end point. Stepping leaves a ragged half-step of nothing at the bottom, and
    that gap is precisely what makes the guide look like it stops short of the bucket.
    """
    d = ImageDraw.Draw(canvas)
    n = max(1, int(round((y1 - y0) / float(step))))
    for i in range(n + 1):
        y = y0 + (y1 - y0) * i / float(n)
        d.ellipse([x - r, y - r, x + r, y + r], fill=colour)


def streak(canvas, x, y, length, w=4, alpha=170):
    """One falling-speed mark. Tapered, because a rectangle reads as a scratch."""
    d = ImageDraw.Draw(canvas)
    d.polygon([(x - w / 2, y), (x + w / 2, y), (x + 1, y - length), (x - 1, y - length)],
              fill=(255, 255, 255, alpha))


def dust(canvas, cx, bottom, w, h, alpha=210):
    """Dust: the puff sprite squashed flat and tinted tan.

    Left white and round it reads as a small cloud sitting on the lawn - the shape and the colour are
    both wrong for dust, and both have to change, not just the position.
    """
    p = sprite("puff.png").resize((w, h), Image.NEAREST)
    tint = Image.new("RGBA", p.size, (206, 186, 150, 0))
    tint.putalpha(p.getchannel("A").point(lambda v: int(v * alpha / 255)))
    canvas.alpha_composite(tint, (int(cx - w / 2), int(bottom - h)))


def swoosh(canvas, x, y, length, h=8, alpha=150):
    """A horizontal speed mark, used where the bucket slides sideways."""
    d = ImageDraw.Draw(canvas)
    d.polygon([(x, y - h / 2), (x - length, y), (x, y + h / 2), (x - length * 0.2, y)],
              fill=(255, 255, 255, alpha))


# ---------------------------------------------------------------- the screen

def wavy(canvas, y, amp, period, colour):
    """Fill from a wavy top edge downwards.

    The sky's two tones meet on a wave, not a ruler line: a dead-straight edge across 1280px reads as
    a ledge or a waterline, and this is a sky.
    """
    pts = [(x, y + amp * math.sin(2 * math.pi * x / period)) for x in range(0, W + 6, 6)]
    ImageDraw.Draw(canvas).polygon([(0, H)] + pts + [(W, H)], fill=colour)


def draw_sky(c):
    # The build's sky is a smooth gradient. Flat-fill house style steps it into three tones instead of
    # dithering: the steps are small enough in value to still read as one sky, and the seams wave so
    # neither one becomes a horizon line.
    ImageDraw.Draw(c).rectangle([0, HUD_H, W, H], fill=SKY_TOP)
    wavy(c, 300, 6, 430, SKY_MID)
    wavy(c, 412, 8, 290, SKY_LOW)
    paste(c, sprite("cloud.png"), 205, top=160)
    cloud = sprite("cloud.png").resize((int(132 * 1.2), int(60 * 1.2)), Image.NEAREST)
    paste(c, cloud, 1015, top=136)
    paste(c, sprite("cloud.png"), 596, top=124)


def draw_ground(c):
    d = ImageDraw.Draw(c)
    d.rectangle([0, GROUND_Y, W, H - SOIL_H], fill=GRASS)
    d.rectangle([0, GROUND_Y, W, GROUND_Y + 7], fill=GRASS_LIGHT)
    d.line([0, GROUND_Y, W, GROUND_Y], fill=GRASS_DARK, width=1)
    d.rectangle([0, H - SOIL_H, W, H], fill=GRASS_SOIL)
    d.rectangle([0, H - SOIL_H, W, H - SOIL_H + 3], fill=GRASS_SOIL_DARK)

    # Tufts, placed off the bucket and off the fallen apple so nothing collides with the two things
    # the eye has to read.
    for x, s in ((86, 1.0), (150, 0.8), (368, 1.1), (455, 0.9), (556, 0.75), (838, 1.0),
                 (958, 0.85), (1088, 1.05), (1212, 0.9), (300, 0.7), (1248, 0.7)):
        t = sprite("tuft.png")
        if s != 1.0:
            t = t.resize((int(44 * s), int(26 * s)), Image.NEAREST)
        paste(c, t, x, bottom=GROUND_Y + 8 + int(6 * s))


def draw_landed(c):
    """A fruit that got past the bucket.

    Sitting on the grass, squashed, with its own little dust and a shadow. No X, no red flash, no
    shake: at tier 1 a miss costs nothing, and the picture has to say so before the player learns it.
    """
    cx, cy = 192, GROUND_Y + 12
    # The shadow has to be visible past the sprite's base, or the fruit looks pasted on. Two puffs were
    # tried here and both read as ground clouds - the squashed body and the level face say "landed,
    # fine" on their own, so the dust went.
    shadow(c, cx, cy + 7, 40, 10, alpha=100)
    paste(c, sprite("apple_settled.png"), cx, bottom=cy)


def draw_bucket(c, cx, happy=False, base=GROUND_Y + 10, with_shadow=True):
    if with_shadow:
        # Wide and low, and drawn before the sprite so it spills out either side of the base: the
        # bucket has to look heavy, and a shadow hidden under the sprite looks like no shadow.
        # Wide enough to escape the pail on both sides: at 74 against a 144-wide bucket the shadow was
    # sealed inside the silhouette and the bucket read as a sticker with nothing holding it down.
    shadow(c, cx, base - 2, 86, 11, alpha=120)
    paste(c, sprite("bucket_happy.png" if happy else "bucket.png"), cx, bottom=base)
    return base - 128  # top of the sprite, i.e. top of the handle


def draw_screen():
    c = Image.new("RGBA", (W, H), SKY_LOW + (255,))
    draw_sky(c)
    draw_ground(c)

    # --- the tracked column -------------------------------------------------
    # One fruit, one cursor, one bucket, all on x=700, joined by the drop line. This is the tier: the
    # bucket is on the cursor's x, so the player only ever has to think about one number.
    track_x = 660
    fruit_top = 292
    bucket_base = GROUND_Y + 10
    rim_y = bucket_base - 95           # CatchScreen CATCH_Y: 74% of the bucket's height, so the
                                       # drawn rim and the line a fruit falls in are the same line

    # The line starts a hand's width below the fruit and stops at the rim: touching the fruit made it
    # read as a string the apple was hanging from.
    dots(c, track_x, fruit_top + 78, rim_y - 50)   # stops clear of the arrow's shoulder, not on it
    streak(c, track_x - 2, fruit_top - 3, 26, 5, 190)
    streak(c, track_x + 13, fruit_top + 12, 18, 4, 150)

    # --- the rest of the air ------------------------------------------------
    # Heights deliberately spread from 232 to 500 so the lower half of the playfield is not empty:
    # the player has to see that fruit arrives at eye level, not only at the top of the screen.
    for name, x, y, sl in (("apple.png", 296, 246, 26),
                           ("strawberry.png", 452, 352, 22),
                           ("star.png", 946, 232, 28),
                           ("apple.png", 856, 468, 20),
                           ("strawberry.png", 1080, 396, 20),
                           ("apple.png", 1188, 288, 24),
                           ("strawberry.png", 566, 500, 18)):
        streak(c, x - 2, y - 3, sl, 5, 180)
        streak(c, x + 12, y + 9, sl - 8, 4, 140)
        paste(c, sprite(name), x, top=y)

    # The tracked fruit last, so nothing overlaps the one being read.
    paste(c, sprite("apple.png"), track_x, top=fruit_top)

    draw_landed(c)
    draw_bucket(c, track_x, base=bucket_base)

    # --- cursor -------------------------------------------------------------
    # The tip sits on the bucket's centre line, one short gap above the rim, so the drop line runs
    # fruit -> cursor -> mouth as one chain. Higher detaches it from the bucket; sitting it on the rim
    # hides the mouth, which is the thing being aimed.
    # Flipped, so the point aims down into the mouth instead of up at the sky: the cursor is the
    # thing the bucket follows, and the eye should be able to walk fruit -> dots -> point -> mouth.
    cur = sprite("cursor.png").transpose(Image.FLIP_TOP_BOTTOM)
    c.alpha_composite(cur, (track_x - 4, rim_y - 46))

    draw_hud(c)
    return c


def draw_hud(c):
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, W, HUD_H], fill=CREAM)
    d.rectangle([0, HUD_H - 6, W, HUD_H], fill=CREAM_DARK)
    d.line([0, HUD_H - 1, W, HUD_H - 1], fill=INK, width=1)

    # Caught fruit: five sockets, three filled. The empty slots are sockets, not faded fruit - a
    # washed-out apple reads as a pale apple, which is a lie about what is in the game.
    pip_y = (HUD_H - 36) // 2
    for i in range(5):
        x = 28 + i * 46
        c.alpha_composite(sprite("slot.png"), (x, pip_y))
        if i < 3:
            c.alpha_composite(sprite("pip.png"), (x, pip_y))

    # Bonus stars, right aligned: two earned, one still to come.
    for i in range(3):
        x = W - 28 - 36 - (2 - i) * 46
        c.alpha_composite(sprite("star_slot.png"), (x, pip_y))
        if i < 2:
            c.alpha_composite(sprite("star_pip.png"), (x, pip_y))


# ---------------------------------------------------------------- the mechanic strip
#
# Three beats, left to right: the fruit falls, the bucket arrives under it, the fruit is in the bucket
# with a puff. Same sprites, same palette, same one-number idea - the dotted line is the x the player
# is matching, and it is in every panel so the panels read as one move rather than three pictures.

PANEL_W, PANEL_H = 400, 452
STRIP_W = PANEL_W * 3
STRIP_H = PANEL_H
CAPTION_H = 56
GROUND = PANEL_H - CAPTION_H - 46      # grass line inside a panel


def font(size):
    for name in ("ariblk.ttf", "arialbd.ttf", "segoeuib.ttf"):
        path = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_panel(base, ox, lit, caption, beat):
    d = ImageDraw.Draw(base)
    d.rectangle([ox, 0, ox + PANEL_W, GROUND], fill=SKY_TOP)
    d.rectangle([ox, GROUND - 96, ox + PANEL_W, GROUND], fill=SKY_LOW)
    d.rectangle([ox, GROUND, ox + PANEL_W, GROUND + 46], fill=GRASS)
    d.rectangle([ox, GROUND, ox + PANEL_W, GROUND + 7], fill=GRASS_LIGHT)
    d.rectangle([ox, PANEL_H - CAPTION_H, ox + PANEL_W, PANEL_H], fill=CREAM)

    for i in range(5):
        x = ox + 16 + i * 40
        base.alpha_composite(sprite("slot.png"), (x, 10))
        if i < lit:
            base.alpha_composite(sprite("pip.png"), (x, 10))

    d.line([ox, 0, ox, PANEL_H], fill=INK, width=1)
    d.line([ox + PANEL_W - 1, 0, ox + PANEL_W - 1, PANEL_H], fill=INK, width=1)
    d.text((ox + PANEL_W // 2, PANEL_H - CAPTION_H + 10), caption, font=font(24), fill=INK,
           anchor="mt")

    d.ellipse([ox + PANEL_W - 54, 12, ox + PANEL_W - 18, 48], fill=GOLD, outline=INK)
    d.text((ox + PANEL_W - 36, 31), str(beat), font=font(22), fill=INK, anchor="mm")
    return base


def strip():
    base = Image.new("RGBA", (STRIP_W, STRIP_H), (255, 250, 238, 255))
    base = draw_panel(base, 0, 3, "falling", 1)
    base = draw_panel(base, PANEL_W, 3, "slide under", 2)
    base = draw_panel(base, PANEL_W * 2, 4, "caught", 3)

    g = GROUND

    # --- 1: fruit in the air, bucket still off to the left -------------------
    cx = 236
    paste(base, sprite("strawberry.png"), cx, top=104)
    streak(base, cx - 2, 98, 28, 5, 190)
    streak(base, cx + 13, 110, 20, 4, 150)
    shadow(base, 78, g - 4, 62, 13, alpha=115)
    paste(base, sprite("bucket.png"), 78, bottom=g + 2)

    # --- 2: bucket slid under it, fruit lower --------------------------------
    ox = PANEL_W
    cx = ox + 206
    # The slide is carried by the trail, not by a caption: three speed marks off the back of the
    # bucket and two puffs of dust kicked up off the grass behind it.
    for k in range(3):
        swoosh(base, cx - 84, g - 58 + k * 30, 62 + k * 16, 9, 160)
    dust(base, cx - 112, g + 16, 74, 34)
    dust(base, cx - 156, g + 18, 50, 22, 170)
    shadow(base, cx, g - 4, 72, 14, alpha=115)
    paste(base, sprite("bucket.png"), cx, bottom=g + 2)
    paste(base, sprite("strawberry.png"), cx, top=150)
    streak(base, cx - 2, 144, 22, 5, 190)

    # --- 3: caught ----------------------------------------------------------
    ox = PANEL_W * 2
    cx = ox + 200
    shadow(base, cx, g - 4, 76, 15, alpha=115)
    # The puff is squeezed out at the mouth, not floated behind the bucket: centred on the rim it sat
    # entirely inside the pail's silhouette and vanished. Two small tan puffs escaping past the sides
    # of the rim say "something landed in here" without adding a single word.
    dust(base, cx - 58, g - 96, 34, 18)
    dust(base, cx + 58, g - 96, 30, 16, 190)
    # Fruit behind the bucket: the opaque rim cuts it, so it reads as sitting in the pail.
    paste(base, sprite("apple.png"), cx, bottom=g - 76)
    paste(base, sprite("bucket_happy.png"), cx, bottom=g + 2)
    dd = ImageDraw.Draw(base)
    # Sparkles frame the fruit, not the rim: celebration belongs to the catch, the puffs own the impact.
    for dx, dy, r in ((-40, -150, 5), (42, -142, 4), (58, -88, 3)):
        dd.polygon([(cx + dx, g + dy - r * 2), (cx + dx + r, g + dy),
                    (cx + dx, g + dy + r * 2), (cx + dx - r, g + dy)], fill=GOLD)

    ImageDraw.Draw(base).rectangle([0, 0, STRIP_W - 1, STRIP_H - 1], outline=INK, width=1)
    return base


# ---------------------------------------------------------------- main

def main():
    screen = draw_screen()
    assert (screen.width, screen.height) == (1280, 720), screen.size
    out = os.path.join(GAME, "mockup.png")
    screen.convert("RGB").save(out)
    print("  mockup.png       ", screen.size, "->", out)

    st = strip()
    out2 = os.path.join(GAME, "mockup-catch.png")
    st.convert("RGB").save(out2)
    print("  mockup-catch.png ", st.size, "->", out2)


if __name__ == "__main__":
    main()
