"""Helpers for retrying requests which are safe to repeat."""

import logging
from collections.abc import Iterator, Mapping
from http import HTTPStatus
from typing import Protocol, runtime_checkable

from beartype import beartype

_LOGGER = logging.getLogger(name="hackerrank")

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


@runtime_checkable
class _MultipartStream(Protocol):
    """A readable binary stream which can be rewound for a retry."""

    def read(self) -> bytes:
        """Read the remaining bytes from the stream."""
        ...  # pylint: disable=unnecessary-ellipsis

    def seek(self, offset: int, _whence: int, /) -> int:
        """Move to a byte offset in the stream."""
        ...  # pylint: disable=unnecessary-ellipsis

    def seekable(self) -> bool:
        """Return whether the stream supports seeking."""
        ...  # pylint: disable=unnecessary-ellipsis


type _MultipartContent = _MultipartStream | bytes | str
type _MultipartFile = (
    _MultipartContent
    | tuple[str | None, _MultipartContent]
    | tuple[str | None, _MultipartContent, str | None]
    | tuple[str | None, _MultipartContent, str | None, Mapping[str, str]]
)
type _MultipartFiles = Mapping[str, _MultipartFile] | None


@beartype
def _file_contents(*, files: _MultipartFiles) -> Iterator[_MultipartContent]:
    """Yield the content from each multipart ``files`` value.

    Args:
        files: Files to send as multipart form-data.

    Yields:
        Each bare value or the content element of each tuple value.
    """
    if files is None:
        return
    for value in files.values():
        if isinstance(value, _MultipartStream | bytes | str):
            yield value
        else:
            yield value[1]


@beartype
def _content_is_repeatable(*, content: _MultipartContent) -> bool:
    """Whether multipart file content can be sent more than once.

    Args:
        content: The content from a multipart ``files`` value.

    Returns:
        Whether sending ``content`` again would send the same bytes.
    """
    if isinstance(content, bytes | str):
        return True
    return content.seekable()


@beartype
def rewind_files(*, files: _MultipartFiles) -> bool:
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
    contents = list(_file_contents(files=files))
    if not all(
        _content_is_repeatable(content=content) for content in contents
    ):
        return False
    for content in contents:
        if not isinstance(content, bytes | str):
            _ = content.seek(0, 0)
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
    return BACKOFF_BASE_SECONDS * 2.0 ** (attempt - 1)


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
