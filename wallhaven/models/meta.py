from typing import Optional, Union

from pydantic import BaseModel

from wallhaven.search import SearchParameters


class Meta(BaseModel):
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

    # Listings are limited to 24, 32, or 64 results per page.
    per_page: int
    total: int

    # A custom field that will be used for pagination.
    # The URL will look like this: https://wallhaven.cc/api/v1/collections/USERNAME/ID
    # For pagination, we simply need to append "?page=<page_number>".
    request_url: str
    params: SearchParameters

    # Query and Seed are only available when searching. The search query is usually a
    # string, but when searching for exact tags, a dictionary is returned instead.
    # This dictionary is similar to the following: {"id": 1, "tag": "anime"}.
    query: Optional[Union[str, dict]] = None

    # Sorting by `random` will produce a seed that can be passed between pages to ensure
    # there are no repeats when getting a new page.
    seed: Optional[str] = None
