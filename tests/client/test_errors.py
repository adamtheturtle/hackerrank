"""Tests for `hackerrank` errors client."""

from http import HTTPStatus

import httpx
import pytest
import respx

from hackerrank.client import HackerRank
from hackerrank.exceptions import (
    AuthenticationError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    HackerRankError,
    NotFoundError,
    RateLimitError,
    RedirectError,
    ServerError,
    UnprocessableEntityError,
)


@pytest.mark.parametrize(
    argnames=("status_code", "expected"),
    argvalues=[
        (HTTPStatus.BAD_REQUEST, BadRequestError),
        (HTTPStatus.UNAUTHORIZED, AuthenticationError),
        (HTTPStatus.FORBIDDEN, ForbiddenError),
        (HTTPStatus.NOT_FOUND, NotFoundError),
        (HTTPStatus.CONFLICT, ConflictError),
        (
            HTTPStatus.UNPROCESSABLE_ENTITY,
            UnprocessableEntityError,
        ),
        (HTTPStatus.TOO_MANY_REQUESTS, RateLimitError),
        (
            HTTPStatus.INTERNAL_SERVER_ERROR,
            ServerError,
        ),
    ],
)
def test_status_maps_to_specific_error(
    status_code: HTTPStatus,
    expected: type[HackerRankError],
) -> None:
    """Each known status code raises a specific subclass.

    Args:
        status_code: The HTTP status code to simulate.
        expected: The expected exception subclass.
    """
    with respx.mock(
        base_url="https://www.hackerrank.com",
        assert_all_called=False,
    ) as router:
        _ = router.get(
            url__regex=r".*/x/api/v3/tests.*",
        ).mock(
            return_value=httpx.Response(
                status_code=status_code,
            ),
        )
        client = HackerRank(api_key="test-key")
        try:
            with pytest.raises(expected_exception=expected):
                _ = client.tests.list()
        finally:
            client.close()


def test_unknown_status_uses_base_error() -> None:
    """An unmapped status raises the base ``HackerRankError``."""
    with respx.mock(
        base_url="https://www.hackerrank.com",
        assert_all_called=False,
    ) as router:
        _ = router.get(
            url__regex=r".*/x/api/v3/tests.*",
        ).mock(
            return_value=httpx.Response(status_code=418),
        )
        client = HackerRank(api_key="test-key")
        try:
            with pytest.raises(expected_exception=HackerRankError):
                _ = client.tests.list()
        finally:
            client.close()


def test_redirect_raises_redirect_error() -> None:
    """Unexpected 3xx responses raise ``RedirectError``."""
    with respx.mock(
        base_url="https://www.hackerrank.com",
        assert_all_called=False,
    ) as router:
        _ = router.get(
            url__regex=r".*/x/api/v3/users.*",
        ).mock(
            return_value=httpx.Response(
                status_code=HTTPStatus.FOUND,
                headers={"location": "https://example.test/"},
            ),
        )
        client = HackerRank(api_key="test-key")
        try:
            with pytest.raises(expected_exception=RedirectError):
                _ = client.users.list()
        finally:
            client.close()
