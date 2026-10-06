"""Tests for `hackerrank` integration models."""

from hackerrank.types import (
    ATSCodePair,
    ATSCodeScreen,
    SCIMMessage,
    SCIMTeam,
    SCIMUser,
    TestsUpdate,
    UserUpdate,
)


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


def test_ats_codescreen_from_dict() -> None:
    """``ATSCodeScreen.from_dict`` populates the dataclass."""
    codescreen = ATSCodeScreen.from_dict(
        data={
            "test_id": "t1",
            "email": "x@example.com",
        },
    )
    assert codescreen.email == "x@example.com"


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


def test_scim_team_from_dict_uses_displayname() -> None:
    """``SCIMTeam.from_dict`` prefers ``displayName``."""
    scim_team = SCIMTeam.from_dict(
        data={
            "id": "scim-2",
            "displayName": "Engineering",
        },
    )
    assert scim_team.display_name == "Engineering"


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


def test_user_update_to_dict() -> None:
    """``UserUpdate.to_dict`` serializes required fields."""
    body = UserUpdate(
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
        team_admin=True,
    )
    assert body.to_dict()["team_admin"] is True


def test_tests_update_to_dict() -> None:
    """``TestsUpdate.to_dict`` serializes required fields."""
    expected_duration = 60
    expected_questions = ["q1"]
    body = TestsUpdate(
        name="T",
        starttime="2024",
        endtime="2024",
        duration=expected_duration,
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
        questions=expected_questions,
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
    assert body.to_dict()["duration"] == expected_duration
    assert body.to_dict()["questions"] == expected_questions


def test_scim_message_from_dict() -> None:
    """``SCIMMessage.from_dict`` populates the dataclass."""
    message = SCIMMessage.from_dict(
        data={
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:User",
            ],
            "message": "Successful transaction",
        },
    )
    assert message.message == "Successful transaction"
    assert message.schemas == [
        "urn:ietf:params:scim:schemas:core:2.0:User",
    ]
