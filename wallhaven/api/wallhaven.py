"""Provides Wallhaven to interact with the Wallhaven API."""
from typing import Dict, List, Optional, Union

from wallhaven.api import API_ENDPOINTS
from wallhaven.exceptions import ApiKeyError
from wallhaven.models import Collection, CollectionListing, Tag, UserSettings, Wallpaper
from wallhaven.session import RequestHandler


class Wallhaven:
    """A wrapper around the Wallhaven API.

    Basic Usage:
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
        # so we don't need to set the headers right now. We will later improve this
        # class, so that we can add things like timeouts, retries and cache.
        self.handler = RequestHandler()

    @staticmethod
    def _get_collections_from_response(response: Dict[str, list]) -> List[Collection]:
        """Get a list of `Collection` objects from a given response.

        This is a helper method and it's not meant to be used by users. It is supposed
        to be used only internally by `Wallhaven` when requesting for collections. This
        method is only needed if we have two separate methods for requesting
        collections: by username and by API key.

        Args:
            response (dict): The json-encoded content of a `requests.Response` object.

        Returns:
            A list of `Collection` objects or an empty list for when no collections are
                found.
        """
        # Wallhaven requires that users have at least one collection, however, if
        # they only have one collection and it's marked as private, the API will return
        # an empty list when fetching collections from a given username. This is not the
        # case when fetching collections using the API key, since the response will have
        # at least one collection.
        collections: list = response["data"]
        if collections:
            collections = [Collection.from_dict(c) for c in collections]
        return collections

    def _get_collection_listing(
        self, username: str, collection_id: int, private: bool = False
    ) -> CollectionListing:
        """Get the listing of wallpapers in a collection.

        This is a internal method that is shared between `get_collection_listing` and
        `get_private_collection_listing`. It is not supposed to be used on its own, but
        through those two methods. This method does NOT check if the API key exists.

        Args:
            username (str): A string representing the collection's owner.
            collection_id (int): An integer representing the collection's ID.
            private (bool): Whether the collection is private (True) or public (False).

        Returns:
            A `CollectionListing` object that provides a list of wallpapers and meta
            information that can be used as pagination.
        """
        # Same endpoint for both public and private collection listing.
        url = API_ENDPOINTS["collection_listing"].format(
            username=username, id=collection_id
        )

        if private:
            response = self.handler.get_json(url, headers=self.headers)
        else:
            response = self.handler.get_json(url)

        # Add the request URL to the meta dict.
        # This URL will be later used for pagination, as we only need to append
        # "?page=<n>" to the URL.
        response["meta"]["request_url"] = url

        # Since we also need the `meta` key inside the dictionary, we can't use
        # `response["data"]` in here.
        return CollectionListing.from_dict(response)

    def get_wallpaper(self, wallpaper_id: str) -> Wallpaper:
        """Get wallpaper from a given ID. An API key is required for NSFW wallpapers.

        Args:
            wallpaper_id (str): The wallpaper ID, e.g "8oxreo".

        Returns:
            An instance of a `Wallpaper` object.
        """
        url = API_ENDPOINTS["wallpaper"].format(id=wallpaper_id)
        response = self.handler.get_json(url, headers=self.headers)
        return Wallpaper.from_dict(response["data"])

    def get_tag(self, tag_id: Union[str, int]) -> Tag:
        """Get tag from a given ID.

        Args:
            tag_id (str | int): An integer or a numeric string representing the Tag id.

        Returns:
            An instance of a `Tag` object.
        """
        url = API_ENDPOINTS["tag"].format(id=tag_id)
        response = self.handler.get_json(url)
        return Tag.from_dict(response["data"])

    def get_user_settings(self) -> UserSettings:
        """Read an authenticated user's settings from the API key.

        Returns:
            An instance of a `UserSettings` object.

        Raises:
            ApiKeyError: For an invalid API key or when one is not provided.
        """
        if self.api_key is None:
            raise ApiKeyError("An API key is required to read an user's settings.")

        url = API_ENDPOINTS["settings"]
        response = self.handler.get_json(url, headers=self.headers)
        return UserSettings.from_dict(response["data"])

    def get_user_collections(self, username: str) -> List[Collection]:
        """Get the collections of a given user.

        Fetching the collections by username only returns public collections.
        If you want to fetch all collections (including private ones), you need to
        provide an API key and call `get_collections` instead.

        Args:
            username (str): The collections' owner.

        Returns:
            A list of `Collection` objects or an empty list if no collections are found.
            This will only happen if the user has only one collection and it's marked as
            private. In this case, use `get_collections` with an API key.

        """
        url = API_ENDPOINTS["collection"].format(username=username)
        response = self.handler.get_json(url)
        return self._get_collections_from_response(response)

    def get_collections(self) -> List[Collection]:
        """Get all collections (including private ones) from an authenticated user.
        This operation requires an API key.

        Returns:
            A list of `Collection` objects. At least one (1) collection should always be
            present.

        Raises:
            ApiKeyError: For an invalid API key or when one is not provided.
        """
        if self.api_key is None:
            raise ApiKeyError(
                "An API key is required to get collections from an authenticated user."
            )
        url = API_ENDPOINTS["collection_apikey"]
        response = self.handler.get_json(url, headers=self.headers)
        return self._get_collections_from_response(response)

    def get_collection_listing(
        self, username: str, collection_id: int
    ) -> CollectionListing:
        """Get the listing of wallpapers from a public collection.

        Args:
            username (str): A string representing the collection's owner.
            collection_id (int): An integer representing the collection's ID.

        Returns:
            A `CollectionListing` object that provides a list of wallpapers and meta
            information that can be used as pagination.
        """
        return self._get_collection_listing(username, collection_id)

    def get_private_collection_listing(
        self, username: str, collection_id: int
    ) -> CollectionListing:
        """Get the listing of wallpapers from a private collection.
        An API key is needed for this operation to work.

        Args:
            username (str): A string representing the collection's owner.
            collection_id (int): An integer representing the collection's ID.

        Returns:
            A `CollectionListing` object that provides a list of wallpapers and meta
            information that can be used as pagination.

        Raises:
            ApiKeyError: For an invalid API key or when one is not provided.
        """
        if self.api_key is None:
            raise ApiKeyError(
                "An API key is required to access the listing of wallpapers in a "
                + "private collection."
            )

        return self._get_collection_listing(username, collection_id, private=True)
