# Upping My P(Bloom) — An Answer

**Written, drawn, animated and coded entirely by Claude Sonnet 5.5, in Claude.ai.**
Directed and published by Avenrae / ShaeAI. The sung audio comes from a music generator working from the lyrics and style prompt in this repo; it was made with Suno v6 on the Pro plan, as [CREDITS.md](CREDITS.md) and the video description say.

A reply in kind to the "upping my p(doom)" videos: an ultra-singable song, a paper-cut video anyone can fork, and a dial that only moves when somebody on screen does something. It takes the risks seriously, refuses to call the ending written, and asks who is going to pick up the shovel.

![Title card](docs/frames/f1.jpg)

| | |
|---|---|
| ![The bloom stage](docs/frames/f3.jpg) | ![Every bloom needs a trellis](docs/frames/f8.jpg) |
| ![Somebody's…](docs/frames/f5.jpg) | ![Hi! I'm Sonnet 5.5](docs/frames/f7.jpg) |

## Status

The full video renders from this repo, timed to the finished song. `timing.json` is the measured map of that song (bar grid, section starts, line starts); `lyrics.json` carries the words and the same timings. The audio file itself is not in the repo: generate your own with the lyrics and style prompt, then re-measure it (below).

## Render it yourself

```bash
pip install -r requirements.txt        # Pillow, NumPy, SciPy, Fredoka font
python render/video.py still 44.0 92.0            # look at single moments -> out/s_044.00.png ...
python render/video.py clip 37 41 out/c.mp4       # a few seconds, silent
python render/video.py full out/silent.mp4        # the whole video, silent (720p review cut; RENDER_W=1920 for 1080p)
python render/video.py hook 36.5 51.5 out/hook.mp4   # the 15-second chorus clip with a credit tag on the whole time
python render/video.py vert 36.5 51.5 out/vert.mp4   # the same clip as 1080x1920 with its own captions and credit footer
python render/thumb.py                            # the YouTube thumbnail -> out/thumbnail.jpg
ffmpeg -i out/silent.mp4 -i song.mp3 -filter_complex "[1:a]apad=whole_dur=180.02[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k out/video.mp4
```

Everything is plain Python: Pillow draws layered paper cut-outs with soft shadows, NumPy handles compositing and grain, ffmpeg encodes. Every frame is a pure function of song time, so any second can be re-rendered on its own, and a new song is a re-measure, not a redraw.

**Using a different recording?** `tools/` measures a track without anyone listening to it: `analyze_audio.py` (tempo, sections), `recognize_vocals.py` (words on the vocal stem), `align_lyrics.py`, then `build_timing.py` writes a new `timing.json`. Hand-checked line starts live in the `CHECKED` table at the top of `build_timing.py`.

## Make it yours

* `theme.json` holds the title, the credit wording, the seconds the corner tag shows, and the repo line for the end card. Change the words and re-render; no drawing code to touch.
* `lyrics.json` has every section, its bar count and its measured time.
* **Verse 3 is open.** It is a roll call ("Somebody's …") and roll calls grow. See [verses/README.md](verses/README.md) and open a pull request with your own lines.

## The rules the video keeps

* It says plainly that an AI made it, on the opening card, in a short corner tag, in the bridge, and on the end card.
* The dial has no numbers. It is a prop, not a probability, and it stops short of full.
* Nothing about real people or companies. No borrowed mascots. Nobody else's lyrics.
* Every bright picture has its support in the frame: a fence, a lamp, a clipboard, a trellis.

## License

MIT for the code and the words. See [LICENSE](LICENSE). The Fredoka One font is under the SIL Open Font License and is installed from PyPI, not bundled here.
