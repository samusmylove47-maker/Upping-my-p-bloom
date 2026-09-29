"""Chorus (twice). The bloom stage: flowers pop on the beat, Nimbus rains happily, the dial climbs bar by bar."""
from engine import *

WORDS = ["DIG!", "PLANT!", "WATER!", "BLOOM!"]
# (beat, kind, x, [by,] y_or_height, r, colour)
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
CROWD = [(560, 1040, .92, TEAL, PLUM, (198, 134, 92), STRAW, True), (1370, 1040, .92, VIOLET, (60, 120, 100), (141, 92, 62), (230, 120, 100), True),
         (740, 1048, .74, MARIGOLD, DENIM, (250, 205, 170), None, False), (1190, 1048, .74, PINK, LEAF5, (224, 162, 112), STRAW, True),
         (150, 1050, .82, LEAF3, (150, 80, 60), (112, 72, 50), STRAW, True), (1790, 1050, .82, CORAL, VIOLET, (240, 180, 138), None, False)]


def pose(t, t0):
    b = (t - t0) / BEAT; k = int(math.floor(b)); u = b - k
    cur, prev = POSES[k % 4], POSES[(k - 1) % 4]
    w = eoc(u / 0.30)
    hs = [(prev['h'][i][0] + (cur['h'][i][0] - prev['h'][i][0]) * w, prev['h'][i][1] + (cur['h'][i][1] - prev['h'][i][1]) * w) for i in (0, 1)]
    sd = prev['sd'] + (cur['sd'] - prev['sd']) * w
    dy = prev['dy'] + (cur['dy'] - prev['dy']) * w
    if k % 4 == 3:
        dy += -46 * math.sin(math.pi * min(1.0, u / 0.7))
    if k % 4 == 2:
        hs[0] = (hs[0][0] + 9 * math.sin(t * 42), hs[0][1] + 5 * math.cos(t * 38))
    return hs, sd, dy, k % 4


def draw_wren(p, t, t0, cx, by, s, **kw):
    hs, sd, dy, ph = pose(t, t0)
    byy = by + dy * s
    hands = [(cx + h[0] * s, byy + h[1] * s) for h in hs]
    wren(p, cx, byy, s, hands=hands, held=("shovel", 1, sd), smile=1.5 if ph == 3 else 1.0, **kw)


def rays(angle):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m); n = 30
    for i in range(0, n, 2):
        a0 = angle + 2 * math.pi * i / n; a1 = a0 + math.pi / n
        d.polygon([(960, 640), (960 + 2400 * math.cos(a0), 640 + 2400 * math.sin(a0)), (960 + 2400 * math.cos(a1), 640 + 2400 * math.sin(a1))], fill=255)
    return np.asarray(m, dtype=np.float32)[..., None] / 255.0


