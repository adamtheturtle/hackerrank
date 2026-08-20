"""Tests for global candidate search."""

from __future__ import annotations

from http import HTTPStatus

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank

_SEARCH_URL = "https://www.hackerrank.com/x/api/v3/candidates/search"

_MULTI_ATTEMPT_PAGE = {
    "data": [
        {
            "uuid": "634da4e3-4a75-4e60-a8ab-81e9253d84fe",
            "name": "Jane Candidate",
            "email": "jane@example.com",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-06-01T12:00:00Z",
            "attempts": [
                {
                    "attempt_id": "123456",
                    "test_id": "789012",
                    "report_url": (
                        "https://www.hackerrank.com/x/tests/789012/"
                        "candidates/123456/report"
                    ),
                    "score": 80.0,
                    "percentage_score": 72.5,
                    "attempt_starttime": "2024-02-01T10:00:00Z",
                    "attempt_endtime": "2024-02-01T11:00:00Z",
                },
                {
                    "attempt_id": "654321",
                    "test_id": "210987",
                    "report_url": (
                        "https://www.hackerrank.com/x/tests/210987/"
                        "candidates/654321/report"
                    ),
                },
            ],
        },
    ],
    "page_total": 1,
    "offset": 0,
    "previous": "",
    "next": (
        "https://www.hackerrank.com/x/api/v3/candidates/search"
        "?limit=1&offset=1"
    ),
    "first": (
        "https://www.hackerrank.com/x/api/v3/candidates/search"
        "?limit=1&offset=0"
    ),
    "last": (
        "https://www.hackerrank.com/x/api/v3/candidates/search"
        "?limit=1&offset=12"
    ),
    "total": 13,
    "query": "jane",
}


class TestCandidateSearchSync:
    """Sync client coverage for ``candidates.search``."""

    @staticmethod
    def test_search_pagination_and_multi_attempt_payload() -> None:
        """Search returns pagination metadata and nested attempts."""
        with respx.mock(assert_all_called=True) as router:
            route = router.get(url=_SEARCH_URL).mock(
                return_value=httpx.Response(
                    status_code=HTTPStatus.OK,
                    json=_MULTI_ATTEMPT_PAGE,
                ),
            )
            client = HackerRank(api_key="test-key")
            try:
                page = client.candidates.search(
                    query="jane",
                    limit=1,
                    offset=0,
                )
            finally:
                client.close()

        assert route.called
        assert route.calls.last.request.url.params["query"] == "jane"
        assert route.calls.last.request.url.params["limit"] == "1"
        assert route.calls.last.request.url.params["offset"] == "0"

        expected_total = 13
        expected_attempts = 2
        assert page.total == expected_total
        assert page.page_total == 1
        assert page.offset == 0
        assert page.next.endswith("offset=1")
        assert page.first.endswith("offset=0")
        assert page.last.endswith("offset=12")
        assert page.previous == ""
        assert len(page) == 1

        candidate = page[0]
        assert candidate.uuid == "634da4e3-4a75-4e60-a8ab-81e9253d84fe"
        assert candidate.name == "Jane Candidate"
        assert candidate.email == "jane@example.com"
        assert len(candidate.attempts) == expected_attempts
        first, second = candidate.attempts
        assert first.attempt_id == "123456"
        assert first.test_id == "789012"
        assert first.score == 80.0
        assert first.percentage_score == 72.5
        assert first.attempt_starttime == "2024-02-01T10:00:00Z"
        assert second.attempt_id == "654321"
        assert second.score is None
        assert second.attempt_endtime is None


class TestCandidateSearchAsync:
    """Async client coverage for ``candidates.search``."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_search_pagination_and_multi_attempt_payload() -> None:
        """Async search returns pagination metadata and nested
        attempts.
        """
        with respx.mock(assert_all_called=True) as router:
            route = router.get(url=_SEARCH_URL).mock(
                return_value=httpx.Response(
                    status_code=HTTPStatus.OK,
                    json=_MULTI_ATTEMPT_PAGE,
                ),
            )
            client = AsyncHackerRank(api_key="test-key")
            try:
                page = await client.candidates.search(
                    query="jane",
                    limit=1,
                    offset=0,
                )
            finally:
                await client.aclose()

        assert route.called
        expected_total = 13
        expected_attempts = 2
        assert page.total == expected_total
        assert len(page[0].attempts) == expected_attempts
        assert page[0].attempts[0].report_url.endswith("/report")
