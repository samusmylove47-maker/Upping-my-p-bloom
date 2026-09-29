"""Command line for the video engine (kept apart from engine.py so scenes register into ONE engine module).

    python3 render/video.py still 44.0 92.0            -> out/s_044.00.png ...
    python3 render/video.py clip 37.0 41.0 out/c.mp4   (a few seconds, silent)
    python3 render/video.py full out/silent.mp4        (whole video, silent; mux the song afterwards)
    python3 render/video.py hook 36.5 51.5 out/hook.mp4   (a short 16:9 clip with the credit tag on the whole time)
    python3 render/video.py vert 36.5 51.5 out/vert.mp4   (the same clip as 1080x1920 with its own captions and credit footer)
Set RENDER_W=1920 for the 1080p master (default 1280 for review cuts).
"""
import sys, time, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine as E
import scenes

scenes.load()


# ---------------------------------------------------------------- 9:16 layout
VW, VH = 1080, 1920
_VBG = {}


def _shadowed_tag(img, cx, cy, txt, size, fill, ink, padx=44, pady=20, rot_pad=0):
    f = E.font(E.FRED, size)
    w = int(f.getlength(txt) + padx * 2); h = int(size * 1.05 + pady * 2)
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    sh = Image.new("L", img.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle([x0 + 3, y0 + 8, x0 + w + 3, y0 + h + 8], radius=min(30, h // 2), fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    img.paste(Image.new("RGB", img.size, (40, 16, 56)), (0, 0), sh)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=min(30, h // 2), fill=fill)
    d.text((cx, cy + 2), txt, font=f, fill=ink, anchor="mm")


def _wrap(txt, font, maxw):
    words, lines, cur = txt.split(), [], ""
    for w_ in words:
        t_ = (cur + " " + w_).strip()
        if font.getlength(t_) <= maxw or not cur:
            cur = t_
        else:
            lines.append(cur); cur = w_
    lines.append(cur)
    return lines


def render_vert(i):
    """One 1080x1920 frame: blurred warm backdrop, the scene panel in the middle, big captions above, credit footer below."""
    fr = E.render(i)                                        # 1920x1080, no caption
    t = i / E.FPS
    src = Image.fromarray(fr)
    small = src.resize((216, 384), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5))
    bg = small.resize((VW, VH), Image.BICUBIC)
    bg = Image.blend(bg, Image.new("RGB", (VW, VH), (255, 150, 120)), 0.28)
    # panel: the middle 1440 px of the scene, scaled to full width
    panel = src.crop((150, 0, 1770, 1080)).resize((VW, 720), Image.LANCZOS)
    PY = 600
    sh = Image.new("L", (VW, VH), 0)
    ImageDraw.Draw(sh).rectangle([0, PY - 2, VW, PY + 720 + 2], fill=140)
    bg.paste(Image.new("RGB", (VW, VH), (40, 16, 56)), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    bg.paste(panel, (0, PY))
    d = ImageDraw.Draw(bg)
    # caption
    L_ = E.line_at(t)
    if L_:
        txt = E.cap_text(L_[1]); age = t - L_[0]
        pop = 1 + 0.10 * (1 - min(1, max(age, 0) * 6)) ** 3
        size = int(112 * pop)
        f = E.font(E.FRED, size)
        lines = _wrap(txt, f, 960)
        lh = int(size * 1.08)
        y0 = 340 - lh * (len(lines) - 1) // 2 + 10
        for k, ln in enumerate(lines):
            y = y0 + k * lh
            d.text((543, y + 9), ln, font=f, fill=E.CORAL, anchor="mm", stroke_width=8, stroke_fill=E.CORAL)
            d.text((540, y), ln, font=f, fill=E.CREAM, anchor="mm", stroke_width=8, stroke_fill=E.INK)
    # footer: title and credit
    _shadowed_tag(bg, 540, 1440, "Upping My P(Bloom)", 84, E.CREAM, E.INK, padx=48, pady=24)
    _shadowed_tag(bg, 540, 1565, "Made by Claude Sonnet 5.5", 54, E.INK, E.CREAM, padx=44, pady=20)
    f = E.font(E.FRED, 38)
    d.text((540, 1660), "words, art, animation and code, in Claude.ai", font=f, fill=E.CREAM, anchor="mm", stroke_width=4, stroke_fill=E.INK)
    # global fade-out for the clip
    a = np.asarray(bg).astype(np.float32)
    a *= E.clamp((E.HOOK["t1"] - t) / 0.35)
    return np.clip(a, 0, 255).astype(np.uint8)


def _init():
    scenes.load()


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode in ("hook", "vert"):
        a, b, dst = float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
        E.HOOK = {"t0": a, "t1": b, "bug": mode == "hook"}
        E.NO_CAPTION = (mode == "vert")
        fn = E.render if mode == "hook" else render_vert
        size = (E.OW, E.OH) if mode == "hook" else (VW, VH)
        i0, i1 = int(round(a * E.FPS)), int(round(b * E.FPS))
        from multiprocessing import Pool
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}", "-r", str(E.FPS), "-i", "-",
                               "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", dst], stdin=subprocess.PIPE)
        t0_ = time.time()
        with Pool(2, initializer=_init) as pool:
            for n, fr in enumerate(pool.imap(fn, range(i0, i1), chunksize=4)):
                ff.stdin.write(fr.tobytes())
                if n % 60 == 0:
                    print(f"frame {n}/{i1 - i0}  {time.time() - t0_:.0f}s", flush=True)
        ff.stdin.close(); ff.wait(); print("done", round(time.time() - t0_), "s", flush=True)
        sys.exit(0)
    if mode == "still":
        for ts in sys.argv[2:]:
            t0_ = time.time(); fr = E.render(int(round(float(ts) * E.FPS)))
            Image.fromarray(fr).save(f"{E.OUTDIR}/s_{float(ts):06.2f}.png"); print(ts, "%.2fs" % (time.time() - t0_), flush=True)
    else:
        if mode == "clip":
            a, b, dst = float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
        else:
            a, b, dst = 0.0, E.TOTAL, sys.argv[2]
        i0, i1 = int(round(a * E.FPS)), min(E.NF, int(round(b * E.FPS)))
        from multiprocessing import Pool
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{E.OW}x{E.OH}", "-r", str(E.FPS), "-i", "-",
                               "-c:v", "libx264", "-preset", "medium", "-crf", "20" if E.OW > 1300 else "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart", dst], stdin=subprocess.PIPE)
        t0_ = time.time()
        with Pool(2, initializer=_init) as pool:
            for n, fr in enumerate(pool.imap(E.render, range(i0, i1), chunksize=4)):
                ff.stdin.write(fr.tobytes())
                if n % 60 == 0:
                    print(f"frame {n}/{i1 - i0}  {time.time() - t0_:.0f}s", flush=True)
        ff.stdin.close(); ff.wait(); print("done", round(time.time() - t0_), "s", flush=True)
