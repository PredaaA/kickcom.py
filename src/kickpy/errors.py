from aiohttp import ClientResponse


class KickpyException(Exception):
    """Base exception class for Kickpy errors."""


class MissingArgument(KickpyException):
    """Raised when a required argument is missing."""


class NoClientId(KickpyException):
    """Raised when no client_id is provided."""


class NoClientSecret(KickpyException):
    """Raised when no client_secret is provided."""


class HTTPException(KickpyException):
    """Base exception class for HTTP errors."""

    def __init__(self, response: ClientResponse, message: str | None = None) -> None:
        self.response: ClientResponse = response
        self.status: int = response.status
        self.message: str | None = message

        super().__init__(message)


class NotFound(HTTPException):
    """Raised when a resource is not found."""


class Unauthorized(HTTPException):
    """Raised when a request is unauthorized."""


class BadRequest(HTTPException):
    """Raised when a request is bad."""


class Forbidden(HTTPException):
    """Raised when a request is forbidden."""


class Ratelimited(HTTPException):
    """Raised when a request is ratelimited."""

    # def __init__(self, response: ClientResponse, message: str | None, retry_after: int):
    #     super().__init__(response, message)
    #     self.retry_after: int = retry_after


class InternalServerError(HTTPException):
    """Raised when a server error occurs."""
