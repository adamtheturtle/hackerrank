"""Async HackerRank for Work API client."""

import builtins
from collections.abc import Mapping, Sequence
from http import HTTPStatus
from types import TracebackType
from typing import Any, BinaryIO, Self

from beartype import beartype

from hackerrank.exceptions import HackerRankError
from hackerrank.transports import (
    AsyncHTTPXTransport,
    AsyncTransport,
    TransportResponse,
)
from hackerrank.types import (
    ATSCodePair,
    ATSCodeScreen,
    AuditLog,
    Environment,
    Interview,
    InterviewTemplate,
    InterviewTranscript,
    Inviter,
    JSONValue,
    Page,
    Question,
    SCIMPage,
    SCIMTeam,
    SCIMUser,
    Team,
    Template,
    Test,
    TestCandidate,
    User,
    UserTeamMembership,
)

_API_V3 = "/x/api/v3"


def _drop_none(
    data: Mapping[str, JSONValue],
    /,
) -> dict[str, JSONValue]:
    """Return a copy of ``data`` with ``None`` values removed.

    Args:
        data: The dictionary to filter.

    Returns:
        A new dictionary without ``None`` values.
    """
    return {k: v for k, v in data.items() if v is not None}


def _coerce_int(value: object, /) -> int:
    """Coerce ``value`` to ``int``, defaulting to ``0``.

    Args:
        value: A value that may be ``int``, ``str`` or
            ``None``.

    Returns:
        The integer value, or ``0`` if conversion is not
        possible.
    """
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value:
        try:
            return int(value)
        except ValueError:
            return 0
    return 0


def _coerce_str(value: object, /) -> str:
    """Coerce ``value`` to ``str``, defaulting to ``""``.

    Args:
        value: A value that may be a ``str`` or ``None``.

    Returns:
        The string value, or ``""`` if ``None``.
    """
    if isinstance(value, str):
        return value
    return ""


def _make_page[T](
    items: list[T],
    metadata: Mapping[str, JSONValue],
    /,
) -> Page[T]:
    """Wrap ``items`` and ``metadata`` into a ``Page``.

    Args:
        items: The items in the page.
        metadata: The raw response metadata.

    Returns:
        A populated ``Page`` instance.
    """
    return Page(
        items,
        page_total=_coerce_int(metadata.get("page_total")),
        offset=_coerce_int(metadata.get("offset")),
        previous=_coerce_str(metadata.get("previous")),
        next_=_coerce_str(metadata.get("next")),
        first=_coerce_str(metadata.get("first")),
        last=_coerce_str(metadata.get("last")),
        total=_coerce_int(metadata.get("total")),
    )


def _make_scim_page[T](
    items: list[T],
    payload: Mapping[str, JSONValue],
    /,
) -> SCIMPage[T]:
    """Wrap items and a SCIM payload into a ``SCIMPage``.

    Args:
        items: The SCIM items in the page.
        payload: The raw SCIM response payload.

    Returns:
        A populated ``SCIMPage`` instance.
    """
    schemas_raw = payload.get("schemas")
    schemas: list[str] = [
        item
        for item in (schemas_raw if isinstance(schemas_raw, list) else [])
        if isinstance(item, str)
    ]
    start_index = _coerce_int(payload.get("startIndex")) or 1
    return SCIMPage(
        items,
        schemas=schemas,
        start_index=start_index,
        items_per_page=_coerce_int(payload.get("itemsPerPage")),
        total_results=_coerce_int(payload.get("totalResults")),
    )


def _list_params(
    *,
    limit: int | None,
    offset: int | None,
    extra: dict[str, str | int] | None = None,
) -> dict[str, str | int]:
    """Build query parameters for a list call.

    Args:
        limit: Maximum number of items to return.
        offset: Offset to start from.
        extra: Any extra parameters to include.

    Returns:
        The query parameter mapping.
    """
    params: dict[str, str | int] = {}
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if extra:
        params.update(extra)
    return params


