"""Temp beat for the animatic: kick / clap / hat / bass / marimba at 128 BPM. NOT the song."""
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
BPM = 128
SPB = 60 / BPM
DUR = 15.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)


def add(sig, t0, gl=1.0, gr=1.0):
    i = int(t0 * SR)
    n = min(len(sig), N - i)
    if n > 0:
        L[i:i + n] += sig[:n] * gl
        R[i:i + n] += sig[:n] * gr


def kick():
    t = np.arange(int(0.28 * SR)) / SR
    f = 46 + 110 * np.exp(-t * 26)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.11) * 0.95


b, a = signal.butter(2, [900 / (SR / 2), 4200 / (SR / 2)], 'band')


def clap():
    out = np.zeros(int(0.25 * SR))
    for off in (0, 0.011, 0.022):
        n = rng.normal(0, 1, len(out))
        t = np.arange(len(out)) / SR
        env = np.exp(-np.maximum(t - off, 0) / 0.05) * (t >= off)
        out += signal.lfilter(b, a, n) * env
    return out * 0.32


hb, ha = signal.butter(2, 6500 / (SR / 2), 'high')


def hat(open_=False):
    n = int((0.16 if open_ else 0.045) * SR)
    t = np.arange(n) / SR
    return signal.lfilter(hb, ha, rng.normal(0, 1, n)) * np.exp(-t / (0.06 if open_ else 0.012)) * (0.16 if open_ else 0.13)


def bass(f):
    t = np.arange(int(0.24 * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t / 0.12) * 0.42


def pluck(f, dur=0.32):
    t = np.arange(int(dur * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.05)) * np.exp(-t / 0.13) * 0.16


def m(x):
    return 440 * 2 ** ((x - 69) / 12)


K, C, H_ = kick(), clap(), hat(),
notes = [55, 59, 62, 59]  # G major-ish arp (G3 B3 D4 B3)
bar_roots = [43, 43, 47, 40, 43, 43, 47, 40]  # G G B? C -> G,G,B,E... light movement
for beat in range(int(DUR / SPB) + 1):
    t0 = beat * SPB
    if t0 >= DUR:
        break
    add(K, t0)
    if beat % 4 in (1, 3):
        add(C, t0, 0.9, 1.1)
    add(hat(), t0 + SPB / 2, 1.1, 0.9)
    if beat % 4 == 3:
        add(hat(True), t0 + SPB * 0.75, 0.8, 1.0)
    bar = beat // 4
    root = m(bar_roots[min(bar, 7)] - 12 + 12)
    add(bass(root), t0 + SPB / 2)
    add(bass(root), t0 + SPB * 0.75 + 0.0 if False else t0 + SPB / 2 + SPB / 4, 0.7, 0.7)
    for q in range(2):
        add(pluck(m(notes[(beat * 2 + q) % 4] + 12 + (12 if bar >= 4 else 0))), t0 + q * SPB / 2, 0.7 + 0.3 * q, 1.0 - 0.3 * q)
    if beat % 4 == 3:
        add(pluck(m(79), 0.5), t0, 1.3, 1.3)  # "BLOOM" accent, high G
        add(pluck(m(83), 0.5), t0 + 0.02, 1.0, 1.4)

fade = np.minimum(1, np.arange(N) / (SR * 0.05)) * np.minimum(1, (N - np.arange(N)) / (SR * 0.25))
L *= fade
R *= fade
pk = max(np.abs(L).max(), np.abs(R).max())
out = np.stack([L, R], axis=1) * (0.85 / pk)
import os
os.makedirs("out", exist_ok=True)
wavfile.write("out/tempbeat.wav", SR, (out * 32767).astype(np.int16))
print("peak", pk, "dur", N / SR)
