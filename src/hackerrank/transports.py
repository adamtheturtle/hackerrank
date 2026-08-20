"""Transport abstractions for the HackerRank for Work API."""

import json as json_module
from collections.abc import Mapping
from dataclasses import dataclass
from http import HTTPStatus
from types import TracebackType
from typing import Any, Protocol, Self, runtime_checkable

import httpx
from beartype import beartype

from hackerrank.types import JSONValue


class HTTPStatusError(Exception):
    """Raised when an HTTP response has an error status code."""

    def __init__(
        self,
        *,
        status_code: int,
        content: bytes,
    ) -> None:
        """Create a new HTTP status error.

        Args:
            status_code: The HTTP status code.
            content: The response body.
        """
        message = f"HTTP {status_code}"
        super().__init__(message)
        self.status_code = status_code
        self.content = content


@beartype
@dataclass(frozen=True, kw_only=True)
class TransportResponse:
    """A response from a transport."""

    status_code: int
    headers: dict[str, str]
    content: bytes

    def json(self) -> Any:  # noqa: ANN401
        """Parse the response body as JSON.

        Returns:
            The parsed JSON data.
        """
        return json_module.loads(s=self.content)

    def raise_for_status(self) -> None:
        """Raise an error if the response has an error status.

        Raises:
            HTTPStatusError: If the status code is 300 or above.
        """
        if self.status_code >= HTTPStatus.MULTIPLE_CHOICES:
            raise HTTPStatusError(
                status_code=self.status_code,
                content=self.content,
            )


@runtime_checkable
class Transport(Protocol):
    """Protocol for HTTP transports.

    A transport is a callable that makes an HTTP request and
    returns a ``TransportResponse``.
    """

    def __call__(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        params: dict[str, str | int] | None,
        json: Mapping[str, JSONValue] | None,
        files: Mapping[str, Any] | None,
    ) -> TransportResponse:
        """Make an HTTP request.

        Args:
            method: The HTTP method (e.g. ``GET``, ``POST``).
            url: The full URL to request.
            headers: Headers to send with the request.
            params: Query parameters.
            json: A JSON-serialisable body. When provided the
                ``Content-Type`` header is set to
                ``application/json``.
            files: Files to send as multipart form-data.

        Returns:
            A ``TransportResponse`` populated from the HTTP
            response.
        """
        ...  # pylint: disable=unnecessary-ellipsis


@beartype
class HTTPXTransport:
    """HTTP transport using the ``httpx`` library.

    This is the default transport. It uses a shared
    ``httpx.Client`` for connection pooling.
    """

    def __init__(self) -> None:
        """Create a new HTTPX transport."""
        self._client = httpx.Client()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> Self:
        """Enter the context manager.

        Returns:
            This transport instance.
        """
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager and close the client."""
        self.close()

    def __call__(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        params: dict[str, str | int] | None,
        json: Mapping[str, JSONValue] | None,
        files: Mapping[str, Any] | None,
    ) -> TransportResponse:
        """Make an HTTP request using ``httpx``.

        Args:
            method: The HTTP method.
            url: The full URL.
            headers: Request headers.
            params: Query parameters.
            json: A JSON-serialisable body.
            files: Files to send as multipart form-data.

        Returns:
            A ``TransportResponse`` populated from the httpx
            response.
        """
        response = self._client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            files=files,
        )
        return TransportResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            content=response.content,
        )


@runtime_checkable
class AsyncTransport(Protocol):
    """Protocol for async HTTP transports."""

    async def __call__(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        params: dict[str, str | int] | None,
        json: Mapping[str, JSONValue] | None,
        files: Mapping[str, Any] | None,
    ) -> TransportResponse:
        """Make an async HTTP request.

        Args:
            method: The HTTP method.
            url: The full URL to request.
            headers: Headers to send with the request.
            params: Query parameters.
            json: A JSON-serialisable body.
            files: Files to send as multipart form-data.

        Returns:
            A ``TransportResponse`` populated from the HTTP
            response.
        """
        ...  # pylint: disable=unnecessary-ellipsis


@beartype
class AsyncHTTPXTransport:
    """Async HTTP transport using the ``httpx`` library."""

    def __init__(self) -> None:
        """Create a new async HTTPX transport."""
        self._client = httpx.AsyncClient()

    async def aclose(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> Self:
        """Enter the async context manager.

        Returns:
            This transport instance.
        """
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
        /,
    ) -> None:
        """Exit the async context manager and close."""
        await self.aclose()

    async def __call__(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        params: dict[str, str | int] | None,
        json: Mapping[str, JSONValue] | None,
        files: Mapping[str, Any] | None,
    ) -> TransportResponse:
        """Make an async HTTP request using ``httpx``.

        Args:
            method: The HTTP method.
            url: The full URL.
            headers: Request headers.
            params: Query parameters.
            json: A JSON-serialisable body.
            files: Files to send as multipart form-data.

        Returns:
            A ``TransportResponse`` populated from the httpx
            response.
        """
        response = await self._client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            files=files,
        )
        return TransportResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            content=response.content,
        )
