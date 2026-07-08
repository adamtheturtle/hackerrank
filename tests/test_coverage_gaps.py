"""Targeted tests for branches not exercised by the endpoint suite.

These tests cover private helpers and edge cases that the broader
suite doesn't reach (e.g. the bool/str arms of ``_coerce_int``, the
context manager hooks on the HTTP transports, and the
``HackerRankError`` registry fallback).
"""

from __future__ import annotations

from http import HTTPStatus

import httpx
import pytest
import respx

from hackerrank import async_client as ac
from hackerrank import client as sc
from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.exceptions import HackerRankError
from hackerrank.transports import (
    AsyncHTTPXTransport,
    HTTPXTransport,
    TransportResponse,
)

_BASE_URL = "https://www.hackerrank.com"


class TestCoercionHelpers:
    """Tests for the private pagination coercion helpers."""

    # pylint: disable=protected-access

    @staticmethod
    @pytest.mark.parametrize(
        argnames=("value", "expected"),
        argvalues=[
            (True, 1),
            (False, 0),
            (5, 5),
            ("7", 7),
            ("abc", 0),
            ("", 0),
            (None, 0),
            ([], 0),
        ],
    )
    def test_sync_coerce_int(
        value: object,
        expected: int,
    ) -> None:
        """Sync ``_coerce_int`` handles every documented case.

        Args:
            value: Input value to coerce.
            expected: Expected integer result.
        """
        assert sc._coerce_int(value) == expected  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    @staticmethod
    @pytest.mark.parametrize(
        argnames=("value", "expected"),
        argvalues=[
            (True, 1),
            (False, 0),
            (5, 5),
            ("7", 7),
            ("abc", 0),
            ("", 0),
            (None, 0),
            ([], 0),
        ],
    )
    def test_async_coerce_int(
        value: object,
        expected: int,
    ) -> None:
        """Async ``_coerce_int`` handles every documented case.

        Args:
            value: Input value to coerce.
            expected: Expected integer result.
        """
        assert ac._coerce_int(value) == expected  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    @staticmethod
    def test_sync_coerce_str_non_string() -> None:
        """``_coerce_str`` returns ``""`` for non-strings."""
        assert sc._coerce_str(None) == ""  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
        assert sc._coerce_str(5) == ""  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    @staticmethod
    def test_async_coerce_str_non_string() -> None:
        """Async ``_coerce_str`` returns ``""`` for non-strings."""
        assert ac._coerce_str(None) == ""  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
        assert ac._coerce_str(5) == ""  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]


class TestTransportContextManagers:
    """Tests covering the transport context-manager hooks."""

    @staticmethod
    def test_sync_transport_context_manager() -> None:
        """``HTTPXTransport`` works as a context manager."""
        with HTTPXTransport() as transport:
            assert isinstance(transport, HTTPXTransport)

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_transport_context_manager() -> None:
        """``AsyncHTTPXTransport`` works as an async context manager."""
        async with AsyncHTTPXTransport() as transport:
            assert isinstance(transport, AsyncHTTPXTransport)


class TestAsyncErrorPath:
    """Tests covering the async error-raising branch."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_error_raises() -> None:
        """An error response raises ``HackerRankError`` in async paths."""
        with respx.mock(
            base_url=_BASE_URL,
            assert_all_called=False,
        ) as router:
            router.get(url__regex=r".*/x/api/v3/tests.*").mock(
                return_value=httpx.Response(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                ),
            )
            client = AsyncHackerRank(api_key="test-key")
            try:
                with pytest.raises(expected_exception=HackerRankError):
                    await client.tests.list()
            finally:
                await client.aclose()


class TestAsyncCloseOwnership:
    """Tests covering ``AsyncHackerRank.aclose`` ownership branches."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_close_does_not_close_external_transport() -> None:
        """A custom async transport is not closed by ``aclose``."""

        class _CustomTransport:
            """A minimal async transport that never gets closed."""

            async def __call__(
                self,
                *,
                method: str,
                url: str,
                headers: dict[str, str],
                params: dict[str, str | int] | None = None,
                json: object | None = None,
                files: object | None = None,
            ) -> TransportResponse:  # pragma: no cover
                """Make a request."""
                del method, url, headers, params, json, files
                raise NotImplementedError

        client = AsyncHackerRank(
            api_key="test-key",
            transport=_CustomTransport(),
        )
        await client.aclose()


