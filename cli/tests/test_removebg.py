import pytest
from pathlib import Path
from framepacker.removebg import remove_background


def test_remove_bg_creates_files(tmp_path):
    from PIL import Image
    frame_dir = tmp_path / "input"
    frame_dir.mkdir()
    img = Image.new("RGB", (100, 100), (255, 0, 0))
    img.save(frame_dir / "frame_00001.png")

    output = tmp_path / "output"
    result = remove_background(str(frame_dir), output_dir=str(output))
    assert len(result) == 1
    assert Path(result[0]).exists()
    from PIL import Image as PILImage
    loaded = PILImage.open(result[0])
    assert loaded.mode == "RGBA"
