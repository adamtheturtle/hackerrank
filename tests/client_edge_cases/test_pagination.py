"""Tests for `hackerrank` pagination client edge cases.

Test pagination coercion through the public clients.

Edge cases for SCIM pagination parsing.
Preserve an explicit SCIM ``startIndex`` of zero.
"""

from __future__ import annotations

from http import HTTPStatus

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank


def test_sync_coerces_pagination_metadata() -> None:
    """The sync client normalizes irregular pagination metadata."""
    expected_offset = 7
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(url__regex=r".*/x/api/v3/tests.*").mock(
            return_value=httpx.Response(
                status_code=HTTPStatus.OK,
                json={
                    "data": [],
                    "page_total": True,
                    "offset": f"{expected_offset}",
                    "previous": None,
                    "next": 5,
                    "first": "first",
                    "last": [],
                    "total": "invalid",
                },
            ),
        )
        with HackerRank(api_key="test-key") as client:
            result = client.tests.list()

    assert result.page_total == 1
    assert result.offset == expected_offset
    assert result.previous == ""
    assert result.next == ""
    assert result.first == "first"
    assert result.last == ""
    assert result.total == 0


@pytest.mark.asyncio
async def test_async_coerces_pagination_metadata() -> None:
    """The async client normalizes irregular pagination metadata."""
    expected_offset = 7
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(url__regex=r".*/x/api/v3/tests.*").mock(
            return_value=httpx.Response(
                status_code=HTTPStatus.OK,
                json={
                    "data": [],
                    "page_total": True,
                    "offset": f"{expected_offset}",
                    "previous": None,
                    "next": 5,
                    "first": "first",
                    "last": [],
                    "total": "invalid",
                },
            ),
        )
        async with AsyncHackerRank(api_key="test-key") as client:
            result = await client.tests.list()

    assert result.page_total == 1
    assert result.offset == expected_offset
    assert result.previous == ""
    assert result.next == ""
    assert result.first == "first"
    assert result.last == ""
    assert result.total == 0


def test_scim_users_with_missing_schemas() -> None:
    """A SCIM ``Resources`` payload with no ``schemas`` key works.

    Covers the False branch of ``isinstance(schemas_raw, list)``.
    """
    with respx.mock(assert_all_called=False) as router:
        _ = router.get(url__regex=r".*/Users.*").mock(
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


@pytest.mark.asyncio
async def test_async_scim_groups_with_missing_schemas() -> None:
    """Async SCIM groups list handles a missing ``schemas`` key."""
    with respx.mock(assert_all_called=False) as router:
        _ = router.get(url__regex=r".*/Groups.*").mock(
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


def test_sync_preserves_zero_start_index() -> None:
    """A server ``startIndex`` of ``0`` is kept as ``0``."""
    with respx.mock(assert_all_called=False) as router:
        _ = router.get(url__regex=r".*/Users.*").mock(
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


@pytest.mark.asyncio
async def test_async_preserves_zero_start_index() -> None:
    """Async list keeps a server ``startIndex`` of ``0``."""
    with respx.mock(assert_all_called=False) as router:
        _ = router.get(url__regex=r".*/Groups.*").mock(
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
