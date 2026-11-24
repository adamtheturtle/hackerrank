"""Offline project archive creation."""

from io import BytesIO
from pathlib import Path
from shutil import which
from subprocess import run
from zipfile import ZipFile

import pytest

from hackerrank.projects import build_project_archive, git_index_project_files


def test_git_index_project_files(tmp_path: Path) -> None:
    """List candidates relative to the project within the checkout."""
    git = which(cmd="git")
    assert git is not None
    _ = run(args=[git, "init"], cwd=tmp_path, check=True, capture_output=True)  # noqa: S603
    _ = (tmp_path / ".gitignore").write_text(data="*.db\n", encoding="utf-8")
    (tmp_path / "outside.txt").touch()
    project = tmp_path / "project"
    project.mkdir()
    for name in (
        "tracked.db",
        "deleted.txt",
        "ignored.db",
        "untracked file.txt",
    ):
        (project / name).touch()
    _ = run(  # noqa: S603 - Fixed Git arguments in a temporary checkout.
        args=[git, "add", "-f", "--", "tracked.db", "deleted.txt"],
        cwd=project,
        check=True,
        capture_output=True,
    )
    (project / "deleted.txt").unlink()

    assert git_index_project_files(directory=project) == (
        Path("deleted.txt"),
        Path("tracked.db"),
        Path("untracked file.txt"),
    )


def test_git_index_requires_checkout(tmp_path: Path) -> None:
    """Surface discovery errors to callers."""
    with pytest.raises(
        expected_exception=ValueError, match="in a Git checkout"
    ):
        _ = git_index_project_files(directory=tmp_path)


def test_git_index_requires_git(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Git is only required when discovering files through its index."""
    monkeypatch.setenv(name="PATH", value=str(object=tmp_path))
    with pytest.raises(expected_exception=ValueError, match="requires Git"):
        _ = git_index_project_files(directory=tmp_path)


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
