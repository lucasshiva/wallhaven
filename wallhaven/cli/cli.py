import click

from wallhaven import Wallhaven
from wallhaven.cli.commands import ConfigCommand, WallpaperCommand
from wallhaven.config import wallhaven_config


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    ctx.obj = Wallhaven(settings=wallhaven_config.api, params=wallhaven_config.search)


cli.add_command(WallpaperCommand)
cli.add_command(ConfigCommand)

if __name__ == "__main__":
    cli()
