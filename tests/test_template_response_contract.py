"""Preserve verified template wire types through both clients."""

import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.types import InterviewTemplate, JSONValue

_BASE = "https://www.hackerrank.com/x/api/v3/interview_templates"
_TEMPLATES: list[JSONValue] = [
    {"id": "101", "name": "First", "questions": [201]},
    {"id": "102", "name": "Selected", "questions": [202, 203]},
]
_PAGE: dict[str, JSONValue] = {
    "data": _TEMPLATES,
    "page_total": 2,
    "offset": 0,
    "previous": "",
    "next": f"{_BASE}?offset=2&limit=2",
    "first": f"{_BASE}?offset=0&limit=2",
    "last": f"{_BASE}?offset=2&limit=2",
    "total": 3,
}


def test_sync_template_list_and_show() -> None:
    """Read a selected string ID and numeric membership without
    coercion.
    """
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(url=_BASE).respond(status_code=200, json=_PAGE)
        _ = router.get(url=f"{_BASE}/102").respond(
            status_code=200, json=_TEMPLATES[1]
        )
        with HackerRank(api_key="synthetic") as client:
            page = client.interview_templates.list(limit=2, filter="shared")
            selected = client.interview_templates.get(template_id=page[1].id)
    assert [item.id for item in page] == ["101", "102"]
    assert page[0].questions == [201]
    assert selected == page[1]
    assert selected.questions == [202, 203]
    assert page.next == _PAGE["next"]
    assert page.total == _PAGE["total"]


@pytest.mark.asyncio
async def test_async_template_list_and_show() -> None:
    """The asynchronous decoder follows the same list/show contract."""
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(url=_BASE).respond(status_code=200, json=_PAGE)
        _ = router.get(url=f"{_BASE}/102").respond(
            status_code=200, json=_TEMPLATES[1]
        )
        async with AsyncHackerRank(api_key="synthetic") as client:
            page = await client.interview_templates.list(limit=2)
            selected = await client.interview_templates.get(
                template_id=page[1].id
            )
    assert [item.id for item in page] == ["101", "102"]
    assert page[0].questions == [201]
    assert selected == page[1]
    assert selected.questions == [202, 203]
    assert page.next == _PAGE["next"]
    assert page.total == _PAGE["total"]


def test_template_membership_absent_versus_empty() -> None:
    """An omitted membership is distinct from a known empty template."""
    absent = InterviewTemplate.from_dict(data={"id": "101", "name": "Absent"})
    empty = InterviewTemplate.from_dict(
        data={"id": "102", "name": "Empty", "questions": []}
    )
    assert absent.questions is None
    assert empty.questions == []
