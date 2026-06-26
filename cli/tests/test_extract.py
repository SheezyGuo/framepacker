import pytest
from pathlib import Path
from framepacker.extract import extract_frames


def test_extract_frames_returns_list(tmp_path):
    video = Path("tests") / "fixtures" / "test.mp4"
    if not video.exists():
        pytest.skip("test fixture not available")
    output = tmp_path / "frames"
    result = extract_frames(str(video), fps=10, output_dir=str(output))
    assert len(result) > 0
    for p in result:
        assert Path(p).exists()
