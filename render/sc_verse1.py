"""Verse 1: a scary chart on a scary screen -> the storm is real -> a forecast is a question -> bloom is work -> pack a lunch -> my helper too."""
from props import *

WY = 1000                       # Wren's feet
CH = random.Random(5)
CHART = [(1090 + i * 40, 655 - 21 * i - max(0, i - 6) * 3 + CH.uniform(-24, 24)) for i in range(14)]
SHARE = [(13.30, "SHARE", 900, 300), (13.72, "worst-case!!", 560, 380), (14.12, "thread 1/47", 1040, 470), (14.48, "RT RT RT", 690, 560), (14.70, "read this", 360, 300)]
ITEMS = [("lunch", 22.88), ("spade", 23.36), ("hat", 23.96)]


def monitor_static(p):
    p.rrect(1300, 700, 1420, 815, 20, mix(PLUM, INK, .3))
    p.rrect(1200, 800, 1520, 838, 14, mix(PLUM, INK, .45))
    p.rrect(1020, 290, 1700, 730, 40, mix(PLUM, INK, .15))
    p.rrect(1046, 316, 1674, 704, 24, (22, 14, 40), shadow=0, hl=False)


def bag_back(p):
    p.ell(1250, 826, 96, 22, (60, 38, 40), shadow=0.4)


def bag_front(p):
    p.rrect(1150, 826, 1350, 995, 42, (176, 110, 70))
    p.rrect(1170, 906, 1330, 980, 24, (196, 130, 84), shadow=0.4)
    p.rrect(1150, 826, 1350, 862, 20, (156, 94, 60))
    p.ell(1250, 876, 15, 15, MARIGOLD, shadow=0.4)
    p.cap((1178, 850), (1160, 980), 14, (120, 76, 50), shadow=0.3, hl=False)


def item_lunch(p):
    p.rrect(1210, 270, 1310, 335, 14, CORAL)
    p.cap((1235, 270), (1285, 270), 10, mix(CORAL, INK, .3), shadow=0.3, hl=False)
    p.rrect(1204, 296, 1316, 306, 4, CREAM, shadow=0, hl=False)
    p.ell(1260, 322, 8, 8, MARIGOLD, shadow=0, hl=False)


def item_spade(p):
    shovel(p, (1260, 235), 1.35, length=100, blade=(34, 44))


def item_hat(p):
    p.shape(ell_pts(1260, 300, 66, 14, seed=5), STRAW, shadow=0.7)
    p.shape(ell_pts(1260, 286, 36, 28, seed=6), mix(STRAW, (255, 255, 255), .12), shadow=0.5)
    p.rrect(1226, 284, 1294, 298, 5, CORAL, shadow=0, hl=False)


ITEM_FN = {"lunch": (item_lunch, (1190, 250, 1330, 350)), "spade": (item_spade, (1215, 215, 1330, 360)), "hat": (item_hat, (1180, 255, 1340, 335))}
ITEM_C = {"lunch": (1260, 302), "spade": (1265, 290), "hat": (1260, 296)}


