"""Opening: the storm (spoken intro) -> flash -> the title card."""
from props import *
import credits

TITLE = bar_t(5)                 # the downbeat of bar 5 (~9.80 s): flash, dawn, title slam
COOLS = [5.76, 6.32, 6.80, 7.28]
DOOM_TAGS = [(2.35, "my P(doom) is higher", 470, 372, -0.04), (2.85, "no, MINE is higher", 850, 470, 0.03),
             (3.32, "P(doom)!!  P(doom)!!", 330, 520, -0.02), (3.86, "everyone's upping it", 960, 350, 0.035),
             (4.45, "refresh.  refresh.  refresh.", 520, 600, 0.02), (5.05, "doomscroll", 900, 610, -0.04)]
FLASHES = [(2.28, 0.5), (2.44, 0.3), (3.84, 0.95), (4.02, 0.5)]


def wren_deadpan(p, t, cx, by, s):
    nod = 0.0
    for c in COOLS:
        dt = t - c
        if 0 <= dt < 0.30:
            nod += 9 * math.sin(math.pi * dt / 0.30)
    up = eio((t - 5.6) / 0.3) * (1 - eio((t - 7.7) / 0.4))          # the flat "cool" thumbs-up
    sh = eio((t - 8.3) / 0.9)                                         # raising the shovel: "I brought a shovel"
    hop = -34 * math.sin(math.pi * clamp((t - 9.28) / 0.36)) if t >= 9.28 else 0.0
    L = (cx - 48 * s - 62 * s * up, by - 112 * s - 150 * s * up + nod * s * 0.2)
    R = (cx + 54 * s + 26 * s * sh, by - 121 * s - 178 * s * sh)
    ang = -1.35 - 0.25 * sh
    smile = -0.6 + 2.0 * up + 1.2 * sh
    look = -0.6 if t < 8.0 else 0.4
    wren(p, cx, by + nod * s * 0.5 + hop, s, hands=[L, R], held=("shovel", 1, ang), look=look, smile=smile,
         blink=blink_at(t, [3.2, 5.0, 6.05, 6.6, 7.05, 7.5]))
    if 6.0 < t < 8.3:
        sweat(p, cx + 40 * s, by - 300 * s + 6 * math.sin(t * 5), 1.1 * s)


