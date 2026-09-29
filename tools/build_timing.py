#!/usr/bin/env python3
"""Combine the measured bar grid with the aligned vocal lines into timing.json (the one file the renderer reads).

Usage: python3 tools/build_timing.py            (run from the repo root, after analyze/recognize/align)
"""
import json

BAR, BAR0, DUR = 1.8373, 0.616, 174.02          # fitted to five decisive section onsets (residuals under 40 ms)
LEAD = 0.85                                     # chorus lines start this long before the bar downbeat (measured: the pickup begins ~2 beats early)
STARTS = dict(intro=None, verse1=6, pre1=14, chorus1=20, verse2=28, pre2=36, chorus2=42, dance=50, verse3=54, bridge=68, final=78, outro=90)
ONE_BAR_LINES = {"chorus1", "chorus2", "final"}   # one lyric line per bar, so the grid beats the recognizer

lyr = json.load(open("lyrics.json"))
lyr["sections"][0]["lines"][0] = "Everybody's upping their P-doom."   # as sung: the intro says P-doom, the outro says doom
meas = json.load(open("out/audio/timing.json"))["lines"]
bar_t = lambda k: BAR0 + BAR * k
order = list(STARTS)
out_secs, mi = [], 0
for si, sec in enumerate(lyr["sections"]):
    sid = sec["id"]
    k0 = STARTS[sid]
    nxt = STARTS[order[si + 1]] if si + 1 < len(order) else None
    s0 = 0.0 if k0 is None else bar_t(k0)
    s1 = DUR if nxt is None else bar_t(nxt)
    lines = []
    for li, text in enumerate(sec["lines"]):
        m = meas[mi]; mi += 1
        assert m["section"] == sid and m["li"] == li, (sid, li, m["section"], m["li"])
        frac = m["matched"] / max(1, m["words"])
        if sid in ONE_BAR_LINES:
            t, src = bar_t(k0 + li) - LEAD, "grid"
        elif frac >= 0.6 and not m.get("interpolated"):
            t, src = m["t"], "vocal"
        else:
            t, src = m["t"], "vocal-weak"
        lines.append(dict(text=text, t=round(t, 2), src=src))
    out_secs.append(dict(id=sid, name=sec["name"], start_bar=k0, bars=(None if k0 is None else round((s1 - s0) / BAR, 1)),
                         start_s=round(s0, 2), end_s=round(s1, 2), direction=sec["direction"], lines=lines))

song = dict(file="song.mp3", duration=DUR, bpm=round(240 / BAR, 2), bar_s=BAR, bar0_s=BAR0, generator="Suno",
            method="Bar grid fitted to section onsets in the instrumental stem; line starts from speech recognition on the vocal stem, snapped to vocal onsets; chorus lines placed on the grid.")
json.dump(dict(song=song, sections=out_secs), open("timing.json", "w"), indent=1, ensure_ascii=False)

# lyrics.json: keep the words, replace the PLANNED timing with the measured one
for sec, new in zip(lyr["sections"], out_secs):
    sec["start_bar"], sec["bars"], sec["start_s"], sec["end_s"] = new["start_bar"], new["bars"], new["start_s"], new["end_s"]
    sec["line_starts_s"] = [l["t"] for l in new["lines"]]
lyr["bpm"] = song["bpm"]
lyr["timing_note"] = "MEASURED from the finished Suno track (see timing.json and tools/). Bar = 1.8373 s. Line starts are seconds from the start of the audio."
json.dump(lyr, open("lyrics.json", "w"), indent=1, ensure_ascii=False)

print(f"{song['bpm']} BPM, bar {BAR}s, {DUR}s")
for s in out_secs:
    print(f"{s['start_s']:7.2f}-{s['end_s']:7.2f}  {s['name']:14s} bars {s['bars']}")
    for l in s["lines"]:
        print(f"           {l['t']:7.2f} {l['src']:10s} {l['text'][:60]}")
