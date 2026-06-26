# FramePacker Local Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an offline-capable Python CLI + Vue 3 frontend for video→frames/GIF/sprite-sheet processing.

**Architecture:** Python CLI (click + FFmpeg + Pillow) handles all video/image processing; Vue 3 frontend provides GUI. CLI can run standalone or be called from the frontend. Pipeline YAML enables multi-step automation.

**Tech Stack:** Python 3.10+, click, Pillow, opencv-python, rembg, numpy, FFmpeg (system dep); Vue 3 + Vite + Vue Router + Pinia + fabric.js

## Global Constraints

- All core processing must work fully offline (no cloud API calls)
- rembg downloads model on first run, then caches locally — this is acceptable
- FFmpeg must be available in PATH (documented as prerequisite)
- CLI entry point: `fp <command> [args]`

---

### Task 1: Python CLI Scaffolding

**Files:**
- Create: `cli/pyproject.toml`
- Create: `cli/framepacker/__init__.py`
- Create: `cli/framepacker/cli.py`
- Create: `cli/requirements-dev.txt`

**Interfaces:**
- Consumes: nothing
- Produces: `cli/framepacker/cli.py` defines `cli` click group with `--version`; all commands will be subcommands of this group

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "framepacker"
version = "0.1.0"
description = "Video to frames/GIF/sprite-sheet offline tool"
requires-python = ">=3.10"
dependencies = [
    "click>=8.0",
    "Pillow>=10.0",
    "numpy>=1.24",
    "opencv-python-headless>=4.8",
    "rembg>=0.4.0",
    "PyYAML>=6.0",
]

[project.scripts]
fp = "framepacker.cli:cli"
```

- [ ] **Step 2: Create __init__.py**

```python
```

- [ ] **Step 3: Create cli.py skeleton**

```python
import click


@click.group()
@click.version_option("0.1.0")
def cli():
    """FramePacker - Video frame extraction & animation tools."""
    pass
```

- [ ] **Step 4: Create requirements-dev.txt**

```
pytest>=7.0
pytest-cov>=4.0
```

- [ ] **Step 5: Verify CLI runs**

Run: `pip install -e cli/`
Run: `fp --help`
Expected: Shows help text with commands list (currently empty)

- [ ] **Step 6: Commit**

```bash
git add cli/pyproject.toml cli/framepacker/__init__.py cli/framepacker/cli.py cli/requirements-dev.txt
git commit -m "feat: add python cli scaffolding with click"
```

---

### Task 2: Extract Command (video → frames)

**Files:**
- Create: `cli/framepacker/extract.py`
- Create: `cli/tests/test_extract.py`
- Modify: `cli/framepacker/cli.py` (register extract command)

**Interfaces:**
- Consumes: nothing standalone (a video file on disk)
- Produces: `extract.extract_frames(video_path: str, fps: int, output_dir: str, start: float, duration: float, resize: str) -> list[str]` — returns list of saved frame paths
- Registers `fp extract <video>` subcommand on the `cli` group

- [ ] **Step 1: Write failing test**

Create `cli/tests/test_extract.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest cli/tests/test_extract.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'framepacker.extract'`

- [ ] **Step 3: Write minimal extract.py**

```python
import subprocess
import os
from pathlib import Path


def extract_frames(video_path, fps=12, output_dir=None, start=0, duration=None, resize=None):
    output = Path(output_dir) if output_dir else Path.cwd() / "frames"
    output.mkdir(parents=True, exist_ok=True)

    output_pattern = str(output / "frame_%05d.png")

    cmd = ["ffmpeg", "-i", video_path, "-vf", f"fps={fps}"]

    if start > 0:
        cmd = ["ffmpeg", "-ss", str(start), "-i", video_path, "-vf", f"fps={fps}"]
    if duration:
        cmd.extend(["-t", str(duration)])
    if resize:
        cmd.extend(["-vf", f"fps={fps},scale={resize}"])

    cmd.extend(["-y", output_pattern])

    subprocess.run(cmd, check=True, capture_output=True)

    frames = sorted([str(p) for p in output.glob("*.png")])
    return frames
```

- [ ] **Step 4: Register extract command in cli.py**

```python
from .extract import extract_frames


@cli.command()
@click.argument("video", type=click.Path(exists=True))
@click.option("--fps", default=12, help="Frames per second")
@click.option("--output", "-o", default="./frames", help="Output directory")
@click.option("--start", default=0.0, help="Start time in seconds")
@click.option("--duration", default=None, type=float, help="Duration in seconds")
@click.option("--resize", default=None, help="Resize (e.g. 512x512)")
def extract(video, fps, output, start, duration, resize):
    """Extract frames from a video file."""
    result = extract_frames(video, fps, output, start, duration, resize)
    click.echo(f"Extracted {len(result)} frames to {output}")
```

- [ ] **Step 5: Create test fixture and verify**

Run: `ffmpeg -f lavfi -i color=c=black:s=320x240:d=2 -frames:v 20 cli/tests/fixtures/test.mp4 -y 2>$null`
Run: `pytest cli/tests/test_extract.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add cli/framepacker/extract.py cli/tests/test_extract.py cli/framepacker/cli.py
git commit -m "feat: add extract command (video to frames)"
```

---

### Task 3: GIF Command (frames → GIF)

**Files:**
- Create: `cli/framepacker/gif.py`
- Create: `cli/tests/test_gif.py`
- Modify: `cli/framepacker/cli.py`

**Interfaces:**
- Consumes: `gif.frames_to_gif(frame_paths: list[str], output: str, fps: int, resize: str, loop: int) -> str` — returns output path
- Produces: `fp gif` CLI subcommand

- [ ] **Step 1: Write failing test**

```python
import pytest
from pathlib import Path
from framepacker.gif import frames_to_gif


def test_frames_to_gif_creates_file(tmp_path):
    from PIL import Image
    frame_dir = tmp_path / "frames"
    frame_dir.mkdir()
    for i in range(3):
        img = Image.new("RGB", (100, 100), (255, 0, 0))
        img.save(frame_dir / f"frame_{i:05d}.png")

    output = str(tmp_path / "out.gif")
    frames = sorted([str(p) for p in frame_dir.glob("*.png")])
    result = frames_to_gif(frames, output, fps=10)
    assert Path(result).exists()
    assert Path(result).stat().st_size > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest cli/tests/test_gif.py -v`
Expected: FAIL

- [ ] **Step 3: Write gif.py**

```python
from PIL import Image


def frames_to_gif(frame_paths, output, fps=10, resize=None, loop=0):
    images = []
    for path in frame_paths:
        img = Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE)
        if resize:
            w, h = map(int, resize.split("x"))
            img = img.resize((w, h), Image.LANCZOS)
        images.append(img)

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
```

- [ ] **Step 4: Register gif command in cli.py**

```python
from .gif import frames_to_gif


@cli.command()
@click.argument("frames_dir", type=click.Path(exists=True))
@click.option("--fps", default=10, help="Output FPS")
@click.option("--output", "-o", default="output.gif", help="Output GIF path")
@click.option("--resize", default=None, help="Resize (e.g. 512x512)")
@click.option("--loop", default=0, help="Loop count (0 = infinite)")
def gif(frames_dir, fps, output, resize, loop):
    """Create GIF from a directory of frames."""
    from pathlib import Path
    frames = sorted([str(p) for p in Path(frames_dir).glob("*.png")])
    if not frames:
        click.echo("No PNG frames found", err=True)
        return
    result = frames_to_gif(frames, output, fps, resize, loop)
    click.echo(f"GIF saved to {result}")
