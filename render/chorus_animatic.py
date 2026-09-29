"""15-second chorus animatic (8 bars @128 BPM).

Usage:  python render/chorus_animatic.py test 0.5 7.5     (PNG stills into out/)
        python render/chorus_animatic.py full out/chorus_silent.mp4
The temp beat (render/tempbeat.py) is a placeholder, not the song."""
import sys, math, random, time, os, subprocess
import numpy as np
from PIL import Image, ImageDraw
import paper
paper.S = 1
from paper import *

BPM, FPS, DUR = 128, 30, 15.0
SPB = 60.0 / BPM
BAR = SPB * 4
NF = int(DUR * FPS)
OW, OH = 1280, 720
FC = [CORAL, PINK, MARIGOLD, VIOLET, CREAM, (255, 160, 122)]
CAPS = ["I'm upping my P-BLOOM!", "Nothing's written, nothing's doomed!", "Rain is real and so is spring —",
        "Grab a shovel, do the thing!", "I'm upping my P-BLOOM!", "Humans and helpers, fill the room!",
        "Not “it's fine” — it's ours to do —", "The dial moves when we move!"]
WORDS = ["DIG!", "PLANT!", "WATER!", "BLOOM!"]
TARGET = [0.30, 0.42, 0.52, 0.62, 0.70, 0.78, 0.86, 0.93]
POPS = [(3, 'air', 700, 330, 56, PINK), (4, 'stem', 130, 1030, 300, 40, CORAL), (5, 'air', 1240, 330, 56, VIOLET),
        (6, 'stem', 250, 1030, 240, 36, PINK), (7, 'air', 610, 480, 64, CORAL), (8, 'stem', 1790, 1030, 320, 42, MARIGOLD),
        (9, 'air', 1320, 470, 60, PINK), (10, 'stem', 1690, 1030, 220, 34, VIOLET), (11, 'air', 840, 268, 44, MARIGOLD),
        (12, 'stem', 470, 1030, 200, 34, PINK), (13, 'air', 1090, 262, 46, CORAL), (14, 'stem', 1470, 1030, 250, 38, CORAL),
        (15, 'air', 560, 700, 50, VIOLET), (16, 'stem', 640, 1030, 180, 30, MARIGOLD), (17, 'air', 1360, 690, 52, MARIGOLD),
        (18, 'stem', 1290, 1030, 210, 32, VIOLET), (19, 'air', 505, 300, 48, PINK), (20, 'air', 1420, 300, 48, CORAL),
        (21, 'stem', 360, 1030, 320, 44, VIOLET), (22, 'air', 1500, 560, 46, PINK), (23, 'air', 420, 560, 46, MARIGOLD),
        (24, 'stem', 1560, 1030, 300, 40, PINK), (25, 'air', 960, 200, 40, SUN2), (26, 'stem', 60, 1030, 250, 34, MARIGOLD),
        (27, 'air', 1660, 420, 44, VIOLET), (28, 'air', 260, 430, 44, CORAL), (29, 'stem', 1880, 1030, 240, 32, CORAL)]
POSES = [dict(h=[(-40, -130), (55, -150)], sd=1.25, dy=0), dict(h=[(-30, -40), (70, -120)], sd=-1.15, dy=16),
         dict(h=[(-70, -205), (70, -125)], sd=-1.15, dy=0), dict(h=[(-123, -292), (112, -282)], sd=-1.45, dy=-6)]
CROWD = [(560, 1040, .92, TEAL, PLUM, (198, 134, 92), STRAW, True, 16), (1370, 1040, .92, VIOLET, (60, 120, 100), (141, 92, 62), (230, 120, 100), True, 17),
         (740, 1048, .74, MARIGOLD, DENIM, (250, 205, 170), None, False, 18), (1190, 1048, .74, PINK, LEAF5, (224, 162, 112), STRAW, True, 19),
         (150, 1050, .82, LEAF3, (150, 80, 60), (112, 72, 50), STRAW, True, 20), (1790, 1050, .82, CORAL, VIOLET, (240, 180, 138), None, False, 21)]


