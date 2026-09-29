"""Outro (sunset, 'I saved you a shovel') and the end card."""
from props import *
import credits
from sc_chorus import CROWD

R_ = 800


def dome_top(x):
    return 1280 - math.sqrt(max(0, R_ * R_ - (x - 960) ** 2))


class Outro(Stage):
    id = "outro"; t0 = 165.97
    wipe_color = PLUM

    def static(self, p):
        p.ell(960, 1280, R_, R_, LEAF4, shadow=1.0)
        for i, (rr, c) in enumerate([(770, LEAF3), (730, LEAF2)]):
            p.ell(960, 1290, rr, rr, c, shadow=0.5)
        for i in range(17):
            a0 = 196 + i * 8.6; a1 = a0 + 7
            p.shape(annular(960, 1290, 668, 722, a0, a1, 8), [LEAF3, LEAF1, LEAF4][i % 3], shadow=0.15, hl=False, alpha=.75)
        for x, r_ in [(700, 60), (1210, 70)]:
            yb = dome_top(x) + 24
            p.shape([(x - r_ * 1.4, yb)] + [(x + r_ * 1.4 * math.cos(math.radians(a)), yb - r_ * 1.4 * math.sin(math.radians(a))) for a in range(180, -1, -8)][::-1], (206, 240, 240), shadow=0.6, alpha=.85)
            p.cap((x, yb), (x, yb - r_ * 1.4), 4, (150, 200, 205), shadow=0, hl=False)
        wx = 1440; wy = dome_top(wx) + 20
        p.shape([(wx - 16, wy), (wx + 16, wy), (wx + 8, wy - 150), (wx - 8, wy - 150)], CREAM)
        rnd = random.Random(2)
        for x in range(330, 1600, 62):
            if abs(x - 960) < 210:
                continue
            stem_flower(p, x + rnd.uniform(-14, 14), dome_top(x) + 44, rnd.uniform(46, 96), rnd.uniform(15, 26), rnd.choice(FCOLS), lean=rnd.uniform(-8, 8), petals=rnd.choice([5, 6, 8]))
        for x in (560, 1320):
            yb = dome_top(x) + 30
            p.cap((x, yb), (x, yb - 70), 9, WOOD); p.ell(x, yb - 100, 42, 44, LEAF2)
        # planter with the sign and the shovel
        p.rrect(700, 920, 1180, 1030, 40, (146, 96, 64))
        p.rrect(724, 936, 1156, 1014, 30, (120, 76, 50), shadow=0, hl=False)
        F.dashed_rrect(p, 736, 946, 1144, 1004, CREAM, 5, 22, 16)
        p.cap((900, 944), (900, 800), 14, WOOD); p.rrect(700, 716, 1100, 846, 24, STRAW)
        p.text(900, 782, "YOUR TURN", 62, INK, shadow=0, hl=False)

    def prep(self):
        q = Paper(); q.img = to_img(grad((48, 36, 98), (255, 178, 148), 0, 760))
        for i, c in enumerate([CORAL, MARIGOLD, SUN2, LEAF2, SKY, VIOLET]):
            q.shape(annular(960, 950, 520 + i * 25, 545 + i * 25, 180, 360, 60), c, shadow=0.2, hl=False, alpha=.9)
        self.sky = np.asarray(q.img, np.float32)
        self.blade = Sprite(lambda p: [p.shape(leaf_pts(1440, dome_top(1440) - 130, 96, 22, k * 2.094 + 0.5 - 1.57), (255, 236, 200), shadow=0.3, sh_off=(1, 2), sh_blur=2) for k in range(3)],
                            (1320, dome_top(1440) - 260, 1560, dome_top(1440) - 10))
        self.shov = Sprite(lambda p: (shovel(p, (1170, 640), 1.5708, length=300, blade=(58, 76)), p.ell(1150, 690, 26, 16, CORAL, rot=-0.5), p.ell(1192, 690, 26, 16, CORAL, rot=0.5), p.ell(1171, 692, 12, 12, mix(CORAL, INK, .2), shadow=0, hl=False)), (1060, 590, 1290, 1000))

    def base(self, t): return self.sky

    def backdrop(self, t, q):
        stars(q.img, t, n=80, ymax=520, seed=21)

    def draw(self, p, t):
        wy = dome_top(1440) + 20
        self.blade.blit(p.img, rot=(t - 166) * 1.1, pivot=(1440, wy - 150))
        p.ell(1440, wy - 150, 11, 11, CORAL)
        # the shovel is offered
        glow = clamp((t - 172.6) / 0.5)
        self.shov.blit(p.img, dy=-8 * glow * math.sin(t * 6), rot=0.0)
        if glow > 0:
            for j in range(4):
                a = t * 2.2 + j * 1.57
                star4(p, 1170 + 80 * math.cos(a), 800 + 130 * math.sin(a * 1.3), 12 + 6 * math.sin(t * 7 + j), a, SUN2)
        # happy Nimbus rains on the garden, and pretends to be grumpy for one beat on "doom"
        nx, ny = 250 + 12 * math.sin(t * 0.8), 250 + 8 * math.sin(t * 1.3)
        doomy = 169.16 <= t < 169.6
        nimbus(p, nx, ny, 1.0, col=(224, 216, 244), dark=(190, 180, 222), mood="grumpy" if doomy else "happy", lightning=doomy)
        rain(p.img, t, nx - 130, nx + 110, ny + 80, ny + 470, n=22, seed=17, slant=0.0, speed=300, ln=22, w=5)
        # the cast
        k, u = beat_of(t)
        wave = math.sin(t * 6) * 26
        wc = 560
        hands = [(wc - 58 - 20, 985 - 250 - 40 + wave), (wc + 65, 985 - 145)]
        if t > 172.1:
            hands = [(wc - 58, 985 - 135), (wc + 130, 985 - 215)]         # a hand held out towards the camera: "you"
        wren(p, wc, 1010, 1.4, hands=hands, held=("shovel", 1, -1.35) if t <= 172.1 else None, look=0.0, smile=1.6, blink=blink_at(t, [168.0, 171.8]))
        hop = -18 * abs(math.sin(math.pi * (t - 169.6) / 0.6)) if 169.6 < t < 170.2 else 0.0
        sprig(p, 1300, 1052 + hop, 1.3, look=-0.3, happy=1.9, bloom=1.0, tilt=3 * math.sin(t * 2))
        if t < 167.7:
            k2 = pop_scale(t, 166.1, 0.4) * (1 - clamp((t - 167.3) / 0.4))
            if k2 > 0.02:
                p.text(966, 128, "Pass it on.", int(122 * k2), CORAL, shadow=0.0, hl=False)
                p.text(960, 120, "Pass it on.", int(122 * k2), CREAM)
        word_tag(p, 790, 560, "for you", 64, t, 172.7, life=1.3, fill=(255, 226, 150), ink=INK, rot=-0.04)
        if t >= 167.7:
            caption(p, t, y=124, fill=CREAM, shade=CORAL)


