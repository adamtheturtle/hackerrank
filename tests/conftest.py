"""Per-test fixtures."""

from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank


@pytest.fixture(name="hackerrank_client")
def fixture_hackerrank_client(
    mock_hackerrank_api: respx.MockRouter,
) -> Generator[HackerRank]:
    """Provide a sync ``HackerRank`` client wired to the mock API.

    Args:
        mock_hackerrank_api: The respx mock router fixture.

    Yields:
        A ``HackerRank`` client.
    """
    del mock_hackerrank_api
    client = HackerRank(api_key="test-key")
    try:
        yield client
    finally:
        client.close()


@pytest_asyncio.fixture(name="async_hackerrank_client")
async def fixture_async_hackerrank_client(
    mock_hackerrank_api: respx.MockRouter,
) -> AsyncGenerator[AsyncHackerRank]:
    """Provide an async ``AsyncHackerRank`` client.

    Args:
        mock_hackerrank_api: The respx mock router fixture.

    Yields:
        An ``AsyncHackerRank`` client.
    """
    del mock_hackerrank_api
    client = AsyncHackerRank(api_key="test-key")
    try:
        yield client
    finally:
        await client.aclose()
