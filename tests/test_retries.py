"""Tests for the opt-in retry behaviour."""

import asyncio
import io
import logging
import time
from collections.abc import Iterator, Mapping, Sequence
from http import HTTPStatus
from pathlib import Path
from typing import override

import httpx
import httpx2
import pytest

from hackerrank._request_types import MultipartFiles
from hackerrank._retries import rewind_files
from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.exceptions import (
    HackerRankError,
    NotFoundError,
    RateLimitError,
    RedirectError,
)
from hackerrank.transports import TransportResponse
from hackerrank.types import JSONValue

_PAGE_BODY = (
    b'{"data": [], "page_total": 0, "offset": 0, "previous": "",'
    b' "next": "", "first": "", "last": "", "total": 0}'
)
_ZIP_BODY = b'{"file_url": "https://example.com/project.zip"}'


def _response(
    *,
    status_code: int,
    headers: dict[str, str],
    content: bytes,
) -> TransportResponse:
    """Build a transport response.

    Args:
        status_code: The HTTP status code.
        headers: The response headers.
        content: The response body.

    Returns:
        The transport response.
    """
    return TransportResponse(
        status_code=status_code,
        headers=headers,
        content=content,
    )


def _ok(*, content: bytes) -> TransportResponse:
    """Build a ``200 OK`` transport response.

    Args:
        content: The response body.

    Returns:
        The transport response.
    """
    return _response(status_code=200, headers={}, content=content)


def _error(*, status_code: int) -> TransportResponse:
    """Build an error transport response with no headers.

    Args:
        status_code: The HTTP status code.

    Returns:
        The transport response.
    """
    return _response(status_code=status_code, headers={}, content=b"{}")


def _file_parts(*, files: MultipartFiles) -> Iterator[object]:
    """Yield each part of a multipart ``files`` mapping.

    The client only ever sends the ``(filename, file, content_type)``
    tuple which ``httpx`` expects, so that is all this handles.

    Args:
        files: Files sent as multipart form-data.

    Yields:
        Each element of each value.
    """
    if files is None:
        return
    for value in files.values():
        yield from value


class _ScriptedCalls:
    """Shared recording and scripting for the test transports.

    The last entry of the script is repeated for any further calls,
    so a script of one item describes an endpoint which always
    behaves the same way.
    """

    def __init__(
        self,
        *,
        script: Sequence[TransportResponse | Exception],
    ) -> None:
        """Create a scripted transport.

        Args:
            script: The results to return or raise, in order.
        """
        self._script = list(script)
        self.methods: list[str] = []
        self.urls: list[str] = []
        self.file_contents: list[bytes] = []

    def _next(
        self,
        *,
        method: str,
        url: str,
        files: MultipartFiles,
    ) -> TransportResponse:
        """Record a call and return its scripted result.

        Args:
            method: The HTTP method.
            url: The full URL.
            files: Files to send as multipart form-data.

        Returns:
            The scripted response.

        Raises:
            Exception: Whatever the script says to raise.
        """
        index = min(len(self.methods), len(self._script) - 1)
        self.methods.append(method)
        self.urls.append(url)
        for part in _file_parts(files=files):
            if isinstance(part, io.IOBase):
                self.file_contents.append(part.read())
            elif isinstance(part, bytes):
                self.file_contents.append(part)
        result = self._script[index]
        if isinstance(result, Exception):
            raise result
        return result


class _ScriptedTransport(_ScriptedCalls):
    """A transport which replays a script of results, in order."""

    def __call__(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        params: dict[str, str | int] | None,
        json: Mapping[str, JSONValue] | None,
        files: MultipartFiles,
    ) -> TransportResponse:
        """Make a scripted request.

        Args:
            method: The HTTP method.
            url: The full URL.
            headers: Request headers.
            params: Query parameters.
            json: A JSON-serialisable body.
            files: Files to send as multipart form-data.

        Returns:
            The scripted response.
        """
        del headers, params, json
        return self._next(method=method, url=url, files=files)


