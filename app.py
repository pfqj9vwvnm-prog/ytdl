from flask import Flask, request, send_file, abort
import yt_dlp, tempfile, os, glob

app = Flask(__name__)
TOKEN = os.environ["TOKEN"]

@app.post("/dl")
def dl():
    if request.headers.get("X-Token") != TOKEN:
        abort(403)
    url = request.form["url"]
    q = request.form.get("q", "720")
    d = tempfile.mkdtemp()
    opts = {"outtmpl": f"{d}/%(id)s.%(ext)s",
            "noplaylist": True, "merge_output_format": "mp4"}
    if q == "audio":
        opts["format"] = "ba[ext=m4a]/ba"
    else:
        opts["format"] = (f"bv*[height<={q}][ext=mp4]+ba[ext=m4a]"
                          f"/b[height<={q}][ext=mp4]/b[height<={q}]")
    with yt_dlp.YoutubeDL(opts) as y:
        y.download([url])
    return send_file(glob.glob(f"{d}/*")[0])
