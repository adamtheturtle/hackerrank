"""Contract tests for Interviews V2 artifacts, notes and audit cursors."""

from __future__ import annotations

import json
from http import HTTPStatus

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.exceptions import HackerRankError
from hackerrank.types import (
    InterviewArtifacts,
    InterviewArtifactsPending,
    User,
)

_BASE = "https://www.hackerrank.com/x/api/v3"


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
async def test_artifacts_and_pending(*, asynchronous: bool) -> None:
    """Decode available and missing artifacts, then preserve HTTP 202."""
    payload = {
        "interview_id": "123",
        "transcript_url": {"state": "unavailable", "location": None},
        "interviewer_notes": [{"note_id": 4, "evaluator_id": 8}],
        "questions": [
            {
                "tab_id": "2",
                "question_sequence": 1,
                "library_question_id": None,
                "qtype": "code",
                "question_name": "Example",
                "problem_statement": None,
                "artifacts": {
                    "submitted_code_url": {
                        "state": "available",
                        "location": "https://example.com/code?signature=example",
                    },
                    "future_artifact": {
                        "state": "not_applicable",
                        "location": None,
                    },
                },
            }
        ],
    }
    with respx.mock(assert_all_called=True) as router:
        route = router.get(url=f"{_BASE}/interviews/123/artifacts").mock(
            side_effect=[
                httpx.Response(status_code=HTTPStatus.OK, json=payload),
                httpx.Response(
                    status_code=HTTPStatus.ACCEPTED,
                    headers={"Retry-After": "180"},
                    json={"message": "Pending"},
                ),
            ],
        )
        if asynchronous:
            async with AsyncHackerRank(api_key="test") as client:
                result = await client.interviews.get_artifacts(
                    interview_id="123"
                )
                pending = await client.interviews.get_artifacts(
                    interview_id="123"
                )
        else:
            with HackerRank(api_key="test") as sync_client:
                result = sync_client.interviews.get_artifacts(
                    interview_id="123"
                )
                pending = sync_client.interviews.get_artifacts(
                    interview_id="123"
                )
    assert isinstance(result, InterviewArtifacts)
    question = result.questions[0]
    assert question.question_name == "Example"
    assert question.tab_id == "2"
    assert question.question_sequence == 1
    assert question.library_question_id is None
    assert question.qtype == "code"
    assert question.project_mode is None
    assert result.transcript_url.state == "unavailable"
    assert result.questions[0].artifacts["future_artifact"].location is None
    expected_evaluator = 8
    assert result.interviewer_notes[0].evaluator_id == expected_evaluator
    assert isinstance(pending, InterviewArtifactsPending)
    expected_delay = 180
    assert pending.retry_after == expected_delay
    assert pending.message == "Pending"
    assert len(route.calls.last.request.url.params) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
