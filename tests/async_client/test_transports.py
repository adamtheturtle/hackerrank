"""Tests for `hackerrank` transports asynchronous client."""

from http import HTTPStatus

import httpx
import httpx2
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.transports import (
    DEFAULT_TIMEOUT_SECONDS,
    AsyncHTTPX2Transport,
    AsyncHTTPXTransport,
    AsyncTransport,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=("configured_timeout", "expected"),
    argvalues=[
        (None, httpx.Timeout(timeout=DEFAULT_TIMEOUT_SECONDS)),
        (120.0, httpx.Timeout(timeout=120.0)),
        (120, httpx.Timeout(timeout=120.0)),
        (
            httpx.Timeout(timeout=5.0, read=300.0),
            httpx.Timeout(timeout=5.0, read=300.0),
        ),
    ],
)
async def test_timeout(
    configured_timeout: object,
    expected: httpx.Timeout,
) -> None:
    """The configured timeout reaches the outgoing request.

    Args:
        configured_timeout: The timeout to give to the
            transport, or ``None`` to leave it at its default.
        expected: The timeout expected on the request.
    """
    if configured_timeout is None:
        transport = AsyncHTTPXTransport()
    else:
        assert isinstance(configured_timeout, (httpx.Timeout, float, int))
        transport = AsyncHTTPXTransport(timeout=configured_timeout)
    url = "https://timeout.example.com/thing"
    with respx.mock:
        route = respx.get(url=url).mock(
            return_value=httpx.Response(status_code=200, json={}),
        )
        try:
            await transport(
                method="GET",
                url=url,
                headers={},
                params=None,
                json=None,
                files=None,
            )
        finally:
            await transport.aclose()
    request = route.calls.last.request
    assert request.extensions["timeout"] == expected.as_dict()


@pytest.mark.asyncio
async def test_is_async_transport() -> None:
    """AsyncHTTPX2Transport satisfies the AsyncTransport protocol."""
    async with AsyncHTTPX2Transport() as transport:
        assert isinstance(transport, AsyncTransport)


@pytest.mark.asyncio
async def test_timeout_and_response(httpx2_mock: respx.Router) -> None:
    """A native async HTTPX2 request produces a transport response."""
    timeout = httpx2.Timeout(timeout=12.5)
    url = "https://api.example/x/api/v3/tests"
    route = httpx2_mock.get(url=url).respond(
        status_code=HTTPStatus.OK,
        headers={"X-Family": "httpx2"},
        content=b'{"data": []}',
    )

    async with AsyncHTTPX2Transport(timeout=timeout) as transport:
        response = await transport(
            method="GET",
            url=url,
            headers={},
            params=None,
            json=None,
            files=None,
        )

    assert response.status_code == HTTPStatus.OK
    assert response.headers["x-family"] == "httpx2"
    assert response.json() == {"data": []}
    assert route.calls.last.request.extensions["timeout"] == (
        timeout.as_dict()
    )


@pytest.mark.asyncio
async def test_hackerrank_uses_httpx2(
    httpx2_mock: respx.Router,
) -> None:
    """AsyncHackerRank parses a response sent through HTTPX2."""
    _ = httpx2_mock.get(
        url="https://www.hackerrank.com/x/api/v3/tests"
    ).respond(
        status_code=HTTPStatus.OK,
        json={
            "data": [],
            "page_total": 0,
            "offset": 0,
            "previous": "",
            "next": "",
            "first": "",
            "last": "",
            "total": 0,
        },
    )

    async with AsyncHackerRank(
        api_key="test-key",
        transport=AsyncHTTPX2Transport(),
    ) as client:
        assert (await client.tests.list()).total == 0