class _AsyncScriptedTransport(_ScriptedCalls):
    """The async counterpart of ``_ScriptedTransport``."""

    async def __call__(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        params: dict[str, str | int] | None,
        json: Mapping[str, JSONValue] | None,
        files: MultipartFiles,
    ) -> TransportResponse:
        """Make a scripted async request.

        Args:
            method: The HTTP method.
            url: The full URL.
            headers: Request headers.
            params: Query parameters.
            json: A JSON-serialisable body.
            files: Files to send as multipart form-data.

        Returns:
            The scripted response.
        """
        del headers, params, json
        return self._next(method=method, url=url, files=files)


def _create_question(*, client: HackerRank) -> None:
    """Create a question, which is never safe to repeat.

    Args:
        client: The client to create the question with.
    """
    _ = client.questions.create(
        name="Q",
        type="code",
        problem_statement="Do the thing.",
        recommended_duration=10,
    )


@pytest.fixture(name="sleeps", autouse=True)
def fixture_sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record, rather than perform, the delays between attempts.

    This is autouse so that no test ever really waits.

    Args:
        monkeypatch: The pytest monkeypatch fixture.

    Returns:
        The recorded delays, in the order they were requested.
    """
    recorded: list[float] = []
    monkeypatch.setattr(target=time, name="sleep", value=recorded.append)

    async def _record(delay: float) -> None:
        """Record an awaited delay without waiting.

        Args:
            delay: The number of seconds which would be slept.
        """
        recorded.append(delay)

    monkeypatch.setattr(target=asyncio, name="sleep", value=_record)
    return recorded


# Tests that nothing is retried unless retries are asked for.


def test_retries_are_opt_in_default_makes_one_attempt() -> None:
    """By default a failing request is not retried."""
    transport = _ScriptedTransport(
        script=[
            _error(status_code=HTTPStatus.SERVICE_UNAVAILABLE),
            _ok(content=_PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport)
    with pytest.raises(expected_exception=HackerRankError):
        _ = client.tests.list()
    assert transport.methods == ["GET"]


def test_retries_are_used_when_asked_for() -> None:
    """A repeatable request is retried until it succeeds."""
    transport = _ScriptedTransport(
        script=[
            _error(status_code=HTTPStatus.SERVICE_UNAVAILABLE),
            _error(status_code=HTTPStatus.BAD_GATEWAY),
            _ok(content=_PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=2)
    assert client.tests.list().total == 0
    assert transport.methods == ["GET", "GET", "GET"]


def test_retries_are_exhausted(sleeps: list[float]) -> None:
    """The last failure is raised once the retries run out.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _ScriptedTransport(
        script=[_error(status_code=HTTPStatus.SERVICE_UNAVAILABLE)],
    )
    client = HackerRank(api_key="key", transport=transport, retries=2)
    with pytest.raises(expected_exception=HackerRankError):
        _ = client.tests.list()
    assert transport.methods == ["GET", "GET", "GET"]
    assert sleeps == [0.5, 1.0]


# Tests for per-endpoint knowledge of what is safe to repeat.


