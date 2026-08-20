"""Tests for the checked-in OpenAPI document and normalizer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from tests.openapi_helpers import normalize_openapi

_ROOT = Path(__file__).resolve().parents[1]
_OPENAPI_PATH = _ROOT / "openapi.json"
_LIVE_OPENAPI_URL = "https://www.hackerrank.com/apidoc"


def _load_checked_in_spec() -> dict[str, Any]:
    """Load the repository's ``openapi.json``.

    Returns:
        The parsed OpenAPI document.
    """
    return json.loads(s=_OPENAPI_PATH.read_text(encoding="utf-8"))


class TestNormalizeOpenAPI:
    """Unit tests for ``normalize_openapi``."""

    @staticmethod
    def test_strips_examples_and_normalizes_datetime_defaults() -> None:
        """Example and datetime default differences do not affect equality."""
        left: dict[str, Any] = {
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
        right: dict[str, Any] = {
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
        left = {"paths": {"/a": {"get": {}}}}
        right = {"paths": {"/b": {"get": {}}}}
        assert normalize_openapi(spec=left) != normalize_openapi(spec=right)


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


@pytest.mark.network
def test_live_openapi_matches_checked_in_semantically() -> None:
    """Compare the checked-in schema to the live first-party document.

    Skipped unless ``--run-network`` is passed, because fetching the
    live schema is flaky in CI.
    """
    checked = normalize_openapi(spec=_load_checked_in_spec())
    response = httpx.get(url=_LIVE_OPENAPI_URL, timeout=30.0)
    response.raise_for_status()
    live = normalize_openapi(spec=response.json())
    assert checked == live
