from pathlib import Path
from typing import Dict, List, Optional

from typing_extensions import Literal
from pydantic import PrivateAttr

from wallhaven.client import APIClient
from wallhaven.models import BaseModel, Tag, Uploader


class PureWallpaper(BaseModel):
    """Represents a Wallpaper

    Attributes:
        id (str): The wallpaper ID. e.g `8oxreo`.
        url (str): The wallpaper URL, e.g `wallhaven.cc/w/8oxreo`.
        short_url (str): The wallpaper short URL, e.g `whvn.cc/8oxreo`.
        views (int): The amount of views the wallpaper has.
        favorites (int): How many users saved it in their favorites.
        source (str): The source of the wallpaper.
        purity (str): The purity of the wallpaper, one of ["sfw", "sketchy", "nsfw"].
        category (str): The category of the wallpaper, one of
            ["general", "anime", "people"]
        dimension_x (int): The width of the wallpaper, e.g 1920.
        dimension_y (int): The height of the wallpaper, e.g 1080.
        resolution (str): The resolution of the wallpaper, e.g 1920x1080.
        ratio (str): The aspect ratio of the wallpaper.
        file_size (int): The file size in bytes.
        file_type (str): The type of image, one of:z "image/jpeg" or "image/png".
        created_at (str): A `%Y-%m-%d %H:%M:%S` string representing the tag's creation
            date. Example: "2015-01-21 12:34:11".
        colors (list): A list of the colors available in the wallpapers.
        path (str): The full path of the wallpaper, e.g
            `w.wallhaven.cc/full/8o/wallhaven-8oxreo.png`.
        thumbs (dict): A mapping of `{'thumb_size': 'thumb_url'}`
    """

    id: str
    url: str
    short_url: str
    views: int
    favorites: int
    source: str
    purity: Literal["sfw", "sketchy", "nsfw"]
    category: Literal["general", "anime", "people"]
    dimension_x: int
    dimension_y: int
    resolution: str
    ratio: str
    file_size: int
    file_type: Literal["image/jpeg", "image/png"]
    created_at: str
    colors: List[str]
    path: str
    thumbs: Dict[str, str]

    # No tags/uploader when searching or listing a collection.
    tags: List[Tag] = []
    uploader: Optional[Uploader] = None

    @property
    def width(self) -> int:
        """A helper method to make it easier to access the wallpaper's width."""
        return self.dimension_x

    @property
    def height(self) -> int:
        """A helper method to make it easier to access the wallpaper's height."""
        return self.dimension_y

    @property
    def extension(self) -> str:
        """Convert file MIME type to extension."""
        return ".jpg" if self.file_type == "image/jpeg" else ".png"

    @property
    def readable_size(self) -> str:
        """Return the file size as a human friendly KB, MB, GB, TB or PB string."""
        base = 1000
        scales = [
            (base**5, "PB"),
            (base**4, "TB"),
            (base**3, "GB"),
            (base**2, "MB"),
            (base**1, "kB"),
            (base**0, "B"),
        ]

        for scale in scales:
            if self.file_size >= scale[0]:
                break
        return "%.2f%s" % (self.file_size / scale[0], scale[1])


class Wallpaper(PureWallpaper):
    """Represents a Wallpaper

    Attributes:
        id (str): The wallpaper ID. e.g `8oxreo`.
        url (str): The wallpaper URL, e.g `wallhaven.cc/w/8oxreo`.
        short_url (str): The wallpaper short URL, e.g `whvn.cc/8oxreo`.
        views (int): The amount of views the wallpaper has.
        favorites (int): How many users saved it in their favorites.
        source (str): The source of the wallpaper.
        purity (str): The purity of the wallpaper, one of ["sfw", "sketchy", "nsfw"].
        category (str): The category of the wallpaper, one of
            ["general", "anime", "people"]
        dimension_x (int): The width of the wallpaper, e.g 1920.
        dimension_y (int): The height of the wallpaper, e.g 1080.
        resolution (str): The resolution of the wallpaper, e.g 1920x1080.
        ratio (str): The aspect ratio of the wallpaper.
        file_size (int): The file size in bytes.
        file_type (str): The type of image, one of:z "image/jpeg" or "image/png".
        created_at (str): A `%Y-%m-%d %H:%M:%S` string representing the tag's creation
            date. Example: "2015-01-21 12:34:11".
        colors (list): A list of the colors available in the wallpapers.
        path (str): The full path of the wallpaper, e.g
            `w.wallhaven.cc/full/8o/wallhaven-8oxreo.png`.
        thumbs (dict): A mapping of `{'thumb_size': 'thumb_url'}`
    """

    _client: APIClient = PrivateAttr(default_factory=APIClient)

    @property
    def filename(self) -> str:
        """Return a string representing the filename of the wallpaper."""
        return f"wallhaven-{self.id}{self.extension}"

    def download(self, path: str, override: bool = True) -> None:
        """Download the wallpaper.

        Args:
            path: The directory to save the wallpaper.
            override: If true, overrides existing files with the same filename.

        Examples:
            >>> from wallhaven import Wallhaven
            >>> api = Wallhaven()
            >>> w = api.get_wallpaper("3zp9ly")
            >>> w.download("/home/foo/Pictures", override=True)
        """
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)

        filepath = p / self.filename
        if not override and filepath.exists():
            return

        r = self._client.get(self.path, stream=True)
        with open(filepath, "wb") as img_file:
            for chunk in r.iter_bytes():
                img_file.write(chunk)
