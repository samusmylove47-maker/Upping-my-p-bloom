#!/usr/bin/env python3
"""Contact sheet: python3 tools/sheet.py out/sheet.png cols img1 img2 ... (each tile 640 wide)"""
import sys
from PIL import Image, ImageDraw
dst, cols, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
tw = 640
ims = [Image.open(f).convert("RGB") for f in files]
th = int(tw * ims[0].height / ims[0].width)
rows = (len(ims) + cols - 1) // cols
sh = Image.new("RGB", (cols * tw, rows * th), (20, 20, 20))
for i, (f, im) in enumerate(zip(files, ims)):
    sh.paste(im.resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
    ImageDraw.Draw(sh).text(((i % cols) * tw + 8, (i // cols) * th + 6), f.split("/")[-1], fill=(255, 255, 255))
sh.save(dst)
print(dst, sh.size)
