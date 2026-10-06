"""Tests for `hackerrank` questions endpoints."""

from __future__ import annotations

import pytest

# pytest-beartype resolves fixture annotations at runtime.
from hackerrank.async_client import AsyncHackerRank  # noqa: TC001
from hackerrank.client import HackerRank  # noqa: TC001


def test_sync_questions(sync_client: HackerRank) -> None:
    """Exercise the ``questions`` namespace."""
    _ = sync_client.questions.list()
    _ = sync_client.questions.list(
        limit=1,
        offset=0,
        status="active",
        access=["owned"],
        difficulty=["easy"],
        type=["code"],
        owner=["1"],
        tags=["algo"],
        skills=["python"],
        languages=["python3"],
    )
    _ = sync_client.questions.create(
        name="Q",
        type="code",
        problem_statement="ps",
        recommended_duration=10,
    )
    _ = sync_client.questions.create(
        name="Q",
        type="mcq",
        internal_notes="n",
        languages=["python"],
        problem_statement="ps",
        recommended_duration=10,
        tags=["t"],
        options=["a", "b"],
        answer=[1, 2],
    )
    _ = sync_client.questions.create(
        name="Build a TODO app",
        type="fullstack",
        problem_statement="<p>Build it.</p>",
        recommended_duration=60,
        environment_id=92,
        role_type="fullstack",
        tags=["Medium"],
        score=100.0,
        internal_notes="n",
        scoring_command="npm run score",
        scoring_files=["score.test.js"],
        readonly_paths=["README.md"],
        default_files=["src/index.js"],
        configuration={"menu": {"run": "npm start"}},
        testcases=[{"name": "creates a todo", "weight": 1}],
    )
    _ = sync_client.questions.create(
        name="Q",
        type="mcq",
        problem_statement="ps",
        recommended_duration=10,
        answer=1,
    )
    _ = sync_client.questions.get(question_id="q1")
    _ = sync_client.questions.update(
        question_id="q1",
        name="Q",
        type="code",
        internal_notes="n",
        languages=["python"],
        problem_statement="ps",
        recommended_duration=10,
        tags=["t"],
        options=["a"],
        answer=1,
    )
    _ = sync_client.questions.update(
        question_id="q1",
        name="Q",
        type="code",
        internal_notes="n",
        languages=["python"],
        problem_statement="ps",
        recommended_duration=10,
        tags=["t"],
        options=["a"],
        answer=1,
        score=100.0,
        environment_id=92,
        role_type="fullstack",
        scoring_command="npm run grade",
        scoring_files=["score.test.js"],
        readonly_paths=["README.md"],
        default_files=["src/index.js"],
        configuration={"menu": {"run": "npm run dev"}},
        testcases=[{"name": "creates a todo", "weight": 1}],
    )
    _ = sync_client.questions.update(
        question_id="q1",
        name="Q",
        type="mcq",
        internal_notes="n",
        languages=["python"],
        problem_statement="ps",
        recommended_duration=10,
        tags=["t"],
        options=["a", "b"],
        answer=[1, 2],
    )
    _ = sync_client.questions.update(
        question_id="q-with-body",
        name="Q",
        type="code",
        internal_notes="n",
        languages=["python"],
        problem_statement="ps",
        recommended_duration=10,
        tags=["t"],
        options=["a"],
        answer=1,
        scoring_command="npm run grade",
    )
    _ = sync_client.questions.upload_project_zip(
        question_id="q1",
        file=b"zip",
    )
    sync_client.questions.update_codestubs(
        question_id="q1",
        codestubs={"java": "..."},
    )
    _ = sync_client.questions.generate_codestubs(
        question_id="q1",
        body={"type": "code"},
    )
    _ = sync_client.questions.generate_codestubs(
        question_id="q1",
        body={"lang": "java"},
    )
    _ = sync_client.questions.add_testcase(
        question_id="q1",
        body={"input": "x"},
    )
    sync_client.questions.update_testcase(
        question_id="q1",
        testcase_id="tc1",
        body={"input": "y"},
    )
    sync_client.questions.delete_testcase(
        question_id="q1",
        testcase_id="tc1",
    )
    sync_client.questions.delete_all_testcases(
        question_id="q1",
    )


