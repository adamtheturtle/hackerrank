"""Prepare and verify updates that change only question notes."""

from collections.abc import Callable
from dataclasses import replace

from hackerrank.types import JSONValue, Question


def notes_match(
    *,
    actual: str | None,
    expected: str,
    notes_equal: Callable[[str, str], bool] | None,
) -> bool:
    """Compare notes using exact text or a caller's comparison policy."""
    actual_text = "" if actual is None else actual
    if notes_equal is None:
        return actual_text == expected
    return notes_equal(actual_text, expected)


def check_question_id(*, question: Question, question_id: str) -> None:
    """Reject a response for a different question before any update."""
    if question.id != question_id:
        message = f"Expected question {question_id}, received {question.id}"
        raise ValueError(message)


def internal_notes_body(
    *, question: Question, internal_notes: str
) -> dict[str, JSONValue]:
    """Resend required update fields unchanged and omit optional
    changes.
    """
    if (
        question.problem_statement is None
        or question.recommended_duration is None
    ):
        message = (
            f"Question {question.id} lacks fields required to update notes"
        )
        raise ValueError(message)
    return {
        "name": question.name,
        "type": question.type,
        "internal_notes": internal_notes,
        "languages": []
        if question.languages is None
        else list(question.languages),
        "problem_statement": question.problem_statement,
        "recommended_duration": question.recommended_duration,
        "tags": [] if question.tags is None else list(question.tags),
        "options": [] if question.options is None else list(question.options),
        "answer": [] if question.answer is None else question.answer,
    }


def _without_notes(*, question: Question) -> Question:
    """Normalize optional required lists while retaining scalar
    answers.
    """
    return replace(
        question,
        internal_notes=None,
        languages=[] if question.languages is None else question.languages,
        tags=[] if question.tags is None else question.tags,
        options=[] if question.options is None else question.options,
        answer=[] if question.answer is None else question.answer,
    )


def verify_internal_notes(
    *,
    before: Question,
    after: Question,
    internal_notes: str,
    notes_equal: Callable[[str, str], bool] | None,
) -> None:
    """Verify saved notes and every other modeled question field."""
    if not notes_match(
        actual=after.internal_notes,
        expected=internal_notes,
        notes_equal=notes_equal,
    ):
        message = f"HackerRank did not retain notes for question {before.id}"
        raise ValueError(message)
    if _without_notes(question=before) != _without_notes(question=after):
        message = f"Question {before.id} changed fields other than notes"
        raise ValueError(message)
