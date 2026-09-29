"""Verse 2: four gags, one per trope. Each trope is met with the same three moves: look at it, write it down, do the boring safe thing.
   Shoggoth -> get a light, open it up, read it.   Paperclips -> write the goal down, test it, poke it, flip it.
   FOOM -> where are the brakes? build them as fast as the engine.   Big red button -> somebody goes and sits there."""
from props import *

WY = 1020
GAGS_T = [51.45, 55.15, 58.95, 62.85, 66.6]


# ================================================================== gag 1: the Shoggoth
class Shog(Stage):
    def static(self, p):
        p.shape([(0, 850), (W, 850), (W, H), (0, H)], (58, 54, 92), shadow=0.0, hl=False)

    def base(self, t):
        day = eio((t - 54.3) / 0.7)
        return grad(mixc((20, 24, 50), (255, 236, 190), day), mixc((40, 52, 86), (255, 214, 160), day), 0, 850)

    def prep(self):
        self.lamp = Sprite(lambda p: (p.rrect(470, 700, 520, 770, 12, (255, 222, 120)), p.rrect(462, 690, 528, 708, 6, (120, 92, 150)),
                                      p.cap((478, 696), (495, 660), 8, (120, 92, 150), shadow=0.3, hl=False), p.cap((512, 696), (495, 660), 8, (120, 92, 150), shadow=0.3, hl=False)),
                           (440, 640, 560, 800))

    def blob(self, p, t, cx, cy):
        light = eio((t - 52.9) / 0.4); day = eio((t - 54.3) / 0.7); sh = eio((t - 54.5) / 0.6)
        sc = 1 - 0.55 * sh
        col = mixc((58, 40, 92), (150, 116, 196), max(light * 0.5, day))
        dark = mixc((40, 28, 70), (110, 84, 156), max(light * 0.5, day))
        # tentacles
        for i in range(7):
            bx = cx + (i - 3) * 62 * sc; by0 = cy + 150 * sc
            pts = []
            for j in range(9):
                u = j / 8
                pts.append((bx + (i - 3) * 38 * u * sc + 26 * math.sin(t * 2.2 + i + u * 4) * u, by0 + 105 * sc * u + 12 * math.sin(t * 3 + i) * u))
            curve(p, pts, max(6, 34 * sc), dark, shadow=0.5, hl=False)
        for (dx, dy, rx, ry, c) in [(-150, 60, 150, 120, dark), (150, 80, 140, 110, dark), (0, 0, 250, 200, col), (-70, -120, 130, 90, col), (110, -100, 120, 100, col)]:
            p.shape(ell_pts(cx + dx * sc, cy + dy * sc, rx * sc, ry * sc, 0, n=48, jit=0.03, seed=int(dx + 9)), c, shadow=0.8)
        # eyes look at Wren, blink together
        blink = 0.25 if 0 <= (t * 0.9) % 3 < 0.12 else 1.0
        eyes = [(-120, -40, 30), (-20, -70, 24), (70, -30, 34), (150, 10, 22), (-40, 40, 20), (30, 60, 28), (-150, 70, 20), (110, 100, 22), (-90, 110, 18)]
        for (dx, dy, r) in eyes:
            ex, ey = cx + dx * sc, cy + dy * sc
            p.ell(ex, ey, r * sc, r * sc * blink, CREAM, shadow=0.2, sh_off=(1, 2), sh_blur=2)
            p.ell(ex - 6 * sc, ey + 2 * sc, r * 0.5 * sc, r * 0.55 * sc * blink, INK, shadow=0, hl=False)
        if day > 0.5:                                         # it turns out to be quite gentle
            smile = bez((cx - 60 * sc, cy + 60 * sc), (cx, cy + (60 + 46 * day) * sc), (cx + 60 * sc, cy + 60 * sc), 8)
            curve(p, smile, 7 * sc + 2, INK, shadow=0, hl=False)

    def hatch(self, p, t, cx, cy):
        u = eob((t - 53.75) / 0.45)
        if u <= 0.02:
            return
        # inside: tidy gears and neatly labelled wire
        p.rrect(cx - 92, cy - 70, cx + 92, cy + 70, 16, (46, 40, 78), shadow=0.4)
        gear(p, cx - 34, cy - 6, 34, t * 1.4, (206, 214, 232)); gear(p, cx + 30, cy + 14, 24, -t * 1.9 + 0.3, MARIGOLD)
        for k in range(4):
            p.cap((cx - 84, cy + 44 - k * 6), (cx + 84, cy + 44 - k * 6), 4, [CORAL, SKY, LEAF2, SUN2][k], shadow=0, hl=False)
        w = 92 * math.cos(min(1.0, u) * 1.35)                  # the door swings open on its left hinge
        p.rrect(cx - 92, cy - 70, cx - 92 + max(10, w * 0.5 + 12), cy + 70, 12, mixc((84, 60, 130), (150, 116, 196), 0.3), shadow=0.7)

    def draw(self, p, t):
        cx, cy = 1290, 560
        light = eio((t - 52.9) / 0.4); day = eio((t - 54.3) / 0.7)
        wx = 360
        if light > 0.02:
            p.shape([(wx + 175, 730), (1010, 380), (1010, 900)], (255, 240, 170), shadow=0, hl=False, alpha=0.30 * light * (1 - 0.6 * day))
        self.blob(p, t, cx, cy)
        sc = 1 - 0.55 * eio((t - 54.5) / 0.6)
        self.hatch(p, t, cx, cy + 70 * sc)
        # Wren holds up the light (and, after, the readme)
        R = (wx + 150, WY - 275 + (0 if t > 52.85 else 150)) if t > 52.4 else (wx + 70, WY - 130)
        hands = [(wx - 58, WY - 135), R]
        wren(p, wx, WY, 1.2, hands=hands, look=0.7, smile=-0.4 + 2.0 * day, blink=blink_at(t, [53.3, 54.9]))
        if t > 52.4:
            self.lamp.blit(p.img, dx=R[0] - 495, dy=R[1] - 660)
        if t > 54.3:                                            # read it in daylight: a big open book
            k = pop_scale(t, 54.3, 0.3)
            bx, by_ = wx + 20, WY - 60
            p.rrect(bx - 140 * k, by_ - 80 * k, bx - 4, by_ + 60 * k, 12, CORAL, shadow=0.8)
            p.rrect(bx + 4, by_ - 80 * k, bx + 140 * k, by_ + 60 * k, 12, mix(CORAL, (255, 255, 255), .2), shadow=0.8)
            for r_ in range(4):
                p.cap((bx - 110 * k, by_ - 40 * k + r_ * 26 * k), (bx - 24, by_ - 40 * k + r_ * 26 * k), 6, CREAM, shadow=0, hl=False)
                p.cap((bx + 24, by_ - 40 * k + r_ * 26 * k), (bx + 110 * k, by_ - 40 * k + r_ * 26 * k), 6, CREAM, shadow=0, hl=False)
        sprig(p, wx + 260, WY + 6, 1.1, look=0.8, happy=-0.8 + 2.6 * max(light, day), tilt=-3 * (1 - day) + 3 * day)
        word_tag(p, cx, 330, "SHOGGOTH!", 64, t, 51.76, life=1.3, fill=mixc((58, 40, 92), INK, .3), ink=CREAM, rot=-0.04)
        word_tag(p, cx, 300, "just a big pile of numbers", 42, t, 54.6, life=2.0, fill=CREAM, ink=INK, rot=0.02)
        flash(p.img, 0.20 * day, (255, 226, 160))


