"""Build HackerRank project ZIPs from selected local files."""

import os
import subprocess
from collections.abc import Iterable
from io import BytesIO
from pathlib import Path
from shutil import which
from zipfile import ZIP_DEFLATED, ZipFile

from beartype import beartype


@beartype
def git_index_project_files(*, directory: Path) -> tuple[Path, ...]:
    """List sorted, unique candidate paths relative to a Git directory.

    Tracked paths are included even if ignored or absent from the working
    tree. Paths outside the index follow repository ``.gitignore`` files.
    Apply project exclusions and check file types before archiving.
    Raise ValueError if Git is unavailable or cannot list the paths.
    """
    git = which(cmd="git")
    if git is None:
        message = "Project file discovery requires Git."
        raise ValueError(message)
    result = subprocess.run(  # noqa: S603 - Fixed Git arguments.
        args=[
            git,
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-per-directory=.gitignore",
            "--",
            ".",
        ],
        cwd=directory,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = os.fsdecode(filename=result.stderr).strip()
        message = (
            f"Cannot list project files in {directory}. "
            f"Run in a Git checkout. {detail}"
        )
        raise ValueError(message)
    return tuple(
        sorted(
            {
                Path(os.fsdecode(filename=name))
                for name in result.stdout.split(sep=b"\0")
                if name != b""
            }
        )
    )


@beartype
def build_project_archive(*, directory: Path, files: Iterable[Path]) -> bytes:
    """ZIP explicitly selected paths relative to a directory.

    File selection belongs to the caller. Paths must be unique regular files
    inside the directory. Symbolic links within the directory are rejected.
    File contents and permissions are preserved.
    """
    directory = directory.resolve(strict=True)
    if not directory.is_dir():
        raise NotADirectoryError(directory)
    paths = sorted(files)
    if len(paths) != len(set(paths)):
        message = "Project archive contains duplicate paths."
        raise ValueError(message)
    with BytesIO() as buffer:
        with ZipFile(
            file=buffer, mode="w", compression=ZIP_DEFLATED
        ) as archive:
            for relative in paths:
                if relative.anchor != "" or ".." in relative.parts:
                    message = (
                        f"Expected a relative project file path: {relative}"
                    )
                    raise ValueError(message)
                path = directory / relative
                if any(
                    (directory / parent).is_symlink()
                    for parent in (relative, *relative.parents)
                ):
                    message = (
                        f"Project files cannot use symbolic links: {relative}"
                    )
                    raise ValueError(message)
                if not path.is_file():
                    message = (
                        f"Project file must be a regular file: {relative}"
                    )
                    raise ValueError(message)
                archive.write(filename=path, arcname=relative.as_posix())
        return buffer.getvalue()
