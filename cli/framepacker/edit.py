from pathlib import Path
from PIL import Image


def batch_edit(
    frames_dir: str, resize: str | None = None, crop: str | None = None,
    rotate: float | None = None, grayscale: bool = False,
    output_dir: str | None = None
) -> list[str]:
    input_path = Path(frames_dir)
    output = Path(output_dir) if output_dir else input_path / "edited"
    output.mkdir(parents=True, exist_ok=True)

    frames = sorted(input_path.glob("*.png"))
    if not frames:
        raise ValueError(f"No PNG files found in {frames_dir}")

    result_paths = []
    for fpath in frames:
        with Image.open(fpath) as img:
            if crop:
                left, upper, right, lower = map(int, crop.split(","))
                img = img.crop((left, upper, right, lower))
            if resize:
                w, h = map(int, resize.split("x"))
                img = img.resize((w, h), Image.LANCZOS)
            if rotate:
                img = img.rotate(float(rotate), expand=True)
            if grayscale:
                img = img.convert("L")

            dest = output / fpath.name
            img.save(dest)
            result_paths.append(str(dest))

    return result_paths
