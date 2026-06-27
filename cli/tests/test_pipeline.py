import pytest
from pathlib import Path
from framepacker.pipeline import run_pipeline


def test_pipeline_runs(tmp_path):
    from PIL import Image
    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    for i in range(2):
        img = Image.new("RGB", (100, 100), (255, 0, 0))
        img.save(frames_dir / f"frame_{i:05d}.png")

    config = tmp_path / "pipeline.yaml"
    config.write_text(f"""\
steps:
  - command: edit
    args:
      frames_dir: {frames_dir}
      resize: 50x50
      output: {tmp_path / "out"}
""")
    result = run_pipeline(str(config))
    assert result == 0
