from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from typing_extensions import Literal

from wallhaven.session import handler


class WallhavenModel:
    """Base model class with methods that other models will inherit."""

    def __init__(self, **kwargs) -> None:
        self._data: Dict[str, Any] = {}

    def as_dict(self) -> Dict[str, Any]:
        """Return the instance as a dictionary."""
        return self._data

    def as_json(self, **kwargs) -> str:
        """Return the instance as a JSON string.

        Args:
            **kwargs: Optional keyword arguments that `json.dumps` takes.
        """
        return json.dumps(self.as_dict(), **kwargs)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Return an instance of `cls` from `data`.

        Args:
            data (dict): The data returned from the API.
        """
        # Save the original data.
        cls._data = data.copy()
        return cls(**data)


@dataclass(frozen=True)
class Wallpaper(WallhavenModel):
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
            (base ** 5, "PB"),
            (base ** 4, "TB"),
            (base ** 3, "GB"),
            (base ** 2, "MB"),
            (base ** 1, "kB"),
            (base ** 0, "B"),
        ]

        for scale in scales:
            if self.file_size >= scale[0]:
                break
        return "%.2f%s" % (self.file_size / scale[0], scale[1])

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Wallpaper:
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
    def from_listing_data(cls, data: Dict[str, Any]) -> Wallpaper:
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

    def save(self, path: Union[Path, str]) -> None:
        """Download wallpaper and save it in `path`.

        The directory will be automatically created if it doesn't exist and the file
        format is `wallhaven-{id}{extension}`, e.g `wallhaven-8oxreo.png`.

        Args:
            path (Path | str): The directory where the wallpaper will be saved.

        Raises:
            TypeError: If `path` is not a `str` or a `Path` object.
        """
        if not isinstance(path, Path):
            path = Path(path)

        if not path.exists():
            path.mkdir()

        filename = f"wallhaven-{self.id}{self.extension}"
        filepath = path.joinpath(filename)

        response = handler.get(self.path, stream=True, timeout=20)
        with open(filepath, "wb+") as img_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    img_file.write(chunk)


@dataclass
class Tag(WallhavenModel):
    """Represents a Tag.

    Attributes:
        id (int): The tag ID.
        name (str): The user defined name for the tag.
        alias (str): A comma separated string of aliases for the `name`.
        category (str): The name of the tag's category.
        category_id (int): The ID of the category.
        purity (str): The tag's purity. One of ["sfw", "sketchy", "nsfw"]
        created_at (str): A `%Y-%m-%d %H:%M:%S` string representing the tag's creation
            date. Example: "2014-02-02 23:23:48".
    """

    id: int
    name: str
    alias: str
    category: str
    category_id: int
    purity: Literal["sfw", "sketchy", "nsfw"]
    created_at: str


@dataclass
class Uploader(WallhavenModel):
    """Represents an Uploader.

    Uploaders are not included in all wallpapers objects.

    Attributes:
        username (str): The username of the uploader.
        group (str): A string determining the type of account. Usually this defined as
            the literal "user".
        avatar (dict): A mapping of the user's avatar in different sizes.
    """

    username: str
    group: str = field(repr=False)
    avatar: Dict[str, str] = field(repr=False)


@dataclass
class UserSettings(WallhavenModel):
    """Represents an user's browsing settings.

    These settings are read-only, which means that we can't modify them through the API.
    Also, they can be used automatically when performing a search. To achieve that, we
    simply need to perform a search with the only parameter being the user's API key.
    Wallhaven will automatically make use of these settings to return results that
    match them.

    Attributes:
        thumb_size (str): The thumbnail size when browsing for images.
        per_page (str): The amount of images per page when browsing for images.
        purity (list): A list of the enabled purities to match.
        categories (list): A list of the enabled categories to match.
        resolutions (list): A list of the resolutions to match.
        aspect_ratios (list): A list of the aspect ratios to match.
        toplist_range (str): The default toplist range.
        tag_blacklist (list): A list of tags to exclude.
        user_blacklist (list): A list of users to exclude.
    """

    thumb_size: Literal["original", "small", "large"]
    per_page: Literal["24", "32", "64"]
    purity: List[str]
    categories: List[str]
    resolutions: List[str]
    aspect_ratios: List[str]
    toplist_range: Literal["1d", "3d", "1w", "1M", "3M", "6M", "1y"]
    tag_blacklist: List[str]
    user_blacklist: List[str]


@dataclass
class Collection(WallhavenModel):
    """Represents a collection.

    This model only contains information about the collection itself. It does not show a
    listing of the wallpapers inside it, for that you need `CollectionListing` instead.

    Attributes:
        id (int): The ID of the collection.
        label (str): A user defined name/label for the collection.
        views (int): The amount of views the collection has.
        public (int): Whether the collection is public (1) or private (0).
        count (int): The amount of wallpapers inside the collection.
    """

    id: int
    label: str
    views: int

    # The API returns this field as 1 (True) or 0 (False).
    public: Literal[0, 1]
    count: int

    def is_public(self) -> bool:
        """Returns if the collection is marked as private (False) or public (True).

        This is essentially the same as calling the `public` attribute in a condition.
        For example: `if collection.is_public()` instead of `if collection.public`.
        """
        # True if 1, False if 0.
        return bool(self.public)


@dataclass
class BaseListing(WallhavenModel):
    """Base listing class.

    This is a model that will be inherited from `CollectionListing` and `SearchResults`.

    Attributes:
        data (list): A list of `Wallpaper` objects. These objects come without
            information about the `Tags` and the `Uploader`.
        meta (Meta): An instance of `Meta`. It contains metadata about the listing and
            can also be used for pagination.
    """

    data: List[Wallpaper]
    meta: Meta

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Return an instance of `cls` from `data`."""
        cls._data = data.copy()

        wallpapers = [Wallpaper.from_listing_data(w) for w in data.pop("data")]
        meta = Meta.from_dict(data.pop("meta"))

        return cls(data=wallpapers, meta=meta)


