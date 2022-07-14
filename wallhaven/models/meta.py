from typing import Optional, Union

from wallhaven.models import BaseModel
from wallhaven.search import SearchParameters


class Meta(BaseModel):
    """Represents the Meta field in the API response.

    The meta field is only available when viewing the listing of wallpapers in a
    collection or when searching for wallpapers.

    Attributes:
        current_page:
            The current page of the listing/search.
        last_page:
            The last page of the listing/search.
        per_page:
            The amount of wallpapers per page.
        total:
            The total amount of wallpapers in a collection/search result.
        request_url:
            An optional string stating the request URL.
        params:
            The parameters used in the request. When using `Meta.dict()`, `params` will be equal to
            a dictionary of query parameters ignoring any default parameters.
        api_key:
            If an API key was present when the request was made.
        query:
            The search query. It can be a string or, when searching for exact tags, it will be a
            dictionary with the tag id and name.
        seed:
            A seed that can be passed between pages to ensure there are no repeats when sorting by
            `random`.
    """

    current_page: int
    last_page: int

    # Listings are limited to 24, 32, or 64 results per page.
    per_page: int
    total: int

    # Custom fields.
    # The URL will look like this: https://wallhaven.cc/api/v1/collections/USERNAME/ID
    # For pagination, we simply need to append "?page=<page_number>". This will be done by modifying
    # `params.page` and performing another request from a `Listing` model.
    request_url: str
    api_key: bool
    params: SearchParameters

    # Query and Seed are only available when searching. The search query is usually a
    # string, but when searching for exact tags, a dictionary is returned instead.
    # This dictionary is similar to the following: {"id": 1, "tag": "anime"}.
    query: Optional[Union[str, dict]] = None

    # Sorting by `random` will produce a seed that can be passed between pages to ensure
    # there are no repeats when getting a new page.
    seed: Optional[str] = None
