import sys
from pathlib import Path
from flask import Flask, request, jsonify
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


@app.route("/api/extract", methods=["POST"])
def api_extract():
    data = request.json
    result = extract_frames(
        video_path=data["video_path"],
        fps=data.get("fps", 12),
        output_dir=data.get("output", "./frames"),
        start=data.get("start", 0),
        duration=data.get("duration"),
        resize=data.get("resize"),
    )
    return jsonify({"frames": result, "count": len(result)})


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


@app.route("/api/remove-bg", methods=["POST"])
def api_remove_bg():
    data = request.json
    result = remove_background(frames_dir=data["frames_dir"], output_dir=data.get("output"))
    return jsonify({"frames": result, "count": len(result)})


@app.route("/api/edit", methods=["POST"])
def api_edit():
    data = request.json
    result = batch_edit(frames_dir=data["frames_dir"], resize=data.get("resize"), crop=data.get("crop"), rotate=data.get("rotate"), grayscale=data.get("grayscale", False), output_dir=data.get("output"))
    return jsonify({"frames": result, "count": len(result)})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080, debug=True)
