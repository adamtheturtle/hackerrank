"""Tests for `hackerrank` errors client edge cases."""

from __future__ import annotations

from http import HTTPStatus

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.exceptions import HackerRankError
from hackerrank.transports import (
    TransportResponse,
)
from tests.client_edge_cases.constants import BASE_URL


@pytest.mark.asyncio
async def test_async_error_raises() -> None:
    """An error response raises ``HackerRankError`` in async paths."""
    with respx.mock(
        base_url=BASE_URL,
        assert_all_called=False,
    ) as router:
        _ = router.get(url__regex=r".*/x/api/v3/tests.*").mock(
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


def test_unknown_status_falls_back_to_base_error() -> None:
    """An unmapped status returns the base ``HackerRankError``
    type.
    """

    class _UnregisteredError(HackerRankError):
        """A subclass with no status-code mapping."""

    unmapped_status = 418
    response = TransportResponse(
        status_code=unmapped_status,
        headers={},
        content=b"{}",
    )
    err = HackerRankError.from_response(response=response)
    assert err.__class__ is HackerRankError
    assert not isinstance(err, _UnregisteredError)
    assert err.status_code == unmapped_status
    assert err.content == b"{}"
