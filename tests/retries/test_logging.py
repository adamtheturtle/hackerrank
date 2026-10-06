"""Tests for `hackerrank` logging retries."""

import logging
from http import HTTPStatus

import httpx
import pytest

from hackerrank.client import HackerRank
from tests.retries.responses import PAGE_BODY, error, ok
from tests.retries.transports import ScriptedTransport


def test_retry_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    """Each retry is logged with what went wrong.

    Args:
        caplog: The pytest log capture fixture.
    """
    transport = ScriptedTransport(
        script=[
            error(status_code=HTTPStatus.BAD_GATEWAY),
            ok(content=PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    with caplog.at_level(level=logging.WARNING, logger="hackerrank"):
        _ = client.tests.list()
    (record,) = caplog.records
    assert "HTTP 502" in record.getMessage()
    assert "in 0.5 seconds" in record.getMessage()


def test_transport_error_retry_names_the_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A retried transport error is named in the log.

    Args:
        caplog: The pytest log capture fixture.
    """
    transport = ScriptedTransport(
        script=[
            httpx.ReadTimeout(message="The read operation timed out"),
            ok(content=PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    with caplog.at_level(level=logging.WARNING, logger="hackerrank"):
        _ = client.tests.list()
    (record,) = caplog.records
    assert "ReadTimeout" in record.getMessage()
