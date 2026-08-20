"""Test configuration for hackerrank-api-python."""

from __future__ import annotations

import json
<<<<<<< HEAD
from typing import TYPE_CHECKING, Any, TypeGuard
=======
from typing import TYPE_CHECKING, Any, cast
>>>>>>> origin/fix/conftest-pyright-unknowns

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
<<<<<<< HEAD
    result = dict(schema)
    props_obj = result.get("properties")
    if _is_str_keyed_dict(value=props_obj):
        props = props_obj
=======
    result: dict[str, Any] = dict(schema)
    props_raw = result.get("properties")
    if isinstance(props_raw, dict):
        props = cast("dict[str, Any]", props_raw)
>>>>>>> origin/fix/conftest-pyright-unknowns
        required_names: list[str] = []
        existing_required_obj = result.get("required")
        if _is_object_list(value=existing_required_obj):
            required_names.extend(
<<<<<<< HEAD
                name for name in existing_required_obj if isinstance(name, str)
            )
        fixed_props: dict[str, Any] = {}
        for prop_name, prop_schema_obj in props.items():
            if not _is_str_keyed_dict(value=prop_schema_obj):
                continue
            prop_schema = prop_schema_obj
=======
                name
                for name in cast("list[object]", existing_required)
                if isinstance(name, str)
            )
        fixed_props: dict[str, Any] = {}
        for prop_name, prop_schema_raw in props.items():
            if not isinstance(prop_schema_raw, dict):
                continue
            prop_schema = cast("dict[str, Any]", prop_schema_raw)
>>>>>>> origin/fix/conftest-pyright-unknowns
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
<<<<<<< HEAD
    items_obj = result.get("items")
    if _is_str_keyed_dict(value=items_obj):
        result["items"] = _fix_schema_required(schema=items_obj)
=======
    items_raw = result.get("items")
    if isinstance(items_raw, dict):
        items = cast("dict[str, Any]", items_raw)
        result["items"] = _fix_schema_required(schema=items)
>>>>>>> origin/fix/conftest-pyright-unknowns
    return result


def _migrate_body_parameter(*, operation: dict[str, Any]) -> dict[str, Any]:
    """Convert Swagger 2 ``in: body`` parameters to OpenAPI 3
    requestBody.
    """
<<<<<<< HEAD
    result = dict(operation)
    params_obj = result.get("parameters")
    if not _is_object_list(value=params_obj):
=======
    result: dict[str, Any] = dict(operation)
    params_raw = result.get("parameters")
    if not isinstance(params_raw, list):
>>>>>>> origin/fix/conftest-pyright-unknowns
        return result
    params = cast("list[object]", params_raw)
    kept: list[object] = []
    body_param: dict[str, Any] | None = None
<<<<<<< HEAD
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
=======
    for param_raw in params:
        if isinstance(param_raw, dict):
            param = cast("dict[str, Any]", param_raw)
            if param.get("in") == "body":
                body_param = param
            else:
                kept.append(param)
        else:
            kept.append(param_raw)
    result["parameters"] = kept
    if body_param is not None and "requestBody" not in result:
        schema_raw = body_param.get("schema", {})
        schema: object = schema_raw
        if isinstance(schema_raw, dict):
            schema = _fix_schema_required(
                schema=cast("dict[str, Any]", schema_raw),
            )
>>>>>>> origin/fix/conftest-pyright-unknowns
        result["requestBody"] = {
            "required": bool(body_param.get("required", False)),
            "content": {"application/json": {"schema": schema}},
        }
    return result


def _prepare_openapi_spec(*, spec: dict[str, object]) -> dict[str, object]:
    """Normalize the HackerRank OpenAPI document for mock route
    registration.
    """
    prepared: dict[str, object] = dict(spec)
    raw_paths_obj = prepared.get("paths", {})
    if not _is_str_keyed_dict(value=raw_paths_obj):
        return prepared

    raw_paths = cast("dict[object, object]", raw_paths_obj)
    cleaned_paths: dict[str, dict[str, object]] = {}
<<<<<<< HEAD
    for raw_key, raw_value_obj in raw_paths_obj.items():
        if not _is_str_keyed_dict(value=raw_value_obj):
=======
    for raw_key_obj, raw_value_obj in raw_paths.items():
        if not isinstance(raw_key_obj, str) or not isinstance(
            raw_value_obj,
            dict,
        ):
>>>>>>> origin/fix/conftest-pyright-unknowns
            continue
        raw_key = raw_key_obj
        raw_value = cast("dict[object, object]", raw_value_obj)
        cleaned = raw_key.split(sep="?", maxsplit=1)[0]
        merged: dict[str, object] = dict(cleaned_paths.get(cleaned, {}))
<<<<<<< HEAD
        for op_key, op_val in raw_value_obj.items():
            if op_key in _HTTP_METHODS and _is_str_keyed_dict(value=op_val):
=======
        for op_key_obj, op_val_obj in raw_value.items():
            if not isinstance(op_key_obj, str):
                continue
            op_key = op_key_obj
            if op_key in _HTTP_METHODS and isinstance(op_val_obj, dict):
                op_val = cast("dict[str, Any]", op_val_obj)
>>>>>>> origin/fix/conftest-pyright-unknowns
                merged[op_key] = _migrate_body_parameter(operation=op_val)
            else:
                merged[op_key] = op_val_obj
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
