"""Tests for typed required update bodies."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest
import respx
from beartype.roar import BeartypeCallHintParamViolation

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank
from hackerrank.types import TestsUpdate, UserUpdate

_BAD_BODY: Any = {}


def _user_update() -> UserUpdate:
    """Return a complete ``UserUpdate`` body."""
    return UserUpdate(
        firstname="Alice",
        lastname="A",
        country="US",
        role="recruiter",
        phone="555",
        questions_permission=1,
        tests_permission=1,
        interviews_permission=1,
        candidates_permission=1,
        shared_questions_permission=1,
        shared_tests_permission=1,
        shared_interviews_permission=1,
        shared_candidates_permission=1,
        company_admin=False,
        team_admin=False,
    )


def _tests_update() -> TestsUpdate:
    """Return a complete ``TestsUpdate`` body."""
    return TestsUpdate(
        name="new",
        starttime="2024",
        endtime="2024",
        duration=60,
        instructions="i",
        locked=False,
        draft=False,
        languages=["python"],
        candidate_details=["name"],
        custom_acknowledge_text="ack",
        cutoff_score=10,
        master_password="pw",  # noqa: S106
        hide_compile_test=False,
        tags=["t"],
        role_ids=["r"],
        experience=["junior"],
        questions=["q1"],
        mcq_incorrect_score=-1,
        mcq_correct_score=1,
        shuffle_questions=True,
        test_admins=["u1"],
        hide_template=False,
        enable_acknowledgement=True,
        enable_proctoring=False,
        enable_advanced_proctoring=False,
        enable_secure_assessment_mode=False,
        enable_ml_plagiarism_analysis=False,
        enable_photo_identification=False,
        ide_config="{}",
    )


class TestUserUpdateBody:
    """``UserUpdate`` construction and client serialization."""

    @staticmethod
    def test_omission_rejected_by_constructor() -> None:
        """Missing required fields raise ``TypeError`` at construction."""
<<<<<<< HEAD
        user_update_ctor: Any = UserUpdate
        with pytest.raises(expected_exception=TypeError):
            user_update_ctor(firstname="Alice")
=======
        incomplete: Any = UserUpdate
        with pytest.raises(expected_exception=TypeError):
            incomplete(firstname="Alice")
>>>>>>> 66b59b6 (Restore OpenAPI-required kwargs after main merge.)

    @staticmethod
    def test_omission_rejected_by_beartype(
        sync_client: HackerRank,
    ) -> None:
        """Passing a bare mapping to ``users.update`` is rejected."""
        bad: Any = {}
        with pytest.raises(expected_exception=BeartypeCallHintParamViolation):
            sync_client.users.update(
                user_id="u1",
<<<<<<< HEAD
                body=_BAD_BODY,
=======
                body=bad,
>>>>>>> 66b59b6 (Restore OpenAPI-required kwargs after main merge.)
            )

    @staticmethod
    def test_to_dict_serializes_all_required_fields() -> None:
        """``to_dict`` includes every required ``UserUpdate`` key."""
        body = _user_update().to_dict()
        assert body == {
            "firstname": "Alice",
            "lastname": "A",
            "country": "US",
            "role": "recruiter",
            "phone": "555",
            "questions_permission": 1,
            "tests_permission": 1,
            "interviews_permission": 1,
            "candidates_permission": 1,
            "shared_questions_permission": 1,
            "shared_tests_permission": 1,
            "shared_interviews_permission": 1,
            "shared_candidates_permission": 1,
            "company_admin": False,
            "team_admin": False,
        }

    @staticmethod
    def test_sync_update_sends_serialized_body() -> None:
        """Sync ``users.update`` sends the serialized body."""
        requests: list[httpx.Request] = []

        def capture(request: httpx.Request) -> httpx.Response:
            """Record the request and return an empty success."""
            requests.append(request)
            return httpx.Response(status_code=200, json={})

        with respx.mock(assert_all_called=True) as router:
            router.put(
                url="https://www.hackerrank.com/x/api/v3/users/u1",
            ).mock(side_effect=capture)
            with HackerRank(api_key="test-key") as client:
                client.users.update(user_id="u1", body=_user_update())

        assert json.loads(s=requests[0].content) == _user_update().to_dict()

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_update_sends_serialized_body() -> None:
        """Async ``users.update`` sends the serialized body."""
        requests: list[httpx.Request] = []

        def capture(request: httpx.Request) -> httpx.Response:
            """Record the request and return an empty success."""
            requests.append(request)
            return httpx.Response(status_code=200, json={})

        with respx.mock(assert_all_called=True) as router:
            router.put(
                url="https://www.hackerrank.com/x/api/v3/users/u1",
            ).mock(side_effect=capture)
            async with AsyncHackerRank(api_key="test-key") as client:
                await client.users.update(user_id="u1", body=_user_update())

        assert json.loads(s=requests[0].content) == _user_update().to_dict()

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_omission_rejected_by_beartype(
        async_client: AsyncHackerRank,
    ) -> None:
        """Passing a bare mapping to async ``users.update`` is
        rejected.
        """
        bad: Any = {}
        with pytest.raises(expected_exception=BeartypeCallHintParamViolation):
            await async_client.users.update(
                user_id="u1",
<<<<<<< HEAD
                body=_BAD_BODY,
=======
                body=bad,
>>>>>>> 66b59b6 (Restore OpenAPI-required kwargs after main merge.)
            )


class TestTestsUpdateBody:
    """``TestsUpdate`` construction and client serialization."""

    @staticmethod
    def test_omission_rejected_by_constructor() -> None:
        """Missing required fields raise ``TypeError`` at construction."""
<<<<<<< HEAD
        tests_update_ctor: Any = TestsUpdate
        with pytest.raises(expected_exception=TypeError):
            tests_update_ctor(name="T")
=======
        incomplete: Any = TestsUpdate
        with pytest.raises(expected_exception=TypeError):
            incomplete(name="T")
>>>>>>> 66b59b6 (Restore OpenAPI-required kwargs after main merge.)

    @staticmethod
    def test_omission_rejected_by_beartype(
        sync_client: HackerRank,
    ) -> None:
        """Passing a bare mapping to ``tests.update`` is rejected."""
        bad: Any = {}
        with pytest.raises(expected_exception=BeartypeCallHintParamViolation):
            sync_client.tests.update(
                test_id="t1",
<<<<<<< HEAD
                body=_BAD_BODY,
=======
                body=bad,
>>>>>>> 66b59b6 (Restore OpenAPI-required kwargs after main merge.)
            )

    @staticmethod
    def test_to_dict_serializes_all_required_fields() -> None:
        """``to_dict`` includes every required ``TestsUpdate`` key."""
        body = _tests_update().to_dict()
        assert set(body) == {
            "name",
            "starttime",
            "endtime",
            "duration",
            "instructions",
            "locked",
            "draft",
            "languages",
            "candidate_details",
            "custom_acknowledge_text",
            "cutoff_score",
            "master_password",
            "hide_compile_test",
            "tags",
            "role_ids",
            "experience",
            "questions",
            "mcq_incorrect_score",
            "mcq_correct_score",
            "shuffle_questions",
            "test_admins",
            "hide_template",
            "enable_acknowledgement",
            "enable_proctoring",
            "enable_advanced_proctoring",
            "enable_secure_assessment_mode",
            "enable_ml_plagiarism_analysis",
            "enable_photo_identification",
            "ide_config",
        }
        assert body["name"] == "new"
        assert body["languages"] == ["python"]

    @staticmethod
    def test_sync_update_sends_serialized_body() -> None:
        """Sync ``tests.update`` sends the serialized body."""
        requests: list[httpx.Request] = []

        def capture(request: httpx.Request) -> httpx.Response:
            """Record the request and return an empty success."""
            requests.append(request)
            return httpx.Response(status_code=200, json={})

        with respx.mock(assert_all_called=True) as router:
            router.put(
                url="https://www.hackerrank.com/x/api/v3/tests/t1",
            ).mock(side_effect=capture)
            with HackerRank(api_key="test-key") as client:
                client.tests.update(test_id="t1", body=_tests_update())

        assert json.loads(s=requests[0].content) == _tests_update().to_dict()

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_update_sends_serialized_body() -> None:
        """Async ``tests.update`` sends the serialized body."""
        requests: list[httpx.Request] = []

        def capture(request: httpx.Request) -> httpx.Response:
            """Record the request and return an empty success."""
            requests.append(request)
            return httpx.Response(status_code=200, json={})

        with respx.mock(assert_all_called=True) as router:
            router.put(
                url="https://www.hackerrank.com/x/api/v3/tests/t1",
            ).mock(side_effect=capture)
            async with AsyncHackerRank(api_key="test-key") as client:
                await client.tests.update(test_id="t1", body=_tests_update())

        assert json.loads(s=requests[0].content) == _tests_update().to_dict()

    @staticmethod
    @pytest.mark.asyncio
    async def test_async_omission_rejected_by_beartype(
        async_client: AsyncHackerRank,
    ) -> None:
        """Passing a bare mapping to async ``tests.update`` is
        rejected.
        """
        bad: Any = {}
        with pytest.raises(expected_exception=BeartypeCallHintParamViolation):
            await async_client.tests.update(
                test_id="t1",
<<<<<<< HEAD
                body=_BAD_BODY,
=======
                body=bad,
>>>>>>> 66b59b6 (Restore OpenAPI-required kwargs after main merge.)
            )
