"""Tests for `hackerrank` assessments models."""

from hackerrank.types import (
    Environment,
    Question,
    Test,
    TestCandidateDetailField,
)


def test_test_from_dict() -> None:
    """``Test.from_dict`` populates the dataclass."""
    duration_minutes = 60
    test = Test.from_dict(
        data={
            "id": "t1",
            "name": "My Test",
            "duration": duration_minutes,
        },
    )
    assert test.id == "t1"
    assert test.name == "My Test"
    assert test.duration == duration_minutes


def test_test_from_object_candidate_details_and_sections() -> None:
    """``Test.from_dict`` accepts object candidate details and
    sections.
    """
    test = Test.from_dict(
        data={
            "id": "1PxfG1348",
            "name": "Java Challenge",
            "candidate_details": [
                {"predefined_label": "full_name", "required": True},
                "legacy-field",
            ],
            "sections": {"section-1": {"name": "Core"}},
        },
    )
    assert test.candidate_details is not None
    first = test.candidate_details[0]
    assert isinstance(first, TestCandidateDetailField)
    assert first.predefined_label == "full_name"
    assert first.required is True
    assert test.candidate_details[1] == "legacy-field"
    assert test.sections == {"section-1": {"name": "Core"}}


def test_question_from_dict() -> None:
    """``Question.from_dict`` populates the dataclass."""
    environment_id = 92
    test_case_count = 2
    question = Question.from_dict(
        data={
            "id": "q1",
            "type": "code",
            "name": "Reverse a string",
            "environment_id": environment_id,
            "file_path": "question_projects/q1/project.zip",
            "file_url": "https://example.com/project.zip",
            "fullstack_project_details": {"name": "PERN"},
            "has_valid_stacks": True,
            "test_case_count": test_case_count,
        },
    )
    assert question.id == "q1"
    assert question.type == "code"
    assert question.environment_id == environment_id
    assert question.file_path == "question_projects/q1/project.zip"
    assert question.file_url == "https://example.com/project.zip"
    assert question.fullstack_project_details == {"name": "PERN"}
    assert question.has_valid_stacks is True
    assert question.test_case_count == test_case_count


def test_environment_from_dict() -> None:
    """``Environment.from_dict`` populates the dataclass."""
    environment_id = 92
    environment = Environment.from_dict(
        data={
            "id": environment_id,
            "name": "PERN",
            "tags": ["fullstack"],
            "runtime": [{"name": "Node", "version": "20"}],
            "active": True,
            "sample_project_url": "https://example.com/project.zip",
        },
    )
    assert environment.id == environment_id
    assert environment.runtime[0].name == "Node"
    assert environment.active is True
    assert environment.sample_project_url == "https://example.com/project.zip"
