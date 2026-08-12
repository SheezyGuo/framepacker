import sys
import tempfile
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

sys.path.insert(0, str(Path(__file__).parent.parent))

from framepacker.extract import extract_frames
from framepacker.gif import frames_to_gif
from framepacker.sprite import frames_to_sprite
from framepacker.dedup import dedup_frames
from framepacker.removebg import remove_background
from framepacker.edit import batch_edit

app = Flask(__name__)
CORS(app)

WORKSPACE = Path(__file__).parent.parent / "workspace"
WORKSPACE.mkdir(exist_ok=True)

MAX_JOBS = 10


def cleanup_old_jobs(keep=MAX_JOBS):
    jobs = sorted(
        (p for p in WORKSPACE.iterdir() if p.is_dir() and p.name.startswith("job_")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for old in jobs[keep:]:
        try:
            import shutil

            shutil.rmtree(old)
        except OSError:
            pass


@app.route("/api/cleanup", methods=["POST"])
def api_cleanup():
    force = request.json.get("force", False) if request.is_json else False
    if force:
        for p in WORKSPACE.iterdir():
            if p.is_dir() and p.name.startswith("job_"):
                import shutil

                shutil.rmtree(p, ignore_errors=True)
    else:
        cleanup_old_jobs()
    jobs = sorted((p for p in WORKSPACE.iterdir() if p.is_dir() and p.name.startswith("job_")), key=lambda p: p.stat().st_mtime, reverse=True)
    return jsonify({"kept": len(jobs), "workspace": str(WORKSPACE)})


@app.route("/api/file")
def api_file():
    path = request.args.get("path", "")
    target = (Path(path)).resolve()
    if not str(target).startswith(str(WORKSPACE.resolve())) or not target.is_file():
        return jsonify({"error": "forbidden"}), 403
    return send_file(str(target))


@app.route("/api/extract", methods=["POST"])
def api_extract():
    file = request.files.get("file")
    if file is None:
        return jsonify({"error": "no file uploaded"}), 400

    job = WORKSPACE / f"job_{int(time.time() * 1000)}"
    job.mkdir(exist_ok=True)
    video_path = job / file.filename
    file.save(str(video_path))
    output_dir = job / "frames"

    data = request.form
    result = extract_frames(
        video_path=str(video_path),
        fps=int(data.get("fps", 12)),
        output_dir=str(output_dir),
        start=float(data.get("start", 0)),
        duration=float(data["duration"]) if data.get("duration") else None,
        resize=data.get("resize") or None,
    )
    cleanup_old_jobs()
    return jsonify({"frames": result, "count": len(result), "job": str(job)})


@app.route("/api/gif", methods=["POST"])
def api_gif():
    data = request.json
    frames = sorted([str(p) for p in Path(data["frames_dir"]).glob("*.png")])
    result = frames_to_gif(frames, output=data["output"], fps=data.get("fps", 10), resize=data.get("resize"), loop=data.get("loop", 0))
    return jsonify({"output": result})


@app.route("/api/sprite", methods=["POST"])
def api_sprite():
    data = request.json
    frames = sorted([str(p) for p in Path(data["frames_dir"]).glob("*.png")])
    result = frames_to_sprite(frames, output=data["output"], cols=data.get("cols", 8), padding=data.get("padding", 2), resize=data.get("resize"))
    return jsonify({"output": result})


@app.route("/api/dedup", methods=["POST"])
def api_dedup():
    data = request.json
    result = dedup_frames(frames_dir=data["frames_dir"], threshold=data.get("threshold", 0.92), output_dir=data.get("output"))
    return jsonify({"frames": result, "count": len(result)})


@app.route("/api/detect-dupes", methods=["POST"])
def api_detect_dupes():
    import cv2
    import numpy as np

    data = request.json
    threshold = float(data.get("threshold", 0.92))
    frames_dir = Path(data["frames_dir"])
    frames = sorted(frames_dir.glob("*.png"))
    if not frames:
        return jsonify({"error": "no frames found"}), 400

    from framepacker.dedup import _pixel_similarity

    prev_img = None
    dupes = []
    for fpath in frames:
        img = cv2.imread(str(fpath))
        if img is None:
            continue
        if prev_img is not None and _pixel_similarity(prev_img, img) >= threshold:
            dupes.append(str(fpath))
        else:
            prev_img = img
    return jsonify({"dupes": dupes, "count": len(dupes)})


@app.route("/api/remove-bg", methods=["POST"])
def api_remove_bg():
    data = request.json
    result = remove_background(frames_dir=data["frames_dir"], output_dir=data.get("output"))
    return jsonify({"frames": result, "count": len(result)})


@app.route("/api/edit", methods=["POST"])
def api_edit():
    data = request.json
    result = batch_edit(frames_dir=data["frames_dir"], resize=data.get("resize"), crop=data.get("crop"), rotate=data.get("rotate"), grayscale=data.get("grayscale", False), background=data.get("background"), output_dir=data.get("output"))
    return jsonify({"frames": result, "count": len(result)})


@app.route("/api/export-zip", methods=["POST"])
def api_export_zip():
    import io
    import zipfile

    data = request.json
    frames_dir = Path(data["frames_dir"])
    frames = sorted(frames_dir.glob("*.png"))
    if not frames:
        return jsonify({"error": "no frames found"}), 400

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in frames:
            zf.write(str(fpath), arcname=fpath.name)
    buf.seek(0)

    name = data.get("name", "frames.zip")
    return send_file(buf, mimetype="application/zip", as_attachment=True, download_name=name)


@app.route("/api/detect-jumps", methods=["POST"])
def api_detect_jumps():
    import cv2

    data = request.json
    threshold = float(data.get("threshold", 0.4))
    frames_dir = Path(data["frames_dir"])
    frames = sorted(frames_dir.glob("*.png"))
    if not frames:
        return jsonify({"error": "no frames found"}), 400

    from framepacker.dedup import _pixel_similarity

    prev_img = None
    jumps = []
    for fpath in frames:
        img = cv2.imread(str(fpath))
        if img is None:
            continue
        if prev_img is not None and _pixel_similarity(prev_img, img) < threshold:
            jumps.append(str(fpath))
        prev_img = img
    return jsonify({"jumps": jumps, "count": len(jumps)})


@app.route("/api/import-gif", methods=["POST"])
def api_import_gif():
    from PIL import Image, ImageSequence

    file = request.files.get("file")
    if file is None:
        return jsonify({"error": "no file uploaded"}), 400

    job = WORKSPACE / f"job_{int(time.time() * 1000)}_gif"
    output_dir = job / "frames"
    output_dir.mkdir(parents=True, exist_ok=True)

    src = job / file.filename
    file.save(str(src))

    result = []
    with Image.open(str(src)) as im:
        for i, frame in enumerate(ImageSequence.Iterator(im)):
            dest = output_dir / f"frame_{i + 1:05d}.png"
            frame.convert("RGBA").save(str(dest))
            result.append(str(dest))

    cleanup_old_jobs()
    return jsonify({"frames": result, "count": len(result), "job": str(job)})


@app.route("/api/save-frame", methods=["POST"])
def api_save_frame():
    import base64

    data = request.json
    path = data.get("path", "")
    image_data = data.get("data", "")
    target = Path(path).resolve()
    if not str(target).startswith(str(WORKSPACE.resolve())):
        return jsonify({"error": "forbidden"}), 403

    if image_data.startswith("data:"):
        _, encoded = image_data.split(",", 1)
    else:
        encoded = image_data
    raw = base64.b64decode(encoded)
    target.write_bytes(raw)
    return jsonify({"saved": str(target)})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080, debug=True)
