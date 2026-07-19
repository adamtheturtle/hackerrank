"""Tests for the synchronous HackerRank client."""

from http import HTTPStatus

import httpx
import pytest
import respx

import hackerrank.client as client_module
from hackerrank.client import HackerRank
from hackerrank.exceptions import (
    AuthenticationError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    HackerRankError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UnprocessableEntityError,
)
from hackerrank.transports import (
    HTTPStatusError,
    HTTPXTransport,
    Transport,
    TransportResponse,
)


class TestHackerRank:
    """Tests for ``HackerRank``."""

    @staticmethod
    def test_default_base_url() -> None:
        """The default base URL is the HackerRank app."""
        client = HackerRank(api_key="test-key")
        assert client.base_url == "https://www.hackerrank.com"

    @staticmethod
    def test_custom_base_url() -> None:
        """A custom base URL can be provided."""
        client = HackerRank(
            api_key="test-key",
            base_url="https://custom.example.com",
        )
        assert client.base_url == "https://custom.example.com"

    @staticmethod
    def test_default_scim_base_url() -> None:
        """SCIM uses its own host, distinct from the v3 base URL."""
        client = HackerRank(api_key="test-key")
        assert (
            client.scim_base_url == "https://services.hackerrank.com/scim/v2"
        )
        assert client.scim.users.base_url == client.scim_base_url

    @staticmethod
    def test_custom_scim_base_url() -> None:
        """A custom SCIM base URL can be provided."""
        client = HackerRank(
            api_key="test-key",
            scim_base_url="https://scim.example.com/v2",
        )
        assert client.scim_base_url == "https://scim.example.com/v2"
        assert client.scim.groups.base_url == "https://scim.example.com/v2"

    @staticmethod
    def test_close() -> None:
        """The client can be closed."""
        client = HackerRank(api_key="test-key")
        client.close()

    @staticmethod
    def test_context_manager() -> None:
        """The client can be used as a context manager."""
        with HackerRank(api_key="test-key") as client:
            assert isinstance(client, HackerRank)

    @staticmethod
    def test_close_transport_without_close() -> None:
        """Closing works when the transport has no close method."""

        class _NoCloseTransport:
            """A transport without a close method."""

            def __call__(
                self,
                *,
                method: str,
                url: str,
                headers: dict[str, str],
                params: dict[str, str | int] | None = None,
                json: object | None = None,
                files: object | None = None,
            ) -> TransportResponse:  # pragma: no cover
                """Make a request."""
                del method, url, headers, params, json, files
                raise NotImplementedError

        client = HackerRank(
            api_key="test-key",
            transport=_NoCloseTransport(),
        )
        client.close()

    @staticmethod
    def test_namespaces_are_attached() -> None:
        """The client exposes the expected namespaces."""
        client = HackerRank(api_key="test-key")
        assert isinstance(client.interviews, client_module.InterviewsNamespace)
        assert isinstance(
            client.interview_templates,
            client_module.InterviewTemplatesNamespace,
        )
        assert isinstance(
            client.environments,
            client_module.EnvironmentsNamespace,
        )
        assert isinstance(client.questions, client_module.QuestionsNamespace)
        assert isinstance(client.tests, client_module.TestsNamespace)
        assert isinstance(
            client.tests.candidates,
            client_module.TestCandidatesNamespace,
        )
        assert isinstance(client.templates, client_module.TemplatesNamespace)
        assert isinstance(client.users, client_module.UsersNamespace)
        assert isinstance(client.teams, client_module.TeamsNamespace)
        assert isinstance(
            client.teams.memberships,
            client_module.TeamMembershipsNamespace,
        )
        assert isinstance(client.audit_logs, client_module.AuditLogsNamespace)
        assert isinstance(client.ats, client_module.ATSNamespace)
        assert isinstance(
            client.ats.codepair,
            client_module.ATSCodePairNamespace,
        )
        assert isinstance(
            client.ats.codescreen,
            client_module.ATSCodeScreenNamespace,
        )
        assert isinstance(client.scim, client_module.SCIMNamespace)
        assert isinstance(client.scim.users, client_module.SCIMUsersNamespace)
        assert isinstance(
            client.scim.groups,
            client_module.SCIMGroupsNamespace,
        )


class TestHTTPXTransport:
    """Tests for ``HTTPXTransport``."""

    @staticmethod
    def test_is_transport() -> None:
        """HTTPXTransport satisfies the Transport protocol."""
        assert isinstance(HTTPXTransport(), Transport)

    @staticmethod
    def test_close() -> None:
        """The transport can be closed."""
        transport = HTTPXTransport()
        transport.close()


