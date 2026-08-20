"""TypedDict types describing raw HackerRank API response shapes."""

from typing import Any, NotRequired, TypedDict


class InterviewDict(TypedDict):
    """A HackerRank interview."""

    id: str
    status: str
    url: str
    title: NotRequired[str]
    feedback: NotRequired[str]
    thumbs_up: NotRequired[int]
    notes: NotRequired[str]
    resume_url: NotRequired[str]
    interviewers: NotRequired[list[str]]
    result_url: NotRequired[str]
    candidate: NotRequired[dict[str, Any]]
    metadata: NotRequired[dict[str, Any]]
    report_url: NotRequired[str]
    ended_at: NotRequired[str]
    interview_template_id: NotRequired[int]
    created_at: NotRequired[str]
    updated_at: NotRequired[str]
    user: NotRequired[int]
    send_email: NotRequired[bool]


class InterviewTranscriptMessageDict(TypedDict):
    """A single message from an interview transcript."""

    author: str
    timestamp: int
    text: str
    candidate: bool
    messageId: str
    email: NotRequired[str]


class InterviewTranscriptDict(TypedDict):
    """The transcript for an interview."""

    messages: list[InterviewTranscriptMessageDict]


class InterviewTemplateDict(TypedDict):
    """A HackerRank interview template."""

    id: int | str
    name: str
    created_at: NotRequired[str]
    status: NotRequired[int]
    user: NotRequired[int]
    roles: NotRequired[list[str]]
    team_share: NotRequired[int]
    questions: NotRequired[list[int | str]]
    scorecard: NotRequired[int]
    import_template: NotRequired[bool]
    editor_access: NotRequired[bool]


class EnvironmentRuntimeDict(TypedDict):
    """A runtime component for a project-question environment."""

    name: str
    version: str


class EnvironmentDict(TypedDict):
    """A project-question environment."""

    id: int
    name: str
    tags: list[str]
    runtime: list[EnvironmentRuntimeDict]
    active: NotRequired[bool]
    sample_project_url: NotRequired[str]


class QuestionDict(TypedDict):
    """A HackerRank question."""

    id: str
    unique_id: NotRequired[str]
    type: str
    owner: NotRequired[str]
    created_at: NotRequired[str]
    status: NotRequired[str]
    internal_notes: NotRequired[str]
    name: str
    languages: NotRequired[list[str]]
    problem_statement: NotRequired[str]
    recommended_duration: NotRequired[int]
    tags: NotRequired[list[str]]
    max_score: NotRequired[float]
    options: NotRequired[list[str]]
    answer: NotRequired[int | list[int]]
    test_case_count: NotRequired[int]
    role_type: NotRequired[str]
    environment_id: NotRequired[int]
    file_url: NotRequired[str]
    file_path: NotRequired[str]
    has_valid_stacks: NotRequired[bool]
    fullstack_project_details: NotRequired[dict[str, Any]]


class TestDict(TypedDict):
    """A HackerRank test."""

    id: str
    unique_id: NotRequired[str]
    name: str
    starttime: NotRequired[str]
    endtime: NotRequired[str]
    duration: NotRequired[int]
    owner: NotRequired[str]
    instructions: NotRequired[str]
    starred: NotRequired[bool]
    created_at: NotRequired[str]
    state: NotRequired[str]
    locked: NotRequired[bool]
    draft: NotRequired[bool]
    languages: NotRequired[list[str]]
    candidate_details: NotRequired[list[str]]
    custom_acknowledge_text: NotRequired[str]
    cutoff_score: NotRequired[int]
    master_password: NotRequired[str]
    hide_compile_test: NotRequired[bool]
    tags: NotRequired[list[str]]
    role_ids: NotRequired[list[str]]
    experience: NotRequired[list[str]]
    questions: NotRequired[list[str]]
    sections: NotRequired[list[dict[str, Any]]]
    mcq_incorrect_score: NotRequired[int]
    mcq_correct_score: NotRequired[int]
    locked_by: NotRequired[str]
    short_login_url: NotRequired[str]
    public_login_url: NotRequired[str]
    shuffle_questions: NotRequired[bool]
    test_admins: NotRequired[list[str]]
    hide_template: NotRequired[bool]
    enable_acknowledgement: NotRequired[bool]
    enable_proctoring: NotRequired[bool]
    enable_advanced_proctoring: NotRequired[bool]
    enable_secure_assessment_mode: NotRequired[bool]
    enable_ml_plagiarism_analysis: NotRequired[bool]
    enable_photo_identification: NotRequired[bool]
    ide_config: NotRequired[str]


class CandidateDetailDict(TypedDict):
    """A custom candidate detail field."""

    field_name: str
    title: str
    value: str