class Verse1(Stage):
    id = "verse1"; t0 = 11.64; t1 = 26.2
    wipe_color = CORAL

    def static(self, p):
        hills_static(p, [(790, 22, mix(LEAF4, NIGHT_T, .5)), (875, 26, mix(LEAF4, NIGHT_T, .32)), (960, 22, mix(LEAF5, NIGHT_T, .12))], 24)

    def prep(self):
        self.mon = Sprite(monitor_static, (980, 250, 1740, 860))
        self.bb = Sprite(bag_back, (1130, 790, 1370, 860))
        self.bf = Sprite(bag_front, (1120, 800, 1380, 1030))
        self.items = {k: Sprite(f, b) for k, (f, b) in ITEM_FN.items()}
        self.hud = HudDial(1800, 930, 90)

    def base(self, t):
        u = eio((t - 16.9) / 5.0)
        return grad(mixc(NIGHT_T, (146, 158, 222), u), mixc(NIGHT_B, (255, 206, 164), u), 0, 860)

    # ------------------------------------------------------------ cast positions
    def wx(self, t):
        return 640

    def nimbus_at(self, t):
        if t < 14.7:
            return None
        if t < 18.9:
            u = eoc((t - 14.7) / 1.5)
            return (lerp(-330, 470, u) + 12 * math.sin(t * 1.2), 300 + 8 * math.sin(t * 1.7), 1.15)
        if t < 20.7:
            u = eio((t - 18.9) / 1.2)
            return (lerp(470, 1500, u), lerp(300, 260, u), lerp(1.15, 0.85, u))
        u = eio((t - 20.7) / 1.0)
        return (1500 + 40 * math.sin(t * 0.9), lerp(260, 728, u) + 10 * math.sin(t * 1.6), 0.85)

    def backdrop(self, t, q):
        n = self.nimbus_at(t)
        if n:
            nimbus(q, n[0], n[1], n[2], mood="grumpy")

    # ------------------------------------------------------------ pieces
    def monitor(self, p, t):
        if t < 11.5:
            return
        dx = 900 * eio((t - 18.72) / 0.6) if t > 18.72 else 0.0
        k = pop_scale(t, 11.45, 0.35)
        self.mon.blit(p.img, dx=dx, s=k, pivot=(1360, 520))
        if k < 0.98 or dx > 880:
            return
        d = ImageDraw.Draw(p.img)
        d.line([(1080 + dx, 350), (1080 + dx, 672), (1640 + dx, 672)], fill=(120, 110, 150), width=4)
        for gy in (400, 470, 540, 610):
            d.line([(1080 + dx, gy), (1640 + dx, gy)], fill=(52, 42, 84), width=2)
        p.text(1172 + dx, 352, "P(DOOM)", 32, (255, 118, 108), shadow=0, hl=False)
        fr = clamp((t - 11.9) / 1.25)
        n = fr * (len(CHART) - 1); i = int(n); u = n - i
        pts = [(x + dx, y) for x, y in CHART[:i + 1]]
        if i < len(CHART) - 1:
            a, b = CHART[i], CHART[i + 1]
            pts.append((lerp(a[0], b[0], u) + dx, lerp(a[1], b[1], u)))
        if len(pts) > 1:
            d.line(pts, fill=(120, 30, 56), width=24, joint="curve")
            d.line(pts, fill=(255, 92, 80), width=10, joint="curve")
            hx, hy = pts[-1]
            d.ellipse([hx - 13, hy - 13, hx + 13, hy + 13], fill=(255, 226, 190))
        # 17.64 "question" -> a question mark; 17.96 "not the end" -> THE END gets crossed out
        if t > 17.0:
            pulse = 0.5 + 0.5 * math.sin(t * 9) if t < 17.9 else 1.0
            a_end = clamp((t - 17.96) / 0.15) * (1 - 0.7 * clamp((t - 18.3) / 0.25))
            if a_end > 0:
                blend_overlay(p, lambda q: q.text(1300 + dx, 560, "THE END", 96, RED, shadow=0.0, hl=False), a_end)
                if t > 18.3:
                    k2 = clamp((t - 18.3) / 0.18)
                    d.line([(1120 + dx, 566), (1120 + dx + 360 * k2, 548)], fill=CORAL, width=14)
        if t > 17.64:
            k3 = eob((t - 17.64) / 0.3)
            sz = int(300 * k3)
            if sz > 10:
                p.text(1588 + dx, 438, "?", int(sz * 0.8), CORAL, shadow=0.0, hl=False)
                p.text(1580 + dx, 430, "?", int(sz * 0.8), CREAM)

    def shares(self, p, t):
        for (ts, s_, x, y) in SHARE:
            if t < ts:
                continue
            u = eob((t - ts) / 0.4)
            xx = lerp(1360, x, u); yy = lerp(470, y, u) - 60 * math.sin(math.pi * clamp((t - ts) / 0.4))
            fade = 1 - clamp((t - 16.5) / 0.4)
            if fade <= 0:
                continue
            sz = max(8, int(40 * clamp(u * 1.3)))
            blend_overlay(p, lambda q, s_=s_, xx=xx, yy=yy, sz=sz: q.tag(xx, yy + 5 * math.sin(t * 3 + xx), s_, sz, fill=mix(PLUM, INK, .25), ink=CREAM, rot=math.sin(xx) * 0.05), fade)

    def wren_pose(self, t):
        """(hands, held-angle, look, smile, dig amount)"""
        cx = self.wx(t)
        if 19.65 < t < 23.5:
            f = 1.0 if t < 21.6 else 2.0                               # 'don't shirk' -> digs twice as fast
            if t < 21.6:
                ph = ((t - BAR0) / (2 * BEAT)) % 1.0
            else:
                ph = ((t - BAR0) / BEAT) % 1.0
            down = 1 - eio(ph / 0.6) if ph < 0.6 else eio((ph - 0.6) / 0.4)
            hands, ang, tip = dig_hands(cx, WY, 1.2, down)
            return hands, ang, 0.6, 1.4, down, tip, ph
        look = 0.6 if t < 15 else (-0.5 if t < 16.6 else 0.6)
        smile = -0.3 if t < 17.0 else 0.9
        R = (cx + 62 * 1.2, WY - 121 * 1.2)
        return [(cx - 48 * 1.2, WY - 112 * 1.2), R], -1.35, look, smile, None, None, 0.0

    def draw(self, p, t):
        cx = self.wx(t)
        # the screen and what it spawns
        self.monitor(p, t)
        self.shares(p, t)
        # nimbus rain and bolts
        n = self.nimbus_at(t)
        if n and t < 20.8:
            rain(p.img, t, n[0] - 150, n[0] + 130, n[1] + 60, 940, n=34 if t < 18.9 else 16, seed=8)
        if 15.32 <= t < 15.45:
            draw_bolt(p, n[0] + 90, n[1] + 110, 250, 990, seed=6)
        if 15.32 <= t < 15.6:
            flash(p.img, 0.35 * (1 - (t - 15.32) / 0.28))
        # the garden: hole, mound, sprout
        n_dig = max(0, int((t - 19.7) / (2 * BEAT))) if t > 19.7 else 0
        hole = (cx + 300, WY + 50)
        if t > 19.7:
            p.ell(hole[0], hole[1], 60, 16, (60, 38, 40), shadow=0.2)
            m = min(1.0, n_dig / 5.0)
            if m > 0.05:
                p.shape(ell_pts(hole[0] + 120, hole[1] + 4, 70 * m + 10, 30 * m + 4, 0, jit=0.03, seed=3), (126, 88, 62), shadow=0.8)
        if t > 20.6:
            sprout(p, hole[0], hole[1] - 6, eoc((t - 20.6) / 3.5), bloom=eob((t - 25.7) / 0.5) if t > 25.7 else 0.0)
        # Wren
        hands, ang, look, smile, down, tip, ph = self.wren_pose(t)
        nod = 8 * math.sin(math.pi * clamp((t - 15.5) / 0.4)) if 15.5 < t < 15.9 else 0.0
        if 25.4 < t < 25.9:
            nod = 10 * math.sin(math.pi * (t - 25.4) / 0.5)
        wren(p, cx, WY + nod * 0.5, 1.2, hands=hands, held=("shovel", 1, ang), look=look, smile=smile,
             blink=blink_at(t, [13.0, 17.4, 21.2, 25.0]))
        if tip is not None and t > 19.7:
            k = int((t - BAR0) / (2 * BEAT if t < 21.6 else BEAT))
            ts = BAR0 + k * (2 * BEAT if t < 21.6 else BEAT)
            dirt_puff(p, hole[0], hole[1] - 8, t - ts, seed=k)
        # Sprig
        sx = lerp(cx + 240, cx - 250, eio((t - 18.9) / 0.9))     # Sprig rolls round to Wren's other side so the shovel has room
        hop = 0.0; happy = 0.8; tilt = 3 * math.sin(t * 2)
        if t < 17.0:
            happy = -0.6
        if 24.24 <= t < 26.2:
            hop = -34 * abs(math.sin(math.pi * (t - 24.24) / BEAT))
            happy = 1.9
        blm = None
        sprig(p, sx, WY + 6 + hop, 1.1, look=0.5 if t > 17 else -0.4, happy=happy, tilt=tilt)
        if 24.44 <= t < 26.2:                                       # the "5.5" badge sparkles on "helper"
            for j in range(3):
                a = t * 3 + j * 2.1
                star4(p, sx + 45 + 30 * math.cos(a), WY - 48 + 30 * math.sin(a) + hop, 12 + 4 * math.sin(t * 8 + j), a, SUN2)
        # bag and packing
        if t > 22.2:
            k = pop_scale(t, 22.2, 0.3)
            self.bb.blit(p.img, s=k, pivot=(1250, 990))
            for name, ts in ITEMS:
                u = (t - (ts - 0.55)) / 0.55
                if 0 < u < 1.0:
                    sx0, sy0 = cx + 90, WY - 300
                    x = lerp(sx0, 1250, eio(u)); y = lerp(sy0, 815, u * u) - 190 * math.sin(math.pi * u)
                    self.items[name].blit(p.img, dx=x - ITEM_C[name][0], dy=y - ITEM_C[name][1], rot=u * 4.0, pivot=ITEM_C[name])
            wob = 0.05 * sum(math.exp(-(t - ts) * 9) * math.sin((t - ts) * 40) for (_, ts) in ITEMS if t > ts)
            self.bf.blit(p.img, s=k, sx=k * (1 + wob), sy=k * (1 - wob), pivot=(1250, 990))
        # tags on the key words
        word_tag(p, 1480, 300, "weather", 44, t, 19.32, life=0.9, fill=(224, 216, 244), ink=INK, rot=-0.04)
        word_tag(p, cx + 100, 560, "work", 54, t, 20.24, life=0.9, fill=CORAL, ink=CREAM, rot=0.04)
        # hud dial: the needle moves when things get done
        self.hud.draw(p, t, 19.85)
        caption(p, t, y=124)
