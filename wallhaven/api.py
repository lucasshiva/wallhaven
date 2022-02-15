from os import getenv
from typing import List, Optional, Union

from wallhaven.models.api import (
    Collection,
    CollectionListing,
    SearchResults,
    Tag,
    UserSettings,
    Wallpaper,
)
from wallhaven.session import RequestHandler


class API:
    """Interface for the Wallhaven API v1.

    Args:
        api_key: The key grants access to some operations. To get one, log in to ``Wallhaven`` and
            go to your account settings.
        timeout: How much time (in seconds) to wait for the server's response.

    Attributes:
        params: The parameters used when searching for wallpapers.

    Examples:
        >>> import wallhaven
        >>> api = wallhaven.API(<key>, <timeout>)
        >>> api.get_wallpaper(<id>)
        <Wallpaper(...)>
    """

    BASE_URL = "https://wallhaven.cc/api/v1/"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 10) -> None:
        self.api_key = api_key or getenv("WALLHAVEN_API_KEY")
        self.timeout = timeout

        # The session used for the requests. It will also be used by the models when needed.
        self._session = RequestHandler(api_key, timeout)

        # The default parameters used when searching for wallpapers.
        # For more information, see `https://wallhaven.cc/help/api#search`.
        self._default_params: dict = {
            "categories": "111",
            "purity": "100",
            "sorting": "toplist",  # Set to toplist instead of the default 'date_added'.
            "order": "desc",
            "topRange": "1M",
            "page": "1",
        }

        # The parameters the user will interact with.
        # By default, if an API key is present, Wallhaven uses the search parameters from the key.
        # But, if the user explicitly set parameters, then I want Wallhaven to use those instead.
        self.params: dict = {}

    def get_wallpaper(self, id: str) -> Wallpaper:
        """Get wallpaper from id.

        Args:
            id: The wallpaper id, e.g., "8oxreo"

        Returns:
            An instance of ``Wallpaper``

        Raises:
            ``UnauthorizedRequest``: API key is invalid or inexistent.
            ``NotFoundError``: Wallpaper not found.
            ``TooManyRequests``: The request limit of 45/min has been exceeded.

        Examples:
            >>> w = get_wallpaper("8oxreo")
            <Wallpaper(id="8oxreo", ..)>
        """
        r = self._session.get(f"/w/{id}")
        w = Wallpaper.from_response(r)
        w._set_session(self._session)
        return w

    def get_tag(self, id: Union[int, str]) -> Tag:
        """Get tag from id.

        Args:
            id: The tag id, e.g., 120

        Returns:
            An instance of ``Tag``

        Raises:
            ``NotFoundError``: ID is invalid or inexistent
            ``TooManyRequests``: The request limit of 45/min has been exceeded.

        Examples:
            >>> w = get_tag(120)
            <Tag(id=120, ..)>
        """
        r = self._session.get(f"/tag/{id}")
        t = Tag.from_response(r)
        return t

    def get_user_settings(self) -> UserSettings:
        """Fetch an authenticated user's settings.

        Returns:
            An instance of ``UserSettings``.

        Raises:
            ``UnauthorizedRequest``: API key is invalid or inexistent.
            ``TooManyRequests``: The request limit of 45/min has been exceeded.

        Examples:
            >>> get_user_settings()
            <UserSettings(...)>
        """
        r = self._session.get("/settings", auth=True)
        return UserSettings.from_response(r)

    def get_collections(self, username: Optional[str] = None) -> List[Collection]:
        """Get collections from an username or API key.

        Fetch an user's public collections from a given username, or all (public and private)
        collections from an authenticated user.

        If an username is passed, this method will fetch the collections from the username, even if
        an API key has been provided.

        Args:
            username: The username from wallhaven.

        Returns:
            A list of ``Collection`` objects.

        Raises:
            ``UnauthorizedRequest``: API key is invalid or inexistent.
            ``NotFoundError``: Username not found.
            ``TooManyRequests``: The request limit of 45/min has been exceeded.

        Examples:
            Fetch public collections from any user:
            >>> get_collections(<username>)
            <[Collection(..), Collection(..), ..]>

            Fetch all collections from an authenticated user:
            >>> get_collections()
            <[Collection(..), Collection(..), ..]>
        """
        if username:
            r = self._session.get(f"/collections/{username}")
        else:
            r = self._session.get("/collections", auth=True)

        # Wallhaven requires that users have at least one collection, however, if
        # they only have one collection and it's marked as private, the API will return
        # an empty list when fetching collections from a given username. This is not the
        # case when fetching collections using the API key, since the response will have
        # at least one collection.
        collections: list = r.json()["data"]
        if collections:
            collections = [Collection.from_dict(c) for c in collections]
        return collections

    def get_collection_listing(self, username: str, collection_id: int) -> CollectionListing:
        """View collection listing.

        An API key is required to view the listing of a private collection.

        Args:
            username: The username from wallhaven.
            collection_id: The collection id.

        Returns:
            An instance of ``CollectionListing``.

        Raises:
            ``UnauthorizedRequest``: API key is invalid or inexistent.
            ``NotFoundError``: Username or ID not found.
            ``TooManyRequests``: The request limit of 45/min has been exceeded.

        Examples:
            >>> listing = get_collection_listing(<username>, <collection_id>)
            <CollectionListing(data=[Wallpaper(..), ...], meta=Meta(..))>
        """
        r = self._session.get(f"/collections/{username}/{collection_id}")
        return CollectionListing.from_response(r)

    def search(self) -> SearchResults:
        """Perform a search.

        If you provide an API key with no extra parameters, search will be performed
        with the user's browsing settings and default filters. With no additional
        parameters, the search will display the latest SFW wallpapers. See the parameter
        list at `https://wallhaven.cc/help/api` to access other listings.

        If you provide both an API key and search parameters, `Wallhaven` will merge the
        parameters defined in both, but with the search parameters having priority over
        the ones in your browsing settings. For example, if you set `purity` to only
        display `sketchy` wallpapers in your browsing settings, even when providing an API
        key the search will always retrieve `sketchy` wallpapers, unless you explicitly
        state otherwise in the search parameters.

        Also, the only way to retrieve more than 24 results per page is to change the
        `Thumbs Per Page` option in your browsing settings and providing an API key
        whenever performing a search.

        Returns:
            An instance of ``SearchResults``.

        Raises:
            ``NotFoundError``: If a parameter is deemed as invalid.
            ``TooManyRequests``: The request limit of 45/min has been exceeded.
        """
        if self.params:
            r = self._session.get("/search", params=self.params)
        elif self.api_key:
            # Automatically uses the parameters in the user browsing settings.
            r = self._session.get("/search")
        else:
            # Wallhaven uses the default parameters automatically, but I want it to be explicit.
            r = self._session.get("/search", params=self._default_params)

        return SearchResults.from_response(r)
