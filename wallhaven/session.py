"""Provides RequestHandler to handle synchronous GET requests."""

from typing import Any, Dict, Optional

import requests

from wallhaven.exceptions import ApiKeyError, TooManyRequestsError


class RequestHandler:
    """A synchronous request handler to handle GET requests.

    This class is for internal uses only. It is supposed to be used when requesting the
    API and when downloading wallpapers (from an URL).

    Usage:

    >>> handler = RequestHandler()
    >>> response = handler.get(url, **kwargs)
    <Response [200]>
    """

    def __init__(self, timeout: Optional[int] = None) -> None:
        self.timeout = timeout
        self.session = requests.Session()

        # `requests` offers the shorthand helper `raise_for_status()` which asserts
        # that the response HTTP status code is not a 4xx or a 5xx, i.e that the
        # requests didn't result in a client or a server error. This can get
        # repetitive if you need to use raise_for_status() for each call.
        # Luckily the requests library offers a 'hooks' interface where you can attach
        # callbacks on certain parts of the request process. We can use hooks to ensure
        # raise_for_status() is called for each response object.
        self.session.hooks["response"] = [self._check_for_errors]

    @staticmethod
    def _check_for_errors(response: requests.Response, *args, **kwargs) -> None:
        """Check for HTTP errors in a `Response` object."""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.status_code == 401:
                raise ApiKeyError(
                    "The API key is invalid. Please check if everything is correct or "
                    + "regenerate your API key."
                )
            elif response.status_code == 429:
                raise TooManyRequestsError(
                    "You've exceeded the limit of 45 API calls per minute. Please try "
                    + "again later!"
                )
            else:
                raise

    def get(self, url: str, **kwargs) -> requests.Response:
        """Send a GET request.

        Args:
            url: The endpoint to request.
            **kwargs: Optional keyword arguments that `requests.get` takes.

        Returns:
            A `requests.Response` object encoded in UTF-8.

        Raises:
            `requests.exceptions.HTTPError`: For any HTTP errors that ocurred.
        """
        timeout = kwargs.pop("timeout", self.timeout)
        response = self.session.get(url, timeout=timeout, **kwargs)
        response.encoding = "UTF-8"
        return response

    def get_json(self, url: str, **kwargs) -> Dict[str, Any]:
        """Send a GET request and parse it as json.

        Args:
            url (str): The endpoint to request.
            **kwargs: Optional keyword arguments that `requests.get` takes.

        Returns:
            The json-encoded content of the `Response` object.

        Raises:
            `requests.exceptions.HTTPError`: For any HTTP errors that ocurred.
            ValueError: If the response body does not contain valid json.
        """
        response = self.get(url, **kwargs)
        return response.json()


handler = RequestHandler(timeout=30)