def _question_body(
    *,
    name: str | None = None,
    type: str | None = None,  # noqa: A002  # pylint: disable=redefined-builtin
    internal_notes: str | None = None,
    languages: Sequence[str] | None = None,
    problem_statement: str | None = None,
    recommended_duration: int | None = None,
    tags: Sequence[str] | None = None,
    options: Sequence[str] | None = None,
    answer: int | Sequence[int] | None = None,
    score: float | None = None,
    environment_id: int | None = None,
    role_type: str | None = None,
    scoring_command: str | None = None,
    scoring_files: Sequence[str] | None = None,
    readonly_paths: Sequence[str] | None = None,
    default_files: Sequence[str] | None = None,
    configuration: Mapping[str, JSONValue] | None = None,
    testcases: Sequence[Mapping[str, JSONValue]] | None = None,
) -> dict[str, JSONValue]:
    """Build a JSON body for question create/update calls."""
    return _drop_none(
        {
            "name": name,
            "type": type,
            "internal_notes": internal_notes,
            "languages": (
                list(languages) if languages is not None else None
            ),
            "problem_statement": problem_statement,
            "recommended_duration": recommended_duration,
            "tags": list(tags) if tags is not None else None,
            "options": (list(options) if options is not None else None),
            "answer": (
                list(answer)
                if isinstance(answer, Sequence)
                and not isinstance(answer, str)
                else answer
            ),
            "score": score,
            "environment_id": environment_id,
            "role_type": role_type,
            "scoring_command": scoring_command,
            "scoring_files": (
                list(scoring_files) if scoring_files is not None else None
            ),
            "readonly_paths": (
                list(readonly_paths) if readonly_paths is not None else None
            ),
            "default_files": (
                list(default_files) if default_files is not None else None
            ),
            "configuration": configuration,
            "testcases": (
                list(testcases) if testcases is not None else None
            ),
        },
    )


@beartype
class _AsyncNamespace:
    """Base class providing shared async request logic."""

    def __init__(
        self,
        *,
        transport: AsyncTransport,
        base_url: str,
        headers: dict[str, str],
    ) -> None:
        """Create a new async namespace.

        Args:
            transport: The async HTTP transport.
            base_url: The base URL for the API.
            headers: Headers to send with every request.
        """
        self.transport = transport
        self.base_url = base_url
        self.headers = headers

    async def _request(
        self,
        *,
        method: str,
        url: str,
        params: dict[str, str | int] | None = None,
        json: Mapping[str, JSONValue] | None = None,
        files: Mapping[str, Any] | None = None,
    ) -> TransportResponse:
        """Make an async HTTP request.

        Args:
            method: The HTTP method.
            url: The URL path.
            params: Query parameters.
            json: JSON-serialisable body.
            files: Files to send as multipart form-data.

        Returns:
            The transport response.

        Raises:
            HackerRankError: If the response has an error
                status code.
        """
        response = await self.transport(
            method=method,
            url=self.base_url + url,
            headers=self.headers,
            params=params,
            json=json,
            files=files,
        )
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            raise HackerRankError.from_response(response=response)
        return response


@beartype
class AsyncInterviewsNamespace(_AsyncNamespace):
    """Async namespace for interview operations."""

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[Interview]:
        """List interviews.

        Args:
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of interviews.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/interviews",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[Interview] = [
            Interview.from_dict(data=item) for item in raw_items
        ]
        return _make_page(items, payload)

    async def create(
        self,
        *,
        title: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        interview_template_id: int | None = None,
        candidate: Mapping[str, JSONValue] | None = None,
        send_email: bool | None = None,
        metadata: Mapping[str, JSONValue] | None = None,
        interviewers: Sequence[str] | None = None,
    ) -> Interview:
        """Create an interview.

        Args:
            title: Title of the interview.
            from_: Scheduled start time.
            to: Scheduled end time.
            interview_template_id: Template to apply.
            candidate: Candidate details.
            send_email: Whether to send an email invite.
            metadata: Arbitrary metadata.
            interviewers: Emails of interviewers.

        Returns:
            The created interview.
        """
        body = _drop_none(
            {
                "title": title,
                "from": from_,
                "to": to,
                "interview_template_id": interview_template_id,
                "candidate": candidate,
                "send_email": send_email,
                "metadata": metadata,
                "interviewers": (
                    list(interviewers) if interviewers is not None else None
                ),
            },
        )
        response = await self._request(
            method="POST",
            url=f"{_API_V3}/interviews",
            json=body,
        )
        return Interview.from_dict(data=response.json())

    async def get(self, *, interview_id: str) -> Interview:
        """Retrieve an interview.

        Args:
            interview_id: The id of the interview.

        Returns:
            The interview.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/interviews/{interview_id}",
        )
        return Interview.from_dict(data=response.json())

    async def delete(self, *, interview_id: str) -> None:
        """Delete an interview.

        Args:
            interview_id: The id of the interview.
        """
        await self._request(
            method="DELETE",
            url=f"{_API_V3}/interviews/{interview_id}",
        )

    async def get_transcript(
        self,
        *,
        interview_id: str,
    ) -> InterviewTranscript:
        """Retrieve the transcript of an interview.

        Args:
            interview_id: The id of the interview.

        Returns:
            The transcript.
        """
        response = await self._request(
            method="GET",
            url=(f"{_API_V3}/interviews/{interview_id}/transcript"),
        )
        return InterviewTranscript.from_dict(data=response.json())


