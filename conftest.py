"""Test configuration for hackerrank-api-python."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import respx
from openapi_mock import add_openapi_to_respx
from pydantic import TypeAdapter, ValidationError

if TYPE_CHECKING:
    from collections.abc import Generator

_BASE_URL = "https://www.hackerrank.com"
_HTTP_METHODS = frozenset(
    {"get", "post", "put", "delete", "patch", "head", "options", "trace"},
)

type _JSONValue = (
    bool | int | float | str | list[_JSONValue] | dict[str, _JSONValue] | None
)


def _as_json_object(*, value: object) -> dict[str, _JSONValue] | None:
    """Return ``value`` as a JSON object, or ``None``."""
    try:
        return TypeAdapter(type=dict[str, _JSONValue]).validate_python(
            value,
            strict=True,
        )
    except ValidationError:
        return None


def _as_json_list(*, value: object) -> list[_JSONValue] | None:
    """Return ``value`` as a JSON array, or ``None``."""
    try:
        return TypeAdapter(type=list[_JSONValue]).validate_python(
            value,
            strict=True,
        )
    except ValidationError:
        return None


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register command-line options used by this test suite.

    Args:
        parser: The pytest argument parser.
    """
    parser.addoption(
        "--run-network",
        action="store_true",
        default=False,
        help="Run tests marked with @pytest.mark.network.",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers.

    Args:
        config: The pytest config object.
    """
    config.addinivalue_line(
        name="markers",
        line=(
            "network: tests that fetch live resources "
            "(skipped without --run-network)"
        ),
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Skip network tests unless ``--run-network`` is given.

    Args:
        config: The pytest config object.
        items: Collected test items.
    """
    if config.getoption(name="--run-network"):
        return
    skip_network = pytest.mark.skip(reason="need --run-network option to run")
    for item in items:
        if "network" in item.keywords:
            item.add_marker(marker=skip_network)


def _fix_schema_required(
    *, schema: dict[str, _JSONValue]
) -> dict[str, _JSONValue]:
    """Normalize Swagger-style ``required`` flags for OpenAPI 3
    schemas.
    """
    result = dict(schema)
    props = _as_json_object(value=result.get("properties"))
    if props is not None:
        required_names: list[_JSONValue] = []
        existing_required = _as_json_list(value=result.get("required"))
        if existing_required is not None:
            required_names.extend(
                name for name in existing_required if isinstance(name, str)
            )
        fixed_props: dict[str, _JSONValue] = {}
        for prop_name, prop_schema_raw in props.items():
            prop_schema = _as_json_object(value=prop_schema_raw)
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
        if bool(required_names):
            result["required"] = required_names
        elif "required" in result and not isinstance(result["required"], list):
            _ = result.pop("required", None)
    items = _as_json_object(value=result.get("items"))
    if items is not None:
        result["items"] = _fix_schema_required(schema=items)
    return result


def _migrate_body_parameter(
    *, operation: dict[str, _JSONValue]
) -> dict[str, _JSONValue]:
    """Convert Swagger 2 ``in: body`` parameters to OpenAPI 3
    requestBody.
    """
    result = dict(operation)
    params = _as_json_list(value=result.get("parameters"))
    if params is None:
        return result
    kept: list[_JSONValue] = []
    body_param: dict[str, _JSONValue] | None = None
    for param_raw in params:
        param = _as_json_object(value=param_raw)
        if param is not None and param.get("in") == "body":
            body_param = param
        else:
            kept.append(param_raw)
    result["parameters"] = kept
    if body_param is not None and "requestBody" not in result:
        schema_raw = body_param.get("schema", {})
        schema: _JSONValue = schema_raw
        schema_dict = _as_json_object(value=schema_raw)
        if schema_dict is not None:
            schema = _fix_schema_required(schema=schema_dict)
        result["requestBody"] = {
            "required": bool(body_param.get("required", False)),
            "content": {"application/json": {"schema": schema}},
        }
    return result


def _prepare_openapi_spec(
    *, spec: dict[str, _JSONValue]
) -> dict[str, _JSONValue]:
    """Normalize the HackerRank OpenAPI document for mock route
    registration.
    """
    prepared = dict(spec)
    raw_paths = _as_json_object(value=prepared.get("paths", {}))
    if raw_paths is None:
        return prepared

    cleaned_paths: dict[str, dict[str, _JSONValue]] = {}
    for raw_key, raw_value_obj in raw_paths.items():
        raw_value = _as_json_object(value=raw_value_obj)
        if raw_value is None:
            continue
        cleaned = raw_key.split(sep="?", maxsplit=1)[0]
        merged = dict(cleaned_paths.get(cleaned, {}))
        for op_key, op_val_obj in raw_value.items():
            op_val = _as_json_object(value=op_val_obj)
            if op_key in _HTTP_METHODS and op_val is not None:
                merged[op_key] = _migrate_body_parameter(operation=op_val)
            else:
                merged[op_key] = op_val_obj
        cleaned_paths[cleaned] = merged
    json_paths = dict[str, _JSONValue](cleaned_paths)
    prepared["paths"] = json_paths
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
    openapi_spec = TypeAdapter(type=dict[str, _JSONValue]).validate_json(
        spec_text,
        strict=True,
    )
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
