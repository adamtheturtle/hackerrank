"""Known question types share capabilities without closing the API."""

import json

import pytest
import respx

from hackerrank.api import api_catalogue
from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.types import JSONValue, Question, QuestionType


def test_question_types_cover_the_documented_api() -> None:
    """The enum covers every type in the packaged API schema."""
    catalogue = api_catalogue()
    definitions = catalogue["definitions"]
    assert isinstance(definitions, dict)
    for name in ("QuestionCreate", "QuestionUpdate", "QuestionShow"):
        schema = definitions[name]
        assert isinstance(schema, dict)
        properties = schema["properties"]
        assert isinstance(properties, dict)
        field = properties["type"]
        assert isinstance(field, dict)
        values = field["enum"]
        assert isinstance(values, list)
        assert set(values) <= {kind.value for kind in QuestionType}


@pytest.mark.parametrize(
    argnames="question_type",
    argvalues=[*(kind.value for kind in QuestionType), "future_type"],
)
def test_response_types_remain_strings(question_type: str) -> None:
    """Known and future values retain their exact response text."""
    question = Question.from_dict(
        data={"id": "1", "name": "Example", "type": question_type}
    )
    assert type(question.type) is str
    assert question.type == question_type
    assert question.supports_custom_system_prompt == (
        question_type == "fullstack"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(
    argnames="question_type",
    argvalues=[
        QuestionType.CODE,
        QuestionType.APPROX,
        QuestionType.MCQ,
        QuestionType.MULTIPLE_MCQ,
        QuestionType.WHITEBOARD,
        QuestionType.FILE_UPLOAD,
        QuestionType.TEXT_ANSWER,
        QuestionType.FULLSTACK,
    ],
)
async def test_enum_writes_are_plain_api_strings(
    *, asynchronous: bool, question_type: QuestionType
) -> None:
    """Every enum member is accepted by both public typed clients."""
    with respx.mock(assert_all_called=True) as router:
        route = router.post(
            url="https://www.hackerrank.com/x/api/v3/questions"
        ).respond(
            status_code=200,
            json={"id": "1", "name": "Example", "type": question_type.value},
        )
        if asynchronous:
            async with AsyncHackerRank(api_key="test") as client:
                result = await client.questions.create(
                    name="Example",
                    type=question_type,
                    problem_statement="Prompt",
                    recommended_duration=60,
                )
        else:
            with HackerRank(api_key="test") as sync_client:
                result = sync_client.questions.create(
                    name="Example",
                    type=question_type,
                    problem_statement="Prompt",
                    recommended_duration=60,
                )
        assert result.type == question_type.value
        body = json.loads(s=route.calls.last.request.content)
        assert type(body["type"]) is str
        assert body["type"] == question_type.value
        assert "custom_system_prompt" not in body


async def _call_generic_question(
    *,
    asynchronous: bool,
    operation: str,
    parameters: dict[str, str] | None,
    body: dict[str, JSONValue],
) -> None:
    """Exercise shared generic request preparation through either
    client.
    """
    if asynchronous:
        async with AsyncHackerRank(api_key="test") as client:
            _ = await client.api.call(
                operation=operation, path_parameters=parameters, body=body
            )
    else:
        with HackerRank(api_key="test") as sync_client:
            _ = sync_client.api.call(
                operation=operation, path_parameters=parameters, body=body
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(
    argnames="operation",
    argvalues=["api_create_question", "api_update_question"],
)
@pytest.mark.parametrize(
    argnames=("body", "error"),
    argvalues=[
        (
            {"type": QuestionType.CODE, "custom_system_prompt": "Hints"},
            ValueError,
        ),
        ({"type": "whiteboard", "custom_system_prompt": ""}, ValueError),
        (
            {"type": "fullstack", "custom_system_prompt": "x" * 15_001},
            ValueError,
        ),
        ({"type": "fullstack", "custom_system_prompt": 1}, TypeError),
        ({"type": "fullstack", "custom_system_prompt": "  Hints\n"}, None),
        ({"type": "future_project", "custom_system_prompt": ""}, None),
        ({"custom_system_prompt": "Hints"}, None),
        ({"type": "code", "custom_system_prompt": None}, None),
    ],
    ids=[
        "code",
        "whiteboard",
        "overlong",
        "invalid-prompt",
        "project",
        "future-type",
        "partial-update",
        "omitted-prompt",
    ],
)
async def test_generic_question_prompt_validation(
    *,
    asynchronous: bool,
    operation: str,
    body: dict[str, JSONValue],
    error: type[Exception] | None,
) -> None:
    """Generic calls validate before transport and retain partial
    bodies.
    """
    parameters = (
        {"question_id": "1"} if operation == "api_update_question" else None
    )
    with respx.mock(assert_all_mocked=True) as router:
        if error is None:
            route = router.route().respond(status_code=200, json={"ok": True})
            await _call_generic_question(
                asynchronous=asynchronous,
                operation=operation,
                parameters=parameters,
                body=body,
            )
            assert json.loads(s=route.calls.last.request.content) == body
        else:
            with pytest.raises(expected_exception=error):
                await _call_generic_question(
                    asynchronous=asynchronous,
                    operation=operation,
                    parameters=parameters,
                    body=body,
                )
            assert len(router.calls) == 0