@beartype
class AsyncInterviewTemplatesNamespace(_AsyncNamespace):
    """Async namespace for interview-template operations."""

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[InterviewTemplate]:
        """List interview templates.

        Args:
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of interview templates.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/interview_templates",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[InterviewTemplate] = [
            InterviewTemplate.from_dict(data=item) for item in raw_items
        ]
        return _make_page(items, payload)

    async def get(
        self,
        *,
        template_id: int | str,
    ) -> InterviewTemplate:
        """Retrieve an interview template.

        Args:
            template_id: The id of the template.

        Returns:
            The template.
        """
        response = await self._request(
            method="GET",
            url=(f"{_API_V3}/interview_templates/{template_id}"),
        )
        return InterviewTemplate.from_dict(data=response.json())


@beartype
class AsyncEnvironmentsNamespace(_AsyncNamespace):
    """Async namespace for project-question environment operations."""

    async def list(self) -> builtins.list[Environment]:
        """List project-question environments.

        Returns:
            The available environments.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/environments",
        )
        raw_items = list(response.json().get("environments", []))
        return [Environment.from_dict(data=item) for item in raw_items]

    async def get(self, *, environment_id: int) -> Environment:
        """Retrieve a project-question environment.

        Args:
            environment_id: The id of the environment.

        Returns:
            The environment.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/environments/{environment_id}",
        )
        return Environment.from_dict(data=response.json()["environment"])


@beartype
class AsyncQuestionsNamespace(_AsyncNamespace):
    """Async namespace for question operations."""

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[Question]:
        """List questions.

        Args:
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of questions.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/questions",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[Question] = [
            Question.from_dict(data=item) for item in raw_items
        ]
        return _make_page(items, payload)

    async def get(self, *, question_id: str) -> Question:
        """Retrieve a question.

        Args:
            question_id: The id of the question.

        Returns:
            The question.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/questions/{question_id}",
        )
        return Question.from_dict(data=response.json())

    async def create(
        self,
        *,
        name: str,
        type: str,  # noqa: A002  # pylint: disable=redefined-builtin
        internal_notes: str | None = None,
        languages: Sequence[str] | None = None,
        problem_statement: str | None = None,
        recommended_duration: int | None = None,
        tags: Sequence[str] | None = None,
        options: Sequence[str] | None = None,
        answer: int | Sequence[int] | None = None,
        score: float | None = None,
        environment_id: int | None = None,
        role_type: str | None = None,
        scoring_command: str | None = None,
        scoring_files: Sequence[str] | None = None,
        readonly_paths: Sequence[str] | None = None,
        default_files: Sequence[str] | None = None,
        configuration: Mapping[str, JSONValue] | None = None,
        testcases: Sequence[Mapping[str, JSONValue]] | None = None,
    ) -> Question:
        """Create a question.

        Args:
            name: Question name.
            type: Question type (``code``, ``mcq``, ...).
            internal_notes: Private notes.
            languages: Supported languages.
            problem_statement: Problem statement.
            recommended_duration: Recommended duration.
            tags: Tags.
            options: MCQ options.
            answer: Correct MCQ answer.
            score: Maximum score for project questions.
            environment_id: Environment id for a fullstack question.
            role_type: Role type for a fullstack question.
            scoring_command: Command used to score the submission.
            scoring_files: Files that hold scoring tests.
            readonly_paths: Paths the candidate cannot edit.
            default_files: File paths opened by default.
            configuration: Project configuration.
            testcases: Project scoring test cases.

        Returns:
            The created question.
        """
        response = await self._request(
            method="POST",
            url=f"{_API_V3}/questions",
            json=_question_body(
                name=name,
                type=type,
                internal_notes=internal_notes,
                languages=languages,
                problem_statement=problem_statement,
                recommended_duration=recommended_duration,
                tags=tags,
                options=options,
                answer=answer,
                score=score,
                environment_id=environment_id,
                role_type=role_type,
                scoring_command=scoring_command,
                scoring_files=scoring_files,
                readonly_paths=readonly_paths,
                default_files=default_files,
                configuration=configuration,
                testcases=testcases,
            ),
        )
        return Question.from_dict(data=response.json())

    async def update(
        self,
        *,
        question_id: str,
        name: str | None = None,
        # pylint: disable-next=redefined-builtin
        type: str | None = None,  # noqa: A002
        internal_notes: str | None = None,
        languages: Sequence[str] | None = None,
        problem_statement: str | None = None,
        recommended_duration: int | None = None,
        tags: Sequence[str] | None = None,
        options: Sequence[str] | None = None,
        answer: int | Sequence[int] | None = None,
        score: float | None = None,
        environment_id: int | None = None,
        role_type: str | None = None,
        scoring_command: str | None = None,
        scoring_files: Sequence[str] | None = None,
        readonly_paths: Sequence[str] | None = None,
        default_files: Sequence[str] | None = None,
        configuration: Mapping[str, JSONValue] | None = None,
        testcases: Sequence[Mapping[str, JSONValue]] | None = None,
    ) -> Question | None:
        """Update a question.

        Args:
            question_id: The id of the question.
            name: New name.
            type: New question type.
            internal_notes: New internal notes.
            languages: New supported languages.
            problem_statement: New problem statement.
            recommended_duration: New recommended duration.
            tags: New tags.
            options: New MCQ options.
            answer: New MCQ answer.
            score: New maximum score.
            environment_id: New environment id.
            role_type: New role type.
            scoring_command: New scoring command.
            scoring_files: New scoring files.
            readonly_paths: New read-only paths.
            default_files: New default file paths.
            configuration: Project configuration to merge.
            testcases: New project scoring test cases.

        Returns:
            The updated question when returned by the API, otherwise
            ``None``.
        """
        response = await self._request(
            method="PUT",
            url=f"{_API_V3}/questions/{question_id}",
            json=_question_body(
                name=name,
                type=type,
                internal_notes=internal_notes,
                languages=languages,
                problem_statement=problem_statement,
                recommended_duration=recommended_duration,
                tags=tags,
                options=options,
                answer=answer,
                score=score,
                environment_id=environment_id,
                role_type=role_type,
                scoring_command=scoring_command,
                scoring_files=scoring_files,
                readonly_paths=readonly_paths,
                default_files=default_files,
                configuration=configuration,
                testcases=testcases,
            ),
        )
        if response.content:
            return Question.from_dict(data=response.json())
        return None

    async def upload_project_zip(
        self,
        *,
        question_id: str,
        file: bytes | BinaryIO,
        filename: str = "project.zip",
        content_type: str = "application/zip",
    ) -> dict[str, JSONValue]:
        """Upload a project zip for a fullstack question.

        Args:
            question_id: The id of the question.
            file: The zip file content or a binary file object.
            filename: The multipart filename.
            content_type: The multipart content type.

        Returns:
            The raw API response, including ``file_url`` and
            ``file_path``.
        """
        response = await self._request(
            method="POST",
            url=f"{_API_V3}/questions/{question_id}/upload_project_zip",
            files={"file": (filename, file, content_type)},
        )
        result: dict[str, JSONValue] = dict(response.json())
        return result


@beartype
class AsyncTestCandidatesNamespace(_AsyncNamespace):
    """Async namespace for candidates of a test."""

    async def list(
        self,
        *,
        test_id: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[TestCandidate]:
        """List candidates for a test.

        Args:
            test_id: The id of the test.
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of candidates.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/tests/{test_id}/candidates",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[TestCandidate] = [
            TestCandidate.from_dict(data=item) for item in raw_items
        ]
        return _make_page(items, payload)

    async def invite(
        self,
        *,
        test_id: str,
        email: str,
        full_name: str | None = None,
        send_email: bool | None = None,
    ) -> TestCandidate:
        """Invite a candidate to a test.

        Args:
            test_id: The id of the test.
            email: Candidate email address.
            full_name: Candidate full name.
            send_email: Whether to send the invitation email.

        Returns:
            The created candidate.
        """
        body = _drop_none(
            {
                "email": email,
                "full_name": full_name,
                "send_email": send_email,
            },
        )
        response = await self._request(
            method="POST",
            url=f"{_API_V3}/tests/{test_id}/candidates",
            json=body,
        )
        return TestCandidate.from_dict(data=response.json())

    async def get(
        self,
        *,
        test_id: str,
        candidate_id: str,
    ) -> TestCandidate:
        """Retrieve a single candidate.

        Args:
            test_id: The id of the test.
            candidate_id: The id of the candidate.

        Returns:
            The candidate.
        """
        response = await self._request(
            method="GET",
            url=(f"{_API_V3}/tests/{test_id}/candidates/{candidate_id}"),
        )
        return TestCandidate.from_dict(data=response.json())