```

- [ ] **Step 5: Run tests**

Run: `pytest cli/tests/test_gif.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add cli/framepacker/gif.py cli/tests/test_gif.py cli/framepacker/cli.py
git commit -m "feat: add gif command (frames to animated GIF)"
```

---

### Task 4: Sprite Command (frames → sprite sheet)

**Files:**
- Create: `cli/framepacker/sprite.py`
- Create: `cli/tests/test_sprite.py`
- Modify: `cli/framepacker/cli.py`

**Interfaces:**
- Consumes: `sprite.frames_to_sprite(frame_paths: list[str], output: str, cols: int, padding: int, resize: str) -> str`
- Produces: `fp sprite` CLI subcommand

- [ ] **Step 1: Write failing test**

```python
import pytest
from pathlib import Path
from framepacker.sprite import frames_to_sprite


def test_frames_to_sprite_creates_file(tmp_path):
    from PIL import Image
    frame_dir = tmp_path / "frames"
    frame_dir.mkdir()
    for i in range(4):
        img = Image.new("RGB", (50, 50), (255, 0, 0))
        img.save(frame_dir / f"frame_{i:05d}.png")

    frames = sorted([str(p) for p in frame_dir.glob("*.png")])
    output = str(tmp_path / "sprite.png")
    result = frames_to_sprite(frames, output, cols=2, padding=1)
    assert Path(result).exists()
    img = Image.open(result)
    assert img.width == 50 * 2 + 1  # 2 cols + 1px padding
    assert img.height == 50 * 2 + 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest cli/tests/test_sprite.py -v`
Expected: FAIL

- [ ] **Step 3: Write sprite.py**

```python
from PIL import Image


def frames_to_sprite(frame_paths, output, cols=8, padding=2, resize=None):
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
```

- [ ] **Step 4: Register sprite command in cli.py**

```python
from .sprite import frames_to_sprite


@cli.command()
@click.argument("frames_dir", type=click.Path(exists=True))
@click.option("--cols", default=8, help="Number of columns")
@click.option("--output", "-o", default="sprite.png", help="Output image path")
@click.option("--padding", default=2, help="Padding between frames in pixels")
@click.option("--resize", default=None, help="Resize each frame (e.g. 512x512)")
def sprite(frames_dir, cols, output, padding, resize):
    """Create a sprite sheet from a directory of frames."""
    from pathlib import Path
    frames = sorted([str(p) for p in Path(frames_dir).glob("*.png")])
    if not frames:
        click.echo("No PNG frames found", err=True)
        return
    result = frames_to_sprite(frames, output, cols, padding, resize)
    click.echo(f"Sprite sheet saved to {result}")
```

- [ ] **Step 5: Run tests**

Run: `pytest cli/tests/test_sprite.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add cli/framepacker/sprite.py cli/tests/test_sprite.py cli/framepacker/cli.py
git commit -m "feat: add sprite command (frames to sprite sheet)"
```

---

### Task 5: Dedup Command (remove similar frames)

**Files:**
- Create: `cli/framepacker/dedup.py`
- Create: `cli/tests/test_dedup.py`
- Modify: `cli/framepacker/cli.py`

**Interfaces:**
- Consumes: `dedup.dedup_frames(frames_dir: str, threshold: float, output_dir: str) -> list[str]`
- Produces: `fp dedup` CLI subcommand

- [ ] **Step 1: Write failing test**

```python
import pytest
from pathlib import Path
from framepacker.dedup import dedup_frames


def test_dedup_removes_identical_frames(tmp_path):
    from PIL import Image
    frame_dir = tmp_path / "input"
    frame_dir.mkdir()
    for i in range(3):
        img = Image.new("RGB", (50, 50), (255, 0, 0))
        img.save(frame_dir / f"frame_{i:05d}.png")

    output = tmp_path / "output"
    result = dedup_frames(str(frame_dir), threshold=0.95, output_dir=str(output))
    assert len(result) == 1  # All identical → all deduped to 1
    assert Path(result[0]).exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest cli/tests/test_dedup.py -v`
Expected: FAIL

- [ ] **Step 3: Write dedup.py**

```python
import cv2
import numpy as np
from pathlib import Path


def _histogram_similarity(img1, img2):
    h1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
    h2 = cv2.calcHist([img2], [0], None, [256], [0, 256])
    return cv2.compareHist(h1, h2, cv2.HISTCMP_CORREL)


def dedup_frames(frames_dir, threshold=0.92, output_dir=None):
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
```

- [ ] **Step 4: Register dedup command in cli.py**

```python
from .dedup import dedup_frames


@cli.command()
@click.argument("frames_dir", type=click.Path(exists=True))
@click.option("--threshold", default=0.92, type=float, help="Similarity threshold (0-1)")
@click.option("--output", "-o", default=None, help="Output directory")
def dedup(frames_dir, threshold, output):
    """Remove duplicate/similar frames from a sequence."""
    result = dedup_frames(frames_dir, threshold, output)
    click.echo(f"Kept {len(result)} frames after deduplication")
```

- [ ] **Step 5: Run tests**

Run: `pytest cli/tests/test_dedup.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add cli/framepacker/dedup.py cli/tests/test_dedup.py cli/framepacker/cli.py
git commit -m "feat: add dedup command"
```

---

### Task 6: Remove-BG Command (batch background removal)

**Files:**
- Create: `cli/framepacker/removebg.py`
- Create: `cli/tests/test_removebg.py`
- Modify: `cli/framepacker/cli.py`

**Interfaces:**
- Consumes: `removebg.remove_background(frames_dir: str, output_dir: str) -> list[str]`
- Uses `rembg` library (offline, downloads model on first run)
- Produces: `fp remove-bg` CLI subcommand

- [ ] **Step 1: Write failing test**

```python
import pytest
from pathlib import Path
from framepacker.removebg import remove_background


def test_remove_bg_creates_files(tmp_path):
    from PIL import Image
    frame_dir = tmp_path / "input"
    frame_dir.mkdir()
    img = Image.new("RGB", (100, 100), (255, 0, 0))
    img.save(frame_dir / "frame_00001.png")

    output = tmp_path / "output"
    result = remove_background(str(frame_dir), output_dir=str(output))
    assert len(result) == 1
    assert Path(result[0]).exists()
    # Verify RGBA (has alpha channel after bg removal)
    from PIL import Image as PILImage
    loaded = PILImage.open(result[0])
    assert loaded.mode == "RGBA"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest cli/tests/test_removebg.py -v`
Expected: FAIL

- [ ] **Step 3: Write removebg.py**

```python
from pathlib import Path
from rembg import remove
from PIL import Image


def remove_background(frames_dir, output_dir=None):
    input_path = Path(frames_dir)
    output = Path(output_dir) if output_dir else input_path / "no_bg"
    output.mkdir(parents=True, exist_ok=True)

    frames = sorted(input_path.glob("*.png"))
    if not frames:
        raise ValueError(f"No PNG files found in {frames_dir}")

    result_paths = []
    for fpath in frames:
        with Image.open(fpath) as img:
            out = remove(img)
            dest = output / fpath.name
            out.save(dest)
            result_paths.append(str(dest))

    return result_paths
