"""Native HackerRank project configuration and ZIP updates."""

import stat
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import pytest
import yaml

from hackerrank.project_configuration import (
    ProjectConfiguration,
    configure_project_archive,
)

_EXECUTABLE_MODE = (
    stat.S_IFREG
    | stat.S_IRWXU
    | stat.S_IRGRP
    | stat.S_IXGRP
    | stat.S_IROTH
    | stat.S_IXOTH
)
_NATIVE = (
    b"version: 1.0\nconfiguration:\n"
    b"  has_webserver: false\n  future_setting: keep\n"
)


def _zip(*, existing: bool) -> bytes:
    """Include binary bytes, executable permissions, and entry
    metadata.
    """
    with BytesIO() as buffer:
        with ZipFile(
            file=buffer, mode="w", compression=ZIP_DEFLATED
        ) as archive:
            info = ZipInfo(filename="run.sh")
            info.external_attr = _EXECUTABLE_MODE << 16
            info.comment = b"Keep this comment"
            archive.writestr(
                zinfo_or_arcname=info, data=b"#!/bin/sh\n\x00\xff"
            )
            if existing:
                archive.writestr(
                    zinfo_or_arcname="hackerrank.yml", data=b"old"
                )
        return buffer.getvalue()


@pytest.mark.parametrize(argnames="existing", argvalues=[False, True])
def test_configure_preserves_other_entries(*, existing: bool) -> None:
    """Adding or replacing the root configuration preserves other ZIP
    metadata.
    """
    configured = configure_project_archive(
        archive=_zip(existing=existing), configuration=_NATIVE
    )
    with ZipFile(file=BytesIO(initial_bytes=configured)) as archive:
        assert sorted(archive.namelist()) == ["hackerrank.yml", "run.sh"]
        assert archive.read(name="hackerrank.yml") == _NATIVE
        assert archive.read(name="run.sh") == b"#!/bin/sh\n\x00\xff"
        info = archive.getinfo(name="run.sh")
        assert info.external_attr >> 16 == _EXECUTABLE_MODE
        assert info.comment == b"Keep this comment"


def test_explicit_configuration_document() -> None:
    """Typed values render the native hierarchy without choosing
    policy.
    """
    rendered = ProjectConfiguration(
        has_webserver=False,
        readonly_paths=["tests"],
        scoring_command="grade",
        scoring_files=["report.xml"],
        default_open_files=["solution.py"],
        project_menu={"install": "install", "run": "run", "test": "test"},
    ).to_yaml()
    assert yaml.safe_load(stream=rendered) == {
        "version": 1.0,
        "configuration": {
            "has_webserver": False,
            "readonly_paths": ["tests"],
            "scoring": {"command": "grade", "files": ["report.xml"]},
            "ide_config": {
                "default_open_files": ["solution.py"],
                "project_menu": {
                    "install": "install",
                    "run": "run",
                    "test": "test",
                },
            },
        },
    }


@pytest.mark.parametrize(
    argnames="configuration",
    argvalues=[
        b"\xff",
        b"[broken",
        b"[]",
        b"version: true\nconfiguration: {}",
        b"version: 2\nconfiguration: {}",
        b"version: 1\nconfiguration: []",
    ],
)
def test_reject_invalid_configuration(configuration: bytes) -> None:
    """Reject a malformed native configuration before rewriting the
    ZIP.
    """
    with pytest.raises(
        expected_exception=ValueError, match="Project configuration"
    ):
        _ = configure_project_archive(
            archive=_zip(existing=False), configuration=configuration
        )


def test_reject_invalid_zip() -> None:
    """Report an invalid ZIP as a preparation error."""
    with pytest.raises(expected_exception=ValueError, match="valid ZIP"):
        _ = configure_project_archive(
            archive=b"invalid", configuration=_NATIVE
        )


def test_reject_duplicate_zip_entries() -> None:
    """Reject ambiguous ZIPs even if only one entry would be replaced."""
    with BytesIO() as buffer:
        with ZipFile(file=buffer, mode="w") as archive:
            archive.writestr(zinfo_or_arcname="hackerrank.yml", data=b"one")
            with pytest.warns(
                expected_warning=UserWarning, match="Duplicate name"
            ):
                archive.writestr(
                    zinfo_or_arcname="hackerrank.yml", data=b"two"
                )
        with pytest.raises(
            expected_exception=ValueError, match="duplicate entries"
        ):
            _ = configure_project_archive(
                archive=buffer.getvalue(), configuration=_NATIVE
            )