def test_which_requests_are_repeated_create_is_not_repeated(
    sleeps: list[float],
) -> None:
    """A create is sent once, because the write may have landed.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _ScriptedTransport(
        script=[_error(status_code=HTTPStatus.GATEWAY_TIMEOUT)],
    )
    client = HackerRank(api_key="key", transport=transport, retries=5)
    with pytest.raises(expected_exception=HackerRankError):
        _create_question(client=client)
    assert transport.methods == ["POST"]
    assert sleeps == []


def test_upsert_post_is_repeated() -> None:
    """A ``POST`` which replaces state is repeated."""
    transport = _ScriptedTransport(
        script=[
            _error(status_code=HTTPStatus.BAD_GATEWAY),
            _ok(content=b"{}"),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    client.interview_templates.explicit_sharing_roles.update_access(
        template_id=1,
        explicit_roles=[{"rollable_type": "company"}],
    )
    assert transport.methods == ["POST", "POST"]
    assert transport.urls[0].endswith("/update_access")


@pytest.mark.parametrize(
    argnames=("status_code", "expected_error"),
    argvalues=[
        (HTTPStatus.NOT_FOUND, NotFoundError),
        (HTTPStatus.BAD_REQUEST, HackerRankError),
        (HTTPStatus.MOVED_PERMANENTLY, RedirectError),
    ],
)
def test_which_requests_are_repeated_non_transient_status_is_not_repeated(
    status_code: HTTPStatus,
    expected_error: type[HackerRankError],
    sleeps: list[float],
) -> None:
    """A response which a retry cannot fix is raised at once.

    Args:
        status_code: The status code to respond with.
        expected_error: The error the response must raise.
        sleeps: The recorded delays between attempts.
    """
    transport = _ScriptedTransport(
        script=[_error(status_code=status_code)],
    )
    client = HackerRank(api_key="key", transport=transport, retries=3)
    with pytest.raises(expected_exception=expected_error):
        _ = client.tests.list()
    assert transport.methods == ["GET"]
    assert sleeps == []


# Tests for retrying errors raised before any response arrives.


def test_transport_errors_transport_error_is_retried(
    sleeps: list[float],
) -> None:
    """A transport error on a repeatable request is retried.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _ScriptedTransport(
        script=[
            httpx.ReadTimeout(message="The read operation timed out"),
            _ok(content=_PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    assert client.tests.list().total == 0
    assert transport.methods == ["GET", "GET"]
    assert sleeps == [0.5]


def test_transport_error_is_raised_when_retries_run_out() -> None:
    """The transport error is raised once the retries run out."""
    transport = _ScriptedTransport(
        script=[httpx.ConnectError(message="Connection refused")],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    with pytest.raises(expected_exception=httpx.ConnectError):
        _ = client.tests.list()
    assert transport.methods == ["GET", "GET"]


def test_transport_error_on_a_create_is_not_retried(
    sleeps: list[float],
) -> None:
    """A create which times out is not sent again.

    This is the case the retry policy exists to get right. The
    write may well have landed, so a second attempt would create
    a duplicate question which the API cannot delete.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _ScriptedTransport(
        script=[httpx.ReadTimeout(message="The read operation timed out")],
    )
    client = HackerRank(api_key="key", transport=transport, retries=5)
    with pytest.raises(expected_exception=httpx.ReadTimeout):
        _create_question(client=client)
    assert transport.methods == ["POST"]
    assert sleeps == []


def test_transport_errors_httpx2_transport_error_is_retried(
    sleeps: list[float],
) -> None:
    """A native HTTPX2 transport error is retried.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _ScriptedTransport(
        script=[
            httpx2.ReadTimeout(message="The read operation timed out"),
            _ok(content=_PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    assert client.tests.list().total == 0
    assert transport.methods == ["GET", "GET"]
    assert sleeps == [0.5]


# Tests for how long the client waits between attempts.


def test_backoff_is_exponential(sleeps: list[float]) -> None:
    """Each delay is twice the one before it.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _ScriptedTransport(
        script=[_error(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)],
    )
    client = HackerRank(api_key="key", transport=transport, retries=4)
    with pytest.raises(expected_exception=HackerRankError):
        _ = client.tests.list()
    assert sleeps == [0.5, 1.0, 2.0, 4.0]


def test_retry_after_is_honoured(sleeps: list[float]) -> None:
    """A ``Retry-After`` header replaces the backoff.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _ScriptedTransport(
        script=[
            _response(
                status_code=HTTPStatus.TOO_MANY_REQUESTS,
                headers={"Retry-After": "7"},
                content=b"{}",
            ),
            _ok(content=_PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    assert client.tests.list().total == 0
    assert sleeps == [7.0]


def test_http_date_retry_after_falls_back_to_backoff(
    sleeps: list[float],
) -> None:
    """An unparsable ``Retry-After`` is ignored, not misread.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _ScriptedTransport(
        script=[
            _response(
                status_code=HTTPStatus.TOO_MANY_REQUESTS,
                headers={"retry-after": "Wed, 21 Oct 2015 07:28:00 GMT"},
                content=b"{}",
            ),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    with pytest.raises(expected_exception=RateLimitError):
        _ = client.tests.list()
    assert sleeps == [0.5]


def test_negative_retry_after_does_not_go_backwards(
    sleeps: list[float],
) -> None:
    """A negative ``Retry-After`` waits no time at all.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _ScriptedTransport(
        script=[
            _response(
                status_code=HTTPStatus.TOO_MANY_REQUESTS,
                headers={"Retry-After": "-5"},
                content=b"{}",
            ),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    with pytest.raises(expected_exception=RateLimitError):
        _ = client.tests.list()
    assert sleeps == [0.0]


# Tests that a repeated upload sends the file again, not nothing.


def test_uploads_file_object_is_rewound_between_attempts(
    tmp_path: Path,
) -> None:
    """The zip is sent in full on every attempt.

    Args:
        tmp_path: A temporary directory to hold the zip.
    """
    transport = _ScriptedTransport(
        script=[
            _error(status_code=HTTPStatus.BAD_GATEWAY),
            _ok(content=_ZIP_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    zip_path = tmp_path / "project.zip"
    _ = zip_path.write_bytes(data=b"zip-bytes")
    with zip_path.open(mode="rb") as handle:
        _ = client.questions.upload_project_zip(
            question_id="q1",
            file=handle,
        )
    assert transport.file_contents == [b"zip-bytes", b"zip-bytes"]


def test_bytes_are_sent_again() -> None:
    """A zip given as bytes is repeatable without rewinding."""
    transport = _ScriptedTransport(
        script=[
            _error(status_code=HTTPStatus.BAD_GATEWAY),
            _ok(content=_ZIP_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    _ = client.questions.upload_project_zip(question_id="q1", file=b"zip")
    assert transport.file_contents == [b"zip", b"zip"]


# Tests for deciding whether a multipart body can be sent again.


def test_no_files() -> None:
    """A request with no files is always repeatable."""
    assert rewind_files(files=None)
    assert rewind_files(files={})


def test_bytes() -> None:
    """Byte content needs no rewinding."""
    assert rewind_files(
        files={
            "bytes": (
                "data.bin",
                b"data",
                "application/octet-stream",
            )
        }
    )


def test_seekable_file_is_rewound(tmp_path: Path) -> None:
    """A seekable file is returned to its start.

    Args:
        tmp_path: A temporary directory to hold the file.
    """
    path = tmp_path / "project.zip"
    _ = path.write_bytes(data=b"data")
    with path.open(mode="rb") as handle:
        assert handle.read() == b"data"
        files = {"file": ("p.zip", handle, "application/zip")}
        assert rewind_files(files=files)
        assert handle.read() == b"data"


def test_unseekable_file_is_refused(tmp_path: Path) -> None:
    """An unseekable file makes the request unrepeatable."""

    class _Unseekable(io.FileIO):
        """A stream which cannot be rewound."""

        @override
        def seekable(self) -> bool:
            """Report as unseekable.

            Returns:
                Always ``False``.
            """
            return False

    path = tmp_path / "project.zip"
    _ = path.write_bytes(data=b"data")
    with _Unseekable(file=path, mode="rb") as handle:
        assert not rewind_files(
            files={"file": ("project.zip", handle, "application/zip")}
        )


# Tests that a retry is visible to the caller.


def test_retry_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    """Each retry is logged with what went wrong.

    Args:
        caplog: The pytest log capture fixture.
    """
    transport = _ScriptedTransport(
        script=[
            _error(status_code=HTTPStatus.BAD_GATEWAY),
            _ok(content=_PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    with caplog.at_level(level=logging.WARNING, logger="hackerrank"):
        _ = client.tests.list()
    (record,) = caplog.records
    assert "HTTP 502" in record.getMessage()
    assert "in 0.5 seconds" in record.getMessage()


def test_transport_error_retry_names_the_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A retried transport error is named in the log.

    Args:
        caplog: The pytest log capture fixture.
    """
    transport = _ScriptedTransport(
        script=[
            httpx.ReadTimeout(message="The read operation timed out"),
            _ok(content=_PAGE_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    with caplog.at_level(level=logging.WARNING, logger="hackerrank"):
        _ = client.tests.list()
    (record,) = caplog.records
    assert "ReadTimeout" in record.getMessage()


# Tests that the async client behaves the same way.


@pytest.mark.asyncio
async def test_async_retries_non_transient_status_is_not_repeated() -> None:
    """An async request error which cannot improve is raised once."""
    transport = _AsyncScriptedTransport(
        script=[_error(status_code=HTTPStatus.BAD_REQUEST)],
    )
    client = AsyncHackerRank(
        api_key="key",
        transport=transport,
        retries=3,
    )
    with pytest.raises(expected_exception=HackerRankError):
        await client.tests.list()
    assert transport.methods == ["GET"]


@pytest.mark.asyncio
async def test_repeatable_request_is_retried(
    sleeps: list[float],
) -> None:
    """A repeatable async request is retried until it succeeds.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _AsyncScriptedTransport(
        script=[
            _error(status_code=HTTPStatus.SERVICE_UNAVAILABLE),
            _ok(content=_PAGE_BODY),
        ],
    )
    client = AsyncHackerRank(
        api_key="key",
        transport=transport,
        retries=1,
    )
    result = await client.tests.list()
    assert result.total == 0
    assert transport.methods == ["GET", "GET"]
    assert sleeps == [0.5]


@pytest.mark.asyncio
async def test_async_retries_transport_error_is_retried(
    sleeps: list[float],
) -> None:
    """An async transport error on a repeatable request is retried.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _AsyncScriptedTransport(
        script=[
            httpx.ReadTimeout(message="The read operation timed out"),
            _ok(content=_PAGE_BODY),
        ],
    )
    client = AsyncHackerRank(
        api_key="key",
        transport=transport,
        retries=1,
    )
    result = await client.tests.list()
    assert result.total == 0
    assert transport.methods == ["GET", "GET"]
    assert sleeps == [0.5]


@pytest.mark.asyncio
async def test_async_retries_httpx2_transport_error_is_retried(
    sleeps: list[float],
) -> None:
    """A native async HTTPX2 transport error is retried.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _AsyncScriptedTransport(
        script=[
            httpx2.ReadTimeout(message="The read operation timed out"),
            _ok(content=_PAGE_BODY),
        ],
    )
    client = AsyncHackerRank(
        api_key="key",
        transport=transport,
        retries=1,
    )
    result = await client.tests.list()
    assert result.total == 0
    assert transport.methods == ["GET", "GET"]
    assert sleeps == [0.5]


@pytest.mark.asyncio
async def test_async_retries_default_makes_one_attempt() -> None:
    """By default a failing async request is not retried."""
    transport = _AsyncScriptedTransport(
        script=[_error(status_code=HTTPStatus.SERVICE_UNAVAILABLE)],
    )
    client = AsyncHackerRank(api_key="key", transport=transport)
    with pytest.raises(expected_exception=HackerRankError):
        await client.tests.list()
    assert transport.methods == ["GET"]


@pytest.mark.asyncio
async def test_async_retries_create_is_not_repeated() -> None:
    """An async create is sent once, however many retries."""
    transport = _AsyncScriptedTransport(
        script=[httpx.ReadTimeout(message="The read operation timed out")],
    )
    client = AsyncHackerRank(
        api_key="key",
        transport=transport,
        retries=5,
    )
    with pytest.raises(expected_exception=httpx.ReadTimeout):
        await client.questions.create(
            name="Q",
            type="code",
            problem_statement="Do the thing.",
            recommended_duration=10,
        )
    assert transport.methods == ["POST"]


@pytest.mark.asyncio
async def test_async_retries_file_object_is_rewound_between_attempts(
    tmp_path: Path,
) -> None:
    """The async upload sends the zip in full on every attempt.

    Args:
        tmp_path: A temporary directory to hold the zip.
    """
    transport = _AsyncScriptedTransport(
        script=[
            _error(status_code=HTTPStatus.BAD_GATEWAY),
            _ok(content=_ZIP_BODY),
        ],
    )
    client = AsyncHackerRank(
        api_key="key",
        transport=transport,
        retries=1,
    )
    zip_path = tmp_path / "project.zip"
    _ = zip_path.write_bytes(data=b"zip-bytes")
    with zip_path.open(mode="rb") as handle:
        await client.questions.upload_project_zip(
            question_id="q1",
            file=handle,
        )
    assert transport.file_contents == [b"zip-bytes", b"zip-bytes"]
