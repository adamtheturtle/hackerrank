"""Test configuration for hackerrank-api-python."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, TypeGuard

import pytest
import respx
from openapi_mock import add_openapi_to_respx

if TYPE_CHECKING:
    from collections.abc import Generator

_BASE_URL = "https://www.hackerrank.com"
_HTTP_METHODS = frozenset(
    {"get", "post", "put", "delete", "patch", "head", "options", "trace"},
)


def _is_str_keyed_dict(*, value: object) -> TypeGuard[dict[str, Any]]:
    """Return whether ``value`` is a ``dict`` with ``str`` keys."""
    if not isinstance(value, dict):
        return False
    keys: list[object] = list(value)
    return all(isinstance(key, str) for key in keys)


def _is_object_list(*, value: object) -> TypeGuard[list[object]]:
    """Return whether ``value`` is a ``list``."""
    return isinstance(value, list)


def _fix_schema_required(*, schema: dict[str, Any]) -> dict[str, Any]:
    """Normalize Swagger-style ``required`` flags for OpenAPI 3
    schemas.
    """
    result = dict(schema)
    props_obj = result.get("properties")
    if _is_str_keyed_dict(value=props_obj):
        props = props_obj
        required_names: list[str] = []
        existing_required_obj = result.get("required")
        if _is_object_list(value=existing_required_obj):
            required_names.extend(
                name for name in existing_required_obj if isinstance(name, str)
            )
        fixed_props: dict[str, Any] = {}
        for prop_name, prop_schema_obj in props.items():
            if not _is_str_keyed_dict(value=prop_schema_obj):
                continue
            prop_schema = prop_schema_obj
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
    items_obj = result.get("items")
    if _is_str_keyed_dict(value=items_obj):
        result["items"] = _fix_schema_required(schema=items_obj)
    return result


def _migrate_body_parameter(*, operation: dict[str, Any]) -> dict[str, Any]:
    """Convert Swagger 2 ``in: body`` parameters to OpenAPI 3
    requestBody.
    """
    result = dict(operation)
    params_obj = result.get("parameters")
    if not _is_object_list(value=params_obj):
        return result
    kept: list[object] = []
    body_param: dict[str, Any] | None = None
    for param_obj in params_obj:
        if (
            _is_str_keyed_dict(value=param_obj)
            and param_obj.get("in") == "body"
        ):
            body_param = param_obj
        else:
            kept.append(param_obj)
    result["parameters"] = kept
    if body_param is not None and "requestBody" not in result:
        schema_obj = body_param.get("schema", {})
        schema: object = schema_obj
        if _is_str_keyed_dict(value=schema_obj):
            schema = _fix_schema_required(schema=schema_obj)
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
    raw_paths_obj = prepared.get("paths", {})
    if not _is_str_keyed_dict(value=raw_paths_obj):
        return prepared

    cleaned_paths: dict[str, dict[str, object]] = {}
    for raw_key, raw_value_obj in raw_paths_obj.items():
        if not _is_str_keyed_dict(value=raw_value_obj):
            continue
        cleaned = raw_key.split(sep="?", maxsplit=1)[0]
        merged: dict[str, object] = dict(cleaned_paths.get(cleaned, {}))
        for op_key, op_val in raw_value_obj.items():
            if op_key in _HTTP_METHODS and _is_str_keyed_dict(value=op_val):
                merged[op_key] = _migrate_body_parameter(operation=op_val)
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
