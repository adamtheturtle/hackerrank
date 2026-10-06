"""Tests for `hackerrank` integration endpoints."""

from __future__ import annotations

import pytest

# pytest-beartype resolves fixture annotations at runtime.
from hackerrank.async_client import AsyncHackerRank  # noqa: TC001
from hackerrank.client import HackerRank  # noqa: TC001


def test_sync_ats(sync_client: HackerRank) -> None:
    """Exercise the ``ats`` namespace."""
    _ = sync_client.ats.codepair.invite(
        title="t",
        requisition_id="r",
        candidate_id="c",
    )
    _ = sync_client.ats.codepair.invite(
        title="t",
        requisition_id="r",
        candidate_id="c",
        candidate={"email": "x@y.com"},
        send_email=True,
        interview_metadata={"x": "y"},
    )
    _ = sync_client.ats.codescreen.invite(
        test_id="t1",
        email="c@x.com",
        requisition_id="r",
        candidate_id="c",
    )
    _ = sync_client.ats.codescreen.invite(
        test_id="t1",
        email="c@x.com",
        requisition_id="r",
        candidate_id="c",
        send_email=True,
        test_result_url="r",
        webhook_authentication={"type": "basic"},
        accept_result_updates=True,
        force=True,
        force_reattempt_after=60,
        accommodations={"additional_time_percent": 10},
    )


def test_sync_scim(sync_client: HackerRank) -> None:
    """Exercise the SCIM namespaces."""
    _ = sync_client.scim.users.list()
    _ = sync_client.scim.users.list(limit=1, offset=0)
    _ = sync_client.scim.users.create(
        body={"userName": "u@x.com"},
    )
    _ = sync_client.scim.users.get(scim_user_id="scim-1")
    _ = sync_client.scim.users.replace(
        scim_user_id="scim-1",
        body={"userName": "u@x.com"},
    )
    _ = sync_client.scim.users.patch(
        scim_user_id="scim-1",
        operations=[{"op": "replace"}],
    )
    sync_client.scim.users.delete(scim_user_id="scim-1")
    _ = sync_client.scim.groups.list()
    _ = sync_client.scim.groups.create(
        body={"displayName": "G"},
    )
    _ = sync_client.scim.groups.get(scim_group_id="scim-2")
    _ = sync_client.scim.groups.patch(
        scim_group_id="scim-2",
        operations=[{"op": "replace"}],
    )
    sync_client.scim.groups.delete(scim_group_id="scim-2")


@pytest.mark.asyncio
async def test_async_ats(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async ``ats`` namespace."""
    await async_client.ats.codepair.invite(
        title="t",
        requisition_id="r",
        candidate_id="c",
    )
    await async_client.ats.codepair.invite(
        title="t",
        requisition_id="r",
        candidate_id="c",
        candidate={"email": "x@y.com"},
        send_email=True,
        interview_metadata={"x": "y"},
    )
    await async_client.ats.codescreen.invite(
        test_id="t1",
        email="c@x.com",
        requisition_id="r",
        candidate_id="c",
    )
    await async_client.ats.codescreen.invite(
        test_id="t1",
        email="c@x.com",
        requisition_id="r",
        candidate_id="c",
        send_email=True,
        test_result_url="r",
        webhook_authentication={"type": "basic"},
        accept_result_updates=True,
        force=True,
        force_reattempt_after=60,
        accommodations={"additional_time_percent": 10},
    )


@pytest.mark.asyncio
async def test_async_scim(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async SCIM namespaces."""
    await async_client.scim.users.list()
    await async_client.scim.users.list(limit=1, offset=0)
    await async_client.scim.users.create(
        body={"userName": "u@x.com"},
    )
    await async_client.scim.users.get(scim_user_id="scim-1")
    await async_client.scim.users.replace(
        scim_user_id="scim-1",
        body={"userName": "u@x.com"},
    )
    await async_client.scim.users.patch(
        scim_user_id="scim-1",
        operations=[{"op": "replace"}],
    )
    await async_client.scim.users.delete(scim_user_id="scim-1")
    await async_client.scim.groups.list()
    await async_client.scim.groups.create(
        body={"displayName": "G"},
    )
    await async_client.scim.groups.get(scim_group_id="scim-2")
    await async_client.scim.groups.patch(
        scim_group_id="scim-2",
        operations=[{"op": "replace"}],
    )
    await async_client.scim.groups.delete(scim_group_id="scim-2")