class Chorus(Scene):
    wipe_color = CORAL

    def __init__(self, sid, second):
        self.id = sid; self.t0 = S0(sid); self.t1 = S1(sid); self.second = second; self.k0 = SEC[sid]["start_bar"]
        self.hits = [bar_t(self.k0 + j) + 0.36 for j in range(8)]

    def _static(self, p):
        for pts, c in [(leaf_pts(-80, 1120, 980, 400, -1.12), LEAF4), (leaf_pts(-40, 1140, 820, 300, -0.85), LEAF3),
                       (leaf_pts(2000, 1120, 980, 400, -2.02), LEAF4), (leaf_pts(1960, 1140, 820, 300, -2.29), LEAF3),
                       (hill_pts(985, 26, 40), LEAF3), (hill_pts(1035, 20, 41), LEAF5)]:
            p.shape(pts, c, shadow=1.0)
        dial(p, 960, 640, 330, needle=None)

    def setup(self):
        self.P, self.T = plate_pt(self._static)
        ys = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        g = np.array((255, 138, 112), np.float32) * (1 - ys) + np.array((255, 214, 150), np.float32) * ys
        self.grad = np.repeat(g, W, axis=1)

    def paper(self, t=0.0):
        m = rays((t - self.t0) * 0.10)
        bg = self.grad * (1 - 0.22 * m) + np.array((255, 236, 190), np.float32) * (0.22 * m)
        fr = self.P + self.T * bg
        p = Paper(); p.img = Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8))
        return p

    def draw(self, p, t):
        t0 = self.t0
        k, u = beat_of(t)
        lt = t - t0
        bi = lt / BEAT                       # beats since the chorus began
        # needle
        draw_needle(p, 960, 640, 330, dial_value(t))
        # Nimbus: turns up on "Rain is real" the first time, already here the second time
        t_in = (LT(self.id, 2) - 0.2) if not self.second else t0
        if t > t_in:
            e = eoc((t - t_in) / 1.2)
            nx = -300 + (230 + 8 * math.sin(t * 1.1) + 300) * e; ny = 330 + 8 * math.sin(t * 1.7)
            nimbus(p, nx, ny, 0.5, col=(224, 216, 244), dark=(190, 180, 222), mood="happy")
            for q in range(9):
                ph = (t * 1.4 + q * 0.37) % 1.0
                x = nx - 110 + q * 26 + 6 * math.sin(q); y = ny + 90 + ph * 210
                if y < 900:
                    p.cap((x, y), (x - 3, y + 16), 4, SKY, shadow=0, hl=False, alpha=1 - ph)
        # flowers (the garden carries over into the second chorus)
        for (b_, kind, *a) in POPS:
            uu = (t - (t0 + b_ * BEAT)) / 0.42
            if self.second and b_ < 14:
                uu = 1.0 + 0 * uu
            if uu <= 0:
                continue
            g = eob(uu)
            if kind == 'air':
                x, y, rr, col = a
                flower(p, x, y, rr * g, col, SUN2, 6, b_ * 0.6 + t * 0.3, shadow=0.6)
            else:
                x, by, h, rr, col = a
                stem_flower(p, x, by, h * g, rr * g, col, lean=(-1) ** b_ * 10, petals=6, rot=t * 0.3)
        # people
        draw_wren(p, t, t0, 350, 1040, 1.3, look=0.2)
        if self.second:
            join = LT(self.id, 5)
            for j, (x, by, s, shirt, bib, skin, hatc, hat) in enumerate(CROWD):
                e = eob((t - (join + j * BEAT)) / 0.4)
                if e > 0.02:
                    draw_wren(p, t, t0, x, by, s * e, shirt=shirt, bib=bib, skin=skin, hatc=hatc or STRAW, hat=hat)
        hop = 14 * abs(math.sin(math.pi * u))
        bl = None
        tb = self.hits[0]
        if t >= tb:
            v = eob((t - tb) / 0.5) * 1.3
            bl = v if v > 0.05 else None
        if self.second:
            bl = 1.3
        sprig(p, 1600, 1046 - hop, 1.4, look=-0.3, happy=1.6, bloom=bl, tilt=4 * math.sin(t * 3))
        if k % 4 == 2:
            for q in range(5):
                ph = ((t * 3 + q * 0.2) % 1.0)
                p.ell(1600 + 182 - 20 * q + 30 * ph, 1046 - 180 + 200 * ph, 6, 9, SKY, shadow=0.2, sh_off=(1, 2), sh_blur=2)
        # confetti on each bar's hit
        d = ImageDraw.Draw(p.img)
        for j, th in enumerate(self.hits):
            dt = t - th
            if dt < 0 or dt > 1.7:
                continue
            rnd = random.Random(100 + j + (10 if self.second else 0))
            n = 64 if j in (0, 4) else 34
            for i in range(n):
                ang = rnd.uniform(-2.6, -0.5); sp = rnd.uniform(420, 1100)
                x = 960 + rnd.uniform(-160, 160) + math.cos(ang) * sp * dt
                y = 400 + math.sin(ang) * sp * dt + 0.5 * 1500 * dt * dt
                col = rnd.choice(FCOLS); r = rnd.uniform(6, 12) * (1 - dt / 1.9); rot = rnd.uniform(0, 3) + dt * rnd.uniform(-8, 8)
                if r <= 1 or y > 1100:
                    continue
                d.polygon(ell_pts(x, y, r, r * 0.55, rot, n=10, jit=0), fill=col)
        # caption, dig/plant/water/bloom tag, gang shouts
        caption(p, t, y=124)
        kk = int(math.floor(bi)); uu2 = bi - kk
        wd = WORDS[kk % 4]; sz = int(46 * (1 + 0.30 * (1 - min(1, uu2 * 3)) ** 2))
        if bi >= 0:
            p.tag(960, 1012, wd, sz, fill=CORAL if wd == "BLOOM!" else CREAM, ink=CREAM if wd == "BLOOM!" else INK)
        shouts = [(0, "Bloom!", 1560, 300), (1, "Nope!", 1620, 330), (4, "Bloom!", 1560, 300), (5, "Room!", 1600, 330)]
        for (li, s_, x, y) in shouts:
            word_tag(p, x, y, s_, 54, t, LT(self.id, li) + 1.3, life=0.7, fill=CORAL, ink=CREAM, rot=-0.05)