def eob(x):
    x = min(1.0, max(0.0, x)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def eoc(x):
    x = min(1.0, max(0.0, x)); return 1 - (1 - x) ** 3


def draw_static(p):
    for pts, c in [(leaf_pts(-80, 1120, 980, 400, -1.12), LEAF4), (leaf_pts(-40, 1140, 820, 300, -0.85), LEAF3),
                   (leaf_pts(2000, 1120, 980, 400, -2.02), LEAF4), (leaf_pts(1960, 1140, 820, 300, -2.29), LEAF3),
                   (hill_pts(985, 26, 40), LEAF3), (hill_pts(1035, 20, 41), LEAF5)]:
        p.shape(pts, c, shadow=1.0)
    dial(p, 960, 640, 330, needle=None)


_G = {}


def init():
    if _G:
        return
    B, Wt = [], None
    outs = []
    for bgc in [(0, 0, 0), (255, 255, 255)]:
        p = Paper(bgc)
        draw_static(p)
        outs.append(np.asarray(p.img).astype(np.float32))
    _G['P'] = outs[0]
    _G['A'] = np.clip((outs[1] - outs[0]).mean(axis=2) / 255.0, 0, 1)[..., None]
    ys = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    _G['grad'] = np.array((255, 138, 112), np.float32) * (1 - ys) + np.array((255, 214, 150), np.float32) * ys
    _G['grad'] = np.repeat(_G['grad'], W, axis=1)
    rng = np.random.default_rng(5)
    _G['noise'] = rng.normal(0, 2.6, (OH + 64, OW + 64, 1)).astype(np.float32)
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    r2 = ((xx / OW - 0.5) * 1.6) ** 2 + ((yy / OH - 0.5) * 1.0) ** 2
    _G['vig'] = (1 - 0.20 * r2)[..., None]


def rays(angle):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m); n = 30
    for i in range(0, n, 2):
        a0 = angle + 2 * math.pi * i / n; a1 = a0 + math.pi / n
        d.polygon([(960, 640), (960 + 2400 * math.cos(a0), 640 + 2400 * math.sin(a0)), (960 + 2400 * math.cos(a1), 640 + 2400 * math.sin(a1))], fill=255)
    return np.asarray(m, dtype=np.float32)[..., None] / 255.0


def needle_val(t):
    hits = [(4 * j + 3) * SPB for j in range(8)]
    lv = [0.22] + TARGET
    j = -1
    for k, th in enumerate(hits):
        if t >= th:
            j = k
    if j < 0:
        return 0.22 + 0.012 * math.sin(t * 9)
    v0, v1 = lv[j], lv[j + 1]
    u = (t - hits[j]) / 0.6
    return v0 + (v1 - v0) * eob(u) + 0.004 * math.sin(t * 31)


def pose(t, sc=1.0):
    b = t / SPB; k = int(b); u = b - k
    cur, prev = POSES[k % 4], POSES[(k - 1) % 4]
    w = eoc(u / 0.30)
    hs = []
    for i in (0, 1):
        hs.append((prev['h'][i][0] + (cur['h'][i][0] - prev['h'][i][0]) * w, prev['h'][i][1] + (cur['h'][i][1] - prev['h'][i][1]) * w))
    sd = prev['sd'] + (cur['sd'] - prev['sd']) * w
    dy = prev['dy'] + (cur['dy'] - prev['dy']) * w
    if k % 4 == 3:
        dy += -46 * math.sin(math.pi * min(1.0, u / 0.7))
    if k % 4 == 2:
        hs[0] = (hs[0][0] + 9 * math.sin(t * 42), hs[0][1] + 5 * math.cos(t * 38))
    return hs, sd, dy, k % 4


def draw_wren(p, t, cx, by, s, **kw):
    hs, sd, dy, ph = pose(t)
    byy = by + dy * s
    hands = [(cx + h[0] * s, byy + h[1] * s) for h in hs]
    wren(p, cx, byy, s, hands=hands, held=("shovel", 1, sd), smile=1.5 if ph == 3 else 1.0, **kw)


def confetti(p, t):
    d = ImageDraw.Draw(p.img)
    for j in range(8):
        th = (4 * j + 3) * SPB; dt = t - th
        if dt < 0 or dt > 1.7:
            continue
        rnd = random.Random(100 + j)
        n = 64 if j in (3, 7) else 40
        for i in range(n):
            ang = rnd.uniform(-2.6, -0.5); sp = rnd.uniform(420, 1100)
            x = 960 + rnd.uniform(-160, 160) + math.cos(ang) * sp * dt
            y = 400 + math.sin(ang) * sp * dt + 0.5 * 1500 * dt * dt
            col = rnd.choice(FC); r = rnd.uniform(6, 12) * (1 - dt / 1.9); rot = rnd.uniform(0, 3) + dt * rnd.uniform(-8, 8)
            if r <= 1 or y > 1100:
                continue
            pts = ell_pts(x, y, r, r * 0.55, rot, n=10, jit=0)
            d.polygon(pts, fill=col)


