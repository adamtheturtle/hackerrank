"""Tests for the async HackerRank client."""

import pytest

import hackerrank.async_client as async_client_module
from hackerrank.async_client import AsyncHackerRank


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
            client.users,
            async_client_module.AsyncUsersNamespace,
        )
        assert isinstance(
            client.teams,
            async_client_module.AsyncTeamsNamespace,
        )
        assert isinstance(
            client.audit_logs,
            async_client_module.AsyncAuditLogsNamespace,
        )
        assert isinstance(client.ats, async_client_module.AsyncATSNamespace)
        assert isinstance(client.scim, async_client_module.AsyncSCIMNamespace)

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
