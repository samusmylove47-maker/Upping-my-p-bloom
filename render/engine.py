"""Video engine. Every frame is a pure function of song time, so any second can be re-rendered on its own.

    python3 render/engine.py still 44.0 92.0        -> out/s_044.00.png ...   (quick look at single moments)
    python3 render/engine.py clip 37.0 41.0 out/c.mp4  (a few seconds, silent)
    python3 render/engine.py full out/silent.mp4       (the whole video, silent; mux the song afterwards)

Set RENDER_W=1920 for the 1080p master (default is 1280 for review cuts).
"""
import json, math, os, sys, time, random, subprocess
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paper
paper.S = 1                       # animation renders at 1x internal; stills in frames.py use 2x
from paper import *               # noqa: E402,F401
import credits                    # noqa: E402

ROOT = os.path.join(HERE, "..")
OUTDIR = os.path.join(ROOT, "out")
os.makedirs(OUTDIR, exist_ok=True)

TM = json.load(open(os.path.join(ROOT, "timing.json")))
SONG = TM["song"]
BAR0, BAR, DUR = SONG["bar0_s"], SONG["bar_s"], SONG["duration"]
BEAT = BAR / 4
END_CARD = 6.0
TOTAL = DUR + END_CARD
FPS = 30
NF = int(round(TOTAL * FPS))
OW = int(os.environ.get("RENDER_W", 1280)); OH = OW * 9 // 16
SEC = {s["id"]: s for s in TM["sections"]}
FCOLS = [CORAL, PINK, MARIGOLD, VIOLET, CREAM, (255, 160, 122)]


