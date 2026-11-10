"""Validate question fields shared by typed and generic API requests."""

from collections.abc import Mapping

from hackerrank.types import JSONValue, QuestionType

_MAX_CUSTOM_SYSTEM_PROMPT_LENGTH = 15_000


def validate_custom_system_prompt(
    *, question_type: str | None, custom_system_prompt: str | None
) -> None:
    """Reject overlong prompts and known unsupported question types.

    Unknown or omitted types remain available to generic requests and
    newer server APIs. None needs no validation. Empty strings are
    explicit updates.
    """
    if custom_system_prompt is None:
        return
    if len(custom_system_prompt) > _MAX_CUSTOM_SYSTEM_PROMPT_LENGTH:
        message = "custom_system_prompt must be at most 15,000 characters."
        raise ValueError(message)
    if (
        question_type is not None
        and question_type in QuestionType
        and not QuestionType(value=question_type).supports_custom_system_prompt
    ):
        message = (
            "custom_system_prompt is not supported for question type "
            f"{question_type!r}; use a fullstack project question."
        )
        raise ValueError(message)


def validate_question_prompt_body(*, body: Mapping[str, JSONValue]) -> None:
    """Validate prompt fields without filling in generic partial
    updates.
    """
    prompt = body.get("custom_system_prompt")
    if prompt is not None and not isinstance(prompt, str):
        message = "custom_system_prompt must be a string or None."
        raise TypeError(message)
    question_type = body.get("type")
    validate_custom_system_prompt(
        question_type=question_type
        if isinstance(question_type, str)
        else None,
        custom_system_prompt=prompt,
    )
