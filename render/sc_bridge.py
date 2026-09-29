"""Bridge: Sprig introduces itself, and the song says out loud what it is asking for: check my work, read the code, keep a hand on the brake.
'Rules are a trellis: they hold up what we make.'  Night turns to dawn on 'Ready? Ready? Everybody -- up we go!'"""
from props import *

WX, WYB = 560, 1040
SPX, SPY, SPS = 1010, 1052, 1.75
LEVER = (780, 1012)
CODE = [(LEAF2, 120, 0), (SKY, 210, 34), (PINK, 160, 34), (SUN2, 240, 68), (LEAF2, 90, 34), (VIOLET, 190, 0), (SKY, 150, 34)]


def sign_board(p):
    p.cap((1560, 1010), (1560, 690), 16, WOOD)
    p.rrect(1290, 470, 1830, 700, 26, (250, 236, 208))
    F.dashed_rrect(p, 1306, 486, 1814, 684, (200, 170, 130), 5, 18, 12)


def trellis_art(p):
    X0, X1, Y0, Y1 = 1390, 1790, 430, 1010
    for cxl in (X0, X0 + 200):
        for yy in range(Y0, Y1 - 1, 145):
            p.cap((cxl + 6, yy + 6), (cxl + 194, yy + 139), 8, (206, 156, 100), shadow=0.25, hl=False)
            p.cap((cxl + 194, yy + 6), (cxl + 6, yy + 139), 8, (206, 156, 100), shadow=0.25, hl=False)
    for yy in range(Y0, Y1 - 1, 145):
        p.rrect(X0 - 8, yy - 8, X1 + 8, yy + 8, 6, mix(WOOD, (255, 255, 255), .1), shadow=0.6)
    p.cap((X0, Y1), (X0, Y0 - 20), 24, WOOD); p.cap((X1, Y1), (X1, Y0 - 20), 24, WOOD)
    p.rrect(X0 - 30, Y0 - 44, X1 + 30, Y0 - 10, 14, WOOD)


