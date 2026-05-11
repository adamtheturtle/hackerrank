"""Tests for HackerRank typed dataclasses."""

from hackerrank.types import (
    ATSCodePair,
    ATSCodeScreen,
    AuditLog,
    Interview,
    InterviewTemplate,
    InterviewTranscript,
    Inviter,
    Page,
    Question,
    SCIMPage,
    SCIMTeam,
    SCIMUser,
    Team,
    Template,
    Test,
    TestCandidate,
    User,
    UserTeamMembership,
)


class TestPage:
    """Tests for ``Page``."""

    @staticmethod
    def test_construct_empty() -> None:
        """An empty ``Page`` exposes pagination metadata."""
        page: Page[int] = Page(
            page_total=0,
            offset=0,
            previous="",
            next_="",
            first="",
            last="",
            total=0,
        )
        assert page.total == 0
        assert page.data == []

    @staticmethod
    def test_construct_with_items() -> None:
        """Items pass through ``Page`` as a list."""
        expected_items = [1, 2, 3]
        expected_total = len(expected_items)
        page: Page[int] = Page(
            expected_items,
            page_total=expected_total,
            offset=0,
            previous="",
            next_="",
            first="",
            last="",
            total=expected_total,
        )
        assert list(page) == expected_items
        assert page.data == expected_items
        assert page.total == expected_total


class TestSCIMPage:
    """Tests for ``SCIMPage``."""

    @staticmethod
    def test_construct_empty() -> None:
        """An empty ``SCIMPage`` exposes SCIM metadata."""
        page: SCIMPage[int] = SCIMPage(
            schemas=[],
            start_index=1,
            items_per_page=0,
            total_results=0,
        )
        assert page.total_results == 0
        assert page.start_index == 1


