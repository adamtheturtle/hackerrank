"""Plan changes to an interview template's question membership."""

from collections.abc import Sequence

from hackerrank.types import InterviewTemplate


def question_membership_changes(
    *, template: InterviewTemplate, question_ids: Sequence[int]
) -> tuple[list[int], list[int]]:
    """Return unique additions and removals from a known membership."""
    if template.questions is None:
        message = (
            f"Interview template {template.id} omitted question membership."
        )
        raise ValueError(message)
    actual = set(template.questions)
    additions = [
        question_id
        for question_id in dict.fromkeys(question_ids)
        if question_id not in actual
    ]
    removals = sorted(actual.difference(question_ids))
    return additions, removals
