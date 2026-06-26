import click

from .extract import extract_frames
from .gif import frames_to_gif
from .sprite import frames_to_sprite


@click.group()
@click.version_option("0.1.0")
def cli():
    """FramePacker - Video frame extraction & animation tools."""
    pass


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
