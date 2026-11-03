"""Notes updates use required fields and return the API response."""

import json

import httpx
import pytest
import respx
from beartype import beartype

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.transports import AsyncHTTPXTransport, HTTPXTransport
from hackerrank.types import JSONValue, Question

_URL = "https://www.hackerrank.com/x/api/v3/questions/q1"


def _question() -> dict[str, JSONValue]:
    """Supply required fields and unrelated project configuration."""
    return {
        "id": "q1",
        "name": "Question",
        "type": "code",
        "problem_statement": "Candidate prompt",
        "recommended_duration": 60,
        "internal_notes": "Previous notes",
        "languages": ["python3"],
        "tags": ["AI"],
        "options": ["choice"],
        "answer": 0,
        "max_score": 100.0,
        "environment_id": 112,
        "custom_system_prompt": "  Keep this prompt.\n",
        "fullstack_project_details": {
            "configuration": {"menu": {"run": "python3 solution.py"}}
        },
    }


@beartype
def _json_object(*, value: dict[str, JSONValue]) -> dict[str, JSONValue]:
    """Check JSON at the outgoing request boundary."""
    return value


async def _update(*, use_async: bool, notes: str) -> Question | None:
    """Exercise the public operation through either transport."""
    if use_async:
        async with (
            AsyncHTTPXTransport() as transport,
            AsyncHackerRank(api_key="test-key", transport=transport) as client,
        ):
            return await client.questions.update_internal_notes(
                question_id="q1", internal_notes=notes
            )
    with (
        HTTPXTransport() as sync_transport,
        HackerRank(
            api_key="test-key", transport=sync_transport
        ) as sync_client,
    ):
        return sync_client.questions.update_internal_notes(
            question_id="q1", internal_notes=notes
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
@pytest.mark.parametrize(argnames="nullable", argvalues=[False, True])
@pytest.mark.parametrize(argnames="response_body", argvalues=[False, True])
async def test_notes_update(
    *, use_async: bool, nullable: bool, response_body: bool
) -> None:
    """One GET supplies required fields, followed by the requested PUT."""
    current = _question()
    if nullable:
        for field in ("languages", "tags", "options", "answer"):
            del current[field]
    returned = {**current, "internal_notes": "Server-formatted notes"}
    with respx.mock(assert_all_called=True) as router:
        get = router.get(url=_URL).respond(status_code=200, json=current)
        put = router.put(url=_URL).mock(
            return_value=httpx.Response(status_code=200, json=returned)
            if response_body
            else httpx.Response(status_code=204)
        )
        result = await _update(use_async=use_async, notes="New notes")
        body = _json_object(value=json.loads(s=put.calls.last.request.content))
        assert set(body) == {
            "name",
            "type",
            "internal_notes",
            "languages",
            "problem_statement",
            "recommended_duration",
            "tags",
            "options",
            "answer",
        }
        assert body["internal_notes"] == "New notes"
        for field in (
            "name",
            "type",
            "problem_statement",
            "recommended_duration",
        ):
            assert body[field] == current[field]
        for field in ("languages", "tags", "options", "answer"):
            assert body[field] == current.get(field, [])
        if response_body:
            assert result is not None
            assert result.internal_notes == "Server-formatted notes"
        else:
            assert result is None
        assert get.call_count == 1
        assert put.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
@pytest.mark.parametrize(argnames="notes", argvalues=["Previous notes", ""])
async def test_notes_are_always_written(
    *, use_async: bool, notes: str
) -> None:
    """Unchanged and empty notes still produce an update request."""
    with respx.mock(assert_all_called=True) as router:
        get = router.get(url=_URL).respond(status_code=200, json=_question())
        put = router.put(url=_URL).respond(status_code=204)
        assert await _update(use_async=use_async, notes=notes) is None
        assert (
            json.loads(s=put.calls.last.request.content)["internal_notes"]
            == notes
        )
        assert get.call_count == 1
        assert put.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
@pytest.mark.parametrize(
    argnames="missing", argvalues=["problem_statement", "recommended_duration"]
)
async def test_required_fields_must_be_available(
    *, use_async: bool, missing: str
) -> None:
    """The API-required update fields must be available to build the
    body.
    """
    current = _question()
    del current[missing]
    with respx.mock(assert_all_called=True) as router:
        get = router.get(url=_URL).respond(status_code=200, json=current)
        with pytest.raises(
            expected_exception=ValueError, match="lacks fields"
        ):
            _ = await _update(use_async=use_async, notes="New notes")
        assert get.call_count == 1
