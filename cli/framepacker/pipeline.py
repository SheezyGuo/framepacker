import yaml
from pathlib import Path


def _list_frames(directory):
    return sorted([str(p) for p in Path(directory).glob("*.png")])


ARG_NAME_MAP = {
    "extract": {"output": "output_dir", "video": "video_path"},
    "gif": {"frames_dir": "frame_paths"},
    "sprite": {"frames_dir": "frame_paths"},
    "dedup": {"output": "output_dir"},
    "remove-bg": {"output": "output_dir"},
    "edit": {"output": "output_dir"},
}


def run_pipeline(config_path: str, base_dir: str | None = None) -> int:
    with open(config_path) as f:
        config = yaml.safe_load(f)

    base = Path(base_dir) if base_dir else Path(config_path).parent

    for step in config.get("steps", []):
        cmd = step["command"]
        args = step.get("args", {})

        resolved = {}
        for k, v in args.items():
            if k in ("output", "frames_dir", "video") and isinstance(v, str):
                p = Path(v)
                if not p.is_absolute():
                    p = base / v
                resolved[k] = str(p)
            else:
                resolved[k] = v

        mapped = {}
        name_map = ARG_NAME_MAP.get(cmd, {})
        for k, v in resolved.items():
            mapped[name_map.get(k, k)] = v

        if cmd in ("gif", "sprite") and "frame_paths" not in mapped:
            frames_dir = resolved.get("frames_dir") or str(base / "frames")
            if isinstance(frames_dir, str):
                mapped["frame_paths"] = _list_frames(frames_dir)

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