# ------------------------------------------------------------------ small math
def clamp(x, a=0.0, b=1.0): return a if x < a else (b if x > b else x)
def lerp(a, b, u): return a + (b - a) * u
def eoc(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
def eob(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def eoe(x, a=3.2):
    """elastic-ish settle for pops"""
    x = clamp(x)
    return 1 - math.exp(-a * 3 * x) * math.cos(a * 6 * x) if x < 1 else 1.0
def seg_u(t, a, b): return clamp((t - a) / max(1e-6, b - a))


# ------------------------------------------------------------------ song clock
def bar_t(k): return BAR0 + BAR * k
def beat_t(n): return BAR0 + BEAT * n
def beat_of(t):
    """(global beat index, position inside the beat 0..1)"""
    nb = (t - BAR0) / BEAT
    k = math.floor(nb)
    return k, nb - k
def S0(sid): return SEC[sid]["start_s"]
def S1(sid): return SEC[sid]["end_s"]
def LT(sid, i): return SEC[sid]["lines"][i]["t"]
def sec_bar(sid, t):
    """(bar index inside the section starting at 0, position inside the bar 0..1)"""
    s = SEC[sid]; x = (t - bar_t(s["start_bar"])) / BAR
    return math.floor(x), x - math.floor(x)

LINES = sorted((l["t"], l["text"], s["id"], i) for s in TM["sections"] for i, l in enumerate(s["lines"]))


def line_at(t):
    cur = None
    for L_ in LINES:
        if L_[0] <= t + 0.03:
            cur = L_
    return cur


# ------------------------------------------------------------------ the dial (a prop, not a probability)
def _hits():
    h = [(0.0, 0.08), (19.9, 0.12), (24.6, 0.16), (35.44, 0.20), (35.80, 0.24), (36.16, 0.28)]
    for k in range(8): h.append((bar_t(20 + k) + 0.36, 0.30 + 0.0286 * k))
    for j, tt in enumerate([55.2, 59.0, 62.6, 66.3]): h.append((tt, 0.54 + 0.02 * j))
    h += [(75.2, 0.62), (75.8, 0.64), (76.4, 0.66)]
    for k in range(8): h.append((bar_t(42 + k) + 0.36, 0.68 + 0.017 * k))
    for j, i in enumerate(range(6)): h.append((SEC["verse3"]["lines"][i]["t"] + 1.5, 0.81 + 0.008 * j))
    for k in range(12): h.append((bar_t(78 + k) + 0.36, 0.86 + 0.0075 * k))
    return sorted(h)
HITS = _hits()


def dial_value(t):
    lt = None; prev = cur = HITS[0][1]
    for (tt, v) in HITS:
        if t >= tt:
            prev, cur, lt = cur, v, tt
        else:
            break
    if lt is None:
        return HITS[0][1] + 0.006 * math.sin(t * 9)
    return prev + (cur - prev) * eob((t - lt) / 0.55) + 0.004 * math.sin(t * 27)


def draw_needle(p, cx, cy, r, v):
    ang = math.radians(180 + 180 * v)
    tip = (cx + r * 0.84 * math.cos(ang), cy + r * 0.84 * math.sin(ang))
    b1 = (cx + r * 0.06 * math.cos(ang + 1.57), cy + r * 0.06 * math.sin(ang + 1.57))
    b2 = (cx + r * 0.06 * math.cos(ang - 1.57), cy + r * 0.06 * math.sin(ang - 1.57))
    p.shape([b1, tip, b2], CORAL, shadow=0.8)
    p.ell(cx, cy, r * 0.11, r * 0.11, INK, shadow=0.6)
    p.ell(cx, cy, r * 0.045, r * 0.045, CREAM, shadow=0, hl=False)


# ------------------------------------------------------------------ text
def cap_text(s):
    """The caption for a lyric line: gang shouts in (parentheses) are shown separately, not in the caption."""
    import re
    main = re.sub(r"\s*\([^)]*\)", "", s).strip()
    if not main:
        main = re.sub(r"[()]", "", s).strip()
    main = main.replace("P-bloom", "P-BLOOM").replace("Sonnet five-point-five", "Sonnet 5.5")
    return main


def fit_size(txt, maxw, size, path=FRED, lo=40):
    while font(path, size * paper.S).getlength(txt) / paper.S > maxw and size > lo:
        size -= 2
    return size


def caption(p, t, y=124, fill=INK, shade=CORAL, maxw=1700, size=104, line=None, pulse_amp=0.10):
    """Big cut-out caption at the top, pops on each new line."""
    L_ = line or line_at(t)
    if not L_:
        return
    t0, raw = L_[0], L_[1]
    txt = cap_text(raw)
    if not txt:
        return
    s = fit_size(txt, maxw, size)
    age = t - t0
    if age < 0:
        return
    pop = 1 + pulse_amp * (1 - min(1, age * 6)) ** 3
    s = int(s * pop)
    p.text(966, y + 8, txt, s, shade, shadow=0.0, hl=False)
    p.text(960, y, txt, s, fill)


def word_tag(p, cx, cy, s, size, t, t0, life=0.5, fill=CREAM, ink=INK, rot=0.0):
    """A shout that pops in at t0 and stays for `life` seconds."""
    u = (t - t0) / 0.14
    if t < t0 or t > t0 + life:
        return
    sz = int(size * eob(u) * (1 + 0.25 * (1 - min(1, (t - t0) * 5)) ** 2))
    if sz < 8:
        return
    p.tag(cx, cy, s, sz, fill=fill, ink=ink, rot=rot)


# ------------------------------------------------------------------ camera and overlays
def cam_pulse(t, amp=0.016, down=0.010):
    k, u = beat_of(t)
    if t < BAR0 or t >= DUR:
        return 1.0
    z = 1 + amp * (1 - u) ** 2
    if k % 4 == 0:
        z += down * (1 - u) ** 2
    return z


def apply_cam(img, z, cx=960, cy=560):
    if z <= 1.0004:
        return img
    w, h = W / z, H / z
    x0 = clamp(cx - w / 2, 0, W - w); y0 = clamp(cy - h / 2, 0, H - h)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))


def blend_overlay(p, fn, a):
    """Draw fn(p) then mix it in at opacity a (for fades of shaded tags)."""
    if a <= 0.01:
        return
    if a >= 0.99:
        fn(p); return
    base = p.img.copy(); fn(p); p.img = Image.blend(base, p.img, a)


