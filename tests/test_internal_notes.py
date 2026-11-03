"""Notes-only updates preserve question state in both API clients."""

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


async def _update(
    *,
    use_async: bool,
    notes: str,
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
            )
    with (
        HTTPXTransport() as transport,
        HackerRank(api_key="test-key", transport=transport) as client,
    ):
        return client.questions.update_internal_notes(
            question_id="q1",
            internal_notes=notes,
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
            assert body[field] == before[field]
        for field in ("languages", "tags", "options", "answer"):
            assert body[field] == before.get(field, [])
        assert result.custom_system_prompt == "  Keep this prompt.\n"
        expected_reads = 2
        assert get.call_count == expected_reads


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
async def test_unchanged_notes_are_written(*, use_async: bool) -> None:
    """Identical notes still receive a PUT and a verified read-back."""
    question = _question()
    with respx.mock(assert_all_called=True) as router:
        get = router.get(url=_URL).respond(status_code=200, json=question)
        put = router.put(url=_URL).respond(status_code=204)
        result = await _update(use_async=use_async, notes="Previous notes")
        assert result.internal_notes == "Previous notes"
        body = _json_object(value=json.loads(s=put.calls.last.request.content))
        assert body["internal_notes"] == "Previous notes"
        expected_reads = 2
        assert get.call_count == expected_reads
        assert put.call_count == 1


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
            _ = await _update(use_async=use_async, notes="New notes")
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
            _ = await _update(use_async=use_async, notes="New notes")


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
async def test_absent_notes_are_empty(*, use_async: bool) -> None:
    """Clearing absent notes still writes and verifies an empty result."""
    question = _question()
    del question["internal_notes"]
    with respx.mock(assert_all_called=True) as router:
        get = router.get(url=_URL).respond(status_code=200, json=question)
        put = router.put(url=_URL).respond(status_code=204)
        result = await _update(use_async=use_async, notes="")
        assert result.internal_notes is None
        body = _json_object(value=json.loads(s=put.calls.last.request.content))
        assert body["internal_notes"] == ""
        expected_reads = 2
        assert get.call_count == expected_reads
        assert put.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="use_async", argvalues=[False, True])
async def test_html_readback_formatting(*, use_async: bool) -> None:
    """Both clients accept the platform's harmless HTML serialization."""
    before = _question()
    requested = "<div><p>Driver&#8217;s rate</p><pre>  code\n</pre></div>"
    saved = "<div>\n<p>Driver\u2019s rate</p>\n<pre>  code\n</pre>\n</div>"
    after = {**before, "internal_notes": saved}
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(url=_URL).mock(
            side_effect=[
                httpx.Response(status_code=200, json=before),
                httpx.Response(status_code=200, json=after),
            ]
        )
        put = router.put(url=_URL).respond(status_code=204)
        result = await _update(use_async=use_async, notes=requested)
        assert result.internal_notes == saved
        assert (
            json.loads(s=put.calls.last.request.content)["internal_notes"]
            == requested
        )
