# mypy: allow-untyped-defs
import logging
from pathlib import Path

import click

import wallhaven
from wallhaven import __version__

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(__version__, "-v", "--version")
@click.option(
    "-t", "--timeout", type=int, help="How much time to wait for the server's response.", default=20
)
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING"], case_sensitive=False),
    help="Set the log level for the application.",
    default="WARNING",
)
@click.option(
    "-q",
    "--quiet",
    help="Do not print anything to stdout. Overrides log level.",
    is_flag=True,
    type=bool,
)
@click.pass_context
def cli(ctx, timeout, log_level, quiet) -> None:
    if not quiet:
        if log_level == "DEBUG":
            fmt = "%(levelname)s: %(asctime)s - %(name)s - %(message)s"
        else:
            fmt = "%(levelname)s: %(asctime)s - %(message)s"
        logging.basicConfig(format=fmt, level=log_level)
    ctx.obj = wallhaven.API(timeout=timeout)


@cli.command()
@click.argument("id", type=str)
@click.option(
    "-q",
    "--quiet",
    help="Do not print wallpaper's metadata. Does not override log level.",
    type=bool,
    is_flag=True,
)
@click.option(
    "-s",
    "--save",
    help="Save wallpaper in specified directory.",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
)
@click.option(
    "-o",
    "--override",
    help="Whether to override existing files when saving wallpaper.",
    type=bool,
    is_flag=True,
)
@click.pass_obj
def wallpaper(api: wallhaven.API, id, quiet, save, override) -> None:
    """Get wallpaper from a given ID. An API key is required for NSFW wallpapers.

    By default, this command will print the wallpaper's metadata to stdout in JSON format.
    """
    logger.info(f"Fetching wallpaper with id: {id}")
    w = api.get_wallpaper(id)
    logger.info(f"Sucess! Found wallpaper: {w.id}{w.extension}")

    if not quiet:
        click.echo(w.as_json(indent=2))
    else:
        logger.info("Hiding wallpaper's metadata due to --quiet.")

    if save:
        dir = Path(save)
        logger.info(f"Saving wallpaper in {dir.absolute()}")
        w.save(dir, override=override)
        logger.info(f"Finished downloading wallhaven-{w.id}{w.extension}")


if __name__ == "__main__":
    cli()
