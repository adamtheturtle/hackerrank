"""Tests for the checked-in OpenAPI document and normalize helper."""

from __future__ import annotations

import json
from http import HTTPStatus
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from tests.openapi_helpers import normalize_openapi

_ROOT = Path(__file__).resolve().parents[1]
_OPENAPI_PATH = _ROOT / "openapi.json"
_LIVE_OPENAPI_URL = "https://www.hackerrank.com/apidoc"
_MOCK_OPENAPI_URL = "https://example.com/apidoc"


def _load_checked_in_spec() -> dict[str, Any]:
    """Load the repository's ``openapi.json``.

    Returns:
        The parsed OpenAPI document.
    """
    loaded: Any = json.loads(s=_OPENAPI_PATH.read_text(encoding="utf-8"))
    typed: dict[str, Any] = loaded
    return typed


def _assert_remote_openapi_matches_checked_in(*, url: str) -> None:
    """Fetch ``url`` and assert semantic equality with the checked-in
    schema.

    Args:
        url: URL of an OpenAPI document to compare.
    """
    checked = normalize_openapi(spec=_load_checked_in_spec())
    response = httpx.get(url=url, timeout=30.0)
    response.raise_for_status()
    live = normalize_openapi(spec=response.json())
    assert checked == live


class TestNormalizeOpenAPI:
    """Unit tests for ``normalize_openapi``."""

    @staticmethod
    def test_strips_examples_and_normalizes_datetime_defaults() -> None:
        """Example and date-time default differences do not affect equality."""
        left: dict[str, object] = {
            "paths": {
                "/x/api/v3/candidates/search": {
                    "get": {
                        "description": "Search  candidates.",
                        "parameters": [
                            {
                                "name": "query",
                                "type": "string",
                                "example": "alice@example.com",
                            },
                        ],
                        "responses": {
                            "200": {
                                "schema": {
                                    "properties": {
                                        "created_at": {
                                            "type": "string",
                                            "format": "date-time",
                                            "default": "2024-01-01T00:00:00Z",
                                            "example": "2024-01-01T00:00:00Z",
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "x-examples": {"ignored": True},
        }
        right: dict[str, object] = {
            "paths": {
                "/x/api/v3/candidates/search": {
                    "get": {
                        "description": "Search candidates.",
                        "parameters": [
                            {
                                "name": "query",
                                "type": "string",
                                "example": "bob@example.com",
                            },
                        ],
                        "responses": {
                            "200": {
                                "schema": {
                                    "properties": {
                                        "created_at": {
                                            "type": "string",
                                            "format": "date-time",
                                            "default": "2026-08-20T12:00:00Z",
                                            "examples": [
                                                "2026-08-20T12:00:00Z"
                                            ],
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "x-examples": {"different": True},
        }
        assert normalize_openapi(spec=left) == normalize_openapi(spec=right)

    @staticmethod
    def test_structural_differences_remain() -> None:
        """Genuine path/definition drift still fails equality."""
        left: dict[str, object] = {"paths": {"/a": {"get": {}}}}
        right: dict[str, object] = {"paths": {"/b": {"get": {}}}}
        assert normalize_openapi(spec=left) != normalize_openapi(spec=right)

    @staticmethod
    def test_preserves_non_container_scalars() -> None:
        """Non-string scalars pass through unchanged."""
        number = 42
        assert normalize_openapi(spec=number) == number
        assert normalize_openapi(spec=True) is True
        assert normalize_openapi(spec=None) is None


class TestCheckedInOpenAPI:
    """Non-network assertions about the checked-in schema."""

    @staticmethod
    def test_includes_global_candidate_search() -> None:
        """The refreshed schema documents global candidate search."""
        spec = _load_checked_in_spec()
        paths = spec["paths"]
        assert "/x/api/v3/candidates/search" in paths
        definitions = spec["definitions"]
        assert "CandidateSearchResult" in definitions
        assert "CandidateSearchAttemptResult" in definitions
        attempt_required = set(
            definitions["CandidateSearchAttemptResult"]["required"],
        )
        assert attempt_required == {"attempt_id", "test_id", "report_url"}
        result_required = set(definitions["CandidateSearchResult"]["required"])
        assert result_required == {
            "uuid",
            "name",
            "email",
            "created_at",
            "updated_at",
            "attempts",
        }

    @staticmethod
    def test_includes_current_interview_fields() -> None:
        """Interview create/update schemas include current live fields."""
        definitions = _load_checked_in_spec()["definitions"]
        for name in ("InterviewCreate", "InterviewUpdate"):
            properties = definitions[name]["properties"]
            assert "ai_assistant_available" in properties
            assert "interviewers" in properties
            assert "replace_interviewers" in properties

    @staticmethod
    def test_remote_document_matches_after_normalize() -> None:
        """A mocked remote document matches after normalization."""
        with respx.mock(assert_all_called=True) as router:
            router.get(url=_MOCK_OPENAPI_URL).mock(
                return_value=httpx.Response(
                    status_code=HTTPStatus.OK,
                    json=_load_checked_in_spec(),
                ),
            )
            _assert_remote_openapi_matches_checked_in(url=_MOCK_OPENAPI_URL)


@pytest.mark.network
def test_live_openapi_matches_checked_in_semantically() -> (
    None
):  # pragma: no cover
    """Compare the checked-in schema to the live first-party document.

    Skipped unless ``--run-network`` is passed, because fetching the
    live schema is flaky in CI.
    """
    _assert_remote_openapi_matches_checked_in(url=_LIVE_OPENAPI_URL)
