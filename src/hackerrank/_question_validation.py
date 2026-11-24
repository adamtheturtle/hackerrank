"""Validate prompt fields in generic question requests."""

from collections.abc import Mapping

from hackerrank.question_validation import validate_custom_system_prompt
from hackerrank.types import JSONValue


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
