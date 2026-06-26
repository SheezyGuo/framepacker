import cv2
import numpy as np
from pathlib import Path


def _histogram_similarity(img1, img2):
    h1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
    h2 = cv2.calcHist([img2], [0], None, [256], [0, 256])
    return cv2.compareHist(h1, h2, cv2.HISTCMP_CORREL)


def dedup_frames(
    frames_dir: str, threshold: float = 0.92, output_dir: str | None = None
) -> list[str]:
    input_path = Path(frames_dir)
    output = Path(output_dir) if output_dir else input_path
    output.mkdir(parents=True, exist_ok=True)

    frames = sorted(input_path.glob("*.png"))
    if not frames:
        raise ValueError(f"No PNG files found in {frames_dir}")

    kept = []
    prev_img = None

    for fpath in frames:
        img = cv2.imread(str(fpath))
        if img is None:
            continue
        if prev_img is None or _histogram_similarity(prev_img, img) < threshold:
            dest = output / fpath.name
            cv2.imwrite(str(dest), img)
            kept.append(str(dest))
            prev_img = img

    return kept
