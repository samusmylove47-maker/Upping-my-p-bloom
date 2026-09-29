"""Final chorus: every bloom needs a trellis. The vines climb the lattice all chorus long, each rule (tested / written down / watched / honest)
gets nailed to the trellis, everybody sings, and on 'Tell your neighbor, tell your crew' a seed packet is passed hand to hand."""
from props import *
from sc_chorus import draw_wren, CROWD

X0, X1, Y0, Y1 = 690, 1230, 300, 1010
T_START = 143.93
GROW = 14.0
KINDS = ["book", "sun", "plus", "heart", "leaf", "note", "bulb"]
SIGNS = [(145.3, 505, 430, "tested", True), (147.15, 505, 560, "written down", True), (149.0, 1415, 430, "watched", False), (150.85, 1415, 560, "honest", False)]
# (x, feet, scale, colour index into CROWD)
SINGERS = [(100, 1050, .8, 0), (470, 1044, .85, 1), (615, 1050, .7, 2), (1560, 1046, .85, 3), (1700, 1050, .8, 4), (1845, 1052, .72, 5)]
FLOW_COLS = [CORAL, PINK, MARIGOLD, VIOLET, CREAM, (255, 160, 122)]


def vine_pt(v, i):
    ph = 0.4 if v == 0 else 0.4 + math.pi
    return (960 + 240 * math.sin(i / 60 * 9.4 + ph) * (0.55 + 0.45 * i / 60), 1010 - i / 60 * 700)


def final_static(p):
    layers = [(700, 22, 51, LEAF1), (770, 26, 52, LEAF2), (850, 30, 53, LEAF3), (940, 20, 54, LEAF4), (1010, 16, 55, LEAF5)]
    p.shape(hill_pts(*layers[0][:3]), layers[0][3], shadow=0.7)
    for x, b, h in [(250, 690, 150), (420, 700, 110), (1700, 700, 140)]:
        p.shape([(x - 5, b), (x + 5, b), (x + 2.5, b - h), (x - 2.5, b - h)], CREAM, shadow=0.4)
    p.shape(hill_pts(*layers[1][:3]), layers[1][3], shadow=0.8)
    for x, w_, h_, c in [(140, 70, 60, (255, 226, 196)), (250, 60, 48, (255, 200, 190)), (1560, 72, 62, (255, 226, 196)), (1690, 60, 50, (250, 214, 230)), (1810, 66, 56, (255, 226, 196))]:
        F.house(p, x, 790, w_, h_, c)
    for l in layers[2:]:
        p.shape(hill_pts(*l[:3]), l[3], shadow=0.9)
    # the trellis
    for cxl in (X0, X0 + 180, X0 + 360):
        for yy in range(Y0, Y1 - 1, 178):
            p.cap((cxl + 6, yy + 6), (cxl + 174, yy + 172), 8, (206, 156, 100), shadow=0.25, hl=False)
            p.cap((cxl + 174, yy + 6), (cxl + 6, yy + 172), 8, (206, 156, 100), shadow=0.25, hl=False)
    for yy in range(Y0, Y1 - 1, 178):
        p.rrect(X0 - 8, yy - 9, X1 + 8, yy + 9, 6, mix(WOOD, (255, 255, 255), .1), shadow=0.6)
    p.cap((X0, Y1), (X0, Y0 - 20), 26, WOOD); p.cap((X1, Y1), (X1, Y0 - 20), 26, WOOD)
    p.rrect(X0 - 34, Y0 - 48, X1 + 34, Y0 - 12, 14, WOOD)


