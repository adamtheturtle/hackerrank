"""Inventory iterators preserve query intent and detect incomplete results."""

from collections.abc import AsyncIterator, Iterator, Sequence
from typing import TypedDict

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.exceptions import HackerRankError, PaginationError
from hackerrank.types import InterviewTemplate, JSONValue, Question, Team

type Resource = Question | InterviewTemplate | Team

_RESOURCES = ["questions", "interview_templates", "teams"]
_BASE = "https://www.hackerrank.com/x/api/v3/"
_PAGE_SIZE = 3


def _rows(
    *, resource: str, identifiers: list[str]
) -> list[dict[str, JSONValue]]:
    """Supply the minimum valid representation of each resource."""
    rows: list[dict[str, JSONValue]] = []
    for identifier in identifiers:
        row: dict[str, JSONValue] = {
            "id": identifier,
            "name": "Record " + identifier,
        }
        if resource == "questions":
            row.update({"type": "mcq", "answer": "0"})
        rows.append(row)
    return rows


def _sync_iterator(
    *, client: HackerRank, resource: str, page_size: int, filtered: bool
) -> Iterator[Resource]:
    """Select a public inventory iterator without replacing client methods."""
    if resource == "questions":
        return client.questions.iter_all(
            page_size=page_size, status="active" if filtered else None
        )
    if resource == "interview_templates":
        return client.interview_templates.iter_all(
            page_size=page_size, filter="shared" if filtered else None
        )
    return client.teams.iter_all(page_size=page_size)


def _async_iterator(
    *, client: AsyncHackerRank, resource: str, page_size: int, filtered: bool
) -> AsyncIterator[Resource]:
    """Select the corresponding public asynchronous iterator."""
    if resource == "questions":
        return client.questions.iter_all(
            page_size=page_size, status="active" if filtered else None
        )
    if resource == "interview_templates":
        return client.interview_templates.iter_all(
            page_size=page_size, filter="shared" if filtered else None
        )
    return client.teams.iter_all(page_size=page_size)


async def _collect(
    *, asynchronous: bool, resource: str, page_size: int, filtered: bool
) -> list[Resource]:
    """Consume inventory through the selected public client."""
    if asynchronous:
        async with AsyncHackerRank(api_key="synthetic") as client:
            return [
                item
                async for item in _async_iterator(
                    client=client,
                    resource=resource,
                    page_size=page_size,
                    filtered=filtered,
                )
            ]
    with HackerRank(api_key="synthetic") as sync_client:
        return list(
            _sync_iterator(
                client=sync_client,
                resource=resource,
                page_size=page_size,
                filtered=filtered,
            )
        )


def _requests(*, calls: Sequence[object]) -> list[httpx.Request]:
    """Narrow the HTTP recorder at its untyped collection boundary."""
    requests: list[httpx.Request] = []
    for call in calls:
        assert isinstance(call, respx.models.Call)
        requests.append(call.request)
    return requests


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(argnames="resource", argvalues=_RESOURCES)
@pytest.mark.parametrize(argnames="filtered", argvalues=[False, True])
@pytest.mark.parametrize(argnames="totals", argvalues=[True, False])
async def test_short_pages_preserve_all_results_and_filters(
    *, asynchronous: bool, resource: str, filtered: bool, totals: bool
) -> None:
    """Offsets advance by actual records, including pages below the
    limit.
    """
    identifiers = [["1"], ["2", "3"]]
    payloads: list[dict[str, JSONValue]] = []
    for values in identifiers:
        payload: dict[str, JSONValue] = {
            "data": _rows(resource=resource, identifiers=values),
            "next": "https://other.example/never-follow",
        }
        if totals:
            payload["total"] = "3"
        payloads.append(payload)
    expected_offsets = [0, 1]
    if not totals:
        payloads.append({"data": []})
        expected_offsets.append(len(["1", "2", "3"]))
    with respx.mock(assert_all_called=True) as router:
        route = router.get(url=_BASE + resource).mock(
            side_effect=[
                httpx.Response(status_code=200, json=payload)
                for payload in payloads
            ]
        )
        results = await _collect(
            asynchronous=asynchronous,
            resource=resource,
            page_size=_PAGE_SIZE,
            filtered=filtered,
        )
        assert [result.id for result in results] == ["1", "2", "3"]
        assert route.call_count == len(expected_offsets)
        requests = _requests(calls=router.calls)
        assert [
            int(request.url.params["offset"]) for request in requests
        ] == expected_offsets
        for request in requests:
            assert request.url.params["limit"] == str(object=_PAGE_SIZE)
            expected = (
                {"status": "active"}
                if resource == "questions"
                else (
                    {"filter": "shared"}
                    if resource == "interview_templates"
                    else {}
                )
            )
            for key, value in expected.items():
                if filtered:
                    assert request.url.params[key] == value
                else:
                    assert key not in request.url.params
            assert request.url.host == "www.hackerrank.com"
            assert request.headers["Authorization"] == "Bearer synthetic"


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(argnames="resource", argvalues=_RESOURCES)
@pytest.mark.parametrize(argnames="empty_first", argvalues=[False, True])
async def test_empty_page_ends_an_overstated_total(
    *, asynchronous: bool, resource: str, empty_first: bool
) -> None:
    """An empty API page terminates even if its total is stale."""
    payloads: list[dict[str, JSONValue]] = [{"data": [], "total": 100}]
    expected_ids: list[str] = []
    if not empty_first:
        payloads.insert(
            0,
            {
                "data": _rows(resource=resource, identifiers=["1"]),
                "total": 100,
            },
        )
        expected_ids.append("1")
    with respx.mock(assert_all_called=True) as router:
        route = router.get(url=_BASE + resource).mock(
            side_effect=[
                httpx.Response(status_code=200, json=payload)
                for payload in payloads
            ]
        )
        results = await _collect(
            asynchronous=asynchronous,
            resource=resource,
            page_size=_PAGE_SIZE,
            filtered=False,
        )
        assert [result.id for result in results] == expected_ids
        assert route.call_count == len(payloads)


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(argnames="resource", argvalues=_RESOURCES)
@pytest.mark.parametrize(argnames="empty", argvalues=[False, True])
async def test_exhausted_window_is_an_explicit_failure(
    *, asynchronous: bool, resource: str, empty: bool
) -> None:
    """Window exhaustion cannot be reported as a complete inventory."""
    payload = {
        "data": _rows(resource=resource, identifiers=[] if empty else ["1"]),
        "total": 100,
        "offset_window_exhausted": True,
    }
    with respx.mock(assert_all_called=True) as router:
        route = router.get(url=_BASE + resource).respond(
            status_code=200, json=payload
        )
        with pytest.raises(
            expected_exception=PaginationError, match="offset window"
        ):
            _ = await _collect(
                asynchronous=asynchronous,
                resource=resource,
                page_size=_PAGE_SIZE,
                filtered=False,
            )
        assert route.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(argnames="resource", argvalues=_RESOURCES)
