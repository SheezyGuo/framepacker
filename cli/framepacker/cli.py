import click

from .extract import extract_frames


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