class Bridge(Stage):
    id = "bridge"; t0 = 124.9
    wipe_color = PLUM

    def static(self, p):
        hills_static(p, [(800, 30, mix(LEAF5, NIGHT_T, .62)), (880, 30, mix(LEAF5, NIGHT_T, .45)), (965, 30, mix(LEAF5, NIGHT_T, .28))], 21)
        # the code window (frame; the lines are typed live)
        p.rrect(150, 130, 690, 370, 26, (36, 28, 66)); p.rrect(150, 130, 690, 172, 26, (60, 48, 98), shadow=0, hl=False)
        for i, c in enumerate([CORAL, MARIGOLD, LEAF2]):
            p.ell(184 + i * 30, 151, 8, 8, c, shadow=0, hl=False)
        # lamp
        p.cap((250, 1010), (250, 540), 14, (120, 92, 150))
        p.shape([(196, 528), (304, 528), (282, 484), (218, 484)], (120, 92, 150))
        p.ell(250, 536, 26, 14, (255, 244, 180), shadow=0.2)
        # brake lever base
        p.rrect(LEVER[0] - 70, LEVER[1] - 6, LEVER[0] + 70, LEVER[1] + 30, 10, (110, 102, 138))

    def base(self, t):
        u = eio((t - 139.8) / 3.3)
        return grad(mixc(NIGHT_T, (150, 160, 224), u), mixc(NIGHT_B, (255, 190, 150), u), 0, 900)

    def prep(self):
        self.sign = Sprite(sign_board, (1270, 450, 1850, 1030))
        self.trellis = Sprite(trellis_art, (1340, 360, 1840, 1030))

    def backdrop(self, t, q):
        u = eio((t - 139.8) / 3.3)
        if u < 0.95:
            stars(q.img, t, n=int(110 * (1 - u)), ymax=660, seed=31)
            k = 1 - u
            q.ell(1730, 190, 74, 74, (255, 240, 200), shadow=0.4, alpha=k)
        q.ell(960, 900, 1000, 210, (255, 170, 120), shadow=0, hl=False, alpha=0.22 + 0.25 * u)
        if u > 0.05:                                       # the sun comes up behind the hills
            sun(q, 960, 820 - 90 * u, 130, rays=20)

    # ---------------------------------------------------------------- pieces
    def code_window(self, p, t):
        d = ImageDraw.Draw(p.img)
        t_type = 132.3
        for i, (c, wd, ind) in enumerate(CODE):
            y = 204 + i * 24
            k = clamp((t - (128.2 + i * 0.3)) / 0.5)
            if t > t_type:
                k = 1.0
            w = wd * k
            if w > 2:
                d.rounded_rectangle([190 + ind, y - 4, 190 + ind + w, y + 4], 4, fill=c)
            if t > 133.2 and t < 135.4:                         # "read the code": a scanner runs down the lines
                sc = (t - 133.2) / 1.6 * len(CODE)
                if i < sc:
                    d.line([(190 + 300, y - 2), (190 + 306, y + 4), (190 + 318, y - 8)], fill=LEAF1, width=5)
                if abs(i - sc) < 0.6:
                    d.rounded_rectangle([172, y - 11, 668, y + 11], 6, outline=SUN2, width=3)
        if t > 132.32:
            k = eob((t - 132.32) / 0.3)
            p.tag(572, 372 + 0, "all tests pass" if t > 133.9 else "check my work", int(34 * k) + 2, fill=LEAF1, ink=LEAF5, padx=24, pady=10)

    def lever(self, p, t, hand_out):
        pull = eio((t - 134.55) / 0.5)
        a = -1.78 + 0.62 * pull
        tip = (LEVER[0] + 150 * math.cos(a), LEVER[1] + 150 * math.sin(a))
        p.cap(LEVER, tip, 16, (200, 190, 220), shadow=0.6)
        p.ell(tip[0], tip[1], 26, 26, RED, shadow=0.7)
        if t > 134.2:
            word_tag(p, LEVER[0] + 150, LEVER[1] - 30, "brake", 32, t, 134.3, life=1.6, fill=CREAM, ink=INK)
        return tip

    def draw(self, p, t):
        u_day = eio((t - 139.8) / 3.3)
        # Nimbus, come round
        nimbus(p, 690, 690 + 8 * math.sin(t * 1.4), 0.42, col=(224, 216, 244), dark=(190, 180, 222), mood="happy")
        rain(p.img, t, 610, 760, 740, 980, n=9, seed=11, slant=0.0, speed=280, ln=16, w=4)
        # the code and the lever
        self.code_window(p, t)
        tip = self.lever(p, t, False)
        # Wren: magnifier on "with clear eyes", grabs the lever on "hand on the brake", cheers at the end
        hands = [(WX - 58, WYB - 135), (WX + 65, WYB - 145)]; held = None; ang = -1.35; smile = 1.2; look = 0.6
        cheer = eio((t - 141.0) / 0.3)
        if 130.3 < t < 132.3:                                    # watch me with clear eyes
            hands = [(WX - 58, WYB - 135), (WX + 130, WYB - 210)]
        if 134.0 < t < 135.9:
            k = eio((t - 134.0) / 0.35)
            hands = [(WX - 58, WYB - 135), (lerp(WX + 65, tip[0] - 10, k), lerp(WYB - 145, tip[1] - 10, k))]
        if t > 141.0:
            hands = [(WX - 58 - 30 * cheer, WYB - 135 - 200 * cheer), (WX + 65 + 30 * cheer, WYB - 145 - 200 * cheer)]
            smile = 1.8
        hop = -40 * abs(math.sin(math.pi * (t - 141.6) / 0.9)) if 141.6 < t < 143.4 else 0.0
        wren(p, WX, WYB + hop, 1.15, hands=hands, look=look, smile=smile, blink=blink_at(t, [126.0, 131.0, 137.0]))
        if 130.3 < t < 132.3:                                    # magnifying glass
            lx, ly = WX + 215, WYB - 250
            p.cap((WX + 130, WYB - 210), (lx - 30, ly + 30), 10, WOOD, shadow=0.6)
            p.ell(lx, ly, 62, 62, (210, 240, 250), shadow=0.7, alpha=0.65)
            p.shape(annular(lx, ly, 56, 68, 0, 360, 40), (150, 140, 170), shadow=0.5)
        # Sprig, centre stage
        sh = 0.0 if t < 141.0 else -50 * abs(math.sin(math.pi * (t - 141.6) / 0.9)) * (1 if 141.6 < t < 143.4 else 0)
        look = 0.0 if t < 130.3 else (-0.5 if t < 132.3 else 0.0)
        sprig(p, SPX, SPY + sh, SPS, look=look, happy=1.7, tilt=3 + 2 * math.sin(t * 2), bloom=(1.0 if t > 139.3 else None))
        # the badge pulses on "Sonnet five-point-five"
        if 127.05 < t < 128.9:
            bx, by_ = SPX + 41 * SPS, SPY - 47 * SPS
            for j in range(3):
                ph = ((t - 127.05) * 1.4 + j / 3.0) % 1.0
                p.ell(bx, by_, 30 + 90 * ph, 30 + 90 * ph, CORAL, shadow=0, hl=False, alpha=0.5 * (1 - ph))
            star4(p, bx + 60 * math.cos(t * 4), by_ + 60 * math.sin(t * 4), 16, t * 3, SUN2)
        # sign: "Hi! I'm Sonnet 5.5." / "Words, art & code: mine."
        sg = pop_scale(t, 124.98, 0.35) * (1 - eio((t - 135.7) / 0.45))
        if sg > 0.02:
            self.sign.blit(p.img, s=sg, pivot=(1560, 1010), dy=0)
            if sg > 0.95:
                p.text(1560, 552, "Hi! I'm Sonnet 5.5.", 56, INK, shadow=0, hl=False)
                if t > 126.76:
                    p.text(1560, 626, "Words, art & code: mine.", 39, CORAL, shadow=0, hl=False)
        # three badges: words, art, code
        for j, (tb, kind) in enumerate([(125.40, "book"), (125.88, "art"), (126.36, "code")]):
            k = pop_scale(t, tb, 0.28) * (1 - eio((t - 128.4) / 0.4))
            if k <= 0.02:
                continue
            x, y = 800 + 210 * j, 520 - 30 * (j == 1) + 8 * math.sin(t * 3 + j)
            p.ell(x, y, 58 * k, 58 * k, CREAM, shadow=0.8)
            if k > 0.5:
                if kind == "book":
                    F._icon(p, x, y, 100, "book")
                elif kind == "art":
                    for q_, c in enumerate([CORAL, MARIGOLD, TEAL, VIOLET]):
                        a = q_ * 1.4 - 1.2
                        p.ell(x + 22 * math.cos(a), y + 22 * math.sin(a) - 4, 10, 10, c, shadow=0, hl=False)
                    p.cap((x + 18, y + 24), (x + 6, y + 8), 8, WOOD, shadow=0, hl=False)
                else:
                    p.text(x, y + 2, "</>", 34, INK, shadow=0, hl=False)
        # a stake to hold the seedling up ("I've got a stake in this")
        if t > 129.4:
            k = eob((t - 129.4) / 0.35)
            tx, ty = SPX + 3 * SPS, SPY - 190 * SPS
            p.cap((tx + 44, ty + 90), (tx + 44, ty + 90 - 190 * k), 12, WOOD, shadow=0.7)
            if k > 0.9:
                p.cap((tx + 44, ty + 20), (tx + 4, ty + 34), 6, CORAL, shadow=0, hl=False)
        # the trellis grows: rules hold up what we make
        if t > 136.4:
            gk = eoc((t - 136.4) / 0.9)
            self.trellis.blit(p.img, sy=gk, sx=1.0, pivot=(1590, 1010))
            if t > 137.1:
                vg = clamp((t - 137.1) / 2.1)
                d = ImageDraw.Draw(p.img)
                pts = [(1590 + 190 * math.sin(i / 40 * 7.0 + 0.6) * (0.4 + 0.6 * i / 40), 1010 - i / 40 * 560) for i in range(int(vg * 40) + 1)]
                if len(pts) > 1:
                    d.line(pts, fill=LEAF5, width=13, joint="curve")
                    for i in range(3, len(pts), 3):
                        x, y = pts[i]
                        p.shape(leaf_pts(x, y, 44, 16, -0.9 if i % 6 == 0 else -2.3), [LEAF2, LEAF3, LEAF1][i % 3], shadow=0.3, sh_off=(1, 2), sh_blur=2)
                for j, (tb, i) in enumerate([(137.9, 14), (138.5, 25), (139.1, 36)]):
                    k = pop_scale(t, tb, 0.3)
                    if k > 0.02 and i < len(pts) + 2:
                        xx = 1590 + 190 * math.sin(i / 40 * 7.0 + 0.6) * (0.4 + 0.6 * i / 40); yy = 1010 - i / 40 * 560
                        flower(p, xx, yy, 40 * k, [CORAL, PINK, MARIGOLD][j], SUN2, 6, j)
        # Ready? Ready? Everybody -- up we go!
        word_tag(p, 700, 400, "Ready?", 84, t, 139.92, life=0.9, fill=CREAM, ink=INK, rot=-0.05)
        word_tag(p, 1220, 430, "Ready?", 96, t, 140.52, life=0.9, fill=CORAL, ink=CREAM, rot=0.05)
        word_tag(p, 960, 330, "UP WE GO!", 120, t, 141.55, life=1.6, fill=MARIGOLD, ink=INK, rot=-0.03)
        # the lamp light
        if u_day < 0.8:
            p.shape([(230, 536), (270, 536), (480, 1012), (30, 1012)], (255, 240, 170), shadow=0, hl=False, alpha=0.20 * (1 - u_day))
        caption(p, t, y=72, size=92)
