"""Helpers for comparing OpenAPI documents semantically."""

from __future__ import annotations

import re
from typing import TypeGuard

from beartype.door import TypeHint

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


def _is_str_keyed_dict(
    value: object,
    /,
) -> TypeGuard[dict[str, object]]:
    """Return whether ``value`` is a string-keyed dictionary."""
    return TypeHint(hint=dict[str, object]).is_bearable(obj=value)


def _is_object_list(value: object, /) -> TypeGuard[list[object]]:
    """Return whether ``value`` is a list."""
    return isinstance(value, list)


def normalize_openapi(*, spec: object) -> object:
    """Return a copy of ``spec`` suitable for semantic equality checks.

    Removes dynamic ``example`` / ``examples`` / ``x-examples`` values,
    normalizes date-time-looking ``default`` strings, and collapses
    blank runs in strings so live schema refreshes that only change
    sample timestamps or incidental spacing still compare equal.

    Args:
        spec: An OpenAPI / Swagger document or nested fragment.

    Returns:
        A structurally comparable copy of ``spec``.
    """
    if _is_str_keyed_dict(spec):
        normalized: dict[str, object] = {}
        for key, value in spec.items():
            if key in _DYNAMIC_KEYS:
                continue
            if bool(
                key == "default"
                and isinstance(value, str)
                and _DATETIMEISH_RE.fullmatch(string=value)
            ):
                normalized[key] = "<datetime>"
                continue
            normalized[key] = normalize_openapi(spec=value)
        return normalized
    if _is_object_list(spec):
        return [normalize_openapi(spec=item) for item in spec]
    if isinstance(spec, str):
        return _WHITESPACE_RE.sub(repl=" ", string=spec).strip()
    return spec