class EndCard(Stage):
    id = "end"; t0 = 174.02
    wipe_color = PLUM

    def static(self, p):
        p.shape(hill_pts(930, 24, 61), LEAF3, shadow=0.9)
        p.shape(hill_pts(1005, 18, 62), LEAF5, shadow=0.9)
        F.scatter_flowers(p, 960, 1040, 12, 62, 18, 30, 40, 780)

    def base(self, t): return grad((48, 36, 98), (255, 178, 148), 0, 900)

    def backdrop(self, t, q):
        stars(q.img, t, n=70, ymax=520, seed=41)

    def draw(self, p, t):
        T_ = credits.T
        lt = t - self.t0
        hop = -26 * abs(math.sin(math.pi * lt / (BEAT * 2)))
        sprig(p, 400, 1052 + hop, 2.5, look=0.5, happy=1.8, bloom=1.3, tilt=3 * math.sin(t * 2))
        k = eob((lt - 0.25) / 0.45)
        if k > 0.02:
            cx, cy = 1315, 530
            rr = rrect_pts(780, 130, 1850, 930, 46)
            rr = [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in rr]
            p.shape(rr, CREAM)
        if k < 0.98:
            return
        def fade(t0_):
            return clamp((lt - t0_) / 0.35)
        blend_overlay(p, lambda q: q.text(1315, 226, "Made by", 62, VIOLET, shadow=0, hl=False), fade(0.7))
        size = 116
        while font(FRED, size * paper.S).getlength(T_["model"]) / paper.S > 980:
            size -= 2
        def model(q):
            q.text(1321, 350, T_["model"], size, PINK, shadow=0, hl=False); q.text(1315, 342, T_["model"], size, CORAL, shadow=0, hl=False)
        blend_overlay(p, model, fade(1.0))
        blend_overlay(p, lambda q: q.text(1315, 458, "in " + T_["platform"], 74, INK, shadow=0, hl=False), fade(1.3))
        y = 566
        lines_all = list(T_["credit_lines"])
        if T_.get("director"):
            lines_all.insert(1, "Directed by " + T_["director"])
        cs = 38                                                  # credit size: shrink until every line sits on one row
        while cs > 28 and max(font(FRED, cs * paper.S).getlength(ln) / paper.S for ln in lines_all) > 1010:
            cs -= 1
        for i, ln in enumerate(lines_all):
            for sub in F.fit_lines(ln, cs, 1010):
                blend_overlay(p, lambda q, sub=sub, y=y: q.text(1315, y, sub, cs, INK, shadow=0, hl=False), fade(1.7 + 0.45 * i))
                y += cs + 14
            y += 18
        if lt > 3.4:
            kk = eob((lt - 3.4) / 0.35)
            p.tag(1315, 870, "Your turn.  I saved you a shovel.", max(8, int(44 * kk)), fill=(255, 226, 150))
