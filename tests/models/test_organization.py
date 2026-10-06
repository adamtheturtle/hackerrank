"""Tests for `hackerrank` organization models."""

from hackerrank.types import (
    AuditLog,
    InterviewTemplate,
    InterviewTranscript,
    Team,
    Template,
    User,
    UserTeamMembership,
)


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


def test_user_team_membership_from_dict() -> None:
    """``UserTeamMembership.from_dict`` populates the dataclass."""
    membership = UserTeamMembership.from_dict(
        data={"team": "tm1", "user": "u1"},
    )
    assert membership.team == "tm1"
    assert membership.user == "u1"


def test_template_from_dict() -> None:
    """``Template.from_dict`` populates the dataclass."""
    template = Template.from_dict(
        data={"id": "tpl1", "name": "Greeting"},
    )
    assert template.name == "Greeting"


def test_interview_template_from_dict() -> None:
    """``InterviewTemplate.from_dict`` populates the dataclass."""
    template = InterviewTemplate.from_dict(
        data={
            "id": "template-1",
            "name": "Standard",
            "questions": [2687118, "2687119"],
        },
    )
    assert template.id == "template-1"
    assert template.questions == [2687118, 2687119]


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
