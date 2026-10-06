"""Tests for `hackerrank` routing client edge cases.

Direct hits on the stub router's fallback branches.

These requests go to unknown URLs so the side-effect function in
``tests/conftest.py`` exits each method block without matching.
Custom base URLs must not produce double-slash paths.
"""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import httpx
import pytest

from hackerrank.client import HackerRank
from hackerrank.transports import (
    TransportResponse,
)
from tests.client_edge_cases.helpers import BASE_URL

if TYPE_CHECKING:
    import respx


@pytest.mark.parametrize(
    argnames="method",
    argvalues=["GET", "POST", "PATCH"],
)
def test_unknown_url_returns_empty_payload(
    method: str,
    stub_router: respx.MockRouter,
) -> None:
    """Unknown URLs fall through to the empty-payload return.

    Args:
        method: HTTP method to send.
        stub_router: The stub router fixture.
    """
    del stub_router
    with httpx.Client(base_url=BASE_URL) as http_client:
        response = http_client.request(
            method=method,
            url="/never-mapped-anywhere",
        )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {}


def test_unknown_put_returns_no_content(
    stub_router: respx.MockRouter,
) -> None:
    """Unknown PUT requests fall through to the 204 default.

    Args:
        stub_router: The stub router fixture.
    """
    del stub_router
    with httpx.Client(base_url=BASE_URL) as http_client:
        response = http_client.put(url="/never-mapped-anywhere")
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_trailing_slash_does_not_double_slash_path() -> None:
    """A trailing slash on ``base_url`` is stripped before join."""
    captured: list[str] = []

    class _SpyTransport:
        """Capture the absolute URL of each request."""

        def __call__(
            self,
            *,
            method: str,
            url: str,
            headers: dict[str, str],
            params: dict[str, str | int] | None,
            json: object | None,
            files: object | None,
        ) -> TransportResponse:
            """Record ``url`` and return an empty page."""
            del method, headers, params, json, files
            captured.append(url)
            return TransportResponse(
                status_code=200,
                headers={},
                content=(
                    b'{"data":[],"page_total":0,"offset":0,'
                    b'"previous":"","next":"","first":"",'
                    b'"last":"","total":0}'
                ),
            )

    client = HackerRank(
        api_key="test-key",
        base_url="https://example.test/",
        transport=_SpyTransport(),
    )
    _ = client.users.list()
    assert captured == ["https://example.test/x/api/v3/users"]
