"""Test configuration for hackerrank-api-python."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest
import respx
from openapi_mock import add_openapi_to_respx

if TYPE_CHECKING:
    from collections.abc import Generator

_BASE_URL = "https://www.hackerrank.com"
_HTTP_METHODS = frozenset(
    {"get", "post", "put", "delete", "patch", "head", "options", "trace"},
)


def _as_str_keyed_dict(*, value: object) -> dict[str, Any] | None:
    """Return ``value`` as a ``str``-keyed dict, or ``None``."""
    if not isinstance(value, dict):
        return None
    # Route through ``Any`` so strict unknown-key iteration is allowed.
    raw: Any = value
    result: dict[str, Any] = {}
    for key_obj, item in raw.items():
        if not isinstance(key_obj, str):
            return None
        result[key_obj] = item
    return result


def _as_object_list(*, value: object) -> list[object] | None:
    """Return ``value`` as a list, or ``None``."""
    if not isinstance(value, list):
        return None
    raw: Any = value
    return list(raw)


def _fix_schema_required(*, schema: dict[str, Any]) -> dict[str, Any]:
    """Normalize Swagger-style ``required`` flags for OpenAPI 3
    schemas.
    """
    result = dict(schema)
    props = _as_str_keyed_dict(value=result.get("properties"))
    if props is not None:
        required_names: list[str] = []
        existing_required = _as_object_list(value=result.get("required"))
        if existing_required is not None:
            required_names.extend(
                name for name in existing_required if isinstance(name, str)
            )
        fixed_props: dict[str, Any] = {}
        for prop_name, prop_schema_obj in props.items():
            prop_schema = _as_str_keyed_dict(value=prop_schema_obj)
            if prop_schema is None:
                continue
            fixed_prop = _fix_schema_required(schema=prop_schema)
            if (
                fixed_prop.pop("required", None) is True
                and prop_name not in required_names
            ):
                required_names.append(prop_name)
            fixed_props[prop_name] = fixed_prop
        result["properties"] = fixed_props
        if required_names:
            result["required"] = required_names
        elif "required" in result and not isinstance(result["required"], list):
            result.pop("required", None)
    items = _as_str_keyed_dict(value=result.get("items"))
    if items is not None:
        result["items"] = _fix_schema_required(schema=items)
    return result


def _migrate_body_parameter(*, operation: dict[str, Any]) -> dict[str, Any]:
    """Convert Swagger 2 ``in: body`` parameters to OpenAPI 3
    requestBody.
    """
    result = dict(operation)
    params = _as_object_list(value=result.get("parameters"))
    if params is None:
        return result
    kept: list[object] = []
    body_param: dict[str, Any] | None = None
    for param_obj in params:
        param = _as_str_keyed_dict(value=param_obj)
        if param is not None and param.get("in") == "body":
            body_param = param
        else:
            kept.append(param_obj)
    result["parameters"] = kept
    if body_param is not None and "requestBody" not in result:
        schema_obj = body_param.get("schema", {})
        schema: object = schema_obj
        schema_dict = _as_str_keyed_dict(value=schema_obj)
        if schema_dict is not None:
            schema = _fix_schema_required(schema=schema_dict)
        result["requestBody"] = {
            "required": bool(body_param.get("required", False)),
            "content": {"application/json": {"schema": schema}},
        }
    return result


def _prepare_openapi_spec(*, spec: dict[str, object]) -> dict[str, object]:
    """Normalize the HackerRank OpenAPI document for mock route
    registration.
    """
    prepared = dict(spec)
    raw_paths = _as_str_keyed_dict(value=prepared.get("paths", {}))
    if raw_paths is None:
        return prepared

    cleaned_paths: dict[str, dict[str, object]] = {}
    for raw_key, raw_value_obj in raw_paths.items():
        raw_value = _as_str_keyed_dict(value=raw_value_obj)
        if raw_value is None:
            continue
        cleaned = raw_key.split(sep="?", maxsplit=1)[0]
        merged: dict[str, object] = dict(cleaned_paths.get(cleaned, {}))
        for op_key, op_val in raw_value.items():
            op_dict = _as_str_keyed_dict(value=op_val)
            if op_key in _HTTP_METHODS and op_dict is not None:
                merged[op_key] = _migrate_body_parameter(operation=op_dict)
            else:
                merged[op_key] = op_val
        cleaned_paths[cleaned] = merged
    prepared["paths"] = cleaned_paths
    return prepared


@pytest.fixture(name="mock_hackerrank_api")
def fixture_mock_hackerrank_api(
    request: pytest.FixtureRequest,
) -> Generator[respx.MockRouter]:
    """Provide a respx mock router backed by the OpenAPI spec.

    Args:
        request: The pytest request, used to locate the
            ``openapi.json`` file in the project root.

    Yields:
        The configured respx mock router.
    """
    openapi_spec_path = request.config.rootpath / "openapi.json"
    spec_text = openapi_spec_path.read_text(encoding="utf-8")
    openapi_spec: dict[str, object] = json.loads(s=spec_text)
    openapi_spec = _prepare_openapi_spec(spec=openapi_spec)
    with respx.mock(
        base_url=_BASE_URL,
        assert_all_called=False,
    ) as mock_router:
        add_openapi_to_respx(
            mock_obj=mock_router,
            spec=openapi_spec,
            base_url=_BASE_URL,
        )
        yield mock_router
