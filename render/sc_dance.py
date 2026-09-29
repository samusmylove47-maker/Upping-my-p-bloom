"""Dance break (Dig! Plant! Water! BLOOM! -- the clip built to be copied) and Verse 3 (the roll call that ends on YOU)."""
from props import *
from sc_chorus import pose, draw_wren, CROWD

CHANT = [92.92, 96.59]                 # "Dig!" of each chant; BLOOM! lands on the following downbeat
WORDS = ["DIG!", "PLANT!", "WATER!", "BLOOM!"]


class Dance(Stage):
    id = "dance"; t0 = 92.48
    wipe_color = VIOLET

    def static(self, p):
        p.shape([(0, 880), (W, 880), (W, H), (0, H)], mix(PLUM, INK, .05), shadow=0.6)
        for x in range(-500, W + 500, 220):
            p.cap((960 + (x - 960) * 0.72, 884), (x, H), 5, mix(PLUM, INK, .4), shadow=0, hl=False)
        for side in (0, 1):
            pts = [(0, 0), (330, 0)] + [(330 - 70 * (y / 1080.0) + 16 * math.sin(y * 0.03), y) for y in range(0, 1081, 30)] + [(0, 1080)]
            if side:
                pts = [(W - x, y) for x, y in pts]
            p.shape(pts, mix(CORAL, INK, .38), shadow=1.0)
            for f in range(3):
                fx = 60 + f * 90
                pts2 = [(fx + 8 * math.sin(y * 0.03 + f), y) for y in range(0, 1081, 40)]
                if side:
                    pts2 = [(W - x, y) for x, y in pts2]
                for i in range(len(pts2) - 1):
                    p.cap(pts2[i], pts2[i + 1], 5, mix(CORAL, INK, .55), shadow=0, hl=False)

    def base(self, t):
        return grad((150, 54, 130), (255, 140, 120), 0, 880)

    def backdrop(self, t, q):
        for j, sx in enumerate([560, 960, 1360]):
            sw = 260 * math.sin(t * 1.3 + j * 2.1)
            q.shape([(sx, -20), (sx - 200 + sw, 900), (sx + 200 + sw, 900)], (255, 240, 200), shadow=0, hl=False, alpha=0.14)
        # disco ball
        q.cap((960, -10), (960, 130), 5, (200, 190, 220), shadow=0, hl=False)
        q.ell(960, 190, 62, 62, (214, 220, 240), shadow=0.8)
        for k in range(10):
            a = t * 1.2 + k * 0.63
            q.ell(960 + 40 * math.sin(a), 190 + 42 * math.cos(a * 1.3), 9, 6, (255, 255, 255), shadow=0, hl=False, alpha=0.7)

    def active(self, t):
        for c, base in enumerate(CHANT):
            k = (t - base) / BEAT
            if -0.02 <= k < 5.6:
                return c, min(3, int(max(0, k)))
        return None, None

    def draw(self, p, t):
        c, w = self.active(t)
        # the four move cards (the learn-it-in-a-glance strip)
        for i, name in enumerate(WORDS):
            on = (w == i)
            cx = 585 + 250 * i
            if on:
                base = CHANT[c] + i * BEAT
                sz = int(50 * (1 + 0.45 * (1 - min(1, (t - base) * 5)) ** 2))
                p.tag(cx, 330, name, sz, fill=CORAL if i == 3 else CREAM, ink=CREAM if i == 3 else INK, rot=0.0)
            else:
                p.tag(cx, 330, name, 34, fill=mix(PLUM, CREAM, .25), ink=mix(CREAM, PLUM, .3), padx=26, pady=12)
        # giant word behind the dancer
        if w is not None:
            base = CHANT[c] + w * BEAT
            g = 1 - min(1, (t - base) / BEAT)
            p.text(960, 640, WORDS[w], int(290 + 40 * g), CREAM, shadow=0.0, hl=False, alpha=0.22 + 0.2 * g)
        # dancers: Wren centre stage, Sprig, and the crowd who learn the moves on the second time round
        t0 = CHANT[0]
        draw_wren(p, t, t0, 960, 1010, 1.7, look=0.0)
        if t > 96.05:
            for j, (x, by, s, shirt, bib, skin, hatc, hat) in enumerate(CROWD):
                e = eob((t - (96.05 + j * 0.09)) / 0.35)
                if e > 0.02:
                    draw_wren(p, t, t0, x, by, s * e * 1.05, shirt=shirt, bib=bib, skin=skin, hatc=hatc or STRAW, hat=hat)
        k, u = beat_of(t)
        sprig(p, 1460, 1050 - 16 * abs(math.sin(math.pi * u)), 1.5, look=-0.4, happy=1.9, bloom=1.2 if t > 94.3 else None, tilt=4 * math.sin(t * 3))
        # bursts on each BLOOM!
        for j, base in enumerate(CHANT):
            burst(p.img, t, base + 3 * BEAT + 0.02, seed=40 + j, n=70, cx=960, cy=520)
        word_tag(p, 500, 600, "copy the moves!", 64, t, 95.05, life=1.3, fill=(255, 226, 150), ink=INK, rot=-0.05)
        word_tag(p, 1420, 600, "everybody!", 74, t, 96.05, life=0.5, fill=CORAL, ink=CREAM, rot=0.05)


