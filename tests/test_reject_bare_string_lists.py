"""Reject bare ``str`` where ``list[str]`` fields are expected.

``str`` is a ``Sequence[str]``, so the previous annotations allowed a
bare string that ``list(value)`` then split into characters. These
tests lock the ``builtins.list[str]`` annotations so beartype rejects
that mistake on both clients.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from beartype.roar import BeartypeCallHintParamViolation

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

_BARE: Any = "not-a-list"


def _sync_calls(
    client: HackerRank,
) -> list[tuple[str, Callable[[], object]]]:
    """Build sync callables that pass a bare string for each field."""
    return [
        (
            "interviews.interviewers",
            lambda: client.interviews.create(
                title="t",
                interviewers=_BARE,
            ),
        ),
        (
            "questions.languages",
            lambda: client.questions.create(
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                languages=_BARE,
            ),
        ),
        (
            "questions.tags",
            lambda: client.questions.create(
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                tags=_BARE,
            ),
        ),
        (
            "questions.options",
            lambda: client.questions.create(
                name="n",
                type="mcq",
                problem_statement="ps",
                recommended_duration=10,
                options=_BARE,
            ),
        ),
        (
            "questions.scoring_files",
            lambda: client.questions.create(
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                scoring_files=_BARE,
            ),
        ),
        (
            "questions.readonly_paths",
            lambda: client.questions.create(
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                readonly_paths=_BARE,
            ),
        ),
        (
            "questions.default_files",
            lambda: client.questions.create(
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                default_files=_BARE,
            ),
        ),
        (
            "candidates.tags",
            lambda: client.tests.candidates.invite(
                test_id="t1",
                email="a@b.com",
                tags=_BARE,
            ),
        ),
        (
            "tests.languages",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                languages=_BARE,
            ),
        ),
        (
            "tests.candidate_details",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                candidate_details=_BARE,
            ),
        ),
        (
            "tests.tags",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                tags=_BARE,
            ),
        ),
        (
            "tests.role_ids",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=_BARE,
                experience=["junior"],
            ),
        ),
        (
            "tests.experience",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=["r"],
                experience=_BARE,
            ),
        ),
        (
            "tests.questions",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                questions=_BARE,
            ),
        ),
        (
            "tests.test_admins",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                test_admins=_BARE,
            ),
        ),
        (
            "users.teams",
            lambda: client.users.create(
                email="a@b.com",
                firstname="A",
                role="recruiter",
                teams=_BARE,
            ),
        ),
        (
            "teams.locations",
            lambda: client.teams.create(name="t", locations=_BARE),
        ),
        (
            "teams.departments",
            lambda: client.teams.create(name="t", departments=_BARE),
        ),
    ]


def _async_calls(
    client: AsyncHackerRank,
) -> list[tuple[str, Callable[[], Awaitable[Any]]]]:
    """Build async callables that pass a bare string for each field."""
    return [
        (
            "interviews.interviewers",
            lambda: client.interviews.create(
                title="t",
                interviewers=_BARE,
            ),
        ),
        (
            "questions.languages",
            lambda: client.questions.create(
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                languages=_BARE,
            ),
        ),
        (
            "questions.tags",
            lambda: client.questions.create(
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                tags=_BARE,
            ),
        ),
        (
            "questions.options",
            lambda: client.questions.create(
                name="n",
                type="mcq",
                problem_statement="ps",
                recommended_duration=10,
                options=_BARE,
            ),
        ),
        (
            "questions.scoring_files",
            lambda: client.questions.create(
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                scoring_files=_BARE,
            ),
        ),
        (
            "questions.readonly_paths",
            lambda: client.questions.create(
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                readonly_paths=_BARE,
            ),
        ),
        (
            "questions.default_files",
            lambda: client.questions.create(
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                default_files=_BARE,
            ),
        ),
        (
            "candidates.tags",
            lambda: client.tests.candidates.invite(
                test_id="t1",
                email="a@b.com",
                tags=_BARE,
            ),
        ),
        (
            "tests.languages",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                languages=_BARE,
            ),
        ),
        (
            "tests.candidate_details",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                candidate_details=_BARE,
            ),
        ),
        (
            "tests.tags",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                tags=_BARE,
            ),
        ),
        (
            "tests.role_ids",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=_BARE,
                experience=["junior"],
            ),
        ),
        (
            "tests.experience",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=["r"],
                experience=_BARE,
            ),
        ),
        (
            "tests.questions",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                questions=_BARE,
            ),
        ),
        (
            "tests.test_admins",
            lambda: client.tests.create(
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                test_admins=_BARE,
            ),
        ),
        (
            "users.teams",
            lambda: client.users.create(
                email="a@b.com",
                firstname="A",
                role="recruiter",
                teams=_BARE,
            ),
        ),
        (
            "teams.locations",
            lambda: client.teams.create(name="t", locations=_BARE),
        ),
        (
            "teams.departments",
            lambda: client.teams.create(name="t", departments=_BARE),
        ),
    ]


class TestSyncRejectBareStringLists:
    """Sync client rejects bare strings for list fields."""

    @staticmethod
    def test_rejects_bare_string_for_list_fields() -> None:
        """Each affected sync field raises a beartype violation."""
        client = HackerRank(api_key="test-key")
        try:
            for _field_name, call in _sync_calls(client=client):
                with pytest.raises(
                    expected_exception=BeartypeCallHintParamViolation
                ):
                    call()
        finally:
            client.close()


class TestAsyncRejectBareStringLists:
    """Async client rejects bare strings for list fields."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_rejects_bare_string_for_list_fields() -> None:
        """Each affected async field raises a beartype violation."""
        client = AsyncHackerRank(api_key="test-key")
        try:
            for _field_name, call in _async_calls(client=client):
                with pytest.raises(
                    expected_exception=BeartypeCallHintParamViolation
                ):
                    await call()
        finally:
            await client.aclose()
