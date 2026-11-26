"""Plan changes to an interview template's question membership."""

from collections.abc import Sequence
from dataclasses import dataclass

from hackerrank.types import InterviewTemplate


@dataclass(frozen=True, kw_only=True)
class _QuestionMembershipChanges:
    """The question IDs to add and remove."""

    additions: list[int]
    removals: list[int]


def question_membership_changes(
    *, template: InterviewTemplate, question_ids: Sequence[int]
) -> _QuestionMembershipChanges:
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
    return _QuestionMembershipChanges(additions=additions, removals=removals)
