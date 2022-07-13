from typing import Any, Dict

from wallhaven.client import APIClient
from wallhaven.config import APISettings
from wallhaven.models import Listing, Wallpaper
from wallhaven.search import SearchParameters


class Wallhaven:
    """Interface for the Wallhaven API v1.

    Examples:

        A simple example:

        >>> from wallhaven import Wallhaven
        >>> api = Wallhaven()
        >>> api.get_wallpaper(<id>)
        <Wallpaper ...>

        Change default API settings:

        >>> from wallhaven import Wallhaven
        >>> from wallhaven.config import APISettings
        >>> settings = APISettings(timeout=10)  # Changing default config.
        >>> api = Wallhaven(settings=settings)
        >>> api.get_wallpaper(<id>)
        <Wallpaper ...>

        Set the search parameters.
        >>> from wallhaven import Wallhaven
        >>> from wallhaven.search import Sorting, ToplistRange
        >>> api = Wallhaven()
        >>> api.params.categories.set(general=True, anime=True, people=False)  # Disable people
        >>> api.params.sorting = Sorting.Toplist
        >>> api.params.topRange = ToplistRange.LastWeek
        >>> api.search()
        <Listing ...>
    """

    def __init__(
        self,
        *,
        settings: APISettings = APISettings(),
        params: SearchParameters = SearchParameters(),
    ) -> None:
        """Initializes a ``Wallhaven`` instance.

        Args:
            settings: The settings for the API.
            params: The parameters used when searching for wallpapers.
        """
        self.settings = settings

        if not isinstance(params, SearchParameters):
            params = SearchParameters.parse_obj(params)
        self.params = params

        self.client = APIClient(settings=self.settings)

    def _get(
        self,
        endpoint: str,
        *,
        pass_client: bool = False,
        auth: bool = False,
        use_params: bool = False,
    ) -> Dict[str, Any]:
        """Send a GET request to the endpoint.

        Args:
            endpoint:
                The endpoint to request.
            client:
                Whether to add `self.client` to the JSON response. This is necessary for wallpapers
                and listings.
            auth:
                If an API key must be present for the operation to succeed.
            use_params:
                Whether to pass `self.params` to the request. This will also add them to metadata
                when requesting for listings.

        Returns:
            The response in JSON format.
        """
        params = self.params.as_dict() if use_params else None
        response = self.client.get(endpoint, auth=auth, params=params)
        data: Dict[str, Any] = response.json()

        # If we only have the `data` key, add the client inside it.
        if pass_client and len(data) == 1:
            data["data"]["client"] = self.client

        # Otherwise, if it's a listing, add it as another key.
        # We also need to add the request url and the request params for pagination.
        elif pass_client:
            data["client"] = self.client
            data["meta"]["request_url"] = str(response.url)
            data["meta"]["params"] = self.params

        return data

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

    def search(self, params_only: bool = False) -> Listing:
        """Searches for wallpapers.

        If an API key is present, the search parameters will be a mix between the user's browsing
        settings and the parameters defined in `Wallhaven.params`.

        Args:
            params_only:
                Don't use the parameters from the API key when searching, even if an API key is
                present. Searching for NSFW is not possible without an API key.

        Returns:
            An instance of `Listing` that can be used to access the wallpapers and the metadata from
            the search results.
        """
        if params_only:
            data = self._get("/search", pass_client=True, use_params=True)
        else:
            data = self._get("/search", pass_client=True, auth=True, use_params=True)

        return Listing.parse_obj(data)
