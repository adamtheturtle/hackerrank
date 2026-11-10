"""Question answers retain the representation returned by the API."""

import json

import pytest
import respx
from beartype.roar import BeartypeCallHintParamViolation

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.types import JSONValue, Question, QuestionAnswer

_BASE = "https://www.hackerrank.com/x/api/v3/questions"
_ANSWERS: list[QuestionAnswer | None] = [None, "", "0", "[1,2]", 0, [0, 1]]


async def _read_question(*, asynchronous: bool, listing: bool) -> Question:
    """Read an individual question or its containing page."""
    if asynchronous:
        async with AsyncHackerRank(api_key="synthetic") as client:
            if listing:
                return (await client.questions.list())[0]
            return await client.questions.get(question_id="q1")
    with HackerRank(api_key="synthetic") as sync_client:
        if listing:
            return sync_client.questions.list()[0]
        return sync_client.questions.get(question_id="q1")


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(argnames="listing", argvalues=[False, True])
@pytest.mark.parametrize(argnames="answer", argvalues=_ANSWERS)
async def test_response_answer_is_preserved(
    *, asynchronous: bool, listing: bool, answer: QuestionAnswer | None
) -> None:
    """Lists and individual reads accept each supported answer shape."""
    question = {"id": "q1", "name": "Choices", "type": "mcq", "answer": answer}
    with respx.mock(assert_all_called=True) as router:
        if listing:
            _ = router.get(url=_BASE).respond(
                status_code=200, json={"data": [question], "total": 1}
            )
        else:
            _ = router.get(url=_BASE + "/q1").respond(
                status_code=200, json=question
            )
        result = await _read_question(
            asynchronous=asynchronous, listing=listing
        )
    assert result.answer == answer


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
async def test_missing_answer_remains_absent(*, asynchronous: bool) -> None:
    """An optional answer is still optional in a question response."""
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(url=_BASE + "/q1").respond(
            status_code=200, json={"id": "q1", "name": "Code", "type": "code"}
        )
        result = await _read_question(asynchronous=asynchronous, listing=False)
    assert result.answer is None


async def _write_question(
    *, asynchronous: bool, answer: QuestionAnswer
) -> None:
    """Pass the same answer through question creation and replacement."""
    if asynchronous:
        async with AsyncHackerRank(api_key="synthetic") as client:
            created = await client.questions.create(
                name="Choices",
                type="mcq",
                problem_statement="Choose",
                recommended_duration=60,
                answer=answer,
            )
            updated = await client.questions.update(
                question_id=created.id,
                name="Choices",
                type="mcq",
                internal_notes="",
                languages=[],
                problem_statement="Choose",
                recommended_duration=60,
                tags=[],
                options=[],
                answer=answer,
            )
    else:
        with HackerRank(api_key="synthetic") as sync_client:
            created = sync_client.questions.create(
                name="Choices",
                type="mcq",
                problem_statement="Choose",
                recommended_duration=60,
                answer=answer,
            )
            updated = sync_client.questions.update(
                question_id=created.id,
                name="Choices",
                type="mcq",
                internal_notes="",
                languages=[],
                problem_statement="Choose",
                recommended_duration=60,
                tags=[],
                options=[],
                answer=answer,
            )
    assert created.answer == answer
    assert updated is not None
    assert updated.answer == answer


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(
    argnames="answer", argvalues=["", "0", "[1,2]", 0, [0, 1]]
)
async def test_request_answer_is_preserved(
    *, asynchronous: bool, answer: QuestionAnswer
) -> None:
    """String answers stay strings when read values are sent back."""
    question = {"id": "q1", "name": "Choices", "type": "mcq", "answer": answer}
    with respx.mock(assert_all_called=True) as router:
        created = router.post(url=_BASE + "/").respond(
            status_code=200, json=question
        )
        updated = router.put(url=_BASE + "/q1/").respond(
            status_code=200, json=question
        )
        await _write_question(asynchronous=asynchronous, answer=answer)
        assert (
            json.loads(s=created.calls.last.request.content)["answer"]
            == answer
        )
        assert (
            json.loads(s=updated.calls.last.request.content)["answer"]
            == answer
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(argnames="listing", argvalues=[False, True])
@pytest.mark.parametrize(
    argnames="answer",
    argvalues=[{"unexpected": "object"}, ["not an integer"], 0.5],
)
async def test_unsupported_answer_shapes_still_fail(
    *, asynchronous: bool, listing: bool, answer: JSONValue
) -> None:
    """Widening string support does not disable answer validation."""
    question = {"id": "q1", "name": "Choices", "type": "mcq", "answer": answer}
    with respx.mock(assert_all_called=True) as router:
        if listing:
            _ = router.get(url=_BASE).respond(
                status_code=200, json={"data": [question]}
            )
        else:
            _ = router.get(url=_BASE + "/q1").respond(
                status_code=200, json=question
            )
        with pytest.raises(
            expected_exception=(TypeError, BeartypeCallHintParamViolation)
        ):
            _ = await _read_question(
                asynchronous=asynchronous, listing=listing
            )


async def _create_without_answer(*, asynchronous: bool) -> None:
    """Explicit None retains the existing omission behavior on
    creation.
    """
    if asynchronous:
        async with AsyncHackerRank(api_key="synthetic") as client:
            _ = await client.questions.create(
                name="Choices",
                type="mcq",
                problem_statement="Choose",
                recommended_duration=60,
                answer=None,
            )
    else:
        with HackerRank(api_key="synthetic") as sync_client:
            _ = sync_client.questions.create(
                name="Choices",
                type="mcq",
                problem_statement="Choose",
                recommended_duration=60,
                answer=None,
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
async def test_none_answer_is_not_sent(*, asynchronous: bool) -> None:
    """Creation still omits an answer supplied as None."""
    with respx.mock(assert_all_called=True) as router:
        route = router.post(url=_BASE + "/").respond(
            status_code=200,
            json={"id": "q1", "name": "Choices", "type": "mcq"},
        )
        await _create_without_answer(asynchronous=asynchronous)
        assert "answer" not in json.loads(s=route.calls.last.request.content)