```

- [ ] **Step 4: Register remove-bg command in cli.py**

```python
from .removebg import remove_background


@cli.command(name="remove-bg")
@click.argument("frames_dir", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output directory")
def remove_bg(frames_dir, output):
    """Remove background from frames using AI."""
    result = remove_background(frames_dir, output)
    click.echo(f"Processed {len(result)} frames")
```

- [ ] **Step 5: Run tests**

Run: `pytest cli/tests/test_removebg.py -v`
Expected: This test may be slow on first run (model download), but should PASS

- [ ] **Step 6: Commit**

```bash
git add cli/framepacker/removebg.py cli/tests/test_removebg.py cli/framepacker/cli.py
git commit -m "feat: add remove-bg command"
```

---

### Task 7: Edit Command (batch image editing)

**Files:**
- Create: `cli/framepacker/edit.py`
- Create: `cli/tests/test_edit.py`
- Modify: `cli/framepacker/cli.py`

**Interfaces:**
- Consumes: `edit.batch_edit(frames_dir: str, resize: str, crop: str, rotate: float, grayscale: bool, output_dir: str) -> list[str]`
- Produces: `fp edit` CLI subcommand

- [ ] **Step 1: Write failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest cli/tests/test_edit.py -v`
Expected: FAIL

- [ ] **Step 3: Write edit.py**

```python
from pathlib import Path
from PIL import Image


def batch_edit(frames_dir, resize=None, crop=None, rotate=None, grayscale=False, output_dir=None):
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
```

- [ ] **Step 4: Register edit command in cli.py**

```python
from .edit import batch_edit


@cli.command()
@click.argument("frames_dir", type=click.Path(exists=True))
@click.option("--resize", default=None, help="Resize (e.g. 512x512)")
@click.option("--crop", default=None, help="Crop (left,upper,right,lower)")
@click.option("--rotate", default=None, type=float, help="Rotation angle")
@click.option("--grayscale", is_flag=True, help="Convert to grayscale")
@click.option("--output", "-o", default=None, help="Output directory")
def edit(frames_dir, resize, crop, rotate, grayscale, output):
    """Batch edit frames (resize, crop, rotate, grayscale)."""
    result = batch_edit(frames_dir, resize, crop, rotate, grayscale, output)
    click.echo(f"Edited {len(result)} frames")
```

- [ ] **Step 5: Run tests**

Run: `pytest cli/tests/test_edit.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add cli/framepacker/edit.py cli/tests/test_edit.py cli/framepacker/cli.py
git commit -m "feat: add edit command"
```

---

### Task 8: Pipeline Command (multi-step automation)

**Files:**
- Create: `cli/framepacker/pipeline.py`
- Create: `cli/tests/test_pipeline.py`
- Create: `cli/tests/fixtures/test_pipeline.yaml`
- Modify: `cli/framepacker/cli.py`

**Interfaces:**
- Consumes: `pipeline.run_pipeline(config_path: str) -> None`
- Config is a YAML file with steps array
- Produces: `fp pipeline` CLI subcommand

- [ ] **Step 1: Write failing test**

```python
import pytest
from pathlib import Path
from framepacker.pipeline import run_pipeline


def test_pipeline_runs(tmp_path):
    from PIL import Image
    # Create input frames
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest cli/tests/test_pipeline.py -v`
Expected: FAIL

- [ ] **Step 3: Write pipeline.py**

```python
import yaml
from pathlib import Path


def _list_frames(directory):
    """List PNG frame paths sorted, from a directory."""
    return sorted([str(p) for p in Path(directory).glob("*.png")])


# Map CLI-style arg names to function param names per command
ARG_NAME_MAP = {
    "extract": {"output": "output_dir", "video": "video_path"},
    "gif": {"frames_dir": "frame_paths"},
    "sprite": {"frames_dir": "frame_paths"},
    "dedup": {"output": "output_dir"},
    "remove-bg": {"output": "output_dir"},
    "edit": {"output": "output_dir"},
}


def run_pipeline(config_path, base_dir=None):
    with open(config_path) as f:
        config = yaml.safe_load(f)

    base = Path(base_dir) if base_dir else Path(config_path).parent

    for step in config.get("steps", []):
        cmd = step["command"]
        args = step.get("args", {})

        # 1. Resolve relative paths relative to config file location
        resolved = {}
        for k, v in args.items():
            if k in ("output", "frames_dir", "video") and isinstance(v, str):
                p = Path(v)
                if not p.is_absolute():
                    p = base / v
                resolved[k] = str(p)
            else:
                resolved[k] = v

        # 2. Map CLI-style names to function parameter names
        mapped = {}
        name_map = ARG_NAME_MAP.get(cmd, {})
        for k, v in resolved.items():
            mapped[name_map.get(k, k)] = v

        # 3. For gif/sprite: convert frames_dir (directory) to frame_paths (list)
        if cmd in ("gif", "sprite") and "frame_paths" not in mapped:
            frames_dir = (
                resolved.get("frames_dir")
                or (base / "frames")  # fallback to ./frames
            )
            if isinstance(frames_dir, str):
                mapped["frame_paths"] = _list_frames(frames_dir)
                # Remove any extraneous arg names left after mapping
                mapped.pop("output_dir", None)
                mapped.pop("resize_value", None)

        # Dispatch to the appropriate function
        if cmd == "extract":
            from .extract import extract_frames
            extract_frames(**mapped)
        elif cmd == "gif":
            from .gif import frames_to_gif
            frames_to_gif(**mapped)
        elif cmd == "sprite":
            from .sprite import frames_to_sprite
            frames_to_sprite(**mapped)
        elif cmd == "dedup":
            from .dedup import dedup_frames
            dedup_frames(**mapped)
        elif cmd == "remove-bg":
            from .removebg import remove_background
            remove_background(**mapped)
        elif cmd == "edit":
            from .edit import batch_edit
            batch_edit(**mapped)
        else:
            raise ValueError(f"Unknown command: {cmd}")

    return 0
```

- [ ] **Step 4: Register pipeline command in cli.py**

```python
from .pipeline import run_pipeline


@cli.command()
@click.argument("config", type=click.Path(exists=True))
def pipeline(config):
    """Run a multi-step pipeline from a YAML config file."""
    import sys
    sys.exit(run_pipeline(config))
```

- [ ] **Step 5: Run tests**

Run: `pytest cli/tests/test_pipeline.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add cli/framepacker/pipeline.py cli/tests/test_pipeline.py cli/framepacker/cli.py
git commit -m "feat: add pipeline command"
```

---

### Task 9: Frontend Scaffolding (Vue 3 + Vite)

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/stores/frames.js`

**Interfaces:**
- Consumes: nothing (next tasks add views)
- Produces: Run `npm run dev` → serves on localhost:5173

- [ ] **Step 1: Create package.json**

```json
{
  "name": "framepacker-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0",
    "fabric": "^5.3.0"
  },
  "devDependencies": {
    "vite": "^5.4.0",
    "@vitejs/plugin-vue": "^5.0.0"
  }
}
```

- [ ] **Step 2: Create vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
  },
})
```