def render(i):
    init()
    t = i / FPS
    b = t / SPB; k = int(b); u = b - k; bar = min(7, int(t / BAR)); ub = (t - bar * BAR) / BAR
    m = rays(t * 0.10)
    bg = _G['grad'] * (1 - 0.22 * m) + np.array((255, 236, 190), np.float32) * (0.22 * m)
    fr = _G['P'] + _G['A'] * bg
    p = Paper(); p.img = Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8))
    # needle
    v = needle_val(t); ang = math.radians(180 + 180 * v); cx, cy, r = 960, 640, 330
    tip = (cx + r * 0.84 * math.cos(ang), cy + r * 0.84 * math.sin(ang))
    p.shape([(cx + r * 0.06 * math.cos(ang + 1.57), cy + r * 0.06 * math.sin(ang + 1.57)), tip, (cx + r * 0.06 * math.cos(ang - 1.57), cy + r * 0.06 * math.sin(ang - 1.57))], CORAL, shadow=0.8)
    p.ell(cx, cy, r * 0.11, r * 0.11, INK, shadow=0.6); p.ell(cx, cy, r * 0.045, r * 0.045, CREAM, shadow=0, hl=False)
    # nimbus (friendly) arrives bar 1
    if t > BAR:
        e = eoc((t - BAR) / 1.2)
        nx = -300 + (230 + 8 * math.sin(t * 1.1) + 300) * e; ny = 330 + 8 * math.sin(t * 1.7)
        nimbus(p, nx, ny, 0.5, col=(224, 216, 244), dark=(190, 180, 222), mood="happy")
        for q in range(9):
            ph = (t * 1.4 + q * 0.37) % 1.0
            x = nx - 110 + q * 26 + 6 * math.sin(q); y = ny + 90 + ph * 210
            if y < 900:
                p.cap((x, y), (x - 3, y + 16), 4, SKY, shadow=0, hl=False, alpha=1 - ph)
    # flowers popping
    for (bi, kind, *a) in POPS:
        uu = (t - bi * SPB) / 0.42
        if uu <= 0:
            continue
        g = eob(uu)
        if kind == 'air':
            x, y, rr, col = a
            flower(p, x, y, rr * g, col, SUN2, 6, bi * 0.6 + t * 0.3, shadow=0.6)
        else:
            x, by, h, rr, col = a
            stem_flower(p, x, by, h * g, rr * g, col, lean=(-1) ** bi * 10, petals=6, rot=t * 0.3)
    # characters
    draw_wren(p, t, 350, 1040, 1.3, look=0.2)
    for (x, by, s, shirt, bib, skin, hatc, hat, kb) in CROWD:
        e = eob((t - kb * SPB) / 0.4)
        if e > 0.02:
            draw_wren(p, t, x, by, s * e, shirt=shirt, bib=bib, skin=skin, hatc=hatc or STRAW, hat=hat)
    hop = 14 * abs(math.sin(math.pi * u)) if t > 0 else 0
    th0 = 3 * SPB; bl = eob((t - th0) / 0.5) * 1.3 if t >= th0 else 0
    sprig(p, 1600, 1046 - hop, 1.4, look=-0.3, happy=1.6, bloom=bl if bl > 0.05 else None, tilt=4 * math.sin(t * 3))
    if k % 4 == 2:
        for q in range(5):
            ph = ((t * 3 + q * 0.2) % 1.0)
            p.ell(1600 + 182 - 20 * q + 30 * ph, 1046 - 180 + 200 * ph, 6, 9, SKY, shadow=0.2, sh_off=(1, 2), sh_blur=2)
    confetti(p, t)
    # caption + word tag
    cap = CAPS[bar]
    f100 = font(FRED, 100).getlength(cap)
    size = min(116, int(100 * 1700 / f100))
    size = int(size * (1 + 0.10 * (1 - min(1, ub * 6)) ** 3))
    p.text(966, 132, cap, size, CORAL, shadow=0.0, hl=False)
    p.text(960, 124, cap, size, INK)
    wd = WORDS[k % 4]; sz = int(46 * (1 + 0.30 * (1 - min(1, u * 3)) ** 2))
    if wd == "BLOOM!":
        p.tag(960, 1012, wd, sz, fill=CORAL, ink=CREAM)
    else:
        p.tag(960, 1012, wd, sz)
    if bar == 7:
        q = eob((t - 7 * BAR) / 0.5)
        if q > 0:
            p.tag(1560, 250, "still needs you", int(40 * q), fill=(255, 226, 150), rot=-0.05)
    # camera pulse
    z = 1 + 0.018 * (1 - u) ** 2 + (0.02 * (1 - u) ** 2 if k % 4 == 3 else 0)
    w_, h_ = W / z, H / z
    x0, y0 = 960 - w_ / 2, 620 - h_ / 2
    y0 = min(max(0, y0), H - h_)
    out = p.img.resize((OW, OH), Image.LANCZOS, box=(x0, y0, x0 + w_, y0 + h_))
    a = np.asarray(out).astype(np.float32)
    rng = np.random.default_rng(i)
    oy, ox = int(rng.integers(0, 64)), int(rng.integers(0, 64))
    a = (a + _G['noise'][oy:oy + OH, ox:ox + OW]) * _G['vig']
    fade = min(1.0, t / 0.12) * min(1.0, (DUR - t) / 0.25)
    return (np.clip(a, 0, 255) * fade).astype(np.uint8)


if __name__ == "__main__":
    mode = sys.argv[1]
    OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
    if mode == "test":
        for ts in sys.argv[2:]:
            t0 = time.time(); fr = render(int(float(ts) * FPS))
            Image.fromarray(fr).save(f"{OUT}/a_{float(ts):05.2f}.png"); print(ts, "%.2fs" % (time.time() - t0), flush=True)
    else:
        from multiprocessing import Pool
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                               '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', sys.argv[2]], stdin=subprocess.PIPE)
        t0 = time.time()
        with Pool(2, initializer=init) as pool:
            for n, fr in enumerate(pool.imap(render, range(NF), chunksize=3)):
                ff.stdin.write(fr.tobytes())
                if n % 30 == 0:
                    print(f"frame {n}/{NF} {time.time() - t0:.0f}s", flush=True)
        ff.stdin.close(); ff.wait(); print("done", time.time() - t0, flush=True)
