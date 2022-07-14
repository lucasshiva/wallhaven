from typing import Any, Dict, Optional, Union

from wallhaven.models import Listing, Wallpaper
from wallhaven.search import SearchParameters
from wallhaven.config import APISettings
from wallhaven.client import APIClient


ParamTypes = Union[Dict[str, Any], SearchParameters]


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
            params = SearchParameters.from_dict(params)
        self.params = params

        self.client = APIClient(settings=self.settings)

    def _get(
        self,
        endpoint: str,
        *,
        pass_client: bool = False,
        auth: bool = False,
        params: Optional[Dict[str, Any]] = None,
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
        response = self.client.get(endpoint, auth=auth, params=params)
        data: Dict[str, Any] = response.json()

        # We need to add the request url and the request params for pagination.
        if len(data) == 2:
            data["meta"]["request_url"] = str(response.url)
            data["meta"]["params"] = (
                SearchParameters.from_dict(params) if params else SearchParameters()
            )
            data["meta"]["api_key"] = True if self.settings.api_key else False

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
        data: dict = self._get(f"/w/{id}", pass_client=True)["data"]
        wallpaper = Wallpaper.parse_obj(data)
        wallpaper._client = self.client
        return wallpaper

    def search(self, *, default: bool = False) -> Listing:
        """Searches for wallpapers.

        If an API key is provided, searches will be performed using the user's browsing settings
        and default filters.

        With no additional parameters the search will display the latest SFW wallpapers.

        Any additional parameters will override existing parameters.

        Args:
            default:
                Perform the search using only the default parameters, even if an API key is present.

        Returns:
            An instance of `Listing` that can be used to access the wallpapers and the metadata from
            the search results.
        """
        if default:
            params = SearchParameters().as_dict()
        else:
            params = self.params.as_dict(skip_defaults=True)

        # We can't use `auth=True` in here since we don't know if the API key is required or not.
        data = self._get("/search", pass_client=True, params=params)
        listing = Listing.parse_obj(data)
        listing._client = self.client
        return listing
