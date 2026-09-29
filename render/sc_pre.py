"""Pre-chorus (twice): worry becomes fuel -> point it at something and go -> Ready? Ready? -> One! Two! Three! -> the whole crowd is up.
The second time the same words play out with gardeners peeking over the hills, one by one."""
from props import *
import sc_chorus

LAYERS = [(700, 26, 61, LEAF1, 0.35), (790, 32, 62, LEAF2, 0.6), (880, 36, 63, LEAF3, 0.85), (962, 30, 64, LEAF4, 1.0)]
PEEK = [(200, .82, TEAL, PLUM, (198, 134, 92), STRAW, True, 4.3), (1360, .74, MARIGOLD, DENIM, (250, 205, 170), None, False, 1.3),
        (1580, .78, VIOLET, (60, 120, 100), (141, 92, 62), (230, 120, 100), True, 2.3), (1800, .8, PINK, LEAF5, (224, 162, 112), STRAW, True, 3.3),
        (2060, .76, LEAF3, (150, 80, 60), (112, 72, 50), STRAW, True, 5.0), (2300, .7, CORAL, VIOLET, (240, 180, 138), None, False, 5.6)]
WY = 1005


def sign_static(p):
    p.cap((300, 780), (300, 940), 16, WOOD)
    p.rrect(170, 660, 430, 790, 22, (250, 236, 208))


