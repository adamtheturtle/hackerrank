"""Plan changes to an interview template's question membership."""

from collections.abc import Sequence
from dataclasses import dataclass

from hackerrank.types import InterviewTemplate

QUESTION_ADD_PAUSE_SECONDS = 2


@dataclass(frozen=True, kw_only=True)
class _QuestionMembershipChanges:
    """The question IDs to add and remove."""

    additions: list[int]
    removals: list[int]


def template_question_ids(*, template: InterviewTemplate) -> list[int]:
    """Return the stored membership when the API includes it."""
    if template.questions is None:
        message = (
            f"Interview template {template.id} omitted question membership."
        )
        raise ValueError(message)
    return template.questions


def question_membership_changes(
    *, template: InterviewTemplate, question_ids: Sequence[int]
) -> _QuestionMembershipChanges:
    """Return unique additions and removals from a known membership."""
    actual = set(template_question_ids(template=template))
    additions = [
        question_id
        for question_id in dict.fromkeys(question_ids)
        if question_id not in actual
    ]
    removals = sorted(actual.difference(question_ids))
    return _QuestionMembershipChanges(additions=additions, removals=removals)