@beartype
class AsyncTestsNamespace(_AsyncNamespace):
    """Async namespace for test operations."""

    def __init__(
        self,
        *,
        transport: AsyncTransport,
        base_url: str,
        headers: dict[str, str],
    ) -> None:
        """Create the namespace.

        Args:
            transport: The HTTP transport.
            base_url: The base URL for the API.
            headers: Headers to send with every request.
        """
        super().__init__(
            transport=transport,
            base_url=base_url,
            headers=headers,
        )
        self.candidates: AsyncTestCandidatesNamespace = (
            AsyncTestCandidatesNamespace(
                transport=transport,
                base_url=base_url,
                headers=headers,
            )
        )

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[Test]:
        """List tests.

        Args:
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of tests.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/tests",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[Test] = [Test.from_dict(data=item) for item in raw_items]
        return _make_page(items, payload)

    async def get(
        self,
        *,
        test_id: str,
    ) -> Test:
        """Retrieve a test.

        Args:
            test_id: The id of the test.

        Returns:
            The test.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/tests/{test_id}",
        )
        return Test.from_dict(data=response.json())

    async def list_inviters(
        self,
        *,
        test_id: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[Inviter]:
        """List inviters for a test.

        Args:
            test_id: The id of the test.
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of inviters.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/tests/{test_id}/inviters",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[Inviter] = [
            Inviter.from_dict(data=item) for item in raw_items
        ]
        return _make_page(items, payload)


@beartype
class AsyncTemplatesNamespace(_AsyncNamespace):
    """Async namespace for invite-email templates."""

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[Template]:
        """List invite templates.

        Args:
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of templates.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/templates",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[Template] = [
            Template.from_dict(data=item) for item in raw_items
        ]
        return _make_page(items, payload)


