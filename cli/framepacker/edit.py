from pathlib import Path
from PIL import Image


def batch_edit(
    frames_dir: str, resize: str | None = None, crop: str | None = None,
    rotate: float | None = None, grayscale: bool = False,
    background: str | None = None, output_dir: str | None = None
) -> list[str]:
    input_path = Path(frames_dir)
    output = Path(output_dir) if output_dir else input_path / "edited"
    output.mkdir(parents=True, exist_ok=True)

    frames = sorted(input_path.glob("*.png"))
    if not frames:
        raise ValueError(f"No PNG files found in {frames_dir}")

    bg_color = None
    if background:
        bg_color = _parse_color(background)

    result_paths = []
    for fpath in frames:
        with Image.open(fpath) as img:
            if crop:
                left, upper, right, lower = map(int, crop.split(","))
                img = img.crop((left, upper, right, lower))
            if resize:
                w, h = map(int, resize.split("x"))
                img = img.resize((w, h), Image.LANCZOS)
            if bg_color is not None:
                img = _fill_background(img, bg_color)
            if rotate:
                img = img.rotate(float(rotate), expand=True)
            if grayscale:
                img = img.convert("L")

            dest = output / fpath.name
            img.save(dest)
            result_paths.append(str(dest))

    return result_paths


def _parse_color(text: str) -> tuple:
    text = text.strip().lstrip("#")
    if len(text) == 6:
        r, g, b = int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)
        return (r, g, b, 255)
    if len(text) == 8:
        r, g, b, a = int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16), int(text[6:8], 16)
        return (r, g, b, a)
    raise ValueError(f"Invalid color: {background}")


def _fill_background(img: Image.Image, bg: tuple) -> Image.Image:
    if img.mode == "RGBA":
        base = Image.new("RGBA", img.size, bg)
        img = Image.alpha_composite(base, img)
        return img
    if img.mode == "L":
        return img.convert("RGB")
    return img