# ================================================================== gag 2: the paperclip maximizer
def machine_static(p):
    p.rrect(1150, 430, 1530, 800, 34, (108, 122, 150))
    p.rrect(1176, 456, 1504, 596, 22, (30, 30, 52), shadow=0, hl=False)
    p.shape([(1220, 430), (1460, 430), (1400, 340), (1280, 340)], (150, 164, 190), shadow=0.7)
    p.rrect(1250, 330, 1430, 348, 6, (206, 214, 232))
    p.shape([(1150, 700), (1150, 780), (1050, 830), (1050, 750)], (140, 152, 178), shadow=0.6)
    p.ell(1210, 660, 20, 20, RED, shadow=0.4); p.ell(1270, 660, 20, 20, (60, 110, 80), shadow=0.4)
    p.rrect(1330, 640, 1490, 700, 12, (86, 98, 126), shadow=0, hl=False)
    for k in range(3):
        p.cap((1350, 656 + k * 16), (1470, 656 + k * 16), 5, (150, 164, 190), shadow=0, hl=False)
    p.rrect(1170, 790, 1210, 840, 6, (86, 98, 126)); p.rrect(1470, 790, 1510, 840, 6, (86, 98, 126))


def clip_static(p):
    d = ImageDraw.Draw(p.img)
    c = (92, 104, 138)
    d.rounded_rectangle([100, 100, 168, 196], 26, outline=c, width=8)
    d.rounded_rectangle([114, 118, 154, 176], 16, outline=c, width=8)


