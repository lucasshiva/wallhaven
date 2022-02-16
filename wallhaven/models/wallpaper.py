from typing import Dict, List, Optional, Any, Union
from typing_extensions import Literal
from pathlib import Path

from dataclasses import dataclass, field

from wallhaven.session import RequestHandler
from wallhaven.models.base import BaseModel
from wallhaven.models.tag import Tag
from wallhaven.models.uploader import Uploader


@dataclass
class Wallpaper(BaseModel):
    """Represents a Wallpaper.

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

    _session: RequestHandler = field(init=False, repr=False)

    id: str
    url: str
    short_url: str = field(repr=False)
    views: int
    favorites: int
    source: str
    purity: Literal["sfw", "sketchy", "nsfw"]
    category: Literal["general", "anime", "people"]
    dimension_x: int = field(repr=False)
    dimension_y: int = field(repr=False)
    resolution: str
    ratio: str = field(repr=False)
    file_size: int = field(repr=False)
    file_type: Literal["image/jpeg", "image/png"]
    created_at: str = field(repr=False)
    colors: List[str] = field(repr=False)
    path: str = field(repr=False)
    thumbs: Dict[str, str] = field(repr=False)

    # No tags/uploader when searching or listing a collection.
    tags: List[Tag] = field(default_factory=list)
    uploader: Optional[Uploader] = field(default=None)

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

    @property
    def filename(self) -> str:
        """Return a string representing the filename of the wallpaper."""
        return f"wallhaven-{self.id}{self.extension}"

    def _set_session(self, session: RequestHandler) -> None:
        """Set the session."""
        self._session = session

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Wallpaper":
        """Return an instance of Wallpaper from `data`.

        Args:
            data (dict): A dictionary containing the wallpaper's information. This
                dictionary *MUST* contain information about tags and the uploader.

        Returns:
            Wallpaper: A new instance of a `Wallpaper` object.
        """
        # Save the original data.
        cls._data = data.copy()

        # Convert tags and uploaders to objects.
        tags = [Tag.from_dict(tag) for tag in data.pop("tags")]
        uploader = Uploader.from_dict(data.pop("uploader"))

        # Return an instance of Wallpaper with the converted tags and uploader.
        return cls(tags=tags, uploader=uploader, **data)

    @classmethod
    def from_listing_data(cls, data: Dict[str, Any]) -> "Wallpaper":
        """Return an instance of Wallpaper from `data`.

        Args:
            data (dict): A dictionary containing the wallpaper's information. This
                dictionary must *NOT* contain information about tags or the uploader.

        Returns:
            Wallpaper: A new instance of a `Wallpaper` object.
        """
        # Save the original data.
        cls._data = data.copy()

        # Return an instance of Wallpaper with default tags and uploader.
        return cls(**data)

    def _download(self, path: Path) -> None:
        response = self._session.get(self.path, stream=True)
        with open(path, "wb+") as file:
            for chunk in response.iter_bytes():
                if chunk:
                    file.write(chunk)

    def save(self, path: Union[Path, str], override: bool = False) -> None:
        """Download wallpaper and save it in `path`.

        The directory will be automatically created if it doesn't exist and the file
        format is `wallhaven-{id}{extension}`, e.g., `wallhaven-8oxreo.png`.

        Users may choose whether to override existing files or simply skip the download.

        Args:
            path (Path | str): The directory where the wallpaper will be saved.
            override (bool): Whether to override existing files.

        Raises:
            TypeError: If `path` is not a `str` or a `Path` object.
        """
        # Ensure we always used path objects.
        path = Path(path)

        path.mkdir(parents=True, exist_ok=True)

        # Get the file path; /home/user/Pictures/wallhaven-8oxreo.png
        filepath = path.joinpath(self.filename)

        if not filepath.exists() or override:
            self._download(filepath)
