"""Shared building blocks for the scenes: cached cut-out sprites, sky gradients, weather, bubbles, small props.

A Sprite is a piece of paper art rendered ONCE (over black and over white, so its soft shadows survive) and then
pasted cheaply every frame at any scale / rotation / opacity. That is what keeps a 3-minute video renderable.
"""
from engine import *
import frames as F            # the still compositions double as a parts bin (tile2, dashed_rrect, turbine, house, _icon ...)


# ------------------------------------------------------------------ gradients and stage
def grad(top, bot, y0=0, y1=H):
    ys = np.clip((np.arange(H, dtype=np.float32) - y0) / max(1, y1 - y0), 0, 1)[:, None, None]
    g = np.array(top, np.float32) * (1 - ys) + np.array(bot, np.float32) * ys
    return np.repeat(g, W, axis=1)


def mixc(a, b, u):
    return tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


class Sprite:
    """fn(p) draws on a full-size Paper; box = (x0,y0,x1,y1) crop. blit() pastes it anywhere, scaled/rotated about a pivot."""
    def __init__(self, fn, box):
        x0, y0, x1, y1 = [int(round(v)) for v in box]
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        box = (x0, y0, x1, y1)
        P, T = plate_pt(fn)
        P, T = P[y0:y1, x0:x1], T[y0:y1, x0:x1]
        a = 1 - T
        col = np.where(a > 0.004, P / np.maximum(a, 0.004), 0)
        self.im = Image.fromarray(np.concatenate([np.clip(col, 0, 255), a * 255], axis=2).astype(np.uint8), "RGBA")
        self.box = box

    def blit(self, img, dx=0.0, dy=0.0, s=1.0, rot=0.0, alpha=1.0, pivot=None, sx=None, sy=None):
        """pivot (absolute coords of the original) is the point that scales/rotates in place; dx,dy shift it."""
        x0, y0, x1, y1 = self.box
        px, py = pivot if pivot is not None else ((x0 + x1) / 2, (y0 + y1) / 2)
        sx = s if sx is None else sx; sy = s if sy is None else sy
        if sx <= 0.01 or sy <= 0.01 or alpha <= 0.01:
            return
        im = self.im
        if alpha < 0.99:
            a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
        w, h = im.size
        if abs(sx - 1) > 0.002 or abs(sy - 1) > 0.002:
            im = im.resize((max(1, int(w * sx)), max(1, int(h * sy))), Image.BICUBIC)
        ox, oy = (px - x0) * sx, (py - y0) * sy
        if abs(rot) > 0.001:
            w2, h2 = im.size
            R = int(math.hypot(max(ox, w2 - ox), max(oy, h2 - oy))) + 2
            pad = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
            pad.paste(im, (int(R - ox), int(R - oy)))
            im = pad.rotate(-math.degrees(rot), Image.BICUBIC)
            ox, oy = R, R
        img.paste(im, (int(round(px + dx - ox)), int(round(py + dy - oy))), im)


# ------------------------------------------------------------------ weather and sky details
def rain(img, t, x0, x1, y0, y1, n=110, col=(150, 190, 236), seed=3, slant=0.32, speed=900, ln=46, w=3):
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for i in range(n):
        bx = rnd.uniform(x0, x1); by = rnd.uniform(0, 1); sp = rnd.uniform(0.8, 1.25)
        y = y0 + ((by * (y1 - y0) + t * speed * sp) % (y1 - y0))
        x = bx - (y - y0) * slant
        d.line([(x, y), (x - ln * slant, y + ln)], fill=col, width=w)


def stars(img, t, n=90, ymax=600, seed=4, col=(255, 244, 220)):
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for i in range(n):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, ymax), rnd.uniform(1.4, 3.6)
        tw = 0.6 + 0.4 * math.sin(t * rnd.uniform(1.5, 4) + i)
        r *= tw
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)


def flash(img, a, col=(255, 250, 235)):
    if a > 0.01:
        img.paste(Image.new("RGB", img.size, col), (0, 0), Image.new("L", img.size, int(255 * clamp(a))))


def bolt_pts(x0, y0, x1, y1, seed=1, n=7, jag=46):
    rnd = random.Random(seed)
    pts = [(x0, y0)]
    for i in range(1, n):
        u = i / n
        pts.append((x0 + (x1 - x0) * u + rnd.uniform(-jag, jag), y0 + (y1 - y0) * u))
    pts.append((x1, y1))
    return pts


