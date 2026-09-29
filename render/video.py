"""Command line for the video engine (kept apart from engine.py so scenes register into ONE engine module).

    python3 render/video.py still 44.0 92.0            -> out/s_044.00.png ...
    python3 render/video.py clip 37.0 41.0 out/c.mp4   (a few seconds, silent)
    python3 render/video.py full out/silent.mp4        (whole video, silent; mux the song afterwards)
Set RENDER_W=1920 for the 1080p master (default 1280 for review cuts).
"""
import sys, time, subprocess
from PIL import Image
import engine as E
import scenes

scenes.load()


def _init():
    scenes.load()


if __name__ == "__main__":
    mode = sys.argv[1]
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
