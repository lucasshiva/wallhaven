import click

from wallhaven import Wallhaven
from wallhaven.config import wallhaven_config as config

help_message = """Download and save wallpaper.

By default, the save directory will be the one specified in the config file. If this directory is
null, then the current directory will be used instead. It is also possible to provide a custom
location by using the `-p` option followed by a path.
"""


@click.command(help=help_message)
@click.argument("id", type=str)
@click.option("--json", help="Print wallpaper's metadata to sdtout in JSON format.", is_flag=True)
@click.option(
    "--nosave",
    is_flag=True,
    help="Does not save the wallpaper. This is useful if you're only interested in the JSON.",
)
@click.option(
    "-o",
    "--override",
    is_flag=True,
    help=f"Whether to override existing files. Current: {config.download.override}",
)
@click.option(
    "-p",
    "--path",
    type=click.Path(writable=True, file_okay=False, resolve_path=True),
    help=f"Save the wallpaper in this path. Current: {config.download.path.absolute()}",
    default=config.download.path.absolute(),
)
@click.pass_obj
def wallpaper(api: Wallhaven, id: str, json: bool, nosave: bool, override: bool, path: str) -> None:
    w = api.get_wallpaper(id)

    if json:
        click.echo(w.json(indent=2))

    if not nosave:
        w.download(path, override=override)
        click.echo(f"Saved {w.filename} in '{path}'")
