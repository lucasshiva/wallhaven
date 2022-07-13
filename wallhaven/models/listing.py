from typing import List

from pydantic import BaseModel, PrivateAttr

from wallhaven.client import APIClient
from wallhaven.models import Meta, Wallpaper


class Listing(BaseModel):
    """The main listing class.

    Attributes:
        data:
            A list of `Wallpaper` instances without the `Tags` and `Uploader` attributes.
        meta:
            An instance of `Meta` that contains metadata about the listing.
    """

    data: List[Wallpaper]
    meta: Meta
    _client: APIClient = PrivateAttr(default=None)  # This is NOT an optional attribute.

    class Config:
        arbitrary_types_allowed = True
