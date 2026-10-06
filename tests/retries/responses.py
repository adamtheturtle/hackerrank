"""Response builders and example bodies for retry tests."""

from hackerrank.transports import TransportResponse

PAGE_BODY = (
    b'{"data": [], "page_total": 0, "offset": 0, "previous": "",'
    b' "next": "", "first": "", "last": "", "total": 0}'
)


ZIP_BODY = b'{"file_url": "https://example.com/project.zip"}'


def response(
    *,
    status_code: int,
    headers: dict[str, str],
    content: bytes,
) -> TransportResponse:
    """Build a transport response.

    Args:
        status_code: The HTTP status code.
        headers: The response headers.
        content: The response body.

    Returns:
        The transport response.
    """
    return TransportResponse(
        status_code=status_code,
        headers=headers,
        content=content,
    )


def ok(*, content: bytes) -> TransportResponse:
    """Build a ``200 OK`` transport response.

    Args:
        content: The response body.

    Returns:
        The transport response.
    """
    return response(status_code=200, headers={}, content=content)


def error(*, status_code: int) -> TransportResponse:
    """Build an error transport response with no headers.

    Args:
        status_code: The HTTP status code.

    Returns:
        The transport response.
    """
    return response(status_code=status_code, headers={}, content=b"{}")
