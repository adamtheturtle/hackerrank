"""Targeted tests for branches not exercised by the endpoint suite.

These tests cover private helpers and edge cases that the broader
suite doesn't reach (e.g. the bool/str arms of ``_coerce_int``, the
context manager hooks on the HTTP transports, and the
``HackerRankError`` registry fallback).
"""

from __future__ import annotations

from http import HTTPStatus
from typing import Any, cast

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
                params: dict[str, str | int] | None,
                json: object | None,
                files: object | None,
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
        with respx.mock(assert_all_called=False) as router:
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
        with respx.mock(assert_all_called=False) as router:
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
                result = await client.scim.groups.list()
            finally:
                await client.aclose()
        assert result.schemas == []


class TestSCIMStartIndex:
    """Preserve an explicit SCIM ``startIndex`` of zero."""

    @staticmethod
    def test_sync_preserves_zero_start_index() -> None:
        """A server ``startIndex`` of ``0`` is kept as ``0``."""
        with respx.mock(assert_all_called=False) as router:
            router.get(url__regex=r".*/Users.*").mock(
                return_value=httpx.Response(
                    status_code=200,
                    json={
                        "Resources": [],
                        "startIndex": 0,
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
        assert result.start_index == 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_preserves_zero_start_index() -> None:
        """Async list keeps a server ``startIndex`` of ``0``."""
        with respx.mock(assert_all_called=False) as router:
            router.get(url__regex=r".*/Groups.*").mock(
                return_value=httpx.Response(
                    status_code=200,
                    json={
                        "Resources": [],
                        "startIndex": 0,
                        "itemsPerPage": 0,
                        "totalResults": 0,
                    },
                ),
            )
            client = AsyncHackerRank(api_key="test-key")
            try:
                result = await client.scim.groups.list()
            finally:
                await client.aclose()
        assert result.start_index == 0


class TestBaseURLJoining:
    """Custom base URLs must not produce double-slash paths."""

    @staticmethod
    def test_trailing_slash_does_not_double_slash_path() -> None:
        """A trailing slash on ``base_url`` is stripped before join."""
        captured: list[str] = []

        class _SpyTransport:
            """Capture the absolute URL of each request."""

            def __call__(
                self,
                *,
                method: str,
                url: str,
                headers: dict[str, str],
                params: dict[str, str | int] | None,
                json: object | None,
                files: object | None,
            ) -> TransportResponse:
                """Record ``url`` and return an empty page."""
                del method, headers, params, json, files
                captured.append(url)
                return TransportResponse(
                    status_code=200,
                    headers={},
                    content=(
                        b'{"data":[],"page_total":0,"offset":0,'
                        b'"previous":"","next":"","first":"",'
                        b'"last":"","total":0}'
                    ),
                )

        client = HackerRank(
            api_key="test-key",
            base_url="https://example.test/",
            transport=_SpyTransport(),
        )
        client.users.list()
        assert captured == ["https://example.test/x/api/v3/users"]


class TestGenerateCodestubsBody:
    """``generate_codestubs`` requires a request body."""

    @staticmethod
    def test_sync_requires_body() -> None:
        """Omitting ``body`` is rejected locally."""
        client = HackerRank(api_key="test-key")
        generate = cast("Any", client.questions.generate_codestubs)
        with pytest.raises(expected_exception=TypeError):
            generate(question_id="q1")

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_requires_body() -> None:
        """Omitting ``body`` is rejected locally in the async client."""
        client = AsyncHackerRank(api_key="test-key")
        generate = cast("Any", client.questions.generate_codestubs)
        with pytest.raises(expected_exception=TypeError):
            await generate(question_id="q1")


class TestSCIMPatchMessage:
    """SCIM PATCH returns a message acknowledgement, not a resource."""

    @staticmethod
    def test_sync_user_patch_returns_message() -> None:
        """User PATCH parses the documented message payload."""
        with respx.mock(assert_all_called=False) as router:
            router.patch(url__regex=r".*/Users/.*").mock(
                return_value=httpx.Response(
                    status_code=200,
                    json={
                        "schemas": [
                            "urn:ietf:params:scim:schemas:core:2.0:User",
                        ],
                        "message": "Successful transaction",
                    },
                ),
            )
            client = HackerRank(api_key="test-key")
            try:
                result = client.scim.users.patch(
                    scim_user_id="scim-1",
                    operations=[{"op": "replace"}],
                )
            finally:
                client.close()
        assert result.message == "Successful transaction"

    @staticmethod
    def test_sync_group_patch_returns_message() -> None:
        """Group PATCH parses the documented message payload."""
        with respx.mock(assert_all_called=False) as router:
            router.patch(url__regex=r".*/Groups/.*").mock(
                return_value=httpx.Response(
                    status_code=200,
                    json={
                        "schemas": [
                            "urn:ietf:params:scim:schemas:core:2.0:Group",
                        ],
                        "message": "Successful transaction",
                    },
                ),
            )
            client = HackerRank(api_key="test-key")
            try:
                result = client.scim.groups.patch(
                    scim_group_id="scim-2",
                    operations=[{"op": "replace"}],
                )
            finally:
                client.close()
        assert result.message == "Successful transaction"

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_user_patch_returns_message() -> None:
        """Async user PATCH parses the documented message payload."""
        with respx.mock(assert_all_called=False) as router:
            router.patch(url__regex=r".*/Users/.*").mock(
                return_value=httpx.Response(
                    status_code=200,
                    json={
                        "schemas": [
                            "urn:ietf:params:scim:schemas:core:2.0:User",
                        ],
                        "message": "Successful transaction",
                    },
                ),
            )
            client = AsyncHackerRank(api_key="test-key")
            try:
                result = await client.scim.users.patch(
                    scim_user_id="scim-1",
                    operations=[{"op": "replace"}],
                )
            finally:
                await client.aclose()
        assert result.message == "Successful transaction"

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_group_patch_returns_message() -> None:
        """Async group PATCH parses the documented message payload."""
        with respx.mock(assert_all_called=False) as router:
            router.patch(url__regex=r".*/Groups/.*").mock(
                return_value=httpx.Response(
                    status_code=200,
                    json={
                        "schemas": [
                            "urn:ietf:params:scim:schemas:core:2.0:Group",
                        ],
                        "message": "Successful transaction",
                    },
                ),
            )
            client = AsyncHackerRank(api_key="test-key")
            try:
                result = await client.scim.groups.patch(
                    scim_group_id="scim-2",
                    operations=[{"op": "replace"}],
                )
            finally:
                await client.aclose()
        assert result.message == "Successful transaction"
