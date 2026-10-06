"""Tests for `hackerrank` request bodies client edge cases.

``generate_codestubs`` requires a request body.
SCIM PATCH returns a message acknowledgement, not a resource.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank


def test_sync_requires_body() -> None:
    """Omitting ``body`` is rejected locally."""
    client = HackerRank(api_key="test-key")
    with pytest.raises(expected_exception=TypeError):
        client.questions.generate_codestubs(  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]  # pyrefly: ignore[missing-argument, unused-call-result]  # pylint: disable=missing-kwoa  # ty: ignore[missing-argument]
            question_id="q1",
        )


@pytest.mark.asyncio
async def test_async_requires_body() -> None:
    """Omitting ``body`` is rejected locally in the async client."""
    client = AsyncHackerRank(api_key="test-key")
    with pytest.raises(expected_exception=TypeError):
        await client.questions.generate_codestubs(  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]  # pyrefly: ignore[missing-argument]  # pylint: disable=missing-kwoa  # ty: ignore[missing-argument]
            question_id="q1",
        )


def test_sync_user_patch_returns_message() -> None:
    """User PATCH parses the documented message payload."""
    with respx.mock(assert_all_called=False) as router:
        _ = router.patch(url__regex=r".*/Users/.*").mock(
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


def test_sync_group_patch_returns_message() -> None:
    """Group PATCH parses the documented message payload."""
    with respx.mock(assert_all_called=False) as router:
        _ = router.patch(url__regex=r".*/Groups/.*").mock(
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


@pytest.mark.asyncio
async def test_async_user_patch_returns_message() -> None:
    """Async user PATCH parses the documented message payload."""
    with respx.mock(assert_all_called=False) as router:
        _ = router.patch(url__regex=r".*/Users/.*").mock(
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


@pytest.mark.asyncio
async def test_async_group_patch_returns_message() -> None:
    """Async group PATCH parses the documented message payload."""
    with respx.mock(assert_all_called=False) as router:
        _ = router.patch(url__regex=r".*/Groups/.*").mock(
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
