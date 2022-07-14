from typing import List

from pydantic import PrivateAttr

from wallhaven.client import APIClient
from wallhaven.models import BaseModel, Meta, Wallpaper


class Listing(BaseModel):
    """Represents a listing.

    Attributes:
        data:
            A list of `Wallpaper` instances without the `Tags` and `Uploader` attributes.
        meta:
            An instance of `Meta` that contains metadata about the listing.
    """

    data: List[Wallpaper]
    meta: Meta
    _client: APIClient = PrivateAttr(default_factory=APIClient)