def wipe(p, u, color=CORAL, back=CREAM, seed=0):
    """Paper-page wipe left->right. Fully covers the screen around u=0.5."""
    if u <= 0 or u >= 1:
        return
    span = 2700
    xf = lerp(-150, W + span + 150, u)
    def band(xr, w_, col, ph):
        pts = [(xr - w_, -60)] + [(xr + 70 * math.sin(y * 0.012 + ph) + 30 * math.sin(y * 0.031 + 2 * ph), y) for y in range(-60, H + 61, 40)] + [(xr - w_, H + 60)]
        p.shape(pts, col, shadow=1.0)
    band(xf - 120, span, back, seed + 1.3)
    band(xf, span, color, seed)


# ------------------------------------------------------------------ scene base
class Scene:
    id = ""; t0 = 0.0; t1 = 0.0
    _ready = False
    plate = None
    cam_amp = 0.016
    cap = dict(fill=INK, shade=CORAL, y=124)

    def setup(self): pass

    def ensure(self):
        if not self._ready:
            self.setup(); self._ready = True

    def paper(self, t=0.0):
        p = Paper()
        if self.plate is not None:
            p.img = Image.fromarray(self.plate)
        return p

    def draw(self, p, t): pass
    def cam(self, t): return (cam_pulse(t, self.cam_amp), 960, 560)


def render_plate(fn, bg=CREAM):
    p = Paper(bg); fn(p)
    return np.asarray(p.img).copy()


def plate_pt(fn):
    """Static layer with holes: returns (P, T). A frame is P + T * background (T = how much background shows through)."""
    outs = []
    for bgc in [(0, 0, 0), (255, 255, 255)]:
        p = Paper(bgc); fn(p); outs.append(np.asarray(p.img).astype(np.float32))
    T_ = np.clip((outs[1] - outs[0]).mean(axis=2) / 255.0, 0, 1)[..., None]
    return outs[0], T_


REG = []   # ordered scenes, filled by scenes.py


def scene_at(t):
    cur = REG[0]
    for s in REG:
        if t >= s.t0: cur = s
    return cur


_NOISE = {}


def post(img, t):
    """resize, paper grain, vignette, global fades"""
    if (OW, OH) != (W, H):
        img = img.resize((OW, OH), Image.LANCZOS)
    a = np.asarray(img).astype(np.float32)
    if "n" not in _NOISE:
        rng = np.random.default_rng(5)
        _NOISE["n"] = rng.normal(0, 2.6, (OH + 64, OW + 64, 1)).astype(np.float32)
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
        r2 = ((xx / OW - 0.5) * 1.6) ** 2 + ((yy / OH - 0.5) * 1.0) ** 2
        _NOISE["v"] = (1 - 0.20 * r2)[..., None]
    oy, ox = int(t * 977) % 64, int(t * 613) % 64
    a = (a + _NOISE["n"][oy:oy + OH, ox:ox + OW]) * _NOISE["v"]
    fade = clamp(t / 0.5) * clamp((TOTAL - t) / 0.9)
    return (np.clip(a, 0, 255) * fade).astype(np.uint8)


def wipe_state(t):
    """(u, scene_to_draw) around scene boundaries; the switch happens at u=0.5."""
    HALF = 0.22
    for i, s in enumerate(REG[1:], 1):
        if s.t0 - HALF <= t <= s.t0 + HALF and getattr(s, "wipe", True):
            u = (t - (s.t0 - HALF)) / (2 * HALF)
            return u, (REG[i - 1] if u < 0.5 else s), s
    return None, scene_at(t), None


def render(i):
    t = i / FPS
    u, sc, wsc = wipe_state(t)
    sc.ensure()
    tt = min(t, sc.t1 + 0.3) if sc is not scene_at(t) else t
    p = sc.paper(tt)
    sc.draw(p, tt)
    z, cx, cy = sc.cam(tt)
    p.img = apply_cam(p.img, z, cx, cy)
    # credits (drawn after the camera so they never shake)
    if t < 6.6:
        a = clamp(min((t - 0.35) / 0.6, (6.4 - t) / 0.6))
        blend_overlay(p, lambda q: credits.opening_ribbon(q, 960, 1000), a)
    ba = credits.bug_alpha(t)
    if ba > 0:
        blend_overlay(p, lambda q: credits.bug(q, 36, 24), ba)
    if u is not None:
        col = getattr(wsc, "wipe_color", CORAL)
        wipe(p, u, col, CREAM, seed=wsc.t0)
    return post(p.img, t)
