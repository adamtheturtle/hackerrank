"""Build project archives from prepared directories."""

from collections.abc import Iterator
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from beartype import beartype


@beartype
def _directory_files(
    *, directory: Path, prefix: Path
) -> Iterator[tuple[Path, Path]]:
    """Yield sorted file paths, rejecting symbolic links."""
    for path in sorted(directory.iterdir()):
        relative = prefix / path.name
        if path.is_symlink():
            msg = f"Directory uploads do not support symbolic links: {path}"
            raise ValueError(msg)
        if path.is_dir():
            yield from _directory_files(directory=path, prefix=relative)
        else:
            yield path, relative


@beartype
def project_archive(*, directory: Path) -> bytes:
    """Package every file as a ZIP without creating a temporary
    archive.
    """
    if not directory.is_dir():
        msg = f"Not a directory: {directory}"
        raise NotADirectoryError(msg)
    with BytesIO() as buffer:
        with ZipFile(
            file=buffer, mode="w", compression=ZIP_DEFLATED
        ) as archive:
            for path, relative in _directory_files(
                directory=directory, prefix=Path()
            ):
                archive.write(filename=path, arcname=relative.as_posix())
        return buffer.getvalue()