class Final(Stage):
    id = "final"; t0 = T_START
    wipe_color = MARIGOLD

    def static(self, p): final_static(p)

    def cam(self, t):
        return (cam_pulse(t, 0.016 if t < 157.7 else 0.024), 960, 560)

    def prep(self):
        q = Paper(); q.img = to_img(grad((140, 206, 240), (255, 238, 205), 0, 780))
        for i, c in enumerate([CORAL, MARIGOLD, SUN2, LEAF2, SKY, VIOLET]):
            q.shape(annular(960, 930, 700 + i * 26, 726 + i * 26, 180, 360, 80), c, shadow=0.0, hl=False, alpha=.55)
        self.sky = np.asarray(q.img, np.float32)
        self.sun = Sprite(lambda p: sun(p, 1560, 380, 80, rays=20), (1380, 200, 1740, 560))
        self.cl = Sprite(lambda p: small_cloud(p, 400, 300, 1.0, CREAM), (100, 100, 720, 440))
        self.blade = Sprite(lambda p: [p.shape(leaf_pts(300, 300, 100, 14, k * 2.094), CREAM, shadow=0.3, sh_off=(1, 2), sh_blur=2) for k in range(3)], (180, 180, 420, 420))
        # the flowers with their little icons
        self.fl = []
        fr = random.Random(8)
        j = 0
        for v, start in ((0, 10), (1, 12)):
            for i in range(start, 60, 5):
                x, y = vine_pt(v, i)
                r = 34 + 14 * (i / 60)
                col = FLOW_COLS[j % len(FLOW_COLS)]; kind = KINDS[j % len(KINDS)]; rot = fr.uniform(0, 6); pet = 6 if j % 2 else 8
                box = (int(x - r * 1.3), int(y - r * 1.3), int(x + r * 1.3), int(y + r * 1.3))
                spr = Sprite(lambda p, x=x, y=y, r=r, col=col, kind=kind, rot=rot, pet=pet: (flower(p, x, y, r, col, SUN2, pet, rot), F._icon(p, x, y, r, kind)), box)
                self.fl.append((i, v, x, y, spr)); j += 1
        self.packet = Sprite(lambda p: (p.rrect(240, 240, 330, 320, 10, CREAM), p.rrect(240, 240, 330, 262, 8, CORAL, shadow=0, hl=False),
                                        flower(p, 285, 292, 20, PINK, SUN2, 6, 0.3)), (215, 215, 355, 345))
        self.hud = HudDial(1830, 205, 84)

    def base(self, t):
        return self.sky

    def backdrop(self, t, q):
        lt = t - T_START
        for k, (X, Y, s, sp) in enumerate([(330, 300, .62, 8), (1240, 170, .48, 12), (560, 520, .38, 9), (1480, 600, .36, 7)]):
            self.cl.blit(q.img, dx=X - 400 + sp * lt, dy=Y - 300, s=s, pivot=(400, 300))
        self.sun.blit(q.img, rot=lt * 0.25, pivot=(1560, 380))
        for (x, b, h, a0) in [(250, 690, 150, 0.4), (420, 700, 110, 1.2), (1700, 700, 140, 0.9)]:
            self.blade.blit(q.img, dx=x - 300, dy=b - h - 300, rot=a0 + lt * 1.6 * (150 / h) * 0.5, pivot=(300, 300), s=h / 150.0 * 1.0)

    def draw(self, p, t):
        lt = t - T_START
        k, u = beat_of(t)
        # vines
        g = clamp((t - 144.4) / GROW)
        d = ImageDraw.Draw(p.img)
        vp = []
        for v in (0, 1):
            n = int(g * 60)
            pts = [vine_pt(v, i) for i in range(n + 1)]
            if len(pts) > 1:
                d.line(pts, fill=mixc(LEAF4, LEAF5, .3), width=12, joint="curve")
            vp.append(pts)
            for i in range(2, n, 2):
                x, y = pts[i]
                p.shape(leaf_pts(x, y, 54, 19, -0.9 if i % 4 == 0 else -2.3), [LEAF2, LEAF3, LEAF1][(i // 2 + v) % 3], shadow=0.35, sh_off=(1, 2), sh_blur=2)
        for (i, v, x, y, spr) in self.fl:
            if i <= g * 60:
                tb = T_START + 1.0 + (i / 60.0) * GROW * 0.95 - 0.3
                tb = beat_t(math.ceil((tb - BAR0) / BEAT))
                s = pop_scale(t, tb, 0.3)
                if s > 0.02:
                    spr.blit(p.img, s=s * (1 + 0.04 * (1 - u) ** 2), pivot=(x, y))
        # rules nailed to the trellis
        for (ts, x, y, s_, left) in SIGNS:
            if t < ts:
                continue
            ax = X0 if left else X1
            kk = pop_scale(t, ts, 0.3)
            p.cap((ax, y), (x + (110 if left else -110), y), 5, (120, 92, 70), shadow=0, hl=False)
            p.tag(x, y, s_, max(8, int(38 * kk)), fill=(250, 236, 208), padx=26, pady=12, rot=-0.03 if left else 0.03)
        # Nimbus, rained-out and happy
        nx, ny = 330, 300 + 8 * math.sin(t * 1.3)
        nimbus(p, nx, ny, 0.7, col=(224, 216, 244), dark=(190, 180, 222), mood="happy")
        rain(p.img, t, nx - 90, nx + 90, ny + 70, ny + 400, n=16, seed=13, slant=0.0, speed=260, ln=18, w=4)
        # the singers
        draw_wren(p, t, T_START, 270, 1044, 1.3, look=0.4)
        for j, (x, by, s, ci) in enumerate(SINGERS):
            shirt, bib, skin, hatc, hat = CROWD[ci][3:]
            e = eob((t - (T_START + 0.3 + j * 0.12)) / 0.4)
            if e > 0.02:
                draw_wren(p, t, T_START, x, by, s * e, shirt=shirt, bib=bib, skin=skin, hatc=hatc or STRAW, hat=hat)
        sx = 1400
        hop = 14 * abs(math.sin(math.pi * u))
        sprig(p, sx, 1052 - hop, 1.35, look=-0.4, happy=1.8, bloom=1.0, tilt=4 * math.sin(t * 3))
        # pass it on: a seed packet goes from hand to hand
        if 159.61 <= t < 163.9:
            chain = [(270, 1044, 1.3)] + [(SINGERS[i][0], SINGERS[i][1], SINGERS[i][2]) for i in (1, 2)] + [(sx, 1052, 1.35)] + [(SINGERS[i][0], SINGERS[i][1], SINGERS[i][2]) for i in (3, 4, 5)]
            hopn = (t - 159.61) / 0.55
            a = min(len(chain) - 2, int(hopn)); uu = hopn - a
            if hopn < len(chain) - 1:
                (x0_, y0_, s0_), (x1_, y1_, s1_) = chain[a], chain[a + 1]
                hy = -300
                x = lerp(x0_, x1_, eio(uu)); y = lerp(y0_ + hy * s0_ / 1.3, y1_ + hy * s1_ / 1.3, eio(uu)) - 170 * math.sin(math.pi * uu)
                self.packet.blit(p.img, dx=x - 285, dy=y - 280, rot=uu * 3.0, pivot=(285, 280))
        # bursts on every bar
        for j in range(12):
            burst(p.img, t, bar_t(78 + j) + 0.36, seed=200 + j, n=40 if j not in (0, 4, 8) else 70, cx=960, cy=400)
        self.hud.draw(p, t, T_START + 0.1)
        # the theme tag
        p.tag(960, 226, "Every bloom needs a trellis.", 42, fill=(255, 226, 150), pady=14)
        caption(p, t, y=124)
