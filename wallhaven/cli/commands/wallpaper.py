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
    "--no-save",
    is_flag=True,
    help="Does not save the wallpaper. This is useful if you're only interested in the metadata.",
)
@click.option(
    "-o",
    "--override",
    is_flag=True,
    help="Whether to override existing files when saving the wallpaper. Default: False",
)
@click.option(
    "-p",
    "--path",
    type=click.Path(writable=True, file_okay=False),
    help="A custom path in which to save the wallpaper.",
)
@click.pass_obj
def wallpaper(
    api: Wallhaven, id: str, json: bool, no_save: bool, override: bool, path: str
) -> None:
    w = api.get_wallpaper(id)

    if json:
        click.echo(w.json(indent=2))

    if not no_save:
        save_directory = config.download.path or path or "."
        w.download(save_directory, override=override)
