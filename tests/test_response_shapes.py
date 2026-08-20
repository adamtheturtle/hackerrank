"""Contract tests for live API response and request shapes."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.types import CandidateInvite, Interview, Interviewer, Test


_INTERVIEW_PAYLOAD = {
    "id": "289187",
    "status": "active",
    "url": "https://example.test/interview",
    "title": "Interview",
    "from": "2026-08-19T01:09:27+0000",
    "to": "2026-08-19T02:09:27+0000",
    "started_at": "2026-08-18T01:09:27+0000",
    "ai_assistant_available": True,
    "interviewers": [{"email": "hina@techcorp.com", "name": "Hina"}],
}

_INVITE_PAYLOAD = {
    "test_link": "https://example.test/invite",
    "email": "a@example.com",
    "id": 10000,
}

_CANDIDATE_PAYLOAD = {
    "id": "98Sjnbj12",
    "email": "alice.wonders@email.com",
    "full_name": "Updated",
    "added_time": "30",
}

_TEST_PAYLOAD = {
    "id": "1PxfG1348",
    "name": "Java Challenge",
    "candidate_details": [
        {"predefined_label": "full_name", "required": True},
    ],
    "sections": {"section-1": {"name": "Core"}},
}


class TestSyncResponseShapes:
    """Sync client parsing against documented live shapes."""

    @staticmethod
    def test_interview_create_accepts_object_interviewers() -> None:
        """Interview create sends and parses object-form interviewers."""
        requests: list[httpx.Request] = []

        def interview_response(request: httpx.Request) -> httpx.Response:
            """Record the request and return a live-shaped interview."""
            requests.append(request)
            return httpx.Response(status_code=201, json=_INTERVIEW_PAYLOAD)

        with respx.mock(assert_all_called=True) as router:
            router.post(
                url="https://www.hackerrank.com/x/api/v3/interviews",
            ).mock(side_effect=interview_response)
            with HackerRank(api_key="test-key") as client:
                created = client.interviews.create(
                    title="Example",
                    interviewers=[
                        {"email": "a@example.com", "name": "A"},
                    ],
                )

        assert json.loads(s=requests[0].content)["interviewers"] == [
            {"email": "a@example.com", "name": "A"},
        ]
        assert isinstance(created.interviewers[0], Interviewer)
        assert created.from_ == "2026-08-19T01:09:27+0000"
        assert created.to == "2026-08-19T02:09:27+0000"
        assert created.started_at == "2026-08-18T01:09:27+0000"
        assert created.ai_assistant_available is True

    @staticmethod
    def test_interview_update_returns_interview() -> None:
        """Interview update returns the documented InterviewShow body."""
        with respx.mock(assert_all_called=True) as router:
            router.put(
                url="https://www.hackerrank.com/x/api/v3/interviews/i",
            ).mock(
                return_value=httpx.Response(
                    status_code=200,
                    json=_INTERVIEW_PAYLOAD,
                ),
            )
            with HackerRank(api_key="test-key") as client:
                updated = client.interviews.update(
                    interview_id="i",
                    title="Updated",
                )

        assert isinstance(updated, Interview)
        assert updated.id == "289187"
        assert updated.title == "Interview"

    @staticmethod
    def test_test_create_accepts_object_candidate_details() -> None:
        """Test create sends object-form candidate_details."""
        requests: list[httpx.Request] = []

        def test_response(request: httpx.Request) -> httpx.Response:
            """Record the request and return a live-shaped test."""
            requests.append(request)
            return httpx.Response(status_code=201, json=_TEST_PAYLOAD)

        with respx.mock(assert_all_called=True) as router:
            router.post(
                url="https://www.hackerrank.com/x/api/v3/tests",
            ).mock(side_effect=test_response)
            with HackerRank(api_key="test-key") as client:
                created = client.tests.create(
                    name="Example",
                    duration=60,
                    role_ids=["role"],
                    experience=["0-2 years"],
                    candidate_details=[
                        {"predefined_label": "full_name", "required": True},
                    ],
                )

        assert json.loads(s=requests[0].content)["candidate_details"] == [
            {"predefined_label": "full_name", "required": True},
        ]
        assert isinstance(created, Test)
        assert created.sections == {"section-1": {"name": "Core"}}

    @staticmethod
    def test_candidate_invite_keeps_test_link_and_integer_id() -> None:
        """Candidate invite returns test_link and integer id."""
        with respx.mock(assert_all_called=True) as router:
            router.post(
                url=(
                    "https://www.hackerrank.com/x/api/v3/tests/t/candidates"
                ),
            ).mock(
                return_value=httpx.Response(
                    status_code=200,
                    json=_INVITE_PAYLOAD,
                ),
            )
            with HackerRank(api_key="test-key") as client:
                invite = client.tests.candidates.invite(
                    test_id="t",
                    email="a@example.com",
                )

        assert isinstance(invite, CandidateInvite)
        assert invite.test_link == "https://example.test/invite"
        assert invite.id == 10000

    @staticmethod
    def test_candidate_update_returns_candidate() -> None:
        """Candidate update returns the documented TestCandidateShow body."""
        with respx.mock(assert_all_called=True) as router:
            router.put(
                url=(
                    "https://www.hackerrank.com/x/api/v3/"
                    "tests/t/candidates/c"
                ),
            ).mock(
                return_value=httpx.Response(
                    status_code=200,
                    json=_CANDIDATE_PAYLOAD,
                ),
            )
            with HackerRank(api_key="test-key") as client:
                updated = client.tests.candidates.update(
                    test_id="t",
                    candidate_id="c",
                    full_name="Updated",
                )

        assert updated.full_name == "Updated"
        assert updated.added_time == "30"

    @staticmethod
    def test_ats_invites_use_correct_response_models() -> None:
        """ATS CodePair returns Interview; CodeScreen returns invite."""
        with respx.mock(assert_all_called=True) as router:
            router.post(
                url="https://www.hackerrank.com/x/api/v3/ats/codepair",
            ).mock(
                return_value=httpx.Response(
                    status_code=200,
                    json=_INTERVIEW_PAYLOAD,
                ),
            )
            router.post(
                url="https://www.hackerrank.com/x/api/v3/ats/codescreen",
            ).mock(
                return_value=httpx.Response(
                    status_code=200,
                    json=_INVITE_PAYLOAD,
                ),
            )
            with HackerRank(api_key="test-key") as client:
                codepair = client.ats.codepair.invite(title="Interview")
                codescreen = client.ats.codescreen.invite(
                    test_id="t",
                    email="a@example.com",
                )

        assert isinstance(codepair, Interview)
        assert codepair.id == "289187"
        assert codepair.url == "https://example.test/interview"
        assert isinstance(codescreen, CandidateInvite)
        assert codescreen.test_link == "https://example.test/invite"


class TestAsyncResponseShapes:
    """Async client parsing against documented live shapes."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_interview_and_invite_shapes() -> None:
        """Async create/update/invite paths match sync response models."""
        with respx.mock(assert_all_called=True) as router:
            router.post(
                url="https://www.hackerrank.com/x/api/v3/interviews",
            ).mock(
                return_value=httpx.Response(
                    status_code=201,
                    json=_INTERVIEW_PAYLOAD,
                ),
            )
            router.put(
                url="https://www.hackerrank.com/x/api/v3/interviews/i",
            ).mock(
                return_value=httpx.Response(
                    status_code=200,
                    json=_INTERVIEW_PAYLOAD,
                ),
            )
            router.post(
                url=(
                    "https://www.hackerrank.com/x/api/v3/tests/t/candidates"
                ),
            ).mock(
                return_value=httpx.Response(
                    status_code=200,
                    json=_INVITE_PAYLOAD,
                ),
            )
            router.put(
                url=(
                    "https://www.hackerrank.com/x/api/v3/"
                    "tests/t/candidates/c"
                ),
            ).mock(
                return_value=httpx.Response(
                    status_code=200,
                    json=_CANDIDATE_PAYLOAD,
                ),
            )
            router.post(
                url="https://www.hackerrank.com/x/api/v3/tests",
            ).mock(
                return_value=httpx.Response(
                    status_code=201,
                    json=_TEST_PAYLOAD,
                ),
            )
            router.post(
                url="https://www.hackerrank.com/x/api/v3/ats/codepair",
            ).mock(
                return_value=httpx.Response(
                    status_code=200,
                    json=_INTERVIEW_PAYLOAD,
                ),
            )
            router.post(
                url="https://www.hackerrank.com/x/api/v3/ats/codescreen",
            ).mock(
                return_value=httpx.Response(
                    status_code=200,
                    json=_INVITE_PAYLOAD,
                ),
            )
            async with AsyncHackerRank(api_key="test-key") as client:
                created = await client.interviews.create(
                    title="Example",
                    interviewers=[
                        {"email": "a@example.com", "name": "A"},
                    ],
                )
                updated = await client.interviews.update(
                    interview_id="i",
                    title="Updated",
                )
                invite = await client.tests.candidates.invite(
                    test_id="t",
                    email="a@example.com",
                )
                candidate = await client.tests.candidates.update(
                    test_id="t",
                    candidate_id="c",
                    full_name="Updated",
                )
                test = await client.tests.create(
                    name="Example",
                    candidate_details=[
                        {"predefined_label": "full_name", "required": True},
                    ],
                )
                codepair = await client.ats.codepair.invite(
                    title="Interview",
                )
                codescreen = await client.ats.codescreen.invite(
                    test_id="t",
                    email="a@example.com",
                )

        assert isinstance(created.interviewers[0], Interviewer)
        assert created.ai_assistant_available is True
        assert isinstance(updated, Interview)
        assert invite.test_link == "https://example.test/invite"
        assert invite.id == 10000
        assert candidate.added_time == "30"
        assert test.sections == {"section-1": {"name": "Core"}}
        assert isinstance(codepair, Interview)
        assert isinstance(codescreen, CandidateInvite)
