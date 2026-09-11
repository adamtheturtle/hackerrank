"""Request-shape tests for newly documented query/body fields."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
import respx
from beartype import beartype

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.types import JSONValue

if TYPE_CHECKING:
    from collections.abc import Mapping

    import httpx

_BASE = "https://www.hackerrank.com/x/api/v3"
_EMPTY_DATA: list[JSONValue] = []
_PAGE: dict[str, JSONValue] = {
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
_CANDIDATE_INVITE = {
    "id": "c1",
    "email": "c@x.com",
    "test_link": "https://example.com/invite/c1",
}


def _query(*, request: httpx.Request) -> dict[str, str]:
    """Return decoded query parameters for ``request``."""
    return dict(request.url.params)


def _last_route_request(*, route: respx.Route) -> httpx.Request:
    """Return the last typed ``httpx.Request`` captured by ``route``."""
    call: object = route.calls.last
    assert isinstance(call, respx.models.Call)
    return call.request


@beartype
def _as_json_object(*, value: dict[str, JSONValue]) -> dict[str, JSONValue]:
    """Return ``value`` as a runtime-validated JSON object."""
    return value


def _last_route_json(*, route: respx.Route) -> dict[str, JSONValue]:
    """Return decoded JSON body from the last captured ``route`` call."""
    return _as_json_object(
        value=json.loads(s=_last_route_request(route=route).content),
    )


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
                _ = client.interviews.list(
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
        params = _query(request=_last_route_request(route=route))
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
        params = _query(request=_last_route_request(route=route))
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
                _ = client.questions.list(
                    status="active",
                    access=["owned", "shared"],
                    difficulty=["easy", "hard"],
                    type=["code", "mcq"],
                    owner=["1", "2"],
                    tags=["algo", "ds"],
                    skills=["python"],
                    languages=["python3", "java"],
                )
        params = _query(request=_last_route_request(route=route))
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
        params = _query(request=_last_route_request(route=route))
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
                _ = client.interview_templates.list(filter="owned")
                first = _query(request=_last_route_request(route=route))
                _ = client.interview_templates.list(filter="shared")
                second = _query(request=_last_route_request(route=route))
        assert first["filter"] == "owned"
        assert second["filter"] == "shared"

    @staticmethod
    def test_sync_invite_template_access() -> None:
        """Sync invite-template list sends ``access``."""
        with respx.mock(assert_all_called=True) as router:
            route = router.get(url=f"{_BASE}/templates").respond(
                status_code=200,
                json=_PAGE,
            )
            with HackerRank(api_key="test-key") as client:
                _ = client.templates.list(access="owned")
                first = _query(request=_last_route_request(route=route))
                _ = client.templates.list(access="shared")
                second = _query(request=_last_route_request(route=route))
                _ = client.templates.list()
                third = _query(request=_last_route_request(route=route))
        assert first["access"] == "owned"
        assert second["access"] == "shared"
        assert "access" not in third

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
        interview_request = _last_route_request(route=interview_route)
        interview_params = _query(request=interview_request)
        assert interview_params["filter"] == "owned"
        invite_request = _last_route_request(route=invite_route)
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
        body = _last_route_json(route=route)
        assert body["ai_assistant_available"] is True
        assert created.ai_assistant_available is True

    @staticmethod
    def test_sync_update_interviewers_and_ai() -> None:
        """Sync update sends interviewers, replace flag, and AI."""
        with respx.mock(assert_all_called=True) as router:
            route = router.put(url=f"{_BASE}/interviews/iv1").respond(
                status_code=200,
                json=_INTERVIEW,
            )
            with HackerRank(api_key="test-key") as client:
                _ = client.interviews.update(
                    interview_id="iv1",
                    title="t",
                    from_="2024",
                    to="2024",
                    notes="n",
                    resume_url="r",
                    result_url="rr",
                    candidate={"email": "c@x.com"},
                    send_email=True,
                    metadata={"x": "y"},
                    interview_template_id=1,
                    interviewers=["a@b.com"],
                    replace_interviewers=True,
                    ai_assistant_available=False,
                )
                first = _last_route_json(route=route)
                object_interviewers: list[Mapping[str, JSONValue]] = [
                    {"email": "a@b.com", "name": "Ada"},
                ]
                _ = client.interviews.update(
                    interview_id="iv1",
                    title="t",
                    from_="2024",
                    to="2024",
                    notes="n",
                    resume_url="r",
                    result_url="rr",
                    candidate={"email": "c@x.com"},
                    send_email=True,
                    metadata={"x": "y"},
                    interview_template_id=1,
                    interviewers=object_interviewers,
                    replace_interviewers=False,
                    ai_assistant_available=True,
                )
                second = _last_route_json(route=route)
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
            ).respond(status_code=200, json=_INTERVIEW)
            async with AsyncHackerRank(api_key="test-key") as client:
                created = await client.interviews.create(
                    title="AI interview",
                    ai_assistant_available=True,
                )
                await client.interviews.update(
                    interview_id="iv1",
                    title="t",
                    from_="2024",
                    to="2024",
                    notes="n",
                    resume_url="r",
                    result_url="rr",
                    candidate={"email": "c@x.com"},
                    send_email=True,
                    metadata={"x": "y"},
                    interview_template_id=1,
                    interviewers=["a@b.com"],
                    replace_interviewers=True,
                    ai_assistant_available=False,
                )
        create_body = _last_route_json(route=create_route)
        update_body = _last_route_json(route=update_route)
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
            ).respond(status_code=200, json=_CANDIDATE_INVITE)
            first_ats_state = 0
            second_ats_state = 22
            with HackerRank(api_key="test-key") as client:
                _ = client.tests.candidates.invite(
                    test_id="t1",
                    email="c@x.com",
                    ats_state=first_ats_state,
                )
                first_body = _last_route_json(route=route)
                _ = client.tests.candidates.invite(
                    test_id="t1",
                    email="c@x.com",
                    ats_state=second_ats_state,
                )
                second_body = _last_route_json(route=route)
        assert first_body["ats_state"] == first_ats_state
        assert second_body["ats_state"] == second_ats_state

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_invite_sends_ats_state() -> None:
        """Async invite serializes ``ats_state``."""
        with respx.mock(assert_all_called=True) as router:
            route = router.post(
                url=f"{_BASE}/tests/t1/candidates",
            ).respond(status_code=200, json=_CANDIDATE_INVITE)
            async_ats_state = 5
            async with AsyncHackerRank(api_key="test-key") as client:
                await client.tests.candidates.invite(
                    test_id="t1",
                    email="c@x.com",
                    ats_state=async_ats_state,
                )
        assert _last_route_json(route=route)["ats_state"] == async_ats_state
