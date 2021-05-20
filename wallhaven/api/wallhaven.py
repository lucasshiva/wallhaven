"""Provides Wallhaven to interact with the Wallhaven API."""
from typing import Any, Dict, Optional

from wallhaven.api import API_ENDPOINTS
from wallhaven.session import RequestHandler


class Wallhaven:
    """A wrapper around the Wallhaven API.

    Usage:
        >>> wallhaven = Wallhaven()
        >>> wallpaper = wallhaven.get_wallpaper(wallpaper_id="8oxreo")
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

    def get_wallpaper(self, wallpaper_id: str) -> Dict[str, Any]:
        """Get wallpaper from ID. An API key is required for NSFW wallpapers."""
        url = API_ENDPOINTS["wallpaper"].format(id=wallpaper_id)
        response = self.handler.get(url, headers=self.headers).json()
        return response.get("data")
