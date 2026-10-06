"""Tests for `hackerrank` errors retries."""

import httpx
import httpx2
import pytest

from hackerrank.client import HackerRank
from tests.retries.questions import create_question
from tests.retries.responses import PAGE_BODY, ok
from tests.retries.transports import ScriptedTransport


def test_transport_error_is_retried(sleeps: list[float]) -> None:
    """A transport error on a repeatable request is retried.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = ScriptedTransport(
        script=[
            httpx.ReadTimeout(message="The read operation timed out"),
            ok(content=PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    assert client.tests.list().total == 0
    assert transport.methods == ["GET", "GET"]
    assert sleeps == [0.5]


def test_transport_error_is_raised_when_retries_run_out() -> None:
    """The transport error is raised once the retries run out."""
    transport = ScriptedTransport(
        script=[httpx.ConnectError(message="Connection refused")],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    with pytest.raises(expected_exception=httpx.ConnectError):
        _ = client.tests.list()
    assert transport.methods == ["GET", "GET"]


def test_transport_error_on_a_create_is_not_retried(
    sleeps: list[float],
) -> None:
    """A create which times out is not sent again.

    This is the case the retry policy exists to get right. The
    write may well have landed, so a second attempt would create
    a duplicate question which the API cannot delete.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = ScriptedTransport(
        script=[httpx.ReadTimeout(message="The read operation timed out")],
    )
    client = HackerRank(api_key="key", transport=transport, retries=5)
    with pytest.raises(expected_exception=httpx.ReadTimeout):
        create_question(client=client)
    assert transport.methods == ["POST"]
    assert sleeps == []


def test_httpx2_transport_error_is_retried(
    sleeps: list[float],
) -> None:
    """A native HTTPX2 transport error is retried.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = ScriptedTransport(
        script=[
            httpx2.ReadTimeout(message="The read operation timed out"),
            ok(content=PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    assert client.tests.list().total == 0
    assert transport.methods == ["GET", "GET"]
    assert sleeps == [0.5]
