"""Regenerate every web image from the original photography.

Run this only when the source art in the "Bargain Vape" folder changes:

    python scripts/build-assets.py

Requires Pillow:  pip install pillow

Product photography keeps its original white studio background — the site
presents each shot as a rounded white tile against the dark page. Only the logo
crops carry a black backdrop, which the stylesheet blends out with
mix-blend-mode: screen so the neon glow survives.
"""

import os
from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.dirname(HERE), "Bargain Vape")
OUT = os.path.join(HERE, "assets", "img")


# Anything darker than this is the product itself. A looser threshold also
# catches the soft drop shadow, which sits to one side and would drag the
# measured centre off — that is what makes a product look off-centre in its tile.
PRODUCT = 185


def frame(im, ratio, pad=0.09):
    """Centre the product on a white canvas of `ratio`.

    The studio shots have inconsistent margins; this makes every tile frame the
    product identically so the grid reads as one set.

    The product is located by its own pixels, ignoring the soft drop shadow —
    measuring the shadow would drag the apparent centre to one side. But the
    crop window is then taken from the *original* image around that centre, so
    the shadow is carried along instead of being sliced off at the product's
    edge.
    """
    im = im.convert("RGB")
    mask = im.convert("L").point(lambda v: 255 if v < PRODUCT else 0, mode="L")
    box = mask.getbbox()
    if not box:
        box = (0, 0, im.width, im.height)

    l, t, r, b = box
    cw, ch = r - l, b - t
    cx, cy = (l + r) / 2.0, (t + b) / 2.0

    # Window sized to hold the product plus padding, at the target ratio.
    tw = max(cw / (1 - 2 * pad), (ch / (1 - 2 * pad)) * ratio)
    th = tw / ratio

    # Take that window from the source, centred on the product, so surrounding
    # pixels (the shadow) come with it. Where the window runs past the edge of
    # the source, only the overlapping part is pasted — asking PIL to crop
    # out of bounds would pad with black rather than the studio white.
    left, top = int(round(cx - tw / 2)), int(round(cy - th / 2))
    w, h = int(round(tw)), int(round(th))
    canvas = Image.new("RGB", (w, h), (255, 255, 255))

    sx0, sy0 = max(0, left), max(0, top)
    sx1, sy1 = min(im.width, left + w), min(im.height, top + h)
    if sx1 > sx0 and sy1 > sy0:
        canvas.paste(im.crop((sx0, sy0, sx1, sy1)), (sx0 - left, sy0 - top))
    return canvas


def save(im, path, max_w, quality=84):
    im = im.convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * (max_w / im.width))), Image.LANCZOS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, "WEBP", quality=quality, method=6)
    print("wrote", os.path.relpath(path, HERE), im.size)


def load(*parts):
    return Image.open(os.path.join(SRC, *parts))


# ---------------------------------------------------------------- brand marks
# The supplied "Logos (2).png" is the monogram on a genuinely transparent
# background, so it drops straight onto the dark page with no blend tricks.
mono = Image.open(os.path.join(SRC, "Logos", "Bargain Vape Logos (2).png")).convert("RGBA")
box = mono.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
if box:
    mono = mono.crop(box)

mono_out = os.path.join(OUT, "brand", "logo-icon.webp")
os.makedirs(os.path.dirname(mono_out), exist_ok=True)
mono_web = mono.resize((420, int(mono.height * (420 / mono.width))), Image.LANCZOS)
mono_web.save(mono_out, "WEBP", quality=92, method=6)
print("wrote", os.path.relpath(mono_out, HERE), mono_web.size)

# The full lockup supplied as "Logos (3).png" sits on an opaque white panel that
# would read as a white block on the dark page, and cropping the lockup out of
# the packaging art leaves a visible rectangular seam. So the site pairs this
# transparent monogram with the brand name set in type instead.

