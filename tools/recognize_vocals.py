#!/usr/bin/env python3
"""Run offline speech recognition (sherpa-onnx transducer) on the vocal stem and save timed words.

Usage: python3 tools/recognize_vocals.py out/audio/stems/vocals.wav out/audio/models/asr/<model-dir> out/audio/words.json
Singing is hard for speech models, so treat the words as evidence about timing, not as a transcript.
"""
import sys, json, glob, os
import numpy as np, soundfile as sf, librosa, sherpa_onnx

wav, mdir, dst = sys.argv[1], sys.argv[2], sys.argv[3]
WIN, HOP = 12.0, 10.0   # seconds; 2 s of overlap between windows

y, sr = sf.read(wav, always_2d=True)
y = y.mean(1).astype(np.float32)
y = librosa.resample(y, orig_sr=sr, target_sr=16000)
sr = 16000
dur = len(y) / sr

def pick(pattern):
    fs = sorted(glob.glob(os.path.join(mdir, pattern)))
    fs = [f for f in fs if "int8" in f] or fs
    return fs[0]
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=pick("encoder*.onnx"), decoder=pick("decoder*.onnx"), joiner=pick("joiner*.onnx"),
    tokens=os.path.join(mdir, "tokens.txt"), num_threads=2, sample_rate=16000, feature_dim=80,
    decoding_method="greedy_search")

toks = []   # (time, token)
t = 0.0
while t < dur:
    a, b = int(t * sr), int(min(dur, t + WIN) * sr)
    st = rec.create_stream()
    st.accept_waveform(sr, y[a:b])
    rec.decode_stream(st)
    r = st.result
    keep_lo = t + (1.0 if t > 0 else 0.0)
    keep_hi = t + WIN - 1.0 if (t + WIN) < dur else dur + 1
    for tk, ts in zip(r.tokens, r.timestamps):
        T = t + ts
        if keep_lo <= T < keep_hi:
            toks.append((round(T, 3), tk))
    print(f"[{t:6.1f}-{min(dur, t+WIN):6.1f}] {r.text.strip()[:110]}", flush=True)
    t += HOP

# tokens -> words (a token that starts with a space, or the BPE mark, starts a word)
words, cur, cur_t = [], "", None
for T, tk in toks:
    if tk.startswith(" ") or tk.startswith("\u2581") or cur == "":
        if cur: words.append((cur_t, cur))
        cur, cur_t = tk.lstrip(" \u2581"), T
    else:
        cur += tk
if cur: words.append((cur_t, cur))
json.dump([{"t": w[0], "w": w[1].lower()} for w in words], open(dst, "w"), indent=0)
print(len(words), "words ->", dst)
