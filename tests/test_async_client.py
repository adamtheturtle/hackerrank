"""Tests for the async HackerRank client."""

from collections.abc import Mapping
from typing import Any

import pytest

import hackerrank.async_client as async_client_module
from hackerrank.async_client import AsyncHackerRank
from hackerrank.transports import TransportResponse
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
                files: Mapping[str, Any] | None,
            ) -> TransportResponse:  # pragma: no cover
                """Make a request."""
                del method, url, headers, params, json, files
                raise NotImplementedError

        transport: Any = _FalsyTransport()
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
