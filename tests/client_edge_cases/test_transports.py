"""Tests for `hackerrank` transports client edge cases."""

from __future__ import annotations

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.transports import (
    AsyncHTTPXTransport,
    HTTPXTransport,
)


def test_sync_transport_context_manager() -> None:
    """``HTTPXTransport`` works as a context manager."""
    with HTTPXTransport() as transport:
        assert isinstance(transport, HTTPXTransport)


@pytest.mark.asyncio
async def test_async_transport_context_manager() -> None:
    """``AsyncHTTPXTransport`` works as an async context manager."""
    async with AsyncHTTPXTransport() as transport:
        assert isinstance(transport, AsyncHTTPXTransport)


@pytest.mark.asyncio
async def test_close_does_not_close_transport_callable() -> None:
    """A transport callable remains usable after ``aclose``."""
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(
            url="https://www.hackerrank.com/x/api/v3/tests",
        ).mock(return_value=httpx.Response(status_code=200, json={"data": []}))
        async with AsyncHTTPXTransport() as transport:
            client = AsyncHackerRank(
                api_key="test-key",
                transport=transport.__call__,
            )
            await client.aclose()
            other_client = AsyncHackerRank(
                api_key="test-key",
                transport=transport.__call__,
            )
            result = await other_client.tests.list()
            await other_client.aclose()
            assert not bool(result.data)
