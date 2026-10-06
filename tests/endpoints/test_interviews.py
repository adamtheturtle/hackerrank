"""Tests for `hackerrank` interviews endpoints."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank


def test_sync_interviews(sync_client: HackerRank) -> None:
    """Exercise the ``interviews`` namespace."""
    _ = sync_client.interviews.list()
    _ = sync_client.interviews.list(
        limit=1,
        offset=0,
        created_at="2024-01-01..2024-01-02",
        updated_at="2024-01-01..2024-01-02",
        ended_at="2024-01-01..2024-01-02",
        user=1,
        interviewers=2,
        access="owned",
        current_status=0,
        order_by="created_at",
        order_dir="asc",
    )
    _ = sync_client.interviews.create(title="t")
    _ = sync_client.interviews.create(
        title="t",
        from_="2024",
        to="2024",
        notes="n",
        resume_url="r",
        interviewers=["a@b.com"],
        result_url="rr",
        candidate={"email": "c@x.com"},
        send_email=True,
        metadata={"x": "y"},
        interview_template_id=1,
        ai_assistant_available=True,
    )
    _ = sync_client.interviews.get(interview_id="iv1")
    _ = sync_client.interviews.update(
        interview_id="iv1",
        title="t",
        from_="2024",
        to="2024",
        notes="n",
        resume_url="r",
        interviewers=["a@b.com"],
        result_url="rr",
        candidate={"email": "c@x.com"},
        send_email=True,
        replace_interviewers=True,
        metadata={"x": "y"},
        interview_template_id=1,
        ai_assistant_available=False,
    )
    sync_client.interviews.delete(interview_id="iv1")
    _ = sync_client.interviews.get_transcript(interview_id="iv1")


def test_sync_interview_templates(sync_client: HackerRank) -> None:
    """Exercise the ``interview_templates`` namespace."""
    _ = sync_client.interview_templates.list()
    _ = sync_client.interview_templates.list(
        limit=1,
        offset=0,
        filter="owned",
    )
    _ = sync_client.interview_templates.create(name="t")
    _ = sync_client.interview_templates.create(
        name="t",
        role_id="dev",
        question_ids=[2687118],
    )
    _ = sync_client.interview_templates.get(template_id="template-1")
    _ = sync_client.interview_templates.update(template_id="template-1")
    _ = sync_client.interview_templates.update(
        template_id="template-1",
        name="t",
        role_id="dev",
        scorecard_id=2,
    )
    sync_client.interview_templates.delete(template_id="template-1")
    _ = sync_client.interview_templates.add_questions(
        template_id="template-1",
        question_ids=[2687118],
    )
    _ = sync_client.interview_templates.remove_question(
        template_id="template-1",
        question_id=2687118,
    )


def test_sync_template_questions_contract() -> None:
    """Send the documented add and remove question requests."""
    requests: list[httpx.Request] = []

    def template_response(request: httpx.Request) -> httpx.Response:
        """Record a request and return a live-shaped response."""
        requests.append(request)
        return httpx.Response(
            status_code=200,
            json={
                "id": "12345",
                "name": "Frontend Developer Interview Template",
                "questions": [111166] if request.method == "PUT" else [],
            },
        )

    base = "https://www.hackerrank.com/x/api/v3/interview_templates/12345"
    with respx.mock(assert_all_called=True) as router:
        _ = router.put(url=f"{base}/add_questions").mock(
            side_effect=template_response,
        )
        _ = router.delete(
            url=f"{base}/remove_question",
            params={"question_id": "111166"},
        ).mock(side_effect=template_response)
        with HackerRank(api_key="test-key") as client:
            added = client.interview_templates.add_questions(
                template_id=12345,
                question_ids=[111166],
            )
            removed = client.interview_templates.remove_question(
                template_id=12345,
                question_id=111166,
            )

    assert json.loads(s=requests[0].content) == {
        "question_ids": [111166],
    }
    assert added.questions == [111166]
    assert requests[1].url.params["question_id"] == "111166"
    assert requests[1].content == b""
    assert removed.questions == []


def test_sync_explicit_sharing_roles(sync_client: HackerRank) -> None:
    """Exercise the ``explicit_sharing_roles`` namespace."""
    sharing = sync_client.interview_templates.explicit_sharing_roles
    sharing.update_access(
        template_id="template-1",
        explicit_roles=[
            {
                "rollable_type": "team",
                "rollable_id": 241877,
                "role_name": "editor",
            },
        ],
    )
    sharing.remove_access(
        template_id="template-1",
        explicit_roles=[
            {"rollable_type": "team", "rollable_id": 241877},
        ],
    )


def test_explicit_sharing_roles_contract() -> None:
    """Send the documented sharing request bodies."""
    requests: list[httpx.Request] = []

    def sharing_response(request: httpx.Request) -> httpx.Response:
        """Record a request and return a live-shaped response."""
        requests.append(request)
        return httpx.Response(
            status_code=200,
            json={
                "model": [],
                "status": True,
                "message": "Successfully updated",
            },
        )

    base = (
        "https://www.hackerrank.com/x/api/v3/interview_templates"
        "/template-1/explicit_sharing_roles"
    )
    with respx.mock(assert_all_called=True) as router:
        _ = router.post(url=f"{base}/update_access").mock(
            side_effect=sharing_response,
        )
        _ = router.delete(url=f"{base}/remove_access").mock(
            side_effect=sharing_response,
        )
        with HackerRank(api_key="test-key") as client:
            sharing = client.interview_templates.explicit_sharing_roles
            sharing.update_access(
                template_id="template-1",
                explicit_roles=[
                    {
                        "rollable_type": "team",
                        "rollable_id": 241877,
                        "role_name": "editor",
                    },
                ],
            )
            sharing.remove_access(
                template_id="template-1",
                explicit_roles=[{"rollable_type": "company"}],
            )

    assert json.loads(s=requests[0].content) == {
        "explicit_roles": [
            {
                "rollable_type": "team",
                "rollable_id": 241877,
                "role_name": "editor",
            },
        ],
    }
    assert json.loads(s=requests[1].content) == {
        "explicit_roles": [{"rollable_type": "company"}],
    }


def test_sync_interview_template_contract() -> None:
    """Use the current request and response fields for templates."""
    requests: list[httpx.Request] = []

    def template_response(request: httpx.Request) -> httpx.Response:
        """Record a request and return a live-shaped response."""
        requests.append(request)
        return httpx.Response(
            status_code=201 if request.method == "POST" else 200,
            json={
                "id": "template-1",
                "name": "Backend interview",
                "questions": [2687118],
            },
        )

    with respx.mock(assert_all_called=True) as router:
        _ = router.post(
            url=("https://www.hackerrank.com/x/api/v3/interview_templates"),
        ).mock(side_effect=template_response)
        _ = router.put(
            url=(
                "https://www.hackerrank.com/x/api/v3/"
                "interview_templates/template-1"
            ),
        ).mock(side_effect=template_response)
        with HackerRank(api_key="test-key") as client:
            created = client.interview_templates.create(
                name="Backend interview",
                role_id="backend",
                question_ids=[2687118, 2687119],
            )
            updated = client.interview_templates.update(
                template_id=created.id,
                name="Senior backend interview",
                role_id="senior-backend",
                scorecard_id=98765,
            )

    create_request = requests[0]
    assert json.loads(s=create_request.content) == {
        "name": "Backend interview",
        "role_id": "backend",
        "question_ids": [2687118, 2687119],
    }
    assert created.id == "template-1"
    assert created.questions == [2687118]

    update_request = requests[1]
    assert json.loads(s=update_request.content) == {
        "name": "Senior backend interview",
        "role_id": "senior-backend",
        "scorecard_id": 98765,
    }
    assert updated.id == "template-1"
    assert updated.questions == [2687118]


@pytest.mark.asyncio
async def test_async_interviews(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async ``interviews`` namespace."""
    await async_client.interviews.list()
    await async_client.interviews.list(
        limit=1,
        offset=0,
        created_at="2024-01-01..2024-01-02",
        updated_at="2024-01-01..2024-01-02",
        ended_at="2024-01-01..2024-01-02",
        user=1,
        interviewers=2,
        access="owned",
        current_status=0,
        order_by="created_at",
        order_dir="asc",
    )
    await async_client.interviews.create(title="t")
    await async_client.interviews.create(
        title="t",
        from_="2024",
        to="2024",
        notes="n",
        resume_url="r",
        interviewers=["a@b.com"],
        result_url="rr",
        candidate={"email": "c@x.com"},
        send_email=True,
        metadata={"x": "y"},
        interview_template_id=1,
        ai_assistant_available=True,
    )
    await async_client.interviews.get(interview_id="iv1")
    await async_client.interviews.update(
        interview_id="iv1",
        title="t",
        from_="2024",
        to="2024",
        notes="n",
        resume_url="r",
        interviewers=["a@b.com"],
        result_url="rr",
        candidate={"email": "c@x.com"},
        send_email=True,
        replace_interviewers=True,
        metadata={"x": "y"},
        interview_template_id=1,
        ai_assistant_available=False,
    )
    await async_client.interviews.delete(interview_id="iv1")
    await async_client.interviews.get_transcript(
        interview_id="iv1",
    )


