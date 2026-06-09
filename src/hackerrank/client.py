"""HackerRank for Work API client."""

from collections.abc import Mapping, Sequence
from http import HTTPStatus
from types import TracebackType
from typing import Self

from beartype import beartype

from hackerrank.exceptions import HackerRankError
from hackerrank.transports import (
    HTTPXTransport,
    Transport,
    TransportResponse,
)
from hackerrank.types import (
    ATSCodePair,
    ATSCodeScreen,
    AuditLog,
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


@beartype
class _Namespace:
    """Base class providing shared request logic."""

    def __init__(
        self,
        *,
        transport: Transport,
        base_url: str,
        headers: dict[str, str],
    ) -> None:
        """Create a new namespace.

        Args:
            transport: The HTTP transport.
            base_url: The base URL for the API.
            headers: Headers to send with every request.
        """
        self.transport = transport
        self.base_url = base_url
        self.headers = headers

    def _request(
        self,
        *,
        method: str,
        url: str,
        params: dict[str, str | int] | None = None,
        json: Mapping[str, JSONValue] | None = None,
    ) -> TransportResponse:
        """Make an HTTP request.

        Args:
            method: The HTTP method.
            url: The URL path.
            params: Query parameters.
            json: JSON-serialisable body.

        Returns:
            The transport response.

        Raises:
            HackerRankError: If the response has an error
                status code.
        """
        response = self.transport(
            method=method,
            url=self.base_url + url,
            headers=self.headers,
            params=params,
            json=json,
        )
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            raise HackerRankError.from_response(response=response)
        return response


def _coerce_int(value: object, /) -> int:
    """Coerce ``value`` to an ``int``, defaulting to ``0``.

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
    """Coerce ``value`` to a ``str``, defaulting to ``""``.

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


@beartype
class InterviewsNamespace(_Namespace):
    """Namespace for interview operations."""

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        created_at: str | None = None,
        updated_at: str | None = None,
        ended_at: str | None = None,
    ) -> Page[Interview]:
        """List interviews.

        Args:
            limit: Number of records to fetch.
            offset: Offset of records.
            created_at: ``from..to`` filter for creation time.
            updated_at: ``from..to`` filter for update time.
            ended_at: ``from..to`` filter for ending time.

        Returns:
            A page of interviews.
        """
        extra: dict[str, str | int] = {}
        if created_at is not None:
            extra["created_at"] = created_at
        if updated_at is not None:
            extra["updated_at"] = updated_at
        if ended_at is not None:
            extra["ended_at"] = ended_at
        response = self._request(
            method="GET",
            url=f"{_API_V3}/interviews",
            params=_list_params(
                limit=limit,
                offset=offset,
                extra=extra,
            ),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[Interview] = [
            Interview.from_dict(data=item) for item in raw_items
        ]
        return _make_page(items, payload)

    def create(
        self,
        *,
        title: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        notes: str | None = None,
        resume_url: str | None = None,
        interviewers: Sequence[str] | None = None,
        result_url: str | None = None,
        candidate: Mapping[str, JSONValue] | None = None,
        send_email: bool | None = None,
        metadata: Mapping[str, JSONValue] | None = None,
        interview_template_id: int | None = None,
    ) -> Interview:
        """Create an interview.

        Args:
            title: Title of the interview.
            from_: Scheduled start time.
            to: Scheduled end time.
            notes: Private notes.
            resume_url: URL to the candidate resume.
            interviewers: Emails of interviewers.
            result_url: URL invoked when the interview ends.
            candidate: Candidate details.
            send_email: Whether to send an email invite.
            metadata: Arbitrary metadata.
            interview_template_id: Template to apply.

        Returns:
            The created interview.
        """
        body = _drop_none(
            {
                "title": title,
                "from": from_,
                "to": to,
                "notes": notes,
                "resume_url": resume_url,
                "interviewers": (
                    list(interviewers) if interviewers is not None else None
                ),
                "result_url": result_url,
                "candidate": candidate,
                "send_email": send_email,
                "metadata": metadata,
                "interview_template_id": interview_template_id,
            },
        )
        response = self._request(
            method="POST",
            url=f"{_API_V3}/interviews",
            json=body,
        )
        return Interview.from_dict(data=response.json())

    def get(self, *, interview_id: str) -> Interview:
        """Retrieve an interview.

        Args:
            interview_id: The id of the interview.

        Returns:
            The interview.
        """
        response = self._request(
            method="GET",
            url=f"{_API_V3}/interviews/{interview_id}",
        )
        return Interview.from_dict(data=response.json())

    def update(
        self,
        *,
        interview_id: str,
        title: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        notes: str | None = None,
        resume_url: str | None = None,
        result_url: str | None = None,
        candidate: Mapping[str, JSONValue] | None = None,
        send_email: bool | None = None,
        metadata: Mapping[str, JSONValue] | None = None,
        interview_template_id: int | None = None,
    ) -> None:
        """Update an interview.

        Args:
            interview_id: The id of the interview.
            title: New title.
            from_: New start time.
            to: New end time.
            notes: New private notes.
            resume_url: New resume URL.
            result_url: New result URL.
            candidate: New candidate details.
            send_email: Whether to send an email.
            metadata: New metadata.
            interview_template_id: New template id.
        """
        body = _drop_none(
            {
                "title": title,
                "from": from_,
                "to": to,
                "notes": notes,
                "resume_url": resume_url,
                "result_url": result_url,
                "candidate": candidate,
                "send_email": send_email,
                "metadata": metadata,
                "interview_template_id": interview_template_id,
            },
        )
        self._request(
            method="PUT",
            url=f"{_API_V3}/interviews/{interview_id}",
            json=body,
        )

    def delete(self, *, interview_id: str) -> None:
        """Delete an interview.

        Args:
            interview_id: The id of the interview.
        """
        self._request(
            method="DELETE",
            url=f"{_API_V3}/interviews/{interview_id}",
        )

    def get_transcript(
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
        response = self._request(
            method="GET",
            url=(f"{_API_V3}/interviews/{interview_id}/transcript"),
        )
        return InterviewTranscript.from_dict(data=response.json())


@beartype
class InterviewTemplatesNamespace(_Namespace):
    """Namespace for interview-template operations."""

    def list(
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
        response = self._request(
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

    def create(
        self,
        *,
        name: str,
        roles: Sequence[str] | None = None,
        team_share: int | None = None,
        questions: Sequence[str] | None = None,
        scorecard: int | None = None,
    ) -> InterviewTemplate:
        """Create an interview template.

        Args:
            name: The template name.
            roles: Roles for the template.
            team_share: Team-share flag.
            questions: Associated question ids.
            scorecard: Scorecard id.

        Returns:
            The created interview template.
        """
        body = _drop_none(
            {
                "name": name,
                "roles": list(roles) if roles is not None else None,
                "team_share": team_share,
                "questions": (
                    list(questions) if questions is not None else None
                ),
                "scorecard": scorecard,
            },
        )
        response = self._request(
            method="POST",
            url=f"{_API_V3}/interview_templates",
            json=body,
        )
        return InterviewTemplate.from_dict(data=response.json())

    def get(self, *, template_id: int | str) -> InterviewTemplate:
        """Retrieve an interview template.

        Args:
            template_id: The id of the template.

        Returns:
            The template.
        """
        response = self._request(
            method="GET",
            url=(f"{_API_V3}/interview_templates/{template_id}"),
        )
        return InterviewTemplate.from_dict(data=response.json())

    def update(
        self,
        *,
        template_id: int | str,
        name: str | None = None,
        roles: Sequence[str] | None = None,
        team_share: int | None = None,
        questions: Sequence[str] | None = None,
        scorecard: int | None = None,
    ) -> None:
        """Update an interview template.

        Args:
            template_id: The id of the template.
            name: New name.
            roles: New roles.
            team_share: New team-share flag.
            questions: New question ids.
            scorecard: New scorecard id.
        """
        body = _drop_none(
            {
                "name": name,
                "roles": list(roles) if roles is not None else None,
                "team_share": team_share,
                "questions": (
                    list(questions) if questions is not None else None
                ),
                "scorecard": scorecard,
            },
        )
        self._request(
            method="PUT",
            url=(f"{_API_V3}/interview_templates/{template_id}"),
            json=body,
        )

    def delete(self, *, template_id: int | str) -> None:
        """Delete an interview template.

        Args:
            template_id: The id of the template.
        """
        self._request(
            method="DELETE",
            url=(f"{_API_V3}/interview_templates/{template_id}"),
        )


@beartype
class QuestionsNamespace(_Namespace):
    """Namespace for question operations."""

    def list(
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
        response = self._request(
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

    def create(
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

        Returns:
            The created question.
        """
        body = _drop_none(
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
            },
        )
        response = self._request(
            method="POST",
            url=f"{_API_V3}/questions",
            json=body,
        )
        return Question.from_dict(data=response.json())

    def get(self, *, question_id: str) -> Question:
        """Retrieve a question.

        Args:
            question_id: The id of the question.

        Returns:
            The question.
        """
        response = self._request(
            method="GET",
            url=f"{_API_V3}/questions/{question_id}",
        )
        return Question.from_dict(data=response.json())

    def update(
        self,
        *,
        question_id: str,
        name: str | None = None,
        type: str | None = None,  # noqa: A002  # pylint: disable=redefined-builtin
        internal_notes: str | None = None,
        languages: Sequence[str] | None = None,
        problem_statement: str | None = None,
        recommended_duration: int | None = None,
        tags: Sequence[str] | None = None,
        options: Sequence[str] | None = None,
        answer: int | Sequence[int] | None = None,
    ) -> None:
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
        """
        body = _drop_none(
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
            },
        )
        self._request(
            method="PUT",
            url=f"{_API_V3}/questions/{question_id}",
            json=body,
        )

    def update_codestubs(
        self,
        *,
        question_id: str,
        codestubs: Mapping[str, JSONValue],
    ) -> None:
        """Update custom code-stubs for a question.

        Args:
            question_id: The id of the question.
            codestubs: A mapping describing the code-stubs.
        """
        self._request(
            method="PUT",
            url=(f"{_API_V3}/questions/{question_id}/custom_codestubs"),
            json=codestubs,
        )

    def generate_codestubs(
        self,
        *,
        question_id: str,
        body: Mapping[str, JSONValue] | None = None,
    ) -> dict[str, JSONValue]:
        """Generate code-stubs for a question.

        Args:
            question_id: The id of the question.
            body: An optional request body.

        Returns:
            The raw API response.
        """
        response = self._request(
            method="PUT",
            url=(f"{_API_V3}/questions/{question_id}/generate"),
            json=body if body is not None else {},
        )
        result: dict[str, JSONValue] = dict(response.json())
        return result

    def add_testcase(
        self,
        *,
        question_id: str,
        body: Mapping[str, JSONValue],
    ) -> dict[str, JSONValue]:
        """Add a test case to a question.

        Args:
            question_id: The id of the question.
            body: The test-case payload.

        Returns:
            The raw API response.
        """
        response = self._request(
            method="POST",
            url=(f"{_API_V3}/questions/{question_id}/testcases"),
            json=body,
        )
        result: dict[str, JSONValue] = dict(response.json())
        return result

    def update_testcase(
        self,
        *,
        question_id: str,
        testcase_id: str,
        body: Mapping[str, JSONValue],
    ) -> None:
        """Update an existing test case.

        Args:
            question_id: The id of the question.
            testcase_id: The id of the test case.
            body: The test-case payload.
        """
        self._request(
            method="PUT",
            url=(f"{_API_V3}/questions/{question_id}/testcases/{testcase_id}"),
            json=body,
        )

    def delete_testcase(
        self,
        *,
        question_id: str,
        testcase_id: str,
    ) -> None:
        """Delete a single test case.

        Args:
            question_id: The id of the question.
            testcase_id: The id of the test case.
        """
        self._request(
            method="DELETE",
            url=(f"{_API_V3}/questions/{question_id}/testcases/{testcase_id}"),
        )

    def delete_all_testcases(self, *, question_id: str) -> None:
        """Delete every test case on a question.

        Args:
            question_id: The id of the question.
        """
        self._request(
            method="DELETE",
            url=(f"{_API_V3}/questions/{question_id}/testcases/delete_all"),
        )


@beartype
class TestCandidatesNamespace(_Namespace):
    """Namespace for the candidates of a test."""

    def list(
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
        response = self._request(
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

    def search(
        self,
        *,
        test_id: str,
        search: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[TestCandidate]:
        """Search candidates within a test.

        Args:
            test_id: The id of the test.
            search: Search query.
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of candidates.
        """
        params = _list_params(
            limit=limit,
            offset=offset,
            extra={"search": search},
        )
        response = self._request(
            method="GET",
            url=f"{_API_V3}/tests/{test_id}/candidates/search",
            params=params,
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[TestCandidate] = [
            TestCandidate.from_dict(data=item) for item in raw_items
        ]
        return _make_page(items, payload)

    def invite(
        self,
        *,
        test_id: str,
        email: str,
        full_name: str | None = None,
        send_email: bool | None = None,
        evaluator_email: str | None = None,
        test_result_url: str | None = None,
        test_finish_url: str | None = None,
        tags: Sequence[str] | None = None,
        invite_valid_from: str | None = None,
        invite_valid_to: str | None = None,
        force: bool | None = None,
        force_reattempt: bool | None = None,
        accommodations: Mapping[str, JSONValue] | None = None,
        invite_metadata: Mapping[str, JSONValue] | None = None,
        webhook_authentication: Mapping[str, JSONValue] | None = None,
        accept_result_updates: bool | None = None,
        subject: str | None = None,
        message: str | None = None,
        template: str | None = None,
    ) -> TestCandidate:
        """Invite a candidate to a test.

        Args:
            test_id: The id of the test.
            email: Candidate email address.
            full_name: Candidate full name.
            send_email: Whether to send the invitation email.
            evaluator_email: Evaluator email.
            test_result_url: URL to which results are posted.
            test_finish_url: URL the candidate sees on finish.
            tags: Tags to set on the candidate.
            invite_valid_from: Invitation start time.
            invite_valid_to: Invitation end time.
            force: Force inviting even if previously invited.
            force_reattempt: Allow re-attempt.
            accommodations: Accommodation settings.
            invite_metadata: Arbitrary metadata.
            webhook_authentication: Webhook auth config.
            accept_result_updates: Accept result updates flag.
            subject: Custom email subject.
            message: Custom email message.
            template: Email template id.

        Returns:
            The created candidate.
        """
        body = _drop_none(
            {
                "email": email,
                "full_name": full_name,
                "send_email": send_email,
                "evaluator_email": evaluator_email,
                "test_result_url": test_result_url,
                "test_finish_url": test_finish_url,
                "tags": list(tags) if tags is not None else None,
                "invite_valid_from": invite_valid_from,
                "invite_valid_to": invite_valid_to,
                "force": force,
                "force_reattempt": force_reattempt,
                "accommodations": accommodations,
                "invite_metadata": invite_metadata,
                "webhook_authentication": webhook_authentication,
                "accept_result_updates": accept_result_updates,
                "subject": subject,
                "message": message,
                "template": template,
            },
        )
        response = self._request(
            method="POST",
            url=f"{_API_V3}/tests/{test_id}/candidates",
            json=body,
        )
        return TestCandidate.from_dict(data=response.json())

    def get(
        self,
        *,
        test_id: str,
        candidate_id: str,
        additional_fields: str | None = None,
    ) -> TestCandidate:
        """Retrieve a single candidate.

        Args:
            test_id: The id of the test.
            candidate_id: The id of the candidate.
            additional_fields: Comma-separated extra fields.

        Returns:
            The candidate.
        """
        params: dict[str, str | int] = {}
        if additional_fields is not None:
            params["additional_fields"] = additional_fields
        response = self._request(
            method="GET",
            url=(f"{_API_V3}/tests/{test_id}/candidates/{candidate_id}"),
            params=params or None,
        )
        return TestCandidate.from_dict(data=response.json())

    def update(
        self,
        *,
        test_id: str,
        candidate_id: str,
        full_name: str | None = None,
        ats_state: int | None = None,
        invite_valid_from: str | None = None,
        invite_valid_to: str | None = None,
        invite_metadata: Mapping[str, JSONValue] | None = None,
        evaluator_email: str | None = None,
        test_finish_url: str | None = None,
        test_result_url: str | None = None,
        webhook_authentication: Mapping[str, JSONValue] | None = None,
        accept_result_updates: bool | None = None,
        tags: Sequence[str] | None = None,
        accommodations: Mapping[str, JSONValue] | None = None,
    ) -> None:
        """Update a candidate.

        Args:
            test_id: The id of the test.
            candidate_id: The id of the candidate.
            full_name: New full name.
            ats_state: New ATS state.
            invite_valid_from: New invitation start time.
            invite_valid_to: New invitation end time.
            invite_metadata: New invite metadata.
            evaluator_email: New evaluator email.
            test_finish_url: New finish URL.
            test_result_url: New result URL.
            webhook_authentication: New webhook auth.
            accept_result_updates: New flag value.
            tags: New tags.
            accommodations: New accommodations.
        """
        body = _drop_none(
            {
                "full_name": full_name,
                "ats_state": ats_state,
                "invite_valid_from": invite_valid_from,
                "invite_valid_to": invite_valid_to,
                "invite_metadata": invite_metadata,
                "evaluator_email": evaluator_email,
                "test_finish_url": test_finish_url,
                "test_result_url": test_result_url,
                "webhook_authentication": webhook_authentication,
                "accept_result_updates": accept_result_updates,
                "tags": list(tags) if tags is not None else None,
                "accommodations": accommodations,
            },
        )
        self._request(
            method="PUT",
            url=(f"{_API_V3}/tests/{test_id}/candidates/{candidate_id}"),
            json=body,
        )

    def cancel_invite(
        self,
        *,
        test_id: str,
        candidate_id: str,
    ) -> None:
        """Cancel a candidate's invitation.

        Args:
            test_id: The id of the test.
            candidate_id: The id of the candidate.
        """
        self._request(
            method="DELETE",
            url=(
                f"{_API_V3}/tests/{test_id}/candidates/{candidate_id}/invite"
            ),
        )

    def delete_report(
        self,
        *,
        test_id: str,
        candidate_id: str,
    ) -> None:
        """Delete the report for a candidate.

        Args:
            test_id: The id of the test.
            candidate_id: The id of the candidate.
        """
        self._request(
            method="DELETE",
            url=(
                f"{_API_V3}/tests/{test_id}/candidates/{candidate_id}/report"
            ),
        )

    def get_report_pdf(
        self,
        *,
        test_id: str,
        candidate_id: str,
        format_: str = "url",
    ) -> dict[str, JSONValue]:
        """Retrieve the PDF report for a candidate.

        Args:
            test_id: The id of the test.
            candidate_id: The id of the candidate.
            format_: Format of the PDF (e.g. ``"url"``).

        Returns:
            The raw API response. When ``format_`` is
            ``"url"`` the response typically contains a URL
            for downloading the PDF.
        """
        response = self._request(
            method="GET",
            url=(f"{_API_V3}/tests/{test_id}/candidates/{candidate_id}/pdf"),
            params={"format": format_},
        )
        result: dict[str, JSONValue] = dict(response.json())
        return result


@beartype
class TestsNamespace(_Namespace):
    """Namespace for test operations."""

    def __init__(
        self,
        *,
        transport: Transport,
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
        self.candidates: TestCandidatesNamespace = TestCandidatesNamespace(
            transport=transport,
            base_url=base_url,
            headers=headers,
        )

    def list(
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
        response = self._request(
            method="GET",
            url=f"{_API_V3}/tests",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[Test] = [Test.from_dict(data=item) for item in raw_items]
        return _make_page(items, payload)

    def create(
        self,
        *,
        name: str,
        starttime: str | None = None,
        endtime: str | None = None,
        duration: int | None = None,
        instructions: str | None = None,
        locked: bool | None = None,
        draft: bool | None = None,
        languages: Sequence[str] | None = None,
        candidate_details: Sequence[str] | None = None,
        custom_acknowledge_text: str | None = None,
        cutoff_score: int | None = None,
        master_password: str | None = None,
        hide_compile_test: bool | None = None,
        tags: Sequence[str] | None = None,
        role_ids: Sequence[str] | None = None,
        experience: Sequence[str] | None = None,
        questions: Sequence[str] | None = None,
        mcq_incorrect_score: int | None = None,
        mcq_correct_score: int | None = None,
        shuffle_questions: bool | None = None,
        test_admins: Sequence[str] | None = None,
        hide_template: bool | None = None,
        enable_acknowledgement: bool | None = None,
        enable_proctoring: bool | None = None,
        enable_advanced_proctoring: bool | None = None,
        enable_secure_assessment_mode: bool | None = None,
        enable_ml_plagiarism_analysis: bool | None = None,
        enable_photo_identification: bool | None = None,
        ide_config: str | None = None,
    ) -> Test:
        """Create a test.

        Args:
            name: The name of the test.
            starttime: Test start time.
            endtime: Test end time.
            duration: Test duration in minutes.
            instructions: Test instructions.
            locked: Whether the test is locked.
            draft: Whether the test is a draft.
            languages: Allowed programming languages.
            candidate_details: Candidate detail fields.
            custom_acknowledge_text: Custom acknowledge text.
            cutoff_score: The cut-off score.
            master_password: Master password for the test.
            hide_compile_test: Hide compile-test option.
            tags: Tags applied to the test.
            role_ids: Role ids associated with the test.
            experience: Experience-level metadata.
            questions: Question ids to include.
            mcq_incorrect_score: Score for incorrect MCQ.
            mcq_correct_score: Score for correct MCQ.
            shuffle_questions: Whether to shuffle.
            test_admins: Test admin user ids.
            hide_template: Hide the template flag.
            enable_acknowledgement: Enable acknowledgement.
            enable_proctoring: Enable proctoring.
            enable_advanced_proctoring: Advanced proctoring.
            enable_secure_assessment_mode: Secure mode flag.
            enable_ml_plagiarism_analysis: ML plagiarism.
            enable_photo_identification: Photo ID flag.
            ide_config: IDE configuration.

        Returns:
            The created test.
        """
        body = _drop_none(
            {
                "name": name,
                "starttime": starttime,
                "endtime": endtime,
                "duration": duration,
                "instructions": instructions,
                "locked": locked,
                "draft": draft,
                "languages": (
                    list(languages) if languages is not None else None
                ),
                "candidate_details": (
                    list(candidate_details)
                    if candidate_details is not None
                    else None
                ),
                "custom_acknowledge_text": custom_acknowledge_text,
                "cutoff_score": cutoff_score,
                "master_password": master_password,
                "hide_compile_test": hide_compile_test,
                "tags": list(tags) if tags is not None else None,
                "role_ids": (list(role_ids) if role_ids is not None else None),
                "experience": (
                    list(experience) if experience is not None else None
                ),
                "questions": (
                    list(questions) if questions is not None else None
                ),
                "mcq_incorrect_score": mcq_incorrect_score,
                "mcq_correct_score": mcq_correct_score,
                "shuffle_questions": shuffle_questions,
                "test_admins": (
                    list(test_admins) if test_admins is not None else None
                ),
                "hide_template": hide_template,
                "enable_acknowledgement": enable_acknowledgement,
                "enable_proctoring": enable_proctoring,
                "enable_advanced_proctoring": (enable_advanced_proctoring),
                "enable_secure_assessment_mode": (
                    enable_secure_assessment_mode
                ),
                "enable_ml_plagiarism_analysis": (
                    enable_ml_plagiarism_analysis
                ),
                "enable_photo_identification": (enable_photo_identification),
                "ide_config": ide_config,
            },
        )
        response = self._request(
            method="POST",
            url=f"{_API_V3}/tests",
            json=body,
        )
        return Test.from_dict(data=response.json())

    def get(
        self,
        *,
        test_id: str,
        additional_fields: str | None = None,
    ) -> Test:
        """Retrieve a test.

        Args:
            test_id: The id of the test.
            additional_fields: Comma-separated extra fields.

        Returns:
            The test.
        """
        params: dict[str, str | int] = {}
        if additional_fields is not None:
            params["additional_fields"] = additional_fields
        response = self._request(
            method="GET",
            url=f"{_API_V3}/tests/{test_id}",
            params=params or None,
        )
        return Test.from_dict(data=response.json())

    def update(
        self,
        *,
        test_id: str,
        body: Mapping[str, JSONValue],
    ) -> None:
        """Update a test using a raw payload.

        Args:
            test_id: The id of the test.
            body: A mapping of fields to update. See the
                HackerRank API documentation for the
                supported fields.
        """
        self._request(
            method="PUT",
            url=f"{_API_V3}/tests/{test_id}",
            json=body,
        )

    def delete(self, *, test_id: str) -> None:
        """Delete a test.

        Args:
            test_id: The id of the test.
        """
        self._request(
            method="DELETE",
            url=f"{_API_V3}/tests/{test_id}",
        )

    def archive(self, *, test_id: str) -> None:
        """Archive a test.

        Args:
            test_id: The id of the test.
        """
        self._request(
            method="POST",
            url=f"{_API_V3}/tests/{test_id}/archive",
        )

    def list_inviters(
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
        response = self._request(
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
class TemplatesNamespace(_Namespace):
    """Namespace for invite-email templates."""

    def list(
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
        response = self._request(
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

    def get(self, *, template_id: str) -> Template:
        """Retrieve an invite template.

        Args:
            template_id: The id of the template.

        Returns:
            The template.
        """
        response = self._request(
            method="GET",
            url=f"{_API_V3}/templates/{template_id}",
        )
        return Template.from_dict(data=response.json())


@beartype
class UsersNamespace(_Namespace):
    """Namespace for user operations."""

    def list(
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
        response = self._request(
            method="GET",
            url=f"{_API_V3}/users",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[User] = [User.from_dict(data=item) for item in raw_items]
        return _make_page(items, payload)

    def search(
        self,
        *,
        search: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Page[User]:
        """Search users.

        Args:
            search: Search query.
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of users.
        """
        params = _list_params(
            limit=limit,
            offset=offset,
            extra={"search": search},
        )
        response = self._request(
            method="GET",
            url=f"{_API_V3}/users/search",
            params=params,
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[User] = [User.from_dict(data=item) for item in raw_items]
        return _make_page(items, payload)

    def create(
        self,
        *,
        email: str,
        firstname: str | None = None,
        lastname: str | None = None,
        country: str | None = None,
        role: str | None = None,
        send_email: bool | None = None,
        phone: str | None = None,
        questions_permission: int | None = None,
        tests_permission: int | None = None,
        interviews_permission: int | None = None,
        candidates_permission: int | None = None,
        shared_questions_permission: int | None = None,
        shared_tests_permission: int | None = None,
        shared_interviews_permission: int | None = None,
        shared_candidates_permission: int | None = None,
        company_admin: bool | None = None,
        team_admin: bool | None = None,
        teams: Sequence[str] | None = None,
    ) -> User:
        """Create a user.

        Args:
            email: Email address.
            firstname: First name.
            lastname: Last name.
            country: Country.
            role: Role.
            send_email: Send invite email flag.
            phone: Phone number.
            questions_permission: Permission level.
            tests_permission: Permission level.
            interviews_permission: Permission level.
            candidates_permission: Permission level.
            shared_questions_permission: Permission level.
            shared_tests_permission: Permission level.
            shared_interviews_permission: Permission level.
            shared_candidates_permission: Permission level.
            company_admin: Company admin flag.
            team_admin: Team admin flag.
            teams: Team ids the user belongs to.

        Returns:
            The created user.
        """
        body = _drop_none(
            {
                "email": email,
                "firstname": firstname,
                "lastname": lastname,
                "country": country,
                "role": role,
                "send_email": send_email,
                "phone": phone,
                "questions_permission": questions_permission,
                "tests_permission": tests_permission,
                "interviews_permission": interviews_permission,
                "candidates_permission": candidates_permission,
                "shared_questions_permission": (shared_questions_permission),
                "shared_tests_permission": (shared_tests_permission),
                "shared_interviews_permission": (shared_interviews_permission),
                "shared_candidates_permission": (shared_candidates_permission),
                "company_admin": company_admin,
                "team_admin": team_admin,
                "teams": (
                    [{"id": t} for t in teams] if teams is not None else None
                ),
            },
        )
        response = self._request(
            method="POST",
            url=f"{_API_V3}/users",
            json=body,
        )
        return User.from_dict(data=response.json())

    def get(self, *, user_id: str) -> User:
        """Retrieve a user.

        Args:
            user_id: The id of the user.

        Returns:
            The user.
        """
        response = self._request(
            method="GET",
            url=f"{_API_V3}/users/{user_id}",
        )
        return User.from_dict(data=response.json())

    def update(
        self,
        *,
        user_id: str,
        body: Mapping[str, JSONValue],
    ) -> None:
        """Update a user.

        Args:
            user_id: The id of the user.
            body: A mapping of fields to update. See the
                HackerRank API documentation for the
                supported fields.
        """
        self._request(
            method="PUT",
            url=f"{_API_V3}/users/{user_id}",
            json=body,
        )

    def delete(self, *, user_id: str) -> None:
        """Lock (deactivate) a user.

        Args:
            user_id: The id of the user.
        """
        self._request(
            method="DELETE",
            url=f"{_API_V3}/users/{user_id}",
        )


@beartype
class TeamMembershipsNamespace(_Namespace):
    """Namespace for user-team membership operations."""

    def list(
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
        response = self._request(
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

    def get(
        self,
        *,
        team_id: str,
        user_id: str,
    ) -> UserTeamMembership:
        """Retrieve a single membership.

        Args:
            team_id: The id of the team.
            user_id: The id of the user.

        Returns:
            The membership.
        """
        response = self._request(
            method="GET",
            url=f"{_API_V3}/teams/{team_id}/users/{user_id}",
        )
        return UserTeamMembership.from_dict(data=response.json())

    def create(
        self,
        *,
        team_id: str,
        user_id: str,
        license: str | None = None,  # noqa: A002  # pylint: disable=redefined-builtin
    ) -> UserTeamMembership:
        """Add a user to a team.

        Args:
            team_id: The id of the team.
            user_id: The id of the user.
            license: License kind to assign.

        Returns:
            The created membership.
        """
        params: dict[str, str | int] = {}
        if license is not None:
            params["license"] = license
        response = self._request(
            method="POST",
            url=f"{_API_V3}/teams/{team_id}/users/{user_id}",
            params=params or None,
        )
        return UserTeamMembership.from_dict(data=response.json())

    def delete(
        self,
        *,
        team_id: str,
        user_id: str,
    ) -> None:
        """Remove a user from a team.

        Args:
            team_id: The id of the team.
            user_id: The id of the user.
        """
        self._request(
            method="DELETE",
            url=f"{_API_V3}/teams/{team_id}/users/{user_id}",
        )


@beartype
class TeamsNamespace(_Namespace):
    """Namespace for team operations."""

    def __init__(
        self,
        *,
        transport: Transport,
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
        self.memberships: TeamMembershipsNamespace = TeamMembershipsNamespace(
            transport=transport,
            base_url=base_url,
            headers=headers,
        )

    def list(
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
        response = self._request(
            method="GET",
            url=f"{_API_V3}/teams",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw_items = list(payload.get("data", []))
        items: list[Team] = [Team.from_dict(data=item) for item in raw_items]
        return _make_page(items, payload)

    def create(
        self,
        *,
        name: str,
        recruiter_cap: int | None = None,
        developer_cap: int | None = None,
        invite_as: str | None = None,
        locations: Sequence[str] | None = None,
        departments: Sequence[str] | None = None,
    ) -> Team:
        """Create a team.

        Args:
            name: Team name.
            recruiter_cap: Recruiter seat cap.
            developer_cap: Developer seat cap.
            invite_as: Default role for invites.
            locations: Allowed locations.
            departments: Allowed departments.

        Returns:
            The created team.
        """
        body = _drop_none(
            {
                "name": name,
                "recruiter_cap": recruiter_cap,
                "developer_cap": developer_cap,
                "invite_as": invite_as,
                "locations": (
                    list(locations) if locations is not None else None
                ),
                "departments": (
                    list(departments) if departments is not None else None
                ),
            },
        )
        response = self._request(
            method="POST",
            url=f"{_API_V3}/teams",
            json=body,
        )
        return Team.from_dict(data=response.json())

    def get(self, *, team_id: str) -> Team:
        """Retrieve a team.

        Args:
            team_id: The id of the team.

        Returns:
            The team.
        """
        response = self._request(
            method="GET",
            url=f"{_API_V3}/teams/{team_id}",
        )
        return Team.from_dict(data=response.json())

    def update(
        self,
        *,
        team_id: str,
        name: str | None = None,
        recruiter_cap: int | None = None,
        developer_cap: int | None = None,
        invite_as: str | None = None,
        locations: Sequence[str] | None = None,
        departments: Sequence[str] | None = None,
    ) -> None:
        """Update a team.

        Args:
            team_id: The id of the team.
            name: New team name.
            recruiter_cap: New recruiter seat cap.
            developer_cap: New developer seat cap.
            invite_as: New default invite role.
            locations: New allowed locations.
            departments: New allowed departments.
        """
        body = _drop_none(
            {
                "name": name,
                "recruiter_cap": recruiter_cap,
                "developer_cap": developer_cap,
                "invite_as": invite_as,
                "locations": (
                    list(locations) if locations is not None else None
                ),
                "departments": (
                    list(departments) if departments is not None else None
                ),
            },
        )
        self._request(
            method="PUT",
            url=f"{_API_V3}/teams/{team_id}",
            json=body,
        )

    def delete(self, *, team_id: str) -> None:
        """Delete a team.

        Args:
            team_id: The id of the team.
        """
        self._request(
            method="DELETE",
            url=f"{_API_V3}/teams/{team_id}",
        )


@beartype
class AuditLogsNamespace(_Namespace):
    """Namespace for audit-log operations."""

    def list(
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
        response = self._request(
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
class ATSCodePairNamespace(_Namespace):
    """Namespace for ATS Codepair operations."""

    def invite(
        self,
        *,
        title: str | None = None,
        requisition_id: str | None = None,
        candidate_id: str | None = None,
        candidate: Mapping[str, JSONValue] | None = None,
        send_email: bool | None = None,
        interview_metadata: Mapping[str, JSONValue] | None = None,
    ) -> ATSCodePair:
        """Invite a candidate to an ATS Codepair interview.

        Args:
            title: The interview title.
            requisition_id: The ATS requisition id.
            candidate_id: The ATS candidate id.
            candidate: Candidate information.
            send_email: Whether to send an email.
            interview_metadata: Arbitrary metadata.

        Returns:
            The ATS Codepair result.
        """
        body = _drop_none(
            {
                "title": title,
                "requisition_id": requisition_id,
                "candidate_id": candidate_id,
                "candidate": candidate,
                "send_email": send_email,
                "interview_metadata": interview_metadata,
            },
        )
        response = self._request(
            method="POST",
            url=f"{_API_V3}/ats/codepair",
            json=body,
        )
        return ATSCodePair.from_dict(data=response.json())


@beartype
class ATSCodeScreenNamespace(_Namespace):
    """Namespace for ATS CodeScreen operations."""

    def invite(
        self,
        *,
        test_id: str,
        email: str,
        requisition_id: str | None = None,
        candidate_id: str | None = None,
        send_email: bool | None = None,
        test_result_url: str | None = None,
        webhook_authentication: Mapping[str, JSONValue] | None = None,
        accept_result_updates: bool | None = None,
        force: bool | None = None,
        force_reattempt_after: int | None = None,
        accommodations: Mapping[str, JSONValue] | None = None,
    ) -> ATSCodeScreen:
        """Invite a candidate to a CodeScreen test.

        Args:
            test_id: The test id.
            email: Candidate email.
            requisition_id: ATS requisition id.
            candidate_id: ATS candidate id.
            send_email: Whether to send an email.
            test_result_url: URL for posting results.
            webhook_authentication: Webhook auth config.
            accept_result_updates: Accept-updates flag.
            force: Force inviting flag.
            force_reattempt_after: Seconds before re-attempt.
            accommodations: Accommodation settings.

        Returns:
            The ATS CodeScreen result.
        """
        body = _drop_none(
            {
                "test_id": test_id,
                "email": email,
                "requisition_id": requisition_id,
                "candidate_id": candidate_id,
                "send_email": send_email,
                "test_result_url": test_result_url,
                "webhook_authentication": webhook_authentication,
                "accept_result_updates": accept_result_updates,
                "force": force,
                "force_reattempt_after": force_reattempt_after,
                "accommodations": accommodations,
            },
        )
        response = self._request(
            method="POST",
            url=f"{_API_V3}/ats/codescreen",
            json=body,
        )
        return ATSCodeScreen.from_dict(data=response.json())


@beartype
class ATSNamespace(_Namespace):
    """Namespace for ATS operations."""

    def __init__(
        self,
        *,
        transport: Transport,
        base_url: str,
        headers: dict[str, str],
    ) -> None:
        """Create the ATS namespace.

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
        self.codepair: ATSCodePairNamespace = ATSCodePairNamespace(
            transport=transport,
            base_url=base_url,
            headers=headers,
        )
        self.codescreen: ATSCodeScreenNamespace = ATSCodeScreenNamespace(
            transport=transport,
            base_url=base_url,
            headers=headers,
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
        The populated ``SCIMPage`` instance.
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


@beartype
class SCIMUsersNamespace(_Namespace):
    """Namespace for SCIM v2 user operations."""

    def list(
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
        response = self._request(
            method="GET",
            url="/Users",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw = list(payload.get("Resources", []))
        items: list[SCIMUser] = [SCIMUser.from_dict(data=item) for item in raw]
        return _make_scim_page(items, payload)

    def create(
        self,
        *,
        body: Mapping[str, JSONValue],
    ) -> SCIMUser:
        """Create a SCIM user.

        Args:
            body: The SCIM user payload.

        Returns:
            The created SCIM user.
        """
        response = self._request(
            method="POST",
            url="/Users",
            json=body,
        )
        return SCIMUser.from_dict(data=response.json())

    def get(self, *, scim_user_id: str) -> SCIMUser:
        """Retrieve a SCIM user.

        Args:
            scim_user_id: The id of the SCIM user.

        Returns:
            The SCIM user.
        """
        response = self._request(
            method="GET",
            url=f"/Users/{scim_user_id}",
        )
        return SCIMUser.from_dict(data=response.json())

    def replace(
        self,
        *,
        scim_user_id: str,
        body: Mapping[str, JSONValue],
    ) -> SCIMUser:
        """Replace a SCIM user (PUT).

        Args:
            scim_user_id: The id of the SCIM user.
            body: The full SCIM user payload.

        Returns:
            The updated SCIM user.
        """
        response = self._request(
            method="PUT",
            url=f"/Users/{scim_user_id}",
            json=body,
        )
        return SCIMUser.from_dict(data=response.json())

    def patch(
        self,
        *,
        scim_user_id: str,
        operations: Sequence[Mapping[str, JSONValue]],
    ) -> SCIMUser:
        """Patch a SCIM user.

        Args:
            scim_user_id: The id of the SCIM user.
            operations: The SCIM patch operations.

        Returns:
            The updated SCIM user.
        """
        body: dict[str, JSONValue] = {
            "operations": [dict(op) for op in operations],
        }
        response = self._request(
            method="PATCH",
            url=f"/Users/{scim_user_id}",
            json=body,
        )
        return SCIMUser.from_dict(data=response.json())

    def delete(self, *, scim_user_id: str) -> None:
        """Lock a SCIM user.

        Args:
            scim_user_id: The id of the SCIM user.
        """
        self._request(
            method="DELETE",
            url=f"/Users/{scim_user_id}",
        )


@beartype
class SCIMGroupsNamespace(_Namespace):
    """Namespace for SCIM v2 group (team) operations."""

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> SCIMPage[SCIMTeam]:
        """List SCIM groups.

        Args:
            limit: Number of records to fetch.
            offset: Offset of records.

        Returns:
            A page of SCIM teams.
        """
        response = self._request(
            method="GET",
            url="/Groups",
            params=_list_params(limit=limit, offset=offset),
        )
        payload = response.json()
        raw = list(payload.get("Resources", []))
        items: list[SCIMTeam] = [SCIMTeam.from_dict(data=item) for item in raw]
        return _make_scim_page(items, payload)

    def create(self, *, body: Mapping[str, JSONValue]) -> SCIMTeam:
        """Create a SCIM group.

        Args:
            body: The SCIM group payload.

        Returns:
            The created SCIM team.
        """
        response = self._request(
            method="POST",
            url="/Groups",
            json=body,
        )
        return SCIMTeam.from_dict(data=response.json())

    def get(self, *, scim_group_id: str) -> SCIMTeam:
        """Retrieve a SCIM group.

        Args:
            scim_group_id: The id of the SCIM group.

        Returns:
            The SCIM team.
        """
        response = self._request(
            method="GET",
            url=f"/Groups/{scim_group_id}",
        )
        return SCIMTeam.from_dict(data=response.json())

    def patch(
        self,
        *,
        scim_group_id: str,
        operations: Sequence[Mapping[str, JSONValue]],
    ) -> SCIMTeam:
        """Patch a SCIM group.

        Args:
            scim_group_id: The id of the SCIM group.
            operations: The SCIM patch operations.

        Returns:
            The updated SCIM team.
        """
        body: dict[str, JSONValue] = {
            "operations": [dict(op) for op in operations],
        }
        response = self._request(
            method="PATCH",
            url=f"/Groups/{scim_group_id}",
            json=body,
        )
        return SCIMTeam.from_dict(data=response.json())

    def delete(self, *, scim_group_id: str) -> None:
        """Deprovision a SCIM group.

        Args:
            scim_group_id: The id of the SCIM group.
        """
        self._request(
            method="DELETE",
            url=f"/Groups/{scim_group_id}",
        )


@beartype
class SCIMNamespace(_Namespace):
    """Namespace for SCIM v2 operations."""

    def __init__(
        self,
        *,
        transport: Transport,
        base_url: str,
        headers: dict[str, str],
    ) -> None:
        """Create the SCIM namespace.

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
        self.users: SCIMUsersNamespace = SCIMUsersNamespace(
            transport=transport,
            base_url=base_url,
            headers=headers,
        )
        self.groups: SCIMGroupsNamespace = SCIMGroupsNamespace(
            transport=transport,
            base_url=base_url,
            headers=headers,
        )


@beartype
class HackerRank:
    """A client for the HackerRank for Work API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://www.hackerrank.com",
        transport: Transport | None = None,
    ) -> None:
        """Create a new HackerRank client.

        Args:
            api_key: The API key for authentication.
            base_url: The base URL for the API.
            transport: The HTTP transport. Defaults to
                ``HTTPXTransport()``.
        """
        self.base_url = base_url
        resolved_transport = transport or HTTPXTransport()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }
        self.interviews: InterviewsNamespace = InterviewsNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.interview_templates: InterviewTemplatesNamespace = (
            InterviewTemplatesNamespace(
                transport=resolved_transport,
                base_url=base_url,
                headers=headers,
            )
        )
        self.questions: QuestionsNamespace = QuestionsNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.tests: TestsNamespace = TestsNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.templates: TemplatesNamespace = TemplatesNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.users: UsersNamespace = UsersNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.teams: TeamsNamespace = TeamsNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.audit_logs: AuditLogsNamespace = AuditLogsNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.ats: ATSNamespace = ATSNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        self.scim: SCIMNamespace = SCIMNamespace(
            transport=resolved_transport,
            base_url=base_url,
            headers=headers,
        )
        if isinstance(resolved_transport, HTTPXTransport):
            self._close = resolved_transport.close
        else:
            self._close = lambda: None

    def close(self) -> None:
        """Close the underlying transport if it supports closing."""
        self._close()

    def __enter__(self) -> Self:
        """Enter the context manager.

        Returns:
            This client instance.
        """
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager and close the transport."""
        self.close()
