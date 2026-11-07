"""Response models for Interviews V2 artifacts and interviewer notes."""

from dataclasses import dataclass
from typing import Self, TypedDict

from hackerrank._responses import (
    optional_response,
    response_data,
    response_items,
)


class _Descriptor(TypedDict):
    """An artifact download descriptor."""

    state: str
    location: str | None


class _Question(TypedDict):
    """Saved question metadata and available artifact descriptors."""

    tab_id: str
    question_sequence: int
    library_question_id: str | None
    qtype: str
    artifacts: dict[str, _Descriptor]


class _NoteReference(TypedDict):
    """A note identifier returned with artifacts."""

    note_id: int
    evaluator_id: int


@dataclass(frozen=True, kw_only=True)
class InterviewArtifactDescriptor:
    """An artifact's availability and temporary signed download URL."""

    state: str
    location: str | None


@dataclass(frozen=True, kw_only=True)
class InterviewArtifactQuestion:
    """A saved question tab and its artifacts."""

    tab_id: str
    question_sequence: int
    library_question_id: str | None
    qtype: str
    artifacts: dict[str, InterviewArtifactDescriptor]
    question_name: str | None
    problem_statement: str | None
    role_type: str | None
    project_mode: str | None

    @classmethod
    def from_dict(cls, *, data: object) -> Self:
        """Decode a question, preserving unknown artifact names."""
        value = response_data(data, _Question)
        optional = response_data(data, dict[str, object])
        return cls(
            tab_id=value["tab_id"],
            question_sequence=value["question_sequence"],
            library_question_id=value["library_question_id"],
            qtype=value["qtype"],
            artifacts={
                key: InterviewArtifactDescriptor(
                    state=descriptor["state"],
                    location=descriptor["location"],
                )
                for key, descriptor in value["artifacts"].items()
            },
            question_name=optional_response(
                optional.get("question_name"), str
            ),
            problem_statement=optional_response(
                optional.get("problem_statement"), str
            ),
            role_type=optional_response(optional.get("role_type"), str),
            project_mode=optional_response(optional.get("project_mode"), str),
        )


@dataclass(frozen=True, kw_only=True)
class InterviewArtifactNote:
    """A reference to a note; content comes from the notes endpoint."""

    note_id: int
    evaluator_id: int


@dataclass(frozen=True, kw_only=True)
class InterviewArtifacts:
    """Available artifact metadata for an ended Interviews V2
    interview.
    """

    interview_id: str
    transcript_url: InterviewArtifactDescriptor
    interviewer_notes: list[InterviewArtifactNote]
    questions: list[InterviewArtifactQuestion]

    @classmethod
    def from_dict(cls, *, data: object) -> Self:
        """Decode the unwrapped artifact response."""
        value = response_data(data, dict[str, object])
        transcript = response_data(value["transcript_url"], _Descriptor)
        return cls(
            interview_id=response_data(value["interview_id"], str),
            transcript_url=InterviewArtifactDescriptor(
                state=transcript["state"],
                location=transcript["location"],
            ),
            interviewer_notes=[
                InterviewArtifactNote(
                    note_id=note["note_id"], evaluator_id=note["evaluator_id"]
                )
                for note in response_items(
                    value=value["interviewer_notes"], item_type=_NoteReference
                )
            ],
            questions=[
                InterviewArtifactQuestion.from_dict(data=question)
                for question in response_data(value["questions"], list[object])
            ],
        )


@dataclass(frozen=True, kw_only=True)
class InterviewArtifactsPending:
    """HTTP 202 result; callers may request again after retry_after
    seconds.
    """

    message: str
    retry_after: int | None


@dataclass(frozen=True, kw_only=True)
class InterviewNote:
    """An interviewer note, restricted by the caller's report
    permissions.
    """

    note_id: int | None
    evaluator_id: int | None
    evaluator_name: str | None
    content: str | None
    updated_at: str | None
    editable: bool | None

    @classmethod
    def from_dict(cls, *, data: object) -> Self:
        """Decode a GET note or the smaller PATCH response."""
        value = response_data(data, dict[str, object])
        return cls(
            note_id=optional_response(value.get("note_id"), int),
            evaluator_id=optional_response(value.get("evaluator_id"), int),
            evaluator_name=optional_response(value.get("evaluator_name"), str),
            content=optional_response(value.get("content"), str),
            updated_at=optional_response(value.get("updated_at"), str),
            editable=optional_response(value.get("editable"), bool),
        )