class TestFromDict:
    """Tests for the ``from_dict`` constructors."""

    @staticmethod
    def test_interview_from_minimal_dict() -> None:
        """``Interview.from_dict`` accepts a minimal payload."""
        interview = Interview.from_dict(
            data={
                "id": "1",
                "status": "scheduled",
                "url": "https://example.com",
            },
        )
        assert interview.id == "1"
        assert interview.status == "scheduled"
        assert interview.title is None

    @staticmethod
    def test_test_from_dict() -> None:
        """``Test.from_dict`` populates the dataclass."""
        duration_minutes = 60
        test = Test.from_dict(
            data={
                "id": "t1",
                "name": "My Test",
                "duration": duration_minutes,
            },
        )
        assert test.id == "t1"
        assert test.name == "My Test"
        assert test.duration == duration_minutes

    @staticmethod
    def test_question_from_dict() -> None:
        """``Question.from_dict`` populates the dataclass."""
        question = Question.from_dict(
            data={
                "id": "q1",
                "type": "code",
                "name": "Reverse a string",
            },
        )
        assert question.id == "q1"
        assert question.type == "code"

    @staticmethod
    def test_user_from_dict() -> None:
        """``User.from_dict`` populates the dataclass."""
        user = User.from_dict(
            data={
                "id": "u1",
                "email": "alice@example.com",
                "firstname": "Alice",
            },
        )
        assert user.firstname == "Alice"

    @staticmethod
    def test_team_from_dict() -> None:
        """``Team.from_dict`` populates the dataclass."""
        developer_cap = 10
        team = Team.from_dict(
            data={
                "id": "tm1",
                "name": "Engineering",
                "developer_cap": developer_cap,
            },
        )
        assert team.developer_cap == developer_cap

    @staticmethod
    def test_user_team_membership_from_dict() -> None:
        """``UserTeamMembership.from_dict`` populates the dataclass."""
        membership = UserTeamMembership.from_dict(
            data={"team": "tm1", "user": "u1"},
        )
        assert membership.team == "tm1"
        assert membership.user == "u1"

    @staticmethod
    def test_template_from_dict() -> None:
        """``Template.from_dict`` populates the dataclass."""
        template = Template.from_dict(
            data={"id": "tpl1", "name": "Greeting"},
        )
        assert template.name == "Greeting"

    @staticmethod
    def test_interview_template_from_dict() -> None:
        """``InterviewTemplate.from_dict`` populates the dataclass."""
        template = InterviewTemplate.from_dict(
            data={"id": 1, "name": "Standard"},
        )
        assert template.id == 1

    @staticmethod
    def test_interview_transcript_from_dict() -> None:
        """``InterviewTranscript.from_dict`` parses messages."""
        transcript = InterviewTranscript.from_dict(
            data={
                "messages": [
                    {
                        "author": "Alice",
                        "timestamp": 1,
                        "text": "hi",
                        "candidate": False,
                        "messageId": "m1",
                    },
                ],
            },
        )
        assert len(transcript.messages) == 1
        assert transcript.messages[0].message_id == "m1"

    @staticmethod
    def test_audit_log_from_dict() -> None:
        """``AuditLog.from_dict`` populates the dataclass."""
        log = AuditLog.from_dict(
            data={
                "source_id": 1,
                "source_type": "Test",
                "action": "create",
            },
        )
        assert log.action == "create"

    @staticmethod
    def test_test_candidate_from_dict() -> None:
        """``TestCandidate.from_dict`` populates the dataclass."""
        candidate = TestCandidate.from_dict(
            data={
                "id": "c1",
                "email": "bob@example.com",
                "tags": ["foo"],
                "candidate_details": [
                    {
                        "field_name": "f",
                        "title": "t",
                        "value": "v",
                    },
                ],
            },
        )
        assert candidate.tags == ["foo"]
        assert candidate.candidate_details is not None
        assert candidate.candidate_details[0].field_name == "f"

    @staticmethod
    def test_inviter_from_dict() -> None:
        """``Inviter.from_dict`` populates the dataclass."""
        inviter = Inviter.from_dict(
            data={
                "id": "i1",
                "email": "inviter@example.com",
                "role": "recruiter",
            },
        )
        assert inviter.role == "recruiter"

    @staticmethod
    def test_ats_codepair_from_dict() -> None:
        """``ATSCodePair.from_dict`` populates the dataclass."""
        codepair = ATSCodePair.from_dict(
            data={
                "title": "Codepair",
                "requisition_id": "req-1",
                "candidate_id": "cand-1",
            },
        )
        assert codepair.title == "Codepair"

    @staticmethod
    def test_ats_codescreen_from_dict() -> None:
        """``ATSCodeScreen.from_dict`` populates the dataclass."""
        codescreen = ATSCodeScreen.from_dict(
            data={
                "test_id": "t1",
                "email": "x@example.com",
            },
        )
        assert codescreen.email == "x@example.com"

    @staticmethod
    def test_scim_user_from_dict() -> None:
        """``SCIMUser.from_dict`` populates the dataclass."""
        scim_user = SCIMUser.from_dict(
            data={
                "id": "scim-1",
                "userName": "alice@example.com",
                "active": True,
            },
        )
        assert scim_user.user_name == "alice@example.com"
        assert scim_user.active is True

    @staticmethod
    def test_scim_team_from_dict_uses_displayname() -> None:
        """``SCIMTeam.from_dict`` prefers ``displayName``."""
        scim_team = SCIMTeam.from_dict(
            data={
                "id": "scim-2",
                "displayName": "Engineering",
            },
        )
        assert scim_team.display_name == "Engineering"

    @staticmethod
    def test_scim_team_from_dict_falls_back_to_typo() -> None:
        """``SCIMTeam.from_dict`` falls back to ``diplayName``.

        The HackerRank OpenAPI spec contains a typo
        (``diplayName``) and clients should still parse it.
        """
        scim_team = SCIMTeam.from_dict(
            data={
                "id": "scim-2",
                "diplayName": "Engineering",
            },
        )
        assert scim_team.display_name == "Engineering"
