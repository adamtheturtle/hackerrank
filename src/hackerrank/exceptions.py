"""Custom exception hierarchy for the HackerRank API."""

from http import HTTPStatus
from typing import ClassVar

from hackerrank.transports import TransportResponse


class HackerRankError(Exception):
    """Base exception for all HackerRank API errors.

    Attributes:
        response: The full transport response for debugging.
        status_code: The HTTP status code.
        content: The response body.
    """

    _registry: ClassVar[dict[int, type["HackerRankError"]]] = {}

    def __init_subclass__(
        cls,
        *,
        status_code: HTTPStatus | None = None,
    ) -> None:
        """Register subclass for a specific HTTP status code.

        Args:
            status_code: The HTTP status code to map.
        """
        super().__init_subclass__()
        if status_code is not None:
            HackerRankError._registry[status_code.value] = cls

    def __init__(
        self,
        *,
        response: TransportResponse,
    ) -> None:
        """Create a new HackerRank error.

        Args:
            response: The transport response that caused
                the error.
        """
        message = f"HTTP {response.status_code}"
        super().__init__(message)
        self.response: TransportResponse = response
        self.status_code: int = response.status_code
        self.content: bytes = response.content

    @classmethod
    def from_response(
        cls,
        *,
        response: TransportResponse,
    ) -> "HackerRankError":
        """Create the appropriate exception for a response.

        Uses the registry to find a specific exception class
        for the response's status code, falling back to
        ``HackerRankError``.

        Args:
            response: The transport response.

        Returns:
            The appropriate exception instance.
        """
        exc_cls = cls._registry.get(
            response.status_code,
            HackerRankError,
        )
        return exc_cls(response=response)


class BadRequestError(
    HackerRankError,
    status_code=HTTPStatus.BAD_REQUEST,
):
    """Raised for 400 Bad Request responses."""


class AuthenticationError(
    HackerRankError,
    status_code=HTTPStatus.UNAUTHORIZED,
):
    """Raised for 401 Unauthorized responses."""


class ForbiddenError(
    HackerRankError,
    status_code=HTTPStatus.FORBIDDEN,
):
    """Raised for 403 Forbidden responses."""


class NotFoundError(
    HackerRankError,
    status_code=HTTPStatus.NOT_FOUND,
):
    """Raised for 404 Not Found responses."""


class ConflictError(
    HackerRankError,
    status_code=HTTPStatus.CONFLICT,
):
    """Raised for 409 Conflict responses."""


class UnprocessableEntityError(
    HackerRankError,
    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
):
    """Raised for 422 Unprocessable Entity responses."""


class RateLimitError(
    HackerRankError,
    status_code=HTTPStatus.TOO_MANY_REQUESTS,
):
    """Raised for 429 Too Many Requests responses."""


class ServerError(
    HackerRankError,
    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
):
    """Raised for 500 Internal Server Error responses."""
