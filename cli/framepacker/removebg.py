from pathlib import Path
from rembg import remove, new_session
from PIL import Image


_session = None


def _get_session():
    global _session
    if _session is None:
        _session = new_session("u2netp")
    return _session


def remove_background(frames_dir: str, output_dir: str | None = None) -> list[str]:
    input_path = Path(frames_dir)
    output = Path(output_dir) if output_dir else input_path / "no_bg"
    output.mkdir(parents=True, exist_ok=True)

    frames = sorted(input_path.glob("*.png"))
    if not frames:
        raise ValueError(f"No PNG files found in {frames_dir}")

    session = _get_session()
    result_paths = []
    for fpath in frames:
        with Image.open(fpath) as img:
            out = remove(img, session=session)
            dest = output / fpath.name
            out.save(dest)
            result_paths.append(str(dest))

    return result_paths
