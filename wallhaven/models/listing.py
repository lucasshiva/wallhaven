from typing import List, Dict, Any
from dataclasses import dataclass

from wallhaven.models.base import BaseModel
from wallhaven.models.meta import Meta
from wallhaven.models.wallpaper import Wallpaper


@dataclass
class BaseListing(BaseModel):
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


@dataclass
class SearchResults(BaseListing):
    """Represents the search results.

    This model contains information about the wallpapers liste in a search result, as
    well as meta information required for pagination.
    """

    pass
