"""Request-shape tests for newly documented query/body fields."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank

if TYPE_CHECKING:
    from collections.abc import Mapping

    from hackerrank.types import JSONValue

_BASE = "https://www.hackerrank.com/x/api/v3"
_EMPTY_DATA: list[object] = []
_PAGE: dict[str, object] = {
    "data": _EMPTY_DATA,
    "page_total": 0,
    "offset": 0,
    "previous": "",
    "next": "",
    "first": "",
    "last": "",
    "total": 0,
}
_INTERVIEW = {
    "id": "iv1",
    "status": "new",
    "url": "https://example.com/iv1",
    "title": "Interview",
    "ai_assistant_available": True,
}
_CANDIDATE = {
    "id": "c1",
    "email": "c@x.com",
    "full_name": "Candidate",
}


def _query(*, request: httpx.Request) -> dict[str, str]:
    """Return decoded query parameters for ``request``."""
    return dict(request.url.params)


def _route_request(
    *,
    route: respx.Route,
    index: int | None = None,
) -> httpx.Request:
    """Return a typed ``httpx.Request`` captured by ``route``."""
    # respx call objects are untyped; getattr is the narrowest access.
    calls_obj: object = route.calls
    call_obj: object
    if index is None:
        call_obj = getattr(  # pylint: disable=bad-builtin
            calls_obj,
            "last",
            None,
        )
    else:
        getitem = getattr(  # pylint: disable=bad-builtin
            calls_obj,
            "__getitem__",
            None,
        )
        if not callable(getitem):
            message = "expected respx call list"
            raise TypeError(message)
        call_obj = getitem(index)
    request_obj = getattr(  # pylint: disable=bad-builtin
        call_obj,
        "request",
        None,
    )
    if not isinstance(request_obj, httpx.Request):
        message = "expected httpx.Request from respx call"
        raise TypeError(message)
    return request_obj


def _as_str_keyed_dict(*, value: object) -> dict[str, object] | None:
    """Return ``value`` as a ``str``-keyed dict, or ``None``."""
    if not isinstance(value, dict):
        return None
    result: dict[str, object] = {}
    for key_obj, item in value.items():  # pyright: ignore[reportUnknownVariableType]
        if not isinstance(key_obj, str):
            return None
        result[key_obj] = item
    return result


def _route_json(
    *,
    route: respx.Route,
    index: int | None = None,
) -> dict[str, object]:
    """Return decoded JSON body from a captured ``route`` call."""
    loaded = _as_str_keyed_dict(
        value=json.loads(s=_route_request(route=route, index=index).content),
    )
    if loaded is None:
        message = "expected JSON object body"
        raise TypeError(message)
    return loaded


class TestInterviewListParams:
    """Interview list query parameters."""

    @staticmethod
    def test_sync_sends_documented_filters() -> None:
        """Sync list forwards documented interview filters."""
        with respx.mock(assert_all_called=True) as router:
            route = router.get(url=f"{_BASE}/interviews").respond(
                status_code=200,
                json=_PAGE,
            )
            with HackerRank(api_key="test-key") as client:
                client.interviews.list(
                    user=42,
                    interviewers=7,
                    access="owned",
                    current_status=1,
                    order_by="created_at",
                    order_dir="desc",
                    created_at="2024-01-01..2024-01-02",
                    updated_at="2024-01-01..2024-01-02",
                    ended_at="2024-01-01..2024-01-02",
                )
        params = _query(request=_route_request(route=route))
        assert params["user"] == "42"
        assert params["interviewers"] == "7"
        assert params["access"] == "owned"
        assert params["current_status"] == "1"
        assert params["order_by"] == "created_at"
        assert params["order_dir"] == "desc"
        assert params["created_at"] == "2024-01-01..2024-01-02"
        assert params["updated_at"] == "2024-01-01..2024-01-02"
        assert params["ended_at"] == "2024-01-01..2024-01-02"

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_sends_documented_filters() -> None:
        """Async list forwards documented interview filters."""
        with respx.mock(assert_all_called=True) as router:
            route = router.get(url=f"{_BASE}/interviews").respond(
                status_code=200,
                json=_PAGE,
            )
            async with AsyncHackerRank(api_key="test-key") as client:
                await client.interviews.list(
                    user=42,
                    interviewers=7,
                    access="shared",
                    current_status=2,
                    order_by="title",
                    order_dir="asc",
                    created_at="2024-01-01..2024-01-02",
                    updated_at="2024-01-01..2024-01-02",
                    ended_at="2024-01-01..2024-01-02",
                )
        params = _query(request=_route_request(route=route))
        assert params["user"] == "42"
        assert params["interviewers"] == "7"
        assert params["access"] == "shared"
        assert params["current_status"] == "2"
        assert params["order_by"] == "title"
        assert params["order_dir"] == "asc"
        assert params["created_at"] == "2024-01-01..2024-01-02"
        assert params["updated_at"] == "2024-01-01..2024-01-02"
        assert params["ended_at"] == "2024-01-01..2024-01-02"


class TestQuestionListParams:
    """Question list query parameters."""

    @staticmethod
    def test_sync_sends_documented_filters() -> None:
        """Sync question list joins list filters as CSV."""
        with respx.mock(assert_all_called=True) as router:
            route = router.get(url=f"{_BASE}/questions").respond(
                status_code=200,
                json=_PAGE,
            )
            with HackerRank(api_key="test-key") as client:
                client.questions.list(
                    status="active",
                    access=["owned", "shared"],
                    difficulty=["easy", "hard"],
                    type=["code", "mcq"],
                    owner=["1", "2"],
                    tags=["algo", "ds"],
                    skills=["python"],
                    languages=["python3", "java"],
                )
        params = _query(request=_route_request(route=route))
        assert params["status"] == "active"
        assert params["access"] == "owned,shared"
        assert params["difficulty"] == "easy,hard"
        assert params["type"] == "code,mcq"
        assert params["owner"] == "1,2"
        assert params["tags"] == "algo,ds"
        assert params["skills"] == "python"
        assert params["languages"] == "python3,java"

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_sends_documented_filters() -> None:
        """Async question list joins list filters as CSV."""
        with respx.mock(assert_all_called=True) as router:
            route = router.get(url=f"{_BASE}/questions").respond(
                status_code=200,
                json=_PAGE,
            )
            async with AsyncHackerRank(api_key="test-key") as client:
                await client.questions.list(
                    status="archived",
                    access=["library"],
                    difficulty=["medium"],
                    type=["fullstack"],
                    owner=["9"],
                    tags=["graphs"],
                    skills=["java"],
                    languages=["javascript"],
                )
        params = _query(request=_route_request(route=route))
        assert params["status"] == "archived"
        assert params["access"] == "library"
        assert params["difficulty"] == "medium"
        assert params["type"] == "fullstack"
        assert params["owner"] == "9"
        assert params["tags"] == "graphs"
        assert params["skills"] == "java"
        assert params["languages"] == "javascript"


class TestTemplateListParams:
    """Interview-template and invite-template list filters."""

    @staticmethod
    def test_sync_interview_template_filter() -> None:
        """Sync interview-template list sends ``filter``."""
        with respx.mock(assert_all_called=True) as router:
            route = router.get(
                url=f"{_BASE}/interview_templates",
            ).respond(status_code=200, json=_PAGE)
            with HackerRank(api_key="test-key") as client:
                client.interview_templates.list(filter="owned")
                client.interview_templates.list(filter="shared")
        assert (
            _query(request=_route_request(route=route, index=0))["filter"]
            == "owned"
        )
        assert (
            _query(request=_route_request(route=route, index=1))["filter"]
            == "shared"
        )

    @staticmethod
    def test_sync_invite_template_access() -> None:
        """Sync invite-template list sends ``access``."""
        with respx.mock(assert_all_called=True) as router:
            route = router.get(url=f"{_BASE}/templates").respond(
                status_code=200,
                json=_PAGE,
            )
            with HackerRank(api_key="test-key") as client:
                client.templates.list(access="owned")
                client.templates.list(access="shared")
                client.templates.list()
        assert (
            _query(request=_route_request(route=route, index=0))["access"]
            == "owned"
        )
        assert (
            _query(request=_route_request(route=route, index=1))["access"]
            == "shared"
        )
        assert "access" not in _query(
            request=_route_request(route=route, index=2)
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_template_filters() -> None:
        """Async template lists send documented filters."""
        with respx.mock(assert_all_called=True) as router:
            interview_route = router.get(
                url=f"{_BASE}/interview_templates",
            ).respond(status_code=200, json=_PAGE)
            invite_route = router.get(
                url=f"{_BASE}/templates",
            ).respond(status_code=200, json=_PAGE)
            async with AsyncHackerRank(api_key="test-key") as client:
                await client.interview_templates.list(filter="owned")
                await client.templates.list(access="shared")
        interview_request = _route_request(route=interview_route)
        interview_params = _query(request=interview_request)
        assert interview_params["filter"] == "owned"
        invite_request = _route_request(route=invite_route)
        invite_params = _query(request=invite_request)
        assert invite_params["access"] == "shared"


class TestInterviewBodyFields:
    """Interview create/update body fields."""

    @staticmethod
    def test_sync_create_ai_assistant() -> None:
        """Sync create sends ``ai_assistant_available``."""
        with respx.mock(assert_all_called=True) as router:
            route = router.post(url=f"{_BASE}/interviews").respond(
                status_code=200,
                json=_INTERVIEW,
            )
            with HackerRank(api_key="test-key") as client:
                created = client.interviews.create(
                    title="AI interview",
                    ai_assistant_available=True,
                )
        body = _route_json(route=route)
        assert body["ai_assistant_available"] is True
        assert created.ai_assistant_available is True

    @staticmethod
    def test_sync_update_interviewers_and_ai() -> None:
        """Sync update sends interviewers, replace flag, and AI."""
        with respx.mock(assert_all_called=True) as router:
            route = router.put(url=f"{_BASE}/interviews/iv1").respond(
                status_code=200,
                json={},
            )
            with HackerRank(api_key="test-key") as client:
                client.interviews.update(
                    interview_id="iv1",
                    interviewers=["a@b.com"],
                    replace_interviewers=True,
                    ai_assistant_available=False,
                )
                object_interviewers: list[Mapping[str, JSONValue]] = [
                    {"email": "a@b.com", "name": "Ada"},
                ]
                client.interviews.update(
                    interview_id="iv1",
                    interviewers=object_interviewers,
                    replace_interviewers=False,
                    ai_assistant_available=True,
                )
        first = _route_json(route=route, index=0)
        second = _route_json(route=route, index=1)
        assert first["interviewers"] == ["a@b.com"]
        assert first["replace_interviewers"] is True
        assert first["ai_assistant_available"] is False
        assert second["interviewers"] == [
            {"email": "a@b.com", "name": "Ada"},
        ]
        assert second["replace_interviewers"] is False
        assert second["ai_assistant_available"] is True

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_create_and_update_fields() -> None:
        """Async create/update send documented interview fields."""
        with respx.mock(assert_all_called=True) as router:
            create_route = router.post(
                url=f"{_BASE}/interviews",
            ).respond(status_code=200, json=_INTERVIEW)
            update_route = router.put(
                url=f"{_BASE}/interviews/iv1",
            ).respond(status_code=200, json={})
            async with AsyncHackerRank(api_key="test-key") as client:
                created = await client.interviews.create(
                    title="AI interview",
                    ai_assistant_available=True,
                )
                await client.interviews.update(
                    interview_id="iv1",
                    interviewers=["a@b.com"],
                    replace_interviewers=True,
                    ai_assistant_available=False,
                )
        create_body = _route_json(route=create_route)
        update_body = _route_json(route=update_route)
        assert create_body["ai_assistant_available"] is True
        assert created.ai_assistant_available is True
        assert update_body["interviewers"] == ["a@b.com"]
        assert update_body["replace_interviewers"] is True
        assert update_body["ai_assistant_available"] is False


class TestCandidateInviteAtsState:
    """Candidate invite ``ats_state`` body field."""

    @staticmethod
    def test_sync_invite_sends_ats_state() -> None:
        """Sync invite serializes ``ats_state``."""
        with respx.mock(assert_all_called=True) as router:
            route = router.post(
                url=f"{_BASE}/tests/t1/candidates",
            ).respond(status_code=200, json=_CANDIDATE)
            first_ats_state = 0
            second_ats_state = 22
            with HackerRank(api_key="test-key") as client:
                client.tests.candidates.invite(
                    test_id="t1",
                    email="c@x.com",
                    ats_state=first_ats_state,
                )
                client.tests.candidates.invite(
                    test_id="t1",
                    email="c@x.com",
                    ats_state=second_ats_state,
                )
        assert (
            _route_json(route=route, index=0)["ats_state"] == first_ats_state
        )
        assert (
            _route_json(route=route, index=1)["ats_state"] == second_ats_state
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_invite_sends_ats_state() -> None:
        """Async invite serializes ``ats_state``."""
        with respx.mock(assert_all_called=True) as router:
            route = router.post(
                url=f"{_BASE}/tests/t1/candidates",
            ).respond(status_code=200, json=_CANDIDATE)
            async_ats_state = 5
            async with AsyncHackerRank(api_key="test-key") as client:
                await client.tests.candidates.invite(
                    test_id="t1",
                    email="c@x.com",
                    ats_state=async_ats_state,
                )
        assert _route_json(route=route)["ats_state"] == async_ats_state
