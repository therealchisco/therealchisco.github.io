#!/usr/bin/env python3
"""Drag-and-drop UI for turning scans / Write exports into blog posts.

usage: python3 scripts/post_studio.py [port]   (default 4720, opens the browser)

Same pipeline as svgz_to_post.py. Run `bundle exec jekyll serve --port 4719`
alongside it to get a working "view post" link.
"""
import datetime, http.server, json, os, re, shutil, sys, tempfile, uuid, urllib.parse, webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import svgz_to_post as core

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4720
JEKYLL = "http://127.0.0.1:4719"
TMP = tempfile.mkdtemp(prefix="post-studio-")
scans = {}  # id -> {"path", "kind", "params", "height", "body"} | {"kind": "raw", "html"}  ponytail: in memory, lost on restart
TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp"}


def trace(scan):
    if scan["kind"] == "write":
        scan["height"], scan["body"] = core.from_write(scan["path"])
    else:
        scan["height"], scan["body"] = core.from_scan(scan["path"], **scan["params"])


def photo(scan):
    if "jpeg" not in scan:
        scan["jpeg"] = core.photo_jpeg(scan["path"])
    return scan["jpeg"]


def view(sid):
    s = scans[sid]
    return {"id": sid, "name": s["name"], "kind": s["kind"], "params": s["params"],
            "height": s["height"], "body": s["body"]}