for size, name in [(32, "favicon-32.png"), (180, "apple-touch-icon.png"), (512, "icon-512.png")]:
    canvas = Image.new("RGBA", (size, size), (7, 7, 11, 255))
    scale = (size * 0.80) / max(mono.width, mono.height)
    resized = mono.resize((max(1, int(mono.width * scale)), max(1, int(mono.height * scale))), Image.LANCZOS)
    canvas.alpha_composite(resized, ((size - resized.width) // 2, (size - resized.height) // 2))
    path = os.path.join(OUT, "brand", name)
    canvas.convert("RGB").save(path)
    print("wrote", os.path.relpath(path, HERE), canvas.size)


# ------------------------------------------------------------- display cases
CASES = {
    "case-greenpurple": "Green and purple box front top view.png",
    "case-orangegreen": "OrangeGreen box.png",
    "case-pinkblue": "PinkBlue box.png",
}
CASE_BACKS = {
    "case-greenpurple-back": "green purple box backside.png",
    "case-orangegreen-back": "orange green box backside.png",
    "case-pinkblue-back": "pink blue backside.png",
}
CASE_RATIO = 4 / 3
for slug, fname in {**CASES, **CASE_BACKS}.items():
    save(frame(load("Boxes", fname), CASE_RATIO), os.path.join(OUT, "cases", slug + ".webp"), 1200, 85)


# ------------------------------------------------------------------- flavors
# (folder, sleeve front, sleeve back, flavor-box back)
# (folder, sleeve front, sleeve back, 10-count flavour box)
# Most flavours were shot as a three-quarter "side view" of the box; Jokerz
# Candy only has a straight-on box front, which frames the same information.
FLAVORS = {
    "green-crack": ("Green Crack", "Green Crack Sleeve.png", "Green Crack Sleeve Back side.png", "Green Crack side view box.png"),
    "joker-candy": ("Joker Candy", "Joker Candy Sleeve Front.png", "Joker Candy Sleeve Back.png", "Joker Candy box Front.png"),
    "purple-urkle": ("Purple Urkle", "purple urkle sleeve front.png", "Purple Urkle sleeve back.png", "Purple urkle box side view.png"),
    "tropical-sunrise": ("Tropical Sunrise", "Tropical Sunrise front view.png", "Tropical Sunrise sleeve back.png", "Tropical Sunrise Box Side View.png"),
    "mimosa": ("Mimosa", "Mimosa Sleeve Front.png", "Mimosa Sleeve Back.png", "Mimosa Box Side view.png"),
    "slurricane": ("Slurricane", "Slurricane Sleeve Front.png", "Slurricane Sleeve Back.png", "Slurricane Side View.png"),
    "pink-lemonade": ("Pink Lemonade", "Pink lemonade sleeve front.png", "pink lemonade sleeve back.png", "Pink Lemonade Box side.png"),
    "gelato": ("Gelato", "Gelato sleeve front.png", "gelato sleeve back.png", "Gelato box side view.png"),
    "berry-punch": ("Berry Punch", "berry punch sleeve front.png", "berry punch sleeve back.png", "berry punch box side view.png"),
}
SLEEVE_RATIO = 3 / 4   # tall tile suits the sleeve
# All three views share one tile, so the box uses the same ratio. It is a
# landscape object in a portrait frame, so it gets a tighter pad to fill more.
for slug, (folder, front, back, box) in FLAVORS.items():
    save(frame(load(folder, front), SLEEVE_RATIO), os.path.join(OUT, "products", slug + ".webp"), 620, 84)
    save(frame(load(folder, back), SLEEVE_RATIO), os.path.join(OUT, "products", slug + "-back.webp"), 620, 84)
    save(frame(load(folder, box), SLEEVE_RATIO, pad=0.05), os.path.join(OUT, "products", slug + "-box.webp"), 620, 84)


# ----------------------------------------------------------------- hardware
save(frame(load("Slurricane", "Bargain Vape Pen.png"), 3 / 4, pad=0.12),
     os.path.join(OUT, "brand", "pen.webp"), 620, 86)


# --------------------------------------------------------------------- hero
# Doubles as the video's poster frame, so it must look finished on its own.
HERO_SRC = os.path.join(os.path.expanduser("~"), "Downloads", "Bargain Vape",
                        "Bargain Vape hero image.png")
if os.path.exists(HERO_SRC):
    hero = Image.open(HERO_SRC)
    save(hero, os.path.join(OUT, "hero", "hero.webp"), 1600, 82)
    save(hero, os.path.join(OUT, "hero", "hero-900.webp"), 900, 80)
else:
    print("NOTE: hero source not found, skipped:", HERO_SRC)

print("\nDONE — if any image's proportions changed, update the matching")
print('width="" / height="" attributes in the HTML so the page does not jump on load.')
