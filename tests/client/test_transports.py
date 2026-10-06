"""Tests for `hackerrank` transports client."""

from http import HTTPStatus

import httpx
import httpx2
import pytest
import respx

from hackerrank.client import HackerRank
from hackerrank.transports import (
    DEFAULT_TIMEOUT_SECONDS,
    HTTPStatusError,
    HTTPX2Transport,
    HTTPXTransport,
    Transport,
    TransportResponse,
)

# The timeout ``httpx.Client()`` uses when none is given.
_HTTPX_DEFAULT_TIMEOUT_SECONDS = 5.0


def test_httpx_transport_is_transport() -> None:
    """HTTPXTransport satisfies the Transport protocol."""
    assert isinstance(HTTPXTransport(), Transport)


def test_close() -> None:
    """The transport can be closed."""
    transport = HTTPXTransport()
    transport.close()


@pytest.mark.parametrize(
    argnames=("timeout", "expected"),
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
def test_timeout(
    timeout: object,
    expected: httpx.Timeout,
) -> None:
    """The configured timeout reaches the outgoing request.

    Args:
        timeout: The timeout to give to the transport, or
            ``None`` to leave it at its default.
        expected: The timeout expected on the request.
    """
    if timeout is None:
        transport = HTTPXTransport()
    else:
        assert isinstance(timeout, (httpx.Timeout, float, int))
        transport = HTTPXTransport(timeout=timeout)
    url = "https://timeout.example.com/thing"
    with respx.mock:
        route = respx.get(url=url).mock(
            return_value=httpx.Response(status_code=200, json={}),
        )
        try:
            _ = transport(
                method="GET",
                url=url,
                headers={},
                params=None,
                json=None,
                files=None,
            )
        finally:
            transport.close()
    request = route.calls.last.request
    assert request.extensions["timeout"] == expected.as_dict()


def test_default_timeout_is_not_the_httpx_default() -> None:
    """The default timeout is not ``httpx``'s 5 second default."""
    assert DEFAULT_TIMEOUT_SECONDS > _HTTPX_DEFAULT_TIMEOUT_SECONDS


def test_httpx2_transport_is_transport() -> None:
    """HTTPX2Transport satisfies the Transport protocol."""
    with HTTPX2Transport() as transport:
        assert isinstance(transport, Transport)


def test_timeout_and_response(httpx2_mock: respx.Router) -> None:
    """A native HTTPX2 request produces a transport response."""
    timeout = httpx2.Timeout(timeout=12.5)
    url = "https://api.example/x/api/v3/tests"
    route = httpx2_mock.get(url=url).respond(
        status_code=HTTPStatus.OK,
        headers={"X-Family": "httpx2"},
        content=b'{"data": []}',
    )

    with HTTPX2Transport(timeout=timeout) as transport:
        response = transport(
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


def test_hackerrank_uses_httpx2(httpx2_mock: respx.Router) -> None:
    """HackerRank parses a successful response sent through HTTPX2."""
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

    with HackerRank(
        api_key="test-key",
        transport=HTTPX2Transport(),
    ) as client:
        assert client.tests.list().total == 0


def test_raise_for_status_no_op() -> None:
    """No exception is raised for 2xx responses."""
    response = TransportResponse(
        status_code=HTTPStatus.OK,
        headers={},
        content=b"{}",
    )
    response.raise_for_status()


def test_raise_for_status_raises() -> None:
    """4xx responses raise ``HTTPStatusError``."""
    response = TransportResponse(
        status_code=HTTPStatus.NOT_FOUND,
        headers={},
        content=b"{}",
    )
    with pytest.raises(expected_exception=HTTPStatusError):
        response.raise_for_status()


def test_raise_for_status_raises_on_redirect() -> None:
    """3xx responses raise ``HTTPStatusError``."""
    response = TransportResponse(
        status_code=HTTPStatus.FOUND,
        headers={"location": "https://example.test/"},
        content=b"",
    )
    with pytest.raises(expected_exception=HTTPStatusError):
        response.raise_for_status()


def test_json() -> None:
    """JSON content is parsed correctly."""
    response = TransportResponse(
        status_code=HTTPStatus.OK,
        headers={},
        content=b'{"a": 1}',
    )
    assert response.json() == {"a": 1}
