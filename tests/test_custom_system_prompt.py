"""Project system prompts keep their exact text and top-level wire
shape.
"""

from __future__ import annotations

import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.types import Question
from tests.test_documented_request_params import _last_route_json

_BASE = "https://www.hackerrank.com/x/api/v3/questions"
_QUESTION = {"id": "q1", "type": "fullstack", "name": "Project"}
_PROMPTS = [None, "", "  Give hints.\nDo not solve.  ", "\U0001f422" * 15_000]


def _assert_prompt(*, route: respx.Route, prompt: str | None) -> None:
    """Verify omission or exact top-level serialization."""
    body = _last_route_json(route=route)
    if prompt is None:
        assert "custom_system_prompt" not in body
    else:
        assert body["custom_system_prompt"] == prompt
    assert "configuration" not in body


@pytest.mark.parametrize(
    argnames="prompt",
    argvalues=_PROMPTS,
    ids=["omitted", "empty", "multiline", "unicode-limit"],
)
def test_sync_prompt(prompt: str | None) -> None:
    """Sync create and update serialize prompts without trimming or
    nesting.
    """
    with respx.mock(assert_all_called=True) as router:
        create = router.post(url=_BASE).respond(
            status_code=200, json=_QUESTION
        )
        update = router.put(url=f"{_BASE}/q1").respond(
            status_code=200, json=_QUESTION
        )
        with HackerRank(api_key="test-key") as client:
            _ = client.questions.create(
                name="Project",
                type="fullstack",
                problem_statement="Build it.",
                recommended_duration=60,
                custom_system_prompt=prompt,
            )
            _ = client.questions.update(
                question_id="q1",
                name="Project",
                type="fullstack",
                internal_notes="",
                languages=[],
                problem_statement="Build it.",
                recommended_duration=60,
                tags=[],
                options=[],
                answer=[],
                custom_system_prompt=prompt,
            )
        _assert_prompt(route=create, prompt=prompt)
        _assert_prompt(route=update, prompt=prompt)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames="prompt",
    argvalues=_PROMPTS,
    ids=["omitted", "empty", "multiline", "unicode-limit"],
)
async def test_async_prompt(prompt: str | None) -> None:
    """Async create and update have the same prompt semantics."""
    with respx.mock(assert_all_called=True) as router:
        create = router.post(url=_BASE).respond(
            status_code=200, json=_QUESTION
        )
        update = router.put(url=f"{_BASE}/q1").respond(
            status_code=200, json=_QUESTION
        )
        async with AsyncHackerRank(api_key="test-key") as client:
            _ = await client.questions.create(
                name="Project",
                type="fullstack",
                problem_statement="Build it.",
                recommended_duration=60,
                custom_system_prompt=prompt,
            )
            _ = await client.questions.update(
                question_id="q1",
                name="Project",
                type="fullstack",
                internal_notes="",
                languages=[],
                problem_statement="Build it.",
                recommended_duration=60,
                tags=[],
                options=[],
                answer=[],
                custom_system_prompt=prompt,
            )
        _assert_prompt(route=create, prompt=prompt)
        _assert_prompt(route=update, prompt=prompt)


def test_sync_rejects_long_prompt() -> None:
    """Overlong prompts fail before any sync request."""
    with (
        respx.mock(assert_all_mocked=True) as router,
        HackerRank(api_key="test-key") as client,
    ):
        with pytest.raises(expected_exception=ValueError, match="15,000"):
            _ = client.questions.create(
                name="Project",
                type="fullstack",
                problem_statement="Build it.",
                recommended_duration=60,
                custom_system_prompt="x" * 15_001,
            )
        with pytest.raises(expected_exception=ValueError, match="15,000"):
            _ = client.questions.update(
                question_id="q1",
                name="Project",
                type="fullstack",
                internal_notes="",
                languages=[],
                problem_statement="Build it.",
                recommended_duration=60,
                tags=[],
                options=[],
                answer=[],
                custom_system_prompt="x" * 15_001,
            )
        assert len(router.calls) == 0


@pytest.mark.asyncio
async def test_async_rejects_long_prompt() -> None:
    """Overlong prompts fail before any async request."""
    with respx.mock(assert_all_mocked=True) as router:
        async with AsyncHackerRank(api_key="test-key") as client:
            with pytest.raises(expected_exception=ValueError, match="15,000"):
                _ = await client.questions.create(
                    name="Project",
                    type="fullstack",
                    problem_statement="Build it.",
                    recommended_duration=60,
                    custom_system_prompt="x" * 15_001,
                )
            with pytest.raises(expected_exception=ValueError, match="15,000"):
                _ = await client.questions.update(
                    question_id="q1",
                    name="Project",
                    type="fullstack",
                    internal_notes="",
                    languages=[],
                    problem_statement="Build it.",
                    recommended_duration=60,
                    tags=[],
                    options=[],
                    answer=[],
                    custom_system_prompt="x" * 15_001,
                )
        assert len(router.calls) == 0


@pytest.mark.parametrize(
    argnames="prompt", argvalues=[None, "", "  Give hints.\n"]
)
def test_question_response(prompt: str | None) -> None:
    """Returned prompts expose exact text; absent prompts remain
    optional.
    """
    question = Question.from_dict(
        data={
            "id": "q1",
            "type": "fullstack",
            "name": "Project",
            "custom_system_prompt": prompt,
        }
    )
    assert question.custom_system_prompt == prompt
    assert (
        Question.from_dict(
            data={"id": "q1", "type": "code", "name": "Q"}
        ).custom_system_prompt
        is None
    )