class TestListEndpoints:
    """Tests that the list endpoints unwrap pagination."""

    @staticmethod
    def test_list_tests(
        hackerrank_client: HackerRank,
    ) -> None:
        """The tests list endpoint returns a populated page."""
        result = hackerrank_client.tests.list()
        assert result.total >= 0

    @staticmethod
    def test_list_interviews(
        hackerrank_client: HackerRank,
    ) -> None:
        """The interviews list endpoint returns a page."""
        result = hackerrank_client.interviews.list()
        assert result.total >= 0

    @staticmethod
    def test_list_users(
        hackerrank_client: HackerRank,
    ) -> None:
        """The users list endpoint returns a page."""
        result = hackerrank_client.users.list()
        assert result.total >= 0

    @staticmethod
    def test_list_teams(
        hackerrank_client: HackerRank,
    ) -> None:
        """The teams list endpoint returns a page."""
        result = hackerrank_client.teams.list()
        assert result.total >= 0

    @staticmethod
    def test_list_templates(
        hackerrank_client: HackerRank,
    ) -> None:
        """The templates list endpoint returns a page."""
        result = hackerrank_client.templates.list()
        assert result.total >= 0

    @staticmethod
    def test_list_audit_logs(
        hackerrank_client: HackerRank,
    ) -> None:
        """The audit-log list endpoint returns a page."""
        result = hackerrank_client.audit_logs.list()
        assert result.total >= 0

    @staticmethod
    def test_list_interview_templates(
        hackerrank_client: HackerRank,
    ) -> None:
        """The interview-template list returns a page."""
        result = hackerrank_client.interview_templates.list()
        assert result.total >= 0

    @staticmethod
    def test_list_questions(
        hackerrank_client: HackerRank,
    ) -> None:
        """The questions list endpoint returns a page."""
        result = hackerrank_client.questions.list()
        assert result.total >= 0


class TestErrorHandling:
    """Tests for HTTP error mapping."""

    @staticmethod
    @pytest.mark.parametrize(
        argnames=("status_code", "expected"),
        argvalues=[
            (HTTPStatus.BAD_REQUEST, BadRequestError),
            (HTTPStatus.UNAUTHORIZED, AuthenticationError),
            (HTTPStatus.FORBIDDEN, ForbiddenError),
            (HTTPStatus.NOT_FOUND, NotFoundError),
            (HTTPStatus.CONFLICT, ConflictError),
            (
                HTTPStatus.UNPROCESSABLE_ENTITY,
                UnprocessableEntityError,
            ),
            (HTTPStatus.TOO_MANY_REQUESTS, RateLimitError),
            (
                HTTPStatus.INTERNAL_SERVER_ERROR,
                ServerError,
            ),
        ],
    )
    def test_status_maps_to_specific_error(
        status_code: HTTPStatus,
        expected: type[HackerRankError],
    ) -> None:
        """Each known status code raises a specific subclass.

        Args:
            status_code: The HTTP status code to simulate.
            expected: The expected exception subclass.
        """
        with respx.mock(
            base_url="https://www.hackerrank.com",
            assert_all_called=False,
        ) as router:
            router.get(
                url__regex=r".*/x/api/v3/tests.*",
            ).mock(
                return_value=httpx.Response(
                    status_code=status_code,
                ),
            )
            client = HackerRank(api_key="test-key")
            try:
                with pytest.raises(expected_exception=expected):
                    client.tests.list()
            finally:
                client.close()

    @staticmethod
    def test_unknown_status_uses_base_error() -> None:
        """An unmapped status raises the base ``HackerRankError``."""
        with respx.mock(
            base_url="https://www.hackerrank.com",
            assert_all_called=False,
        ) as router:
            router.get(
                url__regex=r".*/x/api/v3/tests.*",
            ).mock(
                return_value=httpx.Response(status_code=418),
            )
            client = HackerRank(api_key="test-key")
            try:
                with pytest.raises(expected_exception=HackerRankError):
                    client.tests.list()
            finally:
                client.close()


class TestTransportResponse:
    """Tests for ``TransportResponse``."""

    @staticmethod
    def test_raise_for_status_no_op() -> None:
        """No exception is raised for 2xx responses."""
        response = TransportResponse(
            status_code=HTTPStatus.OK,
            headers={},
            content=b"{}",
        )
        response.raise_for_status()

    @staticmethod
    def test_raise_for_status_raises() -> None:
        """4xx responses raise ``HTTPStatusError``."""
        response = TransportResponse(
            status_code=HTTPStatus.NOT_FOUND,
            headers={},
            content=b"{}",
        )
        with pytest.raises(expected_exception=HTTPStatusError):
            response.raise_for_status()

    @staticmethod
    def test_json() -> None:
        """JSON content is parsed correctly."""
        response = TransportResponse(
            status_code=HTTPStatus.OK,
            headers={},
            content=b'{"a": 1}',
        )
        assert response.json() == {"a": 1}
