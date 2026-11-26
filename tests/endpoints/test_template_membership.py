"""Test interview template reconciliation through both SDK clients."""

import json
from contextlib import nullcontext
from http import HTTPStatus
from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.exceptions import ForbiddenError

if TYPE_CHECKING:
    from hackerrank.types import InterviewTemplate

_TEMPLATE = "https://www.hackerrank.com/x/api/v3/interview_templates/12345"


def _response(*, questions: list[int] | None) -> httpx.Response:
    """Preserve the wire distinction between absent and empty
    membership.
    """
    body: dict[str, str | list[int]] = {
        "id": "12345",
        "name": "Sample template",
    }
    if questions is not None:
        body["questions"] = questions
    return httpx.Response(status_code=HTTPStatus.OK, json=body)


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
@pytest.mark.parametrize(
    argnames=("initial", "desired", "updated", "additions", "removals"),
    argvalues=[
        ([3, 2, 1], [4, 2, 5, 4], [2, 4, 5], [4, 5], [1, 3]),
        ([3, 2], [2, 3, 3], [3, 2], [], []),
        ([1], [], [], [], [1]),
        ([], [1], [1], [1], []),
        (None, [1], None, [], []),
    ],
)
async def test_reconcile_questions(
    *,
    use_async: bool,
    initial: list[int] | None,
    desired: list[int],
    updated: list[int] | None,
    additions: list[int],
    removals: list[int],
) -> None:
    """Add before removing, skip a membership no-op, and reject
    omissions.
    """
    expected_methods = ["GET"]
    responses = [_response(questions=initial)]
    requests: list[httpx.Request] = []

    def read(request: httpx.Request) -> httpx.Response:
        """Capture a read and return its scripted response."""
        requests.append(request)
        return responses.pop(0)

    def write(request: httpx.Request) -> httpx.Response:
        """Capture a write without returning membership."""
        requests.append(request)
        return _response(questions=None)

    with respx.mock(assert_all_called=True) as router:
        if len(additions) > 0:
            _ = router.put(url=f"{_TEMPLATE}/add_questions").mock(
                side_effect=write,
            )
            expected_methods.append("PUT")
        for question_id in removals:
            _ = router.delete(
                url=f"{_TEMPLATE}/remove_question",
                params={"question_id": str(object=question_id)},
            ).mock(side_effect=write)
            expected_methods.append("DELETE")
        if len(additions) + len(removals) > 0:
            responses.append(_response(questions=updated))
            expected_methods.append("GET")
        _ = router.get(url=_TEMPLATE).mock(side_effect=read)
        result: InterviewTemplate | None = None
        context = (
            pytest.raises(
                expected_exception=ValueError,
                match="omitted question membership",
            )
            if initial is None
            else nullcontext()
        )
        with context:
            if use_async:
                async with AsyncHackerRank(api_key="test-key") as client:
                    result = (
                        await client.interview_templates.reconcile_questions(
                            template_id=12345,
                            question_ids=desired,
                        )
                    )
            else:
                with HackerRank(api_key="test-key") as sync_client:
                    result = (
                        sync_client.interview_templates.reconcile_questions(
                            template_id=12345,
                            question_ids=desired,
                        )
                    )
    assert [request.method for request in requests] == expected_methods
    if result is not None:
        assert result.questions == updated
    if len(additions) > 0:
        assert json.loads(s=requests[1].content) == {
            "question_ids": additions,
        }


def test_reconcile_questions_retries_from_fresh_membership() -> None:
    """Repeat the desired membership after a partial failure."""
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(url=_TEMPLATE).mock(
            side_effect=[
                _response(questions=[1, 2, 3]),
                _response(questions=[2, 3, 4]),
                _response(questions=[3, 4]),
            ],
        )
        add = router.put(url=f"{_TEMPLATE}/add_questions").mock(
            return_value=_response(questions=[1, 2, 3, 4]),
        )
        first_remove = router.delete(
            url=f"{_TEMPLATE}/remove_question",
            params={"question_id": "1"},
        ).mock(return_value=_response(questions=[2, 3, 4]))
        second_remove = router.delete(
            url=f"{_TEMPLATE}/remove_question",
            params={"question_id": "2"},
        ).mock(
            side_effect=[
                httpx.Response(status_code=HTTPStatus.FORBIDDEN, json={}),
                _response(questions=[3, 4]),
            ],
        )
        with HackerRank(api_key="test-key") as client:
            with pytest.raises(expected_exception=ForbiddenError):
                _ = client.interview_templates.reconcile_questions(
                    template_id=12345,
                    question_ids=[3, 4],
                )
            result = client.interview_templates.reconcile_questions(
                template_id=12345,
                question_ids=[3, 4],
            )
    assert add.call_count == first_remove.call_count == 1
    attempts = 2
    assert second_remove.call_count == attempts
    assert result.questions == [3, 4]
