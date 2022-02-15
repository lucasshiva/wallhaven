class UnauthorizedError(Exception):
    """Missing or invalid API key."""

    pass


class TooManyRequests(Exception):
    """The request limit has been exceeded."""

    pass


class NotFoundError(Exception):
    """Unable to find resource."""

    pass
