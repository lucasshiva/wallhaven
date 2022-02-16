from typing import Any, Optional

import httpx

from wallhaven.exceptions import NotFoundError, TooManyRequests, UnauthorizedError


class RequestHandler:
    """A synchronous request handler to handle GET requests.

    This class is for internal uses only. It is supposed to be used when requesting the
    API and when interacting with models.
    """

    BASE_URL = "https://wallhaven.cc/api/v1"
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout

        self.client = httpx.Client(base_url=self.BASE_URL, timeout=self.timeout)
        self.client.event_hooks["response"] = [self._check_for_errors]
        self.client.headers["User-Agent"] = self.USER_AGENT
        if self.api_key:
            self.client.headers["X-API-KEY"] = self.api_key

    def _check_for_errors(self, response: httpx.Response) -> None:
        """Check for HTTP errors in a ``httpx.Response`` object."""
        sc = response.status_code
        if sc in (400, 404):
            raise NotFoundError(f"Unable to find resource {response.url}")
        elif sc == 401:
            if self.api_key:
                raise UnauthorizedError(f"Invalid API key. Unable to request {response.url}")
            else:
                raise UnauthorizedError(f"API key not found. Unable to request {response.url}")
        elif sc == 429:
            raise TooManyRequests("The request limit has been exceeded.")

        # Check for other 4xx or 5xx errors.
        response.raise_for_status()

    def _prepare_request(self, endpoint: str, auth: bool = False, **kwargs: Any) -> httpx.Request:
        """Build and prepare a custom GET request.

        Args:
            endpoint: The address to request. It can be both a full url (https://..) or an
                endpoint (/tag/..)
            auth: If an API key is required. Defaults to ``False``.
            **kwargs: Additional keyword arguments that ``httpx.Client.build_request`` takes.

        Returns:
            The custom ``httpx.Request`` instance.

        Raises:
            ``UnauthorizedError``: When an operation requires an API key, yet none has been found.
        """
        request = self.client.build_request("GET", endpoint, **kwargs)

        # Avoid sending a request we known it's going to return an error.
        if auth and not request.headers.get("X-API-KEY"):
            raise UnauthorizedError(f"You need an API key to request: {request.url}")

        return request

    def get(self, endpoint: str, auth: bool = False, **kwargs: Any) -> httpx.Response:
        """Send a GET request to endpoint."""
        stream = kwargs.pop("stream", False)
        request = self._prepare_request(endpoint, auth, **kwargs)
        response = self.client.send(request, stream=stream)

        return response
