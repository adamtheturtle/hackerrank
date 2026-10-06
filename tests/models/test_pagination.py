"""Tests for `hackerrank` pagination models."""

from hackerrank.types import (
    Page,
    SCIMPage,
)


def test_page_construct_empty() -> None:
    """An empty ``Page`` exposes pagination metadata."""
    page: Page[int] = Page(
        page_total=0,
        offset=0,
        previous="",
        next_="",
        first="",
        last="",
        total=0,
    )
    assert page.total == 0
    assert not bool(page.data)


def test_construct_with_items() -> None:
    """Items pass through ``Page`` as a list."""
    expected_items = [1, 2, 3]
    expected_total = len(expected_items)
    page: Page[int] = Page(
        expected_items,
        page_total=expected_total,
        offset=0,
        previous="",
        next_="",
        first="",
        last="",
        total=expected_total,
    )
    assert list(page) == expected_items
    assert page.data == expected_items
    assert page.total == expected_total


def test_scim_page_construct_empty() -> None:
    """An empty ``SCIMPage`` exposes SCIM metadata."""
    page: SCIMPage[int] = SCIMPage(
        schemas=[],
        start_index=1,
        items_per_page=0,
        total_results=0,
    )
    assert page.total_results == 0
    assert page.start_index == 1
