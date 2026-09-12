"""Runtime validation for HackerRank API response payloads."""

from typing import TypeGuard

from beartype.door import TypeHint

from hackerrank import _dict_types


@beartype
def _is_interviews(
    value: object,
    /,
) -> TypeGuard[list[_dict_types.InterviewDict]]:
    """Return whether a value is a list of interview objects."""
    return TypeHint(hint=list[_dict_types.InterviewDict]).is_bearable(
        obj=value,
    )


def object_response(
    value: object,
) -> dict[str, _dict_types.JSONValue]:
    """Return a runtime-validated API response object."""
    return response_data(value, dict[str, _dict_types.JSONValue])


def _is_response[Response](
    value: object,
    response_type: type[Response],
    /,
) -> TypeGuard[Response]:
    """Return whether a value has the expected API response shape."""
    return TypeHint(hint=response_type).is_bearable(obj=value)


def response_data[Response](
    value: object,
    response_type: type[Response],
    /,
) -> Response:
    """Return API response data narrowed to its domain type."""
    if not _is_response(value, response_type):
        message = "Response data did not have the expected shape."
        raise TypeError(message)
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
