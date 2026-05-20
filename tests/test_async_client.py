"""Tests for the async HackerRank client."""

import pytest

from hackerrank.async_client import AsyncHackerRank


class TestAsyncHackerRank:
    """Tests for ``AsyncHackerRank``."""

    @staticmethod
    def test_default_base_url() -> None:
        """The default base URL is the HackerRank app."""
        client = AsyncHackerRank(api_key="test-key")
        assert client.base_url == "https://www.hackerrank.com"

    @staticmethod
    def test_namespaces_are_attached() -> None:
        """The async client exposes the expected namespaces."""
        client = AsyncHackerRank(api_key="test-key")
        assert hasattr(client, "interviews")  # pylint: disable=bad-builtin
        assert hasattr(client, "interview_templates")  # pylint: disable=bad-builtin
        assert hasattr(client, "questions")  # pylint: disable=bad-builtin
        assert hasattr(client, "tests")  # pylint: disable=bad-builtin
        assert hasattr(client.tests, "candidates")  # pylint: disable=bad-builtin
        assert hasattr(client, "templates")  # pylint: disable=bad-builtin
        assert hasattr(client, "users")  # pylint: disable=bad-builtin
        assert hasattr(client, "teams")  # pylint: disable=bad-builtin
        assert hasattr(client, "audit_logs")  # pylint: disable=bad-builtin
        assert hasattr(client, "ats")  # pylint: disable=bad-builtin
        assert hasattr(client, "scim")  # pylint: disable=bad-builtin

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