class TestCandidateDict(TypedDict):
    """A candidate associated with a test."""

    id: str
    full_name: NotRequired[str]
    email: str
    score: NotRequired[float]
    test: NotRequired[str]
    user: NotRequired[str]
    attempt_starttime: NotRequired[str]
    attempt_endtime: NotRequired[str]
    attempt_events: NotRequired[list[str]]
    status: NotRequired[int]
    ats_state: NotRequired[int]
    integrity_status: NotRequired[str]
    integrity_summary: NotRequired[str]
    invite_email_done: NotRequired[bool]
    invite_valid: NotRequired[bool]
    invited_on: NotRequired[str]
    invite_valid_from: NotRequired[str]
    invite_valid_to: NotRequired[str]
    invite_link: NotRequired[str]
    invite_metadata: NotRequired[dict[str, Any]]
    evaluator_email: NotRequired[str]
    test_finish_url: NotRequired[str]
    test_result_url: NotRequired[str]
    accept_result_updates: NotRequired[bool]
    tags: NotRequired[list[str]]
    report_url: NotRequired[str]
    authenticated_report_url: NotRequired[str]
    pdf_url: NotRequired[str]
    scores_tags_split: NotRequired[dict[str, Any]]
    scores_skills_split: NotRequired[dict[str, Any]]
    added_time: NotRequired[int]
    unclaimed_added_time: NotRequired[int]
    comments: NotRequired[dict[str, Any]]
    performance_summary: NotRequired[str]
    ip_address: NotRequired[str]
    questions: NotRequired[dict[str, Any]]
    plagiarism: NotRequired[dict[str, Any]]
    plagiarism_status: NotRequired[bool]
    max_code_similarity: NotRequired[dict[str, Any]]
    feedback: NotRequired[str]
    percentage_score: NotRequired[float]
    candidate_details: NotRequired[list[CandidateDetailDict]]
    out_of_window_events: NotRequired[int]
    out_of_window_duration: NotRequired[float]
    editor_paste_count: NotRequired[int]
    proctor_images: NotRequired[list[str]]


class InviterDict(TypedDict):
    """A user permitted to invite candidates to a test."""

    id: str
    email: str
    firstname: NotRequired[str]
    lastname: NotRequired[str]
    role: NotRequired[str]
    status: NotRequired[str]
    phone: NotRequired[str]
    timezone: NotRequired[str]
    questions_permission: NotRequired[int]
    tests_permission: NotRequired[int]
    interviews_permission: NotRequired[int]
    candidates_permission: NotRequired[int]
    teams: NotRequired[list[str]]
    candidates_invited: NotRequired[int]
    activated: NotRequired[bool]


class UserDict(TypedDict):
    """A HackerRank user."""

    id: str
    email: str
    firstname: NotRequired[str]
    lastname: NotRequired[str]
    country: NotRequired[str]
    role: NotRequired[str]
    status: NotRequired[str]
    phone: NotRequired[str]
    timezone: NotRequired[str]
    questions_permission: NotRequired[int]
    tests_permission: NotRequired[int]
    interviews_permission: NotRequired[int]
    candidates_permission: NotRequired[int]
    shared_questions_permission: NotRequired[int]
    shared_tests_permission: NotRequired[int]
    shared_interviews_permission: NotRequired[int]
    shared_candidates_permission: NotRequired[int]
    company_admin: NotRequired[bool]
    team_admin: NotRequired[bool]
    teams: NotRequired[list[str]]
    activated: NotRequired[bool]
    last_activity_time: NotRequired[str]


class TeamDict(TypedDict):
    """A HackerRank team."""

    id: str
    name: str
    owner: NotRequired[str]
    created_at: NotRequired[str]
    recruiter_count: NotRequired[int]
    developer_count: NotRequired[int]
    recruiter_cap: NotRequired[int]
    developer_cap: NotRequired[int]
    invite_as: NotRequired[str]
    locations: NotRequired[list[str]]
    departments: NotRequired[list[str]]


class UserTeamMembershipDict(TypedDict):
    """A membership of a user in a team."""

    team: str
    user: str


class TemplateDict(TypedDict):
    """An invite-email template."""

    id: str
    name: str
    subject: NotRequired[str]
    content: NotRequired[str]
    default: NotRequired[bool]
    created_at: NotRequired[str]
    updated_at: NotRequired[str]
    user: NotRequired[str]


class AuditLogDict(TypedDict):
    """An audit log entry."""

    source_id: int
    source_type: str
    user: NotRequired[str]
    action: str
    modified_fields: NotRequired[list[str]]
    modified_values: NotRequired[dict[str, Any]]
    ip_address: NotRequired[str]
    created_at: NotRequired[str]


class ATSCodePairDict(TypedDict):
    """Result of an ATS Codepair invite."""

    title: NotRequired[str]
    requisition_id: NotRequired[str]
    candidate_id: NotRequired[str]
    candidate: NotRequired[dict[str, Any]]
    send_email: NotRequired[bool]
    interview_metadata: NotRequired[dict[str, Any]]


class ATSCodeScreenDict(TypedDict):
    """Result of an ATS CodeScreen invite."""

    test_id: NotRequired[str]
    requisition_id: NotRequired[str]
    candidate_id: NotRequired[str]
    email: NotRequired[str]
    test_result_url: NotRequired[str]
    accept_result_updates: NotRequired[bool]


class SCIMUserDict(TypedDict):
    """A SCIM v2 user."""

    id: str
    userName: str
    name: NotRequired[dict[str, Any]]
    active: NotRequired[bool]
    role: NotRequired[str]
    team_admin: NotRequired[bool]
    company_admin: NotRequired[bool]
    emails: NotRequired[list[dict[str, Any]]]
    schemas: NotRequired[list[str]]


class SCIMTeamDict(TypedDict):
    """A SCIM v2 team."""

    id: str
    displayName: NotRequired[str]
    diplayName: NotRequired[str]
    schemas: NotRequired[list[str]]


class SCIMMessageDict(TypedDict):
    """A SCIM patch acknowledgement message."""

    message: str
    schemas: NotRequired[list[str]]

