"""Provides RequestHandler to handle synchronous GET requests."""

import requests


class RequestHandler:
    """A synchronous request handler to handle GET requests.

    This class is for internal uses only. It is supposed to be used when requesting the
    API and when downloading wallpapers (from an URL).

    Usage:

    >>> handler = RequestHandler(timeout)
    >>> response = handler.get(url, **kwargs)
    <Response [200]>
    """

    @staticmethod
    def _check_for_errors(response: requests.Response, *args, **kwargs) -> None:
        """Check for HTTP errors in a `Response` object."""
        response.raise_for_status()

    @property
    def session(self) -> requests.Session:
        """Create a custom `requests.Session` object.

        This custom session runs a hook to ensure `raise_for_status()` is called for
        each response object.

        Returns:
            The modified `requests.Session` object.
        """
        session = requests.Session()

        # `requests` offers the shorthand helper `raise_for_status()` which asserts
        # that the response HTTP status code is not a 4xx or a 5xx, i.e that the
        # requests didn't result in a client or a server error. This can get
        # repetitive if you need to use raise_for_status() for each call.
        # Luckily the requests library offers a 'hooks' interface where you can attach
        # callbacks on certain parts of the request process. We can use hooks to ensure
        # raise_for_status() is called for each response object.
        session.hooks["response"] = [self._check_for_errors]
        return session

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
        response = self.session.get(url, **kwargs)
        response.encoding = "utf-8"
        return response