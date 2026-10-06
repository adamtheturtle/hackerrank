"""Tests for `hackerrank` organization endpoints."""

from __future__ import annotations

import pytest

# pytest-beartype resolves fixture annotations at runtime.
from hackerrank.async_client import AsyncHackerRank  # noqa: TC001
from hackerrank.client import HackerRank  # noqa: TC001
from hackerrank.types import UserUpdate


def test_sync_users(sync_client: HackerRank) -> None:
    """Exercise the ``users`` namespace."""
    _ = sync_client.users.list()
    _ = sync_client.users.list(limit=1, offset=0)
    _ = sync_client.users.search(search="alice")
    _ = sync_client.users.search(
        search="alice",
        limit=1,
        offset=0,
    )
    _ = sync_client.users.create(
        email="u@x.com",
        firstname="Alice",
        role="recruiter",
        teams=["tm1"],
    )
    _ = sync_client.users.create(
        email="u@x.com",
        firstname="Alice",
        lastname="A",
        country="US",
        role="recruiter",
        send_email=True,
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
        teams=["tm1"],
    )
    _ = sync_client.users.get(user_id="u1")
    sync_client.users.update(
        user_id="u1",
        body=UserUpdate(
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
        ),
    )
    sync_client.users.delete(user_id="u1")


def test_sync_teams(sync_client: HackerRank) -> None:
    """Exercise the ``teams`` namespace."""
    _ = sync_client.teams.list()
    _ = sync_client.teams.list(limit=1, offset=0)
    _ = sync_client.teams.create(name="t")
    _ = sync_client.teams.create(
        name="t",
        recruiter_cap=5,
        developer_cap=5,
        invite_as="recruiter",
        locations=["NYC"],
        departments=["Eng"],
    )
    _ = sync_client.teams.get(team_id="tm1")
    sync_client.teams.update(
        team_id="tm1",
        name="t",
        recruiter_cap=5,
        developer_cap=5,
        invite_as="recruiter",
        locations=["NYC"],
        departments=["Eng"],
    )
    sync_client.teams.delete(team_id="tm1")


def test_sync_team_memberships(sync_client: HackerRank) -> None:
    """Exercise the ``teams.memberships`` namespace."""
    ns = sync_client.teams.memberships
    _ = ns.list(team_id="tm1")
    _ = ns.list(team_id="tm1", limit=1, offset=0)
    _ = ns.get(team_id="tm1", user_id="u1")
    _ = ns.create(team_id="tm1", user_id="u1")
    _ = ns.create(team_id="tm1", user_id="u1", license="developer")
    ns.delete(team_id="tm1", user_id="u1")


def test_sync_audit_logs(sync_client: HackerRank) -> None:
    """Exercise the ``audit_logs`` namespace."""
    _ = sync_client.audit_logs.list()
    _ = sync_client.audit_logs.list(
        limit=1,
        offset=0,
        user_id="u1",
    )


@pytest.mark.asyncio
async def test_async_users(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async ``users`` namespace."""
    await async_client.users.list()
    await async_client.users.list(limit=1, offset=0)
    await async_client.users.search(search="alice")
    await async_client.users.search(
        search="alice",
        limit=1,
        offset=0,
    )
    await async_client.users.create(
        email="u@x.com",
        firstname="Alice",
        role="recruiter",
        teams=["tm1"],
    )
    await async_client.users.create(
        email="u@x.com",
        firstname="Alice",
        lastname="A",
        country="US",
        role="recruiter",
        send_email=True,
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
        teams=["tm1"],
    )
    await async_client.users.get(user_id="u1")
    await async_client.users.update(
        user_id="u1",
        body=UserUpdate(
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
        ),
    )
    await async_client.users.delete(user_id="u1")


@pytest.mark.asyncio
async def test_async_teams(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async ``teams`` namespace."""
    await async_client.teams.list()
    await async_client.teams.list(limit=1, offset=0)
    await async_client.teams.create(name="t")
    await async_client.teams.create(
        name="t",
        recruiter_cap=5,
        developer_cap=5,
        invite_as="recruiter",
        locations=["NYC"],
        departments=["Eng"],
    )
    await async_client.teams.get(team_id="tm1")
    await async_client.teams.update(
        team_id="tm1",
        name="t",
        recruiter_cap=5,
        developer_cap=5,
        invite_as="recruiter",
        locations=["NYC"],
        departments=["Eng"],
    )
    await async_client.teams.delete(team_id="tm1")


@pytest.mark.asyncio
async def test_async_team_memberships(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async ``teams.memberships`` namespace."""
    ns = async_client.teams.memberships
    await ns.list(team_id="tm1")
    await ns.list(team_id="tm1", limit=1, offset=0)
    await ns.get(team_id="tm1", user_id="u1")
    await ns.create(team_id="tm1", user_id="u1")
    await ns.create(team_id="tm1", user_id="u1", license="developer")
    await ns.delete(team_id="tm1", user_id="u1")


@pytest.mark.asyncio
async def test_async_audit_logs(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async ``audit_logs`` namespace."""
    await async_client.audit_logs.list()
    await async_client.audit_logs.list(
        limit=1,
        offset=0,
        user_id="u1",
    )