@pytest.mark.parametrize(argnames="complete", argvalues=[False, True])
async def test_window_limit_stops_only_incomplete_inventory(
    *, asynchronous: bool, resource: str, complete: bool
) -> None:
    """Reaching the declared total at the window boundary is valid."""
    payload = {
        "data": _rows(resource=resource, identifiers=["1"]),
        "total": 1 if complete else 100,
        "offset_window_limit": 1,
        "offset_window_exhausted": False,
    }
    with respx.mock(assert_all_called=True) as router:
        route = router.get(url=_BASE + resource).respond(
            status_code=200, json=payload
        )
        if complete:
            results = await _collect(
                asynchronous=asynchronous,
                resource=resource,
                page_size=_PAGE_SIZE,
                filtered=False,
            )
            assert [result.id for result in results] == ["1"]
        else:
            with pytest.raises(
                expected_exception=PaginationError, match="offset window"
            ):
                _ = await _collect(
                    asynchronous=asynchronous,
                    resource=resource,
                    page_size=_PAGE_SIZE,
                    filtered=False,
                )
        assert route.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(argnames="resource", argvalues=_RESOURCES)
async def test_repeated_identities_stop_pagination(
    *, asynchronous: bool, resource: str
) -> None:
    """Changing record fields does not disguise a repeated page."""
    first = {"data": _rows(resource=resource, identifiers=["1"])}
    repeated = {"data": [{**first["data"][0], "name": "Renamed"}]}
    with respx.mock(assert_all_called=True) as router:
        route = router.get(url=_BASE + resource).mock(
            side_effect=[
                httpx.Response(status_code=200, json=first),
                httpx.Response(status_code=200, json=repeated),
            ]
        )
        with pytest.raises(
            expected_exception=PaginationError, match="repeated"
        ):
            _ = await _collect(
                asynchronous=asynchronous,
                resource=resource,
                page_size=_PAGE_SIZE,
                filtered=False,
            )
        assert route.call_count == len([first, repeated])


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(argnames="resource", argvalues=_RESOURCES)
@pytest.mark.parametrize(argnames="page_size", argvalues=[0, -1])
async def test_invalid_page_size_prevents_requests(
    *, asynchronous: bool, resource: str, page_size: int
) -> None:
    """Invalid limits fail before fetching the first page."""
    with respx.mock(assert_all_called=True) as router:
        with pytest.raises(
            expected_exception=ValueError, match="page_size must be positive"
        ):
            _ = await _collect(
                asynchronous=asynchronous,
                resource=resource,
                page_size=page_size,
                filtered=False,
            )
        assert len(router.calls) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(argnames="resource", argvalues=_RESOURCES)