class Clips(Stage):
    def static(self, p):
        p.shape([(0, 860), (W, 860), (W, H), (0, H)], (176, 150, 132), shadow=0.0, hl=False)

    def base(self, t):
        return grad((216, 208, 236), (244, 230, 214), 0, 860)

    def prep(self):
        self.mach = Sprite(machine_static, (1030, 320, 1550, 850))
        self.clip = Sprite(clip_static, (90, 90, 180, 210))
        self.board = Sprite(lambda p: (p.rrect(640, 560, 800, 730, 14, WOOD), p.rrect(654, 580, 786, 716, 8, CREAM), p.rrect(692, 548, 748, 578, 8, (150, 140, 170))), (620, 530, 820, 750))
        rnd = random.Random(12)
        self.pile = [(rnd.gauss(0, 120), rnd.uniform(0, 1), rnd.uniform(0, 6.28)) for _ in range(80)]

    def count(self, t):
        if t < 55.6: return 0
        if t < 56.9: return min(999, int(999 * ((t - 55.6) / 0.85) ** 2))     # it goes wild... until the goal is written down
        return 100

    def draw(self, p, t):
        cnt = self.count(t)
        flip = eio((t - 58.05) / 0.75)
        pivot = (1340, 585)
        bump = 1 + 0.10 * math.sin(math.pi * flip)
        self.mach.blit(p.img, rot=math.pi * flip, s=bump, pivot=pivot)
        # display
        shown = min(cnt, 999)
        stopped = t > 56.9
        txt = ("100" if stopped else str(shown).zfill(3)) if t > 55.6 else "000"
        im = text_img(txt, 92, (120, 255, 170) if not (t > 56.9 and t < 57.0) else (255, 255, 255))
        paste_rot(p.img, im, 1340, 526, math.pi * flip)
        lamp_g = (60, 110, 80) if not stopped else (110, 255, 150)
        # clips falling off the chute and piling up
        run = 55.6 < t < 56.9
        n_pile = int(min(1.0, (t - 55.6) / 1.3) * 70) if t > 55.6 else 0
        for i in range(n_pile):
            dx, u, rot = self.pile[i]
            x = 960 + dx * (1 - 0.35 * u); y = 935 + 40 * u - 130 * max(0.0, 1 - abs(dx) / 170)
            self.clip.blit(p.img, dx=x - 134, dy=y - 146, rot=rot + flip * 0.0, s=0.8, pivot=(134, 146))
        if run:
            for i in range(6):
                ph = ((t * 3.2) + i / 6.0) % 1.0
                self.clip.blit(p.img, dx=(1090 - 134) - 130 * ph, dy=(790 - 146) + 130 * ph * ph + 60 * ph, rot=ph * 6 + i, s=0.8, pivot=(134, 146))
        wx = 760
        # Wren: write it down -> test it -> poke it -> step back
        hands = [(wx - 58, WY - 135), (wx + 65, WY - 145)]; ang = -1.35; look = 0.6; smile = 0.8
        if 56.2 < t < 57.3:
            hands = [(wx - 20, WY - 210), (wx + 50, WY - 190)]; ang = None
        if 57.55 < t < 58.05:                                                # poke it
            k = math.sin(math.pi * clamp((t - 57.55) / 0.5))
            hands = [(wx + 20, WY - 190), (wx + 70 + 20 * k, WY - 180)]; ang = 0.02
        wren(p, wx, WY, 1.2, hands=hands, held=("shovel", 1, ang) if ang is not None else None, look=look, smile=smile if t > 55.6 else -0.5,
             blink=blink_at(t, [55.0, 56.0]))
        if 56.2 < t < 57.3:
            k = pop_scale(t, 56.2, 0.25)
            self.board.blit(p.img, dx=wx + 20 - 720, dy=WY - 150 - 640, s=k * 1.3, pivot=(720, 640))
            if k > 0.95:
                p.text(wx + 20, WY - 182, "GOAL: 100", 28, INK, shadow=0, hl=False)
                p.text(wx + 20, WY - 146, "then STOP", 28, CORAL, shadow=0, hl=False)
        sprig(p, 470, WY + 6, 1.1, look=0.8, happy=1.0 + (0.8 if stopped else -1.6) if t > 55.4 else 0.5, tilt=3 * math.sin(t * 2) + (10 * math.sin(t * 20) if flip > 0.2 and flip < 1 else 0))
        # words
        word_tag(p, 1340, 250, "PAPERCLIPS!", 64, t, 55.64, life=1.3, fill=(196, 204, 224), ink=INK, rot=-0.04)
        word_tag(p, 940, 350, "test it  ✓", 56, t, 57.30, life=0.9, fill=LEAF1, ink=LEAF5, rot=0.03)
        word_tag(p, 1000, 300, "still stops.", 58, t, 58.35, life=0.9, fill=(255, 226, 150), ink=INK, rot=-0.03)


