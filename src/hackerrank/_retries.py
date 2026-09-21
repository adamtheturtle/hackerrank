"""Helpers for retrying requests which are safe to repeat."""

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable, Iterator, Mapping
from http import HTTPStatus
from typing import Protocol

import httpx
import httpx2
from beartype import beartype
from tenacity import (
    RetryCallState,
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exception,
)

from hackerrank._request_types import MultipartContent, MultipartFiles
from hackerrank.exceptions import HackerRankError
from hackerrank.transports import TransportResponse

_LOGGER = logging.getLogger(name="hackerrank")


class _RetryLogger:
    """Adapt the standard logger to Tenacity's narrower protocol."""

    @staticmethod
    def log(
        level: int,
        message: str,
        /,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Write Tenacity's already-formatted retry message."""
        del args, kwargs
        _LOGGER.log(level, message)


_log_before_sleep = before_sleep_log(
    logger=_RetryLogger(),
    log_level=logging.WARNING,
)

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


class _SeekableStream(Protocol):
    """The file operations needed to make an upload repeatable."""

    def seek(self, offset: int, _whence: int, /) -> int:
        """Move to a byte offset in the stream."""
        ...  # pylint: disable=unnecessary-ellipsis

    def seekable(self) -> bool:
        """Return whether the stream supports seeking."""
        ...  # pylint: disable=unnecessary-ellipsis


type Request = Callable[[], TransportResponse]
type AsyncRequest = Callable[[], Awaitable[TransportResponse]]

_TRANSPORT_ERRORS = (httpx.TransportError, httpx2.TransportError)


@beartype
def _is_retryable(exception: BaseException) -> bool:
    """Return whether an exception represents a transient failure."""
    if isinstance(exception, _TRANSPORT_ERRORS):
        return True
    return (
        isinstance(exception, HackerRankError)
        and exception.status_code in RETRY_STATUS_CODES
    )


@beartype
def _file_contents(*, files: MultipartFiles) -> Iterator[MultipartContent]:
    """Yield the content from each multipart ``files`` value.

    Args:
        files: Files to send as multipart form-data.

    Yields:
        Each bare value or the content element of each tuple value.
    """
    if files is None:
        return
    for value in files.values():
        yield value[1]


@beartype
def _content_is_repeatable(*, content: MultipartContent) -> bool:
    """Whether multipart file content can be sent more than once.

    Args:
        content: The content from a multipart ``files`` value.

    Returns:
        Whether sending ``content`` again would send the same bytes.
    """
    if isinstance(content, bytes):
        return True
    stream: _SeekableStream = content
    return stream.seekable()


@beartype
def rewind_files(*, files: MultipartFiles) -> bool:
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
        if not isinstance(content, bytes):
            stream: _SeekableStream = content
            _ = stream.seek(0, 0)
    return True


@beartype
def _files_are_repeatable(*, files: MultipartFiles) -> bool:
    """Return whether every multipart file can be repeated.

    Unlike :func:`rewind_files`, this check does not move any stream.

    Args:
        files: Files to send as multipart form-data.

    Returns:
        Whether every file can be sent again.
    """
    return all(
        _content_is_repeatable(content=content)
        for content in _file_contents(files=files)
    )


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

    pre: attempt >= 1
    post[]:
        _ >= 0.0
        bool(headers) or _ == 2.0 ** (attempt - 2)

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
def _wait_seconds(*, attempt: int, exception: BaseException) -> float:
    """Return the delay before Tenacity's next attempt.

    Args:
        attempt: The number of the attempt which just failed.
        exception: The transient exception from that attempt.

    Returns:
        The delay in seconds.
    """
    headers = (
        exception.response.headers
        if isinstance(exception, HackerRankError)
        else None
    )
    return delay_seconds(attempt=attempt, headers=headers)


@beartype
def _before_sleep(
    *,
    retry_state: RetryCallState,
    files: MultipartFiles,
) -> None:
    """Rewind uploads and use Tenacity's standard retry logging.

    Args:
        retry_state: Tenacity's state after the failed attempt.
        files: Multipart files to rewind.
    """
    _ = rewind_files(files=files)
    _log_before_sleep(retry_state)


@beartype
def _attempts(*, retries: int, repeatable: bool, files: MultipartFiles) -> int:
    """Return the number of request attempts which are safe to make.

    Args:
        retries: The number of retries requested by the caller.
        repeatable: Whether repeating the API operation is safe.
        files: Multipart files which may need to be sent again.

    Returns:
        One attempt for an unsafe operation or body, otherwise one plus the
        requested number of retries.
    """
    if not repeatable or not _files_are_repeatable(files=files):
        return 1
    return max(1, 1 + retries)


@beartype
def request_with_retries(
    *,
    request: Request,
    retries: int,
    repeatable: bool,
    files: MultipartFiles,
) -> TransportResponse:
    """Run a synchronous request under the shared retry policy.

    Args:
        request: The zero-argument request operation.
        retries: The number of retries requested by the caller.
        repeatable: Whether repeating the API operation is safe.
        files: Multipart files which may need to be sent again.

    Returns:
        The successful response.
    """
    attempts = _attempts(
        retries=retries,
        repeatable=repeatable,
        files=files,
    )
    attempt = 0

    def _wait(exception: BaseException) -> float:
        """Calculate the delay after the current attempt."""
        return _wait_seconds(attempt=attempt, exception=exception)

    @retry(
        sleep=time.sleep,
        stop=stop_after_attempt(max_attempt_number=attempts),
        wait=wait_exception(predicate=_wait),
        retry=retry_if_exception(predicate=_is_retryable),
        before_sleep=lambda state: _before_sleep(
            retry_state=state,
            files=files,
        ),
        reraise=True,
    )
    def _send() -> TransportResponse:
        """Send once, representing a transient response as an error."""
        nonlocal attempt
        attempt += 1
        response = request()
        if response.status_code >= HTTPStatus.MULTIPLE_CHOICES:
            raise HackerRankError.from_response(response=response)
        return response

    return _send()


@beartype
async def async_request_with_retries(
    *,
    request: AsyncRequest,
    retries: int,
    repeatable: bool,
    files: MultipartFiles,
) -> TransportResponse:
    """Run an asynchronous request under the shared retry policy.

    Args:
        request: The zero-argument async request operation.
        retries: The number of retries requested by the caller.
        repeatable: Whether repeating the API operation is safe.
        files: Multipart files which may need to be sent again.

    Returns:
        The successful response.
    """
    attempts = _attempts(
        retries=retries,
        repeatable=repeatable,
        files=files,
    )
    attempt = 0

    def _wait(exception: BaseException) -> float:
        """Calculate the delay after the current attempt."""
        return _wait_seconds(attempt=attempt, exception=exception)

    @retry(
        sleep=asyncio.sleep,
        stop=stop_after_attempt(max_attempt_number=attempts),
        wait=wait_exception(predicate=_wait),
        retry=retry_if_exception(predicate=_is_retryable),
        before_sleep=lambda state: _before_sleep(
            retry_state=state,
            files=files,
        ),
        reraise=True,
    )
    async def _send() -> TransportResponse:
        """Send once, representing a transient response as an error."""
        nonlocal attempt
        attempt += 1
        response = await request()
        if response.status_code >= HTTPStatus.MULTIPLE_CHOICES:
            raise HackerRankError.from_response(response=response)
        return response

    return await _send()