class Intro(Scene):
    id = "intro"; t0 = 0.0; t1 = 11.64
    wipe_color = CORAL

    def setup(self):
        self.PS, self.TS = plate_pt(self.storm_static)
        self.PD, self.TD = plate_pt(self.dawn_static)
        self.sun = Sprite(lambda p: sun(p, 960, 690, 200, rays=26), (620, 350, 1300, 1030))
        self.cl = [(Sprite(lambda p, c=c: small_cloud(p, 400, 300, 1.0, c), (100, 100, 720, 440)), c) for c in [(255, 236, 220), CREAM]]

    def storm_static(self, p):
        hills_static(p, [(800, 30, mix(LEAF5, NIGHT_T, .62)), (880, 30, mix(LEAF5, NIGHT_T, .45)), (965, 30, mix(LEAF5, NIGHT_T, .28))])
        stem_flower(p, 300, 1040, 120, 20, mix(PINK, NIGHT_T, .25), lean=6, petals=5)

    def dawn_static(self, p):
        layers = [(690, 24, 11, LEAF1), (760, 34, 12, LEAF2), (835, 40, 13, LEAF3), (915, 44, 14, LEAF4), (995, 40, 15, LEAF5)]
        for i, (b, a, sd, c) in enumerate(layers):
            p.shape(hill_pts(b, a, sd), c, shadow=0.9)
            if i in (1, 2, 3):
                F.scatter_flowers(p, b + 20, b + 78, 7 + 3 * i, 30 + i, 12 + 4 * i, 20 + 6 * i)

    def paper(self, t=0.0):
        q = Paper()
        if t < TITLE:
            bg = to_img(grad(NIGHT_T, NIGHT_B, 0, 860)); P, T = self.PS, self.TS
        else:
            bg = to_img(grad((255, 168, 150), (255, 240, 208), 0, 720)); P, T = self.PD, self.TD
            u = eoc((t - TITLE) / 1.5)
            self.sun.blit(bg, dy=250 * (1 - u), rot=(t - TITLE) * 0.22, pivot=(960, 690))
            for k, (X, Y, s, ci) in enumerate([(300, 250, .7, 0), (1610, 200, .85, 0), (1450, 470, .5, 1), (470, 520, .42, 1)]):
                self.cl[ci][0].blit(bg, dx=X - 400 + (t - TITLE) * (10 + 6 * k), dy=Y - 300, s=s, pivot=(400, 300))
        p = Paper(); p.img = to_img(P + T * np.asarray(bg, np.float32))
        return p

    def cam(self, t):
        if t < TITLE - 0.2:
            return (1.0, 960, 560)
        return (cam_pulse(t, 0.012), 960, 560)

    # ---------------------------------------------------------------- storm
    def draw_storm(self, p, t):
        nx, ny = 1330, 460 + 9 * math.sin(t * 1.3)
        nimbus(p, nx, ny, 1.35, mood="grumpy")
        # bolts on the two big flashes
        for (ts, amp) in FLASHES:
            if ts <= t < ts + 0.13 and amp > 0.4:
                draw_bolt(p, nx + 120, ny + 130, 1500 if ts > 3 else 1250, 940, seed=int(ts * 10))
        rain(p.img, t, 0, W, 300, 1000, n=120, seed=3)
        wren_deadpan(p, t, 560, 1040, 1.2)
        sd = eio((t - 8.3) / 0.6)
        hop = -20 * math.sin(math.pi * clamp((t - 9.28) / 0.36)) if t >= 9.28 else 0.0
        sprig(p, 790, 1046 + hop, 1.15, look=-0.6 + 1.0 * sd, happy=-0.7 + 2.4 * sd, tilt=-3 + 6 * sd)
        # the crowd of doom tags
        for (ts, s_, x, y, rot) in DOOM_TAGS:
            if t < ts:
                continue
            fade = 1 - clamp((t - 5.35) / 0.3)
            if fade <= 0:
                continue
            k = pop_scale(t, ts, 0.2)
            yy = y - 12 * (t - ts)
            blend_overlay(p, lambda q, s_=s_, x=x, yy=yy, k=k, rot=rot: q.tag(x, yy, s_, max(8, int(42 * k)), fill=mix(PLUM, INK, .3), ink=CREAM, rot=rot), fade)
        caption(p, t, y=232, size=100)
        fl = max([amp * max(0.0, 1 - (t - ts) / 0.24) for (ts, amp) in FLASHES if t >= ts] + [0.0])
        flash(p.img, fl)

    # ---------------------------------------------------------------- title card
    def draw_title(self, p, t):
        e = t - TITLE
        beats = [(0.06, "Upping My", 118, 224), (0.52, "P(Bloom)", 258, 420)]
        for (dt, s_, size, y) in beats:
            if e >= dt:
                sz = int(size * eob((e - dt) / 0.26))
                if sz > 8:
                    p.text(966, y + 8, s_, sz, CORAL, shadow=0.0, hl=False)
                    p.text(960, y, s_, sz, INK)
        if e >= 0.98:
            sz = int(60 * eob((e - 0.98) / 0.26))
            if sz > 8:
                p.tag(960, 610, "— An Answer", sz, fill=CORAL, ink=CREAM, rot=-0.02)
        k = eob((e - 0.98) / 0.3) if e > 0.98 else 0.0            # Wren and Sprig hop in with "An Answer" so the card has company for a second
        bob_ = -14 * abs(math.sin(math.pi * (t - TITLE) / BEAT * 0.5))
        if k > 0.02:
            wren(p, 450, 1046 + bob_ * 0.5, 1.4 * k, hands=[(450 - 33, 1046 - 158 * k), (450 + 44, 1046 - 168 * k)], held=("shovel", 1, -1.15), look=0.6)
            sprig(p, 740, 1052 + bob_, 1.4 * k, look=0.5, bloom=None, tilt=4)
        a = clamp((e - 0.15) / 0.35) * clamp((11.62 - t) / 0.2)
        blend_overlay(p, lambda q: credits.opening_ribbon(q, 960, 84), a)

    def draw(self, p, t):
        if t < TITLE:
            self.draw_storm(p, t)
        else:
            self.draw_title(p, t)
        # the smash-cut flash into dawn
        if TITLE - 0.14 <= t < TITLE:
            flash(p.img, (t - (TITLE - 0.14)) / 0.14)
        elif t >= TITLE:
            flash(p.img, 1 - (t - TITLE) / 0.42)
