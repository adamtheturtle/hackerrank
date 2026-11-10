"""Handle question-write URLs and verify uploads after lost responses."""

import json as json_module
import zlib
from collections.abc import Mapping
from dataclasses import dataclass
from http import HTTPStatus
from io import BytesIO
from typing import BinaryIO
from zipfile import BadZipFile, ZipFile

import httpx
import httpx2

from hackerrank._request_types import MultipartFiles
from hackerrank._request_urls import project_upload_question_url
from hackerrank._responses import object_response
from hackerrank.transports import AsyncTransport, Transport, TransportResponse
from hackerrank.types import JSONValue

_READ_TIMEOUTS = (httpx.ReadTimeout, httpx2.ReadTimeout)
_VERIFICATION_ERRORS = (
    httpx.TransportError,
    httpx2.TransportError,
    OSError,
    ValueError,
    TypeError,
    RuntimeError,
    BadZipFile,
    zlib.error,
)


@dataclass(frozen=True)
class _UploadMetadata:
    """The archive location returned by a question read."""

    file_url: str
    file_path: JSONValue


def _archive_bytes(*, archive: bytes | BinaryIO) -> bytes | None:
    """Read seekable input without changing its current position."""
    if isinstance(archive, bytes):
        return archive
    if not archive.seekable():
        return None
    position = archive.tell()
    try:
        _ = archive.seek(0, 0)  # noqa: KW001 - Positional-only API.
        return archive.read()
    finally:
        _ = archive.seek(position, 0)  # noqa: KW001 - Positional-only API.


def project_upload_context(
    *, method: str, url: str, files: MultipartFiles
) -> tuple[str, bytes] | None:
    """Identify a project upload whose contents can still be verified."""
    if files is None:
        return None
    question_url = project_upload_question_url(method=method, url=url)
    if question_url is None:
        return None
    archive = _archive_bytes(archive=files["file"][1])
    if archive is None:
        return None
    return question_url, archive


def _upload_metadata(*, response: TransportResponse) -> _UploadMetadata | None:
    """Read the archive location from a wrapped or bare question."""
    if response.status_code >= HTTPStatus.MULTIPLE_CHOICES:
        return None
    payload = object_response(value=response.json())
    question = object_response(value=payload.get("data", payload))
    file_url = question.get("file_url")
    if not isinstance(file_url, str) or not file_url.startswith("https://"):
        return None
    return _UploadMetadata(
        file_url=file_url, file_path=question.get("file_path")
    )


def _verified_response(
    *, metadata: _UploadMetadata, uploaded: bytes, stored: TransportResponse
) -> TransportResponse | None:
    """Accept matching file names and contents, independent of ZIP
    metadata.
    """
    if stored.status_code >= HTTPStatus.MULTIPLE_CHOICES:
        return None
    with (
        ZipFile(file=BytesIO(initial_bytes=uploaded)) as expected,
        ZipFile(file=BytesIO(initial_bytes=stored.content)) as actual,
    ):
        expected_names = expected.namelist()
        actual_names = actual.namelist()
        if (
            len(set(expected_names)) != len(expected_names)
            or len(set(actual_names)) != len(actual_names)
            or set(expected_names) != set(actual_names)
            or any(
                expected.read(name=name) != actual.read(name=name)
                for name in expected_names
            )
        ):
            return None
    return TransportResponse(
        status_code=HTTPStatus.OK,
        headers={"content-type": "application/json"},
        content=json_module.dumps(
            obj={
                "file_url": metadata.file_url,
                "file_path": metadata.file_path,
            }
        ).encode(encoding="utf-8"),
    )


def question_request(
    *,
    transport: Transport,
    method: str,
    url: str,
    headers: dict[str, str],
    params: dict[str, str | int] | None,
    json: Mapping[str, JSONValue] | None,
    files: MultipartFiles,
) -> TransportResponse:
    """Verify a timed-out project upload before the retry policy repeats
    it.
    """
    try:
        return transport(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            files=files,
        )
    except _READ_TIMEOUTS:
        try:
            context = project_upload_context(
                method=method, url=url, files=files
            )
            if context is not None:
                question_url, uploaded = context
                question = transport(
                    method="GET",
                    url=question_url,
                    headers=headers,
                    params=None,
                    json=None,
                    files=None,
                )
                metadata = _upload_metadata(response=question)
                if metadata is not None:
                    stored = transport(
                        method="GET",
                        url=metadata.file_url,
                        headers={},
                        params=None,
                        json=None,
                        files=None,
                    )
                    verified = _verified_response(
                        metadata=metadata, uploaded=uploaded, stored=stored
                    )
                    if verified is not None:
                        return verified
        except _VERIFICATION_ERRORS:
            pass
        raise


async def async_question_request(
    *,
    transport: AsyncTransport,
    method: str,
    url: str,
    headers: dict[str, str],
    params: dict[str, str | int] | None,
    json: Mapping[str, JSONValue] | None,
    files: MultipartFiles,
) -> TransportResponse:
    """Verify a timed-out async upload before the retry policy repeats
    it.
    """
    try:
        return await transport(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            files=files,
        )
    except _READ_TIMEOUTS:
        try:
            context = project_upload_context(
                method=method, url=url, files=files
            )
            if context is not None:
                question_url, uploaded = context
                question = await transport(
                    method="GET",
                    url=question_url,
                    headers=headers,
                    params=None,
                    json=None,
                    files=None,
                )
                metadata = _upload_metadata(response=question)
                if metadata is not None:
                    stored = await transport(
                        method="GET",
                        url=metadata.file_url,
                        headers={},
                        params=None,
                        json=None,
                        files=None,
                    )
                    verified = _verified_response(
                        metadata=metadata, uploaded=uploaded, stored=stored
                    )
                    if verified is not None:
                        return verified
        except _VERIFICATION_ERRORS:
            pass
        raise
