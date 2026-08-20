"""Helpers for comparing OpenAPI documents semantically."""

from __future__ import annotations

import json
import re
from typing import Any

# ISO-8601-ish date / date-time strings that appear as dynamic defaults
# or examples in HackerRank's live schema.
_DATETIMEISH_RE = re.compile(
    pattern=(
        r"^\d{4}-\d{2}-\d{2}"
        r"(?:[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?"
        r"(?:Z|[+-]\d{2}:?\d{2})?)?$"
    ),
)

_WHITESPACE_RE = re.compile(pattern=r"\s+")

_DYNAMIC_KEYS = frozenset({"example", "examples", "x-examples"})


def _as_str_keyed_dict(*, value: object) -> dict[str, Any] | None:
    """Return ``value`` as a ``str``-keyed dict, or ``None``.

    Uses a JSON round-trip so static checkers see concrete ``Any``
    values rather than unknown dict items from ``isinstance`` narrowing.
    """
    if not isinstance(value, dict):
        return None
    decoded: Any = json.loads(s=json.dumps(obj=value))
    typed: dict[str, Any] = decoded
    return typed


def _as_object_list(*, value: object) -> list[object] | None:
    """Return ``value`` as a list of objects, or ``None``."""
    if not isinstance(value, list):
        return None
    decoded: Any = json.loads(s=json.dumps(obj=value))
    typed: list[object] = decoded
    return typed


def normalize_openapi(*, spec: object) -> object:
    """Return a copy of ``spec`` suitable for semantic equality checks.

    Removes dynamic ``example`` / ``examples`` / ``x-examples`` values,
    normalizes date-time-looking ``default`` strings, and collapses
    whitespace in strings so live schema refreshes that only change
    sample timestamps or incidental spacing still compare equal.

    Args:
        spec: An OpenAPI / Swagger document or subtree.

    Returns:
        A structurally comparable copy of ``spec``.
    """
    as_dict = _as_str_keyed_dict(value=spec)
    if as_dict is not None:
        normalized: dict[str, object] = {}
        for key, value in as_dict.items():
            if key in _DYNAMIC_KEYS:
                continue
            if (
                key == "default"
                and isinstance(value, str)
                and _DATETIMEISH_RE.fullmatch(string=value)
            ):
                normalized[key] = "<datetime>"
                continue
            normalized[key] = normalize_openapi(spec=value)
        return normalized
    as_list = _as_object_list(value=spec)
    if as_list is not None:
        return [normalize_openapi(spec=item) for item in as_list]
    if isinstance(spec, str):
        return _WHITESPACE_RE.sub(repl=" ", string=spec).strip()
    return spec
