"""Tests for `hackerrank` delays retries."""

from http import HTTPStatus

import pytest

from hackerrank.client import HackerRank
from hackerrank.exceptions import (
    HackerRankError,
    RateLimitError,
)
from tests.retries.helpers import (
    PAGE_BODY,
    ScriptedTransport,
    error,
    ok,
    response,
)


def test_backoff_is_exponential(sleeps: list[float]) -> None:
    """Each delay is twice the one before it.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = ScriptedTransport(
        script=[error(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)],
    )
    client = HackerRank(api_key="key", transport=transport, retries=4)
    with pytest.raises(expected_exception=HackerRankError):
        _ = client.tests.list()
    assert sleeps == [0.5, 1.0, 2.0, 4.0]


def test_retry_after_is_honoured(sleeps: list[float]) -> None:
    """A ``Retry-After`` header replaces the backoff.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = ScriptedTransport(
        script=[
            response(
                status_code=HTTPStatus.TOO_MANY_REQUESTS,
                headers={"Retry-After": "7"},
                content=b"{}",
            ),
            ok(content=PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    assert client.tests.list().total == 0
    assert sleeps == [7.0]


def test_http_date_retry_after_falls_back_to_backoff(
    sleeps: list[float],
) -> None:
    """An unparsable ``Retry-After`` is ignored, not misread.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = ScriptedTransport(
        script=[
            response(
                status_code=HTTPStatus.TOO_MANY_REQUESTS,
                headers={"retry-after": "Wed, 21 Oct 2015 07:28:00 GMT"},
                content=b"{}",
            ),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    with pytest.raises(expected_exception=RateLimitError):
        _ = client.tests.list()
    assert sleeps == [0.5]


def test_negative_retry_after_does_not_go_backwards(
    sleeps: list[float],
) -> None:
    """A negative ``Retry-After`` waits no time at all.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = ScriptedTransport(
        script=[
            response(
                status_code=HTTPStatus.TOO_MANY_REQUESTS,
                headers={"Retry-After": "-5"},
                content=b"{}",
            ),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    with pytest.raises(expected_exception=RateLimitError):
        _ = client.tests.list()
    assert sleeps == [0.0]
