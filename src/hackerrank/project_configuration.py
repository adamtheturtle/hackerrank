"""Render native HackerRank configuration and add it to project ZIPs."""

from io import BytesIO
from typing import TypedDict, TypeIs
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

import yaml
from beartype import beartype
from pydantic import BaseModel, ConfigDict, field_validator

_CONFIGURATION_VERSION = 1.0


class ScoringConfiguration(TypedDict):
    """The scoring command and report files."""

    command: str
    files: list[str]


class IDEConfiguration(TypedDict):
    """The files and menu commands displayed in the IDE."""

    default_open_files: list[str]
    project_menu: dict[str, str]


class ProjectSettings(TypedDict):
    """The settings in the native configuration mapping."""

    has_webserver: bool
    readonly_paths: list[str]
    scoring: ScoringConfiguration
    ide_config: IDEConfiguration


class ProjectConfiguration(BaseModel):
    """A version-one HackerRank project configuration document."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    version: float
    configuration: ProjectSettings

    @field_validator("version")
    @classmethod
    def _require_version_one(cls, version: float) -> float:
        if version != _CONFIGURATION_VERSION:
            message = "Project configuration requires version 1.0."
            raise ValueError(message)
        return version

    def to_yaml(self) -> bytes:
        """Render a UTF-8 native configuration document."""
        return yaml.safe_dump(data=self.model_dump(), sort_keys=False).encode(
            encoding="utf-8"
        )


def _is_mapping(value: object, /) -> TypeIs[dict[object, object]]:
    """Check whether a YAML root is a dictionary."""
    return isinstance(value, dict)


@beartype
def validate_project_configuration(*, configuration: bytes) -> None:
    """Require a native version-one mapping without limiting future
    keys.
    """
    try:
        document: object = yaml.safe_load(
            stream=configuration.decode(encoding="utf-8")
        )
    except (UnicodeError, yaml.YAMLError):
        message = "Project configuration must contain valid UTF-8 YAML."
        raise ValueError(message) from None
    if (
        not _is_mapping(document)
        or isinstance(document.get("version"), bool)
        or document.get("version") != _CONFIGURATION_VERSION
        or not isinstance(document.get("configuration"), dict)
    ):
        message = (
            "Project configuration requires version 1.0 "
            "and a configuration mapping."
        )
        raise ValueError(message)


@beartype
def configure_project_archive(
    *, archive: bytes, configuration: bytes
) -> bytes:
    """Replace the root native configuration, preserving other ZIP entries.

    Return a ZIP containing one root ``hackerrank.yml`` entry with the
    supplied UTF-8 configuration bytes. Other entries keep their contents
    and metadata. Invalid YAML, invalid ZIPs, and repeated names raise
    ValueError.
    """
    validate_project_configuration(configuration=configuration)
    with BytesIO() as buffer:
        try:
            with (
                ZipFile(file=BytesIO(initial_bytes=archive)) as original,
                ZipFile(
                    file=buffer, mode="w", compression=ZIP_DEFLATED
                ) as output,
            ):
                names = original.namelist()
                if len(names) != len(set(names)):
                    message = "Project archive contains duplicate entries."
                    raise ValueError(message)
                for entry in original.infolist():
                    if entry.filename != "hackerrank.yml":
                        output.writestr(
                            zinfo_or_arcname=entry,
                            data=original.read(name=entry),
                        )
                output.writestr(
                    zinfo_or_arcname="hackerrank.yml", data=configuration
                )
        except BadZipFile:
            message = "Project archive must be a valid ZIP file."
            raise ValueError(message) from None
        return buffer.getvalue()
