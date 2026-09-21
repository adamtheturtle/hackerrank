"""Types shared by request transports and retry handling."""

from collections.abc import Mapping
from typing import BinaryIO

type MultipartContent = BinaryIO | bytes
type MultipartFile = tuple[str, MultipartContent, str]
type MultipartFiles = Mapping[str, MultipartFile] | None
