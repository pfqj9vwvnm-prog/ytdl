from flask import Flask, request, send_file, abort
import yt_dlp, tempfile, os, glob

app = Flask(__name__)
TOKEN = os.environ["TOKEN"]


@app.get("/")
def index():
    return "ok"


@app.post("/dl")
def dl():
    if request.headers.get("X-Token") != TOKEN:
        abort(403)

    url = (request.form.get("url") or "").strip()
    if not url:
        abort(400)

    q = (request.form.get("q") or "720").strip().lower()
    if q in ("audio", "mp3"):
        q = "audio"
    elif not q.isdigit():
        q = "720"

    d = tempfile.mkdtemp()
    opts = {
        "outtmpl": f"{d}/%(id)s.%(ext)s",
        "noplaylist": True,
        "merge_output_format": "mp4",
        "quiet": True,
    }

    if q == "audio":
        opts["format"] = "ba[ext=m4a]/ba"
    else:
        opts["format"] = (
            f"bv*[height<={q}][ext=mp4]+ba[ext=m4a]"
            f"/b[height<={q}][ext=mp4]"
            f"/b[height<={q}]/b"
        )

    with yt_dlp.YoutubeDL(opts) as y:
        y.download([url])

    files = glob.glob(f"{d}/*")
    if not files:
        abort(500)
    return send_file(files[0])
