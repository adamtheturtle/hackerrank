"""Question writes and upload verification use real HTTP transports."""

from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from http import HTTPStatus
from io import BytesIO, FileIO
from pathlib import Path
from typing import BinaryIO, override
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

import httpx
import httpx2
import pytest
import respx

from hackerrank._question_requests import project_upload_context
from hackerrank._request_urls import question_write_url
from hackerrank.api import prepare_operation
from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.transports import (
    AsyncHTTPX2Transport,
    AsyncHTTPXTransport,
    HTTPX2Transport,
    HTTPXTransport,
)
from hackerrank.types import JSONValue

_QUESTION_URL = "https://www.hackerrank.com/x/api/v3/questions/q1"
_UPLOAD_URL = _QUESTION_URL + "/upload_project_zip/"
_DOWNLOAD_URL = "https://files.example/project.zip?signature=private"
_METADATA = {"file_url": _DOWNLOAD_URL, "file_path": "projects/q1.zip"}
_TIMEOUT_SECONDS = 7
_PROJECT_TIMEOUT_SECONDS = 3
_ENTRIES = [("solution.py", b"pass\n"), ("nested/binary", bytes(range(256)))]


def _zip(*, entries: list[tuple[str, bytes]], compression: int) -> bytes:
    """Prepare an archive with independently selected ZIP metadata."""
    with BytesIO() as buffer:
        with ZipFile(
            file=buffer, mode="w", compression=compression
        ) as archive:
            for name, contents in entries:
                archive.writestr(zinfo_or_arcname=name, data=contents)
        return buffer.getvalue()


_ARCHIVE = _zip(entries=_ENTRIES, compression=ZIP_STORED)
_STORED = _zip(entries=list(reversed(_ENTRIES)), compression=ZIP_DEFLATED)


@dataclass(frozen=True, kw_only=True)
class _Mode:
    """Choose a public client and its HTTP transport family."""

    asynchronous: bool
    httpx2: bool


@dataclass(frozen=True, kw_only=True)
class _Connection:
    """Keep request recording next to the selected public client."""

    mode: _Mode
    router: respx.Router


@pytest.fixture(
    name="connection",
    params=[
        _Mode(asynchronous=False, httpx2=False),
        _Mode(asynchronous=True, httpx2=False),
        _Mode(asynchronous=False, httpx2=True),
        _Mode(asynchronous=True, httpx2=True),
    ],
    ids=["sync-httpx", "async-httpx", "sync-httpx2", "async-httpx2"],
)
def fixture_connection(
    request: pytest.FixtureRequest,
    respx_mock: respx.MockRouter,
    httpx2_mock: respx.Router,
) -> _Connection:
    """Use each family's HTTP interception with the real client
    methods.
    """
    mode = request.param
    assert isinstance(mode, _Mode)
    return _Connection(
        mode=mode, router=httpx2_mock if mode.httpx2 else respx_mock
    )


@asynccontextmanager
async def _client(
    *, connection: _Connection, retries: int
) -> AsyncGenerator[HackerRank | AsyncHackerRank]:
    """Construct and close a client using the selected HTTP transport."""
    if connection.mode.asynchronous:
        transport = (
            AsyncHTTPX2Transport(
                timeout=_TIMEOUT_SECONDS,
                project_upload_timeout=_PROJECT_TIMEOUT_SECONDS,
            )
            if connection.mode.httpx2
            else AsyncHTTPXTransport(
                timeout=_TIMEOUT_SECONDS,
                project_upload_timeout=_PROJECT_TIMEOUT_SECONDS,
            )
        )
        async with (
            transport,
            AsyncHackerRank(
                api_key="secret", transport=transport, retries=retries
            ) as client,
        ):
            yield client
        return
    sync_transport = (
        HTTPX2Transport(
            timeout=_TIMEOUT_SECONDS,
            project_upload_timeout=_PROJECT_TIMEOUT_SECONDS,
        )
        if connection.mode.httpx2
        else HTTPXTransport(
            timeout=_TIMEOUT_SECONDS,
            project_upload_timeout=_PROJECT_TIMEOUT_SECONDS,
        )
    )
    with (
        sync_transport,
        HackerRank(
            api_key="secret", transport=sync_transport, retries=retries
        ) as sync_client,
    ):
        yield sync_client


