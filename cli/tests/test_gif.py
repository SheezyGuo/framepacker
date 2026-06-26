import pytest
from pathlib import Path
from framepacker.gif import frames_to_gif


def test_frames_to_gif_creates_file(tmp_path):
    from PIL import Image
    frame_dir = tmp_path / "frames"
    frame_dir.mkdir()
    for i in range(3):
        img = Image.new("RGB", (100, 100), (255, 0, 0))
        img.save(frame_dir / f"frame_{i:05d}.png")

    output = str(tmp_path / "out.gif")
    frames = sorted([str(p) for p in frame_dir.glob("*.png")])
    result = frames_to_gif(frames, output, fps=10)
    assert Path(result).exists()
    assert Path(result).stat().st_size > 0
