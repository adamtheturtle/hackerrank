"""Runtime validation for HackerRank API response payloads."""

from typing import TypeGuard

from beartype import beartype
from beartype.door import TypeHint

from hackerrank._dict_types import InterviewDict

type _JSONValue = (
    bool | int | float | str | list[_JSONValue] | dict[str, _JSONValue] | None
)


def _is_interviews(value: object, /) -> TypeGuard[list[InterviewDict]]:
    """Return whether a value is a list of interview objects."""
    return TypeHint(hint=list[InterviewDict]).is_bearable(obj=value)


@beartype
def object_response(
    value: dict[str, _JSONValue],
) -> dict[str, _JSONValue]:
    """Return a runtime-validated API response object."""
    return value


def interview_items(value: object) -> list[InterviewDict]:
    """Return runtime-validated interview response objects."""
    if not _is_interviews(value):
        message = "Expected the response data to contain interview objects."
        raise TypeError(message)
    return value