async def _upload(
    *, connection: _Connection, archive: bytes | BinaryIO, retries: int
) -> dict[str, JSONValue]:
    """Exercise the public ZIP operation with the chosen transport."""
    async with _client(connection=connection, retries=retries) as client:
        if isinstance(client, AsyncHackerRank):
            return await client.questions.upload_project_zip(
                question_id="q1", file=archive
            )
        return client.questions.upload_project_zip(
            question_id="q1", file=archive
        )


def _timeout(
    *, connection: _Connection
) -> httpx.ReadTimeout | httpx2.ReadTimeout:
    """Raise the selected transport family's original upload failure."""
    kind = httpx2.ReadTimeout if connection.mode.httpx2 else httpx.ReadTimeout
    return kind(message="Original upload timeout")


@pytest.mark.parametrize(
    argnames=("method", "path", "expected"),
    argvalues=[
        ("POST", "/x/api/v3/questions", "/x/api/v3/questions/"),
        ("PUT", "/x/api/v3/questions/q1?x=1", "/x/api/v3/questions/q1/?x=1"),
        ("POST", "/x/api/v3/questions/", "/x/api/v3/questions/"),
        ("GET", "/x/api/v3/questions/q1", "/x/api/v3/questions/q1"),
        ("PUT", "/x/api/v3/questions_extra", "/x/api/v3/questions_extra"),
        (
            "PUT",
            "/x/api/v3/interview_templates/1",
            "/x/api/v3/interview_templates/1",
        ),
    ],
)
def test_canonical_question_paths(
    *, method: str, path: str, expected: str
) -> None:
    """Question writes are canonical and unrelated requests are
    preserved.
    """
    assert question_write_url(method=method, url=path) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="wrapped", argvalues=[False, True])
@pytest.mark.parametrize(argnames="stream", argvalues=[False, True])
async def test_verified_upload_is_not_repeated(
    *, connection: _Connection, wrapped: bool, stream: bool, tmp_path: Path
) -> None:
    """Stored file contents prove success despite a different ZIP encoding."""
    timeout = _timeout(connection=connection)
    post = connection.router.post(url=_UPLOAD_URL).mock(side_effect=timeout)
    get = connection.router.get(url=_QUESTION_URL).respond(
        status_code=HTTPStatus.OK,
        json={"data": _METADATA} if wrapped else _METADATA,
    )
    download = connection.router.get(url=_DOWNLOAD_URL).respond(
        status_code=HTTPStatus.OK, content=_STORED
    )
    archive_path = tmp_path / "project.zip"
    _ = archive_path.write_bytes(data=_ARCHIVE)
    with archive_path.open(mode="rb") as handle:
        supplied = handle if stream else _ARCHIVE
        result = await _upload(
            connection=connection, archive=supplied, retries=2
        )
        if stream:
            assert handle.tell() == len(_ARCHIVE)
    assert result == _METADATA
    assert post.call_count == 1
    assert get.call_count == 1
    assert download.call_count == 1
    assert get.calls.last.request.headers["Authorization"] == "Bearer secret"
    assert "Authorization" not in download.calls.last.request.headers
    assert (
        post.calls.last.request.extensions["timeout"]["read"]
        == _PROJECT_TIMEOUT_SECONDS
    )
    assert (
        get.calls.last.request.extensions["timeout"]["read"]
        == _TIMEOUT_SECONDS
    )
    assert (
        download.calls.last.request.extensions["timeout"]["read"]
        == _TIMEOUT_SECONDS
    )
    assert _ARCHIVE != _STORED


def _duplicate_archive() -> bytes:
    """Build deliberately ambiguous ZIP input for verification checks."""
    with pytest.warns(expected_warning=UserWarning, match="Duplicate name"):
        return _zip(entries=[*_ENTRIES, _ENTRIES[0]], compression=ZIP_STORED)


