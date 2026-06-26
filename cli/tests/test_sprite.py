import pytest
from pathlib import Path
from framepacker.sprite import frames_to_sprite


def test_frames_to_sprite_creates_file(tmp_path):
    from PIL import Image
    frame_dir = tmp_path / "frames"
    frame_dir.mkdir()
    for i in range(4):
        img = Image.new("RGB", (50, 50), (255, 0, 0))
        img.save(frame_dir / f"frame_{i:05d}.png")

    frames = sorted([str(p) for p in frame_dir.glob("*.png")])
    output = str(tmp_path / "sprite.png")
    result = frames_to_sprite(frames, output, cols=2, padding=1)
    assert Path(result).exists()
    img = Image.open(result)
    assert img.width == 50 * 2 + 1  # 2 cols + 1px padding = 101
    assert img.height == 50 * 2 + 1  # 2 rows + 1px padding = 101
