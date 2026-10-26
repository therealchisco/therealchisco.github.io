#!/usr/bin/env python3
"""Turn a Write app .svgz export, or a scanned page (.jpg/.png/.pdf), into a Jekyll post.

usage: svgz_to_post.py FILE "Title" [Category] [YYYY-MM-DD]

Scans need potrace (brew install potrace), Pillow + numpy, and pdftoppm for PDFs.
If the post file already exists, only the drawings are replaced; everything above
them (front matter, heading, transcript) is kept.

scripts/post_studio.py is a drag-and-drop web UI over the same functions.
"""
import datetime, gzip, json, os, re, subprocess, sys, tempfile

W = 920  # post drawing width, matches the Write page
MARK = '<div class="svg-box">'
BODY = "<!-- generated body: edits above this line survive re-imports -->"
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
POSTS = os.path.join(ROOT, "_posts")


def from_write(src):
    svg = gzip.open(src, "rt", encoding="utf-8").read()
    height = re.search(r'class="write-page"[^>]*height="(\d+)', svg).group(1)
    paths = re.findall(r"<path\b[^>]*/>", svg)  # pen strokes only; skips ruling, thumbnail, config
    return int(height), "\n".join("    " + p for p in paths)


def pdf_pages(src, out_dir):
    subprocess.run(["pdftoppm", "-r", "200", "-png", src, f"{out_dir}/p"], check=True)
    return sorted(f"{out_dir}/{f}" for f in os.listdir(out_dir) if f.startswith("p"))


def open_image(src, max_w=1600):
    """Upright RGB image, at most max_w wide (phone photos: keeps tracing fast and speck size meaningful)."""
    from PIL import Image, ImageOps, UnidentifiedImageError

    try:
        im = Image.open(src)
        im.load()
    except UnidentifiedImageError:  # iPhone HEIC (often misnamed .png/.jpg): let macOS sips convert it
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["sips", "-s", "format", "png", src, "--out", f"{tmp}/c.png"], check=True, capture_output=True)
            im = Image.open(f"{tmp}/c.png")
            im.load()
    im = ImageOps.exif_transpose(im).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)))
    return im


def photo_jpeg(src):
    """JPEG bytes for embedding a photo as-is. Re-encoding drops EXIF (GPS location etc.)."""
    import io

    buf = io.BytesIO()
    open_image(src).save(buf, "JPEG", quality=85)
    return buf.getvalue()


def from_scan(src, threshold=0.80, specks=12, trim=1.0):
    """Trace one page image. threshold: how much darker than the paper counts as ink
    (lower keeps less), specks: blobs under this many px are dropped (dot-grid paper),
    trim: % cut from each edge to lose page edges and shadows."""
    from PIL import Image, ImageFilter
    import numpy as np

    im = open_image(src).convert("L")
    # flatten uneven lighting, then keep anything noticeably darker than the paper
    bg = im.filter(ImageFilter.GaussianBlur(30))
    ink = np.asarray(im, float) / np.maximum(np.asarray(bg, float), 1) < threshold
    h, w = ink.shape
    ty, tx = round(h * trim / 100), round(w * trim / 100)
    ink = ink[ty:h - ty, tx:w - tx]
    h, w = ink.shape
    with tempfile.TemporaryDirectory() as tmp:
        Image.fromarray(np.where(ink, 0, 255).astype("uint8")).convert("1").save(f"{tmp}/bw.bmp")
        # dot-grid dots are <10px at this size, i-dots and periods are 15+
        subprocess.run(["potrace", f"{tmp}/bw.bmp", "-s", "-t", str(int(specks)), "-o", f"{tmp}/out.svg"], check=True)
        paths = re.findall(r"<path\b[^>]*/>", open(f"{tmp}/out.svg").read())
    s = W / w
    # potrace coords are 10x and y-up; this maps them onto the 920-wide page
    g = f'    <g transform="translate(0,{h * s:.2f}) scale({0.1 * s:.6f},{-0.1 * s:.6f})" fill="#000000" stroke="none">\n'
    return round(h * s), g + "\n".join("    " + p for p in paths) + "\n    </g>"


def svg_box(height, body):
    return (MARK + '\n\n  <svg class="svg-box-content" version="1.1" '
            'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewbox="0, 0, {W}, {height}">\n\n' + body + "\n\n </svg>\n\n</div>\n")


