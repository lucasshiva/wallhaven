from __future__ import annotations

from typing import List, Dict, Any, Optional
import json

from dataclasses import dataclass, field


class WallhavenModel:
    """Base model class with methods that other classes will inherit."""

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
            data (dict): A JSON object returned from the API.
        """
        # Save the original data.
        cls._data = data.copy()
        return cls(**data)


@dataclass(frozen=True)
class Wallpaper(WallhavenModel):
    """Represents a wallpaper."""

    id: str = field(repr=True)
    url: str
    short_url: str = field(repr=False)
    views: int
    favorites: int
    source: str
    purity: str
    category: str
    dimension_x: int = field(repr=False)
    dimension_y: int = field(repr=False)
    resolution: str
    ratio: str = field(repr=False)
    file_size: int = field(repr=False)
    file_type: str
    created_at: str = field(repr=False)
    colors: List[str] = field(repr=False)
    path: str = field(repr=False)
    thumbs: Dict[str, str] = field(repr=False)

    # Search results don't include tags in wallpapers.
    tags: List[Tag] = field(default_factory=list)

    # Collections don't include the uploader in wallpapers.
    uploader: Optional[Uploader] = field(default=None)

    @property
    def width(self) -> int:
        return self.dimension_x

    @property
    def height(self) -> int:
        return self.dimension_y

    @property
    def extension(self) -> str:
        return ".jpg" if self.file_type == "image/jpeg" else ".png"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Wallpaper:
        """Return an instance of Wallpaper from `data`.

        Args:
            data (dict): A dictionary containing the wallpaper's information. This
                dictionary *MUST* contain information about tags and the uploader.
        """
        # Save the original data.
        cls._data = data.copy()

        # Convert tags and uploaders to objects.
        tags = [Tag.from_dict(tag) for tag in data.pop("tags")]
        uploader = Uploader.from_dict(data.pop("uploader"))

        # Return an instance of Wallpaper with the converted tags and uploader.
        return cls(tags=tags, uploader=uploader, **data)

    @classmethod
    def from_collection_dict(cls, data: Dict[str, Any]) -> Wallpaper:
        """Return an instance of Wallpaper from `data`.

        Args:
            data (dict): A dictionary containing the wallpaper's information. This
                dictionary must *NOT* contain information about tags or the uploader.
        """
        # Save the original data.
        cls._data = data.copy()

        # Return an instance of Wallpaper with default tags and uploader.
        return cls(**data)


@dataclass
class Tag(WallhavenModel):
    """Represents a Tag."""

    id: int
    name: str
    alias: str = field(repr=False)
    category_id: int = field(repr=False)
    category: str
    purity: str
    created_at: str = field(repr=False)


@dataclass
class Uploader(WallhavenModel):
    """Represents a Uploader."""

    username: str
    group: str = field(repr=False)
    avatar: Dict[str, str] = field(repr=False)
