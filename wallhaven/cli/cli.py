import click

from wallhaven import Wallhaven
from wallhaven.cli.commands import ConfigCommand, WallpaperCommand
from wallhaven.config import wallhaven_config as config


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    ctx.obj = Wallhaven(api_key=config.api.api_key, timeout=config.api.timeout)


cli.add_command(WallpaperCommand)
cli.add_command(ConfigCommand)

if __name__ == "__main__":
    cli()