class Handler(http.server.BaseHTTPRequestHandler):
    def send(self, code, data, ctype="application/json"):
        raw = data if isinstance(data, bytes) else json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def body(self):
        return self.rfile.read(int(self.headers.get("Content-Length", 0)))

    def do_GET(self):
        path = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
        if path == "/":
            return self.send(200, open(os.path.join(HERE, "post_studio.html"), "rb").read(), "text/html; charset=utf-8")
        m = re.fullmatch(r"/api/scan/([0-9a-f]+)/photo", path)
        if m and m.group(1) in scans and scans[m.group(1)]["kind"] in ("scan", "photo"):
            return self.send(200, photo(scans[m.group(1)]), "image/jpeg")
        if path == "/api/posts":
            return self.send(200, [{"file": f, "title": core.parse_post(os.path.join(core.POSTS, f))["title"]}
                                   for f in sorted(os.listdir(core.POSTS), reverse=True) if f.endswith(".md")])
        m = re.fullmatch(r"/api/posts/([\w.-]+\.md)", path)
        if m and os.path.isfile(os.path.join(core.POSTS, m.group(1))):
            return self.send(200, self.load_post(m.group(1)))
        if path.startswith("/assets/"):  # existing post images, for previews
            f = os.path.realpath(os.path.join(core.ROOT, path.lstrip("/")))
            if f.startswith(os.path.join(core.ROOT, "assets") + os.sep) and os.path.isfile(f):
                return self.send(200, open(f, "rb").read(), TYPES.get(os.path.splitext(f)[1].lower(), "application/octet-stream"))
        self.send(404, {"error": "not found"})

    def load_post(self, name):
        post = core.parse_post(os.path.join(core.POSTS, name))
        blocks = []
        for b in post["blocks"]:
            if b[0] == "svg":
                sid = uuid.uuid4().hex[:12]
                scans[sid] = {"kind": "raw", "html": b[1], "name": f"Drawing {sum(x['kind'] == 'raw' for x in blocks) + 1}", "params": {}}
                blocks.append({"id": sid, "kind": "raw", "name": scans[sid]["name"], "html": b[1]})
            elif b[0] == "image":
                blocks.append({"kind": "image", "alt": b[1], "url": b[2]})
            else:
                blocks.append({"kind": "text", "text": b[1]})
        return {"file": name, "title": post["title"], "date": post["date"], "category": post["category"],
                "heading": post["heading"], "transcript": post["transcript"], "blocks": blocks}

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        try:
            if url.path == "/api/scan":
                return self.send(200, self.add_scan(url))
            m = re.fullmatch(r"/api/scan/([0-9a-f]+)", url.path)
            if m and m.group(1) in scans:
                s = scans[m.group(1)]
                s["params"] = {k: float(v) for k, v in json.loads(self.body()).items() if k in s["params"]}
                trace(s)
                return self.send(200, view(m.group(1)))
            if url.path == "/api/post":
                return self.create_post(json.loads(self.body()))
            self.send(404, {"error": "not found"})
        except Exception as e:  # surface pipeline errors (bad file, potrace missing) in the UI
            self.send(500, {"error": f"{type(e).__name__}: {e}"})

    def add_scan(self, url):
        """?as=scan traces the upload; ?as=photo keeps it as an image (no tracing)."""
        q = urllib.parse.parse_qs(url.query)
        name = os.path.basename(q.get("name", ["scan"])[0])
        as_photo = q.get("as", ["scan"])[0] == "photo"
        ext = os.path.splitext(name)[1].lower()
        if ext not in (".svgz", ".pdf", ".png", ".jpg", ".jpeg", ".heic"):
            raise ValueError(f"unsupported file type {ext or '(none)'}")
        if as_photo and ext == ".svgz":
            raise ValueError("Write .svgz exports are drawings, add them as scans")
        d = tempfile.mkdtemp(dir=TMP)
        src = os.path.join(d, "upload" + ext)
        open(src, "wb").write(self.body())
        if ext == ".svgz":
            pages, kind = [src], "write"
        elif ext == ".pdf":
            pages, kind = core.pdf_pages(src, d), "scan"
        else:
            pages, kind = [src], "scan"
        if as_photo:
            kind = "photo"
        out = []
        for n, p in enumerate(pages):
            sid = uuid.uuid4().hex[:12]
            label = f"{name} (page {n + 1})" if len(pages) > 1 else name
            params = {"threshold": 0.80, "specks": 12, "trim": 1.0} if kind == "scan" else {}
            scans[sid] = {"name": label, "path": p, "kind": kind, "params": params}
            if kind == "photo":
                photo(scans[sid])  # validates the file now, so a bad upload fails at drop time
                out.append({"id": sid, "name": label, "kind": kind})
            else:
                trace(scans[sid])
                out.append(view(sid))
        return out

    def create_post(self, req):
        """req["blocks"] in post order: {"type": "scan", "id", "alt"} (new upload, scan or photo) | {"type": "raw", "id"}
        (drawing loaded from an existing post) | {"type": "image", "url", "alt"} | {"type": "text", "text"}.
        req["file"]: edit that existing post in place instead of creating one."""
        title = req.get("title", "").strip()
        ok = {"scan": lambda b: b.get("id") in scans, "raw": lambda b: b.get("id") in scans,
              "image": lambda b: b.get("url"), "text": lambda b: b.get("text", "").strip()}
        blocks = [b for b in req.get("blocks", []) if b.get("type") in ok and ok[b["type"]](b)]
        if not title or not blocks:
            return self.send(400, {"error": "needs a title and at least one block"})
        date = req.get("date") or datetime.date.today().isoformat()
        edit = req.get("file")
        if edit:
            if not re.fullmatch(r"[\w.-]+\.md", edit) or not os.path.isfile(os.path.join(core.POSTS, edit)):
                return self.send(400, {"error": f"no such post {edit}"})
            path = os.path.join(core.POSTS, edit)
        else:
            path = core.post_path(title, date)
            if os.path.exists(path) and not req.get("overwrite"):
                return self.send(409, {"exists": os.path.relpath(path, core.ROOT)})
        pdir, purl = core.photo_dir(path)
        taken = [int(f[:2]) for f in os.listdir(pdir) if f[:2].isdigit()] if os.path.isdir(pdir) else []
        n, chunks, new = max(taken, default=0), [], 0
        clean_alt = lambda a: (a or "").replace("]", "").replace("\n", " ").strip()
        for b in blocks:
            if b["type"] == "text":
                chunks.append(b["text"].strip() + "\n")
            elif b["type"] == "image":
                chunks.append(f"![{clean_alt(b.get('alt'))}]({b['url']})\n")
            elif b["type"] == "raw":
                chunks.append(scans[b["id"]]["html"] + "\n")
            elif scans[b["id"]]["kind"] == "photo":
                n, new = n + 1, new + 1
                os.makedirs(pdir, exist_ok=True)
                open(f"{pdir}/{n:02d}.jpg", "wb").write(photo(scans[b["id"]]))
                chunks.append(f"![{clean_alt(b.get('alt'))}]({purl}/{n:02d}.jpg)\n")
            else:
                s = scans[b["id"]]
                chunks.append(core.svg_box(s["height"], s["body"]))
        out = core.write_post(title, chunks, cat=req.get("category") or "Self", date=date,
                              heading=req.get("heading", "").strip(), transcript=req.get("transcript", ""),
                              path=path if edit else None)
        # drop photos this post no longer references (removed blocks, or an overwritten re-create)
        if os.path.isdir(pdir):
            text = open(out, encoding="utf-8").read()
            for f in os.listdir(pdir):
                if f"{purl}/{f}" not in text:
                    os.remove(os.path.join(pdir, f))
            if not os.listdir(pdir):
                os.rmdir(pdir)
        y, m, d = date.split("-")
        cat = (req.get("category") or "Self").split()[0].lower()
        slug = os.path.basename(out)[11:-3]
        self.send(200, {"path": os.path.relpath(out, core.ROOT), "file": os.path.basename(out), "photos": new,
                        "url": f"{JEKYLL}/{cat}/{y}/{m}/{d}/{slug}.html"})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Post studio on http://127.0.0.1:{PORT}  (ctrl-c to stop)")
    webbrowser.open(f"http://127.0.0.1:{PORT}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