def draw_bolt(p, x0, y0, x1, y1, seed=1, w=16):
    pts = bolt_pts(x0, y0, x1, y1, seed)
    d = ImageDraw.Draw(p.img)
    d.line(pts, fill=(255, 248, 200), width=w + 8, joint="curve")
    d.line(pts, fill=(255, 214, 90), width=w, joint="curve")
    d.line(pts, fill=(255, 255, 240), width=max(3, w // 3), joint="curve")


# ------------------------------------------------------------------ small pieces used by several scenes
def hills_static(p, layers, seed0=21):
    """layers: [(base_y, amp, colour), ...] back to front"""
    for i, (b, a, c) in enumerate(layers):
        p.shape(hill_pts(b, a, seed0 + i), c, shadow=0.9)


def bubble(p, cx, cy, s, size=40, fill=(255, 255, 255), ink=INK, tail=(-1, 1), rot=0.0):
    """Speech bubble with a tail pointing down-left (tail=(-1,1)) or down-right."""
    f = font(FRED, size * paper.S)
    w = f.getlength(s) / paper.S + 60; h = size * 1.05 + 36
    pts = ell_pts(cx, cy, w / 2 + 12, h / 2 + 8, 0, n=60, jit=0)
    if rot:
        pts = rot_pts(pts, cx, cy, rot)
    p.shape(pts, fill)
    tx = cx + tail[0] * w * 0.22
    p.shape([(tx - 20, cy + h / 2 - 6), (tx + 22, cy + h / 2 - 6), (tx + tail[0] * 30, cy + h / 2 + 34)], fill, shadow=0, hl=False)
    p.text(cx, cy + 2, s, size, ink, shadow=0, hl=False)


def pop_scale(t, t0, dur=0.22):
    """0 before t0, overshoots to ~1.1, settles at 1"""
    return eob((t - t0) / dur) if t >= t0 else 0.0


def bounce(t, amp=10, f=2.0, ph=0.0):
    return -amp * abs(math.sin(math.pi * f * t + ph))


def sweat(p, x, y, s=1.0):
    p.shape(ell_pts(x, y, 9 * s, 13 * s, 0, n=20, jit=0), SKY, shadow=0.3, sh_off=(1, 2), sh_blur=2)
    p.shape([(x - 7 * s, y - 6 * s), (x + 7 * s, y - 6 * s), (x, y - 26 * s)], SKY, shadow=0, hl=False)


def mini_dial_static(p, cx, cy, r):
    dial(p, cx, cy, r, needle=None, label=False)


def blink_at(t, times, dur=0.13):
    return any(a <= t < a + dur for a in times)


def curve(p, pts, w, col, **kw):
    for i in range(len(pts) - 1):
        p.cap(pts[i], pts[i + 1], w, col, **kw)


def arrow(p, x0, y0, x1, y1, w=16, col=CORAL, head=42):
    a = math.atan2(y1 - y0, x1 - x0)
    bx, by = x1 - math.cos(a) * head * 0.8, y1 - math.sin(a) * head * 0.8
    p.cap((x0, y0), (bx, by), w, col, shadow=0.6)
    p.shape([(x1, y1), (bx + math.cos(a + 1.57) * head * 0.7, by + math.sin(a + 1.57) * head * 0.7),
             (bx + math.cos(a - 1.57) * head * 0.7, by + math.sin(a - 1.57) * head * 0.7)], col, shadow=0.6)


def wren_row(p, t, t0, xs, by, s, cols, poser):
    for x, c in zip(xs, cols):
        poser(p, t, t0, x, by, s, **c)


# ------------------------------------------------------------------ scene skeleton with a static foreground plate
class Stage(Scene):
    """Static foreground (hills, ground, props) is rendered once into a plate; the sky/backdrop is redrawn per frame BEHIND it.
    static(p)      -> draws the foreground plate
    backdrop(t, q) -> draws the sky on q (a Paper whose image is already the base gradient from base(t))
    """
    def static(self, p): pass
    def base(self, t): return grad(CREAM, CREAM)
    def backdrop(self, t, q): pass
    def prep(self): pass

    def setup(self):
        self.P, self.T = plate_pt(self.static)
        self.prep()

    def paper(self, t=0.0):
        q = Paper(); q.img = to_img(self.base(t))
        self.backdrop(t, q)
        bg = np.asarray(q.img, np.float32)
        p = Paper(); p.img = to_img(self.P + self.T * bg)
        return p


class HudDial:
    """The small Bloom-o-meter that sits in a corner of the verse scenes and ticks up as things get done."""
    def __init__(self, cx, cy, r):
        self.c = (cx, cy, r)
        box = (int(cx - r * 1.2), int(cy - r * 1.2), min(W, int(cx + r * 1.2)), min(H, int(cy + r * 1.1)))
        self.spr = Sprite(lambda p: dial(p, cx, cy, r, needle=None, label=False), box)

    def draw(self, p, t, tin):
        cx, cy, r = self.c
        s = pop_scale(t, tin, 0.35)
        if s <= 0:
            return
        self.spr.blit(p.img, s=s, pivot=(cx, cy))
        if s > 0.92:
            draw_needle(p, cx, cy, r, dial_value(t))


def star4(p, x, y, r, rot=0.0, col=SUN2, shadow=0.0):
    pts = []
    for i in range(8):
        a = rot + i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    p.shape(pts, col, shadow=shadow, hl=False)


def dirt_puff(p, x, y, dt, seed=0, n=7, col=(126, 88, 62)):
    """little brown crumbs thrown up at a shovel stab; dt = seconds since the stab"""
    if dt < 0 or dt > 0.5:
        return
    rnd = random.Random(seed)
    d = ImageDraw.Draw(p.img)
    for i in range(n):
        a = rnd.uniform(-2.5, -0.6); sp = rnd.uniform(160, 330)
        px = x + math.cos(a) * sp * dt; py = y + math.sin(a) * sp * dt + 0.5 * 1300 * dt * dt
        r = rnd.uniform(5, 10) * (1 - dt / 0.6)
        d.ellipse([px - r, py - r, px + r, py + r], fill=col)


def dig_hands(cx, by, s, down):
    """Wren digging: down 0 (shovel raised) .. 1 (blade in the ground). Returns hands, shovel angle, blade-tip position."""
    R = (cx + (50 + 26 * down) * s, by + (-215 + 70 * down) * s)
    ang = -0.95 + 1.75 * down
    L = (R[0] + 0.30 * 205 * s * math.cos(ang), R[1] + 0.30 * 205 * s * math.sin(ang))
    tip = (R[0] + 300 * s * math.cos(ang), R[1] + 300 * s * math.sin(ang))
    return [L, R], ang, tip


def sprout(p, x, by, g, bloom=0.0, col=PINK):
    """a seedling that grows (g 0..1) and can open into a flower (bloom 0..1)"""
    if g <= 0.02:
        return
    h = 120 * g
    p.cap((x, by), (x + 4 * g, by - h), 9, LEAF4, shadow=0.4, hl=False)
    p.shape(leaf_pts(x + 2, by - h * 0.55, 62 * g, 21 * g, -0.45), LEAF2, shadow=0.4, sh_off=(1, 2), sh_blur=2)
    p.shape(leaf_pts(x + 2, by - h * 0.55, 62 * g, 21 * g, -2.7), LEAF3, shadow=0.4, sh_off=(1, 2), sh_blur=2)
    if bloom > 0.02:
        flower(p, x + 4 * g, by - h - 6, 42 * bloom, col, SUN2, 6, 0.3)
    else:
        p.ell(x + 4 * g, by - h - 6, 9 * g, 12 * g, mix(col, INK, .1), shadow=0.4)


def text_img(s, size, col, path=FRED):
    """RGBA image of a piece of text (for things that must rotate with a prop)"""
    f = font(path, size)
    bb = f.getbbox(s)
    im = Image.new("RGBA", (bb[2] - bb[0] + 8, bb[3] - bb[1] + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - bb[0], 4 - bb[1]), s, font=f, fill=tuple(col) + (255,))
    return im


def paste_rot(img, im, cx, cy, rot=0.0, s=1.0):
    if s != 1.0:
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    if abs(rot) > 0.001:
        im = im.rotate(-math.degrees(rot), Image.BICUBIC, expand=True)
    img.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)


def gear(p, x, y, r, rot=0.0, col=(170, 180, 200), teeth=8):
    pts = []
    for i in range(teeth * 4):
        a = rot + i * 2 * math.pi / (teeth * 4)
        rr = r if (i // 2) % 2 == 0 else r * 0.78
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    p.shape(pts, col, shadow=0.4, sh_off=(1, 2), sh_blur=2)
    p.ell(x, y, r * 0.32, r * 0.32, mix(col, INK, .5), shadow=0, hl=False)


def push_transition(old, new, u):
    """new Paper slides in from the right over old (which drifts left)"""
    e = eio(u)
    base = Image.new("RGB", (W, H), (30, 20, 50))
    base.paste(old.img, (int(-0.28 * W * e), 0))
    sh = Image.new("L", (60, H), 0)
    x = int(W * (1 - e))
    base.paste(new.img, (x, 0))
    return base


def burst(img, t, tb, seed=1, n=60, cx=960, cy=560, spread=(-2.6, -0.5), sp=(420, 1100), grav=1500, life=1.7, cols=None):
    """confetti thrown up at time tb"""
    dt = t - tb
    if dt < 0 or dt > life:
        return
    cols = cols or FCOLS
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    for i in range(n):
        ang = rnd.uniform(*spread); v = rnd.uniform(*sp)
        x = cx + rnd.uniform(-160, 160) + math.cos(ang) * v * dt
        y = cy + math.sin(ang) * v * dt + 0.5 * grav * dt * dt
        col = rnd.choice(cols); r = rnd.uniform(6, 12) * (1 - dt / (life + 0.2)); rot = rnd.uniform(0, 3) + dt * rnd.uniform(-8, 8)
        if r <= 1 or y > 1100:
            continue
        d.polygon(ell_pts(x, y, r, r * 0.55, rot, n=10, jit=0), fill=col)
