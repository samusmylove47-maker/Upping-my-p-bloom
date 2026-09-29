#!/usr/bin/env python3
"""Measure a finished song: tempo grid, downbeats, per-bar energy, section boundaries, key.

Usage: python3 tools/analyze_audio.py out/audio/song.mp3 out/audio/analysis.json
Everything here is signal processing, so it can't hear words. It finds WHEN things happen.
"""
import sys, json
import numpy as np, librosa

src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else "analysis.json"
SR = 22050
y, sr = librosa.load(src, sr=SR, mono=True)
dur = len(y) / sr
hop = 512

# ---- tempo and beat grid -------------------------------------------------
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
tempo, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=hop, start_bpm=128, tightness=200)
bt = librosa.frames_to_time(beats, sr=sr, hop_length=hop)
tempo = float(np.atleast_1d(tempo)[0])
# fit a constant-tempo grid to the tracked beats (robust: drop outliers once)
idx = np.arange(len(bt))
A = np.vstack([idx, np.ones_like(idx)]).T
slope, icpt = np.linalg.lstsq(A, bt, rcond=None)[0]
res = bt - (slope * idx + icpt)
keep = np.abs(res) < 0.06
slope, icpt = np.linalg.lstsq(A[keep], bt[keep], rcond=None)[0]
res = bt - (slope * idx + icpt)
print(f"duration {dur:.2f}s  tracked tempo {tempo:.2f}  fitted beat {slope:.4f}s = {60/slope:.2f} BPM  grid residual std {res[keep].std()*1000:.1f} ms  outliers {int((~keep).sum())}/{len(bt)}")

beat = slope
t0 = icpt % beat  # first grid beat time
# ---- downbeat phase: which of 4 positions carries the kick/bass most --------
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop)) ** 2
freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
low = S[(freqs >= 35) & (freqs <= 130)].sum(0)
tframes = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=hop)
def at(x, t, w=0.045):
    m = (tframes >= t - w) & (tframes <= t + w)
    return x[m].max() if m.any() else 0.0
nb = int((dur - t0) / beat)
lowb = np.array([at(low, t0 + i * beat) for i in range(nb)])
phase_scores = [lowb[p::4].mean() for p in range(4)]
print("low-band by beat phase (higher = more downbeat-like):", np.round(phase_scores, 1))
# Downbeat = phase with strongest bass (a kick+bass on 1 is typical); we also report the spread so weak cases are visible.
p_db = int(np.argmax(phase_scores))
db0 = t0 + p_db * beat          # time of the first downbeat found on the grid
bar = beat * 4

# ---- per-bar features ------------------------------------------------------
nbars = int((dur - db0) / bar) + 1
rms = librosa.feature.rms(S=np.sqrt(S), frame_length=2048, hop_length=hop)[0]
cent = librosa.feature.spectral_centroid(S=np.sqrt(S), sr=sr)[0]
chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
mfcc = librosa.feature.mfcc(S=librosa.power_to_db(librosa.feature.melspectrogram(S=S, sr=sr)), n_mfcc=13)
vox = S[(freqs >= 300) & (freqs <= 3400)].sum(0)
def seg(x, a, b):
    m = (tframes >= a) & (tframes < b)
    return x[m].mean(0) if x.ndim == 1 else x[:, m].mean(1)
rows = []
for k in range(nbars):
    a, b = db0 + k * bar, db0 + (k + 1) * bar
    rows.append(dict(bar=k, t=round(a, 3),
                     rms_db=float(20 * np.log10(seg(rms, a, b) + 1e-9)),
                     low_db=float(10 * np.log10(seg(low, a, b) + 1e-9)),
                     vox_db=float(10 * np.log10(seg(vox, a, b) + 1e-9)),
                     centroid=float(seg(cent, a, b))))
# bars before the first downbeat (pickup / intro before the grid starts)
pre_bars = int(db0 // bar)

# ---- section boundaries by novelty over bars ---------------------------------
F = []
for k in range(nbars):
    a, b = db0 + k * bar, db0 + (k + 1) * bar
    F.append(np.concatenate([seg(chroma, a, b), seg(mfcc, a, b)]))
F = np.array(F)
F = (F - F.mean(0)) / (F.std(0) + 1e-9)
Sm = F @ F.T / F.shape[1]
L = 4  # half-window in bars
nov = np.zeros(nbars)
for i in range(L, nbars - L):
    a = Sm[i - L:i, i - L:i].mean() + Sm[i:i + L, i:i + L].mean()
    b = 2 * Sm[i - L:i, i:i + L].mean()
    nov[i] = a - b
peaks = [i for i in range(2, nbars - 2) if nov[i] > 0.35 * nov.max() and nov[i] == nov[max(0, i - 2):i + 3].max()]

# ---- key estimate per bar-window (Krumhansl) for the key-change check -------------
maj = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
mnr = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
def key_of(c):
    best = (-9, None)
    for i in range(12):
        for nm, prof in (("maj", maj), ("min", mnr)):
            r = np.corrcoef(np.roll(prof, i), c)[0, 1]
            if r > best[0]: best = (r, names[i] + " " + nm)
    return best
keys = []
for k in range(0, nbars - 3, 4):
    a, b = db0 + k * bar, db0 + (k + 4) * bar
    r, nm = key_of(seg(chroma, a, b))
    keys.append((k, round(db0 + k * bar, 1), nm, round(float(r), 2)))

out = dict(duration=dur, bpm=60 / beat, beat_s=beat, bar_s=bar, first_downbeat_s=db0, downbeat_phase=p_db,
           phase_scores=[float(x) for x in phase_scores], grid_residual_ms=float(res[keep].std() * 1000),
           bars=rows, novelty=[float(x) for x in nov], boundary_bars=peaks, keys=keys, pre_bars=pre_bars)
json.dump(out, open(dst, "w"), indent=1)
print(f"first downbeat {db0:.3f}s (phase {p_db}), bar {bar:.3f}s, {nbars} bars, boundaries at bars {peaks}")
print("bar   time    rms   low   vox  cent")
for r in rows:
    m = "<<" if r["bar"] in peaks else ""
    print(f"{r['bar']:3d} {r['t']:7.2f} {r['rms_db']:6.1f} {r['low_db']:6.1f} {r['vox_db']:6.1f} {r['centroid']:6.0f} {m}")
print("keys (4-bar windows):", keys)
