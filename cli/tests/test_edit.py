import pytest
from pathlib import Path
from framepacker.edit import batch_edit


def test_batch_edit_resize(tmp_path):
    from PIL import Image
    frame_dir = tmp_path / "input"
    frame_dir.mkdir()
    img = Image.new("RGB", (100, 100), (255, 0, 0))
    img.save(frame_dir / "frame_00001.png")

    output = tmp_path / "output"
    result = batch_edit(str(frame_dir), resize="50x50", output_dir=str(output))
    assert len(result) == 1
    edited = Image.open(result[0])
    assert edited.size == (50, 50)


def test_batch_edit_grayscale(tmp_path):
    from PIL import Image
    frame_dir = tmp_path / "input"
    frame_dir.mkdir()
    img = Image.new("RGB", (100, 100), (255, 0, 0))
    img.save(frame_dir / "frame_00001.png")

    output = tmp_path / "output2"
    result = batch_edit(str(frame_dir), grayscale=True, output_dir=str(output))
    assert len(result) == 1
    edited = Image.open(result[0])
    assert edited.mode == "L"
