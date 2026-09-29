"""Timing animatic: the approved style frames cut to the MEASURED song timing, with an info strip.

It exists so a human can check the map by ear and eye: does the lyric line change when the singer starts it,
does the beat counter tick on the beat, does each section change when the music does.

Usage (from the repo root):
    python3 render/timing_animatic.py out/timing_silent.mp4 [--from 0 --to 180]
    ffmpeg ... mux with the song (see README)
"""
import json, math, os, sys, subprocess, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from paper import FRED      # noqa: E402  (font path)

TM = json.load(open(os.path.join(ROOT, "timing.json")))
TH = json.load(open(os.path.join(ROOT, "theme.json")))
SONG = TM["song"]; SECS = TM["sections"]
BAR0, BAR = SONG["bar0_s"], SONG["bar_s"]; BEAT = BAR / 4
DUR = SONG["duration"]; END = 6.0; TOTAL = DUR + END
FPS = 30
PW, PH, SH = 1280, 720, 104          # picture and strip height
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
INK, CREAM, CORAL = (52, 34, 74), (255, 246, 229), (255, 107, 90)
KIND = dict(intro=(142, 201, 240), verse1=(183, 163, 230), pre1=(255, 192, 77), chorus1=(255, 138, 120), verse2=(183, 163, 230),
            pre2=(255, 192, 77), chorus2=(255, 138, 120), dance=(142, 201, 240), verse3=(183, 163, 230), bridge=(125, 211, 168),
            final=(255, 138, 120), outro=(142, 201, 240))
FRAME_OF = dict(intro="f1", verse1="f2", pre1="f2", chorus1="f3", verse2="f4", pre2="f4", chorus2="f3", dance="poses",
                verse3="f5", bridge="f7", final="f8", outro="f6")
LABEL = dict(intro="INTRO", verse1="VERSE 1", pre1="PRE-CHORUS", chorus1="CHORUS", verse2="VERSE 2", pre2="PRE-CHORUS", chorus2="CHORUS",
             dance="DANCE BREAK", verse3="VERSE 3", bridge="BRIDGE", final="FINAL CHORUS", outro="OUTRO")

_F = {}


