"""Notes-only updates preserve question state in both API clients."""

import json
from collections.abc import Callable

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
        "answer": [1],
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


def _case_equal(actual: str, expected: str, /) -> bool:
    """Represent a caller's serialization comparison policy."""
    return actual.casefold() == expected.casefold()


async def _update(
    *,
    use_async: bool,
    notes: str,
    notes_equal: Callable[[str, str], bool] | None,
) -> Question:
    """Exercise the same public operation through either transport."""
    if use_async:
        async with (
            AsyncHTTPXTransport() as async_transport,
            AsyncHackerRank(
                api_key="test-key", transport=async_transport
            ) as async_client,
        ):
            return await async_client.questions.update_internal_notes(
                question_id="q1",
                internal_notes=notes,
                notes_equal=notes_equal,
            )
    with (
        HTTPXTransport() as transport,
        HackerRank(api_key="test-key", transport=transport) as client,
    ):
        return client.questions.update_internal_notes(
            question_id="q1",
            internal_notes=notes,
            notes_equal=notes_equal,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
@pytest.mark.parametrize(argnames="nullable", argvalues=[False, True])
async def test_notes_only_update(*, use_async: bool, nullable: bool) -> None:
    """Read current state, send required fields only, and read back
    notes.
    """
    before = _question()
    after = {**before, "internal_notes": "New notes"}
    if nullable:
        for field in ("languages", "tags", "options", "answer"):
            del before[field]
            after[field] = []
    with respx.mock(assert_all_called=True) as router:
        get = router.get(url=_URL)
        _ = get.mock(
            side_effect=[
                httpx.Response(status_code=200, json=before),
                httpx.Response(status_code=200, json=after),
            ]
        )
        put = router.put(url=_URL).respond(status_code=204)
        result = await _update(
            use_async=use_async, notes="New notes", notes_equal=None
        )
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
            assert body[field] == before[field]
        for field in ("languages", "tags", "options", "answer"):
            assert body[field] == before.get(field, [])
        assert result.custom_system_prompt == "  Keep this prompt.\n"
        expected_reads = 2
        assert get.call_count == expected_reads


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
@pytest.mark.parametrize(argnames="custom_comparison", argvalues=[False, True])
async def test_unchanged_notes_skip_writes(
    *, use_async: bool, custom_comparison: bool
) -> None:
    """Equivalent notes need only one GET and no PUT."""
    with respx.mock(assert_all_called=True) as router:
        get = router.get(url=_URL).respond(status_code=200, json=_question())
        result = await _update(
            use_async=use_async,
            notes="PREVIOUS NOTES" if custom_comparison else "Previous notes",
            notes_equal=_case_equal if custom_comparison else None,
        )
        assert result.id == "q1"
        assert get.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
async def test_custom_comparison_verifies_saved_notes(
    *, use_async: bool
) -> None:
    """Caller comparison applies to read-back as well as unchanged
    checks.
    """
    with respx.mock(assert_all_called=True) as router:
        get = router.get(url=_URL)
        _ = get.mock(
            side_effect=[
                httpx.Response(status_code=200, json=_question()),
                httpx.Response(
                    status_code=200,
                    json={**_question(), "internal_notes": "NEW NOTES"},
                ),
            ]
        )
        _ = router.put(url=_URL).respond(status_code=204)
        result = await _update(
            use_async=use_async, notes="New notes", notes_equal=_case_equal
        )
        assert result.internal_notes == "NEW NOTES"


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
@pytest.mark.parametrize(
    argnames="invalid",
    argvalues=["id", "problem_statement", "recommended_duration"],
)
async def test_invalid_current_question_prevents_write(
    *, use_async: bool, invalid: str
) -> None:
    """Reject mismatched identities and incomplete required fields."""
    before = _question()
    if invalid == "id":
        before["id"] = "other"
    else:
        del before[invalid]
    with respx.mock(assert_all_called=True) as router:
        get = router.get(url=_URL).respond(status_code=200, json=before)
        with pytest.raises(
            expected_exception=ValueError,
            match="Expected question" if invalid == "id" else "lacks fields",
        ):
            _ = await _update(
                use_async=use_async, notes="New notes", notes_equal=None
            )
        assert get.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
@pytest.mark.parametrize(
    argnames="changed",
    argvalues=["internal_notes", "custom_system_prompt", "answer"],
)
async def test_unexpected_readback_fails(
    *, use_async: bool, changed: str
) -> None:
    """Check saved text and every modeled field, including scalar zero."""
    before = {**_question(), "answer": 0}
    after = {**before, "internal_notes": "New notes"}
    after[changed] = [] if changed == "answer" else "Unexpected"
    with respx.mock(assert_all_called=True) as router:
        get = router.get(url=_URL)
        _ = get.mock(
            side_effect=[
                httpx.Response(status_code=200, json=before),
                httpx.Response(status_code=200, json=after),
            ]
        )
        _ = router.put(url=_URL).respond(status_code=204)
        with pytest.raises(
            expected_exception=ValueError,
            match="did not retain notes"
            if changed == "internal_notes"
            else "changed fields other than notes",
        ):
            _ = await _update(
                use_async=use_async, notes="New notes", notes_equal=None
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
async def test_absent_notes_are_empty(*, use_async: bool) -> None:
    """Clearing absent notes is already satisfied without a write."""
    question = _question()
    del question["internal_notes"]
    with respx.mock(assert_all_called=True) as router:
        get = router.get(url=_URL).respond(status_code=200, json=question)
        result = await _update(use_async=use_async, notes="", notes_equal=None)
        assert result.internal_notes is None
        assert get.call_count == 1
