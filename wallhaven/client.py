from typing import Any, Optional

import httpx

from wallhaven.errors import NotFoundError, TooManyRequestsError, UnauthorizedError


class APIClient:
    """The client used for to handle GET requests sent to the API.

    This class is supposed to be used internally only.

    Attributes:
        API_URL: The base url for the API.

    Examples:
        >>> from wallhaven.client import APIClient
        >>> client = APIClient()
        >>> client.get(<url>)
        <Response [200 OK]>
    """

    API_URL = "https://wallhaven.cc/api/v1"

    def __init__(
        self, api_key: Optional[str] = None, *, timeout: int = 20, retries: int = 1
    ) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries

        transport = httpx.HTTPTransport(retries=self.retries)
        self.client = httpx.Client(base_url=self.API_URL, timeout=self.timeout, transport=transport)
        self.client.event_hooks["response"] = [self._check_for_errors]
        if self.api_key:
            self.client.headers["X-API-KEY"] = self.api_key

    def _check_for_errors(self, response: httpx.Response) -> None:
        """Check for HTTP errors in a ``httpx.Response`` object."""
        sc = response.status_code
        if sc in (400, 404):
            raise NotFoundError(f"Unable to find resource {response.url}")
        elif sc == 401:
            raise UnauthorizedError(f"Invalid API key. Unable to request {response.url}")
        elif sc == 429:
            raise TooManyRequestsError("The request limit has been exceeded.")

        # Check for other 4xx or 5xx errors.
        response.raise_for_status()

    def _prepare_request(self, endpoint: str, auth: bool = False, **kwargs: Any) -> httpx.Request:
        """Build and prepare a custom GET request.

        Args:
            endpoint: The address to request. It can be both a full url (https://...) or an
                endpoint (/tag/...)
            auth: If an API key is required for this operation.
            **kwargs: Additional keyword arguments that ``httpx.Client.build_request`` takes.

        Returns:
            The custom ``httpx.Request`` instance.

        Raises:
            ``UnauthorizedError``: If ``auth`` is True, but an API key is not present.
        """
        request = self.client.build_request("GET", endpoint, **kwargs)

        # Avoid sending a request we know it's invalid.
        if auth and not request.headers.get("X-API-KEY"):
            raise UnauthorizedError(f"You need an API key to request: {request.url}")

        return request

    def get(
        self, endpoint: str, auth: bool = False, stream: bool = False, **kwargs: Any
    ) -> httpx.Response:
        """Send a GET request to endpoint.

        Args:
            endpoint: The address to request. It can be both a full url (https://...) or an
                endpoint (/tag/...)
            auth: If an API key is required for this operation.
            stream: Whether to avoid loading the entire response body into memory at once.
            **kwargs: Additional keyword arguments that ``httpx.Client.build_request`` takes.
        """
        request = self._prepare_request(endpoint, auth, **kwargs)
        response = self.client.send(request, stream=stream)

        return response
