"""Reject bare ``str`` where ``list[str]`` fields are expected.

``str`` is a ``Sequence[str]``, so the previous annotations allowed a
bare string that ``list(value)`` then split into characters. These
tests lock the ``builtins.list[str]`` annotations so beartype rejects
that mistake on both clients.
"""

from __future__ import annotations

from operator import methodcaller
from typing import TYPE_CHECKING

import pytest
from beartype.roar import BeartypeCallHintParamViolation

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

# Resolve methods at runtime to test rejection of invalid inputs.
_BARE = "not-a-list"


def _sync_calls(
    client: HackerRank,
) -> list[tuple[str, Callable[[], object]]]:
    """Build sync callables that pass a bare string for each field."""
    return [
        (
            "interviews.interviewers",
            lambda: methodcaller(
                "create",
                title="t",
                interviewers=_BARE,
            )(client.interviews),
        ),
        (
            "questions.languages",
            lambda: methodcaller(
                "create",
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                languages=_BARE,
            )(client.questions),
        ),
        (
            "questions.tags",
            lambda: methodcaller(
                "create",
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                tags=_BARE,
            )(client.questions),
        ),
        (
            "questions.options",
            lambda: methodcaller(
                "create",
                name="n",
                type="mcq",
                problem_statement="ps",
                recommended_duration=10,
                options=_BARE,
            )(client.questions),
        ),
        (
            "questions.scoring_files",
            lambda: methodcaller(
                "create",
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                scoring_files=_BARE,
            )(client.questions),
        ),
        (
            "questions.readonly_paths",
            lambda: methodcaller(
                "create",
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                readonly_paths=_BARE,
            )(client.questions),
        ),
        (
            "questions.default_files",
            lambda: methodcaller(
                "create",
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                default_files=_BARE,
            )(client.questions),
        ),
        (
            "candidates.tags",
            lambda: methodcaller(
                "invite",
                test_id="t1",
                email="a@b.com",
                tags=_BARE,
            )(client.tests.candidates),
        ),
        (
            "tests.languages",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                languages=_BARE,
            )(client.tests),
        ),
        (
            "tests.candidate_details",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                candidate_details=_BARE,
            )(client.tests),
        ),
        (
            "tests.tags",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                tags=_BARE,
            )(client.tests),
        ),
        (
            "tests.role_ids",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=_BARE,
                experience=["junior"],
            )(client.tests),
        ),
        (
            "tests.experience",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=["r"],
                experience=_BARE,
            )(client.tests),
        ),
        (
            "tests.questions",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                questions=_BARE,
            )(client.tests),
        ),
        (
            "tests.test_admins",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                test_admins=_BARE,
            )(client.tests),
        ),
        (
            "users.teams",
            lambda: methodcaller(
                "create",
                email="a@b.com",
                firstname="A",
                role="recruiter",
                teams=_BARE,
            )(client.users),
        ),
        (
            "teams.locations",
            lambda: methodcaller("create", name="t", locations=_BARE)(
                client.teams
            ),
        ),
        (
            "teams.departments",
            lambda: methodcaller("create", name="t", departments=_BARE)(
                client.teams
            ),
        ),
    ]


def _async_calls(
    client: AsyncHackerRank,
) -> list[tuple[str, Callable[[], Awaitable[object]]]]:
    """Build async callables that pass a bare string for each field."""
    return [
        (
            "interviews.interviewers",
            lambda: methodcaller(
                "create",
                title="t",
                interviewers=_BARE,
            )(client.interviews),
        ),
        (
            "questions.languages",
            lambda: methodcaller(
                "create",
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                languages=_BARE,
            )(client.questions),
        ),
        (
            "questions.tags",
            lambda: methodcaller(
                "create",
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                tags=_BARE,
            )(client.questions),
        ),
        (
            "questions.options",
            lambda: methodcaller(
                "create",
                name="n",
                type="mcq",
                problem_statement="ps",
                recommended_duration=10,
                options=_BARE,
            )(client.questions),
        ),
        (
            "questions.scoring_files",
            lambda: methodcaller(
                "create",
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                scoring_files=_BARE,
            )(client.questions),
        ),
        (
            "questions.readonly_paths",
            lambda: methodcaller(
                "create",
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                readonly_paths=_BARE,
            )(client.questions),
        ),
        (
            "questions.default_files",
            lambda: methodcaller(
                "create",
                name="n",
                type="coding",
                problem_statement="ps",
                recommended_duration=10,
                default_files=_BARE,
            )(client.questions),
        ),
        (
            "candidates.tags",
            lambda: methodcaller(
                "invite",
                test_id="t1",
                email="a@b.com",
                tags=_BARE,
            )(client.tests.candidates),
        ),
        (
            "tests.languages",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                languages=_BARE,
            )(client.tests),
        ),
        (
            "tests.candidate_details",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                candidate_details=_BARE,
            )(client.tests),
        ),
        (
            "tests.tags",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                tags=_BARE,
            )(client.tests),
        ),
        (
            "tests.role_ids",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=_BARE,
                experience=["junior"],
            )(client.tests),
        ),
        (
            "tests.experience",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=["r"],
                experience=_BARE,
            )(client.tests),
        ),
        (
            "tests.questions",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                questions=_BARE,
            )(client.tests),
        ),
        (
            "tests.test_admins",
            lambda: methodcaller(
                "create",
                name="t",
                duration=60,
                role_ids=["r"],
                experience=["junior"],
                test_admins=_BARE,
            )(client.tests),
        ),
        (
            "users.teams",
            lambda: methodcaller(
                "create",
                email="a@b.com",
                firstname="A",
                role="recruiter",
                teams=_BARE,
            )(client.users),
        ),
        (
            "teams.locations",
            lambda: methodcaller("create", name="t", locations=_BARE)(
                client.teams
            ),
        ),
        (
            "teams.departments",
            lambda: methodcaller("create", name="t", departments=_BARE)(
                client.teams
            ),
        ),
    ]


def test_sync_rejects_bare_string_for_list_fields() -> None:
    """Each affected sync field raises a beartype violation."""
    client = HackerRank(api_key="test-key")
    try:
        for _field_name, call in _sync_calls(client=client):
            with pytest.raises(
                expected_exception=BeartypeCallHintParamViolation
            ):
                _ = call()
    finally:
        client.close()


@pytest.mark.asyncio
async def test_async_rejects_bare_string_for_list_fields() -> None:
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