def load():
    if _F:
        return
    d = os.path.join(ROOT, "docs", "frames")
    for n in ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9"]:
        _F[n] = Image.open(os.path.join(d, n + ".jpg")).convert("RGB").resize((PW, PH), Image.LANCZOS)
    po = Image.open(os.path.join(d, "poses.jpg")).convert("RGB")
    bg = Image.new("RGB", (PW, PH), (255, 236, 200))
    s = min(PW * 0.96 / po.width, PH * 0.9 / po.height)
    po = po.resize((int(po.width * s), int(po.height * s)), Image.LANCZOS)
    bg.paste(po, ((PW - po.width) // 2, (PH - po.height) // 2))
    _F["poses"] = bg
    _F["f9"] = _F["f9"]
    _F["fonts"] = dict(cap=lambda s: ImageFont.truetype(FRED, s), mono=lambda s: ImageFont.truetype(MONO, s))
    flat = []
    for s in SECS:
        for li, l in enumerate(s["lines"]):
            flat.append((l["t"], l["text"], s["id"], li))
    flat.sort()
    _F["lines"] = flat


def sec_at(t):
    cur = SECS[0]
    for s in SECS:
        if t >= s["start_s"]:
            cur = s
    return cur


def frame_for(t):
    if t >= DUR:
        return _F["f9"], None
    s = sec_at(t)
    img = _F[FRAME_OF[s["id"]]]
    # short dissolve from the previous section's picture
    dt = t - s["start_s"]
    if 0 <= dt < 0.25 and s["id"] != "intro":
        prev = SECS[[x["id"] for x in SECS].index(s["id"]) - 1]
        pimg = _F[FRAME_OF[prev["id"]]]
        if pimg is not img:
            img = Image.blend(pimg, img, dt / 0.25)
    return img, s


def render(i):
    load()
    t = i / FPS
    img, s = frame_for(t)
    # beat pulse (camera push)
    nb = (t - BAR0) / BEAT
    k = math.floor(nb); u = nb - k
    z = 1 + (0.012 * (1 - u) ** 2 if (t >= BAR0 and t < DUR) else 0) + (0.010 * (1 - u) ** 2 if (k % 4 == 0 and t >= BAR0 and t < DUR) else 0)
    w, h = PW / z, PH / z
    x0, y0 = (PW - w) / 2, (PH - h) / 2
    pic = img.resize((PW, PH), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h)) if z > 1.0005 else img.copy()
    # corner credit tag window, as the final video will show it
    w0, w1 = TH.get("credit_bug_window", [6, 14]); fd = TH.get("credit_bug_fade", 0.5)
    a = max(0.0, min(1.0, (t - w0) / fd, (w1 - t) / fd))
    if a > 0.01 and t < DUR:
        ov = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        f = _F["fonts"]["cap"](22); txt = TH["credit_bug"]; tw = f.getlength(txt)
        d.rounded_rectangle((26, 22, 26 + tw + 36, 22 + 44), 22, fill=(255, 246, 229, int(230 * a)))
        d.text((44, 44), txt, font=f, fill=(52, 34, 74, int(255 * a)), anchor="lm")
        pic = Image.alpha_composite(pic.convert("RGBA"), ov).convert("RGB")
    # canvas with strip
    can = Image.new("RGB", (PW, PH + SH), INK)
    can.paste(pic, (0, 0))
    d = ImageDraw.Draw(can)
    mono = _F["fonts"]["mono"]
    if t < DUR:
        sid = s["id"]; col = KIND[sid]
        bar_i = int((t - s["start_s"]) / BAR) + 1 if s["start_bar"] is not None else None
        nbars = int(round(s["bars"])) if s["bars"] else None
        lab = LABEL[sid] + (f"  bar {bar_i}/{nbars}" if bar_i and nbars else "")
        d.rounded_rectangle((16, PH + 10, 16 + mono(17).getlength(lab) + 24, PH + 36), 13, fill=col)
        d.text((28, PH + 23), lab, font=mono(17), fill=INK, anchor="lm")
        mm = int(t // 60); ss = t - 60 * mm
        d.text((PW - 250, PH + 23), f"{mm}:{ss:04.1f}", font=mono(20), fill=CREAM, anchor="rm")
        # beat dots
        if t >= BAR0:
            for q in range(4):
                on = (k % 4) == q
                cx = PW - 200 + q * 34; r = 10 if q == 0 else 7
                d.ellipse((cx - r, PH + 23 - r, cx + r, PH + 23 + r), fill=(CORAL if on else (100, 80, 130)) if on else (100, 80, 130))
                if on:
                    d.ellipse((cx - r - 3, PH + 23 - r - 3, cx + r + 3, PH + 23 + r + 3), outline=CORAL, width=2)
        # current lyric line
        cur = None
        for (lt, txt, ls, li) in _F["lines"]:
            if lt <= t + 0.02:
                cur = (lt, txt, ls, li)
        if cur:
            txt = cur[1]; size = 32
            f = _F["fonts"]["cap"](size)
            while f.getlength(txt) > PW - 60 and size > 16:
                size -= 2; f = _F["fonts"]["cap"](size)
            age = t - cur[0]
            fill = CREAM if age > 0.12 else (255, 224, 140)
            d.text((PW // 2, PH + 66), txt, font=f, fill=fill, anchor="mm")
    else:
        d.text((PW // 2, PH + 50), "END CARD  (6 s)", font=mono(22), fill=CREAM, anchor="mm")
    # timeline
    x_a, x_b, y = 16, PW - 16, PH + SH - 16
    for sc in SECS:
        xa = x_a + (x_b - x_a) * sc["start_s"] / TOTAL; xb = x_a + (x_b - x_a) * sc["end_s"] / TOTAL
        d.rectangle((xa + 1, y, xb - 1, y + 7), fill=KIND[sc["id"]])
    d.rectangle((x_a + (x_b - x_a) * DUR / TOTAL + 1, y, x_b, y + 7), fill=(255, 246, 229))
    px = x_a + (x_b - x_a) * min(t, TOTAL) / TOTAL
    d.rectangle((px - 1, y - 6, px + 1, y + 13), fill=CREAM)
    return np.asarray(can)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--from", dest="t0", type=float, default=0.0); ap.add_argument("--to", dest="t1", type=float, default=TOTAL)
    ap.add_argument("--still", type=float, nargs="*")
    a = ap.parse_args()
    if a.still:
        for ts in a.still:
            Image.fromarray(render(int(ts * FPS))).save(os.path.join(ROOT, "out", f"tan_{ts:06.2f}.png"))
        sys.exit(0)
    from multiprocessing import Pool
    i0, i1 = int(a.t0 * FPS), int(min(a.t1, TOTAL) * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{PW}x{PH + SH}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "fast", "-crf", "24", "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    with Pool(2, initializer=load) as pool:
        for n, fr in enumerate(pool.imap(render, range(i0, i1), chunksize=8)):
            ff.stdin.write(fr.tobytes())
            if n % 300 == 0:
                print(f"{n}/{i1 - i0}", flush=True)
    ff.stdin.close(); ff.wait(); print("done")
