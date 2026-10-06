"""Scripted transports for retry tests."""

import io
from collections.abc import Iterator, Mapping, Sequence

from hackerrank._request_types import MultipartFiles
from hackerrank.transports import TransportResponse
from hackerrank.types import JSONValue


def file_parts(*, files: MultipartFiles) -> Iterator[object]:
    """Yield each part of a multipart ``files`` mapping.

    The client only ever sends the ``(filename, file, content_type)``
    tuple which ``httpx`` expects, so that is all this handles.

    Args:
        files: Files sent as multipart form-data.

    Yields:
        Each element of each value.
    """
    if files is None:
        return
    for value in files.values():
        yield from value


class ScriptedCalls:
    """Shared recording and scripting for the test transports.

    The last entry of the script is repeated for any further calls,
    so a script of one item describes an endpoint which always
    behaves the same way.
    """

    def __init__(
        self,
        *,
        script: Sequence[TransportResponse | Exception],
    ) -> None:
        """Create a scripted transport.

        Args:
            script: The results to return or raise, in order.
        """
        self._script = list(script)
        self.methods: list[str] = []
        self.urls: list[str] = []
        self.file_contents: list[bytes] = []

    def _next(
        self,
        *,
        method: str,
        url: str,
        files: MultipartFiles,
    ) -> TransportResponse:
        """Record a call and return its scripted result.

        Args:
            method: The HTTP method.
            url: The full URL.
            files: Files to send as multipart form-data.

        Returns:
            The scripted response.

        Raises:
            Exception: Whatever the script says to raise.
        """
        index = min(len(self.methods), len(self._script) - 1)
        self.methods.append(method)
        self.urls.append(url)
        for part in file_parts(files=files):
            if isinstance(part, io.IOBase):
                self.file_contents.append(part.read())
            elif isinstance(part, bytes):
                self.file_contents.append(part)
        result = self._script[index]
        if isinstance(result, Exception):
            raise result
        return result


class ScriptedTransport(ScriptedCalls):
    """A transport which replays a script of results, in order."""

    def __call__(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        params: dict[str, str | int] | None,
        json: Mapping[str, JSONValue] | None,
        files: MultipartFiles,
    ) -> TransportResponse:
        """Make a scripted request.

        Args:
            method: The HTTP method.
            url: The full URL.
            headers: Request headers.
            params: Query parameters.
            json: A JSON-serialisable body.
            files: Files to send as multipart form-data.

        Returns:
            The scripted response.
        """
        del headers, params, json
        return self._next(method=method, url=url, files=files)
