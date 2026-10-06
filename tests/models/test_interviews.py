"""Tests for `hackerrank` interviews models."""

from hackerrank.types import (
    Interview,
    Interviewer,
)


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


def test_interview_from_object_interviewers() -> None:
    """``Interview.from_dict`` accepts object-form interviewers."""
    interview = Interview.from_dict(
        data={
            "id": "289187",
            "status": "active",
            "url": "www.hackerrank.com/paper/demo",
            "interviewers": [
                {"email": "hina@techcorp.com", "name": "Hina"},
                "other@techcorp.com",
            ],
        },
    )
    assert interview.interviewers is not None
    first = interview.interviewers[0]
    assert isinstance(first, Interviewer)
    assert first.email == "hina@techcorp.com"
    assert first.name == "Hina"
    assert interview.interviewers[1] == "other@techcorp.com"


def test_interview_preserves_schedule_and_live_fields() -> None:
    """``Interview.from_dict`` keeps scheduled and live fields."""
    interview = Interview.from_dict(
        data={
            "id": "i",
            "status": "ended",
            "url": "https://example.test/i",
            "from": "2026-08-19T01:09:27+0000",
            "to": "2026-08-19T02:09:27+0000",
            "started_at": "2026-08-18T01:09:27+0000",
            "ai_assistant_available": True,
        },
    )
    assert interview.from_ == "2026-08-19T01:09:27+0000"
    assert interview.to == "2026-08-19T02:09:27+0000"
    assert interview.started_at == "2026-08-18T01:09:27+0000"
    assert interview.ai_assistant_available is True