@dataclass
class CollectionListing(BaseListing):
    """Represents the listing of wallpapers inside a collection.

    This model contains information about the wallpapers inside a collection, if you
    need information about the collection itself, you need to use `Collection` instead.
    """

    pass


@dataclass(frozen=True)
class Meta(WallhavenModel):
    """Represents the Meta field in the API response.

    The meta field is only available when viewing the listing of wallpapers in a
    collection or when searching for wallpapers.

    Attributes:
        current_page (int): The current page of the listing/search.
        last_page (int): The last page of the listing/search.
        per_page (int): The amount of wallpapers per page.
        total (int): The total amount of wallpapers in a collection/search result.
        query (str | dict): The search query. It can be a string or, when searching
            for exact tags, it will be a dictionary with the tag id and name.
        seed (str): A seed that can be passed between pages to ensure there are no
            repeats when sorting by `random`.
        request_url (str): An optional string stating the request URL.
    """

    current_page: int
    last_page: int

    # Listings are limited to 24 results per page.
    per_page: Literal[24]
    total: int

    # A custom field that will be used for pagination.
    # The URL will look like this: https://wallhaven.cc/api/v1/collections/USERNAME/ID
    # For pagination, we simply need to append "?page=<page_number>".
    request_url: Optional[str] = field(repr=False, default=None)

    # Query and Seed are only available when searching. The search query is usually a
    # string, but when searching for exact tags, a dictionary is returned instead.
    # This dictionary is similar to the following: {"id": 1, "tag": "anime"}.
    query: Optional[Union[str, dict]] = None

    # Sorting by `random` will produce a seed that can be passed between pages to ensure
    # there are no repeats when getting a new page.
    seed: Optional[str] = None


@dataclass
class SearchResults(BaseListing):
    """Represents the search results.

    This model contains information about the wallpapers liste in a search result, as
    well as meta information required for pagination.
    """

    pass
