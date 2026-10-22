#!/usr/bin/env python3
"""Turn a Write app .svgz export into a Jekyll post.

usage: svgz_to_post.py FILE.svgz "Title" [Category] [YYYY-MM-DD]

If the post file already exists, only the drawing is replaced; front matter
and heading (e.g. hand-edited titles) are kept.
"""
import datetime, gzip, os, re, sys

src, title = sys.argv[1], sys.argv[2]
cat = sys.argv[3] if len(sys.argv) > 3 else "Self"
date = sys.argv[4] if len(sys.argv) > 4 else datetime.date.today().isoformat()

svg = gzip.open(src, "rt", encoding="utf-8").read()
height = re.search(r'class="write-page"[^>]*height="(\d+)', svg).group(1)
paths = re.findall(r"<path\b[^>]*/>", svg)  # pen strokes only; skips ruling, thumbnail, config
slug = re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")

out = f"_posts/{date}-{slug}.md"
MARK = '<div class="svg-box">'
if os.path.exists(out):
    head = open(out, encoding="utf-8").read().split(MARK)[0]
else:
    head = f'---\nlayout: post\ntitle:  "{title}"\ndate:   {date} 10:18:00\ncategories: {cat}\n---\n\n'
with open(out, "w", encoding="utf-8") as f:
    f.write(head + MARK + '\n\n  <svg class="svg-box-content" version="1.1" '
            'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewbox="0, 0, 920, {height}">\n\n')
    f.write("\n".join("    " + p for p in paths))
    f.write("\n\n </svg>\n\n</div>\n")
print(out, len(paths), "paths, height", height)
