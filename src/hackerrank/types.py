"""Types for the HackerRank for Work API."""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any, ClassVar, Self

from beartype import beartype

from hackerrank._dict_types import (
    ATSCodePairDict,
    ATSCodeScreenDict,
    AuditLogDict,
    CandidateDetailDict,
    CandidateInviteDict,
    CandidateSearchAttemptResultDict,
    CandidateSearchResultDict,
    EnvironmentDict,
    EnvironmentRuntimeDict,
    InterviewDict,
    InterviewerDict,
    InterviewTemplateDict,
    InterviewTranscriptDict,
    InterviewTranscriptMessageDict,
    InviterDict,
    QuestionDict,
    SCIMMessageDict,
    SCIMTeamDict,
    SCIMUserDict,
    TeamDict,
    TemplateDict,
    TestCandidateDetailFieldDict,
    TestCandidateDict,
    TestDict,
    UserDict,
    UserTeamMembershipDict,
)

type JSONValue = (
    str | int | float | bool | Sequence[Any] | Mapping[str, Any] | None
)
"""A JSON-compatible value.

Used for free-form fields such as ``metadata``, ``candidate``,
``accommodations`` and ``webhook_authentication`` — anything where
the HackerRank API accepts or returns an opaque blob constrained
only to be JSON-serialisable.

``Sequence`` / ``Mapping`` (rather than ``list`` / ``dict``) make
the alias accept narrower concrete types such as ``dict[str, str]``
without invariance issues. The inner ``Any`` keeps the alias
non-recursive so ``@beartype`` can resolve it at runtime.
"""


@beartype
class Page[T](list[T]):
    """A page of results with HackerRank's pagination metadata."""

    def __init__(
        self,
        iterable: Iterable[T] = (),
        /,
        *,
        page_total: int,
        offset: int,
        previous: str,
        next_: str,
        first: str,
        last: str,
        total: int,
    ) -> None:
        """Create a new page.

        Args:
            iterable: The items for the list.
            page_total: Count of items in the current page.
            offset: The offset of the current page.
            previous: URL of the previous page.
            next_: URL of the next page.
            first: URL of the first page.
            last: URL of the last page.
            total: Total number of items across all pages.
        """
        super().__init__(iterable)
        self.page_total = page_total
        self.offset = offset
        self.previous = previous
        self.next = next_
        self.first = first
        self.last = last
        self.total = total

    @property
    def data(self) -> list[T]:
        """Return the items as a plain list.

        Returns:
            A copy of the items in this page.
        """
        return list(self)


@beartype
class SCIMPage[T](list[T]):
    """A SCIM v2 paginated response.

    SCIM uses a different envelope from the v3 API.
    """

    def __init__(
        self,
        iterable: Iterable[T] = (),
        /,
        *,
        schemas: list[str],
        start_index: int,
        items_per_page: int,
        total_results: int,
    ) -> None:
        """Create a new SCIM page.

        Args:
            iterable: The items for the list.
            schemas: The SCIM schemas for the response.
            start_index: Index of the first item in the page.
            items_per_page: Number of items per page.
            total_results: Total number of items.
        """
        super().__init__(iterable)
        self.schemas = schemas
        self.start_index = start_index
        self.items_per_page = items_per_page
        self.total_results = total_results


