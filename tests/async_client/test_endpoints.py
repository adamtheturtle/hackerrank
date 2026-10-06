"""Tests for `hackerrank` endpoints asynchronous client."""

import pytest

from hackerrank.async_client import AsyncHackerRank


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
