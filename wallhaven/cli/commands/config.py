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


@config.command(help="Add missing values to the configuration file.")
def update() -> None:
    wallhaven_config.update_config()


@config.command(help="Print the current path of the configuration file.")
def path() -> None:
    click.echo(wallhaven_config.PATH.absolute())
