from PIL import Image


def frames_to_sprite(
    frame_paths: list[str], output: str, cols: int = 8,
    padding: int = 2, resize: str | None = None
) -> str:
    images = []
    for path in frame_paths:
        img = Image.open(path)
        if resize:
            w, h = map(int, resize.split("x"))
            img = img.resize((w, h), Image.LANCZOS)
        images.append(img)

    if not images:
        raise ValueError("No frames provided")

    frame_w, frame_h = images[0].size
    total = len(images)
    rows = (total + cols - 1) // cols

    sheet_w = cols * frame_w + (cols - 1) * padding
    sheet_h = rows * frame_h + (rows - 1) * padding

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

    for idx, img in enumerate(images):
        x = (idx % cols) * (frame_w + padding)
        y = (idx // cols) * (frame_h + padding)
        if img.mode == "RGBA":
            sheet.paste(img, (x, y), img)
        else:
            sheet.paste(img, (x, y))

    sheet.save(output)
    return output
