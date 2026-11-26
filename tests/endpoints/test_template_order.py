"""Test paced interview template ordering through the SDK's HTTP
boundary.
"""

from contextlib import nullcontext
from dataclasses import dataclass
from http import HTTPStatus
from unittest.mock import patch

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank

_TEMPLATE = "https://www.hackerrank.com/x/api/v3/interview_templates/12345"


@dataclass(frozen=True, kw_only=True)
class _Rebuild:
    """One desired list and its scripted server responses and calls."""

    desired: list[int]
    readbacks: list[list[int]]
    calls: list[str]
    error: str | None


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
@pytest.mark.parametrize(
    argnames="rebuild",
    argvalues=[
        _Rebuild(
            desired=[2, 1, 2], readbacks=[[2, 1]], calls=["read"], error=None
        ),
        _Rebuild(
            desired=[2, 1],
            readbacks=[[1, 2], [1, 2], [], [2, 1]],
            calls=[
                "read",
                "read",
                "remove 1",
                "remove 2",
                "read",
                'add {"question_ids":[2]}',
                "pause 2",
                'add {"question_ids":[1]}',
                "read",
            ],
            error=None,
        ),
        _Rebuild(
            desired=[],
            readbacks=[[1], [1], []],
            calls=["read", "read", "remove 1", "read"],
            error=None,
        ),
        _Rebuild(
            desired=[2],
            readbacks=[[1], [1], [1], [1]],
            calls=["read", "read", "remove 1", "read", "read"],
            error="did not clear its questions",
        ),
        _Rebuild(
            desired=[2, 1],
            readbacks=[[1, 2], [1, 2], [], [1, 2]],
            calls=[
                "read",
                "read",
                "remove 1",
                "remove 2",
                "read",
                'add {"question_ids":[2]}',
                "pause 2",
                'add {"question_ids":[1]}',
                "read",
            ],
            error="did not retain the requested question order",
        ),
        _Rebuild(
            desired=[2],
            readbacks=[[1], [1], [], [], [], [1]],
            calls=[
                "read",
                "read",
                "remove 1",
                "read",
                'add {"question_ids":[2]}',
                "read",
                "read",
                'add {"question_ids":[1]}',
                "read",
            ],
            error="did not retain the requested question order",
        ),
    ],
)
async def test_reconcile_question_order(
    *, use_async: bool, rebuild: _Rebuild
) -> None:
    """Check pacing, read-back, and restoration on incomplete
    membership.
    """
    readbacks = iter(rebuild.readbacks)
    calls: list[str] = []

    def read(_request: httpx.Request) -> httpx.Response:
        """Record a read and return the next stored question list."""
        calls.append("read")
        return httpx.Response(
            status_code=HTTPStatus.OK,
            json={
                "id": "12345",
                "name": "Sample template",
                "questions": next(readbacks),
            },
        )

    def add(request: httpx.Request) -> httpx.Response:
        """Record the IDs sent with an addition."""
        calls.append(f"add {request.content.decode(encoding='utf-8')}")
        return httpx.Response(
            status_code=HTTPStatus.OK,
            json={"id": "12345", "name": "Sample template"},
        )

    def remove(request: httpx.Request) -> httpx.Response:
        """Record the single ID sent with a removal."""
        calls.append(f"remove {request.url.params['question_id']}")
        return httpx.Response(
            status_code=HTTPStatus.OK,
            json={"id": "12345", "name": "Sample template"},
        )

    def record_pause(seconds: int, /) -> None:
        """Record the interval between successful adds."""
        calls.append(f"pause {seconds}")

    async def record_async_pause(delay: int) -> None:
        """Record the async interval without waiting."""
        record_pause(delay)

    context = (
        nullcontext()
        if rebuild.error is None
        else pytest.raises(expected_exception=ValueError, match=rebuild.error)
    )
    with respx.mock(assert_all_called=False) as router:
        _ = router.get(url=_TEMPLATE).mock(side_effect=read)
        _ = router.put(url=f"{_TEMPLATE}/add_questions").mock(side_effect=add)
        _ = router.delete(url=f"{_TEMPLATE}/remove_question").mock(
            side_effect=remove
        )
        with context:
            if use_async:
                with patch(
                    target="hackerrank.async_client.sleep",
                    new=record_async_pause,
                ):
                    async with AsyncHackerRank(api_key="test-key") as client:
                        templates = client.interview_templates
                        template = await templates.reconcile_question_order(
                            template_id=12345,
                            question_ids=rebuild.desired,
                        )
            else:
                with (
                    patch(target="hackerrank.client.sleep", new=record_pause),
                    HackerRank(api_key="test-key") as sync_client,
                ):
                    sync_templates = sync_client.interview_templates
                    template = sync_templates.reconcile_question_order(
                        template_id=12345,
                        question_ids=rebuild.desired,
                    )
            assert template.questions == list(dict.fromkeys(rebuild.desired))
    assert calls == rebuild.calls
    assert not bool(list(readbacks))
