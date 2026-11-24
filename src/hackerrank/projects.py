"""Build HackerRank project ZIPs from selected local files."""

from collections.abc import Iterable
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from beartype import beartype


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
