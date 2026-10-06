"""Tests for `hackerrank` candidates models."""

from hackerrank.types import (
    CandidateInvite,
    CandidateSearchAttemptResult,
    CandidateSearchResult,
    Inviter,
    TestCandidate,
)


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


def test_test_candidate_added_time_string_and_int() -> None:
    """``TestCandidate.from_dict`` accepts string or int
    added_time.
    """
    as_string = TestCandidate.from_dict(
        data={
            "id": "98Sjnbj12",
            "email": "alice.wonders@email.com",
            "added_time": "30",
        },
    )
    assert as_string.added_time == "30"

    as_int = TestCandidate.from_dict(
        data={
            "id": "98Sjnbj12",
            "email": "alice.wonders@email.com",
            "added_time": 0,
        },
    )
    assert as_int.added_time == 0

    absent = TestCandidate.from_dict(
        data={
            "id": "98Sjnbj12",
            "email": "alice.wonders@email.com",
        },
    )
    assert absent.added_time is None


def test_candidate_invite_from_dict() -> None:
    """``CandidateInvite.from_dict`` keeps test_link and id."""
    invite = CandidateInvite.from_dict(
        data={
            "test_link": "https://example.test/invite",
            "email": "a@example.com",
            "id": 10000,
        },
    )
    assert invite.test_link == "https://example.test/invite"
    assert invite.email == "a@example.com"
    invite_id = 10000
    assert invite.id == invite_id


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


def test_candidate_search_result_from_dict() -> None:
    """``CandidateSearchResult.from_dict`` parses nested attempts."""
    result = CandidateSearchResult.from_dict(
        data={
            "uuid": "u1",
            "name": "Jane",
            "email": "jane@example.com",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-06-01T00:00:00Z",
            "attempts": [
                {
                    "attempt_id": "a1",
                    "test_id": "t1",
                    "report_url": "https://example.com/report",
                    "score": 10.0,
                },
                {
                    "attempt_id": "a2",
                    "test_id": "t2",
                    "report_url": "https://example.com/report-2",
                },
            ],
        },
    )
    assert result.uuid == "u1"
    expected_attempts = 2
    expected_score = 10.0
    expected_percentage = 50.0
    assert len(result.attempts) == expected_attempts
    assert result.attempts[0].score == expected_score
    assert result.attempts[1].percentage_score is None
    attempt = CandidateSearchAttemptResult.from_dict(
        data={
            "attempt_id": "a3",
            "test_id": "t3",
            "report_url": "https://example.com/r",
            "percentage_score": expected_percentage,
            "attempt_starttime": "2024-02-01T00:00:00Z",
            "attempt_endtime": "2024-02-01T01:00:00Z",
        },
    )
    assert attempt.percentage_score == expected_percentage
    assert attempt.attempt_endtime == "2024-02-01T01:00:00Z"
