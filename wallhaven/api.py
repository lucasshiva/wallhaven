import os
from typing import Any, Dict, Optional

from wallhaven.client import APIClient
from wallhaven.models import Wallpaper


class Wallhaven:
    """Interface for the Wallhaven API v1.

    Examples:
        >>> from wallhaven import Wallhaven
        >>> api = Wallhaven(api_key=<api_key>)
        >>> api.get_wallpaper(<id>)
        <Wallpaper(id=...)>
    """

    def __init__(
        self, api_key: Optional[str] = None, *, timeout: int = 20, retries: int = 1
    ) -> None:
        """Initialize a ``Wallhaven`` instance.

        Args:
            api_key: The API key is used for operations that require the user to be authenticated
                (such as viewing your browsing settings), and for NSFW wallpapers. If none is given,
                `Wallhaven` will try to read one from the 'WALLHAVEN_API_KEY' environment variable.
            timeout: The amount of seconds to wait for the server's response before giving up.
            retries: The amount of retries to perform when requesting the API.
        """
        self.api_key = api_key or os.environ.get("WALLHAVEN_API_KEY")
        self.timeout = timeout
        self.retries = retries

        # TODO: Find a way to share this client between this class and the models.
        # I want to be able to reuse the connection in every request the user makes.
        # So far, the only way I can get this working is by passing the client to the models, but
        # I don't think that it the ideal solution.
        self.client = APIClient(api_key, timeout=self.timeout, retries=self.retries)

    def _get(self, endpoint: str, *, pass_client: bool = False) -> Dict[str, Any]:
        """Send a GET request to the endpoint.

        Args:
            endpoint: The url to request.
            client: Whether to add ``self.client`` to the JSON response.

        Returns:
            The response in JSON format.
        """
        response: Dict[str, Any] = self.client.get(endpoint).json()

        # If we only have the `data` key, add the client inside it.
        if len(response.keys()) == 1 and pass_client:
            response["data"]["client"] = self.client

        # Otherwise, add it as another key.
        else:
            response["client"] = self.client

        return response

    def get_wallpaper(self, id: str) -> Wallpaper:
        """Get wallpaper from ID.

        Args:
            id: The wallpaper's unique identifier, e.g., "8oxreo".

        Returns:
            An instance of ``Wallpaper``

        Raises:
            ``UnauthorizedRequest``: API key is invalid or inexistent.
            ``NotFoundError``: Wallpaper not found.
            ``TooManyRequestsError``: Exceeded the request limit.

        Examples:
            >>> from wallhaven import Wallhaven
            >>> api = Wallhaven()
            >>> w = api.get_wallpaper("8oxreo")
            <Wallpaper(id="8oxreo", ...)>
        """
        data = self._get(f"/w/{id}", pass_client=True)["data"]
        return Wallpaper.parse_obj(data)