- [ ] **Step 3: Create index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>FramePacker Local</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 4: Create src/main.js**

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **Step 5: Create src/App.vue**

```vue
<script setup>
</script>

<template>
  <div id="app-root">
    <header>
      <nav>
        <router-link to="/">FramePacker</router-link>
        <router-link to="/extract">提取帧</router-link>
        <router-link to="/editor">帧编辑器</router-link>
        <router-link to="/export">导出</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: sans-serif; background: #f5f5f5; color: #333; }
header { background: #1a1a2e; padding: 1rem 2rem; }
nav { display: flex; gap: 1.5rem; align-items: center; }
nav a { color: #e0e0e0; text-decoration: none; font-weight: 500; }
nav a:hover { color: #fff; }
nav a:first-child { font-size: 1.2rem; font-weight: 700; color: #ff6b35; }
main { max-width: 1200px; margin: 0 auto; padding: 2rem; }
</style>
```

- [ ] **Step 6: Create src/router/index.js**

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/extract', name: 'Extract', component: () => import('../views/ExtractView.vue') },
  { path: '/editor', name: 'Editor', component: () => import('../views/EditorView.vue') },
  { path: '/export', name: 'Export', component: () => import('../views/ExportView.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
```

- [ ] **Step 7: Create src/stores/frames.js**

```javascript
import { defineStore } from 'pinia'

export const useFrameStore = defineStore('frames', {
  state: () => ({
    videoFile: null,
    frames: [],
    fps: 12,
    selectedFrames: new Set(),
  }),
  getters: {
    frameCount: (state) => state.frames.length,
    selectedCount: (state) => state.selectedFrames.size,
  },
  actions: {
    setVideo(file) { this.videoFile = file; },
    addFrames(paths) { this.frames.push(...paths); },
    clearFrames() { this.frames = []; this.selectedFrames.clear(); },
    toggleSelect(idx) {
      if (this.selectedFrames.has(idx)) this.selectedFrames.delete(idx)
      else this.selectedFrames.add(idx)
    },
    selectAll() {
      this.selectedFrames = new Set(this.frames.map((_, i) => i))
    },
    deselectAll() { this.selectedFrames.clear(); },
    removeSelected() {
      const sorted = [...this.selectedFrames].sort((a, b) => b - a)
      for (const idx of sorted) this.frames.splice(idx, 1)
      this.selectedFrames.clear()
    },
    removeFrame(idx) { this.frames.splice(idx, 1); },
    moveFrame(from, to) {
      const [item] = this.frames.splice(from, 1)
      this.frames.splice(to, 0, item)
    },
  },
})
```

- [ ] **Step 8: Verify frontend starts**

Run: `cd frontend && npm install && npm run dev`
Expected: Vite dev server starts on localhost:5173, page renders header with nav links

- [ ] **Step 9: Commit**

```bash
git add frontend/package.json frontend/vite.config.js frontend/index.html frontend/src/main.js frontend/src/App.vue frontend/src/router/index.js frontend/src/stores/frames.js
git commit -m "feat: scaffold vue 3 frontend"
```

---

### Task 10: Home Page View

**Files:**
- Create: `frontend/src/views/Home.vue`

**Interfaces:**
- Consumes: nothing static page
- Produces: Home route `/`

- [ ] **Step 1: Create Home.vue**

```vue
<script setup>
</script>

<template>
  <div class="home">
    <section class="hero">
      <h1>FramePacker Local</h1>
      <p class="subtitle">视频转序列帧 / GIF / 帧动画 — 完全离线</p>
      <div class="actions">
        <router-link to="/extract" class="btn-primary">开始提取帧</router-link>
      </div>
    </section>

    <section class="features">
      <div class="card">
        <h3>📹 视频抽帧</h3>
        <p>上传视频，选好帧率和时长，一键提取帧画面</p>
      </div>
      <div class="card">
        <h3>✏️ 帧编辑器</h3>
        <p>逐帧预览、排序去重、批量抠图、换背景</p>
      </div>
      <div class="card">
        <h3>🎞️ 导出</h3>
        <p>GIF 动图 / PNG 序列帧 / 精灵表，自定义分辨率</p>
      </div>
      <div class="card">
        <h3>⚡ 自动化流水线</h3>
        <p>YAML 配置多步处理，CLI 脚本一键执行</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero { text-align: center; padding: 4rem 0; }
.hero h1 { font-size: 3rem; color: #1a1a2e; }
.subtitle { font-size: 1.2rem; color: #666; margin: 1rem 0 2rem; }
.btn-primary { display: inline-block; padding: 0.8rem 2rem; background: #ff6b35; color: #fff; text-decoration: none; border-radius: 8px; font-weight: 600; }
.features { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
.card { background: #fff; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.card h3 { margin-bottom: 0.5rem; color: #1a1a2e; }
.card p { color: #555; line-height: 1.6; }
</style>
```

- [ ] **Step 2: Verify Home renders**

Run: `npm run dev` and visit http://localhost:5173
Expected: Hero section with title and 4 feature cards

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/Home.vue
git commit -m "feat: add home page"
```

---

### Task 11: Extract View (Video Upload + Frame Extraction)

**Files:**
- Create: `frontend/src/views/ExtractView.vue`
- Create: `frontend/src/components/VideoUpload.vue`
- Create: `frontend/src/components/FrameExtractor.vue`

**Interfaces:**
- Consumes: `useFrameStore` for storing extracted frame paths
- Produces: `/extract` route — video upload, fps/duration settings, extract button, progress

- [ ] **Step 1: Create VideoUpload.vue**

```vue
<script setup>
import { ref } from 'vue'
import { useFrameStore } from '../stores/frames'

const store = useFrameStore()
const videoUrl = ref(null)
const fileInput = ref(null)

function onFileSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  store.setVideo(file)
  videoUrl.value = URL.createObjectURL(file)
}

function triggerFileInput() {
  fileInput.value.click()
}
</script>

<template>
  <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="onFileSelected($event.dataTransfer)">
    <input ref="fileInput" type="file" accept="video/*" hidden @change="onFileSelected" />
    <div v-if="!store.videoFile" class="upload-placeholder">
      <p>拖拽视频到此处，或点击选择</p>
      <p class="hint">支持 MP4, AVI, MOV, WebM 等常见格式</p>
    </div>
    <div v-else class="upload-preview">
      <video :src="videoUrl" controls width="100%" />
      <p>{{ store.videoFile.name }} ({{ (store.videoFile.size / 1024 / 1024).toFixed(1) }} MB)</p>
      <button @click.stop="store.setVideo(null); videoUrl=null" class="btn-link">更换视频</button>
    </div>
  </div>
</template>

<style scoped>
.upload-area { border: 2px dashed #ccc; border-radius: 12px; padding: 3rem; text-align: center; cursor: pointer; background: #fafafa; }
.upload-area:hover { border-color: #ff6b35; }
.upload-placeholder p { font-size: 1.1rem; color: #666; }
.hint { font-size: 0.85rem; color: #999; margin-top: 0.5rem; }
.upload-preview p { margin-top: 0.5rem; color: #555; }
.btn-link { background: none; border: none; color: #ff6b35; cursor: pointer; text-decoration: underline; margin-top: 0.5rem; }
</style>
```

- [ ] **Step 2: Create FrameExtractor.vue**

```vue
<script setup>
import { ref } from 'vue'
import { useFrameStore } from '../stores/frames'

const store = useFrameStore()
const fps = ref(12)
const duration = ref(null)
const start = ref(0)
const resize = ref('')
const extracting = ref(false)
const progress = ref('')

async function extractFrames() {
  // Validate CLI is available by checking the store has a video
  if (!store.videoFile) return

  extracting.value = true
  progress.value = 'Preparing...'

  // This is a placeholder — Task 14 replaces with real API call (api/extractFrames)
  extracting.value = false
  progress.value = 'Connecting to backend... (see Task 14 for full integration)'
}
</script>

<template>
  <div class="extractor">
    <h2>提取参数</h2>
    <div class="form-row">
      <label>
        帧率 (FPS)
        <input v-model.number="fps" type="number" min="1" max="60" />
      </label>
      <label>
        起始时间 (秒)
        <input v-model.number="start" type="number" min="0" step="0.1" />
      </label>
      <label>
        时长 (秒, 留空=全部)
        <input v-model.number="duration" type="number" min="0" step="0.1" placeholder="全部" />
      </label>
      <label>
        缩放 (留空=原始)
        <input v-model="resize" type="text" placeholder="如 512x512" />
      </label>
    </div>
    <button :disabled="!store.videoFile || extracting" class="btn-primary" @click="extractFrames">
      {{ extracting ? '提取中...' : '提取帧' }}
    </button>
    <pre v-if="progress" class="cli-hint">{{ progress }}</pre>
  </div>
</template>

<style scoped>
.extractor { margin-top: 2rem; }
h2 { color: #1a1a2e; margin-bottom: 1rem; }
.form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.9rem; color: #555; }
input { padding: 0.5rem; border: 1px solid #ddd; border-radius: 6px; font-size: 1rem; }
.btn-primary { padding: 0.7rem 2rem; background: #ff6b35; color: #fff; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.cli-hint { margin-top: 1rem; padding: 1rem; background: #1a1a2e; color: #0f0; border-radius: 8px; white-space: pre-wrap; font-family: monospace; }
</style>
```

- [ ] **Step 3: Create ExtractView.vue**

```vue
<script setup>
import VideoUpload from '../components/VideoUpload.vue'
import FrameExtractor from '../components/FrameExtractor.vue'
</script>

<template>
  <div class="extract-view">
    <h1>视频抽帧</h1>
    <VideoUpload />
    <FrameExtractor />
  </div>
</template>

<style scoped>
h1 { margin-bottom: 1.5rem; color: #1a1a2e; }
</style>
```

- [ ] **Step 4: Verify page renders**

Run: `npm run dev`, visit http://localhost:5173/extract
Expected: Upload area + parameter form visible, upload works

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/ExtractView.vue frontend/src/components/VideoUpload.vue frontend/src/components/FrameExtractor.vue
git commit -m "feat: add extract view with video upload"
```

---

### Task 12: Frame Editor View

**Files:**
- Create: `frontend/src/views/EditorView.vue`
- Create: `frontend/src/components/FrameList.vue`
- Create: `frontend/src/components/FramePreview.vue`
- Create: `frontend/src/components/BatchToolbar.vue`
- Create: `frontend/src/components/FrameCanvas.vue`

**Interfaces:**
- Consumes: `useFrameStore` frames list
- Produces: `/editor` route — thumbnail grid, preview, batch ops

- [ ] **Step 1: Create FrameList.vue**

```vue
<script setup>
import { useFrameStore } from '../stores/frames'

const store = useFrameStore()

function onDragStart(e, idx) {
  e.dataTransfer.setData('text/plain', idx)
}
function onDrop(e, idx) {
  const from = parseInt(e.dataTransfer.getData('text/plain'))
  if (from !== idx) store.moveFrame(from, idx)
}
</script>

<template>
  <div class="frame-list">
    <div class="list-header">
      <h3>帧列表 ({{ store.frameCount }})</h3>
      <div class="list-actions">
        <button @click="store.selectAll" :disabled="!store.frameCount">全选</button>
        <button @click="store.deselectAll" :disabled="!store.selectedCount">取消选择</button>
        <button @click="store.removeSelected" :disabled="!store.selectedCount">删除选中</button>
      </div>
    </div>
    <div class="frame-grid">
      <div v-for="(frame, idx) in store.frames" :key="idx"
        class="frame-thumb"
        :class="{ selected: store.selectedFrames.has(idx) }"
        draggable="true"
        @dragstart="onDragStart($event, idx)"
        @dragover.prevent
        @drop="onDrop($event, idx)"
        @click="store.toggleSelect(idx)">
        <img :src="frame" :alt="'Frame ' + idx" />
        <span class="frame-idx">{{ idx + 1 }}</span>
      </div>
    </div>
    <div v-if="!store.frameCount" class="empty">
      <p>暂无帧数据。请先提取视频帧。</p>
      <router-link to="/extract">前往提取帧</router-link>
    </div>
  </div>
</template>

<style scoped>
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.list-actions { display: flex; gap: 0.5rem; }
.list-actions button { padding: 0.3rem 0.8rem; border: 1px solid #ddd; background: #fff; border-radius: 4px; cursor: pointer; }
.frame-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 0.5rem; }
.frame-thumb { position: relative; border: 2px solid transparent; border-radius: 6px; cursor: pointer; transition: border-color 0.2s; }
.frame-thumb:hover { border-color: #ff6b35; }
.frame-thumb.selected { border-color: #1a1a2e; background: #e0e0e0; }
.frame-thumb img { width: 100%; height: 80px; object-fit: cover; border-radius: 4px; }
.frame-idx { position: absolute; bottom: 2px; right: 4px; background: rgba(0,0,0,0.6); color: #fff; font-size: 0.7rem; padding: 1px 4px; border-radius: 3px; }
.empty { text-align: center; padding: 3rem; color: #999; }
</style>
```

- [ ] **Step 2: Create BatchToolbar.vue**

```vue
<script setup>
import { ref } from 'vue'
import { useFrameStore } from '../stores/frames'

const store = useFrameStore()
const threshold = ref(0.92)

function runDedup() {
  const indices = [...store.selectedFrames].length
    ? [...store.selectedFrames].sort((a, b) => b - a)
    : []
  if (indices.length <= 1) return

  // Mark removal for selected duplicates (in production, call CLI)
  for (let i = 1; i < indices.length; i++) {
    store.removeFrame(indices[i])
  }
  store.deselectAll()
}

function removeBg() {
  alert('批量抠图功能需要 CLI: fp remove-bg ./frames')
}

function grayscaleAll() {
  alert('批量转灰度需要 CLI: fp edit ./frames --grayscale')
}
</script>

<template>
  <div class="batch-toolbar">
    <h4>批量操作</h4>
    <div class="tool-group">
      <label>去重阈值</label>
      <input v-model.number="threshold" type="number" min="0" max="1" step="0.01" />
      <button @click="runDedup" :disabled="store.selectedCount < 2">去重选中</button>
    </div>
    <div class="tool-group">
      <button @click="store.selectAll">全选</button>
      <button @click="removeBg">批量抠图</button>
      <button @click="grayscaleAll">批量灰度</button>
    </div>
  </div>
</template>

<style scoped>
.batch-toolbar { padding: 1rem; background: #fff; border-radius: 8px; margin-bottom: 1rem; }
h4 { margin-bottom: 0.5rem; color: #1a1a2e; }
.tool-group { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; margin-bottom: 0.5rem; }
.tool-group input { width: 80px; padding: 0.3rem; border: 1px solid #ddd; border-radius: 4px; }
.tool-group button { padding: 0.3rem 0.8rem; border: 1px solid #ddd; background: #fff; border-radius: 4px; cursor: pointer; }
.tool-group button:hover { background: #f0f0f0; }
</style>
```

- [ ] **Step 3: Create FramePreview.vue**

```vue
<script setup>
import { ref, computed } from 'vue'
import { useFrameStore } from '../stores/frames'

const store = useFrameStore()
const selectedIdx = ref(0)

const currentFrame = computed(() => {
  if (!store.frames.length) return null
  return store.frames[selectedIdx.value]
})

function prev() {
  if (selectedIdx.value > 0) selectedIdx.value--
}
function next() {
  if (selectedIdx.value < store.frames.length - 1) selectedIdx.value++
}
</script>

<template>
  <div class="frame-preview" v-if="currentFrame">
    <div class="preview-nav">
      <button @click="prev" :disabled="selectedIdx === 0">◀ 上一帧</button>
      <span>{{ selectedIdx + 1 }} / {{ store.frameCount }}</span>
      <button @click="next" :disabled="selectedIdx >= store.frames.length - 1">下一帧 ▶</button>
    </div>
    <div class="preview-image">
      <img :src="currentFrame" alt="Frame preview" />
    </div>
  </div>
  <div v-else class="preview-empty">
    <p>选择一帧以预览</p>
  </div>
</template>

<style scoped>
.frame-preview { text-align: center; }
.preview-nav { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-bottom: 0.5rem; }
.preview-nav button { padding: 0.3rem 0.8rem; border: 1px solid #ddd; background: #fff; border-radius: 4px; cursor: pointer; }
.preview-nav button:disabled { opacity: 0.4; cursor: not-allowed; }
.preview-image img { max-width: 100%; max-height: 400px; border: 1px solid #ddd; border-radius: 8px; }
.preview-empty { text-align: center; padding: 3rem; color: #999; }
</style>
```

- [ ] **Step 4: Create FrameCanvas.vue**

```vue
<script setup>
import { ref, onMounted, watch } from 'vue'
import { useFrameStore } from '../stores/frames'

const store = useFrameStore()
const canvasRef = ref(null)
const selectedIdx = ref(0)

watch(() => store.frames.length, () => {
  if (store.frames.length > 0) loadFrame(0)
})

function loadFrame(idx) {
  selectedIdx.value = idx
  if (!canvasRef.value || !store.frames[idx]) return
  const img = new Image()
  img.onload = () => {
    const canvas = canvasRef.value
    canvas.width = img.width
    canvas.height = img.height
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0)
  }
  img.src = store.frames[idx]
}
</script>

<template>
  <div class="frame-canvas">
    <h4>逐帧精修</h4>
    <canvas ref="canvasRef" class="editor-canvas"></canvas>
    <p class="hint">提示：完整 Canvas 编辑功能（画笔/裁剪/滤镜）将在后续版本实现</p>
  </div>
</template>

<style scoped>
.frame-canvas { margin-top: 1rem; }
h4 { margin-bottom: 0.5rem; color: #1a1a2e; }
.editor-canvas { max-width: 100%; border: 1px solid #ddd; border-radius: 8px; background: #fff; }
.hint { font-size: 0.85rem; color: #999; margin-top: 0.5rem; }
</style>
```

- [ ] **Step 5: Create EditorView.vue**

```vue
<script setup>
import FrameList from '../components/FrameList.vue'
import FramePreview from '../components/FramePreview.vue'
import BatchToolbar from '../components/BatchToolbar.vue'
import FrameCanvas from '../components/FrameCanvas.vue'
</script>

<template>
  <div class="editor-view">
    <h1>帧编辑器</h1>
    <div class="editor-layout">
      <aside class="sidebar">
        <BatchToolbar />
        <FrameList />
      </aside>
      <section class="main-area">
        <FramePreview />
        <FrameCanvas />
      </section>
    </div>
  </div>
</template>

<style scoped>
h1 { margin-bottom: 1.5rem; color: #1a1a2e; }
.editor-layout { display: grid; grid-template-columns: 320px 1fr; gap: 1.5rem; }
.sidebar { overflow-y: auto; max-height: calc(100vh - 150px); }
.main-area { min-height: 500px; }
</style>
```

- [ ] **Step 6: Verify Editor renders**

Run: `npm run dev`, visit http://localhost:5173/editor
Expected: Layout with sidebar (batch toolbar + frame list) and main area (preview + canvas)

- [ ] **Step 7: Commit**

```bash
git add frontend/src/views/EditorView.vue frontend/src/components/FrameList.vue frontend/src/components/FramePreview.vue frontend/src/components/BatchToolbar.vue frontend/src/components/FrameCanvas.vue
git commit -m "feat: add frame editor view"
```

---

### Task 13: Export View

**Files:**
- Create: `frontend/src/views/ExportView.vue`
- Create: `frontend/src/components/ExportPanel.vue`

**Interfaces:**
- Consumes: `useFrameStore` frames data
- Produces: `/export` route — export format selection, settings, download

- [ ] **Step 1: Create ExportPanel.vue**

```vue
<script setup>
import { ref } from 'vue'
import { useFrameStore } from '../stores/frames'

const store = useFrameStore()
const format = ref('gif')
const exportFps = ref(10)
const exportResize = ref('')
const loop = ref(0)
const cols = ref(8)
const exporting = ref(false)
const cliCommand = ref('')

function getCliCommand() {
  if (!store.frameCount) return ''
  const parts = []
  if (format.value === 'gif') {
    parts.push('fp gif ./frames')
    parts.push(`--fps ${exportFps.value}`)
    if (exportResize.value) parts.push(`--resize ${exportResize.value}`)
    parts.push(`--loop ${loop.value}`)
    parts.push('--output animation.gif')
  } else if (format.value === 'png') {
    parts.push('zip -r frames.zip ./frames')
  } else if (format.value === 'sprite') {
    parts.push('fp sprite ./frames')
    parts.push(`--cols ${cols.value}`)
    if (exportResize.value) parts.push(`--resize ${exportResize.value}`)
    parts.push('--output sprite.png')
  }
  return '$ ' + parts.join(' ')
}

function showCommand() {
  cliCommand.value = getCliCommand()
}

async function doExport() {
  exporting.value = true
  showCommand()
  setTimeout(() => { exporting.value = false }, 1000)
}
</script>

<template>
  <div class="export-panel">
    <h2>导出设置</h2>

    <div class="export-options">
      <div class="format-select">
        <label>
          <input type="radio" v-model="format" value="gif" />
          <span>GIF 动图</span>
        </label>
        <label>
          <input type="radio" v-model="format" value="png" />
          <span>PNG 序列帧 (ZIP)</span>
        </label>
        <label>
          <input type="radio" v-model="format" value="sprite" />
          <span>精灵表 (Sprite Sheet)</span>
        </label>
      </div>

      <div class="export-params">
        <label v-if="format === 'gif'">
          帧率 (FPS)
          <input v-model.number="exportFps" type="number" min="1" max="60" />
        </label>
        <label v-if="format === 'gif'">
          循环次数 (0=无限)
          <input v-model.number="loop" type="number" min="0" />
        </label>
        <label v-if="format === 'sprite'">
          列数
          <input v-model.number="cols" type="number" min="1" max="20" />
        </label>
        <label>
          缩放 (留空=原始)
          <input v-model="exportResize" type="text" placeholder="如 512x512" />
        </label>
      </div>
    </div>

    <button :disabled="!store.frameCount || exporting" class="btn-primary" @click="doExport">
      {{ exporting ? '导出中...' : '生成导出命令' }}
    </button>

    <pre v-if="cliCommand" class="cli-command">{{ cliCommand }}</pre>
  </div>
</template>

<style scoped>
.export-panel { max-width: 600px; }
h2 { color: #1a1a2e; margin-bottom: 1rem; }
.export-options { margin-bottom: 1.5rem; }
.format-select { display: flex; gap: 1.5rem; margin-bottom: 1rem; }
.format-select label { display: flex; align-items: center; gap: 0.3rem; cursor: pointer; }
.export-params { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
.export-params label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.9rem; color: #555; }
.export-params input { padding: 0.5rem; border: 1px solid #ddd; border-radius: 6px; }
.btn-primary { padding: 0.7rem 2rem; background: #ff6b35; color: #fff; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.cli-command { margin-top: 1rem; padding: 1rem; background: #1a1a2e; color: #0f0; border-radius: 8px; white-space: pre-wrap; font-family: monospace; }
</style>
```

- [ ] **Step 2: Create ExportView.vue**

```vue
<script setup>
import ExportPanel from '../components/ExportPanel.vue'
</script>

<template>
  <div class="export-view">
    <h1>导出</h1>
    <ExportPanel />
  </div>
</template>

<style scoped>
h1 { margin-bottom: 1.5rem; color: #1a1a2e; }
</style>
```

- [ ] **Step 3: Verify Export renders**

Run: `npm run dev`, visit http://localhost:5173/export
Expected: Export format selection, parameter inputs, generate command button

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/ExportView.vue frontend/src/components/ExportPanel.vue
git commit -m "feat: add export view"
```

---

### Task 14: Integration — CLI ↔ Frontend Bridge

**Files:**
- Create: `frontend/src/api/framepacker.js`
- Modify: `frontend/src/components/FrameExtractor.vue` (call API)
- Modify: `frontend/src/components/ExportPanel.vue` (call API)
- Modify: `frontend/vite.config.js` (proxy for backend if needed)

**Interfaces:**
- Consumes: all CLI commands from Tasks 2-8
- Produces: API module `api/framepacker.js` that calls CLI via child_process (Electron) or HTTP (Flask wrapper)

- [ ] **Step 1: Create api/framepacker.js**

```javascript
/**
 * FramePacker API bridge.
 *
 * In dev mode, this calls a lightweight Flask/Express wrapper around the CLI.
 * In standalone mode (Electron/desktop), it calls the CLI directly via child_process.
 *
 * For now, returns CLI command strings that the user can copy-paste.
 * Replace with actual HTTP calls once the backend wrapper is built.
 */

const API_BASE = 'http://localhost:5080/api'

export async function extractFrames({ videoPath, fps = 12, output = './frames', start = 0, duration = null, resize = null }) {
  const params = { video_path: videoPath, fps, output, start }
  if (duration) params.duration = duration
  if (resize) params.resize = resize
  const res = await fetch(`${API_BASE}/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`Extract failed: ${res.statusText}`)
  return res.json()
}

export async function framesToGif({ framesDir, fps = 10, output = 'output.gif', resize = null, loop = 0 }) {
  const params = { frames_dir: framesDir, fps, output, loop }
  if (resize) params.resize = resize
  const res = await fetch(`${API_BASE}/gif`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`GIF failed: ${res.statusText}`)
  return res.json()
}

export async function framesToSprite({ framesDir, cols = 8, output = 'sprite.png', padding = 2, resize = null }) {
  const params = { frames_dir: framesDir, cols, output, padding }
  if (resize) params.resize = resize
  const res = await fetch(`${API_BASE}/sprite`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`Sprite failed: ${res.statusText}`)
  return res.json()
}

export async function dedupFrames({ framesDir, threshold = 0.92, output = null }) {
  const params = { frames_dir: framesDir, threshold }
  if (output) params.output = output
  const res = await fetch(`${API_BASE}/dedup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`Dedup failed: ${res.statusText}`)
  return res.json()
}

export async function removeBg({ framesDir, output = null }) {
  const params = { frames_dir: framesDir }
  if (output) params.output = output
  const res = await fetch(`${API_BASE}/remove-bg`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`Remove-BG failed: ${res.statusText}`)
  return res.json()
}

export async function batchEdit({ framesDir, resize = null, crop = null, rotate = null, grayscale = false, output = null }) {
  const params = { frames_dir: framesDir, grayscale }
  if (resize) params.resize = resize
  if (crop) params.crop = crop
  if (rotate !== null) params.rotate = rotate
  if (output) params.output = output
  const res = await fetch(`${API_BASE}/edit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`Edit failed: ${res.statusText}`)
  return res.json()
}
```

- [ ] **Step 2: Create Flask wrapper backend**

Create `cli/backend/app.py`:

```python
"""
Lightweight Flask wrapper around the framepacker CLI.
This provides HTTP endpoints for the Vue frontend to call.
"""
import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add parent to path so framepacker CLI module is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from framepacker.extract import extract_frames
from framepacker.gif import frames_to_gif
from framepacker.sprite import frames_to_sprite
from framepacker.dedup import dedup_frames
from framepacker.removebg import remove_background
from framepacker.edit import batch_edit

app = Flask(__name__)
CORS(app)


@app.route("/api/extract", methods=["POST"])
def api_extract():
    data = request.json
    result = extract_frames(
        video_path=data["video_path"],
        fps=data.get("fps", 12),
        output_dir=data.get("output", "./frames"),
        start=data.get("start", 0),
        duration=data.get("duration"),
        resize=data.get("resize"),
    )
    return jsonify({"frames": result, "count": len(result)})


@app.route("/api/gif", methods=["POST"])
def api_gif():
    data = request.json
    from pathlib import Path
    frames = sorted([str(p) for p in Path(data["frames_dir"]).glob("*.png")])
    result = frames_to_gif(
        frames,
        output=data["output"],
        fps=data.get("fps", 10),
        resize=data.get("resize"),
        loop=data.get("loop", 0),
    )
    return jsonify({"output": result})


@app.route("/api/sprite", methods=["POST"])
def api_sprite():
    data = request.json
    from pathlib import Path
    frames = sorted([str(p) for p in Path(data["frames_dir"]).glob("*.png")])
    result = frames_to_sprite(
        frames,
        output=data["output"],
        cols=data.get("cols", 8),
        padding=data.get("padding", 2),
        resize=data.get("resize"),
    )
    return jsonify({"output": result})


@app.route("/api/dedup", methods=["POST"])
def api_dedup():
    data = request.json
    result = dedup_frames(
        frames_dir=data["frames_dir"],
        threshold=data.get("threshold", 0.92),
        output_dir=data.get("output"),
    )
    return jsonify({"frames": result, "count": len(result)})


@app.route("/api/remove-bg", methods=["POST"])
def api_remove_bg():
    data = request.json
    result = remove_background(
        frames_dir=data["frames_dir"],
        output_dir=data.get("output"),
    )
    return jsonify({"frames": result, "count": len(result)})


@app.route("/api/edit", methods=["POST"])
def api_edit():
    data = request.json
    result = batch_edit(
        frames_dir=data["frames_dir"],
        resize=data.get("resize"),
        crop=data.get("crop"),
        rotate=data.get("rotate"),
        grayscale=data.get("grayscale", False),
        output_dir=data.get("output"),
    )
    return jsonify({"frames": result, "count": len(result)})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080, debug=True)
```

- [ ] **Step 3: Create requirements for backend wrapper**

Create `cli/backend/requirements.txt`:
```
flask>=3.0
flask-cors>=4.0
```

- [ ] **Step 4: Modify FrameExtractor.vue to call real API**

Replace the placeholder `extractFrames` in `frontend/src/components/FrameExtractor.vue`:

```vue
<script setup>
import { ref } from 'vue'
import { useFrameStore } from '../stores/frames'
import { extractFrames as apiExtract } from '../api/framepacker'

const store = useFrameStore()
const fps = ref(12)
const duration = ref(null)
const start = ref(0)
const resize = ref('')
const extracting = ref(false)
const progress = ref('')
const error = ref('')

async function extractFrames() {
  if (!store.videoFile) return
  extracting.value = true
  error.value = ''
  progress.value = '提取中...'

  try {
    const result = await apiExtract({
      videoPath: store.videoFile.name,
      fps: fps.value,
      output: './frames',
      start: start.value,
      duration: duration.value || null,
      resize: resize.value || null,
    })
    store.addFrames(result.frames)
    progress.value = `成功提取 ${result.count} 帧`
  } catch (e) {
    error.value = `提取失败: ${e.message}`
  } finally {
    extracting.value = false
  }
}
</script>

<template>
  <div class="extractor">
    <h2>提取参数</h2>
    <div class="form-row">
      <label>
        帧率 (FPS)
        <input v-model.number="fps" type="number" min="1" max="60" />
      </label>
      <label>
        起始时间 (秒)
        <input v-model.number="start" type="number" min="0" step="0.1" />
      </label>
      <label>
        时长 (秒, 留空=全部)
        <input v-model.number="duration" type="number" min="0" step="0.1" placeholder="全部" />
      </label>
      <label>
        缩放 (留空=原始)
        <input v-model="resize" type="text" placeholder="如 512x512" />
      </label>
    </div>
    <button :disabled="!store.videoFile || extracting" class="btn-primary" @click="extractFrames">
      {{ extracting ? '提取中...' : '提取帧' }}
    </button>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="progress && !error" class="progress">{{ progress }}</p>
  </div>
</template>

<style scoped>
.extractor { margin-top: 2rem; }
h2 { color: #1a1a2e; margin-bottom: 1rem; }
.form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.9rem; color: #555; }
input { padding: 0.5rem; border: 1px solid #ddd; border-radius: 6px; font-size: 1rem; }
.btn-primary { padding: 0.7rem 2rem; background: #ff6b35; color: #fff; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.error { margin-top: 0.5rem; color: #d32f2f; }
.progress { margin-top: 0.5rem; color: #2e7d32; }
</style>
```

- [ ] **Step 5: Modify ExportPanel.vue to call real API**

Replace the `doExport` in `frontend/src/components/ExportPanel.vue`:

```vue
<script setup>
import { ref } from 'vue'
import { useFrameStore } from '../stores/frames'
import { framesToGif, framesToSprite } from '../api/framepacker'

const store = useFrameStore()
const format = ref('gif')
const exportFps = ref(10)
const exportResize = ref('')
const loop = ref(0)
const cols = ref(8)
const exporting = ref(false)
const result = ref('')
const error = ref('')

async function doExport() {
  exporting.value = true
  error.value = ''
  result.value = ''
  try {
    if (format.value === 'gif') {
      const res = await framesToGif({
        framesDir: './frames',
        fps: exportFps.value,
        output: 'animation.gif',
        resize: exportResize.value || null,
        loop: loop.value,
      })
      result.value = `GIF 已保存: ${res.output}`
    } else if (format.value === 'sprite') {
      const res = await framesToSprite({
        framesDir: './frames',
        cols: cols.value,
        output: 'sprite.png',
        resize: exportResize.value || null,
      })
      result.value = `精灵表已保存: ${res.output}`
    } else {
      result.value = 'PNG 序列帧需手动打包: fp pipeline pack.yaml'
    }
  } catch (e) {
    error.value = `导出失败: ${e.message}`
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <div class="export-panel">
    <h2>导出设置</h2>

    <div class="export-options">
      <div class="format-select">
        <label><input type="radio" v-model="format" value="gif" /><span>GIF 动图</span></label>
        <label><input type="radio" v-model="format" value="png" /><span>PNG 序列帧 (ZIP)</span></label>
        <label><input type="radio" v-model="format" value="sprite" /><span>精灵表 (Sprite Sheet)</span></label>
      </div>

      <div class="export-params">
        <label v-if="format === 'gif'">
          帧率 (FPS) <input v-model.number="exportFps" type="number" min="1" max="60" />
        </label>
        <label v-if="format === 'gif'">
          循环次数 <input v-model.number="loop" type="number" min="0" />
        </label>
        <label v-if="format === 'sprite'">
          列数 <input v-model.number="cols" type="number" min="1" max="20" />
        </label>
        <label>
          缩放 <input v-model="exportResize" type="text" placeholder="如 512x512" />
        </label>
      </div>
    </div>

    <button :disabled="!store.frameCount || exporting" class="btn-primary" @click="doExport">
      {{ exporting ? '导出中...' : '开始导出' }}
    </button>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="result" class="success">{{ result }}</p>
  </div>
</template>

<style scoped>
.export-panel { max-width: 600px; }
h2 { color: #1a1a2e; margin-bottom: 1rem; }
.export-options { margin-bottom: 1.5rem; }
.format-select { display: flex; gap: 1.5rem; margin-bottom: 1rem; }
.format-select label { display: flex; align-items: center; gap: 0.3rem; cursor: pointer; }
.export-params { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
.export-params label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.9rem; color: #555; }
.export-params input { padding: 0.5rem; border: 1px solid #ddd; border-radius: 6px; }
.btn-primary { padding: 0.7rem 2rem; background: #ff6b35; color: #fff; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.error { margin-top: 0.5rem; color: #d32f2f; }
.success { margin-top: 0.5rem; color: #2e7d32; }
</style>
```

- [ ] **Step 6: Configure Vite proxy**

Modify `frontend/vite.config.js`:
```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5080',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 7: Start backend and test integration**

Run: `pip install flask flask-cors`
Run: `python cli/backend/app.py`
In another terminal: `cd frontend && npm run dev`
Open http://localhost:5173

Expected: Frontend loads, API calls go through Vite proxy to Flask backend

- [ ] **Step 8: Commit**

```bash
git add frontend/src/api/framepacker.js cli/backend/app.py cli/backend/requirements.txt frontend/vite.config.js
git commit -m "feat: add flask api backend and frontend api bridge"
```
