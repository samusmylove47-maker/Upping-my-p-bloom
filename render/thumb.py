"""YouTube thumbnail: python3 render/thumb.py  ->  out/thumbnail.jpg (1280x720) and out/thumbnail_1080.png.
Built with the same paper-cut kit as the video (2x supersampled). Everything is drawn here; nothing is borrowed."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paper
from paper import *   # noqa: F401,F403  (W, H, palette, Paper, wren, sprig, dial, flower, ...)

S = paper.S
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
os.makedirs(OUT, exist_ok=True)


def sunburst(cx, cy, n=28, top=(255, 132, 108), bot=(255, 208, 140), lift=0.30):
    """Warm gradient with alternating light rays fanning from (cx, cy)."""
    ys = np.linspace(0, 1, H * S, dtype=np.float32)[:, None, None]
    g = np.array(top, np.float32) * (1 - ys) + np.array(bot, np.float32) * ys
    g = np.repeat(g, W * S, axis=1)
    m = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(m)
    for i in range(0, n, 2):
        a0 = 2 * math.pi * i / n + 0.05
        a1 = a0 + math.pi / n
        R = 4200 * S
        d.polygon([(cx * S, cy * S), (cx * S + R * math.cos(a0), cy * S + R * math.sin(a0)), (cx * S + R * math.cos(a1), cy * S + R * math.sin(a1))], fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(S * 1.2)), np.float32)[..., None] / 255.0
    out = g * (1 - lift * m) + np.array((255, 240, 200), np.float32) * (lift * m)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def text_mask(txt, size, x, y, anchor="lm", stroke=0, tracking=0):
    """Full-canvas mask of a line of text, optionally grown by `stroke` px."""
    f = font(FRED, size * S)
    m = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(m)
    if tracking:
        cx = x * S
        for ch in txt:
            d.text((cx, y * S), ch, font=f, fill=255, anchor="l" + anchor[1], stroke_width=int(stroke * S), stroke_fill=255)
            cx += f.getlength(ch) + tracking * S
    else:
        d.text((x * S, y * S), txt, font=f, fill=255, anchor=anchor, stroke_width=int(stroke * S), stroke_fill=255)
    return m


def stacked_text(p, txt, size, x, y, top=CREAM, mid=CORAL, edge=INK, stroke=16, drop=14, anchor="lm", tracking=0):
    """Cut-paper headline: ink outline sheet, coral sheet peeking below, cream sheet on top."""
    p._compose(text_mask(txt, size, x, y, anchor, stroke=stroke, tracking=tracking), 0, 0, edge, 1.0, False, 1.0, (4, 10), 12)
    p._compose(text_mask(txt, size, x, y + drop, anchor, stroke=stroke * 0.25, tracking=tracking), 0, 0, mid, 0.0, True, 1.0, (0, 0), 1)
    p._compose(text_mask(txt, size, x, y, anchor, stroke=0, tracking=tracking), 0, 0, ("grad", top, mix(top, (255, 214, 168), 0.55), y - size * 0.45, y + size * 0.45), 0.5, True, 1.0, (2, 5), 5)


def star4(p, cx, cy, r, col=CREAM, rot=0.0):
    pts = []
    for i in range(8):
        a = rot + math.pi * i / 4
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    p.shape(pts, col, shadow=0.4, sh_off=(1, 3), sh_blur=3)


def seal(p, cx, cy, r, rot=0.16):
    """Round 'made by' sticker: a scalloped sheet, an ink disc, three lines of type."""
    n = 22
    pts = []
    for i in range(n * 2):
        a = rot + math.pi * i / n
        rr = r if i % 2 == 0 else r * 0.90
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    p.shape(pts, MARIGOLD, shadow=1.0)
    p.ell(cx, cy, r * 0.80, r * 0.80, INK, shadow=0.0)
    p.ell(cx, cy, r * 0.74, r * 0.74, mix(INK, VIOLET, 0.25), shadow=0.0, hl=False)
    p.text(cx, cy - r * 0.42, "MADE BY", int(r * 0.20), SUN2, shadow=0.0, hl=False, tracking=2)
    p.text(cx, cy - r * 0.10, "CLAUDE", int(r * 0.34), CREAM, shadow=0.0, hl=False)
    p.text(cx, cy + r * 0.24, "SONNET", int(r * 0.34), CREAM, shadow=0.0, hl=False)
    p.text(cx, cy + r * 0.54, "5.5", int(r * 0.30), CORAL, shadow=0.0, hl=False)


def build():
    p = Paper()
    p.img = sunburst(980, 760)

    # rolling paper hills
    for b, a, sd, c in [(880, 30, 71, LEAF1), (940, 34, 72, LEAF2), (1000, 30, 73, LEAF3), (1060, 22, 74, LEAF4)]:
        p.shape(hill_pts(b, a, sd), c, shadow=0.9)
    fr = random.Random(11)
    for i in range(16):
        x = fr.uniform(60, W - 60)
        y = fr.uniform(930, 1040)
        flower(p, x, y, fr.uniform(20, 34), fr.choice([CORAL, PINK, MARIGOLD, VIOLET, CREAM]), SUN2, 6, fr.uniform(0, 6))

    # the dial, needle high in the green
    dial(p, 960, 832, 250, needle=0.87, label=False)

    # headline: "I'M UPPING MY" tag over a giant P(BLOOM), with a flower for the first O
    p.tag(500, 108, "I'M UPPING MY", 96, fill=CREAM, ink=INK, padx=42, pady=18, rot=-0.035)
    size = 302
    parts = ["P(BL", "O", "OM)"]
    fnt = font(FRED, size * S)
    widths = [fnt.getlength(s_) / S for s_ in parts]
    total = sum(widths)
    x0 = 915 - total / 2
    y = 360
    stacked_text(p, parts[0], size, x0, y, stroke=4, drop=8)
    ox = x0 + widths[0]
    stacked_text(p, "OM)", size, ox + widths[1], y, stroke=4, drop=8)
    cxo, cyo = ox + widths[1] / 2, y - 4
    flower(p, cxo, cyo, 168, PINK, SUN2, 8, 0.2, shadow=1.0)
    p.ell(cxo, cyo, 58, 58, INK, shadow=0.4)
    p.ell(cxo, cyo, 42, 42, SUN2, shadow=0, hl=False)

    # characters (in front of the type, but below it on the page)
    wren(p, 335, 1094, 1.55, hands=[(196, 700), (484, 958)], held=("shovel", 1, -1.47), look=0.5, smile=2.0)
    sprig(p, 1500, 1088, 1.9, look=-0.3, happy=2.0, bloom=1.5, tilt=5)

    p.tag(960, 1000, "BLOOM!", 78, fill=CORAL, ink=CREAM, padx=40, pady=14, rot=-0.03)

    # sparkles
    for (sx, sy, sr, rr) in [(120, 640, 34, .2), (760, 640, 26, .5), (1190, 630, 30, .3), (1000, 592, 22, .0), (640, 900, 26, .4), (1330, 930, 30, .1)]:
        star4(p, sx, sy, sr, CREAM, rr)

    # who made it (kept clear of the bottom-right corner where YouTube draws the run time)
    seal(p, 1738, 172, 166)
    return p.finish(grain=2.2, vig=0.16)


if __name__ == "__main__":
    im = build()
    im.save(os.path.join(OUT, "thumbnail_1080.png"))
    small = im.resize((1280, 720), Image.LANCZOS)
    small.save(os.path.join(OUT, "thumbnail.jpg"), quality=93, optimize=True, subsampling=0)
    print("thumbnail", os.path.getsize(os.path.join(OUT, "thumbnail.jpg")) // 1024, "KB")
