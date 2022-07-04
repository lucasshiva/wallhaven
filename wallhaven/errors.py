class WallhavenError(Exception):
    pass


class NotFoundError(WallhavenError):
    pass


class UnauthorizedError(WallhavenError):
    pass


class TooManyRequestsError(WallhavenError):
    pass