@beartype
@dataclass(frozen=True, kw_only=True)
class CandidateDetail:
    """A custom candidate detail field."""

    field_name: str
    title: str
    value: str

    @classmethod
    def from_dict(cls, data: CandidateDetailDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            field_name=data["field_name"],
            title=data["title"],
            value=data["value"],
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class CandidateSearchAttemptResult:
    """A test attempt returned by global candidate search."""

    attempt_id: str
    test_id: str
    report_url: str
    score: float | None = None
    percentage_score: float | None = None
    attempt_starttime: str | None = None
    attempt_endtime: str | None = None

    @classmethod
    def from_dict(
        cls,
        data: CandidateSearchAttemptResultDict,
    ) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            attempt_id=data["attempt_id"],
            test_id=data["test_id"],
            report_url=data["report_url"],
            score=data.get("score"),
            percentage_score=data.get("percentage_score"),
            attempt_starttime=data.get("attempt_starttime"),
            attempt_endtime=data.get("attempt_endtime"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class CandidateSearchResult:
    """A candidate match from global candidate search."""

    uuid: str
    name: str
    email: str
    created_at: str
    updated_at: str
    attempts: list[CandidateSearchAttemptResult]

    @classmethod
    def from_dict(cls, data: CandidateSearchResultDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            uuid=data["uuid"],
            name=data["name"],
            email=data["email"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            attempts=[
                CandidateSearchAttemptResult.from_dict(data=item)
                for item in data["attempts"]
            ],
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class Interviewer:
    """An interviewer identified by email and optional name."""

    email: str
    name: str | None = None

    @classmethod
    def from_dict(cls, data: InterviewerDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            email=data["email"],
            name=data.get("name"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class Interview:
    """A HackerRank interview."""

    id: str
    status: str
    url: str
    title: str | None = None
    feedback: str | None = None
    thumbs_up: int | None = None
    notes: str | None = None
    resume_url: str | None = None
    interviewers: list[str | Interviewer] | None = None
    result_url: str | None = None
    candidate: dict[str, JSONValue] | None = None
    metadata: dict[str, JSONValue] | None = None
    report_url: str | None = None
    ended_at: str | None = None
    interview_template_id: int | None = None
    created_at: str | None = None
    updated_at: str | None = None
    user: int | None = None
    send_email: bool | None = None
    from_: str | None = None
    to: str | None = None
    started_at: str | None = None
    ai_assistant_available: bool | None = None

    @classmethod
    def from_dict(cls, data: InterviewDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        raw_interviewers = data.get("interviewers")
        interviewers: list[str | Interviewer] | None
        if raw_interviewers is None:
            interviewers = None
        else:
            interviewers = [
                item
                if isinstance(item, str)
                else Interviewer.from_dict(data=item)
                for item in raw_interviewers
            ]
        from_value = data.get("from")
        return cls(
            id=data["id"],
            status=data["status"],
            url=data["url"],
            title=data.get("title"),
            feedback=data.get("feedback"),
            thumbs_up=data.get("thumbs_up"),
            notes=data.get("notes"),
            resume_url=data.get("resume_url"),
            interviewers=interviewers,
            result_url=data.get("result_url"),
            candidate=data.get("candidate"),
            metadata=data.get("metadata"),
            report_url=data.get("report_url"),
            ended_at=data.get("ended_at"),
            interview_template_id=data.get(
                "interview_template_id",
            ),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            user=data.get("user"),
            send_email=data.get("send_email"),
            from_=from_value,
            to=data.get("to"),
            started_at=data.get("started_at"),
            ai_assistant_available=data.get(
                "ai_assistant_available",
            ),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class InterviewTranscriptMessage:
    """A single message in an interview transcript."""

    author: str
    timestamp: int
    text: str
    candidate: bool
    message_id: str
    email: str | None = None

    @classmethod
    def from_dict(
        cls,
        data: InterviewTranscriptMessageDict,
    ) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            author=data["author"],
            timestamp=data["timestamp"],
            text=data["text"],
            candidate=data["candidate"],
            message_id=data["messageId"],
            email=data.get("email"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class InterviewTranscript:
    """The transcript for an interview."""

    messages: list[InterviewTranscriptMessage]

    @classmethod
    def from_dict(cls, data: InterviewTranscriptDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            messages=[
                InterviewTranscriptMessage.from_dict(data=m)
                for m in data["messages"]
            ],
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class InterviewTemplate:
    """A HackerRank interview template."""

    id: str
    name: str
    created_at: str | None = None
    status: int | None = None
    user: int | None = None
    roles: list[str] | None = None
    team_share: int | None = None
    questions: list[int] | None = None
    scorecard: int | None = None
    import_template: bool | None = None
    editor_access: bool | None = None

    @classmethod
    def from_dict(cls, data: InterviewTemplateDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            id=str(object=data["id"]),
            name=data["name"],
            created_at=data.get("created_at"),
            status=data.get("status"),
            user=data.get("user"),
            roles=data.get("roles"),
            team_share=data.get("team_share"),
            questions=(
                [int(question_id) for question_id in data["questions"]]
                if "questions" in data
                else None
            ),
            scorecard=data.get("scorecard"),
            import_template=data.get("import_template"),
            editor_access=data.get("editor_access"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class EnvironmentRuntime:
    """A runtime component for a project-question environment."""

    name: str
    version: str

    @classmethod
    def from_dict(cls, data: EnvironmentRuntimeDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(name=data["name"], version=data["version"])


@beartype
@dataclass(frozen=True, kw_only=True)
class Environment:
    """A project-question environment."""

    id: int
    name: str
    tags: list[str]
    runtime: list[EnvironmentRuntime]
    active: bool | None = None
    sample_project_url: str | None = None

    @classmethod
    def from_dict(cls, data: EnvironmentDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            id=data["id"],
            name=data["name"],
            tags=data["tags"],
            runtime=[
                EnvironmentRuntime.from_dict(data=item)
                for item in data["runtime"]
            ],
            active=data.get("active"),
            sample_project_url=data.get("sample_project_url"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class Question:
    """A HackerRank question."""

    id: str
    type: str
    name: str
    unique_id: str | None = None
    owner: str | None = None
    created_at: str | None = None
    status: str | None = None
    internal_notes: str | None = None
    languages: list[str] | None = None
    problem_statement: str | None = None
    recommended_duration: int | None = None
    tags: list[str] | None = None
    max_score: float | None = None
    options: list[str] | None = None
    answer: int | list[int] | None = None
    test_case_count: int | None = None
    role_type: str | None = None
    environment_id: int | None = None
    file_url: str | None = None
    file_path: str | None = None
    has_valid_stacks: bool | None = None
    fullstack_project_details: dict[str, JSONValue] | None = None

    @classmethod
    def from_dict(cls, data: QuestionDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            id=data["id"],
            type=data["type"],
            name=data["name"],
            unique_id=data.get("unique_id"),
            owner=data.get("owner"),
            created_at=data.get("created_at"),
            status=data.get("status"),
            internal_notes=data.get("internal_notes"),
            languages=data.get("languages"),
            problem_statement=data.get("problem_statement"),
            recommended_duration=data.get(
                "recommended_duration",
            ),
            tags=data.get("tags"),
            max_score=data.get("max_score"),
            options=data.get("options"),
            answer=data.get("answer"),
            test_case_count=data.get("test_case_count"),
            role_type=data.get("role_type"),
            environment_id=data.get("environment_id"),
            file_url=data.get("file_url"),
            file_path=data.get("file_path"),
            has_valid_stacks=data.get("has_valid_stacks"),
            fullstack_project_details=data.get(
                "fullstack_project_details",
            ),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class TestCandidateDetailField:
    """A candidate-detail field descriptor configured on a test."""

    __test__: ClassVar[bool] = False

    predefined_label: str | None = None
    required: bool | None = None
    title: str | None = None
    type: str | None = None
    options: list[str] | None = None

    @classmethod
    def from_dict(cls, data: TestCandidateDetailFieldDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            predefined_label=data.get("predefined_label"),
            required=data.get("required"),
            title=data.get("title"),
            type=data.get("type"),
            options=data.get("options"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class Test:
    """A HackerRank test."""

    __test__: ClassVar[bool] = False

    id: str
    name: str
    unique_id: str | None = None
    starttime: str | None = None
    endtime: str | None = None
    duration: int | None = None
    owner: str | None = None
    instructions: str | None = None
    starred: bool | None = None
    created_at: str | None = None
    state: str | None = None
    locked: bool | None = None
    draft: bool | None = None
    languages: list[str] | None = None
    candidate_details: list[str | TestCandidateDetailField] | None = None
    custom_acknowledge_text: str | None = None
    cutoff_score: int | None = None
    master_password: str | None = None
    hide_compile_test: bool | None = None
    tags: list[str] | None = None
    role_ids: list[str] | None = None
    experience: list[str] | None = None
    questions: list[str] | None = None
    sections: dict[str, JSONValue] | None = None
    mcq_incorrect_score: int | None = None
    mcq_correct_score: int | None = None
    locked_by: str | None = None
    short_login_url: str | None = None
    public_login_url: str | None = None
    shuffle_questions: bool | None = None
    test_admins: list[str] | None = None
    hide_template: bool | None = None
    enable_acknowledgement: bool | None = None
    enable_proctoring: bool | None = None
    enable_advanced_proctoring: bool | None = None
    enable_secure_assessment_mode: bool | None = None
    enable_ml_plagiarism_analysis: bool | None = None
    enable_photo_identification: bool | None = None
    ide_config: str | None = None

    @classmethod
    def from_dict(cls, data: TestDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        raw_details = data.get("candidate_details")
        candidate_details: list[str | TestCandidateDetailField] | None
        if raw_details is None:
            candidate_details = None
        else:
            candidate_details = [
                item
                if isinstance(item, str)
                else TestCandidateDetailField.from_dict(data=item)
                for item in raw_details
            ]
        return cls(
            id=data["id"],
            name=data["name"],
            unique_id=data.get("unique_id"),
            starttime=data.get("starttime"),
            endtime=data.get("endtime"),
            duration=data.get("duration"),
            owner=data.get("owner"),
            instructions=data.get("instructions"),
            starred=data.get("starred"),
            created_at=data.get("created_at"),
            state=data.get("state"),
            locked=data.get("locked"),
            draft=data.get("draft"),
            languages=data.get("languages"),
            candidate_details=candidate_details,
            custom_acknowledge_text=data.get(
                "custom_acknowledge_text",
            ),
            cutoff_score=data.get("cutoff_score"),
            master_password=data.get("master_password"),
            hide_compile_test=data.get("hide_compile_test"),
            tags=data.get("tags"),
            role_ids=data.get("role_ids"),
            experience=data.get("experience"),
            questions=data.get("questions"),
            sections=data.get("sections"),
            mcq_incorrect_score=data.get("mcq_incorrect_score"),
            mcq_correct_score=data.get("mcq_correct_score"),
            locked_by=data.get("locked_by"),
            short_login_url=data.get("short_login_url"),
            public_login_url=data.get("public_login_url"),
            shuffle_questions=data.get("shuffle_questions"),
            test_admins=data.get("test_admins"),
            hide_template=data.get("hide_template"),
            enable_acknowledgement=data.get(
                "enable_acknowledgement",
            ),
            enable_proctoring=data.get("enable_proctoring"),
            enable_advanced_proctoring=data.get(
                "enable_advanced_proctoring",
            ),
            enable_secure_assessment_mode=data.get(
                "enable_secure_assessment_mode",
            ),
            enable_ml_plagiarism_analysis=data.get(
                "enable_ml_plagiarism_analysis",
            ),
            enable_photo_identification=data.get(
                "enable_photo_identification",
            ),
            ide_config=data.get("ide_config"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class TestCandidate:
    """A candidate associated with a test."""

    __test__: ClassVar[bool] = False

    id: str
    email: str
    full_name: str | None = None
    score: float | None = None
    test: str | None = None
    user: str | None = None
    attempt_starttime: str | None = None
    attempt_endtime: str | None = None
    attempt_events: list[str] | None = None
    status: int | None = None
    ats_state: int | None = None
    integrity_status: str | None = None
    integrity_summary: str | None = None
    invite_email_done: bool | None = None
    invite_valid: bool | None = None
    invited_on: str | None = None
    invite_valid_from: str | None = None
    invite_valid_to: str | None = None
    invite_link: str | None = None
    invite_metadata: dict[str, JSONValue] | None = None
    evaluator_email: str | None = None
    test_finish_url: str | None = None
    test_result_url: str | None = None
    accept_result_updates: bool | None = None
    tags: list[str] | None = None
    report_url: str | None = None
    authenticated_report_url: str | None = None
    pdf_url: str | None = None
    scores_tags_split: dict[str, JSONValue] | None = None
    scores_skills_split: dict[str, JSONValue] | None = None
    added_time: str | int | None = None
    unclaimed_added_time: int | None = None
    comments: dict[str, JSONValue] | None = None
    performance_summary: str | None = None
    ip_address: str | None = None
    questions: dict[str, JSONValue] | None = None
    plagiarism: dict[str, JSONValue] | None = None
    plagiarism_status: bool | None = None
    max_code_similarity: dict[str, JSONValue] | None = None
    feedback: str | None = None
    percentage_score: float | None = None
    candidate_details: list[CandidateDetail] | None = None
    out_of_window_events: int | None = None
    out_of_window_duration: float | None = None
    editor_paste_count: int | None = None
    proctor_images: list[str] | None = None

    @classmethod
    def from_dict(cls, data: TestCandidateDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        raw_details = data.get("candidate_details")
        return cls(
            id=data["id"],
            email=data["email"],
            full_name=data.get("full_name"),
            score=data.get("score"),
            test=data.get("test"),
            user=data.get("user"),
            attempt_starttime=data.get("attempt_starttime"),
            attempt_endtime=data.get("attempt_endtime"),
            attempt_events=data.get("attempt_events"),
            status=data.get("status"),
            ats_state=data.get("ats_state"),
            integrity_status=data.get("integrity_status"),
            integrity_summary=data.get("integrity_summary"),
            invite_email_done=data.get("invite_email_done"),
            invite_valid=data.get("invite_valid"),
            invited_on=data.get("invited_on"),
            invite_valid_from=data.get("invite_valid_from"),
            invite_valid_to=data.get("invite_valid_to"),
            invite_link=data.get("invite_link"),
            invite_metadata=data.get("invite_metadata"),
            evaluator_email=data.get("evaluator_email"),
            test_finish_url=data.get("test_finish_url"),
            test_result_url=data.get("test_result_url"),
            accept_result_updates=data.get(
                "accept_result_updates",
            ),
            tags=data.get("tags"),
            report_url=data.get("report_url"),
            authenticated_report_url=data.get(
                "authenticated_report_url",
            ),
            pdf_url=data.get("pdf_url"),
            scores_tags_split=data.get("scores_tags_split"),
            scores_skills_split=data.get(
                "scores_skills_split",
            ),
            added_time=data.get("added_time"),
            unclaimed_added_time=data.get(
                "unclaimed_added_time",
            ),
            comments=data.get("comments"),
            performance_summary=data.get("performance_summary"),
            ip_address=data.get("ip_address"),
            questions=data.get("questions"),
            plagiarism=data.get("plagiarism"),
            plagiarism_status=data.get("plagiarism_status"),
            max_code_similarity=data.get(
                "max_code_similarity",
            ),
            feedback=data.get("feedback"),
            percentage_score=data.get("percentage_score"),
            candidate_details=[
                CandidateDetail.from_dict(data=item) for item in raw_details
            ]
            if raw_details is not None
            else None,
            out_of_window_events=data.get(
                "out_of_window_events",
            ),
            out_of_window_duration=data.get(
                "out_of_window_duration",
            ),
            editor_paste_count=data.get("editor_paste_count"),
            proctor_images=data.get("proctor_images"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class Inviter:
    """A user permitted to invite candidates to a test."""

    id: str
    email: str
    firstname: str | None = None
    lastname: str | None = None
    role: str | None = None
    status: str | None = None
    phone: str | None = None
    timezone: str | None = None
    questions_permission: int | None = None
    tests_permission: int | None = None
    interviews_permission: int | None = None
    candidates_permission: int | None = None
    teams: list[str] | None = None
    candidates_invited: int | None = None
    activated: bool | None = None

    @classmethod
    def from_dict(cls, data: InviterDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            id=data["id"],
            email=data["email"],
            firstname=data.get("firstname"),
            lastname=data.get("lastname"),
            role=data.get("role"),
            status=data.get("status"),
            phone=data.get("phone"),
            timezone=data.get("timezone"),
            questions_permission=data.get(
                "questions_permission",
            ),
            tests_permission=data.get("tests_permission"),
            interviews_permission=data.get(
                "interviews_permission",
            ),
            candidates_permission=data.get(
                "candidates_permission",
            ),
            teams=data.get("teams"),
            candidates_invited=data.get("candidates_invited"),
            activated=data.get("activated"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class User:
    """A HackerRank user."""

    id: str
    email: str
    firstname: str | None = None
    lastname: str | None = None
    country: str | None = None
    role: str | None = None
    status: str | None = None
    phone: str | None = None
    timezone: str | None = None
    questions_permission: int | None = None
    tests_permission: int | None = None
    interviews_permission: int | None = None
    candidates_permission: int | None = None
    shared_questions_permission: int | None = None
    shared_tests_permission: int | None = None
    shared_interviews_permission: int | None = None
    shared_candidates_permission: int | None = None
    company_admin: bool | None = None
    team_admin: bool | None = None
    teams: list[str] | None = None
    activated: bool | None = None
    last_activity_time: str | None = None

    @classmethod
    def from_dict(cls, data: UserDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            id=data["id"],
            email=data["email"],
            firstname=data.get("firstname"),
            lastname=data.get("lastname"),
            country=data.get("country"),
            role=data.get("role"),
            status=data.get("status"),
            phone=data.get("phone"),
            timezone=data.get("timezone"),
            questions_permission=data.get(
                "questions_permission",
            ),
            tests_permission=data.get("tests_permission"),
            interviews_permission=data.get(
                "interviews_permission",
            ),
            candidates_permission=data.get(
                "candidates_permission",
            ),
            shared_questions_permission=data.get(
                "shared_questions_permission",
            ),
            shared_tests_permission=data.get(
                "shared_tests_permission",
            ),
            shared_interviews_permission=data.get(
                "shared_interviews_permission",
            ),
            shared_candidates_permission=data.get(
                "shared_candidates_permission",
            ),
            company_admin=data.get("company_admin"),
            team_admin=data.get("team_admin"),
            teams=data.get("teams"),
            activated=data.get("activated"),
            last_activity_time=data.get("last_activity_time"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class Team:
    """A HackerRank team."""

    id: str
    name: str
    owner: str | None = None
    created_at: str | None = None
    recruiter_count: int | None = None
    developer_count: int | None = None
    recruiter_cap: int | None = None
    developer_cap: int | None = None
    invite_as: str | None = None
    locations: list[str] | None = None
    departments: list[str] | None = None

    @classmethod
    def from_dict(cls, data: TeamDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            id=data["id"],
            name=data["name"],
            owner=data.get("owner"),
            created_at=data.get("created_at"),
            recruiter_count=data.get("recruiter_count"),
            developer_count=data.get("developer_count"),
            recruiter_cap=data.get("recruiter_cap"),
            developer_cap=data.get("developer_cap"),
            invite_as=data.get("invite_as"),
            locations=data.get("locations"),
            departments=data.get("departments"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class UserTeamMembership:
    """A membership of a user in a team."""

    team: str
    user: str

    @classmethod
    def from_dict(cls, data: UserTeamMembershipDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            team=data["team"],
            user=data["user"],
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class Template:
    """An invite-email template."""

    id: str
    name: str
    subject: str | None = None
    content: str | None = None
    default: bool | None = None
    created_at: str | None = None
    updated_at: str | None = None
    user: str | None = None

    @classmethod
    def from_dict(cls, data: TemplateDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            id=data["id"],
            name=data["name"],
            subject=data.get("subject"),
            content=data.get("content"),
            default=data.get("default"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            user=data.get("user"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class AuditLog:
    """An audit log entry."""

    source_id: int
    source_type: str
    action: str
    user: str | None = None
    modified_fields: list[str] | None = None
    modified_values: dict[str, JSONValue] | None = None
    ip_address: str | None = None
    created_at: str | None = None

    @classmethod
    def from_dict(cls, data: AuditLogDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            source_id=data["source_id"],
            source_type=data["source_type"],
            action=data["action"],
            user=data.get("user"),
            modified_fields=data.get("modified_fields"),
            modified_values=data.get("modified_values"),
            ip_address=data.get("ip_address"),
            created_at=data.get("created_at"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class CandidateInvite:
    """Success payload for inviting a candidate to a test."""

    test_link: str
    email: str
    id: int | str

    @classmethod
    def from_dict(cls, data: CandidateInviteDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            test_link=data["test_link"],
            email=data["email"],
            id=data["id"],
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class ATSCodePair:
    """Request-shaped payload for an ATS Codepair invite."""

    title: str | None = None
    requisition_id: str | None = None
    candidate_id: str | None = None
    candidate: dict[str, JSONValue] | None = None
    send_email: bool | None = None
    interview_metadata: dict[str, JSONValue] | None = None

    @classmethod
    def from_dict(cls, data: ATSCodePairDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            title=data.get("title"),
            requisition_id=data.get("requisition_id"),
            candidate_id=data.get("candidate_id"),
            candidate=data.get("candidate"),
            send_email=data.get("send_email"),
            interview_metadata=data.get("interview_metadata"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class ATSCodeScreen:
    """Request-shaped payload for an ATS CodeScreen invite."""

    test_id: str | None = None
    requisition_id: str | None = None
    candidate_id: str | None = None
    email: str | None = None
    test_result_url: str | None = None
    accept_result_updates: bool | None = None

    @classmethod
    def from_dict(cls, data: ATSCodeScreenDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            test_id=data.get("test_id"),
            requisition_id=data.get("requisition_id"),
            candidate_id=data.get("candidate_id"),
            email=data.get("email"),
            test_result_url=data.get("test_result_url"),
            accept_result_updates=data.get(
                "accept_result_updates",
            ),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class SCIMUser:
    """A SCIM v2 user."""

    id: str
    user_name: str
    name: dict[str, JSONValue] | None = None
    active: bool | None = None
    role: str | None = None
    team_admin: bool | None = None
    company_admin: bool | None = None
    emails: list[dict[str, JSONValue]] | None = None
    schemas: list[str] | None = None

    @classmethod
    def from_dict(cls, data: SCIMUserDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            id=data["id"],
            user_name=data["userName"],
            name=data.get("name"),
            active=data.get("active"),
            role=data.get("role"),
            team_admin=data.get("team_admin"),
            company_admin=data.get("company_admin"),
            emails=data.get("emails"),
            schemas=data.get("schemas"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class SCIMTeam:
    """A SCIM v2 team."""

    id: str
    display_name: str | None = None
    schemas: list[str] | None = None

    @classmethod
    def from_dict(cls, data: SCIMTeamDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            id=data["id"],
            display_name=data.get("displayName") or data.get("diplayName"),
            schemas=data.get("schemas"),
        )


@beartype
@dataclass(frozen=True, kw_only=True)
class UserUpdate:
    """Required body for ``PUT /x/api/v3/users/{id}``."""

    firstname: str
    lastname: str
    country: str
    role: str
    phone: str
    questions_permission: int
    tests_permission: int
    interviews_permission: int
    candidates_permission: int
    shared_questions_permission: int
    shared_tests_permission: int
    shared_interviews_permission: int
    shared_candidates_permission: int
    company_admin: bool
    team_admin: bool

    def to_dict(self) -> dict[str, JSONValue]:
        """Serialize to a JSON-compatible mapping.

        Returns:
            The update body as a dictionary.
        """
        return dict(asdict(obj=self))


@beartype
@dataclass(frozen=True, kw_only=True)
class TestsUpdate:
    """Required body for ``PUT /x/api/v3/tests/{id}``."""

    __test__: ClassVar[bool] = False

    name: str
    starttime: str
    endtime: str
    duration: int
    instructions: str
    locked: bool
    draft: bool
    languages: list[str]
    candidate_details: list[str]
    custom_acknowledge_text: str
    cutoff_score: int
    master_password: str
    hide_compile_test: bool
    tags: list[str]
    role_ids: list[str]
    experience: list[str]
    questions: list[str]
    mcq_incorrect_score: int
    mcq_correct_score: int
    shuffle_questions: bool
    test_admins: list[str]
    hide_template: bool
    enable_acknowledgement: bool
    enable_proctoring: bool
    enable_advanced_proctoring: bool
    enable_secure_assessment_mode: bool
    enable_ml_plagiarism_analysis: bool
    enable_photo_identification: bool
    ide_config: str

    def to_dict(self) -> dict[str, JSONValue]:
        """Serialize to a JSON-compatible mapping.

        Returns:
            The update body as a dictionary.
        """
        return dict(asdict(obj=self))


@beartype
@dataclass(frozen=True, kw_only=True)
class SCIMMessage:
    """A SCIM patch acknowledgement response."""

    message: str
    schemas: list[str] | None = None

    @classmethod
    def from_dict(cls, data: SCIMMessageDict) -> Self:
        """Create from an API response dictionary.

        Args:
            data: The dictionary to convert.

        Returns:
            A new instance.
        """
        return cls(
            message=data["message"],
            schemas=data.get("schemas"),
        )
