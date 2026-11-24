"""Test explicit polling for a created question through both clients."""

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.exceptions import (
    ForbiddenError,
    HackerRankError,
    NotFoundError,
)
from hackerrank.types import Question

_URL = "https://www.hackerrank.com/x/api/v3/questions/123"


async def _wait(
    *, asynchronous: bool, retry_delays: tuple[float, ...]
) -> Question:
    """Call the public readiness helper for the selected client."""
    if asynchronous:
        async with AsyncHackerRank(api_key="test") as client:
            return await client.questions.wait_until_readable(
                question_id="123", retry_delays=retry_delays
            )
    with HackerRank(api_key="test") as sync_client:
        return sync_client.questions.wait_until_readable(
            question_id="123", retry_delays=retry_delays
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(argnames="initially_missing", argvalues=[False, True])
async def test_wait_for_readable_question(
    *, asynchronous: bool, initially_missing: bool
) -> None:
    """An immediate or eventual success returns the requested question."""
    responses = [httpx.Response(status_code=404)] if initially_missing else []
    responses.append(
        httpx.Response(
            status_code=200,
            json={"id": "123", "type": "code", "name": "Example"},
        )
    )
    with respx.mock(assert_all_called=True) as router:
        route = router.get(url=_URL).mock(side_effect=responses)
        question = await _wait(asynchronous=asynchronous, retry_delays=(0,))

    assert question.id == "123"
    assert route.call_count == len(responses)


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(
    argnames=("status", "error", "retry_delays", "count"),
    argvalues=[
        (403, ForbiddenError, (0.0,), 1),
        (404, NotFoundError, (), 1),
        (404, NotFoundError, (0.0, 0.0), 3),
    ],
)
async def test_wait_for_readable_question_errors(
    *,
    asynchronous: bool,
    status: int,
    error: type[HackerRankError],
    retry_delays: tuple[float, ...],
    count: int,
) -> None:
    """Only a 404 uses the retry schedule. The last error is preserved."""
    responses = [
        httpx.Response(
            status_code=status, content=f"response {index}".encode()
        )
        for index in range(count)
    ]
    with respx.mock(assert_all_called=True) as router:
        route = router.get(url=_URL).mock(side_effect=responses)
        with pytest.raises(expected_exception=error) as exc_info:
            _ = await _wait(
                asynchronous=asynchronous, retry_delays=retry_delays
            )

    assert route.call_count == count
    assert exc_info.value.content == f"response {count - 1}".encode()


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(argnames="delay", argvalues=[-1.0, float("inf")])
async def test_reject_invalid_readiness_retry_delay(
    *, asynchronous: bool, delay: float
) -> None:
    """Invalid schedules fail before the first request."""
    with (
        respx.mock(assert_all_called=True),
        pytest.raises(
            expected_exception=ValueError, match="finite and non-negative"
        ),
    ):
        _ = await _wait(asynchronous=asynchronous, retry_delays=(0, delay))
