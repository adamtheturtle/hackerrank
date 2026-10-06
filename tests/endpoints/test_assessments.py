"""Tests for `hackerrank` assessments endpoints."""

from __future__ import annotations

import pytest

# pytest-beartype resolves fixture annotations at runtime.
from hackerrank.async_client import AsyncHackerRank  # noqa: TC001
from hackerrank.client import HackerRank  # noqa: TC001
from hackerrank.types import TestsUpdate


def test_sync_tests(sync_client: HackerRank) -> None:
    """Exercise the ``tests`` namespace."""
    _ = sync_client.tests.list()
    _ = sync_client.tests.list(limit=1, offset=0)
    _ = sync_client.tests.create(
        name="T",
        duration=60,
        role_ids=["r"],
        experience=["junior"],
    )
    _ = sync_client.tests.create(
        name="T",
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
    _ = sync_client.tests.get(test_id="t1")
    _ = sync_client.tests.get(
        test_id="t1",
        additional_fields="questions",
    )
    sync_client.tests.update(
        test_id="t1",
        body=TestsUpdate(
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
        ),
    )
    sync_client.tests.delete(test_id="t1")
    sync_client.tests.archive(test_id="t1")
    _ = sync_client.tests.list_inviters(test_id="t1")
    _ = sync_client.tests.list_inviters(
        test_id="t1",
        limit=1,
        offset=0,
    )


def test_sync_test_candidates(sync_client: HackerRank) -> None:
    """Exercise the ``tests.candidates`` namespace."""
    ns = sync_client.tests.candidates
    _ = ns.list(test_id="t1")
    _ = ns.list(test_id="t1", limit=1, offset=0)
    _ = ns.search(test_id="t1", search="alice")
    _ = ns.search(
        test_id="t1",
        search="alice",
        limit=1,
        offset=0,
    )
    _ = ns.invite(test_id="t1", email="c@x.com")
    _ = ns.invite(
        test_id="t1",
        email="c@x.com",
        full_name="Alice",
        ats_state=3,
        send_email=True,
        evaluator_email="e@x.com",
        test_result_url="r",
        test_finish_url="f",
        tags=["t"],
        invite_valid_from="2024",
        invite_valid_to="2024",
        force=True,
        force_reattempt=True,
        accommodations={"additional_time_percent": 10},
        invite_metadata={"x": "y"},
        webhook_authentication={"type": "basic"},
        accept_result_updates=True,
        subject="hi",
        message="msg",
        template="tpl",
    )
    _ = ns.get(test_id="t1", candidate_id="c1")
    _ = ns.get(
        test_id="t1",
        candidate_id="c1",
        additional_fields="questions",
    )
    _ = ns.update(
        test_id="t1",
        candidate_id="c1",
        full_name="Alice",
        ats_state=1,
        invite_valid_from="2024",
        invite_valid_to="2024",
        invite_metadata={"x": "y"},
        evaluator_email="e@x.com",
        test_finish_url="f",
        test_result_url="r",
        webhook_authentication={"type": "basic"},
        accept_result_updates=True,
        tags=["t"],
        accommodations={"additional_time_percent": 10},
    )
    ns.cancel_invite(test_id="t1", candidate_id="c1")
    ns.delete_report(test_id="t1", candidate_id="c1")
    _ = ns.get_report_pdf(test_id="t1", candidate_id="c1")
    _ = ns.get_report_pdf(
        test_id="t1",
        candidate_id="c1",
        format_="url",
    )


def test_sync_templates(sync_client: HackerRank) -> None:
    """Exercise the ``templates`` namespace."""
    _ = sync_client.templates.list()
    _ = sync_client.templates.list(limit=1, offset=0, access="owned")
    _ = sync_client.templates.get(template_id="tpl1")


def test_sync_candidates(sync_client: HackerRank) -> None:
    """Exercise the top-level ``candidates`` namespace."""
    _ = sync_client.candidates.search(query="jane")
    _ = sync_client.candidates.search(
        query="jane",
        limit=1,
        offset=0,
    )


@pytest.mark.asyncio
async def test_async_tests(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async ``tests`` namespace."""
    await async_client.tests.list()
    await async_client.tests.list(limit=1, offset=0)
    await async_client.tests.create(
        name="T",
        duration=60,
        role_ids=["r"],
        experience=["junior"],
    )
    await async_client.tests.create(
        name="T",
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
    await async_client.tests.get(test_id="t1")
    await async_client.tests.get(
        test_id="t1",
        additional_fields="questions",
    )
    await async_client.tests.update(
        test_id="t1",
        body=TestsUpdate(
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
        ),
    )
    await async_client.tests.delete(test_id="t1")
    await async_client.tests.archive(test_id="t1")
    await async_client.tests.list_inviters(test_id="t1")
    await async_client.tests.list_inviters(
        test_id="t1",
        limit=1,
        offset=0,
    )


@pytest.mark.asyncio
async def test_async_test_candidates(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async ``tests.candidates`` namespace."""
    ns = async_client.tests.candidates
    await ns.list(test_id="t1")
    await ns.list(test_id="t1", limit=1, offset=0)
    await ns.search(test_id="t1", search="alice")
    await ns.search(
        test_id="t1",
        search="alice",
        limit=1,
        offset=0,
    )
    await ns.invite(test_id="t1", email="c@x.com")
    await ns.invite(
        test_id="t1",
        email="c@x.com",
        full_name="Alice",
        ats_state=3,
        send_email=True,
        evaluator_email="e@x.com",
        test_result_url="r",
        test_finish_url="f",
        tags=["t"],
        invite_valid_from="2024",
        invite_valid_to="2024",
        force=True,
        force_reattempt=True,
        accommodations={"additional_time_percent": 10},
        invite_metadata={"x": "y"},
        webhook_authentication={"type": "basic"},
        accept_result_updates=True,
        subject="hi",
        message="msg",
        template="tpl",
    )
    await ns.get(test_id="t1", candidate_id="c1")
    await ns.get(
        test_id="t1",
        candidate_id="c1",
        additional_fields="questions",
    )
    await ns.update(
        test_id="t1",
        candidate_id="c1",
        full_name="Alice",
        ats_state=1,
        invite_valid_from="2024",
        invite_valid_to="2024",
        invite_metadata={"x": "y"},
        evaluator_email="e@x.com",
        test_finish_url="f",
        test_result_url="r",
        webhook_authentication={"type": "basic"},
        accept_result_updates=True,
        tags=["t"],
        accommodations={"additional_time_percent": 10},
    )
    await ns.cancel_invite(test_id="t1", candidate_id="c1")
    await ns.delete_report(test_id="t1", candidate_id="c1")
    await ns.get_report_pdf(test_id="t1", candidate_id="c1")
    await ns.get_report_pdf(
        test_id="t1",
        candidate_id="c1",
        format_="url",
    )


@pytest.mark.asyncio
async def test_async_templates(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async ``templates`` namespace."""
    await async_client.templates.list()
    await async_client.templates.list(
        limit=1,
        offset=0,
        access="owned",
    )
    await async_client.templates.get(template_id="tpl1")


@pytest.mark.asyncio
async def test_async_candidates(
    async_client: AsyncHackerRank,
) -> None:
    """Exercise the async top-level ``candidates`` namespace."""
    await async_client.candidates.search(query="jane")
    await async_client.candidates.search(
        query="jane",
        limit=1,
        offset=0,
    )
