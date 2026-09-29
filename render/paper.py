"""Paper-cut renderer kit for the P(Bloom) video. PIL + numpy, 2x supersampled."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H, S = 1920, 1080, 2
import os, glob


def _find_fredoka():
    """Fredoka One (SIL Open Font License). `pip install font-fredoka-one`, or set FREDOKA_TTF to any .ttf."""
    env = os.environ.get("FREDOKA_TTF")
    if env and os.path.exists(env):
        return env
    try:
        import font_fredoka_one
        hits = glob.glob(os.path.join(os.path.dirname(font_fredoka_one.__file__), "files", "*.ttf"))
        if hits:
            return hits[0]
    except ImportError:
        pass
    for pat in ("/usr/share/fonts/**/Fredoka*.ttf", os.path.expanduser("~/Library/Fonts/Fredoka*.ttf"), "C:/Windows/Fonts/Fredoka*.ttf"):
        hits = glob.glob(pat, recursive=True)
        if hits:
            return hits[0]
    raise SystemExit("Fredoka font not found. Run: pip install font-fredoka-one   (or set FREDOKA_TTF=/path/to/font.ttf)")


FRED = _find_fredoka()

# palette -- "Dawn Paper"
INK = (52, 34, 74)
CREAM = (255, 246, 229)
PEACH = (255, 216, 168)
APRICOT = (255, 190, 140)
MARIGOLD = (255, 182, 39)
SUN2 = (255, 209, 102)
CORAL = (255, 107, 90)
PINK = (255, 143, 177)
VIOLET = (123, 94, 167)
PLUM = (92, 70, 128)
STORM = (109, 90, 140)
STORM_D = (72, 56, 104)
NIGHT_T = (35, 22, 60)
NIGHT_B = (90, 62, 122)
LEAF1 = (168, 213, 162)
LEAF2 = (124, 192, 138)
LEAF3 = (79, 163, 124)
LEAF4 = (46, 133, 112)
LEAF5 = (31, 106, 90)
TEAL = (43, 179, 163)
DENIM = (61, 110, 168)
SKIN = (240, 180, 138)
STRAW = (242, 193, 78)
WOOD = (181, 118, 58)
RED = (229, 72, 77)
SKY = (142, 201, 240)

_fc = {}


def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ------------------------------------------------------------------ geometry
def ell_pts(cx, cy, rx, ry, rot=0.0, n=72, jit=0.004, seed=0):
    rnd = random.Random(seed + int(cx * 7 + cy * 13))
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        j = 1 + rnd.uniform(-jit, jit)
        x, y = rx * math.cos(a) * j, ry * math.sin(a) * j
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def rrect_pts(x0, y0, x1, y1, r, n=10):
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    pts = []
    for (cx, cy, a0) in [(x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)]:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def capsule_pts(p0, p1, w, n=8):
    (x0, y0), (x1, y1) = p0, p1
    a = math.atan2(y1 - y0, x1 - x0)
    r = w / 2
    pts = []
    for i in range(n + 1):
        t = a - math.pi / 2 + math.pi * i / n
        pts.append((x1 + r * math.cos(t), y1 + r * math.sin(t)))
    for i in range(n + 1):
        t = a + math.pi / 2 + math.pi * i / n
        pts.append((x0 + r * math.cos(t), y0 + r * math.sin(t)))
    return pts


def rot_pts(pts, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def bez(p0, p1, p2, n=16):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]


def leaf_pts(cx, cy, length, width, rot):
    """leaf with base at (cx,cy) pointing along rot"""
    a = bez((0, 0), (length * 0.45, -width), (length, 0))
    b = bez((length, 0), (length * 0.45, width), (0, 0))
    pts = a + b[1:]
    c, s = math.cos(rot), math.sin(rot)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


def hill_pts(base, amp, seed, waves=3, x0=-30, x1=W + 30):
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(waves)]
    fr = [rnd.uniform(0.0016, 0.0042) * (1 + k * 0.9) for k, _ in enumerate(ph)]
    am = [amp / (1 + k * 0.8) for k in range(waves)]
    pts = []
    x = x0
    while x <= x1:
        y = base + sum(am[k] * math.sin(fr[k] * x * 2 + ph[k]) for k in range(waves))
        pts.append((x, y))
        x += 10
    pts += [(x1, H + 40), (x0, H + 40)]
    return pts


def annular(cx, cy, r0, r1, a0, a1, n=30):
    top = [(cx + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    bot = [(cx + r0 * math.cos(math.radians(a1 - (a1 - a0) * i / n)), cy + r0 * math.sin(math.radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    return top + bot


# ------------------------------------------------------------------ canvas
def shift(m, dx, dy):
    out = Image.new("L", m.size, 0)
    out.paste(m, (int(dx), int(dy)))
    return out


class Paper:
    def __init__(self, bg=CREAM):
        self.img = Image.new("RGB", (W * S, H * S), bg)

    # fill may be an RGB tuple or ('grad', top, bottom, y0, y1)
    def shape(self, polys, fill, shadow=1.0, hl=True, alpha=1.0, sh_off=(3, 6), sh_blur=7):
        if polys and isinstance(polys[0], tuple):
            polys = [polys]
        xs = [p[0] for poly in polys for p in poly]
        ys = [p[1] for poly in polys for p in poly]
        pad = 34
        x0, y0 = max(0, int(min(xs) - pad)), max(0, int(min(ys) - pad))
        x1, y1 = min(W, int(max(xs) + pad)), min(H, int(max(ys) + pad))
        if x1 <= x0 or y1 <= y0:
            return
        w, h = (x1 - x0) * S, (y1 - y0) * S
        m = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(m)
        for poly in polys:
            d.polygon([((x - x0) * S, (y - y0) * S) for x, y in poly], fill=255)
        self._compose(m, x0, y0, fill, shadow, hl, alpha, sh_off, sh_blur)

    def _compose(self, m, x0, y0, fill, shadow, hl, alpha, sh_off, sh_blur):
        w, h = m.size
        box = (x0 * S, y0 * S, x0 * S + w, y0 * S + h)
        region = self.img.crop(box)
        if shadow > 0:
            sm = shift(m, sh_off[0] * S, sh_off[1] * S).filter(ImageFilter.GaussianBlur(sh_blur * S / 2))
            sm = sm.point(lambda v: int(v * 0.34 * shadow * alpha))
            region = Image.composite(Image.new("RGB", (w, h), (28, 12, 44)), region, sm)
        if isinstance(fill, tuple) and len(fill) == 3 and isinstance(fill[0], int):
            layer = Image.new("RGB", (w, h), fill)
            base = fill
        else:
            _, c0, c1, gy0, gy1 = fill
            ys = (np.arange(h) / S + y0 - gy0) / max(1, (gy1 - gy0))
            ys = np.clip(ys, 0, 1)[:, None, None]
            arr = np.array(c0, np.float32) * (1 - ys) + np.array(c1, np.float32) * ys
            arr = np.repeat(arr, w, axis=1).astype(np.uint8)
            layer = Image.fromarray(arr)
            base = c0
        ma = m.point(lambda v: int(v * alpha)) if alpha < 1 else m
        region = Image.composite(layer, region, ma)
        if hl:
            rim = ImageChops.subtract(m, shift(m, 1.6 * S, 1.8 * S))
            rim = rim.point(lambda v: int(v * 0.55 * alpha))
            region = Image.composite(Image.new("RGB", (w, h), mix(base, (255, 255, 255), 0.55)), region, rim)
        self.img.paste(region, box[:2])

    def ell(self, cx, cy, rx, ry, fill, **kw):
        self.shape(ell_pts(cx, cy, rx, ry, kw.pop("rot", 0.0)), fill, **kw)

    def rrect(self, x0, y0, x1, y1, r, fill, **kw):
        self.shape(rrect_pts(x0, y0, x1, y1, r), fill, **kw)

    def cap(self, p0, p1, w, fill, **kw):
        self.shape(capsule_pts(p0, p1, w), fill, **kw)

    def text(self, x, y, s, size, fill, path=FRED, anchor="mm", shadow=1.0, hl=True, tracking=0, alpha=1.0):
        f = font(path, size * S)
        bb = f.getbbox(s, anchor=anchor)
        pad = 30
        x0, y0 = int(x + bb[0] / S - pad), int(y + bb[1] / S - pad)
        x1, y1 = int(x + bb[2] / S + pad), int(y + bb[3] / S + pad)
        x0c, y0c, x1c, y1c = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        if x1c <= x0c or y1c <= y0c:
            return
        m = Image.new("L", ((x1c - x0c) * S, (y1c - y0c) * S), 0)
        d = ImageDraw.Draw(m)
        if tracking:
            total = sum(f.getlength(ch) for ch in s) + tracking * S * (len(s) - 1)
            cx = (x - x0c) * S - (total / 2 if anchor[0] == "m" else 0)
            for ch in s:
                d.text((cx, (y - y0c) * S), ch, font=f, fill=255, anchor="l" + anchor[1])
                cx += f.getlength(ch) + tracking * S
        else:
            d.text(((x - x0c) * S, (y - y0c) * S), s, font=f, fill=255, anchor=anchor)
        self._compose(m, x0c, y0c, fill, shadow, hl, alpha, (3, 5), 6)

    def tag(self, cx, cy, s, size=44, fill=CREAM, ink=INK, padx=34, pady=18, path=FRED, rot=0.0):
        f = font(path, size * S)
        w = f.getlength(s) / S + padx * 2
        h = size * 1.05 + pady * 2
        pts = rrect_pts(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, min(28, h / 2))
        if rot:
            pts = rot_pts(pts, cx, cy, rot)
        self.shape(pts, fill)
        self.text(cx, cy + 2, s, size, ink, path=path, shadow=0.0, hl=False)

    def finish(self, grain=3.2, vig=0.20, seed=1):
        im = self.img.resize((W, H), Image.LANCZOS)
        a = np.asarray(im).astype(np.float32)
        rng = np.random.default_rng(seed)
        a += rng.normal(0, grain, (H, W, 1))
        # paper fibers
        fib = rng.normal(0, 1, (H, W)).astype(np.float32)
        fib = np.asarray(Image.fromarray(((fib * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) - 128
        a += fib[..., None] * 0.10
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r2 = ((xx / W - 0.5) * 1.6) ** 2 + ((yy / H - 0.5) * 1.0) ** 2
        a *= (1 - vig * r2)[..., None]
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------ props & characters
def flower(p, cx, cy, r, col, center=SUN2, petals=6, rot=0.0, shadow=0.6):
    for i in range(petals):
        a = rot + 2 * math.pi * i / petals
        px, py = cx + math.cos(a) * r * 0.52, cy + math.sin(a) * r * 0.52
        p.shape(ell_pts(px, py, r * 0.48, r * 0.30, a), col, shadow=shadow, hl=True, sh_off=(1.5, 3), sh_blur=3)
    p.ell(cx, cy, r * 0.30, r * 0.30, center, shadow=shadow, sh_off=(1, 2), sh_blur=2)


def stem_flower(p, x, base_y, height, r, col, lean=0, leaf=LEAF3, center=SUN2, petals=6, rot=0.0):
    tip = (x + lean, base_y - height)
    mid = (x + lean * 0.3, base_y - height * 0.5)
    pts = bez((x, base_y), mid, tip, 10)
    for i in range(len(pts) - 1):
        p.cap(pts[i], pts[i + 1], max(4, r * 0.16), mix(leaf, INK, 0.12), shadow=0.25, hl=False, sh_off=(1, 2), sh_blur=2)
    p.shape(leaf_pts(mid[0], mid[1], r * 1.5, r * 0.55, -0.7 if lean >= 0 else -2.4), leaf, shadow=0.4, sh_off=(1, 2), sh_blur=2)
    flower(p, tip[0], tip[1], r, col, center, petals, rot)


def sun(p, cx, cy, r, rays=22, col=MARIGOLD, ray=SUN2, ray_len=1.55):
    for i in range(rays):
        a = 2 * math.pi * i / rays
        a0, a1 = a - math.pi / rays * 0.55, a + math.pi / rays * 0.55
        L = r * (ray_len if i % 2 == 0 else ray_len * 0.82)
        tri = [(cx + math.cos(a0) * r * 0.9, cy + math.sin(a0) * r * 0.9), (cx + math.cos(a) * L, cy + math.sin(a) * L),
               (cx + math.cos(a1) * r * 0.9, cy + math.sin(a1) * r * 0.9)]
        p.shape(tri, ray if i % 2 == 0 else mix(ray, col, 0.5), shadow=0.25, sh_off=(1, 3), sh_blur=4)
    p.ell(cx, cy, r, r, col, shadow=0.5)
    p.ell(cx, cy, r * 0.82, r * 0.82, mix(col, (255, 240, 200), 0.25), shadow=0.0, hl=False)


def cloud_polys(cx, cy, s):
    return [ell_pts(cx - 150 * s, cy + 20 * s, 95 * s, 70 * s, seed=1), ell_pts(cx - 40 * s, cy - 40 * s, 120 * s, 100 * s, seed=2),
            ell_pts(cx + 90 * s, cy - 10 * s, 115 * s, 90 * s, seed=3), ell_pts(cx + 190 * s, cy + 25 * s, 85 * s, 62 * s, seed=4),
            rrect_pts(cx - 220 * s, cy + 20 * s, cx + 250 * s, cy + 90 * s, 42 * s)]


def small_cloud(p, cx, cy, s, col=CREAM, shadow=0.7):
    p.shape(cloud_polys(cx, cy, s), col, shadow=shadow)


def shovel(p, hand, tip_dir, length=210, blade=(46, 62), handle_col=WOOD, metal=(150, 172, 196)):
    """handle from hand along tip_dir (radians) with blade at end"""
    hx, hy = hand
    ex, ey = hx + math.cos(tip_dir) * length, hy + math.sin(tip_dir) * length
    p.cap((hx, hy), (ex, ey), 11, handle_col, shadow=0.6)
    # D handle
    bx, by = hx - math.cos(tip_dir) * 14, hy - math.sin(tip_dir) * 14
    p.cap((bx, by), (bx + math.cos(tip_dir + 1.57) * 30, by + math.sin(tip_dir + 1.57) * 30), 10, handle_col, shadow=0.5, hl=False)
    bw, bh = blade
    bl = [(-bw / 2, 0), (bw / 2, 0), (bw / 2 + 4, bh * 0.55), (0, bh), (-bw / 2 - 4, bh * 0.55)]
    ang = tip_dir - math.pi / 2
    c, s = math.cos(ang), math.sin(ang)
    pts = [(ex + x * c - y * s, ey + x * s + y * c) for x, y in bl]
    p.shape(pts, metal, shadow=0.6)
    hl = [(ex + x * c - y * s, ey + x * s + y * c) for x, y in [(-bw / 5, 6), (bw / 8, 6), (bw / 8, bh * 0.6), (-bw / 5, bh * 0.5)]]
    p.shape(hl, mix(metal, (255, 255, 255), 0.4), shadow=0, hl=False)


def wren(p, cx, by, s=1.0, hands=None, held=None, look=0.0, smile=1.0, hat=True, blink=False,
         shirt=CORAL, bib=DENIM, skin=SKIN, hatc=STRAW, sh=1.0):
    """Original character: Wren the gardener. cx,by = centre/feet. hands=((lx,ly),(rx,ry)) absolute.
    held = ('shovel', hand_index, dir) """
    def P(dx, dy):
        return (cx + dx * s, by + dy * s)
    # boots
    for dx in (-26, 26):
        p.rrect(*(P(dx - 24, -22) + P(dx + 24, 2)), 12 * s, (74, 50, 40), shadow=0.6)
    # legs (overalls)
    p.rrect(*(P(-44, -120) + P(44, -14)), 22 * s, bib, shadow=0.7)
    p.cap(P(0, -110), P(0, -20), 4 * s, mix(bib, INK, 0.25), shadow=0, hl=False)
    # torso shirt + bib
    p.rrect(*(P(-50, -212) + P(50, -100)), 30 * s, shirt, shadow=0.7)
    p.rrect(*(P(-34, -190) + P(34, -100)), 14 * s, bib, shadow=0.4)
    for dx in (-30, 30):
        p.cap(P(dx, -210), P(dx * 0.6, -186), 9 * s, bib, shadow=0.3, hl=False)
    p.rrect(*(P(-14, -160) + P(14, -136)), 6 * s, mix(bib, INK, 0.2), shadow=0, hl=False)
    # arms
    shd = [P(-52, -190), P(52, -190)]
    if hands is None:
        hands = [P(-70, -110), P(70, -110)]
    for i in (0, 1):
        p.cap(shd[i], hands[i], 26 * s, shirt, shadow=0.7)
        p.ell(hands[i][0], hands[i][1], 15 * s, 15 * s, skin, shadow=0.6)
    if held:
        kind, idx, ang = held
        shovel(p, hands[idx], ang, length=205 * s, blade=(46 * s, 62 * s))
        p.ell(hands[idx][0], hands[idx][1], 15 * s, 15 * s, skin, shadow=0.0, hl=True)
    # head sits straight on the shoulders (no neck piece)
    hx, hy = P(0, -260)
    p.ell(hx, hy, 46 * s, 48 * s, skin, shadow=0.7)
    p.ell(hx - 28 * s, hy + 12 * s, 9 * s, 6 * s, mix(skin, CORAL, 0.35), shadow=0, hl=False)
    p.ell(hx + 28 * s, hy + 12 * s, 9 * s, 6 * s, mix(skin, CORAL, 0.35), shadow=0, hl=False)
    ex = look * 5 * s
    for dx in (-17, 17):
        if blink:
            p.cap((hx + dx * s - 8 * s, hy - 2 * s), (hx + dx * s + 8 * s, hy - 2 * s), 4 * s, INK, shadow=0, hl=False)
        else:
            p.ell(hx + dx * s + ex, hy - 2 * s, 5.5 * s, 7 * s, INK, shadow=0, hl=False)
            p.ell(hx + dx * s + ex + 2 * s, hy - 5 * s, 2 * s, 2 * s, CREAM, shadow=0, hl=False)
    sm = bez((hx - 15 * s, hy + 18 * s), (hx, hy + (18 + 16 * smile) * s), (hx + 15 * s, hy + 18 * s), 8)
    for i in range(len(sm) - 1):
        p.cap(sm[i], sm[i + 1], 3.6 * s, INK, shadow=0, hl=False)
    if hat:
        p.shape(ell_pts(hx, hy - 44 * s, 84 * s, 16 * s, seed=5), hatc, shadow=0.8)
        p.shape(ell_pts(hx, hy - 58 * s, 44 * s, 34 * s, seed=6), mix(hatc, (255, 255, 255), 0.12), shadow=0.6)
        p.rrect(hx - 43 * s, hy - 60 * s, hx + 43 * s, hy - 46 * s, 6 * s, CORAL, shadow=0, hl=False)
        # little sprig in hat band
        p.shape(leaf_pts(hx + 30 * s, hy - 56 * s, 30 * s, 12 * s, -0.9), LEAF3, shadow=0.3, sh_off=(1, 2), sh_blur=2)


def sprig(p, cx, by, s=1.0, look=0.0, happy=1.0, bloom=None, tilt=0.0, badge=True):
    """Original character: Sprig, a watering-can helper bot with a seedling on top."""
    def P(dx, dy):
        return (cx + dx * s, by + dy * s)
    # wheels
    for dx in (-38, 38):
        p.ell(*P(dx, -18), 20 * s, 20 * s, (74, 60, 92), shadow=0.6)
        p.ell(*P(dx, -18), 8 * s, 8 * s, (150, 140, 170), shadow=0, hl=False)
    # spout
    sp = [P(50, -78), P(118, -132), P(132, -120), P(66, -52)]
    p.shape(sp, mix(TEAL, INK, 0.12), shadow=0.6)
    p.ell(*P(130, -128), 16 * s, 12 * s, mix(TEAL, INK, 0.2), rot=-0.6, shadow=0.4)
    # handle
    hpts = bez(P(-52, -120), P(-118, -128), P(-52, -46), 14)
    for i in range(len(hpts) - 1):
        p.cap(hpts[i], hpts[i + 1], 15 * s, mix(TEAL, INK, 0.2), shadow=0.5)
    # body
    p.rrect(*(P(-62, -132) + P(62, -22)), 30 * s, TEAL, shadow=0.8)
    p.rrect(*(P(-46, -96) + P(46, -34)), 18 * s, mix(TEAL, (255, 255, 255), 0.22), shadow=0.0, hl=False)
    # lid
    p.rrect(*(P(-44, -146) + P(44, -128)), 9 * s, mix(TEAL, INK, 0.2), shadow=0.5)
    # name badge: Sprig is the Sonnet 5.5 helper
    if badge:
        bx, byy = P(41, -47)
        p.ell(bx, byy, 21 * s, 21 * s, CREAM, shadow=0.5)
        p.ell(bx, byy, 17 * s, 17 * s, CORAL, shadow=0, hl=False)
        p.text(bx, byy + 1 * s, "5.5", max(8, int(19 * s)), CREAM, shadow=0, hl=False)
    # face
    for dx in (-22, 22):
        p.ell(*P(dx, -98), 17 * s, 19 * s, CREAM, shadow=0, hl=False)
        p.ell(P(dx, -98)[0] + look * 5 * s, P(dx, -98)[1] + 2 * s, 9 * s, 10 * s, INK, shadow=0, hl=False)
        p.ell(P(dx, -98)[0] + look * 5 * s + 3 * s, P(dx, -98)[1] - 2 * s, 3 * s, 3 * s, CREAM, shadow=0, hl=False)
    sm = bez(P(-13, -66), P(0, -66 + 14 * happy), P(13, -66), 8)
    for i in range(len(sm) - 1):
        p.cap(sm[i], sm[i + 1], 3.6 * s, INK, shadow=0, hl=False)
    # seedling
    top = P(0, -146)
    p.cap(top, (top[0] + tilt * s, top[1] - 44 * s), 7 * s, LEAF4, shadow=0.4, hl=False)
    tp = (top[0] + tilt * s, top[1] - 44 * s)
    if bloom is None:
        p.shape(leaf_pts(tp[0], tp[1], 44 * s, 17 * s, -0.4), LEAF2, shadow=0.5, sh_off=(1, 3), sh_blur=3)
        p.shape(leaf_pts(tp[0], tp[1], 44 * s, 17 * s, -2.75), LEAF3, shadow=0.5, sh_off=(1, 3), sh_blur=3)
    else:
        p.shape(leaf_pts(top[0], top[1] - 22 * s, 36 * s, 14 * s, -0.2), LEAF2, shadow=0.4, sh_off=(1, 2), sh_blur=2)
        p.shape(leaf_pts(top[0], top[1] - 22 * s, 36 * s, 14 * s, -2.94), LEAF3, shadow=0.4, sh_off=(1, 2), sh_blur=2)
        flower(p, tp[0], tp[1] - 4 * s, 30 * s * bloom, PINK, SUN2, 6, 0.3)


def nimbus(p, cx, cy, s=1.0, col=STORM, dark=STORM_D, mood="grumpy", lightning=False):
    """Original character: Nimbus, a big grumpy cloud (who comes round in the end)."""
    for dx, dy in [(6, 34)]:
        p.shape(cloud_polys(cx + dx * s, cy + dy * s, s), dark, shadow=0.0, hl=False)
    p.shape(cloud_polys(cx, cy, s), col, shadow=0.9)
    fx, fy = cx + 20 * s, cy + 30 * s
    if mood == "grumpy":
        for sx in (-1, 1):
            p.ell(fx + sx * 62 * s, fy, 26 * s, 30 * s, CREAM, shadow=0, hl=False)
            p.ell(fx + sx * 62 * s - sx * 3 * s, fy + 5 * s, 13 * s, 15 * s, INK, shadow=0, hl=False)
            p.cap((fx + sx * 100 * s, fy - 46 * s), (fx + sx * 30 * s, fy - 26 * s), 12 * s, INK, shadow=0, hl=False)
        fr = bez((fx - 44 * s, fy + 74 * s), (fx, fy + 44 * s), (fx + 44 * s, fy + 74 * s), 10)
        for i in range(len(fr) - 1):
            p.cap(fr[i], fr[i + 1], 8 * s, INK, shadow=0, hl=False)
    else:
        for sx in (-1, 1):
            arc = bez((fx + sx * 62 * s - 24 * s, fy + 6 * s), (fx + sx * 62 * s, fy - 26 * s), (fx + sx * 62 * s + 24 * s, fy + 6 * s), 8)
            for i in range(len(arc) - 1):
                p.cap(arc[i], arc[i + 1], 8 * s, INK, shadow=0, hl=False)
        sm = bez((fx - 40 * s, fy + 50 * s), (fx, fy + 84 * s), (fx + 40 * s, fy + 50 * s), 10)
        for i in range(len(sm) - 1):
            p.cap(sm[i], sm[i + 1], 8 * s, INK, shadow=0, hl=False)
        for sx in (-1, 1):
            p.ell(fx + sx * 100 * s, fy + 44 * s, 22 * s, 14 * s, mix(col, PINK, 0.6), shadow=0, hl=False)
    if lightning:
        bolt = [(cx + 120 * s, cy + 100 * s), (cx + 60 * s, cy + 230 * s), (cx + 105 * s, cy + 228 * s), (cx + 40 * s, cy + 380 * s),
                (cx + 170 * s, cy + 200 * s), (cx + 122 * s, cy + 200 * s), (cx + 190 * s, cy + 100 * s)]
        p.shape(bolt, MARIGOLD, shadow=0.5)


def dial(p, cx, cy, r, needle=0.5, label=True, small=False):
    """The Bloom-o-meter. needle 0..1 (storm -> sun). Dimensionless on purpose: it is a prop, not a probability."""
    p.rrect(cx - r * 0.34, cy + r * 0.05, cx + r * 0.34, cy + r * 0.86, r * 0.08, mix(PLUM, INK, 0.2), shadow=0.9)
    p.rrect(cx - r * 0.52, cy + r * 0.78, cx + r * 0.52, cy + r * 0.92, r * 0.06, mix(PLUM, INK, 0.35), shadow=0.9)
    p.ell(cx, cy, r * 1.06, r * 1.06, mix(PLUM, INK, 0.25), shadow=1.0)
    p.ell(cx, cy, r * 0.98, r * 0.98, CREAM, shadow=0.0)
    cols = [PLUM, VIOLET, PINK, CORAL, MARIGOLD, SUN2, LEAF2, LEAF3]
    n = len(cols)
    for i, c in enumerate(cols):
        a0 = 180 + 180 * i / n + 0.8
        a1 = 180 + 180 * (i + 1) / n - 0.8
        p.shape(annular(cx, cy, r * 0.60, r * 0.90, a0, a1, 10), c, shadow=0.3, sh_off=(1, 2), sh_blur=2)
    for i in range(0, 17):
        a = math.radians(180 + 180 * i / 16)
        r0, r1 = r * 0.50, r * (0.56 if i % 2 else 0.58)
        p.cap((cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a)), r * 0.018, INK, shadow=0, hl=False)
    if needle is not None:
        ang = math.radians(180 + 180 * needle)
        tip = (cx + r * 0.84 * math.cos(ang), cy + r * 0.84 * math.sin(ang))
        b1 = (cx + r * 0.06 * math.cos(ang + 1.57), cy + r * 0.06 * math.sin(ang + 1.57))
        b2 = (cx + r * 0.06 * math.cos(ang - 1.57), cy + r * 0.06 * math.sin(ang - 1.57))
        p.shape([b1, tip, b2], CORAL, shadow=0.8)
        p.ell(cx, cy, r * 0.11, r * 0.11, INK, shadow=0.6)
        p.ell(cx, cy, r * 0.045, r * 0.045, CREAM, shadow=0, hl=False)
    if label:
        p.text(cx, cy + r * 0.34, "P(BLOOM)", int(r * 0.19), INK, shadow=0.0, hl=False)
