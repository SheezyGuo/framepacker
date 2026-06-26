import click


@click.group()
@click.version_option("0.1.0")
def cli():
    """FramePacker - Video frame extraction & animation tools."""
    pass