def test_sync_environments(sync_client: HackerRank) -> None:
    """Exercise the ``environments`` namespace."""
    _ = sync_client.environments.list()
    _ = sync_client.environments.get(environment_id=92)


@pytest.mark.asyncio
async def test_async_questions(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async ``questions`` namespace."""
    await async_client.questions.list()
    await async_client.questions.list(
        limit=1,
        offset=0,
        status="active",
        access=["owned"],
        difficulty=["easy"],
        type=["code"],
        owner=["1"],
        tags=["algo"],
        skills=["python"],
        languages=["python3"],
    )
    await async_client.questions.create(
        name="Q",
        type="code",
        problem_statement="ps",
        recommended_duration=10,
    )
    await async_client.questions.create(
        name="Q",
        type="mcq",
        internal_notes="n",
        languages=["python"],
        problem_statement="ps",
        recommended_duration=10,
        tags=["t"],
        options=["a", "b"],
        answer=[1, 2],
    )
    await async_client.questions.create(
        name="Build a TODO app",
        type="fullstack",
        problem_statement="<p>Build it.</p>",
        recommended_duration=60,
        environment_id=92,
        role_type="fullstack",
        tags=["Medium"],
        score=100.0,
        internal_notes="n",
        scoring_command="npm run score",
        scoring_files=["score.test.js"],
        readonly_paths=["README.md"],
        default_files=["src/index.js"],
        configuration={"menu": {"run": "npm start"}},
        testcases=[{"name": "creates a todo", "weight": 1}],
    )
    await async_client.questions.create(
        name="Q",
        type="mcq",
        problem_statement="ps",
        recommended_duration=10,
        answer=1,
    )
    await async_client.questions.get(question_id="q1")
    await async_client.questions.update(
        question_id="q1",
        name="Q",
        type="code",
        internal_notes="n",
        languages=["python"],
        problem_statement="ps",
        recommended_duration=10,
        tags=["t"],
        options=["a"],
        answer=1,
    )
    await async_client.questions.update(
        question_id="q1",
        name="Q",
        type="code",
        internal_notes="n",
        languages=["python"],
        problem_statement="ps",
        recommended_duration=10,
        tags=["t"],
        options=["a"],
        answer=1,
        score=100.0,
        environment_id=92,
        role_type="fullstack",
        scoring_command="npm run grade",
        scoring_files=["score.test.js"],
        readonly_paths=["README.md"],
        default_files=["src/index.js"],
        configuration={"menu": {"run": "npm run dev"}},
        testcases=[{"name": "creates a todo", "weight": 1}],
    )
    await async_client.questions.update(
        question_id="q1",
        name="Q",
        type="mcq",
        internal_notes="n",
        languages=["python"],
        problem_statement="ps",
        recommended_duration=10,
        tags=["t"],
        options=["a", "b"],
        answer=[1, 2],
    )
    await async_client.questions.update(
        question_id="q-with-body",
        name="Q",
        type="code",
        internal_notes="n",
        languages=["python"],
        problem_statement="ps",
        recommended_duration=10,
        tags=["t"],
        options=["a"],
        answer=1,
        scoring_command="npm run grade",
    )
    await async_client.questions.upload_project_zip(
        question_id="q1",
        file=b"zip",
    )
    await async_client.questions.update_codestubs(
        question_id="q1",
        codestubs={"java": "..."},
    )
    await async_client.questions.generate_codestubs(
        question_id="q1",
        body={"type": "code"},
    )
    await async_client.questions.generate_codestubs(
        question_id="q1",
        body={"lang": "java"},
    )
    await async_client.questions.add_testcase(
        question_id="q1",
        body={"input": "x"},
    )
    await async_client.questions.update_testcase(
        question_id="q1",
        testcase_id="tc1",
        body={"input": "y"},
    )
    await async_client.questions.delete_testcase(
        question_id="q1",
        testcase_id="tc1",
    )
    await async_client.questions.delete_all_testcases(
        question_id="q1",
    )


@pytest.mark.asyncio
async def test_async_environments(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async ``environments`` namespace."""
    await async_client.environments.list()
    await async_client.environments.get(environment_id=92)