def slugify(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")


def post_path(title, date=None):
    date = date or datetime.date.today().isoformat()
    return os.path.join(POSTS, f"{date}-{slugify(title)}.md")


def photo_dir(post):
    """Where a post's photos live, keyed by its filename so a title edit doesn't orphan them.
    Returns (filesystem dir, site URL prefix)."""
    rel = "assets/images/posts/" + os.path.splitext(os.path.basename(post))[0]
    return os.path.join(ROOT, rel), "/" + rel


def yaml_str(v):
    v = v.strip()
    if v.startswith('"'):
        try:
            return json.loads(v)
        except ValueError:
            return v.strip('"')
    return v.strip("'")


SVG_BOX = re.compile(r'<div class="svg-box">.*?</svg>\s*</div>', re.S)
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
TRANSCRIPT = re.compile(r"\s*<details>\s*<summary>Transcript</summary>\s*(.*?)\s*</details>", re.S)


def parse_post(path):
    """Split a post back into fields and body blocks: ("svg", html) | ("image", alt, url) | ("text", markdown)."""
    raw = open(path, encoding="utf-8").read()
    _, fm, body = raw.split("---\n", 2)
    post = {"fm_lines": fm.rstrip("\n").split("\n"), "title": "", "date_raw": "", "category": "", "heading": "", "transcript": ""}
    for line in post["fm_lines"]:
        k, _, v = line.partition(":")
        if k.strip() in ("title", "date", "categories"):
            post[{"title": "title", "date": "date_raw", "categories": "category"}[k.strip()]] = yaml_str(v)
    post["date"] = post["date_raw"][:10] or os.path.basename(path)[:10]
    body = body.replace(BODY, "")
    first = SVG_BOX.search(body)
    top, body = (body[:first.start()], body[first.start():]) if first else (body, "")
    m = re.match(r"\s*# ([^\n]+)\n", top)  # a leading "# heading" line is the post heading
    if m:
        post["heading"], top = m.group(1).strip(), top[m.end():]
    m = TRANSCRIPT.match(top)
    if m:
        post["transcript"], top = m.group(1), top[m.end():]
    blocks, text = [], []

    def flush():
        if text:
            blocks.append(("text", "\n\n".join(text)))
            text.clear()

    rest = top + body
    boxes = SVG_BOX.findall(rest)
    for i, part in enumerate(SVG_BOX.split(rest)):
        for para in re.split(r"\n\s*\n", part.strip()) if part.strip() else []:
            img = IMAGE.fullmatch(para.strip())
            if img:
                flush()
                blocks.append(("image", img.group(1), img.group(2)))
            else:
                text.append(para.strip())
        if i < len(boxes):
            flush()
            blocks.append(("svg", boxes[i]))
    flush()
    post["blocks"] = blocks
    return post


def write_post(title, blocks, cat="Self", date=None, heading="", transcript="", path=None):
    """blocks: markdown/HTML chunks in order (svg_box() drawings, images, text). Returns the post path.

    path=None: new post at post_path(); if that file exists, keep everything above the body (re-import).
    path=existing post: edit in place, rewriting the whole file but keeping unmanaged front matter keys."""
    now = datetime.datetime.now().astimezone()
    date = date or now.date().isoformat()
    # explicit offset so Jekyll files it under the right day and doesn't skip it as future
    stamp = now.strftime("%H:%M:%S %z") if date == now.date().isoformat() else "12:00:00 " + now.strftime("%z")
    q = lambda s: json.dumps(s, ensure_ascii=False)  # JSON strings are valid YAML
    t = transcript.strip()
    head = None
    if path:
        out, old = path, parse_post(path)
        date_val = old["date_raw"] if old["date"] == date else f"{date} {stamp}"
        managed = ("title", "date", "categories") + (("excerpt",) if t else ())
        keep = [l for l in old["fm_lines"] if l.partition(":")[0].strip() not in managed]
    else:
        out, date_val, keep = post_path(title, date), f"{date} {stamp}", ["layout: post"]
        if os.path.exists(out):
            old = open(out, encoding="utf-8").read()
            head = old.split(BODY)[0] if BODY in old else old.split(MARK)[0]
    if head is None:
        fm = [f"title:  {q(title)}", f"date:   {date_val}", f"categories: {cat}"]
        if t:  # otherwise the home page excerpt is just the word "Transcript"
            fm.append(f"excerpt: {q(t.splitlines()[0])}")
        fm = [l for l in keep if l.startswith("layout")] + fm + [l for l in keep if not l.startswith("layout")]
        head = "---\n" + "\n".join(fm) + "\n---\n\n"
        if heading:
            head += f"# {heading}\n\n"
        if t:
            head += f"<details>\n<summary>Transcript</summary>\n\n{t}\n\n</details>\n\n"
    with open(out, "w", encoding="utf-8") as f:
        f.write(head + BODY + "\n\n" + "\n".join(blocks))
    return out


if __name__ == "__main__":
    src, title = sys.argv[1], sys.argv[2]
    cat = sys.argv[3] if len(sys.argv) > 3 else "Self"
    date = sys.argv[4] if len(sys.argv) > 4 else None
    if src.endswith(".svgz"):
        drawings = [from_write(src)]
    elif src.lower().endswith(".pdf"):
        with tempfile.TemporaryDirectory() as tmp:
            drawings = [from_scan(p) for p in pdf_pages(src, tmp)]
    else:
        drawings = [from_scan(src)]
    out = write_post(title, [svg_box(h, b) for h, b in drawings], cat, date)
    print(os.path.relpath(out), sum(b.count("<path") for _, b in drawings), "paths,", len(drawings), "drawing(s)")