async def test_page_error_is_not_hidden(
    *, asynchronous: bool, resource: str
) -> None:
    """An API failure after a page propagates to the caller."""
    first = {"data": _rows(resource=resource, identifiers=["1"]), "total": 100}
    with respx.mock(assert_all_called=True) as router:
        route = router.get(url=_BASE + resource).mock(
            side_effect=[
                httpx.Response(status_code=200, json=first),
                httpx.Response(status_code=403),
            ]
        )
        with pytest.raises(expected_exception=HackerRankError):
            _ = await _collect(
                asynchronous=asynchronous,
                resource=resource,
                page_size=_PAGE_SIZE,
                filtered=False,
            )
        assert route.call_count == len(["first", "failure"])


class _QuestionFilters(TypedDict):
    """The mutable filters accepted by the question listing API."""

    access: list[str]
    difficulty: list[str]
    type: list[str]
    owner: list[str]
    tags: list[str]
    skills: list[str]
    languages: list[str]


def _clear_filters(*, filters: _QuestionFilters) -> None:
    """Change caller-owned lists after an iterator has been created."""
    filters["access"].clear()
    filters["difficulty"].clear()
    filters["type"].clear()
    filters["owner"].clear()
    filters["tags"].clear()
    filters["skills"].clear()
    filters["languages"].clear()


async def _filtered_questions(
    *, asynchronous: bool, filters: _QuestionFilters
) -> list[Question]:
    """Mutate the source filters before consuming the lazy iterator."""
    if asynchronous:
        async with AsyncHackerRank(api_key="synthetic") as client:
            iterator = client.questions.iter_all(
                page_size=1,
                status="active",
                access=filters["access"],
                difficulty=filters["difficulty"],
                type=filters["type"],
                owner=filters["owner"],
                tags=filters["tags"],
                skills=filters["skills"],
                languages=filters["languages"],
            )
            _clear_filters(filters=filters)
            return [question async for question in iterator]
    with HackerRank(api_key="synthetic") as sync_client:
        sync_iterator = sync_client.questions.iter_all(
            page_size=1,
            status="active",
            access=filters["access"],
            difficulty=filters["difficulty"],
            type=filters["type"],
            owner=filters["owner"],
            tags=filters["tags"],
            skills=filters["skills"],
            languages=filters["languages"],
        )
        _clear_filters(filters=filters)
        return list(sync_iterator)


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
async def test_question_filter_lists_are_copied_at_creation(
    *, asynchronous: bool
) -> None:
    """Caller changes cannot alter query values between inventory
    pages.
    """
    filters: _QuestionFilters = {
        "access": ["owned", "shared"],
        "difficulty": ["easy", "medium"],
        "type": ["mcq"],
        "owner": ["u1"],
        "tags": ["python", "backend"],
        "skills": ["algorithms"],
        "languages": ["python3", "go"],
    }
    expected = {
        "limit": "1",
        "status": "active",
        "access": "owned,shared",
        "difficulty": "easy,medium",
        "type": "mcq",
        "owner": "u1",
        "tags": "python,backend",
        "skills": "algorithms",
        "languages": "python3,go",
    }
    payloads = [
        {
            "data": _rows(resource="questions", identifiers=[identifier]),
            "total": 2,
        }
        for identifier in ["1", "2"]
    ]
    with respx.mock(assert_all_called=True) as router:
        route = router.get(url=_BASE + "questions").mock(
            side_effect=[
                httpx.Response(status_code=200, json=payload)
                for payload in payloads
            ]
        )
        questions = await _filtered_questions(
            asynchronous=asynchronous, filters=filters
        )
        assert [question.id for question in questions] == ["1", "2"]
        assert route.call_count == len(payloads)
        for offset, request in enumerate(
            iterable=_requests(calls=router.calls)
        ):
            assert dict(request.url.params) == {
                **expected,
                "offset": str(object=offset),
            }


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
@pytest.mark.parametrize(argnames="resource", argvalues=_RESOURCES)
async def test_iteration_is_lazy(*, asynchronous: bool, resource: str) -> None:
    """Creating an iterator and taking one item never fetches later
    pages.
    """
    payload = {
        "data": _rows(resource=resource, identifiers=["1", "2"]),
        "total": 100,
    }
    with respx.mock(assert_all_called=True) as router:
        route = router.get(url=_BASE + resource).respond(
            status_code=200, json=payload
        )
        if asynchronous:
            async with AsyncHackerRank(api_key="synthetic") as client:
                iterator = _async_iterator(
                    client=client,
                    resource=resource,
                    page_size=_PAGE_SIZE,
                    filtered=False,
                )
                assert len(router.calls) == 0
                first = await anext(iterator)
        else:
            with HackerRank(api_key="synthetic") as sync_client:
                sync_iterator = _sync_iterator(
                    client=sync_client,
                    resource=resource,
                    page_size=_PAGE_SIZE,
                    filtered=False,
                )
                assert len(router.calls) == 0
                first = next(sync_iterator)
        assert first.id == "1"
        assert route.call_count == 1
