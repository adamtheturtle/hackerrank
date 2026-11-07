"""The complete documented operation catalogue and request preparation."""

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from importlib.resources import files
from typing import TypeGuard
from urllib.parse import quote

from beartype.door import TypeHint

from hackerrank._responses import object_response, response_data
from hackerrank.types import JSONValue


@dataclass(frozen=True, kw_only=True)
class APIOperation:
    """One documented v3 or SCIM operation."""

    id: str
    method: str
    path: str
    group: str
    summary: str
    description: str
    scim: bool
    parameters: list[dict[str, JSONValue]]
    body_schema: JSONValue
    body_required: bool
    fixed_query: dict[str, str]


@dataclass(frozen=True, kw_only=True)
class APIResponse:
    """A complete response, preserving empty bodies and pending
    statuses.
    """

    status: int
    headers: dict[str, str]
    data: dict[str, JSONValue] | None


def api_catalogue() -> dict[str, JSONValue]:
    """Read the packaged operation catalogue and referenced body
    schemas.
    """
    resource = files(anchor="hackerrank").joinpath("api_operations.json")
    return parse_api_object(text=resource.read_text(encoding="utf-8"))


def api_operations() -> dict[str, APIOperation]:
    """Return all documented operations, keyed by their stable command
    name.
    """
    catalogue = api_catalogue()
    result: dict[str, APIOperation] = {}
    for value in response_data(
        catalogue["operations"], list[dict[str, JSONValue]]
    ):
        operation = APIOperation(
            id=response_data(value["id"], str),
            method=response_data(value["method"], str),
            path=response_data(value["path"], str),
            group=response_data(value["group"], str),
            summary=response_data(value["summary"], str),
            description=response_data(value["description"], str),
            scim=response_data(value["scim"], bool),
            parameters=response_data(
                value["parameters"], list[dict[str, JSONValue]]
            ),
            body_schema=value["bodySchema"],
            body_required=response_data(value["bodyRequired"], bool),
            fixed_query=response_data(value["fixedQuery"], dict[str, str]),
        )
        result[operation.id] = operation
    return result


def _query_value(value: JSONValue) -> str:
    """Encode scalar or CSV-array query values without losing booleans."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str | int | float):
        return str(object=value)
    if not _is_query_sequence(value):
        message = "Query values must be scalars or arrays of scalars."
        raise ValueError(message)
    return ",".join(_query_value(value=item) for item in value)


def _is_query_sequence(value: JSONValue, /) -> TypeGuard[Sequence[JSONValue]]:
    """Validate a JSON sequence without treating an abstract class as a
    constructor.
    """
    return TypeHint(hint=Sequence[JSONValue]).is_bearable(obj=value)


def prepare_operation(
    *,
    operation: str,
    path_parameters: Mapping[str, str | int] | None,
    query: Mapping[str, JSONValue] | None,
    body: Mapping[str, JSONValue] | None,
) -> tuple[APIOperation, str, dict[str, str | int]]:
    """Resolve a documented operation and encode its path/query inputs."""
    operations = api_operations()
    if operation not in operations:
        message = f"Unknown API operation: {operation}"
        raise ValueError(message)
    selected = operations[operation]
    path = selected.path
    parameters: Mapping[str, str | int] = dict[str, str | int]()
    if path_parameters is not None:
        parameters = path_parameters
    query_values: Mapping[str, JSONValue] = dict[str, JSONValue]()
    if query is not None:
        query_values = query
    params: dict[str, str | int] = dict(selected.fixed_query)
    params.update(
        {
            name: _query_value(value=value)
            for name, value in query_values.items()
            if value is not None
        }
    )
    for parameter in selected.parameters:
        name = response_data(parameter["name"], str)
        if parameter["location"] == "path":
            if name not in parameters or not bool(
                str(object=parameters[name])
            ):
                message = f"Missing path parameter: {name}"
                raise ValueError(message)
            path = path.replace(
                "{" + name + "}",
                quote(string=str(object=parameters[name]), safe=""),
            )
        elif (
            parameter["location"] == "query"
            and parameter["required"] is True
            and name not in params
        ):
            message = f"Missing query parameter: {name}"
            raise ValueError(message)
    if selected.body_required and body is None:
        message = "This operation requires a JSON body."
        raise ValueError(message)
    return selected, path, params


def parse_api_object(*, text: str) -> dict[str, JSONValue]:
    """Parse a JSON object using the SDK's runtime response validation."""
    return object_response(value=json.loads(s=text))
