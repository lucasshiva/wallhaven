from json import dumps

import click

from wallhaven import Wallhaven
from wallhaven.config import wallhaven_config as config


help_message = f"""Search and download wallpapers.

By default, this command will automatically download and save the wallpapers in the specified path.

If an API key is present, the parameters from the user's browsing settings will be used. Otherwise,
`wallhaven` will use the default parameters instead.

Using an API key is the recommended way of setting the parameters, as it allows to change the amount
of wallpapers per request up to 64 (default is 24). The API key is also required for NSFW
wallpapers.

Any parameters set in '{config.PATH}' or one of the options below will have priority over the user's
browsing settings or the default parameters.
"""


@click.command(help=help_message)
@click.option(
    "--nosave",
    help="If True, does not save wallpapers. Current: False",
    type=bool,
    is_flag=True,
    default=False,
)
@click.option(
    "--json",
    help="If True, print the listing in JSON format. Current: False",
    is_flag=True,
    default=False,
)
@click.option(
    "--path",
    help=f"Save the wallpapers in this path. Current: '{config.download.path.absolute()}'",
    default=f"{config.download.path.absolute()}",
    type=click.Path(file_okay=False, writable=True, resolve_path=True),
)
@click.option(
    "--override",
    help=f"Whether to override existing files. Current: {config.download.override}",
    is_flag=True,
    default=config.download.override,
)
@click.option(
    "--default",
    help="Use the default parameters. This will ignore any existing parameters. Current: False",
    is_flag=True,
    default=False,
    type=bool,
)
@click.option(
    "-c",
    "--categories",
    type=str,
    help=f"Set the categories. Current: {config.search.categories.as_query_param()}",
    default=config.search.categories.as_query_param(),
)
@click.pass_obj
def search(
    api: Wallhaven,
    nosave: bool,
    json: bool,
    path: str,
    override: bool,
    default: bool,
    categories: str,
) -> None:

    # No need to make a request, then.
    if not json and nosave:
        return

    if default:
        listing = api.search(default=True)
    else:
        data = {"categories": categories}
        api.params.load_dict(data)
        listing = api.search()

    if json:
        click.echo(dumps(listing.dict(), indent=2))

    if not nosave:
        with click.progressbar(listing.data, label="Downloading wallpapers..") as bar:
            for wallpaper in bar:
                wallpaper.download(path, override)
