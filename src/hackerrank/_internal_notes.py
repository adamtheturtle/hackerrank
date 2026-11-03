"""Build required fields for question-note updates."""

from hackerrank.types import JSONValue, Question


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
