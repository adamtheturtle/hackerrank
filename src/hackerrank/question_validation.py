"""Offline validation for HackerRank question prompts."""

from hackerrank.types import QuestionType

_MAX_CUSTOM_SYSTEM_PROMPT_LENGTH = 15_000


def validate_custom_system_prompt(
    *, question_type: str | None, custom_system_prompt: str | None
) -> None:
    """Reject overlong prompts and known unsupported question types.

    Unknown or omitted types remain available to generic requests and
    newer server APIs. None needs no validation. Empty strings are
    explicit updates.

    Args:
        question_type: Question type, or None to check length only.
        custom_system_prompt: Prompt to validate, or None to omit it.

    Raises:
        ValueError: If the prompt exceeds 15,000 characters or the known
            question type does not support it.
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
