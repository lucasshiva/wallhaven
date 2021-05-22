"""Provides Wallhaven to interact with the Wallhaven API."""
from typing import Dict, Optional, Union

from wallhaven.api import API_ENDPOINTS
from wallhaven.session import RequestHandler
from wallhaven.models.api import Wallpaper, Tag


class Wallhaven:
    """A wrapper around the Wallhaven API.

    Usage:
        >>> wallhaven = Wallhaven()
        >>> wallpaper = wallhaven.get_wallpaper(wallpaper_id="8oxreo")
        <Wallpaper(id='8oxreo', ...)>
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize a Wallhaven instance.

        Args:
            api_key (str): A key that grants users unrestricted access to the API.
                This key is provided via the user's account settings and can be
                regenerated at anytime by the user.
        """
        self.api_key = api_key

        # Users can authenticate by including their API key either in a request URL by
        # appending ?apikey=<API KEY>, or by including the X-API-Key: <API KEY> header
        # with the request. We will use the latter.
        self.headers: Dict[str, str] = {}
        if self.api_key is not None:
            self.headers["X-API-Key"] = self.api_key

        # Instantiates the handler object. We won't use the API key for every request,
        # so we don't need to set the headers right now.
        self.handler = RequestHandler()

    def get_wallpaper(self, wallpaper_id: str) -> Wallpaper:
        """Get wallpaper from ID. An API key is required for NSFW wallpapers."""
        url = API_ENDPOINTS["wallpaper"].format(id=wallpaper_id)
        content = self.handler.get_json(url, headers=self.headers)
        return Wallpaper.from_dict(content.get("data", {}))

    def get_tag(self, tag_id: Union[str, int]) -> Tag:
        """Get tag from ID."""
        url = API_ENDPOINTS["tag"].format(id=tag_id)
        content = self.handler.get_json(url)
        return Tag.from_dict(content.get("data", {}))
