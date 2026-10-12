"""Prepared project directories use the existing multipart ZIP
endpoint.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from email import policy
from email.parser import BytesParser
from io import BytesIO
from pathlib import Path
from shutil import copytree, ignore_patterns
from zipfile import ZipFile

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.types import JSONValue

_URL = "https://www.hackerrank.com/x/api/v3/questions/q1/upload_project_zip"
_RESPONSE: dict[str, JSONValue] = {
    "file_url": "https://example.com/project.zip",
    "file_path": "question_projects/q1/project.zip",
}


@asynccontextmanager
async def _upload_client(
    *,
    client_type: type[HackerRank] | type[AsyncHackerRank],
    router: respx.MockRouter,
) -> AsyncGenerator[HackerRank | AsyncHackerRank]:
    """Construct the selected client and close it after the test."""
    _ = router.post(url=_URL).respond(status_code=200, json=_RESPONSE)
    client = client_type(api_key="test-key", retries=1)
    if isinstance(client, AsyncHackerRank):
        async with client:
            yield client
    else:
        with client:
            yield client


async def _upload(
    *, client: HackerRank | AsyncHackerRank, directory: Path
) -> dict[str, JSONValue]:
    """Upload through either public client."""
    if isinstance(client, AsyncHackerRank):
        return await client.questions.upload_project_directory(
            question_id="q1", directory=directory
        )
    return client.questions.upload_project_directory(
        question_id="q1", directory=directory
    )


def _archive_bytes(*, request: httpx.Request) -> bytes:
    """Extract the ZIP from the outgoing multipart request."""
    message = BytesParser(policy=policy.default).parsebytes(
        text=(
            f"Content-Type: {request.headers['Content-Type']}\r\n\r\n"
        ).encode()
        + request.content,
    )
    parts = [
        part
        for part in message.iter_parts()
        if part.get_filename() is not None
    ]
    assert len(parts) == 1
    part = parts[0]
    assert part.get_param(param="name", header="content-disposition") == "file"
    assert part.get_filename() == "project.zip"
    assert part.get_content_type() == "application/zip"
    payload = part.get_payload(decode=True)
    assert isinstance(payload, bytes)
    return payload


def _archive_contents(*, router: respx.MockRouter) -> dict[str, bytes]:
    """Read the files sent in the latest request."""
    with ZipFile(
        file=BytesIO(
            initial_bytes=_archive_bytes(request=router.calls.last.request)
        )
    ) as archive:
        return {name: archive.read(name=name) for name in archive.namelist()}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames="client_type",
    argvalues=[HackerRank, AsyncHackerRank],
    ids=["sync", "async"],
)
async def test_preserves_files(
    client_type: type[HackerRank] | type[AsyncHackerRank],
    mock_hackerrank_api: respx.MockRouter,
    tmp_path: Path,
) -> None:
    """Preserve every file, including hidden files and binary bytes."""
    async with _upload_client(
        client_type=client_type, router=mock_hackerrank_api
    ) as upload_client:
        expected = {
            ".config": b"hidden\n",
            "nested/main.py": "print('caf\u00e9')\r\n".encode(),
            "nested/image.bin": bytes(range(256)),
            "empty.txt": b"",
            "uv.lock": b"include lockfiles",
            "node_modules/dependency.js": b"include dependencies",
        }
        for name, data in expected.items():
            path = tmp_path / name
            path.parent.mkdir(parents=True, exist_ok=True)
            _ = path.write_bytes(data=data)
        result = await _upload(client=upload_client, directory=tmp_path)
        assert result == _RESPONSE
        assert _archive_contents(router=mock_hackerrank_api) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames="client_type",
    argvalues=[HackerRank, AsyncHackerRank],
    ids=["sync", "async"],
)
async def test_staged_directory(
    client_type: type[HackerRank] | type[AsyncHackerRank],
    mock_hackerrank_api: respx.MockRouter,
    tmp_path: Path,
) -> None:
    """Callers can filter files with ``copytree`` before uploading."""
    async with _upload_client(
        client_type=client_type, router=mock_hackerrank_api
    ) as upload_client:
        source = tmp_path / "source"
        for name in [
            "main.py",
            "node_modules/dependency.js",
            "nested/uv.lock",
        ]:
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            _ = path.write_bytes(data=b"data")
        directory = Path(
            copytree(
                src=source,
                dst=tmp_path / "upload",
                ignore=ignore_patterns("node_modules", "uv.lock"),
            )
        )
        _ = await _upload(client=upload_client, directory=directory)
        assert _archive_contents(router=mock_hackerrank_api) == {
            "main.py": b"data",
        }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames="client_type",
    argvalues=[HackerRank, AsyncHackerRank],
    ids=["sync", "async"],
)
async def test_empty_directory(
    client_type: type[HackerRank] | type[AsyncHackerRank],
    mock_hackerrank_api: respx.MockRouter,
    tmp_path: Path,
) -> None:
    """An empty directory produces a valid ZIP."""
    async with _upload_client(
        client_type=client_type, router=mock_hackerrank_api
    ) as upload_client:
        _ = await _upload(client=upload_client, directory=tmp_path)
        assert _archive_contents(router=mock_hackerrank_api) == {}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames="client_type",
    argvalues=[HackerRank, AsyncHackerRank],
    ids=["sync", "async"],
)
@pytest.mark.parametrize(argnames="existing_file", argvalues=[True, False])
async def test_invalid_directory(
    client_type: type[HackerRank] | type[AsyncHackerRank],
    mock_hackerrank_api: respx.MockRouter,
    tmp_path: Path,
    *,
    existing_file: bool,
) -> None:
    """Reject invalid directories before HTTP requests."""
    async with _upload_client(
        client_type=client_type, router=mock_hackerrank_api
    ) as upload_client:
        directory = tmp_path / "invalid"
        if existing_file:
            _ = directory.write_bytes(data=b"data")
        with pytest.raises(
            expected_exception=NotADirectoryError, match="Not a directory"
        ):
            _ = await _upload(client=upload_client, directory=directory)
        assert len(mock_hackerrank_api.calls) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames="client_type",
    argvalues=[HackerRank, AsyncHackerRank],
    ids=["sync", "async"],
)
@pytest.mark.parametrize(argnames="target_directory", argvalues=[True, False])
async def test_symbolic_links(
    client_type: type[HackerRank] | type[AsyncHackerRank],
    mock_hackerrank_api: respx.MockRouter,
    tmp_path: Path,
    *,
    target_directory: bool,
) -> None:
    """Reject symbolic links before making an upload request."""
    async with _upload_client(
        client_type=client_type, router=mock_hackerrank_api
    ) as upload_client:
        target = tmp_path / "target"
        if target_directory:
            target.mkdir()
        else:
            _ = target.write_bytes(data=b"outside upload directory")
        directory = tmp_path / "project"
        directory.mkdir()
        (directory / "link").symlink_to(
            target=target, target_is_directory=target_directory
        )
        with pytest.raises(
            expected_exception=ValueError, match="symbolic links"
        ):
            _ = await _upload(client=upload_client, directory=directory)
        assert len(mock_hackerrank_api.calls) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames="client_type",
    argvalues=[HackerRank, AsyncHackerRank],
    ids=["sync", "async"],
)
async def test_retries_same_archive(
    client_type: type[HackerRank] | type[AsyncHackerRank],
    mock_hackerrank_api: respx.MockRouter,
    tmp_path: Path,
) -> None:
    """Retries send the same packaged bytes and preserve the response."""
    async with _upload_client(
        client_type=client_type, router=mock_hackerrank_api
    ) as upload_client:
        _ = (tmp_path / "main.py").write_bytes(data=b"print(1)\n")
        archives: list[bytes] = []

        def respond(request: httpx.Request) -> httpx.Response:
            """Record each uploaded archive and fail the first attempt."""
            archives.append(_archive_bytes(request=request))
            if len(archives) == 1:
                return httpx.Response(status_code=502, json={})
            return httpx.Response(status_code=200, json=_RESPONSE)

        route = mock_hackerrank_api.post(url=_URL).mock(side_effect=respond)
        result = await _upload(client=upload_client, directory=tmp_path)
        assert result == _RESPONSE
        expected_attempts = 2
        assert len(route.calls) == expected_attempts
        assert archives == [archives[0], archives[0]]
        assert _archive_contents(router=mock_hackerrank_api) == {
            "main.py": b"print(1)\n",
        }
