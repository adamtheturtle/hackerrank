"""Tests for `hackerrank` policy retries."""

from http import HTTPStatus

import pytest

from hackerrank.client import HackerRank
from hackerrank.exceptions import (
    HackerRankError,
    NotFoundError,
    RedirectError,
)
from tests.retries.questions import create_question
from tests.retries.responses import PAGE_BODY, error, ok
from tests.retries.transports import ScriptedTransport


def test_default_makes_one_attempt() -> None:
    """By default a failing request is not retried."""
    transport = ScriptedTransport(
        script=[
            error(status_code=HTTPStatus.SERVICE_UNAVAILABLE),
            ok(content=PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport)
    with pytest.raises(expected_exception=HackerRankError):
        _ = client.tests.list()
    assert transport.methods == ["GET"]


def test_retries_are_used_when_asked_for() -> None:
    """A repeatable request is retried until it succeeds."""
    transport = ScriptedTransport(
        script=[
            error(status_code=HTTPStatus.SERVICE_UNAVAILABLE),
            error(status_code=HTTPStatus.BAD_GATEWAY),
            ok(content=PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=2)
    assert client.tests.list().total == 0
    assert transport.methods == ["GET", "GET", "GET"]


def test_retries_are_exhausted(sleeps: list[float]) -> None:
    """The last failure is raised once the retries run out.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = ScriptedTransport(
        script=[error(status_code=HTTPStatus.SERVICE_UNAVAILABLE)],
    )
    client = HackerRank(api_key="key", transport=transport, retries=2)
    with pytest.raises(expected_exception=HackerRankError):
        _ = client.tests.list()
    assert transport.methods == ["GET", "GET", "GET"]
    assert sleeps == [0.5, 1.0]


def test_create_is_not_repeated(sleeps: list[float]) -> None:
    """A create is sent once, because the write may have landed.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = ScriptedTransport(
        script=[error(status_code=HTTPStatus.GATEWAY_TIMEOUT)],
    )
    client = HackerRank(api_key="key", transport=transport, retries=5)
    with pytest.raises(expected_exception=HackerRankError):
        create_question(client=client)
    assert transport.methods == ["POST"]
    assert sleeps == []


def test_upsert_post_is_repeated() -> None:
    """A ``POST`` which replaces state is repeated."""
    transport = ScriptedTransport(
        script=[
            error(status_code=HTTPStatus.BAD_GATEWAY),
            ok(content=b"{}"),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    client.interview_templates.explicit_sharing_roles.update_access(
        template_id=1,
        explicit_roles=[{"rollable_type": "company"}],
    )
    assert transport.methods == ["POST", "POST"]
    assert transport.urls[0].endswith("/update_access")


@pytest.mark.parametrize(
    argnames=("status_code", "expected_error"),
    argvalues=[
        (HTTPStatus.NOT_FOUND, NotFoundError),
        (HTTPStatus.BAD_REQUEST, HackerRankError),
        (HTTPStatus.MOVED_PERMANENTLY, RedirectError),
    ],
)
def test_non_transient_status_is_not_repeated(
    status_code: HTTPStatus,
    expected_error: type[HackerRankError],
    sleeps: list[float],
) -> None:
    """A response which a retry cannot fix is raised at once.

    Args:
        status_code: The status code to respond with.
        expected_error: The error the response must raise.
        sleeps: The recorded delays between attempts.
    """
    transport = ScriptedTransport(
        script=[error(status_code=status_code)],
    )
    client = HackerRank(api_key="key", transport=transport, retries=3)
    with pytest.raises(expected_exception=expected_error):
        _ = client.tests.list()
    assert transport.methods == ["GET"]
    assert sleeps == []