@beartype
class AsyncUsersNamespace(_AsyncNamespace):
    """Async namespace for user operations."""

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[User]:
        """List users.

        Args:
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of users.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/users",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[User] = [User.from_dict(data=item) for item in raw_items]
        return _make_page(items, payload)

    async def get(self, *, user_id: str) -> User:
        """Retrieve a user.

        Args:
            user_id: The id of the user.

        Returns:
            The user.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/users/{user_id}",
        )
        return User.from_dict(data=response.json())


@beartype
class AsyncTeamsNamespace(_AsyncNamespace):
    """Async namespace for team operations."""

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[Team]:
        """List teams.

        Args:
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of teams.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/teams",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[Team] = [Team.from_dict(data=item) for item in raw_items]
        return _make_page(items, payload)

    async def get(self, *, team_id: str) -> Team:
        """Retrieve a team.

        Args:
            team_id: The id of the team.

        Returns:
            The team.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/teams/{team_id}",
        )
        return Team.from_dict(data=response.json())

    async def list_members(
        self,
        *,
        team_id: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[UserTeamMembership]:
        """List memberships for a team.

        Args:
            team_id: The id of the team.
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of memberships.
        """
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/teams/{team_id}/users",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[UserTeamMembership] = [
            UserTeamMembership.from_dict(data=item) for item in raw_items
        ]
        return _make_page(items, payload)


