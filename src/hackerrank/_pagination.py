"""Shared offset pagination for inventory resources."""

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator

from hackerrank.exceptions import PaginationError
from hackerrank.types import InterviewTemplate, Page, Question, Team

type InventoryItem = Question | InterviewTemplate | Team


def _next_offset[Item: InventoryItem](
    *, page: Page[Item], offset: int
) -> int | None:
    """Stop at an empty or complete page, rejecting unreachable
    results.
    """
    if page.offset_window_exhausted is True:
        message = (
            "The API offset window is exhausted; narrow the listing filters."
        )
        raise PaginationError(message)
    if len(page) == 0:
        return None
    following = offset + len(page)
    if 0 < page.total <= following:
        return None
    if (
        page.offset_window_limit is not None
        and following >= page.offset_window_limit
    ):
        message = (
            "The API offset window cannot reach all results. "
            "Narrow the listing filters."
        )
        raise PaginationError(message)
    return following


def iter_items[Item: InventoryItem](
    *, fetch: Callable[[int], Page[Item]], page_size: int
) -> Iterator[Item]:
    """Read every reachable item without silently accepting a repeated
    page.
    """
    if page_size <= 0:
        message = "page_size must be positive."
        raise ValueError(message)
    offset = 0
    previous: frozenset[str] | None = None
    while True:
        page = fetch(offset)
        identities = frozenset(item.id for item in page)
        if previous is not None and identities == previous:
            message = "The API repeated a page; pagination did not advance."
            raise PaginationError(message)
        yield from page
        following = _next_offset(page=page, offset=offset)
        if following is None:
            return
        previous = identities
        offset = following


async def async_iter_items[Item: InventoryItem](
    *, fetch: Callable[[int], Awaitable[Page[Item]]], page_size: int
) -> AsyncIterator[Item]:
    """Read every reachable item through an asynchronous page fetcher."""
    if page_size <= 0:
        message = "page_size must be positive."
        raise ValueError(message)
    offset = 0
    previous: frozenset[str] | None = None
    while True:
        page = await fetch(offset)
        identities = frozenset(item.id for item in page)
        if previous is not None and identities == previous:
            message = "The API repeated a page; pagination did not advance."
            raise PaginationError(message)
        for item in page:
            yield item
        following = _next_offset(page=page, offset=offset)
        if following is None:
            return
        previous = identities
        offset = following
