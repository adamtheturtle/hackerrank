"""Tests for the async HackerRank client."""

from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

import httpx
import httpx2
import pytest
import respx

import hackerrank.async_client as async_client_module
from hackerrank.async_client import AsyncHackerRank
from hackerrank.transports import (
    DEFAULT_TIMEOUT_SECONDS,
    AsyncHTTPX2Transport,
    AsyncHTTPXTransport,
    AsyncTransport,
    TransportResponse,
)
from hackerrank.types import JSONValue


class TestAsyncHackerRank:
    """Tests for ``AsyncHackerRank``."""

    @staticmethod
    def test_default_base_url() -> None:
        """The default base URL is the HackerRank app."""
        client = AsyncHackerRank(api_key="test-key")
        assert client.base_url == "https://www.hackerrank.com"

    @staticmethod
    def test_default_scim_base_url() -> None:
        """SCIM uses its own host, distinct from the v3 base URL."""
        client = AsyncHackerRank(api_key="test-key")
        assert (
            client.scim_base_url == "https://services.hackerrank.com/scim/v2"
        )
        assert client.scim.base_url == client.scim_base_url

    @staticmethod
    def test_custom_scim_base_url() -> None:
        """A custom SCIM base URL can be provided."""
        client = AsyncHackerRank(
            api_key="test-key",
            scim_base_url="https://scim.example.com/v2",
        )
        assert client.scim_base_url == "https://scim.example.com/v2"
        assert client.scim.base_url == "https://scim.example.com/v2"

    @staticmethod
    def test_trailing_slash_base_urls_are_normalized() -> None:
        """Trailing slashes are stripped from custom base URLs."""
        client = AsyncHackerRank(
            api_key="test-key",
            base_url="https://custom.example.com/",
            scim_base_url="https://scim.example.com/v2/",
        )
        assert client.base_url == "https://custom.example.com"
        assert client.users.base_url == "https://custom.example.com"
        assert client.scim_base_url == "https://scim.example.com/v2"
        assert client.scim.base_url == "https://scim.example.com/v2"

    @staticmethod
    def test_falsy_transport_is_preserved() -> None:
        """A falsy custom transport is not replaced by the default."""

        class _FalsyTransport:
            """A transport whose ``__bool__`` returns ``False``."""

            def __bool__(self) -> bool:  # pragma: no cover
                """Report as falsy."""
                return False

            async def __call__(
                self,
                *,
                method: str,
                url: str,
                headers: dict[str, str],
                params: dict[str, str | int] | None,
                json: Mapping[str, JSONValue] | None,
                files: Mapping[str, Any] | None,  # pyrefly: ignore [explicit-any]
            ) -> TransportResponse:  # pragma: no cover
                """Make a request."""
                del method, url, headers, params, json, files
                raise NotImplementedError

        transport: Any = _FalsyTransport()  # pyrefly: ignore [explicit-any]
        client = AsyncHackerRank(api_key="test-key", transport=transport)
        assert client.users.transport is transport

    @staticmethod
    def test_namespaces_are_attached() -> None:
        """The async client exposes the expected namespaces."""
        client = AsyncHackerRank(api_key="test-key")
        assert isinstance(
            client.interviews,
            async_client_module.AsyncInterviewsNamespace,
        )
        assert isinstance(
            client.interview_templates,
            async_client_module.AsyncInterviewTemplatesNamespace,
        )
        assert isinstance(
            client.environments,
            async_client_module.AsyncEnvironmentsNamespace,
        )
        assert isinstance(
            client.questions,
            async_client_module.AsyncQuestionsNamespace,
        )
        assert isinstance(
            client.tests,
            async_client_module.AsyncTestsNamespace,
        )
        assert isinstance(
            client.tests.candidates,
            async_client_module.AsyncTestCandidatesNamespace,
        )
        assert isinstance(
            client.templates,
            async_client_module.AsyncTemplatesNamespace,
        )
        assert isinstance(
            client.candidates,
            async_client_module.AsyncCandidatesNamespace,
        )
        assert isinstance(
            client.users,
            async_client_module.AsyncUsersNamespace,
        )
        assert isinstance(
            client.teams,
            async_client_module.AsyncTeamsNamespace,
        )
        assert isinstance(
            client.teams.memberships,
            async_client_module.AsyncTeamMembershipsNamespace,
        )
        assert isinstance(
            client.audit_logs,
            async_client_module.AsyncAuditLogsNamespace,
        )
        assert isinstance(client.ats, async_client_module.AsyncATSNamespace)
        assert isinstance(
            client.ats.codepair,
            async_client_module.AsyncATSCodePairNamespace,
        )
        assert isinstance(
            client.ats.codescreen,
            async_client_module.AsyncATSCodeScreenNamespace,
        )
        assert isinstance(client.scim, async_client_module.AsyncSCIMNamespace)
        assert isinstance(
            client.scim.users,
            async_client_module.AsyncSCIMUsersNamespace,
        )
        assert isinstance(
            client.scim.groups,
            async_client_module.AsyncSCIMGroupsNamespace,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_context_manager() -> None:
        """The async client can be used as a context manager."""
        async with AsyncHackerRank(api_key="test-key") as client:
            assert isinstance(client, AsyncHackerRank)

    @staticmethod
    @pytest.mark.asyncio
    async def test_aclose() -> None:
        """The async client can be closed."""
        client = AsyncHackerRank(api_key="test-key")
        await client.aclose()


class TestAsyncListEndpoints:
    """Async list endpoint smoke tests."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_tests(
        async_hackerrank_client: AsyncHackerRank,
    ) -> None:
        """The async tests list endpoint returns a page."""
        try:
            result = await async_hackerrank_client.tests.list()
        finally:
            await async_hackerrank_client.aclose()
        assert result.total >= 0

    @staticmethod
    @pytest.mark.asyncio
    async def test_list_users(
        async_hackerrank_client: AsyncHackerRank,
    ) -> None:
        """The async users list endpoint returns a page."""
        try:
            result = await async_hackerrank_client.users.list()
        finally:
            await async_hackerrank_client.aclose()
        assert result.total >= 0


class TestAsyncHTTPXTransport:
    """Tests for ``AsyncHTTPXTransport``."""

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames=("configured_timeout", "expected"),
        argvalues=[
            (None, httpx.Timeout(timeout=DEFAULT_TIMEOUT_SECONDS)),
            (120.0, httpx.Timeout(timeout=120.0)),
            (120, httpx.Timeout(timeout=120.0)),
            (
                httpx.Timeout(timeout=5.0, read=300.0),
                httpx.Timeout(timeout=5.0, read=300.0),
            ),
        ],
    )
    async def test_timeout(
        configured_timeout: httpx.Timeout | float | int | None,  # noqa: PYI041
        expected: httpx.Timeout,
    ) -> None:
        """The configured timeout reaches the outgoing request.

        Args:
            configured_timeout: The timeout to give to the
                transport, or ``None`` to leave it at its default.
            expected: The timeout expected on the request.
        """
        transport = (
            AsyncHTTPXTransport()
            if configured_timeout is None
            else AsyncHTTPXTransport(timeout=configured_timeout)
        )
        url = "https://timeout.example.com/thing"
        with respx.mock:
            route = respx.get(url=url).mock(
                return_value=httpx.Response(status_code=200, json={}),
            )
            try:
                await transport(
                    method="GET",
                    url=url,
                    headers={},
                    params=None,
                    json=None,
                    files=None,
                )
            finally:
                await transport.aclose()
        request = route.calls.last.request
        assert request.extensions["timeout"] == expected.as_dict()


class TestAsyncHTTPX2Transport:
    """Tests for ``AsyncHTTPX2Transport``."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_is_async_transport() -> None:
        """AsyncHTTPX2Transport satisfies the AsyncTransport protocol."""
        async with AsyncHTTPX2Transport() as transport:
            assert isinstance(transport, AsyncTransport)

    @staticmethod
    @pytest.mark.asyncio
    async def test_timeout_and_response(httpx2_mock: respx.Router) -> None:
        """A native async HTTPX2 request produces a transport response."""
        timeout = httpx2.Timeout(timeout=12.5)
        url = "https://api.example/x/api/v3/tests"
        route = httpx2_mock.get(url=url).respond(
            status_code=HTTPStatus.OK,
            headers={"X-Family": "httpx2"},
            content=b'{"data": []}',
        )

        async with AsyncHTTPX2Transport(timeout=timeout) as transport:
            response = await transport(
                method="GET",
                url=url,
                headers={},
                params=None,
                json=None,
                files=None,
            )

        assert response.status_code == HTTPStatus.OK
        assert response.headers["x-family"] == "httpx2"
        assert response.json() == {"data": []}
        assert route.calls.last.request.extensions["timeout"] == (
            timeout.as_dict()
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_hackerrank_uses_httpx2(
        httpx2_mock: respx.Router,
    ) -> None:
        """AsyncHackerRank parses a response sent through HTTPX2."""
        _ = httpx2_mock.get(
            url="https://www.hackerrank.com/x/api/v3/tests"
        ).respond(
            status_code=HTTPStatus.OK,
            json={
                "data": [],
                "page_total": 0,
                "offset": 0,
                "previous": "",
                "next": "",
                "first": "",
                "last": "",
                "total": 0,
            },
        )

        async with AsyncHackerRank(
            api_key="test-key",
            transport=AsyncHTTPX2Transport(),
        ) as client:
            assert (await client.tests.list()).total == 0
