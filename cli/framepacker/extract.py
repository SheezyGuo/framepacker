import subprocess
from pathlib import Path


def extract_frames(video_path, fps=12, output_dir=None, start=0, duration=None, resize=None):
    output = Path(output_dir) if output_dir else Path.cwd() / "frames"
    output.mkdir(parents=True, exist_ok=True)

    output_pattern = str(output / "frame_%05d.png")

    filter_parts = [f"fps={fps}"]
    if resize:
        filter_parts.append(f"scale={resize}")
    vf = ",".join(filter_parts)

    cmd = ["ffmpeg"]
    if start > 0:
        cmd.extend(["-ss", str(start)])
    cmd.extend(["-i", video_path, "-vf", vf])
    if duration:
        cmd.extend(["-t", str(duration)])
    cmd.extend(["-y", output_pattern])

    subprocess.run(cmd, check=True, capture_output=True)

    frames = sorted([str(p) for p in output.glob("*.png")])
    return frames
