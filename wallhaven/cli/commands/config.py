import json

import click

from wallhaven.config import wallhaven_config


@click.group()
def config() -> None:
    """Interact with the configuration."""
    pass


@config.command(help="Print the contents of the configuration file.")
def show() -> None:
    c = wallhaven_config.read_config_file()
    click.echo(json.dumps(c, indent=2))
