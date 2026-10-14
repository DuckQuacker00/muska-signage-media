#!/usr/bin/env python3
"""Turn the pictures in source/<screen>/ into files the screens can show.

  source/13in3-a/*.png|jpg   ->  screens/13in3-a/NAME.bin   (13.3" Spectra 6, 1200x1600 portrait)
  source/13in3-b/...         ->  screens/13in3-b/NAME.bin
  source/7in5/...            ->  screens/7in5/NAME.png      (7.5" landscape, 800x480)

It also writes previews/<screen>/NAME_preview.png showing roughly how the real
e-paper will look (its colours are duller than a monitor).

Usage (from the top folder of this repo):
    python3 tools/build_media.py                 # everything
    python3 tools/build_media.py 13in3-a         # one screen
Options:
    --flat       no dithering: solid colour blocks (best for text-and-shape posters)
    --boost N    colour/contrast boost before converting, default 1.4 (1.0 = none, 2.0 = strong)
Needs: pip3 install pillow
"""
import os
import sys

from PIL import Image, ImageEnhance, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SIZES = {"13in3": (1200, 1600), "7in5": (800, 480)}

# Panel colours in the order used for quantising, the 4-bit code the screen
# expects for each (from the Seeed_GFX library), and how the real ink looks.
PURE = [(0, 0, 0), (255, 255, 255), (255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255)]
CODES = [0xF, 0x0, 0x6, 0xB, 0x2, 0xD]  # black, white, red, yellow, green, blue
REAL = [(25, 25, 30), (200, 200, 190), (165, 35, 35), (215, 195, 40), (45, 105, 65), (40, 70, 150)]

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp")


def family(screen):
    return "7in5" if screen.startswith("7in5") else "13in3"


def palette_image():
    p = Image.new("P", (1, 1))
    flat = [c for rgb in PURE for c in rgb]
    p.putpalette(flat + [0] * (768 - len(flat)))
    return p


def prepare(im, size, boost):
    im = im.convert("RGB")
    im = ImageOps.fit(im, size, Image.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.0 + (boost - 1) * 0.5)
    im = ImageEnhance.Color(im).enhance(boost)
    return im


def to_indices(im, flat):
    dither_enum = getattr(Image, "Dither", Image)
    d = dither_enum.NONE if flat else dither_enum.FLOYDSTEINBERG
    q = im.quantize(palette=palette_image(), dither=d)
    return q  # pixel values 0..5 = index into PURE


def pack_frame(q):
    """6-colour indices -> the screen's native format: 4 bits per pixel, two pixels
    per byte, left pixel in the high half, row after row, no header."""
    lut = [CODES[i] if i < len(CODES) else 0 for i in range(256)]
    raw = q.point(lut).tobytes()
    even, odd = raw[0::2], raw[1::2]
    return bytes((a << 4) | b for a, b in zip(even, odd))


def unpack_preview(data, size):
    """Inverse of pack_frame, shown with the duller real-ink colours."""
    w, h = size
    inv = {c: i for i, c in enumerate(CODES)}
    out = bytearray()
    for byte in data:
        for nib in (byte >> 4, byte & 15):
            out += bytes(REAL[inv.get(nib, 1)])
    return Image.frombytes("RGB", (w, h), bytes(out))


def build_13in3(screen, src, name, flat, boost):
    size = SIZES["13in3"]
    im = prepare(Image.open(src), size, boost)
    q = to_indices(im, flat)
    data = pack_frame(q)
    assert len(data) == size[0] * size[1] // 2
    out_dir = os.path.join(ROOT, "screens", screen)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, name + ".bin"), "wb") as f:
        f.write(data)
    prev_dir = os.path.join(ROOT, "previews", screen)
    os.makedirs(prev_dir, exist_ok=True)
    unpack_preview(data, size).resize((450, 600), Image.LANCZOS).save(os.path.join(prev_dir, name + "_preview.png"))
    return name + ".bin"


def build_7in5(screen, src, name):
    im = ImageOps.fit(Image.open(src).convert("RGB"), SIZES["7in5"], Image.LANCZOS)
    out_dir = os.path.join(ROOT, "screens", screen)
    os.makedirs(out_dir, exist_ok=True)
    im.save(os.path.join(out_dir, name + ".png"))
    return name + ".png"


def main(argv):
    flat = "--flat" in argv
    boost = 1.4
    rest = []
    skip = False
    for i, a in enumerate(argv):
        if skip:
            skip = False
        elif a == "--boost":
            boost = float(argv[i + 1])
            skip = True
        elif not a.startswith("--"):
            rest.append(a)
    src_root = os.path.join(ROOT, "source")
    screens = rest or sorted(d for d in os.listdir(src_root) if os.path.isdir(os.path.join(src_root, d)))
    made = 0
    for screen in screens:
        folder = os.path.join(src_root, screen)
        if not os.path.isdir(folder):
            print("No folder source/%s" % screen)
            continue
        for f in sorted(os.listdir(folder)):
            if not f.lower().endswith(IMAGE_EXT):
                continue
            name = os.path.splitext(f)[0].replace(" ", "-")
            src = os.path.join(folder, f)
            if family(screen) == "13in3":
                out = build_13in3(screen, src, name, flat, boost)
            else:
                out = build_7in5(screen, src, name)
            print("%-8s %-30s -> screens/%s/%s" % (screen, f, screen, out))
            made += 1
    print("%d picture(s) built. Next: edit screens/<screen>/playlist.txt, then commit and push." % made)


if __name__ == "__main__":
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        sys.exit(__doc__)
    main(sys.argv[1:])