class Pre(Stage):
    wipe_color = CORAL

    def __init__(self, sid, second):
        self.id = sid; self.second = second
        self.L0 = 26.26 + (40.42 if second else 0.0)            # start of "Worry's a fuel" in this pass
        self.t0 = (66.6 if second else 26.2); self.t1 = (77.78 if second else 37.36)

    def lt(self, t): return t - self.L0

    def prep(self):
        self.sign = Sprite(sign_static, (140, 640, 460, 960))

    def base(self, t):
        o = self.lt(t)
        u = eio((o - 7.0) / 3.0)                                 # the sky warms towards the chorus
        return grad(mixc((146, 158, 222), (255, 150, 120), u), mixc((255, 206, 164), (255, 214, 150), u), 0, 860)

    def scroll(self, o):
        return 760 * eio((o - 5.3) / 1.7)                         # "go that way": the world slides by while they walk

    def backdrop(self, t, q):
        o = self.lt(t); d = self.scroll(o)
        for i, (b, a, sd, c, f) in enumerate(LAYERS):
            sh = d * f
            pts = hill_pts(b, a, sd, x0=-30 + sh, x1=W + 30 + sh)
            q.shape([(x - sh, y) for x, y in pts], c, shadow=0.7)
            if i == 0:
                # the "something": a little flag on the far hill
                fx = 1300 - 0.35 * d; fy = b + 4
                if o > 3.5:
                    k = eob((o - 4.0) / 0.4)
                    q.cap((fx, fy), (fx, fy - 130 * k), 9, WOOD, shadow=0.5, hl=False)
                    q.shape([(fx, fy - 130 * k), (fx + 84 * k, fy - 108 * k), (fx, fy - 84 * k)], CORAL, shadow=0.5)
                    flower(q, fx, fy - 142 * k, 22 * k, PINK, SUN2, 6, o)
            if i == 1 and self.second:
                self.peekers(q, t, o, d)
        # path with dashes so the scroll reads
        pts = [(x, 1012 + 10 * math.sin(0.006 * (x + d))) for x in range(-20, W + 40, 40)]
        q.shape(pts + [(W + 20, H + 20), (-20, H + 20)], (238, 206, 160), shadow=0.5)
        for k in range(-1, 16):
            x = k * 150 - (d % 150)
            q.cap((x, 1050), (x + 70, 1050), 10, (214, 176, 132), shadow=0, hl=False)
        # Worry Motel sign: passes by on the near layer
        if o < 9:
            sx = 0 - d * 1.0
            if o > 2.0 and sx > -420:
                k = eob((o - 2.0) / 0.4)
                self.sign.blit(q.img, dx=sx, s=k, pivot=(300, 960))
                if k > 0.95:
                    q.text(300 + sx, 706, "WORRY", 40, INK, shadow=0, hl=False)
                    q.text(300 + sx, 752, "MOTEL", 40, INK, shadow=0, hl=False)
                    if o > 2.75:
                        k2 = clamp((o - 2.75) / 0.25)
                        q.cap((190 + sx, 668), (190 + sx + 220 * k2, 782), 14, RED, shadow=0.3, hl=False)
                        q.cap((410 + sx, 668), (410 + sx - 220 * k2, 782), 14, RED, shadow=0.3, hl=False)

    def peekers(self, q, t, o, d):
        for j, (x, s, shirt, bib, skin, hatc, hat, ts) in enumerate(PEEK):   # one gardener at a time
            if o < ts:
                continue
            rise = eob((o - ts) / 0.55)
            by = 1000 - 130 * rise + (0 if o > 7.0 else 0)
            xe = x - d * 0.6
            wave = math.sin(o * 6 + j) * 18
            if o > 7.5:                                             # the count-in: every gardener throws both hands up
                up = eio((o - 7.5) / 0.3)
                hands = [(xe - 62 * s - 14 * up, by - (250 + 90 * up) * s), (xe + 62 * s + 14 * up, by - (250 + 90 * up) * s)]
            elif o > ts + 0.7:
                hands = [(xe - 62 * s, by - 250 * s + wave), (xe + 62 * s, by - 250 * s - wave)]
            else:
                hands = None
            wren(q, xe, by, s, hands=hands, look=0.3, smile=1.4, shirt=shirt, bib=bib, skin=skin, hatc=hatc or STRAW, hat=hat)

    # ------------------------------------------------------------ foreground
    def draw(self, p, t):
        o = self.lt(t); d = self.scroll(o)
        walking = 5.3 < o < 7.0
        cx = 640 if o < 7.6 else 640
        sx = 880
        bob = -12 * abs(math.sin(math.pi * (t - BAR0) / BEAT)) if walking else 0.0
        # ---- worry -> fuel
        fuel = eoc((o - 1.0) / 1.6) if o < 7 else 1.0
        if 0.05 < o < 2.9:
            k = pop_scale(t, self.L0 + 0.05, 0.3) * (1 - clamp((o - 2.2) / 0.6))
            if k > 0.02:
                bx, by_ = cx + 20, 400
                p.shape(cloud_polys(bx, by_, 0.9 * k), mix(PLUM, CREAM, .5), shadow=0.8)
                d_ = ImageDraw.Draw(p.img)
                for j in range(3):                                       # a scribble of worry
                    pts = [(bx - 20 + (18 + 22 * a / 7) * k * math.cos(a + j * 2.0 + o * 4), by_ + 10 + (18 + 22 * a / 7) * k * math.sin(a + j * 2.0 + o * 4)) for a in [i * 0.5 for i in range(15)]]
                    d_.line(pts, fill=PLUM, width=5, joint="curve")
        if 0.9 < o < 3.2:                                                 # the stream of worry into Sprig's lid
            a0 = (cx + 40, 400); a1 = (sx, WY - 170); a2 = ((cx + sx) / 2 + 40, 250)
            d_ = ImageDraw.Draw(p.img)
            for i in range(12):
                u = ((o * 1.1) + i / 12.0) % 1.0
                x, y = ((1 - u) ** 2 * a0[0] + 2 * (1 - u) * u * a2[0] + u * u * a1[0], (1 - u) ** 2 * a0[1] + 2 * (1 - u) * u * a2[1] + u * u * a1[1])
                c = mixc(VIOLET, MARIGOLD, u)
                r = 9 * (1 - 0.4 * u)
                d_.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(v) for v in c))
        # ---- characters
        ang = -1.35; smile = 0.7; look = 0.5
        if 1.0 < o < 3.2:
            smile = 1.3
        hh = [(cx - 58, WY - 135), (cx + 65, WY - 145)]
        if o > 7.5:                                                         # "Ready? Ready?" -> hands up
            up = eio((o - 7.5) / 0.3)
            hh = [(cx - 58 - 24 * up, WY - 135 - 190 * up), (cx + 65 + 20 * up, WY - 145 - 170 * up)]
            ang = -1.35 + 0.15 * up
            smile = 1.6
        for ts in (self.L0 + 9.18, self.L0 + 9.54, self.L0 + 9.90):        # a jump on every count
            if 0 <= t - ts < 0.3:
                bob -= 26 * math.sin(math.pi * (t - ts) / 0.3)
        wren(p, cx, WY + bob, 1.2, hands=hh, held=("shovel", 1, ang), look=look, smile=smile, blink=blink_at(t, [self.L0 + 3.4, self.L0 + 6.6]))
        happy = 0.8 + (1.2 if o > 7.5 else 0)
        hop = -34 * abs(math.sin(math.pi * (t - BAR0) / BEAT)) if o > 9.0 else 0.0
        sprig(p, sx, WY + 8 + bob * 0.8 + hop, 1.1, look=0.5, happy=happy, tilt=3 * math.sin(t * 2))
        if 0.9 < o < 3.4:                                                 # Sprig lights up on fuel
            p.ell(sx, WY - 90, 105, 96, MARIGOLD, shadow=0, hl=False, alpha=0.30 * math.sin(math.pi * clamp((o - 0.9) / 2.5)) + 0.05)
        if 1.0 < o < 5.6:                                                 # the fuel gauge
            gk = pop_scale(t, self.L0 + 1.0, 0.3) * (1 - clamp((o - 5.0) / 0.5))
            if gk > 0.03:
                gx, gy = sx + 165, WY - 300
                p.rrect(gx - 24, gy - 90 * gk, gx + 24, gy + 90 * gk, 14, CREAM)
                if fuel > 0.02:
                    p.rrect(gx - 16, gy + 82 * gk - 164 * gk * fuel, gx + 16, gy + 82 * gk, 8, mixc(CORAL, MARIGOLD, fuel), shadow=0, hl=False)
                p.tag(gx, gy - 118 * gk, "FUEL", int(34 * gk) + 4, fill=MARIGOLD, padx=20, pady=8)
        # ---- the arrow: point it at something and go that way
        if 3.5 < o < 8.2:
            k = pop_scale(t, self.L0 + 3.55, 0.3) * (1 - clamp((o - 7.6) / 0.5))
            if k > 0.03:
                x0 = 900 + 12 * math.sin(o * 5)
                arrow(p, x0 - 210 * k, 300, x0 + 210 * k, 300, w=int(30 * k) + 2, col=CORAL, head=int(80 * k))
        word_tag(p, 1300 - 0.35 * d + 30, 450, "something", 50, t, self.L0 + 4.55, life=3.2, fill=(255, 226, 150), ink=INK, rot=-0.03)
        # ---- Ready? Ready?
        word_tag(p, 700, 460, "Ready?", 84, t, self.L0 + 7.3, life=1.15, fill=CREAM, ink=INK, rot=-0.05)
        word_tag(p, 1220, 500, "Ready?", 96, t, self.L0 + 7.74, life=1.15, fill=CORAL, ink=CREAM, rot=0.05)
        # ---- 1 2 3, then everyone jumps
        for j, ts in enumerate([self.L0 + 9.18, self.L0 + 9.54, self.L0 + 9.90]):
            if ts <= t < ts + 0.34:
                sz = int(330 * (0.75 + 0.35 * eob((t - ts) / 0.14)))
                p.ell(960, 500, sz * 0.42, sz * 0.42, CORAL, shadow=1.0)
                p.text(960, 508, str(j + 1), sz, CREAM, shadow=0.3)
        if o > 10.25:                                                     # the pickup: "I'm upping my P-bloom!" starts under a wave of confetti
            k = clamp((o - 10.25) / 0.6)
            for j in range(26):
                rnd = random.Random(300 + j)
                x = rnd.uniform(60, W - 60); y = ((t * rnd.uniform(90, 220) + rnd.uniform(0, 900)) % 900) + 100
                d2 = ImageDraw.Draw(p.img)
                if rnd.random() < k:
                    d2.polygon(ell_pts(x, y, 9, 5, rnd.uniform(0, 3) + t * 2, n=8, jit=0), fill=rnd.choice(FCOLS))
        caption(p, t, y=124)
