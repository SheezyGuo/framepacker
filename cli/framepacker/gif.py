from PIL import Image


def frames_to_gif(
    frame_paths: list[str], output: str, fps: int = 10,
    resize: str | None = None, loop: int = 0
) -> str:
    images = []
    for path in frame_paths:
        img = Image.open(path)
        if img.mode != "P":
            img = img.convert("P", palette=Image.Palette.ADAPTIVE)
        if resize:
            w, h = map(int, resize.split("x"))
            img = img.resize((w, h), Image.LANCZOS)
        images.append(img)

    if not images:
        raise ValueError("No frames to encode")

    duration = int(1000 / fps)
    images[0].save(
        output,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=loop,
        optimize=True,
    )
    return output