# ================================================================== gag 3: FOOM
class Foom(Stage):
    def static(self, p):
        p.shape([(0, 850), (W, 850), (W, H), (0, H)], (150, 150, 176), shadow=0.0, hl=False)
        for x in range(0, W, 160):
            p.rrect(x, 940, x + 90, 956, 6, CREAM, shadow=0.0, hl=False)

    def base(self, t):
        return grad((176, 212, 246), (255, 238, 205), 0, 850)

    def prep(self):
        def cart(p):
            p.rrect(500, 700, 900, 830, 44, CORAL)
            p.shape([(900, 720), (1010, 765), (900, 812)], mix(CORAL, (255, 255, 255), .2))
            p.rrect(560, 660, 780, 712, 20, SKY)
            p.ell(610, 840, 40, 40, (74, 60, 92)); p.ell(610, 840, 15, 15, (150, 140, 170), shadow=0, hl=False)
            p.ell(800, 840, 40, 40, (74, 60, 92)); p.ell(800, 840, 15, 15, (150, 140, 170), shadow=0, hl=False)
            p.text(700, 770, "ENGINE", 48, CREAM, shadow=0, hl=False)
            p.ell(770, 690, 40, 30, SKY, shadow=0, hl=False)
        self.cart = Sprite(cart, (440, 640, 1040, 900))
        def eng(p):
            p.rrect(100, 100, 210, 170, 14, MARIGOLD); p.ell(150, 135, 20, 20, CORAL, shadow=0, hl=False); p.shape([(100, 120), (60, 135), (100, 150)], CORAL, shadow=0.3)
        def brk(p):
            p.ell(160, 135, 46, 46, RED); p.ell(160, 135, 30, 30, mix(RED, INK, .45), shadow=0, hl=False); p.cap((160, 135), (210, 90), 12, (200, 190, 220), shadow=0.3)
        self.eng = Sprite(eng, (40, 80, 230, 200)); self.brk = Sprite(brk, (100, 70, 240, 200))

    def draw(self, p, t):
        d = ImageDraw.Draw(p.img)
        if t < 60.95:
            # the runaway engine
            u = clamp((t - 59.30) / 1.15)
            x = lerp(-900, 2500, u * u * (3 - 2 * u) if u < 1 else 1.0)
            if 0 < u < 1:
                for k in range(16):
                    y = 620 + k * 24 + (k * 37 % 30)
                    d.line([(x - 300 - 180 * (k % 3), y), (x - 90, y)], fill=(255, 255, 255), width=5)
                self.cart.blit(p.img, dx=x - 700, dy=math.sin(t * 60) * 3)
                for k in range(5):
                    p.shape(ell_pts(x - 60 - k * 60, 770 + 8 * math.sin(t * 40 + k), 60 - k * 9, 24 - k * 3, 0, n=20, jit=0.02), mixc(MARIGOLD, CORAL, k / 4), shadow=0.0, hl=False)
            # stunned onlookers
            look = 0.9 if t < 60.4 else 0.9
            wren(p, 380, WY, 1.2, hands=[(322, WY - 135), (445, WY - 145)], held=("shovel", 1, -1.35), look=look, smile=-0.6 if t > 59.9 else 0.5, blink=blink_at(t, [58.9, 60.2]))
            sprig(p, 640, WY + 6, 1.1, look=1.0, happy=-1.0 if t > 59.9 else 0.4, tilt=-4)
            word_tag(p, 960, 330, "FOOM!", 170, t, 59.40, life=0.9, fill=MARIGOLD, ink=INK, rot=-0.06)
            word_tag(p, 1000, 470, "brakes?", 96, t, 60.55, life=0.9, fill=CREAM, ink=RED, rot=0.05)
        else:
            o = t - 61.12
            # two belts running at the same speed: engines above, brakes below
            for (by_, lab) in [(420, "ENGINES"), (620, "BRAKES")]:
                p.rrect(500, by_, 1640, by_ + 44, 22, (90, 82, 116))
                for k in range(-1, 20):
                    xx = 500 + ((k * 70 + t * 240) % 1140)
                    p.cap((xx, by_ + 22), (xx + 26, by_ + 22), 7, (130, 122, 160), shadow=0, hl=False)
            for k in range(6):
                xx = 540 + ((k * 230 + t * 240) % 1100)
                self.eng.blit(p.img, dx=xx - 150, dy=420 - 45 - 135)
                self.brk.blit(p.img, dx=xx - 160, dy=620 - 45 - 135)
            n = max(0, int(o / 0.3)) + 1
            p.tag(760, 290, "engines: %d" % n, 54, fill=MARIGOLD, ink=INK, rot=-0.02)
            p.tag(760, 500, "brakes: %d" % n, 54, fill=RED, ink=CREAM, rot=0.02)
            wren(p, 300, WY, 1.2, hands=[(242, WY - 135), (365, WY - 145)], held=("shovel", 1, -1.35), look=0.7, smile=1.4, blink=blink_at(t, [62.0]))
            sprig(p, 520, WY + 6 + bounce(t, 16, 2.18, 0.0), 1.1, look=-0.6, happy=1.9, tilt=4)


