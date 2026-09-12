"""Runtime validation for HackerRank API response payloads."""

from typing import TypeGuard

from beartype import beartype
from beartype.door import TypeHint

from hackerrank import _dict_types

type _JSONValue = (
    bool | int | float | str | list[_JSONValue] | dict[str, _JSONValue] | None
)


@beartype
def _is_interviews(
    value: object,
    /,
) -> TypeGuard[list[_dict_types.InterviewDict]]:
    """Return whether a value is a list of interview objects."""
    return TypeHint(hint=list[_dict_types.InterviewDict]).is_bearable(
        obj=value,
    )


@beartype
def object_response(
    value: dict[str, _JSONValue],
) -> dict[str, _JSONValue]:
    """Return a runtime-validated API response object."""
    return value


@beartype
def interview_items(value: object) -> list[_dict_types.InterviewDict]:
    """Return runtime-validated interview response objects."""
    if not _is_interviews(value):
        message = "Expected the response data to contain interview objects."
        raise TypeError(message)
    return value


@beartype
def _is_environment(
    value: object,
    /,
) -> TypeGuard[_dict_types.EnvironmentDict]:
    """Return whether a value is an environment response object."""
    return TypeHint(hint=_dict_types.EnvironmentDict).is_bearable(obj=value)


@beartype
def environment_response(value: object) -> _dict_types.EnvironmentDict:
    """Return a runtime-validated environment response object."""
    if not _is_environment(value):
        message = "Expected the response data to contain an environment."
        raise TypeError(message)
    return value


@beartype
def _is_object_list(value: object, /) -> TypeGuard[list[object]]:
    """Return whether a value is a list."""
    return isinstance(value, list)


@beartype
def _is_items[ResponseItem](
    value: object,
    item_type: type[ResponseItem],
    /,
) -> TypeGuard[list[ResponseItem]]:
    """Validate a list of response objects."""
    item_hint = TypeHint(hint=item_type)
    return _is_object_list(value) and all(
        item_hint.is_bearable(obj=item) for item in value
    )


@beartype
def response_items[ResponseItem](
    *,
    value: object,
    item_type: type[ResponseItem],
) -> list[ResponseItem]:
    """Return runtime-validated API response objects."""
    if not _is_items(value, item_type):
        message = "Expected the response data to contain valid objects."
        raise TypeError(message)
    return value
