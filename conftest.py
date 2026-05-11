"""Test configuration for hackerrank-api-python."""

import json
from collections.abc import Generator

import pytest
import respx
from openapi_mock import add_openapi_to_respx

_BASE_URL = "https://www.hackerrank.com"


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
    raw_paths = openapi_spec.get("paths", {})
    if isinstance(raw_paths, dict):
        cleaned_paths: dict[str, dict[str, object]] = {}
        for path, ops in raw_paths.items():
            if not isinstance(ops, dict):
                continue
            cleaned = path.split("?", 1)[0]
            existing = cleaned_paths.get(cleaned)
            if existing is not None:
                merged: dict[str, object] = dict(existing)
                merged.update(ops)
                cleaned_paths[cleaned] = merged
            else:
                cleaned_paths[cleaned] = dict(ops)
        openapi_spec["paths"] = cleaned_paths
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
