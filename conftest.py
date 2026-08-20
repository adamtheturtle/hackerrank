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


def _fix_schema_required(*, schema: dict[str, Any]) -> dict[str, Any]:
    """Normalize Swagger-style ``required`` flags for OpenAPI 3
    schemas.
    """
    result = dict(schema)
    props = result.get("properties")
    if isinstance(props, dict):
        required_names: list[str] = []
        existing_required = result.get("required")
        if isinstance(existing_required, list):
            required_names.extend(
                name for name in existing_required if isinstance(name, str)
            )
        fixed_props: dict[str, Any] = {}
        for prop_name, prop_schema in props.items():
            if not isinstance(prop_name, str) or not isinstance(
                prop_schema, dict
            ):
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
    items = result.get("items")
    if isinstance(items, dict):
        result["items"] = _fix_schema_required(schema=items)
    return result


def _migrate_body_parameter(*, operation: dict[str, Any]) -> dict[str, Any]:
    """Convert Swagger 2 ``in: body`` parameters to OpenAPI 3
    requestBody.
    """
    result = dict(operation)
    params = result.get("parameters")
    if not isinstance(params, list):
        return result
    kept: list[object] = []
    body_param: dict[str, Any] | None = None
    for param in params:
        if isinstance(param, dict) and param.get("in") == "body":
            body_param = param
        else:
            kept.append(param)
    result["parameters"] = kept
    if body_param is not None and "requestBody" not in result:
        schema = body_param.get("schema", {})
        if isinstance(schema, dict):
            schema = _fix_schema_required(schema=schema)
        result["requestBody"] = {
            "required": bool(body_param.get("required", False)),
            "content": {"application/json": {"schema": schema}},
        }
    return result


def _prepare_openapi_spec(*, spec: dict[str, object]) -> dict[str, object]:
    """Make the HackerRank OpenAPI document parseable by openapi-mock."""
    prepared = dict(spec)
    raw_paths_obj = prepared.get("paths", {})
    if not isinstance(raw_paths_obj, dict):
        return prepared

    cleaned_paths: dict[str, dict[str, object]] = {}
    for raw_key, raw_value in raw_paths_obj.items():
        if not isinstance(raw_key, str) or not isinstance(raw_value, dict):
            continue
        cleaned = raw_key.split(sep="?", maxsplit=1)[0]
        merged: dict[str, object] = dict(cleaned_paths.get(cleaned, {}))
        for op_key, op_val in raw_value.items():
            if not isinstance(op_key, str):
                continue
            if op_key in _HTTP_METHODS and isinstance(op_val, dict):
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
