"""Exhaustive endpoint coverage tests.

Each public method on every namespace is invoked at least once with
required arguments only, and once more with every optional argument
populated. Responses are stubbed via the ``stub_router`` fixture in
``conftest.py``.
"""

from __future__ import annotations

import pytest

from hackerrank.async_client import AsyncHackerRank  # noqa: TC001
from hackerrank.client import HackerRank  # noqa: TC001


class TestSyncEndpoints:
    """Sync client endpoint coverage."""

    @staticmethod
    def test_interviews(sync_client: HackerRank) -> None:
        """Exercise the ``interviews`` namespace."""
        sync_client.interviews.list()
        sync_client.interviews.list(
            limit=1,
            offset=0,
            created_at="2024-01-01..2024-01-02",
            updated_at="2024-01-01..2024-01-02",
            ended_at="2024-01-01..2024-01-02",
        )
        sync_client.interviews.create()
        sync_client.interviews.create(
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
        )
        sync_client.interviews.get(interview_id="iv1")
        sync_client.interviews.update(interview_id="iv1")
        sync_client.interviews.update(
            interview_id="iv1",
            title="t",
            from_="2024",
            to="2024",
            notes="n",
            resume_url="r",
            result_url="rr",
            candidate={"email": "c@x.com"},
            send_email=True,
            metadata={"x": "y"},
            interview_template_id=1,
        )
        sync_client.interviews.delete(interview_id="iv1")
        sync_client.interviews.get_transcript(interview_id="iv1")

    @staticmethod
    def test_interview_templates(sync_client: HackerRank) -> None:
        """Exercise the ``interview_templates`` namespace."""
        sync_client.interview_templates.list()
        sync_client.interview_templates.list(limit=1, offset=0)
        sync_client.interview_templates.create(name="t")
        sync_client.interview_templates.create(
            name="t",
            roles=["dev"],
            team_share=1,
            questions=["q1"],
            scorecard=2,
        )
        sync_client.interview_templates.get(template_id=1)
        sync_client.interview_templates.update(template_id=1)
        sync_client.interview_templates.update(
            template_id=1,
            name="t",
            roles=["dev"],
            team_share=1,
            questions=["q1"],
            scorecard=2,
        )
        sync_client.interview_templates.delete(template_id=1)

    @staticmethod
    def test_questions(sync_client: HackerRank) -> None:
        """Exercise the ``questions`` namespace."""
        sync_client.questions.list()
        sync_client.questions.list(limit=1, offset=0)
        sync_client.questions.create(name="Q", type="code")
        sync_client.questions.create(
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
        sync_client.questions.create(
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
        sync_client.questions.create(
            name="Q",
            type="mcq",
            answer=1,
        )
        sync_client.questions.get(question_id="q1")
        sync_client.questions.update(question_id="q1")
        sync_client.questions.update(
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
        sync_client.questions.update(
            question_id="q1",
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
        sync_client.questions.update(
            question_id="q1",
            answer=[1, 2],
        )
        sync_client.questions.upload_project_zip(
            question_id="q1",
            file=b"zip",
        )
        sync_client.questions.update_codestubs(
            question_id="q1",
            codestubs={"java": "..."},
        )
        sync_client.questions.generate_codestubs(question_id="q1")
        sync_client.questions.generate_codestubs(
            question_id="q1",
            body={"lang": "java"},
        )
        sync_client.questions.add_testcase(
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

    @staticmethod
    def test_environments(sync_client: HackerRank) -> None:
        """Exercise the ``environments`` namespace."""
        sync_client.environments.list()
        sync_client.environments.get(environment_id=92)

    @staticmethod
    def test_tests(sync_client: HackerRank) -> None:
        """Exercise the ``tests`` namespace."""
        sync_client.tests.list()
        sync_client.tests.list(limit=1, offset=0)
        sync_client.tests.create(name="T")
        sync_client.tests.create(
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
        sync_client.tests.get(test_id="t1")
        sync_client.tests.get(
            test_id="t1",
            additional_fields="questions",
        )
        sync_client.tests.update(test_id="t1", body={"name": "new"})
        sync_client.tests.delete(test_id="t1")
        sync_client.tests.archive(test_id="t1")
        sync_client.tests.list_inviters(test_id="t1")
        sync_client.tests.list_inviters(
            test_id="t1",
            limit=1,
            offset=0,
        )

    @staticmethod
    def test_test_candidates(sync_client: HackerRank) -> None:
        """Exercise the ``tests.candidates`` namespace."""
        ns = sync_client.tests.candidates
        ns.list(test_id="t1")
        ns.list(test_id="t1", limit=1, offset=0)
        ns.search(test_id="t1", search="alice")
        ns.search(
            test_id="t1",
            search="alice",
            limit=1,
            offset=0,
        )
        ns.invite(test_id="t1", email="c@x.com")
        ns.invite(
            test_id="t1",
            email="c@x.com",
            full_name="Alice",
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
        ns.get(test_id="t1", candidate_id="c1")
        ns.get(
            test_id="t1",
            candidate_id="c1",
            additional_fields="questions",
        )
        ns.update(test_id="t1", candidate_id="c1")
        ns.update(
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
        ns.get_report_pdf(test_id="t1", candidate_id="c1")
        ns.get_report_pdf(
            test_id="t1",
            candidate_id="c1",
            format_="url",
        )

    @staticmethod
    def test_templates(sync_client: HackerRank) -> None:
        """Exercise the ``templates`` namespace."""
        sync_client.templates.list()
        sync_client.templates.list(limit=1, offset=0)
        sync_client.templates.get(template_id="tpl1")

    @staticmethod
    def test_users(sync_client: HackerRank) -> None:
        """Exercise the ``users`` namespace."""
        sync_client.users.list()
        sync_client.users.list(limit=1, offset=0)
        sync_client.users.search(search="alice")
        sync_client.users.search(
            search="alice",
            limit=1,
            offset=0,
        )
        sync_client.users.create(email="u@x.com")
        sync_client.users.create(
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
        sync_client.users.get(user_id="u1")
        sync_client.users.update(
            user_id="u1",
            body={"firstname": "Alice"},
        )
        sync_client.users.delete(user_id="u1")

    @staticmethod
    def test_teams(sync_client: HackerRank) -> None:
        """Exercise the ``teams`` namespace."""
        sync_client.teams.list()
        sync_client.teams.list(limit=1, offset=0)
        sync_client.teams.create(name="t")
        sync_client.teams.create(
            name="t",
            recruiter_cap=5,
            developer_cap=5,
            invite_as="recruiter",
            locations=["NYC"],
            departments=["Eng"],
        )
        sync_client.teams.get(team_id="tm1")
        sync_client.teams.update(team_id="tm1")
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

    @staticmethod
    def test_team_memberships(sync_client: HackerRank) -> None:
        """Exercise the ``teams.memberships`` namespace."""
        ns = sync_client.teams.memberships
        ns.list(team_id="tm1")
        ns.list(team_id="tm1", limit=1, offset=0)
        ns.get(team_id="tm1", user_id="u1")
        ns.create(team_id="tm1", user_id="u1")
        ns.create(team_id="tm1", user_id="u1", license="developer")
        ns.delete(team_id="tm1", user_id="u1")

    @staticmethod
    def test_audit_logs(sync_client: HackerRank) -> None:
        """Exercise the ``audit_logs`` namespace."""
        sync_client.audit_logs.list()
        sync_client.audit_logs.list(
            limit=1,
            offset=0,
            user_id="u1",
        )

    @staticmethod
    def test_ats(sync_client: HackerRank) -> None:
        """Exercise the ``ats`` namespace."""
        sync_client.ats.codepair.invite()
        sync_client.ats.codepair.invite(
            title="t",
            requisition_id="r",
            candidate_id="c",
            candidate={"email": "x@y.com"},
            send_email=True,
            interview_metadata={"x": "y"},
        )
        sync_client.ats.codescreen.invite(
            test_id="t1",
            email="c@x.com",
        )
        sync_client.ats.codescreen.invite(
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

    @staticmethod
    def test_scim(sync_client: HackerRank) -> None:
        """Exercise the SCIM namespaces."""
        sync_client.scim.users.list()
        sync_client.scim.users.list(limit=1, offset=0)
        sync_client.scim.users.create(
            body={"userName": "u@x.com"},
        )
        sync_client.scim.users.get(scim_user_id="scim-1")
        sync_client.scim.users.replace(
            scim_user_id="scim-1",
            body={"userName": "u@x.com"},
        )
        sync_client.scim.users.patch(
            scim_user_id="scim-1",
            operations=[{"op": "replace"}],
        )
        sync_client.scim.users.delete(scim_user_id="scim-1")
        sync_client.scim.groups.list()
        sync_client.scim.groups.create(
            body={"displayName": "G"},
        )
        sync_client.scim.groups.get(scim_group_id="scim-2")
        sync_client.scim.groups.patch(
            scim_group_id="scim-2",
            operations=[{"op": "replace"}],
        )
        sync_client.scim.groups.delete(scim_group_id="scim-2")


class TestAsyncEndpoints:
    """Async client endpoint coverage."""

    @staticmethod
    @pytest.mark.asyncio
    async def test_interviews(
        async_client: AsyncHackerRank,
    ) -> None:
        """Exercise the async ``interviews`` namespace."""
        await async_client.interviews.list()
        await async_client.interviews.list(limit=1, offset=0)
        await async_client.interviews.create()
        await async_client.interviews.create(
            title="t",
            from_="2024",
            to="2024",
            interview_template_id=1,
            candidate={"email": "c@x.com"},
            send_email=True,
            metadata={"x": "y"},
            interviewers=["a@b.com"],
        )
        await async_client.interviews.get(interview_id="iv1")
        await async_client.interviews.delete(interview_id="iv1")
        await async_client.interviews.get_transcript(
            interview_id="iv1",
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_interview_templates(
        async_client: AsyncHackerRank,
    ) -> None:
        """Exercise the async ``interview_templates`` namespace."""
        await async_client.interview_templates.list()
        await async_client.interview_templates.list(
            limit=1,
            offset=0,
        )
        await async_client.interview_templates.get(template_id=1)

    @staticmethod
    @pytest.mark.asyncio
    async def test_questions(
        async_client: AsyncHackerRank,
    ) -> None:
        """Exercise the async ``questions`` namespace."""
        await async_client.questions.list()
        await async_client.questions.list(limit=1, offset=0)
        await async_client.questions.create(name="Q", type="code")
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
        await async_client.questions.get(question_id="q1")
        await async_client.questions.update(
            question_id="q1",
            scoring_command="npm run grade",
        )
        await async_client.questions.upload_project_zip(
            question_id="q1",
            file=b"zip",
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_environments(
        async_client: AsyncHackerRank,
    ) -> None:
        """Exercise the async ``environments`` namespace."""
        await async_client.environments.list()
        await async_client.environments.get(environment_id=92)

    @staticmethod
    @pytest.mark.asyncio
    async def test_tests(
        async_client: AsyncHackerRank,
    ) -> None:
        """Exercise the async ``tests`` namespace."""
        await async_client.tests.list()
        await async_client.tests.list(limit=1, offset=0)
        await async_client.tests.get(test_id="t1")
        await async_client.tests.list_inviters(test_id="t1")
        await async_client.tests.list_inviters(
            test_id="t1",
            limit=1,
            offset=0,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_test_candidates(
        async_client: AsyncHackerRank,
    ) -> None:
        """Exercise the async ``tests.candidates`` namespace."""
        ns = async_client.tests.candidates
        await ns.list(test_id="t1")
        await ns.list(test_id="t1", limit=1, offset=0)
        await ns.invite(test_id="t1", email="c@x.com")
        await ns.invite(
            test_id="t1",
            email="c@x.com",
            full_name="A",
            send_email=True,
        )
        await ns.get(test_id="t1", candidate_id="c1")

    @staticmethod
    @pytest.mark.asyncio
    async def test_templates(
        async_client: AsyncHackerRank,
    ) -> None:
        """Exercise the async ``templates`` namespace."""
        await async_client.templates.list()
        await async_client.templates.list(limit=1, offset=0)

    @staticmethod
    @pytest.mark.asyncio
    async def test_users(
        async_client: AsyncHackerRank,
    ) -> None:
        """Exercise the async ``users`` namespace."""
        await async_client.users.list()
        await async_client.users.list(limit=1, offset=0)
        await async_client.users.get(user_id="u1")

    @staticmethod
    @pytest.mark.asyncio
    async def test_teams(
        async_client: AsyncHackerRank,
    ) -> None:
        """Exercise the async ``teams`` namespace."""
        await async_client.teams.list()
        await async_client.teams.list(limit=1, offset=0)
        await async_client.teams.get(team_id="tm1")
        await async_client.teams.list_members(team_id="tm1")
        await async_client.teams.list_members(
            team_id="tm1",
            limit=1,
            offset=0,
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_audit_logs(
        async_client: AsyncHackerRank,
    ) -> None:
        """Exercise the async ``audit_logs`` namespace."""
        await async_client.audit_logs.list()
        await async_client.audit_logs.list(
            limit=1,
            offset=0,
            user_id="u1",
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_ats(
        async_client: AsyncHackerRank,
    ) -> None:
        """Exercise the async ``ats`` namespace."""
        await async_client.ats.codepair_invite(body={"title": "x"})
        await async_client.ats.codescreen_invite(
            body={"test_id": "t1", "email": "c@x.com"},
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_scim(
        async_client: AsyncHackerRank,
    ) -> None:
        """Exercise the async SCIM namespaces."""
        await async_client.scim.list_users()
        await async_client.scim.list_users(limit=1, offset=0)
        await async_client.scim.list_groups()
        await async_client.scim.list_groups(limit=1, offset=0)
