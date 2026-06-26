import subprocess
from pathlib import Path


def extract_frames(video_path: str, fps: int = 12, output_dir: str | None = None, start: float = 0, duration: float | None = None, resize: str | None = None) -> list[str]:
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

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed: {e.stderr}") from e

    frames = sorted([str(p) for p in output.glob("*.png")])
    return frames
