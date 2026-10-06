"""Tests for `hackerrank` uploads retries."""

import io
from http import HTTPStatus
from pathlib import Path
from typing import override

from hackerrank._retries import rewind_files
from hackerrank.client import HackerRank
from tests.retries.helpers import ZIP_BODY, ScriptedTransport, error, ok


def test_file_object_is_rewound_between_attempts(tmp_path: Path) -> None:
    """The zip is sent in full on every attempt.

    Args:
        tmp_path: A temporary directory to hold the zip.
    """
    transport = ScriptedTransport(
        script=[
            error(status_code=HTTPStatus.BAD_GATEWAY),
            ok(content=ZIP_BODY),
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
    transport = ScriptedTransport(
        script=[
            error(status_code=HTTPStatus.BAD_GATEWAY),
            ok(content=ZIP_BODY),
        ],
    )
    client = HackerRank(api_key="key", transport=transport, retries=1)
    _ = client.questions.upload_project_zip(question_id="q1", file=b"zip")
    assert transport.file_contents == [b"zip", b"zip"]


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
