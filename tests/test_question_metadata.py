"""Selected question updates preserve required metadata at the HTTP
boundary.
"""

import json

import pytest
import respx
from beartype import beartype

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.exceptions import HackerRankError
from hackerrank.types import (
    JSONValue,
    Question,
    QuestionAnswer,
    QuestionChanges,
)

_URL = "https://www.hackerrank.com/x/api/v3/questions/q1"


def _current() -> dict[str, JSONValue]:
    """Include required fields and optional data that must remain
    untouched.
    """
    return {
        "id": "q1",
        "type": "fullstack",
        "name": "Current name",
        "internal_notes": "Current notes",
        "problem_statement": "Current statement",
        "recommended_duration": 0,
        "languages": ["python3"],
        "tags": ["Backend"],
        "options": ["Choice"],
        "answer": "0",
        "max_score": 100.0,
        "environment_id": 112,
        "role_type": "backend",
        "custom_system_prompt": "Keep this prompt",
        "fullstack_project_details": {
            "configuration": {"menu": {"run": "run"}}
        },
    }


@beartype
def _body(*, value: dict[str, JSONValue]) -> dict[str, JSONValue]:
    """Validate decoded request data before making assertions."""
    return value


async def _update(
    *, asynchronous: bool, changes: QuestionChanges
) -> Question | None:
    """Exercise either public client without replacing namespace
    methods.
    """
    if asynchronous:
        async with AsyncHackerRank(api_key="synthetic") as client:
            return await client.questions.update_metadata(
                question_id="q1", changes=changes
            )
    with HackerRank(api_key="synthetic") as sync_client:
        return sync_client.questions.update_metadata(
            question_id="q1", changes=changes
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(argnames="answer", argvalues=[None, "0", 0, [0, 1]])
@pytest.mark.parametrize(argnames="nullable", argvalues=[False, True])
async def test_preserves_required_fields(
    *, asynchronous: bool, answer: QuestionAnswer | None, nullable: bool
) -> None:
    """Only requested optional fields accompany unchanged required
    values.
    """
    current = _current()
    current["answer"] = answer
    if nullable:
        for field in ("internal_notes", "languages", "tags", "options"):
            current[field] = None
    with respx.mock(assert_all_called=True) as router:
        get = router.get(url=_URL).respond(status_code=200, json=current)
        put = router.put(url=_URL + "/").respond(status_code=204)
        assert (
            await _update(
                asynchronous=asynchronous,
                changes=QuestionChanges(
                    custom_system_prompt="  New prompt.\n"
                ),
            )
            is None
        )
        body = _body(value=json.loads(s=put.calls.last.request.content))
        assert body == {
            "name": current["name"],
            "type": "fullstack",
            "internal_notes": "" if nullable else current["internal_notes"],
            "languages": [] if nullable else current["languages"],
            "problem_statement": current["problem_statement"],
            "recommended_duration": 0,
            "tags": [] if nullable else current["tags"],
            "options": [] if nullable else current["options"],
            "answer": [] if answer is None else answer,
            "custom_system_prompt": "  New prompt.\n",
        }
        assert get.call_count == put.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
async def test_applies_every_supported_change(*, asynchronous: bool) -> None:
    """Explicit empty values and complete project metadata reach the
    API.
    """
    changes = QuestionChanges(
        name="New name",
        internal_notes="",
        languages=[],
        problem_statement="",
        recommended_duration=0,
        tags=[],
        options=[],
        answer="",
        score=0.0,
        environment_id=123,
        role_type="frontend",
        scoring_command="score",
        scoring_files=["tests.py"],
        readonly_paths=[],
        default_files=["solution.py"],
        configuration={"menu": {"run": "python3 solution.py"}},
        testcases=[{"name": "case", "score": 0}],
        custom_system_prompt="",
    )
    expected: dict[str, JSONValue] = {
        "name": "New name",
        "type": "fullstack",
        "internal_notes": "",
        "languages": [],
        "problem_statement": "",
        "recommended_duration": 0,
        "tags": [],
        "options": [],
        "answer": "",
        "score": 0,
        "environment_id": 123,
        "role_type": "frontend",
        "scoring_command": "score",
        "scoring_files": ["tests.py"],
        "readonly_paths": [],
        "default_files": ["solution.py"],
        "configuration": {"menu": {"run": "python3 solution.py"}},
        "testcases": [{"name": "case", "score": 0}],
        "custom_system_prompt": "",
    }
    current = _current()
    del current["problem_statement"]
    del current["recommended_duration"]
    returned = {**current, "name": "New name"}
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(url=_URL).respond(status_code=200, json=current)
        put = router.put(url=_URL + "/").respond(
            status_code=200, json=returned
        )
        result = await _update(asynchronous=asynchronous, changes=changes)
        assert result is not None
        assert result.name == "New name"
        assert (
            _body(value=json.loads(s=put.calls.last.request.content))
            == expected
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(
    argnames="missing", argvalues=["problem_statement", "recommended_duration"]
)
async def test_missing_required_fields_prevent_write(
    *, asynchronous: bool, missing: str
) -> None:
    """An incomplete read never invents a statement or a duration."""
    current = _current()
    del current[missing]
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(url=_URL).respond(status_code=200, json=current)
        with pytest.raises(
            expected_exception=ValueError, match="lacks fields"
        ):
            _ = await _update(
                asynchronous=asynchronous,
                changes=QuestionChanges(name="New name"),
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(
    argnames="question_type", argvalues=["code", "whiteboard", "mcq"]
)
async def test_unsupported_prompt_prevents_write(
    *, asynchronous: bool, question_type: str
) -> None:
    """Prompt validation uses the current question type before any PUT."""
    current = _current()
    current["type"] = question_type
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(url=_URL).respond(status_code=200, json=current)
        with pytest.raises(
            expected_exception=ValueError, match="not supported"
        ):
            _ = await _update(
                asynchronous=asynchronous,
                changes=QuestionChanges(custom_system_prompt=""),
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
async def test_read_failure_prevents_write(*, asynchronous: bool) -> None:
    """A failed read is propagated without attempting a metadata
    update.
    """
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(url=_URL).respond(status_code=404)
        with pytest.raises(expected_exception=HackerRankError):
            _ = await _update(
                asynchronous=asynchronous, changes=QuestionChanges(name="New")
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
async def test_empty_changes_still_write_required_metadata(
    *, asynchronous: bool
) -> None:
    """An empty selection still performs the documented read and write."""
    current = _current()
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(url=_URL).respond(status_code=200, json=current)
        put = router.put(url=_URL + "/").respond(status_code=204)
        assert (
            await _update(asynchronous=asynchronous, changes=QuestionChanges())
            is None
        )
        body = _body(value=json.loads(s=put.calls.last.request.content))
        assert body["name"] == current["name"]
        assert body["answer"] == "0"
        assert "custom_system_prompt" not in body
        assert "configuration" not in body