_DUPLICATE_ARCHIVE = _duplicate_archive()
_QUESTION_RESPONSE = httpx.Response(status_code=HTTPStatus.OK, json=_METADATA)
_STORED_RESPONSE = httpx.Response(status_code=HTTPStatus.OK, content=_STORED)
_FAILURES: dict[
    str,
    tuple[
        httpx.Response | Exception, httpx.Response | Exception | None, bytes
    ],
] = {
    "question-unreadable": (
        httpx.Response(status_code=HTTPStatus.NOT_FOUND),
        None,
        _ARCHIVE,
    ),
    "missing-url": (
        httpx.Response(status_code=HTTPStatus.OK, json={}),
        None,
        _ARCHIVE,
    ),
    "insecure-url": (
        httpx.Response(
            status_code=HTTPStatus.OK,
            json={"file_url": "http://files.example/project.zip"},
        ),
        None,
        _ARCHIVE,
    ),
    "bad-json": (
        httpx.Response(status_code=HTTPStatus.OK, content=b"not JSON"),
        None,
        _ARCHIVE,
    ),
    "bad-envelope": (
        httpx.Response(status_code=HTTPStatus.OK, json={"data": []}),
        None,
        _ARCHIVE,
    ),
    "question-timeout": (
        httpx.ReadTimeout(message="Read-back timed out"),
        None,
        _ARCHIVE,
    ),
    "download-failed": (
        _QUESTION_RESPONSE,
        httpx.Response(status_code=HTTPStatus.FORBIDDEN),
        _ARCHIVE,
    ),
    "different-files": (
        _QUESTION_RESPONSE,
        httpx.Response(
            status_code=HTTPStatus.OK,
            content=_zip(
                entries=[("other.py", b"pass\n")], compression=ZIP_STORED
            ),
        ),
        _ARCHIVE,
    ),
    "different-content": (
        _QUESTION_RESPONSE,
        httpx.Response(
            status_code=HTTPStatus.OK,
            content=_zip(
                entries=[("solution.py", b"changed"), _ENTRIES[1]],
                compression=ZIP_STORED,
            ),
        ),
        _ARCHIVE,
    ),
    "duplicate-upload": (
        _QUESTION_RESPONSE,
        _STORED_RESPONSE,
        _DUPLICATE_ARCHIVE,
    ),
    "duplicate-download": (
        _QUESTION_RESPONSE,
        httpx.Response(status_code=HTTPStatus.OK, content=_DUPLICATE_ARCHIVE),
        _ARCHIVE,
    ),
    "invalid-upload": (_QUESTION_RESPONSE, _STORED_RESPONSE, b"not a ZIP"),
    "invalid-download": (
        _QUESTION_RESPONSE,
        httpx.Response(status_code=HTTPStatus.OK, content=b"not a ZIP"),
        _ARCHIVE,
    ),
    "download-timeout": (
        _QUESTION_RESPONSE,
        httpx.ReadTimeout(message="Download timed out"),
        _ARCHIVE,
    ),
}


def _reply(*, route: respx.Route, result: httpx.Response | Exception) -> None:
    """Supply a response or raise a transport failure through HTTP."""
    if isinstance(result, Exception):
        _ = route.mock(side_effect=result)
    else:
        _ = route.mock(return_value=result)


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="problem", argvalues=_FAILURES)
async def test_unverified_upload_keeps_original_timeout(
    *, connection: _Connection, problem: str
) -> None:
    """Failed proof never converts an uncertain upload into success."""
    question, stored, archive = _FAILURES[problem]
    timeout = _timeout(connection=connection)
    post = connection.router.post(url=_UPLOAD_URL).mock(side_effect=timeout)
    _reply(route=connection.router.get(url=_QUESTION_URL), result=question)
    if stored is not None:
        _reply(route=connection.router.get(url=_DOWNLOAD_URL), result=stored)
    with pytest.raises(
        expected_exception=(httpx.ReadTimeout, httpx2.ReadTimeout)
    ) as raised:
        _ = await _upload(connection=connection, archive=archive, retries=0)
    assert raised.value is timeout
    assert post.call_count == 1


class _Unseekable(FileIO):
    """Model input that cannot be replayed or compared after sending."""

    @override
    def seekable(self) -> bool:
        """Report that upload recovery cannot rewind this input."""
        return False


@pytest.mark.asyncio
async def test_unseekable_upload_is_not_verified_or_retried(
    connection: _Connection,
    tmp_path: Path,
) -> None:
    """Consumed non-seekable input retains the original failure."""
    timeout = _timeout(connection=connection)
    post = connection.router.post(url=_UPLOAD_URL).mock(side_effect=timeout)
    archive_path = tmp_path / "project.zip"
    _ = archive_path.write_bytes(data=_ARCHIVE)
    with (
        _Unseekable(file=archive_path, mode="rb") as archive,
        pytest.raises(
            expected_exception=(httpx.ReadTimeout, httpx2.ReadTimeout)
        ) as raised,
    ):
        _ = await _upload(connection=connection, archive=archive, retries=2)
    assert raised.value is timeout
    assert post.call_count == 1


