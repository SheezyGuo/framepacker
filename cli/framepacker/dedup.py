import cv2
import numpy as np
from pathlib import Path


def _histogram_similarity(img1, img2):
    h1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
    h2 = cv2.calcHist([img2], [0], None, [256], [0, 256])
    return cv2.compareHist(h1, h2, cv2.HISTCMP_CORREL)


def _pixel_similarity(img1, img2, size=64):
    """像素级相似度:缩放后逐像素平均绝对差, 0-1 区间, 区分度远好于直方图"""
    a = cv2.resize(img1, (size, size))
    b = cv2.resize(img2, (size, size))
    diff = cv2.absdiff(a, b).astype(np.float32)
    mae = diff.mean() / 255.0
    return 1.0 - mae


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
        if prev_img is None or _pixel_similarity(prev_img, img) < threshold:
            dest = output / fpath.name
            cv2.imwrite(str(dest), img)
            kept.append(str(dest))
            prev_img = img

    return kept
