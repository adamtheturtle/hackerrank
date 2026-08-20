"""Request-shape tests for newly documented query/body fields."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank

_BASE = "https://www.hackerrank.com/x/api/v3"
_PAGE = {
    "data": [],
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


def _query(request: httpx.Request) -> dict[str, str]:
    """Return decoded query parameters for ``request``."""
    return dict(request.url.params)


class TestInterviewListParams:
    """Interview list query parameters."""

    @staticmethod
    def test_sync_sends_documented_filters() -> None:
        """Sync list forwards documented interview filters."""
        with respx.mock(assert_all_called=True) as router:
            route = router.get(url=f"{_BASE}/interviews").respond(
                200,
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
        params = _query(route.calls.last.request)
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
                200,
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
        params = _query(route.calls.last.request)
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
                200,
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
        params = _query(route.calls.last.request)
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
                200,
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
        params = _query(route.calls.last.request)
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
            ).respond(200, json=_PAGE)
            with HackerRank(api_key="test-key") as client:
                client.interview_templates.list(filter="owned")
                client.interview_templates.list(filter="shared")
        assert _query(route.calls[0].request)["filter"] == "owned"
        assert _query(route.calls[1].request)["filter"] == "shared"

    @staticmethod
    def test_sync_invite_template_access() -> None:
        """Sync invite-template list sends ``access``."""
        with respx.mock(assert_all_called=True) as router:
            route = router.get(url=f"{_BASE}/templates").respond(
                200,
                json=_PAGE,
            )
            with HackerRank(api_key="test-key") as client:
                client.templates.list(access="owned")
                client.templates.list(access="shared")
                client.templates.list()
        assert _query(route.calls[0].request)["access"] == "owned"
        assert _query(route.calls[1].request)["access"] == "shared"
        assert "access" not in _query(route.calls[2].request)

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_template_filters() -> None:
        """Async template lists send documented filters."""
        with respx.mock(assert_all_called=True) as router:
            interview_route = router.get(
                url=f"{_BASE}/interview_templates",
            ).respond(200, json=_PAGE)
            invite_route = router.get(
                url=f"{_BASE}/templates",
            ).respond(200, json=_PAGE)
            async with AsyncHackerRank(api_key="test-key") as client:
                await client.interview_templates.list(filter="owned")
                await client.templates.list(access="shared")
        assert _query(interview_route.calls.last.request)["filter"] == "owned"
        assert _query(invite_route.calls.last.request)["access"] == "shared"


class TestInterviewBodyFields:
    """Interview create/update body fields."""

    @staticmethod
    def test_sync_create_ai_assistant() -> None:
        """Sync create sends ``ai_assistant_available``."""
        with respx.mock(assert_all_called=True) as router:
            route = router.post(url=f"{_BASE}/interviews").respond(
                200,
                json=_INTERVIEW,
            )
            with HackerRank(api_key="test-key") as client:
                created = client.interviews.create(
                    title="AI interview",
                    ai_assistant_available=True,
                )
        body = json.loads(s=route.calls.last.request.content)
        assert body["ai_assistant_available"] is True
        assert created.ai_assistant_available is True

    @staticmethod
    def test_sync_update_interviewers_and_ai() -> None:
        """Sync update sends interviewers, replace flag, and AI."""
        with respx.mock(assert_all_called=True) as router:
            route = router.put(url=f"{_BASE}/interviews/iv1").respond(
                200,
                json={},
            )
            with HackerRank(api_key="test-key") as client:
                client.interviews.update(
                    interview_id="iv1",
                    interviewers=["a@b.com"],
                    replace_interviewers=True,
                    ai_assistant_available=False,
                )
                client.interviews.update(
                    interview_id="iv1",
                    interviewers=[
                        {"email": "a@b.com", "name": "Ada"},
                    ],
                    replace_interviewers=False,
                    ai_assistant_available=True,
                )
        first = json.loads(s=route.calls[0].request.content)
        second = json.loads(s=route.calls[1].request.content)
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
            ).respond(200, json=_INTERVIEW)
            update_route = router.put(
                url=f"{_BASE}/interviews/iv1",
            ).respond(200, json={})
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
        create_body = json.loads(s=create_route.calls.last.request.content)
        update_body = json.loads(s=update_route.calls.last.request.content)
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
            ).respond(200, json=_CANDIDATE)
            with HackerRank(api_key="test-key") as client:
                client.tests.candidates.invite(
                    test_id="t1",
                    email="c@x.com",
                    ats_state=0,
                )
                client.tests.candidates.invite(
                    test_id="t1",
                    email="c@x.com",
                    ats_state=22,
                )
        assert json.loads(s=route.calls[0].request.content)["ats_state"] == 0
        assert json.loads(s=route.calls[1].request.content)["ats_state"] == 22

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_invite_sends_ats_state() -> None:
        """Async invite serializes ``ats_state``."""
        with respx.mock(assert_all_called=True) as router:
            route = router.post(
                url=f"{_BASE}/tests/t1/candidates",
            ).respond(200, json=_CANDIDATE)
            async with AsyncHackerRank(api_key="test-key") as client:
                await client.tests.candidates.invite(
                    test_id="t1",
                    email="c@x.com",
                    ats_state=5,
                )
        assert json.loads(s=route.calls.last.request.content)["ats_state"] == 5