# ====================================================================== verse 3
XS, YS = [255, 680, 1105], [400, 780]
LABS = ["testing it\nbefore it flies", "teaching the kids\nto ask why", "writing the\nrules down right",
        "chasing a cure\nthrough the night", "telling the truth\nwhen it's hard", "watering the\nneighbor's yard"]
ROTS = [-0.015, 0.012, -0.01, 0.014, -0.012, 0.01]
NIGHTW = (52, 40, 96)


def tile_art(p, k):
    """One roll-call tile (ported from the still frame f5)."""
    cx, cy = XS[k % 3], YS[k // 3]
    F.tile2(p, cx, cy, ROTS[k]); F._label(p, cx, cy + 104, LABS[k])
    cy = cy - 34
    if k == 0:                                                        # testing it before it flies
        p.rrect(cx - 70, cy - 90, cx + 70, cy + 68, 16, (235, 212, 176)); p.rrect(cx - 30, cy - 104, cx + 30, cy - 78, 8, (150, 140, 170))
        for i in range(3):
            y = cy - 48 + i * 40
            if i < 2:
                p.cap((cx - 50, y), (cx - 41, y + 10), 8, LEAF4, shadow=0, hl=False); p.cap((cx - 41, y + 10), (cx - 24, y - 10), 8, LEAF4, shadow=0, hl=False)
            else:
                p.cap((cx - 50, y - 9), (cx - 28, y + 11), 8, RED, shadow=0, hl=False); p.cap((cx - 28, y - 9), (cx - 50, y + 11), 8, RED, shadow=0, hl=False)
            p.cap((cx - 6, y), (cx + 48, y), 8, (200, 178, 150), shadow=0, hl=False)
    elif k == 1:                                                      # teaching the kids to ask why
        for dx, col in [(-70, CORAL), (2, TEAL)]:
            p.rrect(cx + dx - 32, cy + 20, cx + dx + 32, cy + 80, 18, col); p.ell(cx + dx, cy - 8, 30, 30, SKIN)
            p.ell(cx + dx - 10, cy - 10, 4, 5, INK, shadow=0, hl=False); p.ell(cx + dx + 10, cy - 10, 4, 5, INK, shadow=0, hl=False)
        p.shape(ell_pts(cx + 82, cy - 62, 72, 44), (255, 255, 255)); p.shape([(cx + 34, cy - 32), (cx + 56, cy - 22), (cx + 28, cy + 4)], (255, 255, 255), shadow=0, hl=False)
        p.text(cx + 82, cy - 62, "why?", 42, INK, shadow=0, hl=False)
    elif k == 2:                                                      # writing the rules down right
        p.rrect(cx - 84, cy - 76, cx + 84, cy + 68, 12, (250, 236, 208))
        for dx in (-84, 84):
            p.ell(cx + dx, cy - 4, 18, 76, (218, 190, 150))
        for i in range(4):
            p.cap((cx - 56, cy - 44 + i * 28), (cx + 16 - (i == 3) * 36, cy - 44 + i * 28), 8, (190, 168, 140), shadow=0, hl=False)
        p.ell(cx + 52, cy + 28, 28, 28, CORAL); p.cap((cx + 41, cy + 28), (cx + 49, cy + 37), 6, CREAM, shadow=0, hl=False); p.cap((cx + 49, cy + 37), (cx + 64, cy + 18), 6, CREAM, shadow=0, hl=False)
    elif k == 3:                                                      # chasing a cure through the night
        p.rrect(cx - 150, cy - 110, cx + 150, cy + 62, 22, NIGHTW, shadow=0)
        p.ell(cx + 104, cy - 66, 24, 24, SUN2, shadow=0.3); p.ell(cx + 115, cy - 73, 20, 20, NIGHTW, shadow=0, hl=False)
        p.ell(cx + 6, cy - 4, 72, 72, (170, 255, 210), shadow=0, hl=False, alpha=0.22)
        p.rrect(cx - 150, cy + 36, cx + 150, cy + 62, 8, WOOD)
        p.rrect(cx - 14, cy - 54, cx + 14, cy - 16, 5, (214, 242, 238))
        p.shape([(cx - 14, cy - 18), (cx + 14, cy - 18), (cx + 52, cy + 36), (cx - 52, cy + 36)], (204, 238, 234), shadow=0.4)
        p.shape([(cx - 30, cy + 8), (cx + 30, cy + 8), (cx + 50, cy + 36), (cx - 50, cy + 36)], (120, 220, 170), shadow=0, hl=False)
        p.cap((cx, cy + 10), (cx, cy - 12), 5, LEAF4, shadow=0, hl=False)
        p.shape(leaf_pts(cx, cy - 10, 26, 9, -0.6), LEAF2, shadow=0, hl=False); p.shape(leaf_pts(cx, cy - 10, 26, 9, -2.5), LEAF3, shadow=0, hl=False)
        p.rrect(cx - 130, cy + 22, cx - 88, cy + 36, 5, (150, 140, 170))
        p.cap((cx - 108, cy + 24), (cx - 100, cy - 26), 9, (200, 190, 220), shadow=0.3)
        p.cap((cx - 94, cy - 38), (cx - 118, cy - 2), 15, (150, 140, 170), shadow=0.3)
    elif k == 4:                                                      # telling the truth when it's hard
        p.shape(ell_pts(cx, cy - 14, 150, 74), (255, 255, 255))
        p.shape([(cx - 58, cy + 40), (cx - 98, cy + 84), (cx - 14, cy + 54)], (255, 255, 255), shadow=0, hl=False)
        p.text(cx, cy - 36, "I don't know…", 44, INK, shadow=0, hl=False)
        p.text(cx, cy + 8, "yet.", 46, CORAL, shadow=0, hl=False)
    else:                                                             # watering the neighbor's yard
        for i in range(5):
            x = cx - 4 + i * 30
            p.shape([(x - 11, cy + 82), (x - 11, cy - 26), (x, cy - 44), (x + 11, cy - 26), (x + 11, cy + 82)], (240, 226, 196))
        p.cap((cx - 24, cy + 4), (cx + 136, cy + 4), 6, (200, 184, 156), shadow=0, hl=False); p.cap((cx - 24, cy + 46), (cx + 136, cy + 46), 6, (200, 184, 156), shadow=0, hl=False)
        p.rrect(cx - 148, cy - 30, cx - 78, cy + 38, 18, TEAL)
        p.shape([(cx - 86, cy - 14), (cx - 24, cy - 64), (cx - 15, cy - 53), (cx - 80, cy + 4)], mix(TEAL, INK, .15))
        for x, r, c in [(cx + 40, 20, PINK), (cx + 96, 16, MARIGOLD)]:
            stem_flower(p, x, cy + 82, 62, r, c, petals=5)


def you_tile(p):
    fx0, fy0, fx1, fy1 = 1392, 235, 1860, 945
    p.rrect(fx0, fy0, fx1, fy1, 40, (255, 236, 200), shadow=0, hl=False, alpha=0.13)
    F.dashed_rrect(p, fx0 + 8, fy0 + 8, fx1 - 8, fy1 - 8, CORAL, 7)
    p.text(1626, 340, "somebody is…", 40, CREAM, shadow=0, hl=False)


class Verse3(Stage):
    id = "verse3"; t0 = 98.5
    wipe_color = VIOLET

    def base(self, t):
        return grad((58, 40, 92), (120, 84, 150), 0, H)

    def backdrop(self, t, q):
        stars(q.img, t, n=70, ymax=1000, seed=9, col=(255, 240, 210))

    def prep(self):
        self.tiles = []
        for k in range(6):
            cx, cy = XS[k % 3], YS[k // 3]
            self.tiles.append(Sprite(lambda p, k=k: tile_art(p, k), (cx - 225, cy - 195, cx + 225, cy + 195)))
        self.you = Sprite(you_tile, (1360, 205, 1890, 975))
        self.hud = HudDial(1810, 1008, 62)
        self.tt = [LT("verse3", i) + 0.95 for i in range(6)]

    def draw(self, p, t):
        for k in range(6):
            s = pop_scale(t, self.tt[k], 0.32)
            if s <= 0:
                continue
            cx, cy = XS[k % 3], YS[k // 3]
            wob = 0.02 * math.sin((t - self.tt[k]) * 14) * math.exp(-(t - self.tt[k]) * 4)
            self.tiles[k].blit(p.img, s=s, rot=(-0.05 * (1 - s)) + wob, pivot=(cx, cy))
            # a little life on top of each tile once it has landed
            e = t - self.tt[k]
            if k == 3 and s > 0.9:
                for j, (sx, sy) in enumerate([(-110, -84), (-40, -96), (30, -76), (70, -100), (-80, -50), (10, -50)]):
                    r = 3 + 2 * math.sin(t * 4 + j * 1.7)
                    p.ell(cx + sx, cy - 34 + sy, max(0.5, r), max(0.5, r), CREAM, shadow=0, hl=False)
            if k == 5 and s > 0.9:
                for j in range(4):
                    ph = (t * 1.6 + j * 0.25) % 1.0
                    p.ell(cx - 120 + 10 * j + 22 * ph, cy - 34 - 20 + 96 * ph, 5, 8, SKY, shadow=0.2, sh_off=(1, 2), sh_blur=2)
            if k == 0 and s > 0.9 and e > 0.4:
                pass
        # the empty tile that says you
        ty = LT("verse3", 6)
        if t > ty:
            s = pop_scale(t, ty, 0.35)
            self.you.blit(p.img, s=s, pivot=(1626, 590))
            pulse = 1 + 0.04 * math.sin((t - LT("verse3", 7)) * 9) if t > LT("verse3", 7) else 1.0
            if t > 124.35:
                g = eob((t - 124.35) / 0.3)
                sz = int(175 * g)
                p.text(1632, 566, "you", sz, (255, 190, 175), shadow=0.0, hl=False)
                p.text(1626, 558, "you", sz, CORAL, shadow=0.0, hl=False)
        k, u = beat_of(t)
        yell = 0.0 if t < 124.35 else 1.0
        sprig(p, 1626, 1052 - (30 * abs(math.sin(math.pi * u)) if t > 122.9 else 0), 0.95, look=-0.5, happy=1.5, tilt=3, bloom=(1.0 if t > 124.35 else None))
        burst(p.img, t, 124.4, seed=77, n=50, cx=1626, cy=560, life=0.8)
        self.hud.draw(p, t, 98.7)
        caption(p, t, y=124)
