#!/usr/bin/env python3
"""Fit the lyric lines to the recognized words and snap each line start to a real vocal onset.

Usage: python3 tools/align_lyrics.py lyrics.json out/audio/words.json out/audio/vocals.wav out/audio/timing.json
"""
import sys, json, re
from difflib import SequenceMatcher
import numpy as np, librosa, soundfile as sf

lyr = json.load(open(sys.argv[1]))
asr = json.load(open(sys.argv[2]))
voc = sys.argv[3]
dst = sys.argv[4]

def norm(w):
    w = w.lower().replace("’", "'")
    return re.sub(r"[^a-z0-9']", "", w)

SUB = {"pee": "p", "five-point-five": "five point five"}
L = []   # (word, section_idx, line_idx)
for si, sec in enumerate(lyr["sections"]):
    for li, line in enumerate(sec["lines"]):
        txt = line.replace("—", " ").replace("…", " ").replace("-", " ")
        for w in txt.split():
            n = norm(w)
            if n:
                L.append((SUB.get(n, n), si, li))
A = [(norm(a["w"]), a["t"]) for a in asr if norm(a["w"])]

def sim(a, b):
    if a == b: return 1.0
    r = SequenceMatcher(None, a, b).ratio()
    return 0.85 * r if r >= 0.6 else -0.5

n, m = len(L), len(A)
GAP_L, GAP_A = -0.45, -0.35    # skipped lyric word / extra recognized word
D = np.zeros((n + 1, m + 1)); B = np.zeros((n + 1, m + 1), dtype=np.int8)
for i in range(1, n + 1): D[i, 0] = i * GAP_L; B[i, 0] = 1
for j in range(1, m + 1): D[0, j] = j * GAP_A; B[0, j] = 2
for i in range(1, n + 1):
    for j in range(1, m + 1):
        d = D[i - 1, j - 1] + sim(L[i - 1][0], A[j - 1][0])
        u = D[i - 1, j] + GAP_L
        l = D[i, j - 1] + GAP_A
        best = max(d, u, l)
        D[i, j] = best; B[i, j] = 0 if best == d else (1 if best == u else 2)
i, j = n, m; match = {}
while i > 0 or j > 0:
    b = B[i, j]
    if b == 0 and i > 0 and j > 0:
        if sim(L[i - 1][0], A[j - 1][0]) > 0: match[i - 1] = A[j - 1][1]
        i -= 1; j -= 1
    elif b == 1 and i > 0: i -= 1
    else: j -= 1

# ---- vocal onsets -----------------------------------------------------------
y, sr = sf.read(voc, always_2d=True); y = librosa.resample(y.mean(1).astype(np.float32), orig_sr=sr, target_sr=22050); sr = 22050
hop = 256
env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop, fmin=200, fmax=5000, aggregate=np.median)
on = librosa.onset.onset_detect(onset_envelope=env, sr=sr, hop_length=hop, backtrack=False, delta=0.10, wait=3)
onT = librosa.frames_to_time(on, sr=sr, hop_length=hop)
rmsv = librosa.feature.rms(y=y, hop_length=hop)[0]
rt = librosa.frames_to_time(np.arange(len(rmsv)), sr=sr, hop_length=hop)

# ---- per line ------------------------------------------------------------
lines = []
k = 0
for si, sec in enumerate(lyr["sections"]):
    for li, line in enumerate(sec["lines"]):
        idx = [q for q, (w, s_, l_) in enumerate(L) if s_ == si and l_ == li]
        ts = [match[q] for q in idx if q in match]
        lines.append(dict(section=sec["id"], si=si, li=li, text=line, words=len(idx), matched=len(ts),
                          t_asr=(float(np.median(ts[:2])) if ts else None), t_last=(float(ts[-1]) if ts else None)))
# fill unmatched lines by interpolation between neighbors
known = [(k_, l_["t_asr"]) for k_, l_ in enumerate(lines) if l_["t_asr"] is not None]
for k_, l_ in enumerate(lines):
    if l_["t_asr"] is None:
        prev = [t for q, t in known if q < k_]; nxt = [t for q, t in known if q > k_]
        l_["t_asr"] = float((prev[-1] if prev else 0) * 0.5 + (nxt[0] if nxt else prev[-1] + 3) * 0.5); l_["interpolated"] = True
# monotonic guard
for k_ in range(1, len(lines)):
    if lines[k_]["t_asr"] <= lines[k_ - 1]["t_asr"]:
        lines[k_]["t_asr"] = lines[k_ - 1]["t_asr"] + 0.3
# snap to the nearest vocal onset (within 0.35 s, and after the previous snapped start)
prev = -1
for l_ in lines:
    c = onT[(np.abs(onT - l_["t_asr"]) <= 0.35) & (onT > prev + 0.25)]
    if len(c):
        l_["t"] = float(c[np.argmin(np.abs(c - l_["t_asr"]))]); l_["snap"] = True
    else:
        l_["t"] = l_["t_asr"]; l_["snap"] = False
    prev = l_["t"]

json.dump(dict(lines=lines, onsets=[round(float(x), 3) for x in onT], words_matched=len(match), words_total=len(L), asr_words=len(A)),
          open(dst, "w"), indent=1)
print(f"matched {len(match)}/{len(L)} lyric words against {len(A)} recognized words; {len(onT)} vocal onsets")
for l_ in lines:
    flag = ("~" if l_.get("interpolated") else " ") + ("*" if l_["snap"] else " ")
    print(f"{l_['t']:7.2f} {flag} {l_['matched']:2d}/{l_['words']:2d} [{l_['section'][:6]:6s}] {l_['text'][:64]}")