@beartype
class AsyncAuditLogsNamespace(_AsyncNamespace):
    """Async namespace for audit-log operations."""

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        user_id: str | None = None,
    ) -> Page[AuditLog]:
        """List audit logs.

        Args:
            limit: Number of records to fetch.
            offset: Offset of records.
            user_id: Filter to a specific user.

        Returns:
            A page of audit logs.
        """
        extra: dict[str, str | int] = {}
        if user_id is not None:
            extra["user_id"] = user_id
        response = await self._request(
            method="GET",
            url=f"{_API_V3}/audit_log",
            params=_list_params(
                limit=limit,
                offset=offset,
                extra=extra,
            ),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[AuditLog] = [
            AuditLog.from_dict(data=item) for item in raw_items
        ]
        return _make_page(items, payload)


@beartype
class AsyncATSNamespace(_AsyncNamespace):
    """Async namespace for ATS operations."""

    async def codepair_invite(
        self,
        *,
        body: Mapping[str, JSONValue],
    ) -> ATSCodePair:
        """Invite a candidate to an ATS Codepair interview.

        Args:
            body: The Codepair invite payload.

        Returns:
            The ATS Codepair result.
        """
        response = await self._request(
            method="POST",
            url=f"{_API_V3}/ats/codepair",
            json=body,
        )
        return ATSCodePair.from_dict(data=response.json())

    async def codescreen_invite(
        self,
        *,
        body: Mapping[str, JSONValue],
    ) -> ATSCodeScreen:
        """Invite a candidate to a CodeScreen test.

        Args:
            body: The CodeScreen invite payload.

        Returns:
            The ATS CodeScreen result.
        """
        response = await self._request(
            method="POST",
            url=f"{_API_V3}/ats/codescreen",
            json=body,
        )
        return ATSCodeScreen.from_dict(data=response.json())


@beartype
class AsyncSCIMNamespace(_AsyncNamespace):
    """Async namespace for SCIM v2 operations."""

    async def list_users(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> SCIMPage[SCIMUser]:
        """List SCIM users.

        Args:
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of SCIM users.
        """
        response = await self._request(
            method="GET",
            url="/Users",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw = list(payload.get("Resources", []))
        items: list[SCIMUser] = [SCIMUser.from_dict(data=item) for item in raw]
        return _make_scim_page(items, payload)

    async def list_groups(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> SCIMPage[SCIMTeam]:
        """List SCIM groups (teams).

        Args:
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of SCIM teams.
        """
        response = await self._request(
            method="GET",
            url="/Groups",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw = list(payload.get("Resources", []))
        items: list[SCIMTeam] = [SCIMTeam.from_dict(data=item) for item in raw]
        return _make_scim_page(items, payload)


@beartype
class AsyncHackerRank:
    """An async client for the HackerRank for Work API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://www.hackerrank.com",
        transport: AsyncTransport | None = None,
    ) -> None:
        """Create a new async HackerRank client.

        Args:
            api_key: The API key for authentication.
            base_url: The base URL for the API.
            transport: The HTTP transport. Defaults to
                ``AsyncHTTPXTransport()``.
        """
        self.base_url = base_url
        resolved_transport = transport or AsyncHTTPXTransport()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }
        self.interviews: AsyncInterviewsNamespace = AsyncInterviewsNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.interview_templates: AsyncInterviewTemplatesNamespace = (
            AsyncInterviewTemplatesNamespace(
                transport=resolved_transport,
                base_url=base_url,
                headers=headers,
            )
        )
        self.environments: AsyncEnvironmentsNamespace = (
            AsyncEnvironmentsNamespace(
                transport=resolved_transport,
                base_url=base_url,
                headers=headers,
            )
        )
        self.questions: AsyncQuestionsNamespace = AsyncQuestionsNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.tests: AsyncTestsNamespace = AsyncTestsNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.templates: AsyncTemplatesNamespace = AsyncTemplatesNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.users: AsyncUsersNamespace = AsyncUsersNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.teams: AsyncTeamsNamespace = AsyncTeamsNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.audit_logs: AsyncAuditLogsNamespace = AsyncAuditLogsNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.ats: AsyncATSNamespace = AsyncATSNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.scim: AsyncSCIMNamespace = AsyncSCIMNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self._owned_transport = (
            resolved_transport
            if isinstance(resolved_transport, AsyncHTTPXTransport)
            else None
        )

    async def aclose(self) -> None:
        """Close the underlying transport if it supports closing."""
        if self._owned_transport is not None:
            await self._owned_transport.aclose()

    async def __aenter__(self) -> Self:
        """Enter the async context manager.

        Returns:
            This client instance.
        """
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
        /,
    ) -> None:
        """Exit the async context manager and close."""
        await self.aclose()
