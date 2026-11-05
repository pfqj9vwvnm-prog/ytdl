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

    d = tempfile.mkdtemp()
    opts = {
        "outtmpl": f"{d}/%(id)s.%(ext)s",
        "noplaylist": True,
        "merge_output_format": "mp4",
        "quiet": True,
        "format": ("bv*[height<=1080][ext=mp4]+ba[ext=m4a]"
                   "/b[height<=1080][ext=mp4]"
                   "/b[height<=1080]/b"),
    }

    try:
        with yt_dlp.YoutubeDL(opts) as y:
            y.download([url])
    except Exception as e:
        return str(e)[:500], 400

    files = glob.glob(f"{d}/*")
    if not files:
        abort(500)
    return send_file(files[0])
