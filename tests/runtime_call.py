"""Invoke the public API with intentionally invalid inputs in tests."""

from collections.abc import Callable


def call_with_unchecked_arguments[Result](
    method: Callable[..., Result], /, **arguments: object
) -> Result:
    """Pass raw arguments through so the runtime API can validate them."""
    return method(**arguments)
