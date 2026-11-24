"""Offline project archive creation."""

from io import BytesIO
from operator import methodcaller
from pathlib import Path
from zipfile import ZipFile

import pytest
from beartype.roar import BeartypeCallHintParamViolation

from hackerrank.projects import build_project_archive


def test_build_archive(tmp_path: Path) -> None:
    """Preserve the selected bytes and executable mode."""
    script = tmp_path / "run.sh"
    _ = script.write_bytes(data=b"#!/bin/sh\r\n\x00\xff")
    script.chmod(mode=0o755)
    (tmp_path / "excluded.txt").touch()
    contents = build_project_archive(
        directory=tmp_path, files=[Path("run.sh")]
    )
    with ZipFile(file=BytesIO(initial_bytes=contents)) as archive:
        assert archive.namelist() == ["run.sh"]
        assert archive.read(name="run.sh") == script.read_bytes()
        assert (
            archive.getinfo(name="run.sh").external_attr >> 16
            == script.stat().st_mode
        )


def test_reject_symlinked_directory(tmp_path: Path) -> None:
    """A selected file cannot be reached through a symbolic link."""
    (tmp_path / "link").symlink_to(target=tmp_path, target_is_directory=True)
    with pytest.raises(expected_exception=ValueError, match="symbolic links"):
        _ = build_project_archive(
            directory=tmp_path, files=[Path("link/run.sh")]
        )


@pytest.mark.parametrize(
    argnames=("names", "pattern"),
    argvalues=[
        (["run.sh", "run.sh"], "duplicate paths"),
        (["../run.sh"], "relative project file"),
        (["/run.sh"], "relative project file"),
        (["."], "regular file"),
    ],
)
def test_reject_invalid_selected_files(
    tmp_path: Path, names: list[str], pattern: str
) -> None:
    """Require unique relative names pointing to regular files."""
    with pytest.raises(expected_exception=ValueError, match=pattern):
        _ = build_project_archive(
            directory=tmp_path, files=[Path(name) for name in names]
        )


def test_reject_file_as_directory(tmp_path: Path) -> None:
    """Validate the base directory even for an empty file selection."""
    file = tmp_path / "file.txt"
    file.touch()
    with pytest.raises(expected_exception=NotADirectoryError):
        _ = build_project_archive(directory=file, files=[])


def test_build_archive_requires_path() -> None:
    """Reject a directory string at the public archive boundary."""
    with pytest.raises(expected_exception=BeartypeCallHintParamViolation):
        _ = methodcaller("__call__", directory="starter", files=[])(
            build_project_archive
        )
