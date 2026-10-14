#!/usr/bin/env python3
"""Make a test picture (1200x1600) with arrows and colour bars to check a screen's
orientation. Usage: python3 tools/make_test_pattern.py source/13in3-a/test.png LABEL"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 1600
out = sys.argv[1] if len(sys.argv) > 1 else "test.png"
label = sys.argv[2] if len(sys.argv) > 2 else "SCREEN"


def font(size):
    for p in ("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
d.rectangle([0, 0, W - 1, H - 1], outline="black", width=16)
bars = [("black", "white"), ("red", "white"), ("yellow", "black"), ("green", "white"), ("blue", "white")]
bh = 150
for i, (c, t) in enumerate(bars):
    y = 260 + i * bh
    d.rectangle([60, y, W - 60, y + bh - 10], fill=c)
    d.text((90, y + 30), c.upper(), fill=t, font=font(80))
d.text((60, 40), "TOP EDGE", fill="black", font=font(70))
d.polygon([(W // 2, 130), (W // 2 - 60, 210), (W // 2 + 60, 210)], fill="red")
d.text((60, 1100), "READ ME", fill="black", font=font(150))
d.text((60, 1280), label, fill="blue", font=font(140))
d.text((60, 1470), "BOTTOM", fill="black", font=font(70))
d.text((W - 330, 60), "L  R", fill="green", font=font(70))
im.save(out)
print("wrote", out)
