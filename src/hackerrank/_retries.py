"""Helpers for retrying requests which are safe to repeat."""

import io
import logging
from collections.abc import Iterator, Mapping
from http import HTTPStatus
from typing import Any

from beartype import beartype

_LOGGER = logging.getLogger("hackerrank")

BACKOFF_BASE_SECONDS = 0.5
"""The delay before the first retry, doubled for each retry after it."""

RETRY_STATUS_CODES = frozenset(
    {
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    },
)
"""Status codes which are worth another attempt.

Every other ``4xx`` describes a problem with the request itself,
which a second identical request would hit again.
"""


@beartype
def _file_parts(*, files: Mapping[str, Any] | None) -> Iterator[Any]:
    """Yield each part of a multipart ``files`` mapping.

    Args:
        files: Files to send as multipart form-data.

    Yields:
        Each value, and each element of each tuple value.
    """
    for value in (files or {}).values():
        if isinstance(value, tuple):
            yield from value
        else:
            yield value


@beartype
def _part_is_repeatable(*, part: Any) -> bool:  # noqa: ANN401
    """Whether a single multipart part can be sent more than once.

    Args:
        part: One part of a multipart ``files`` mapping.

    Returns:
        Whether sending ``part`` again would send the same bytes.
    """
    if part is None or isinstance(part, bytes | bytearray | memoryview | str):
        return True
    return isinstance(part, io.IOBase) and part.seekable()


@beartype
def rewind_files(*, files: Mapping[str, Any] | None) -> bool:
    """Rewind the file objects in ``files`` ready for another attempt.

    A file object which has already been read is at its end, so a
    second attempt would send nothing at all. Rewinding is only
    possible for seekable files.

    Args:
        files: Files to send as multipart form-data.

    Returns:
        Whether every part of ``files`` can be sent again. When this
        is ``False`` nothing is rewound and the request must not be
        repeated.
    """
    parts = list(_file_parts(files=files))
    if not all(_part_is_repeatable(part=part) for part in parts):
        return False
    for part in parts:
        if isinstance(part, io.IOBase):
            part.seek(0)
    return True


@beartype
def _retry_after_seconds(*, headers: Mapping[str, str]) -> float | None:
    """Read a delay from a ``Retry-After`` header.

    Only the delay-seconds form is understood. The HTTP-date form
    falls back to the usual backoff rather than being misread as a
    number.

    Args:
        headers: The response headers.

    Returns:
        The number of seconds to wait, or ``None`` if the header is
        absent or is not a number of seconds.
    """
    lowered = {key.lower(): value for key, value in headers.items()}
    value = lowered.get("retry-after")
    if value is None:
        return None
    try:
        seconds = float(value)
    except ValueError:
        return None
    return max(seconds, 0.0)


@beartype
def delay_seconds(*, attempt: int, headers: Mapping[str, str] | None) -> float:
    """The delay before the next attempt.

    Args:
        attempt: The number of the attempt which just failed,
            counting from ``1``.
        headers: The headers of the response which failed, or
            ``None`` if there was no response.

    Returns:
        The number of seconds to wait, taking ``Retry-After`` over
        the exponential backoff when the server sent one.
    """
    if headers is not None:
        retry_after = _retry_after_seconds(headers=headers)
        if retry_after is not None:
            return retry_after
    return BACKOFF_BASE_SECONDS * 2 ** (attempt - 1)


@beartype
def log_retry(
    *,
    method: str,
    url: str,
    attempt: int,
    attempts: int,
    delay: float,
    reason: str,
) -> None:
    """Log that a request is about to be retried.

    Args:
        method: The HTTP method.
        url: The full URL.
        attempt: The number of the attempt which just failed,
            counting from ``1``.
        attempts: The total number of attempts which will be made.
        delay: The number of seconds before the next attempt.
        reason: What went wrong.
    """
    _LOGGER.warning(
        "Retrying %s %s in %.1fs after %s (attempt %d of %d).",
        method,
        url,
        delay,
        reason,
        attempt,
        attempts,
    )
