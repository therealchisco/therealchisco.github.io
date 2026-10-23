#!/usr/bin/env python3
"""Turn a Write app .svgz export, or a scanned page (.jpg/.png/.pdf), into a Jekyll post.

usage: svgz_to_post.py FILE "Title" [Category] [YYYY-MM-DD]

Scans need potrace (brew install potrace), Pillow + numpy, and pdftoppm for PDFs.
If the post file already exists, only the drawing is replaced; everything above
it (front matter, heading, transcript) is kept.
"""
import datetime, gzip, os, re, subprocess, sys, tempfile

W = 920  # post drawing width, matches the Write page


def from_write(src):
    svg = gzip.open(src, "rt", encoding="utf-8").read()
    height = re.search(r'class="write-page"[^>]*height="(\d+)', svg).group(1)
    paths = re.findall(r"<path\b[^>]*/>", svg)  # pen strokes only; skips ruling, thumbnail, config
    return int(height), "\n".join("    " + p for p in paths)


def from_scan(src):
    from PIL import Image, ImageFilter
    import numpy as np

    tmp = tempfile.mkdtemp()
    if src.lower().endswith(".pdf"):
        # ponytail: first page only, loop pages and stack if multi-page scans show up
        subprocess.run(["pdftoppm", "-r", "300", "-png", "-f", "1", "-l", "1", src, f"{tmp}/p"], check=True)
        src = f"{tmp}/" + os.listdir(tmp)[0]
    im = Image.open(src).convert("L")
    # flatten uneven lighting, then keep anything noticeably darker than the paper
    bg = im.filter(ImageFilter.GaussianBlur(30))
    ink = np.asarray(im, float) / np.maximum(np.asarray(bg, float), 1) < 0.80
    h, w = ink.shape
    ink = ink[40:h - 15, 60:w - 40]  # trim page edges/shadow; tune per scan
    h, w = ink.shape
    Image.fromarray(np.where(ink, 0, 255).astype("uint8")).convert("1").save(f"{tmp}/bw.bmp")
    # -t 12 drops specks under 12px: dot-grid paper is <10px, i-dots and periods are 15+
    subprocess.run(["potrace", f"{tmp}/bw.bmp", "-s", "-t", "12", "-o", f"{tmp}/out.svg"], check=True)
    paths = re.findall(r"<path\b[^>]*/>", open(f"{tmp}/out.svg").read())
    s = W / w
    # potrace coords are 10x and y-up; this maps them onto the 920-wide page
    g = f'    <g transform="translate(0,{h * s:.2f}) scale({0.1 * s:.6f},{-0.1 * s:.6f})" fill="#000000" stroke="none">\n'
    return round(h * s), g + "\n".join("    " + p for p in paths) + "\n    </g>"


src, title = sys.argv[1], sys.argv[2]
cat = sys.argv[3] if len(sys.argv) > 3 else "Self"
now = datetime.datetime.now().astimezone()
date = sys.argv[4] if len(sys.argv) > 4 else now.date().isoformat()
# explicit offset so Jekyll files it under the right day and doesn't skip it as future
stamp = now.strftime("%H:%M:%S %z") if date == now.date().isoformat() else "12:00:00 " + now.strftime("%z")

height, body = from_write(src) if src.endswith(".svgz") else from_scan(src)
slug = re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")

out = f"_posts/{date}-{slug}.md"
MARK = '<div class="svg-box">'
if os.path.exists(out):
    head = open(out, encoding="utf-8").read().split(MARK)[0]
else:
    head = f'---\nlayout: post\ntitle:  "{title}"\ndate:   {date} {stamp}\ncategories: {cat}\n---\n\n'
with open(out, "w", encoding="utf-8") as f:
    f.write(head + MARK + '\n\n  <svg class="svg-box-content" version="1.1" '
            'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewbox="0, 0, {W}, {height}">\n\n')
    f.write(body)
    f.write("\n\n </svg>\n\n</div>\n")
print(out, body.count("<path"), "paths, height", height)
