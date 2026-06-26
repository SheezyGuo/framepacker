import pytest
from pathlib import Path
from framepacker.dedup import dedup_frames


def test_dedup_removes_identical_frames(tmp_path):
    from PIL import Image
    frame_dir = tmp_path / "input"
    frame_dir.mkdir()
    for i in range(3):
        img = Image.new("RGB", (50, 50), (255, 0, 0))
        img.save(frame_dir / f"frame_{i:05d}.png")

    output = tmp_path / "output"
    result = dedup_frames(str(frame_dir), threshold=0.95, output_dir=str(output))
    assert len(result) == 1  # All identical → all deduped to 1
    assert Path(result[0]).exists()
