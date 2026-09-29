import sys, random, math, time
from paper import *
import credits

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
os.makedirs(OUT, exist_ok=True)

FCOLS = [CORAL, PINK, MARIGOLD, VIOLET, CREAM, (255, 160, 122)]


def scatter_flowers(p, y0, y1, n, seed, rmin=16, rmax=34, x0=40, x1=W - 40):
    rnd = random.Random(seed)
    items = sorted([(rnd.uniform(y0, y1), rnd.uniform(x0, x1)) for _ in range(n)])
    for y, x in items:
        t = (y - y0) / max(1, (y1 - y0))
        r = rmin + (rmax - rmin) * t
        col = rnd.choice(FCOLS)
        stem_flower(p, x, y + r * 2.4, r * 2.4, r, col, lean=rnd.uniform(-10, 10), petals=rnd.choice([5, 6, 6, 8]), rot=rnd.uniform(0, 6))


def f1_title():
    p = Paper()
    p.shape([(0, 0), (W, 0), (W, 760), (0, 760)], ("grad", (255, 168, 150), (255, 240, 208), 0, 720), shadow=0, hl=False)
    sun(p, 960, 690, 200, rays=26)
    for cx, cy, s in [(300, 250, 0.7), (1610, 200, 0.85), (1450, 470, 0.5), (470, 520, 0.42)]:
        small_cloud(p, cx, cy, s, CREAM if cy > 300 else (255, 236, 220))
    layers = [(690, 24, 11, LEAF1), (760, 34, 12, LEAF2), (835, 40, 13, LEAF3), (915, 44, 14, LEAF4), (995, 40, 15, LEAF5)]
    for i, (b, a, sd, c) in enumerate(layers):
        p.shape(hill_pts(b, a, sd), c, shadow=0.9)
        if i in (1, 2, 3):
            scatter_flowers(p, b + 20, b + 78, 7 + 3 * i, 30 + i, 12 + 4 * i, 20 + 6 * i)
    # title
    credits.opening_ribbon(p, 960, 84)
    p.text(966, 232, "Upping My", 118, CORAL, shadow=0.0, hl=False)
    p.text(960, 224, "Upping My", 118, INK)
    p.text(966, 428, "P(Bloom)", 258, CORAL, shadow=0.0, hl=False)
    p.text(960, 420, "P(Bloom)", 258, INK)
    p.tag(960, 610, "\u2014 An Answer", 60, fill=CORAL, ink=CREAM, rot=-0.02)
    wren(p, 640, 1040, 1.0, hands=[(600, 930), (678, 930)], held=("shovel", 1, -1.15), look=0.6)
    sprig(p, 850, 1046, 1.0, look=0.5, bloom=None, tilt=4)
    return p.finish()




def full(p, fill):
    p.shape([(0, 0), (W, 0), (W, H), (0, H)], fill, shadow=0, hl=False)