@pytest.mark.asyncio
async def test_async_interview_templates(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async ``interview_templates`` namespace."""
    await async_client.interview_templates.list()
    await async_client.interview_templates.list(
        limit=1,
        offset=0,
        filter="owned",
    )
    await async_client.interview_templates.create(name="t")
    await async_client.interview_templates.create(
        name="t",
        role_id="dev",
        question_ids=[2687118],
    )
    await async_client.interview_templates.get(
        template_id="template-1",
    )
    await async_client.interview_templates.update(
        template_id="template-1",
    )
    await async_client.interview_templates.update(
        template_id="template-1",
        name="t",
        role_id="dev",
        scorecard_id=2,
    )
    await async_client.interview_templates.delete(
        template_id="template-1",
    )
    await async_client.interview_templates.add_questions(
        template_id="template-1",
        question_ids=[2687118],
    )
    await async_client.interview_templates.remove_question(
        template_id="template-1",
        question_id=2687118,
    )


@pytest.mark.asyncio
async def test_async_template_questions_contract() -> None:
    """Send the documented add and remove question requests."""
    requests: list[httpx.Request] = []

    def template_response(request: httpx.Request) -> httpx.Response:
        """Record a request and return a live-shaped response."""
        requests.append(request)
        return httpx.Response(
            status_code=200,
            json={
                "id": "12345",
                "name": "Frontend Developer Interview Template",
                "questions": [111166] if request.method == "PUT" else [],
            },
        )

    base = "https://www.hackerrank.com/x/api/v3/interview_templates/12345"
    with respx.mock(assert_all_called=True) as router:
        _ = router.put(url=f"{base}/add_questions").mock(
            side_effect=template_response,
        )
        _ = router.delete(
            url=f"{base}/remove_question",
            params={"question_id": "111166"},
        ).mock(side_effect=template_response)
        async with AsyncHackerRank(api_key="test-key") as client:
            added = await client.interview_templates.add_questions(
                template_id=12345,
                question_ids=[111166],
            )
            removed = await client.interview_templates.remove_question(
                template_id=12345,
                question_id=111166,
            )

    assert json.loads(s=requests[0].content) == {
        "question_ids": [111166],
    }
    assert added.questions == [111166]
    assert requests[1].url.params["question_id"] == "111166"
    assert requests[1].content == b""
    assert removed.questions == []


@pytest.mark.asyncio
async def test_async_explicit_sharing_roles(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async ``explicit_sharing_roles`` namespace."""
    sharing = async_client.interview_templates.explicit_sharing_roles
    await sharing.update_access(
        template_id="template-1",
        explicit_roles=[
            {
                "rollable_type": "team",
                "rollable_id": 241877,
                "role_name": "editor",
            },
        ],
    )
    await sharing.remove_access(
        template_id="template-1",
        explicit_roles=[
            {"rollable_type": "team", "rollable_id": 241877},
        ],
    )


@pytest.mark.asyncio
async def test_async_interview_template_contract() -> None:
    """Use current template fields in the async client."""
    requests: list[httpx.Request] = []

    def template_response(request: httpx.Request) -> httpx.Response:
        """Record a request and return a live-shaped response."""
        requests.append(request)
        return httpx.Response(
            status_code=201 if request.method == "POST" else 200,
            json={
                "id": "template-1",
                "name": "Backend interview",
                "questions": [2687118],
            },
        )

    with respx.mock(assert_all_called=True) as router:
        _ = router.post(
            url=("https://www.hackerrank.com/x/api/v3/interview_templates"),
        ).mock(side_effect=template_response)
        _ = router.put(
            url=(
                "https://www.hackerrank.com/x/api/v3/"
                "interview_templates/template-1"
            ),
        ).mock(side_effect=template_response)
        async with AsyncHackerRank(api_key="test-key") as client:
            created = await client.interview_templates.create(
                name="Backend interview",
                role_id="backend",
                question_ids=[2687118, 2687119],
            )
            updated = await client.interview_templates.update(
                template_id=created.id,
                name="Senior backend interview",
                role_id="senior-backend",
                scorecard_id=98765,
            )

    create_request = requests[0]
    assert json.loads(s=create_request.content) == {
        "name": "Backend interview",
        "role_id": "backend",
        "question_ids": [2687118, 2687119],
    }
    assert created.id == "template-1"
    assert created.questions == [2687118]

    update_request = requests[1]
    assert json.loads(s=update_request.content) == {
        "name": "Senior backend interview",
        "role_id": "senior-backend",
        "scorecard_id": 98765,
    }
    assert updated.id == "template-1"
    assert updated.questions == [2687118]