# ================================================================== gag 4: the big red button and the empty chair
class Button(Stage):
    def static(self, p):
        p.shape([(0, 770), (W, 770), (W, H), (0, H)], (196, 140, 96), shadow=0.0, hl=False)
        for y in (830, 900, 980):
            p.cap((0, y), (W, y), 4, (170, 116, 76), shadow=0, hl=False)
        p.rrect(1560, 690, 1680, 960, 20, (70, 62, 96)); p.rrect(1520, 662, 1720, 704, 14, (110, 102, 138))
        p.ell(1620, 660, 100, 26, mix(RED, INK, .45))

    def base(self, t):
        return grad((26, 74, 92), (48, 112, 122), 0, 780)

    def prep(self):
        self.btn = Sprite(lambda p: (p.shape([(1532, 660)] + [(1620 + 88 * math.cos(math.radians(a)), 660 - 78 * math.sin(math.radians(a))) for a in range(0, 181, 6)][::-1], RED),
                                     p.ell(1590, 616, 26, 12, (255, 178, 170), rot=-0.5, shadow=0, hl=False), p.tag(1620, 800, "OFF", 40, ink=RED)), (1500, 520, 1740, 840))
        def back(p):
            p.rrect(1050, 690, 1250, 900, 30, mix(CORAL, INK, .15))
            p.rrect(1020, 800, 1070, 1010, 16, CORAL); p.rrect(1230, 800, 1280, 1010, 16, CORAL)
        def front(p):
            p.rrect(1060, 880, 1240, 1012, 22, CORAL)
            p.rrect(1078, 894, 1222, 940, 14, mix(CORAL, (255, 255, 255), .18), shadow=0, hl=False)
        self.cb = Sprite(back, (1000, 670, 1300, 1030)); self.cf = Sprite(front, (1040, 860, 1260, 1030))

    def draw(self, p, t):
        # light cone from above onto the chair
        p.shape([(1090, 0), (1210, 0), (1420, 1010), (890, 1010)], (255, 238, 190), shadow=0, hl=False, alpha=0.18)
        pk = pop_scale(t, 62.96, 0.3)
        self.btn.blit(p.img, s=pk, pivot=(1620, 700))
        if pk > 0.9:
            g = 0.25 + 0.15 * math.sin(t * 6)
            p.ell(1620, 640, 130, 60, RED, shadow=0, hl=False, alpha=g)
        self.cb.blit(p.img, s=pop_scale(t, 63.5, 0.3), pivot=(1150, 1010))
        # Wren walks over and sits: "somebody's gotta go sit there"
        walk = eio((t - 64.85) / 1.0)
        cx = lerp(560, 1150, walk)
        sit = eob((t - 65.88) / 0.25) if t > 65.88 else 0.0
        by_ = WY - 30 * sit * 1.0 + (-14 * abs(math.sin(math.pi * (t - BAR0) / BEAT)) if 0.05 < walk < 0.97 else 0.0)
        hands = [(cx - 58, by_ - 135 * 1.2 / 1.2), (cx + 65, by_ - 145)]
        ang = -1.35
        if t > 66.2:
            hands = [(cx - 58, by_ - 135), (cx + 90, by_ - 330)]           # thumbs up
        shrug = math.sin(math.pi * clamp((t - 64.55) / 0.45)) if 64.55 < t < 65.0 else 0.0
        if shrug > 0:
            hands = [(cx - 88, by_ - 190 - 30 * shrug), (cx + 95, by_ - 190 - 30 * shrug)]
        wren(p, cx, by_, 1.2, hands=hands, held=("shovel", 1, ang) if t <= 66.2 else None, look=0.6 if t < 65.9 else 0.0, smile=(0.0 if t < 65.0 else 1.5),
             blink=blink_at(t, [63.1, 64.3]))
        if sit > 0:
            pass
        self.cf.blit(p.img, s=pop_scale(t, 63.5, 0.3), pivot=(1150, 1010))
        sprig(p, lerp(330, 850, eio((t - 64.9) / 0.8)), WY + 6, 1.1, look=0.8, happy=0.6 if t < 65.9 else 1.9, tilt=3)
        word_tag(p, 1150, 620, "?", 130, t, 63.9, life=1.0, fill=(255, 226, 150), ink=INK, rot=0.05)
        word_tag(p, 1150, 560, "somebody", 60, t, 64.85, life=1.5, fill=CORAL, ink=CREAM, rot=-0.03)


# ================================================================== the scene
class Verse2(Scene):
    id = "verse2"; t0 = GAGS_T[0]; t1 = GAGS_T[-1]
    wipe_color = CORAL

    def setup(self):
        self.G = [Shog(), Clips(), Foom(), Button()]
        for g in self.G:
            g.ensure()
        self.hud = HudDial(1800, 930, 90)

    def frame(self, k, t):
        g = self.G[k]
        p = g.paper(t); g.draw(p, t)
        return p

    def paper(self, t=0.0):
        HALF = 0.16
        k = max([i for i in range(4) if t >= GAGS_T[i] - (HALF if i else 0)] or [0])
        # inside a push transition?
        for i in range(1, 4):
            a = GAGS_T[i] - HALF; b = GAGS_T[i] + HALF
            if a <= t <= b:
                old = self.frame(i - 1, min(t, GAGS_T[i] + 0.0)); new = self.frame(i, t)
                p = Paper(); p.img = push_transition(old, new, (t - a) / (2 * HALF))
                return p
        return self.frame(k, t)

    def draw(self, p, t):
        self.hud.draw(p, t, 0.0)
        caption(p, t, y=124)