def dashed_rrect(p, x0, y0, x1, y1, col, w=8, dash=26, gap=18):
    def line(a, b):
        L = math.hypot(b[0] - a[0], b[1] - a[1]); n = int(L // (dash + gap)) + 1
        for i in range(n):
            t0 = i * (dash + gap) / L; t1 = min(1, (i * (dash + gap) + dash) / L)
            if t0 >= 1: break
            p.cap((a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1), w, col, shadow=0, hl=False)
    line((x0, y0), (x1, y0)); line((x1, y0), (x1, y1)); line((x1, y1), (x0, y1)); line((x0, y1), (x0, y0))


def f2_storm():
    p = Paper(NIGHT_T)
    full(p, ("grad", NIGHT_T, NIGHT_B, 0, 860))
    rnd = random.Random(4)
    for i in range(90):
        x, y = rnd.uniform(0, W), rnd.uniform(420, 930)
        p.cap((x, y), (x - 16, y + 50), 5, (160, 196, 240), shadow=0, hl=False, alpha=0.65)
    nimbus(p, 980, 300, 2.05, lightning=True)
    for b, c, sd in [(800, mix(LEAF5, NIGHT_T, .62), 21), (880, mix(LEAF5, NIGHT_T, .45), 22), (965, mix(LEAF5, NIGHT_T, .28), 23)]:
        p.shape(hill_pts(b, 30, sd), c, shadow=0.9)
    # closed bud
    stem_flower(p, 300, 1040, 120, 20, mix(PINK, NIGHT_T, .25), lean=6, petals=5)
    wren(p, 520, 1040, 1.2, hands=[(462, 905), (585, 895)], held=("shovel", 1, -1.35), look=-0.6, smile=-0.6)
    sprig(p, 745, 1046, 1.15, look=-0.6, happy=-0.7, tilt=-3)
    p.tag(1360, 992, "A forecast's a question, not \u201cThe End.\u201d", 46)
    credits.bug(p)   # corner tag lives 0:06-0:14 only; this frame is 0:08
    return p.finish()


def f3_chorus():
    p = Paper()
    full(p, ("grad", (255, 138, 112), (255, 214, 150), 0, 1080))
    for i in range(30):
        a0 = 2 * math.pi * i / 30; a1 = a0 + math.pi / 30
        tri = [(960, 640), (960 + 2200 * math.cos(a0), 640 + 2200 * math.sin(a0)), (960 + 2200 * math.cos(a1), 640 + 2200 * math.sin(a1))]
        p.shape(tri, (255, 236, 190), shadow=0, hl=False, alpha=0.22)
    # big paper leaves framing
    p.shape(leaf_pts(-80, 1120, 980, 400, -1.12), LEAF4, shadow=1.0)
    p.shape(leaf_pts(-40, 1140, 820, 300, -0.85), LEAF3, shadow=1.0)
    p.shape(leaf_pts(2000, 1120, 980, 400, -2.02), LEAF4, shadow=1.0)
    p.shape(leaf_pts(1960, 1140, 820, 300, -2.29), LEAF3, shadow=1.0)
    p.shape(hill_pts(985, 26, 40), LEAF3, shadow=1.0)
    p.shape(hill_pts(1035, 20, 41), LEAF5, shadow=1.0)
    rnd = random.Random(9)
    for x in [130, 250, 470, 640, 1290, 1470, 1690, 1790]:
        stem_flower(p, x, 1030 + rnd.uniform(-10, 10), rnd.uniform(160, 380), rnd.uniform(28, 46), rnd.choice(FCOLS), lean=rnd.uniform(-20, 20), petals=rnd.choice([5, 6, 8]), rot=rnd.uniform(0, 6))
    dial(p, 960, 640, 330, needle=0.86)
    for ang, r, col in [(-160, 60, PINK), (-125, 46, CORAL), (-55, 46, VIOLET), (-20, 62, PINK), (-178, 40, MARIGOLD), (-2, 40, CORAL)]:
        a = math.radians(ang)
        flower(p, 960 + math.cos(a) * 405, 640 + math.sin(a) * 405, r, col, SUN2, 6, ang / 30)
    p.text(966, 132, "I'm upping my P-BLOOM!", 116, CORAL, shadow=0.0, hl=False)
    p.text(960, 124, "I'm upping my P-BLOOM!", 116, INK)
    for i in range(70):
        x, y = rnd.uniform(60, W - 60), rnd.uniform(200, 900)
        p.shape(ell_pts(x, y, rnd.uniform(9, 16), rnd.uniform(5, 8), rnd.uniform(0, 3)), rnd.choice(FCOLS), shadow=0.4, sh_off=(1, 3), sh_blur=3)
    wren(p, 350, 1040, 1.3, hands=[(190, 660), (515, 660)], look=0.0, smile=1.6)
    sprig(p, 1600, 1046, 1.4, look=-0.3, happy=1.6, bloom=1.3)
    p.tag(960, 1012, "dig  \u00b7  plant  \u00b7  water  \u00b7  BLOOM", 44)
    return p.finish()


def f4_chair():
    p = Paper()
    full(p, ("grad", (26, 74, 92), (48, 112, 122), 0, 780))
    p.shape([(0, 770), (W, 770), (W, H), (0, H)], (196, 140, 96), shadow=0.0, hl=False)
    for y in (830, 900, 980):
        p.cap((0, y), (W, y), 4, (170, 116, 76), shadow=0, hl=False)
    p.shape([(850, 0), (1070, 0), (1420, 1010), (500, 1010)], (255, 238, 190), shadow=0, hl=False, alpha=0.20)
    # chair
    p.rrect(1118, 640, 1148, 800, 10, WOOD)
    p.rrect(1112, 792, 1262, 822, 10, mix(WOOD, (255, 255, 255), .12))
    p.rrect(1120, 776, 1256, 796, 10, CORAL)
    p.cap((1130, 820), (1124, 950), 16, WOOD); p.cap((1246, 820), (1252, 950), 16, WOOD)
    # button on pedestal
    p.rrect(1400, 690, 1520, 960, 20, (70, 62, 96))
    p.rrect(1360, 662, 1560, 704, 14, (110, 102, 138))
    p.ell(1460, 660, 100, 26, mix(RED, INK, .45))
    p.shape([(1372 + 0, 660)] + [(1460 + 88 * math.cos(math.radians(a)), 660 - 78 * math.sin(math.radians(a))) for a in range(0, 181, 6)][::-1], RED)
    p.ell(1430, 616, 26, 12, (255, 178, 170), rot=-0.5, shadow=0, hl=False)
    p.tag(1460, 800, "OFF", 40, ink=RED)
    wren(p, 640, 1040, 1.3, hands=[(575, 900), (700, 890)], held=("shovel", 1, -1.2), look=0.7)
    sprig(p, 900, 1046, 1.15, look=0.8, tilt=3)
    p.tag(960, 118, "Big red button.  Empty chair.", 62)
    p.tag(960, 236, "Well \u2014 somebody's gotta go sit there.", 56, fill=(255, 226, 150))
    return p.finish()


def _label(p, cx, y, s, size=29):
    for i, ln in enumerate(s.split("\n")):
        p.text(cx, y + i * (size + 5), ln, size, INK, shadow=0, hl=False)


def tile2(p, cx, cy, rot, w=390, h=330, fill=CREAM):
    p.shape(rot_pts(rrect_pts(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 34), cx, cy, rot), fill, shadow=1.0)


def f5_somebody():
    """Verse 3 roll call: six jobs (three guardrails, three gardens), then the empty tile that says 'you'."""
    p = Paper()
    full(p, ("grad", (58, 40, 92), (120, 84, 150), 0, 1080))
    rnd = random.Random(11)
    for i in range(50):
        p.ell(rnd.uniform(0, W), rnd.uniform(0, 1080), rnd.uniform(2, 5), rnd.uniform(2, 5), (255, 240, 210), shadow=0, hl=False, alpha=0.5)
    p.text(1016, 128, "Somebody's…", 122, CORAL, shadow=0.0, hl=False)
    p.text(1010, 120, "Somebody's…", 122, CREAM)
    xs, ys = [255, 680, 1105], [400, 780]
    labs = ["testing it\nbefore it flies", "teaching the kids\nto ask why", "writing the\nrules down right",
            "chasing a cure\nthrough the night", "telling the truth\nwhen it's hard", "watering the\nneighbor's yard"]
    rots = [-0.015, 0.012, -0.01, 0.014, -0.012, 0.01]
    for k in range(6):
        cx, cy = xs[k % 3], ys[k // 3]
        tile2(p, cx, cy, rots[k])
        _label(p, cx, cy + 104, labs[k])
    y0 = lambda k: ys[k // 3] - 34
    # 1 test clipboard
    cx, cy = xs[0], y0(0)
    p.rrect(cx - 70, cy - 90, cx + 70, cy + 68, 16, (235, 212, 176))
    p.rrect(cx - 30, cy - 104, cx + 30, cy - 78, 8, (150, 140, 170))
    for i in range(3):
        y = cy - 48 + i * 40
        if i < 2:
            p.cap((cx - 50, y), (cx - 41, y + 10), 8, LEAF4, shadow=0, hl=False); p.cap((cx - 41, y + 10), (cx - 24, y - 10), 8, LEAF4, shadow=0, hl=False)
        else:
            p.cap((cx - 50, y - 9), (cx - 28, y + 11), 8, RED, shadow=0, hl=False); p.cap((cx - 28, y - 9), (cx - 50, y + 11), 8, RED, shadow=0, hl=False)
        p.cap((cx - 6, y), (cx + 48, y), 8, (200, 178, 150), shadow=0, hl=False)
    # 2 teaching
    cx, cy = xs[1], y0(1)
    for dx, col in [(-70, CORAL), (2, TEAL)]:
        p.rrect(cx + dx - 32, cy + 20, cx + dx + 32, cy + 80, 18, col)
        p.ell(cx + dx, cy - 8, 30, 30, SKIN)
        p.ell(cx + dx - 10, cy - 10, 4, 5, INK, shadow=0, hl=False); p.ell(cx + dx + 10, cy - 10, 4, 5, INK, shadow=0, hl=False)
    p.shape(ell_pts(cx + 82, cy - 62, 72, 44), (255, 255, 255)); p.shape([(cx + 34, cy - 32), (cx + 56, cy - 22), (cx + 28, cy + 4)], (255, 255, 255), shadow=0, hl=False)
    p.text(cx + 82, cy - 62, "why?", 42, INK, shadow=0, hl=False)
    # 3 rules scroll
    cx, cy = xs[2], y0(2)
    p.rrect(cx - 84, cy - 76, cx + 84, cy + 68, 12, (250, 236, 208))
    for dx in (-84, 84):
        p.ell(cx + dx, cy - 4, 18, 76, (218, 190, 150))
    for i in range(4):
        p.cap((cx - 56, cy - 44 + i * 28), (cx + 16 - (i == 3) * 36, cy - 44 + i * 28), 8, (190, 168, 140), shadow=0, hl=False)
    p.ell(cx + 52, cy + 28, 28, 28, CORAL); p.cap((cx + 41, cy + 28), (cx + 49, cy + 37), 6, CREAM, shadow=0, hl=False); p.cap((cx + 49, cy + 37), (cx + 64, cy + 18), 6, CREAM, shadow=0, hl=False)
    # 4 cure through the night
    cx, cy = xs[0], y0(3)
    NIGHTW = (52, 40, 96)
    p.rrect(cx - 150, cy - 110, cx + 150, cy + 62, 22, NIGHTW, shadow=0)
    for sx, sy, sr in [(-110, -84, 3), (-40, -96, 2.5), (30, -76, 3), (70, -100, 2), (-80, -50, 2), (10, -50, 2.5)]:
        p.ell(cx + sx, cy + sy, sr, sr, CREAM, shadow=0, hl=False)
    p.ell(cx + 104, cy - 66, 24, 24, SUN2, shadow=0.3); p.ell(cx + 115, cy - 73, 20, 20, NIGHTW, shadow=0, hl=False)
    p.ell(cx + 6, cy - 4, 72, 72, (170, 255, 210), shadow=0, hl=False, alpha=0.22)
    p.rrect(cx - 150, cy + 36, cx + 150, cy + 62, 8, WOOD)
    p.rrect(cx - 14, cy - 54, cx + 14, cy - 16, 5, (214, 242, 238))
    p.shape([(cx - 14, cy - 18), (cx + 14, cy - 18), (cx + 52, cy + 36), (cx - 52, cy + 36)], (204, 238, 234), shadow=0.4)
    p.shape([(cx - 30, cy + 8), (cx + 30, cy + 8), (cx + 50, cy + 36), (cx - 50, cy + 36)], (120, 220, 170), shadow=0, hl=False)
    p.cap((cx, cy + 10), (cx, cy - 12), 5, LEAF4, shadow=0, hl=False)
    p.shape(leaf_pts(cx, cy - 10, 26, 9, -0.6), LEAF2, shadow=0, hl=False); p.shape(leaf_pts(cx, cy - 10, 26, 9, -2.5), LEAF3, shadow=0, hl=False)
    for bx, by_, br in [(-6, -34, 3.5), (8, -44, 2.5), (-2, -58, 3)]:
        p.ell(cx + bx, cy + by_, br, br, CREAM, shadow=0, hl=False, alpha=0.9)
    p.rrect(cx - 130, cy + 22, cx - 88, cy + 36, 5, (150, 140, 170))
    p.cap((cx - 108, cy + 24), (cx - 100, cy - 26), 9, (200, 190, 220), shadow=0.3)
    p.cap((cx - 94, cy - 38), (cx - 118, cy - 2), 15, (150, 140, 170), shadow=0.3)
    # 5 truth when it's hard
    cx, cy = xs[1], y0(4)
    p.shape(ell_pts(cx, cy - 14, 150, 74), (255, 255, 255))
    p.shape([(cx - 58, cy + 40), (cx - 98, cy + 84), (cx - 14, cy + 54)], (255, 255, 255), shadow=0, hl=False)
    p.text(cx, cy - 36, "I don't know…", 44, INK, shadow=0, hl=False)
    p.text(cx, cy + 8, "yet.", 46, CORAL, shadow=0, hl=False)
    # 6 neighbor's yard
    cx, cy = xs[2], y0(5)
    for i in range(5):
        x = cx - 4 + i * 30
        p.shape([(x - 11, cy + 82), (x - 11, cy - 26), (x, cy - 44), (x + 11, cy - 26), (x + 11, cy + 82)], (240, 226, 196))
    p.cap((cx - 24, cy + 4), (cx + 136, cy + 4), 6, (200, 184, 156), shadow=0, hl=False); p.cap((cx - 24, cy + 46), (cx + 136, cy + 46), 6, (200, 184, 156), shadow=0, hl=False)
    p.rrect(cx - 148, cy - 30, cx - 78, cy + 38, 18, TEAL)
    p.shape([(cx - 86, cy - 14), (cx - 24, cy - 64), (cx - 15, cy - 53), (cx - 80, cy + 4)], mix(TEAL, INK, .15))
    for i, (dx, dy) in enumerate([(-8, -44), (10, -22), (-4, 2), (16, 24)]):
        p.ell(cx - 16 + dx + i * 3, cy - 30 + dy + 36, 5, 8, SKY, shadow=0.3, sh_off=(1, 2), sh_blur=2)
    for x, r, c in [(cx + 40, 20, PINK), (cx + 96, 16, MARIGOLD)]:
        stem_flower(p, x, cy + 82, 62, r, c, petals=5)
    # the empty tile that says you
    fx0, fy0, fx1, fy1 = 1392, 235, 1860, 945
    p.rrect(fx0, fy0, fx1, fy1, 40, (255, 236, 200), shadow=0, hl=False, alpha=0.13)
    dashed_rrect(p, fx0 + 8, fy0 + 8, fx1 - 8, fy1 - 8, CORAL, 7)
    p.text(1626, 340, "somebody is…", 40, CREAM, shadow=0, hl=False)
    p.text(1632, 566, "you", 175, (255, 190, 175), shadow=0.0, hl=False)
    p.text(1626, 558, "you", 175, CORAL, shadow=0.0, hl=False)
    sprig(p, 1626, 1052, 0.95, look=-0.5, happy=1.5, tilt=3)
    return p.finish()


def f6_finale():
    p = Paper()
    full(p, ("grad", (48, 36, 98), (255, 178, 148), 0, 760))
    rnd = random.Random(21)
    for i in range(80):
        p.ell(rnd.uniform(0, W), rnd.uniform(0, 560), rnd.uniform(1.5, 4), rnd.uniform(1.5, 4), (255, 244, 220), shadow=0, hl=False, alpha=rnd.uniform(.4, .9))
    rc = [CORAL, MARIGOLD, SUN2, LEAF2, SKY, VIOLET]
    for i, c in enumerate(rc):
        p.shape(annular(960, 950, 520 + i * 25, 545 + i * 25, 180, 360, 60), c, shadow=0.2, hl=False, alpha=.9)
    R = 800
    p.ell(960, 1280, R, R, LEAF4, shadow=1.0)
    for i, (rr, c) in enumerate([(770, LEAF3), (730, LEAF2)]):
        p.ell(960, 1290, rr, rr, c, shadow=0.5)
    for i in range(17):
        a0 = 196 + i * 8.6; a1 = a0 + 7
        p.shape(annular(960, 1290, 668, 722, a0, a1, 8), [LEAF3, LEAF1, LEAF4][i % 3], shadow=0.15, hl=False, alpha=.75)
    def top(x):
        return 1280 - math.sqrt(max(0, R * R - (x - 960) ** 2))
    for x, r_ in [(700, 60), (1210, 70)]:
        yb = top(x) + 24
        p.shape([(x - r_ * 1.4, yb)] + [(x + r_ * 1.4 * math.cos(math.radians(a)), yb - r_ * 1.4 * math.sin(math.radians(a))) for a in range(180, -1, -8)][::-1], (206, 240, 240), shadow=0.6, alpha=.85)
        p.cap((x, yb), (x, yb - r_ * 1.4), 4, (150, 200, 205), shadow=0, hl=False)
    # windmill
    wx = 1440; wy = top(wx) + 20
    p.shape([(wx - 16, wy), (wx + 16, wy), (wx + 8, wy - 150), (wx - 8, wy - 150)], CREAM)
    for k in range(3):
        a = k * 2.094 + 0.5
        p.shape(leaf_pts(wx, wy - 150, 96, 22, a - 1.57), (255, 236, 200))
    p.ell(wx, wy - 150, 11, 11, CORAL)
    rnd = random.Random(2)
    for x in range(330, 1600, 62):
        if abs(x - 960) < 210: continue
        stem_flower(p, x + rnd.uniform(-14, 14), top(x) + 44, rnd.uniform(46, 96), rnd.uniform(15, 26), rnd.choice(FCOLS), lean=rnd.uniform(-8, 8), petals=rnd.choice([5, 6, 8]))
    for x in (560, 1320):
        yb = top(x) + 30
        p.cap((x, yb), (x, yb - 70), 9, WOOD); p.ell(x, yb - 100, 42, 44, LEAF2)
    nimbus(p, 250, 250, 1.0, col=(224, 216, 244), dark=(190, 180, 222), mood="happy")
    for i in range(26):
        x = 120 + rnd.uniform(0, 380); y = 400 + rnd.uniform(0, 280)
        p.cap((x, y), (x - 5, y + 22), 5, SKY, shadow=0, hl=False, alpha=.85)
    p.rrect(700, 920, 1180, 1030, 40, (146, 96, 64))
    p.rrect(724, 936, 1156, 1014, 30, (120, 76, 50), shadow=0, hl=False)
    dashed_rrect(p, 736, 946, 1144, 1004, CREAM, 5, 22, 16)
    p.cap((840, 944), (840, 800), 14, WOOD); p.rrect(640, 716, 1040, 846, 24, STRAW)
    p.text(840, 782, "YOUR TURN", 62, INK, shadow=0, hl=False)
    shovel(p, (1090, 770), 1.55, length=190, blade=(50, 66))
    p.text(966, 128, "Pass it on.", 122, CORAL, shadow=0.0, hl=False)
    p.text(960, 120, "Pass it on.", 122, CREAM)
    p.tag(960, 226, "the dial moves when we move", 46)
    sprig(p, 1400, 1054, 1.1, look=-0.6, happy=1.6, tilt=3)
    return p.finish()


def fit_lines(text, size, maxw, path=FRED):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if font(path, size * S).getlength(t) / S <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w_
    lines.append(cur)
    return lines


def f7_bridge():
    """Bridge: Sprig introduces itself. 'Hi -- I wrote this whole song. I'm Sonnet five-point-five.'"""
    p = Paper(NIGHT_T)
    full(p, ("grad", NIGHT_T, NIGHT_B, 0, 900))
    rnd = random.Random(31)
    for i in range(110):
        p.ell(rnd.uniform(0, W), rnd.uniform(0, 660), rnd.uniform(1.5, 4.2), rnd.uniform(1.5, 4.2), (255, 244, 220), shadow=0, hl=False, alpha=rnd.uniform(.35, .95))
    p.ell(1730, 190, 74, 74, (255, 240, 200), shadow=0.4)
    p.ell(1764, 168, 66, 66, mix(NIGHT_T, NIGHT_B, .19), shadow=0, hl=False)
    p.ell(960, 900, 1000, 210, (255, 170, 120), shadow=0, hl=False, alpha=0.22)      # dawn glow on the horizon
    for b, c, sd in [(800, mix(LEAF5, NIGHT_T, .62), 21), (880, mix(LEAF5, NIGHT_T, .45), 22), (965, mix(LEAF5, NIGHT_T, .28), 23)]:
        p.shape(hill_pts(b, 30, sd), c, shadow=0.9)
    # the code window ("read the code")
    p.rrect(150, 130, 690, 370, 26, (36, 28, 66))
    p.rrect(150, 130, 690, 172, 26, (60, 48, 98), shadow=0, hl=False)
    for i, c in enumerate([CORAL, MARIGOLD, LEAF2]):
        p.ell(184 + i * 30, 151, 8, 8, c, shadow=0, hl=False)
    for i, (c, wd, ind) in enumerate([(LEAF2, 120, 0), (SKY, 210, 34), (PINK, 160, 34), (SUN2, 240, 68), (LEAF2, 90, 34), (VIOLET, 190, 0)]):
        y = 204 + i * 25
        p.cap((190 + ind, y), (190 + ind + wd, y), 9, c, shadow=0, hl=False)
    p.tag(572, 372, "all tests pass", 34, fill=LEAF1, ink=LEAF5, padx=24, pady=10)
    # lamp
    p.cap((330, 1010), (330, 540), 14, (120, 92, 150))
    p.shape([(276, 528), (384, 528), (362, 484), (298, 484)], (120, 92, 150))
    p.shape([(312, 536), (348, 536), (580, 1012), (90, 1012)], (255, 240, 170), shadow=0, hl=False, alpha=0.26)
    p.ell(330, 536, 26, 14, (255, 244, 180), shadow=0.2)
    # thermos, Wren, Nimbus
    p.rrect(396, 872, 432, 940, 9, (206, 214, 232)); p.rrect(394, 858, 434, 878, 6, CORAL)
    wren(p, 330, 1040, 1.15, look=0.5, smile=1.2)
    nimbus(p, 650, 700, 0.42, col=(224, 216, 244), dark=(190, 180, 222), mood="happy")
    # Sprig, front and centre
    sprig(p, 1010, 1052, 1.75, look=0.0, happy=1.6, tilt=3)
    # plant-marker sign
    p.cap((1560, 1010), (1560, 690), 16, WOOD)
    p.rrect(1290, 470, 1830, 700, 26, (250, 236, 208))
    dashed_rrect(p, 1306, 486, 1814, 684, (200, 170, 130), 5, 18, 12)
    p.text(1560, 552, "Hi! I'm Sonnet 5.5.", 56, INK, shadow=0, hl=False)
    p.text(1560, 626, "Words, art & code: mine.", 39, CORAL, shadow=0, hl=False)
    p.tag(1560, 748, "check my work", 38, fill=(255, 226, 150), rot=-0.03)
    # brake lever
    p.rrect(1660, 972, 1800, 1010, 10, (110, 102, 138))
    p.cap((1730, 984), (1700, 890), 14, (200, 190, 220))
    p.ell(1696, 876, 24, 24, RED)
    p.tag(1730, 1046, "brake", 26, padx=20, pady=6)
    p.tag(960, 64, "Check my work.  Read the code.  Keep a hand on the brake.", 44)
    return p.finish()


def _icon(p, x, y, r, kind):
    k = r * 0.56
    p.ell(x, y, k, k, CREAM, shadow=0.3)
    q = k * 0.8
    if kind == "book":
        p.rrect(x - q * .70, y - q * .48, x - q * .04, y + q * .48, q * .1, DENIM, shadow=0, hl=False)
        p.rrect(x + q * .04, y - q * .48, x + q * .70, y + q * .48, q * .1, CORAL, shadow=0, hl=False)
    elif kind == "sun":
        for i in range(8):
            a = i * math.pi / 4
            p.cap((x + math.cos(a) * q * .55, y + math.sin(a) * q * .55), (x + math.cos(a) * q * .9, y + math.sin(a) * q * .9), q * .16, MARIGOLD, shadow=0, hl=False)
        p.ell(x, y, q * .42, q * .42, MARIGOLD, shadow=0, hl=False)
    elif kind == "plus":
        p.rrect(x - q * .17, y - q * .7, x + q * .17, y + q * .7, q * .06, LEAF3, shadow=0, hl=False)
        p.rrect(x - q * .7, y - q * .17, x + q * .7, y + q * .17, q * .06, LEAF3, shadow=0, hl=False)
    elif kind == "heart":
        p.ell(x - q * .27, y - q * .18, q * .34, q * .34, CORAL, shadow=0, hl=False)
        p.ell(x + q * .27, y - q * .18, q * .34, q * .34, CORAL, shadow=0, hl=False)
        p.shape([(x - q * .58, y - q * .02), (x + q * .58, y - q * .02), (x, y + q * .66)], CORAL, shadow=0, hl=False)
    elif kind == "leaf":
        p.shape(leaf_pts(x - q * .62, y + q * .42, q * 1.3, q * .42, -0.7), LEAF3, shadow=0, hl=False)
    elif kind == "note":
        p.ell(x - q * .24, y + q * .38, q * .34, q * .25, VIOLET, rot=-0.4, shadow=0, hl=False)
        p.cap((x - q * .02, y + q * .30), (x - q * .02, y - q * .62), q * .13, VIOLET, shadow=0, hl=False)
        p.shape([(x - q * .02, y - q * .62), (x + q * .42, y - q * .36), (x - q * .02, y - q * .22)], VIOLET, shadow=0, hl=False)
    elif kind == "bulb":
        p.ell(x, y - q * .14, q * .40, q * .44, SUN2, shadow=0, hl=False)
        p.rrect(x - q * .2, y + q * .26, x + q * .2, y + q * .58, q * .06, (150, 140, 170), shadow=0, hl=False)


def turbine(p, x, base, h, ang, col=CREAM):
    p.shape([(x - 5, base), (x + 5, base), (x + 2.5, base - h), (x - 2.5, base - h)], col, shadow=0.4)
    for k in range(3):
        p.shape(leaf_pts(x, base - h, h * 0.62, h * 0.09, ang + k * 2.094), col, shadow=0.3, sh_off=(1, 2), sh_blur=2)
    p.ell(x, base - h, 5, 5, CORAL, shadow=0, hl=False)


def house(p, x, base, w, h, wall, roofgreen=True):
    p.rrect(x - w / 2, base - h, x + w / 2, base, 6, wall, shadow=0.6)
    p.rrect(x - w / 2 - 4, base - h - 12, x + w / 2 + 4, base - h + 6, 6, LEAF2 if roofgreen else CORAL, shadow=0.5)
    for i in range(3):
        p.ell(x - w / 2 + 8 + i * (w - 16) / 2, base - h - 14, 6, 6, [PINK, MARIGOLD, CORAL][i], shadow=0, hl=False)
    p.rrect(x - 7, base - 26, x + 7, base, 3, mix(wall, INK, .3), shadow=0, hl=False)


def f8_trellis():
    """Final chorus: every bloom needs a trellis."""
    p = Paper()
    full(p, ("grad", (140, 206, 240), (255, 238, 205), 0, 780))
    for i, c in enumerate([CORAL, MARIGOLD, SUN2, LEAF2, SKY, VIOLET]):
        p.shape(annular(960, 930, 700 + i * 26, 726 + i * 26, 180, 360, 80), c, shadow=0.0, hl=False, alpha=.55)
    sun(p, 1640, 250, 80, rays=20)
    for cx, cy, s in [(330, 300, .62), (1240, 170, .48), (560, 520, .38), (1480, 560, .36)]:
        small_cloud(p, cx, cy, s, CREAM)
    p.shape(hill_pts(700, 22, 51), LEAF1, shadow=0.7)
    turbine(p, 250, 690, 150, 0.4); turbine(p, 420, 700, 110, 1.2); turbine(p, 1700, 700, 140, 0.9)
    p.shape(hill_pts(770, 26, 52), LEAF2, shadow=0.8)
    for x, w_, h_, c in [(140, 70, 60, (255, 226, 196)), (250, 60, 48, (255, 200, 190)), (1560, 72, 62, (255, 226, 196)), (1690, 60, 50, (250, 214, 230)), (1810, 66, 56, (255, 226, 196))]:
        house(p, x, 790, w_, h_, c)
    p.shape(hill_pts(850, 30, 53), LEAF3, shadow=0.9)
    p.shape(hill_pts(940, 20, 54), LEAF4, shadow=0.9)
    p.shape(hill_pts(1010, 16, 55), LEAF5, shadow=0.9)
    # trellis
    X0, X1, Y0, Y1 = 690, 1230, 300, 1010
    for cxl in (X0, X0 + 180, X0 + 360):
        for yy in range(Y0, Y1 - 1, 178):
            p.cap((cxl + 6, yy + 6), (cxl + 174, yy + 172), 8, (206, 156, 100), shadow=0.25, hl=False)
            p.cap((cxl + 174, yy + 6), (cxl + 6, yy + 172), 8, (206, 156, 100), shadow=0.25, hl=False)
    for yy in range(Y0, Y1 - 1, 178):
        p.rrect(X0 - 8, yy - 9, X1 + 8, yy + 9, 6, mix(WOOD, (255, 255, 255), .1), shadow=0.6)
    p.cap((X0, Y1), (X0, Y0 - 20), 26, WOOD)
    p.cap((X1, Y1), (X1, Y0 - 20), 26, WOOD)
    p.rrect(X0 - 34, Y0 - 48, X1 + 34, Y0 - 12, 14, WOOD)
    # two vines weaving up the lattice
    lr = random.Random(5)
    def vine(phase):
        pts = [(960 + 240 * math.sin(i / 60 * 9.4 + phase) * (0.55 + 0.45 * i / 60), 1010 - i / 60 * 700) for i in range(61)]
        for i in range(60):
            p.cap(pts[i], pts[i + 1], 13 - 4 * i / 60, mix(LEAF4, LEAF5, .3), shadow=0.35, hl=False)
        for i in range(2, 60, 2):
            x, y = pts[i]
            p.shape(leaf_pts(x, y, 54, 19, -0.9 if i % 4 == 0 else -2.3), lr.choice([LEAF2, LEAF3, LEAF1]), shadow=0.4, sh_off=(1, 2), sh_blur=2)
        return pts
    v1, v2 = vine(0.4), vine(0.4 + math.pi)
    kinds = ["book", "sun", "plus", "heart", "leaf", "note", "bulb"]
    fr = random.Random(8)
    j = 0
    for pts, start in ((v1, 8), (v2, 10)):
        for i in range(start, 60, 4):
            x, y = pts[i]
            r = 34 + 14 * (i / 60)
            flower(p, x, y, r, FCOLS[j % len(FCOLS)], SUN2, 6 if j % 2 else 8, fr.uniform(0, 6))
            _icon(p, x, y, r, kinds[j % len(kinds)])
            j += 1
    # signs nailed to the trellis
    for (tx, ty, s_, left) in [(505, 470, "tested", True), (505, 720, "written down", True), (1415, 470, "watched", False), (1415, 720, "honest", False)]:
        ax = X0 if left else X1
        p.cap((ax, ty), (tx + (110 if left else -110), ty), 5, (120, 92, 70), shadow=0, hl=False)
        p.tag(tx, ty, s_, 38, fill=(250, 236, 208), padx=26, pady=12, rot=-0.03 if left else 0.03)
    # people
    wren(p, 230, 1042, 1.25, hands=[(172, 898), (296, 892)], held=("shovel", 1, -1.25), look=0.6, smile=1.6)
    sprig(p, 1480, 1050, 1.3, look=-0.4, happy=1.7, bloom=1.0, tilt=3)
    for q in range(6):
        p.ell(1480 + 170 - 10 * q + 6 * (q % 2), 1050 - 170 + q * 26, 6, 9, SKY, shadow=0.2, sh_off=(1, 2), sh_blur=2)
    nimbus(p, 250, 250, 0.7, col=(224, 216, 244), dark=(190, 180, 222), mood="happy")
    for i in range(16):
        x = 130 + lr.uniform(0, 260); y = 380 + lr.uniform(0, 300)
        p.cap((x, y), (x - 4, y + 18), 5, SKY, shadow=0, hl=False, alpha=.85)
    p.text(966, 134, "Every bloom needs a trellis.", 92, CORAL, shadow=0.0, hl=False)
    p.text(960, 126, "Every bloom needs a trellis.", 92, INK)
    p.tag(960, 212, "rules hold up what we make", 40, fill=(255, 226, 150), pady=16)
    return p.finish()


def f9_endcard():
    T_ = credits.T
    p = Paper()
    full(p, ("grad", (48, 36, 98), (255, 178, 148), 0, 900))
    rnd = random.Random(41)
    for i in range(70):
        p.ell(rnd.uniform(0, W), rnd.uniform(0, 520), rnd.uniform(1.5, 4), rnd.uniform(1.5, 4), (255, 244, 220), shadow=0, hl=False, alpha=rnd.uniform(.4, .9))
    p.shape(hill_pts(930, 24, 61), LEAF3, shadow=0.9)
    p.shape(hill_pts(1005, 18, 62), LEAF5, shadow=0.9)
    scatter_flowers(p, 960, 1040, 12, 62, 18, 30, 40, 780)
    sprig(p, 400, 1052, 2.5, look=0.5, happy=1.8, bloom=1.3, tilt=3)
    # card
    p.rrect(780, 130, 1850, 930, 46, CREAM)
    p.text(1315, 226, "Made by", 62, VIOLET, shadow=0, hl=False)
    size = 116
    while font(FRED, size * S).getlength(T_["model"]) / S > 980:
        size -= 2
    p.text(1321, 350, T_["model"], size, PINK, shadow=0, hl=False)
    p.text(1315, 342, T_["model"], size, CORAL, shadow=0, hl=False)
    p.text(1315, 458, "in " + T_["platform"], 74, INK, shadow=0, hl=False)
    y = 566
    lines_all = list(T_["credit_lines"])
    if T_.get("director"):
        lines_all.insert(1, "Directed by " + T_["director"])
    for ln in lines_all:
        for sub in fit_lines(ln, 33, 940):
            p.text(1315, y, sub, 33, INK, shadow=0, hl=False); y += 44
        y += 20
    p.tag(1315, 870, "Your turn.  I saved you a shovel.", 44, fill=(255, 226, 150))
    return p.finish()


if __name__ == "__main__":
    which = sys.argv[1:] or ["f1"]
    fn = {"f1": f1_title, "f2": f2_storm, "f3": f3_chorus, "f4": f4_chair, "f5": f5_somebody, "f6": f6_finale, "f7": f7_bridge, "f8": f8_trellis, "f9": f9_endcard}
    for w in which:
        t0 = time.time()
        fn[w]().save(f"{OUT}/{w}.png")
        print(w, "%.1fs" % (time.time() - t0), flush=True)
