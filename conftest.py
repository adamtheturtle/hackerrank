"""Test configuration for hackerrank-api-python."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, cast

import pytest
import respx
from openapi_mock import add_openapi_to_respx

if TYPE_CHECKING:
    from collections.abc import Generator

_BASE_URL = "https://www.hackerrank.com"
_HTTP_METHODS = frozenset(
    {"get", "post", "put", "delete", "patch", "head", "options", "trace"},
)


def _fix_schema_required(*, schema: dict[str, Any]) -> dict[str, Any]:
    """Normalize Swagger-style ``required`` flags for OpenAPI 3
    schemas.
    """
    result: dict[str, Any] = dict(schema)
    props_raw = result.get("properties")
    if isinstance(props_raw, dict):
        props = cast(dict[str, Any], props_raw)
        required_names: list[str] = []
        existing_required = result.get("required")
        if isinstance(existing_required, list):
            required_names.extend(
                name
                for name in cast(list[object], existing_required)
                if isinstance(name, str)
            )
        fixed_props: dict[str, Any] = {}
        for prop_name, prop_schema_raw in props.items():
            if not isinstance(prop_schema_raw, dict):
                continue
            prop_schema = cast(dict[str, Any], prop_schema_raw)
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
    items_raw = result.get("items")
    if isinstance(items_raw, dict):
        items = cast(dict[str, Any], items_raw)
        result["items"] = _fix_schema_required(schema=items)
    return result


def _migrate_body_parameter(*, operation: dict[str, Any]) -> dict[str, Any]:
    """Convert Swagger 2 ``in: body`` parameters to OpenAPI 3
    requestBody.
    """
    result: dict[str, Any] = dict(operation)
    params_raw = result.get("parameters")
    if not isinstance(params_raw, list):
        return result
    params = cast(list[object], params_raw)
    kept: list[object] = []
    body_param: dict[str, Any] | None = None
    for param_raw in params:
        if isinstance(param_raw, dict):
            param = cast(dict[str, Any], param_raw)
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
                schema=cast(dict[str, Any], schema_raw),
            )
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
    if not isinstance(raw_paths_obj, dict):
        return prepared

    raw_paths = cast(dict[object, object], raw_paths_obj)
    cleaned_paths: dict[str, dict[str, object]] = {}
    for raw_key_obj, raw_value_obj in raw_paths.items():
        if not isinstance(raw_key_obj, str) or not isinstance(
            raw_value_obj,
            dict,
        ):
            continue
        raw_key = raw_key_obj
        raw_value = cast(dict[object, object], raw_value_obj)
        cleaned = raw_key.split(sep="?", maxsplit=1)[0]
        merged: dict[str, object] = dict(cleaned_paths.get(cleaned, {}))
        for op_key_obj, op_val_obj in raw_value.items():
            if not isinstance(op_key_obj, str):
                continue
            op_key = op_key_obj
            if op_key in _HTTP_METHODS and isinstance(op_val_obj, dict):
                op_val = cast(dict[str, Any], op_val_obj)
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