@pytest.mark.parametrize(
    argnames=("method", "url", "has_files"),
    argvalues=[
        ("GET", _UPLOAD_URL, True),
        ("POST", _UPLOAD_URL, False),
        ("POST", "https://example.com/other/upload_project_zip", True),
        ("POST", _QUESTION_URL + "/testcases/", True),
    ],
)
def test_unrelated_requests_have_no_project_upload_context(
    *, method: str, url: str, has_files: bool
) -> None:
    """Recovery only applies to the known project-upload operation."""
    files = (
        {"file": ("project.zip", _ARCHIVE, "application/zip")}
        if has_files
        else None
    )
    assert project_upload_context(method=method, url=url, files=files) is None


def _recorded_requests(*, calls: Sequence[object]) -> list[httpx.Request]:
    """Narrow the request recorder's untyped collection at its
    boundary.
    """
    requests: list[httpx.Request] = []
    for call in calls:
        assert isinstance(call, respx.models.Call)
        requests.append(call.request)
    return requests


@pytest.mark.asyncio
async def test_failed_verification_retains_normal_retry_policy(
    connection: _Connection,
) -> None:
    """A repeatable upload can still retry after inconclusive read-
    back.
    """
    timeout = _timeout(connection=connection)
    post = connection.router.post(url=_UPLOAD_URL).mock(
        side_effect=[
            timeout,
            httpx.Response(status_code=HTTPStatus.OK, json=_METADATA),
        ]
    )
    _ = connection.router.get(url=_QUESTION_URL).respond(
        status_code=HTTPStatus.NOT_FOUND
    )
    assert (
        await _upload(connection=connection, archive=_ARCHIVE, retries=1)
        == _METADATA
    )
    expected_methods = ["POST", "GET", "POST"]
    assert post.call_count == expected_methods.count("POST")
    recorded = _recorded_requests(calls=connection.router.calls)
    assert [request.method for request in recorded] == expected_methods
    for request in recorded:
        if request.method == "POST":
            assert _ARCHIVE in request.content


async def _read_tests(*, connection: _Connection) -> None:
    """Read an unrelated endpoint through the selected public client."""
    async with _client(connection=connection, retries=0) as client:
        if isinstance(client, AsyncHackerRank):
            _ = await client.tests.list()
        else:
            _ = client.tests.list()


@pytest.mark.asyncio
async def test_unrelated_timeout_is_unchanged(connection: _Connection) -> None:
    """Other read timeouts do not trigger project verification
    requests.
    """
    timeout = _timeout(connection=connection)
    route = connection.router.get(
        url="https://www.hackerrank.com/x/api/v3/tests"
    ).mock(side_effect=timeout)
    with pytest.raises(
        expected_exception=(httpx.ReadTimeout, httpx2.ReadTimeout)
    ) as raised:
        await _read_tests(connection=connection)
    assert raised.value is timeout
    assert route.call_count == 1
    assert len(connection.router.calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=("operation", "parameters", "expected_path"),
    argvalues=[
        ("api_create_question", None, "/x/api/v3/questions/"),
        (
            "api_update_question",
            {"question_id": "q1"},
            "/x/api/v3/questions/q1/",
        ),
    ],
)
async def test_prepared_question_writes_match_wire(
    *,
    connection: _Connection,
    operation: str,
    parameters: dict[str, str] | None,
    expected_path: str,
) -> None:
    """Generic preflight plans describe the exact path sent by the
    client.
    """
    selected, path, query = prepare_operation(
        operation=operation, path_parameters=parameters, query=None, body={}
    )
    assert path == expected_path
    route = connection.router.route(
        method=selected.method,
        url="https://www.hackerrank.com" + expected_path,
    ).respond(status_code=HTTPStatus.OK, json={})
    async with _client(connection=connection, retries=0) as client:
        if isinstance(client, AsyncHackerRank):
            _ = await client.api.call(
                operation=operation,
                path_parameters=parameters,
                query=query,
                body={},
            )
        else:
            _ = client.api.call(
                operation=operation,
                path_parameters=parameters,
                query=query,
                body={},
            )
    assert route.call_count == 1
    assert route.calls.last.request.url.path == expected_path
