"""Tests for asynchronous `hackerrank` retries."""

from collections.abc import Mapping
from http import HTTPStatus
from pathlib import Path

import httpx
import httpx2
import pytest

from hackerrank._request_types import MultipartFiles
from hackerrank.async_client import AsyncHackerRank
from hackerrank.exceptions import (
    HackerRankError,
)
from hackerrank.transports import TransportResponse
from hackerrank.types import JSONValue
from tests.retries.responses import PAGE_BODY, ZIP_BODY, error, ok
from tests.retries.transports import ScriptedCalls


class _AsyncScriptedTransport(ScriptedCalls):
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


@pytest.mark.asyncio
async def test_non_transient_status_is_not_repeated() -> None:
    """An async request error which cannot improve is raised once."""
    transport = _AsyncScriptedTransport(
        script=[error(status_code=HTTPStatus.BAD_REQUEST)],
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
            error(status_code=HTTPStatus.SERVICE_UNAVAILABLE),
            ok(content=PAGE_BODY),
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
async def test_transport_error_is_retried(sleeps: list[float]) -> None:
    """An async transport error on a repeatable request is retried.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _AsyncScriptedTransport(
        script=[
            httpx.ReadTimeout(message="The read operation timed out"),
            ok(content=PAGE_BODY),
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
async def test_httpx2_transport_error_is_retried(
    sleeps: list[float],
) -> None:
    """A native async HTTPX2 transport error is retried.

    Args:
        sleeps: The recorded delays between attempts.
    """
    transport = _AsyncScriptedTransport(
        script=[
            httpx2.ReadTimeout(message="The read operation timed out"),
            ok(content=PAGE_BODY),
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
async def test_default_makes_one_attempt() -> None:
    """By default a failing async request is not retried."""
    transport = _AsyncScriptedTransport(
        script=[error(status_code=HTTPStatus.SERVICE_UNAVAILABLE)],
    )
    client = AsyncHackerRank(api_key="key", transport=transport)
    with pytest.raises(expected_exception=HackerRankError):
        await client.tests.list()
    assert transport.methods == ["GET"]


@pytest.mark.asyncio
async def test_create_is_not_repeated() -> None:
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
async def test_file_object_is_rewound_between_attempts(
    tmp_path: Path,
) -> None:
    """The async upload sends the zip in full on every attempt.

    Args:
        tmp_path: A temporary directory to hold the zip.
    """
    transport = _AsyncScriptedTransport(
        script=[
            error(status_code=HTTPStatus.BAD_GATEWAY),
            ok(content=ZIP_BODY),
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
