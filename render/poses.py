"""Dance-move strip: dig / plant / water / BLOOM, with Sprig keeping time."""
import sys, os
from PIL import Image
from paper import *

POSES = [dict(h=[(-40, -130), (55, -150)], sd=1.25, dy=0), dict(h=[(-30, -40), (70, -120)], sd=-1.15, dy=16),
         dict(h=[(-70, -205), (70, -125)], sd=-1.15, dy=0), dict(h=[(-123, -292), (112, -282)], sd=-1.45, dy=-6)]
LABELS = ["DIG!", "PLANT!", "WATER!", "BLOOM!"]


def strip():
    p = Paper()
    p.shape([(0, 0), (W, 0), (W, H), (0, H)], ("grad", (255, 168, 150), (255, 226, 184), 100, 800), shadow=0, hl=False)
    for a0 in range(0, 360, 24):
        pass
    p.shape(hill_pts(742, 16, 71), LEAF3, shadow=0.9)
    p.shape(hill_pts(800, 12, 72), LEAF5, shadow=0.9)
    for i in range(4):
        cx = 215 + i * 450
        po = POSES[i]
        by = 770 + po['dy']
        hands = [(cx + h[0], by + h[1]) for h in po['h']]
        wren(p, cx, by, 1.0, hands=hands, held=("shovel", 1, po['sd']), smile=1.6 if i == 3 else 1.0, look=0.2)
        sprig(p, cx + 215, 786 - (14 if i % 2 else 0), 0.62, look=-0.5, happy=1.5, bloom=(0.9 if i == 3 else None), tilt=3)
        p.tag(cx, 300, LABELS[i], 56, fill=CORAL if i == 3 else CREAM, ink=CREAM if i == 3 else INK)
    for x, y, r, c in [(cx - 130, 500, 24, PINK), (cx + 120, 470, 20, MARIGOLD), (cx - 60, 400, 18, VIOLET), (cx + 80, 390, 26, PINK)]:
        flower(p, x, y, r, c, SUN2, 6, x / 50)
    return p.finish()


if __name__ == "__main__":
    im = strip().crop((0, 190, 1920, 850)).resize((1280, 440), Image.LANCZOS)
    os.makedirs("out", exist_ok=True)
    im.save("out/poses.jpg", quality=90)
    print("poses ok")