class TestHackerRankErrorRegistry:
    """Tests covering the error registry fallback paths."""

    @staticmethod
    def test_subclass_without_status_code_is_not_registered() -> None:
        """Subclasses without ``status_code`` skip registration."""

        class _UnregisteredError(HackerRankError):
            """A subclass with no status_code mapping."""

        registry = HackerRankError._registry  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]  # pylint: disable=protected-access
        assert _UnregisteredError not in registry.values()

    @staticmethod
    def test_unknown_status_falls_back_to_base_error() -> None:
        """An unmapped status returns the base ``HackerRankError``
        type.
        """
        unmapped_status = 418
        response = TransportResponse(
            status_code=unmapped_status,
            headers={},
            content=b"{}",
        )
        err = HackerRankError.from_response(response=response)
        assert type(err) is HackerRankError  # pylint: disable=unidiomatic-typecheck
        assert err.status_code == unmapped_status
        assert err.content == b"{}"


class TestStubRouterFallbacks:
    """Direct hits on the stub router's fallback branches.

    These requests go to unknown URLs so the side-effect function in
    ``test_endpoints.py`` exits each method block without matching.
    """

    @staticmethod
    @pytest.mark.parametrize(
        argnames="method",
        argvalues=["GET", "POST", "PATCH"],
    )
    def test_unknown_url_returns_empty_payload(
        method: str,
        stub_router: respx.MockRouter,
    ) -> None:
        """Unknown URLs fall through to the empty-payload return.

        Args:
            method: HTTP method to send.
            stub_router: The stub router fixture.
        """
        del stub_router
        with httpx.Client(base_url=_BASE_URL) as http_client:
            response = http_client.request(
                method=method,
                url="/never-mapped-anywhere",
            )
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {}

    @staticmethod
    def test_unknown_put_returns_no_content(
        stub_router: respx.MockRouter,
    ) -> None:
        """Unknown PUT requests fall through to the 204 default.

        Args:
            stub_router: The stub router fixture.
        """
        del stub_router
        with httpx.Client(base_url=_BASE_URL) as http_client:
            response = http_client.put(url="/never-mapped-anywhere")
        assert response.status_code == HTTPStatus.NO_CONTENT


class TestSCIMPagingEdgeCases:
    """Edge cases for SCIM pagination parsing."""

    @staticmethod
    def test_scim_users_with_missing_schemas() -> None:
        """A SCIM ``Resources`` payload with no ``schemas`` key works.

        Covers the False branch of ``isinstance(schemas_raw, list)``.
        """
        with respx.mock(
            base_url=_BASE_URL,
            assert_all_called=False,
        ) as router:
            router.get(url__regex=r".*/Users.*").mock(
                return_value=httpx.Response(
                    status_code=200,
                    json={
                        "Resources": [],
                        "startIndex": 1,
                        "itemsPerPage": 0,
                        "totalResults": 0,
                    },
                ),
            )
            client = HackerRank(api_key="test-key")
            try:
                result = client.scim.users.list()
            finally:
                client.close()
        assert result.schemas == []

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_scim_groups_with_missing_schemas() -> None:
        """Async SCIM groups list handles a missing ``schemas`` key."""
        with respx.mock(
            base_url=_BASE_URL,
            assert_all_called=False,
        ) as router:
            router.get(url__regex=r".*/Groups.*").mock(
                return_value=httpx.Response(
                    status_code=200,
                    json={
                        "Resources": [],
                        "startIndex": 1,
                        "itemsPerPage": 0,
                        "totalResults": 0,
                    },
                ),
            )
            client = AsyncHackerRank(api_key="test-key")
            try:
                result = await client.scim.list_groups()
            finally:
                await client.aclose()
        assert result.schemas == []