async def test_notes(*, asynchronous: bool) -> None:
    """GET uses CSV note IDs and PATCH preserves empty content."""
    with respx.mock(assert_all_called=True) as router:
        get_route = router.get(url=f"{_BASE}/interviews/123/notes").respond(
            status_code=HTTPStatus.OK,
            json={
                "notes": [
                    {"note_id": 4, "content": "Feedback", "editable": True}
                ]
            },
        )
        patch_route = router.patch(
            url=f"{_BASE}/interviews/123/notes"
        ).respond(
            status_code=HTTPStatus.OK,
            json={"content": "", "updated_at": "2026-11-07T12:00:00Z"},
        )
        if asynchronous:
            async with AsyncHackerRank(api_key="test") as client:
                notes = await client.interviews.get_notes(
                    interview_id="123", note_ids=[4, 5]
                )
                saved = await client.interviews.update_note(
                    interview_id="123", content=""
                )
        else:
            with HackerRank(api_key="test") as sync_client:
                notes = sync_client.interviews.get_notes(
                    interview_id="123", note_ids=[4, 5]
                )
                saved = sync_client.interviews.update_note(
                    interview_id="123", content=""
                )
    assert get_route.calls.last.request.url.params["note_ids"] == "4,5"
    assert json.loads(s=patch_route.calls.last.request.content) == {
        "content": ""
    }
    assert notes[0].editable is True
    assert notes[0].evaluator_name is None
    assert saved.content == ""
    assert saved.updated_at == "2026-11-07T12:00:00Z"


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
async def test_audit_cursor_and_offset(*, asynchronous: bool) -> None:
    """Expose window metadata and send only the opaque continuation
    token.
    """
    with respx.mock(assert_all_called=True) as router:
        offset_route = router.get(url=f"{_BASE}/audit_log").respond(
            status_code=HTTPStatus.OK,
            json={
                "data": [
                    {
                        "source_id": 9,
                        "source_type": "test",
                        "action": "update",
                        "user": {"id": "8", "email": "actor@example.com"},
                    }
                ],
                "offset_window_limit": 10000,
                "offset_window_exhausted": True,
            },
        )
        cursor_route = router.get(url=f"{_BASE}/audit_log/cursor").mock(
            side_effect=[
                httpx.Response(
                    status_code=HTTPStatus.OK,
                    json={
                        "data": [],
                        "page_total": 0,
                        "has_more": True,
                        "next_cursor": "opaque+/=",
                        "total": 12345,
                    },
                ),
                httpx.Response(
                    status_code=HTTPStatus.OK,
                    json={
                        "data": [],
                        "page_total": 0,
                        "has_more": False,
                        "next_cursor": None,
                    },
                ),
            ]
        )
        if asynchronous:
            async with AsyncHackerRank(api_key="test") as client:
                offset = await client.audit_logs.list(
                    user_id="8", source_type="test", source_id="9"
                )
                first = await client.audit_logs.list_cursor(
                    user="8", include_total=True
                )
                first_request = cursor_route.calls.last.request
                last = await client.audit_logs.list_cursor(
                    cursor=first.next_cursor,
                    source_id="ignored",
                    include_total=True,
                )
        else:
            with HackerRank(api_key="test") as sync_client:
                offset = sync_client.audit_logs.list(
                    user_id="8", source_type="test", source_id="9"
                )
                first = sync_client.audit_logs.list_cursor(
                    user="8", include_total=True
                )
                first_request = cursor_route.calls.last.request
                last = sync_client.audit_logs.list_cursor(
                    cursor=first.next_cursor,
                    source_id="ignored",
                    include_total=True,
                )
    assert offset_route.calls.last.request.url.params["user"] == "8"
    assert "user_id" not in offset_route.calls.last.request.url.params
    assert isinstance(offset.data[0].user, User)
    assert offset.data[0].user.email == "actor@example.com"
    assert offset.offset_window_exhausted is True
    expected_window = 10000
    assert offset.offset_window_limit == expected_window
    expected_total = 12345
    assert first.total == expected_total
    assert dict(first_request.url.params) == {
        "user": "8",
        "include_total": "true",
    }
    assert dict(cursor_route.calls.last.request.url.params) == {
        "cursor": "opaque+/="
    }
    assert last.next_cursor is None
    assert last.total is None
    assert last.has_more is False


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(
    argnames="status",
    argvalues=[
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.GONE,
        HTTPStatus.SERVICE_UNAVAILABLE,
    ],
)
async def test_cursor_errors(
    *, asynchronous: bool, status: HTTPStatus
) -> None:
    """Expose invalid, expired and unavailable cursor responses."""
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(url=f"{_BASE}/audit_log/cursor").respond(
            status_code=status,
            json={"errors": ["Cursor error"], "code": "EXAMPLE"},
        )
        if asynchronous:
            async with AsyncHackerRank(api_key="test") as client:
                with pytest.raises(
                    expected_exception=HackerRankError
                ) as error:
                    _ = await client.audit_logs.list_cursor(cursor="expired")
        else:
            with (
                HackerRank(api_key="test") as sync_client,
                pytest.raises(expected_exception=HackerRankError) as error,
            ):
                _ = sync_client.audit_logs.list_cursor(cursor="expired")
    assert error.value.status_code == status
