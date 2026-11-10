"""Build complete question updates from selected metadata changes."""

from hackerrank._question_validation import validate_question_prompt_body
from hackerrank.types import JSONValue, Question, QuestionChanges


def question_update_body(
    *, question: Question, changes: QuestionChanges
) -> dict[str, JSONValue]:
    """Preserve required fields and omit other optional updates."""
    body: dict[str, JSONValue] = {
        "name": question.name,
        "type": str(object=question.type),
        "internal_notes": ""
        if question.internal_notes is None
        else question.internal_notes,
        "languages": [] if question.languages is None else question.languages,
        "problem_statement": question.problem_statement,
        "recommended_duration": question.recommended_duration,
        "tags": [] if question.tags is None else question.tags,
        "options": [] if question.options is None else question.options,
        "answer": [] if question.answer is None else question.answer,
    }
    body.update(changes.to_dict())
    if (
        body["problem_statement"] is None
        or body["recommended_duration"] is None
    ):
        message = (
            f"Question {question.id} lacks fields required to update metadata"
        )
        raise ValueError(message)
    validate_question_prompt_body(body=body)
    return body
