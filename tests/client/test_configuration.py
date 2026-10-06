"""Tests for `hackerrank` configuration client."""

from collections.abc import Mapping
from http import HTTPStatus

import httpx
import respx

import hackerrank.client as client_module
from hackerrank._request_types import MultipartFiles
from hackerrank.client import HackerRank
from hackerrank.transports import (
    HTTPXTransport,
    TransportResponse,
)
from hackerrank.types import JSONValue


def test_default_base_url() -> None:
    """The default base URL is the HackerRank app."""
    client = HackerRank(api_key="test-key")
    assert client.base_url == "https://www.hackerrank.com"


def test_custom_base_url() -> None:
    """A custom base URL can be provided."""
    client = HackerRank(
        api_key="test-key",
        base_url="https://custom.example.com",
    )
    assert client.base_url == "https://custom.example.com"


def test_trailing_slash_base_urls_are_normalized() -> None:
    """Trailing slashes are stripped from custom base URLs."""
    client = HackerRank(
        api_key="test-key",
        base_url="https://custom.example.com/",
        scim_base_url="https://scim.example.com/v2/",
    )
    assert client.base_url == "https://custom.example.com"
    assert client.users.base_url == "https://custom.example.com"
    assert client.scim_base_url == "https://scim.example.com/v2"
    assert client.scim.users.base_url == "https://scim.example.com/v2"


def test_falsy_transport_is_preserved() -> None:
    """A falsy custom transport is not replaced by the default."""

    class _FalsyTransport:
        """A transport whose ``__bool__`` returns ``False``."""

        def __bool__(self) -> bool:
            """Report as falsy."""
            return False

        def __call__(
            self,
            *,
            method: str,
            url: str,
            headers: dict[str, str],
            params: dict[str, str | int] | None,
            json: Mapping[str, JSONValue] | None,
            files: MultipartFiles,
        ) -> TransportResponse:
            """Make a request."""
            del method, url, headers, params, json, files
            return TransportResponse(
                status_code=HTTPStatus.OK,
                headers={},
                content=b'{"data": [], "total": 0}',
            )

    transport = _FalsyTransport()
    assert not bool(transport)
    client = HackerRank(api_key="test-key", transport=transport)
    assert client.users.transport is transport

    assert (client.users.list()).total == 0


def test_default_scim_base_url() -> None:
    """SCIM uses its own host, distinct from the v3 base URL."""
    client = HackerRank(api_key="test-key")
    assert client.scim_base_url == "https://services.hackerrank.com/scim/v2"
    assert client.scim.users.base_url == client.scim_base_url


def test_custom_scim_base_url() -> None:
    """A custom SCIM base URL can be provided."""
    client = HackerRank(
        api_key="test-key",
        scim_base_url="https://scim.example.com/v2",
    )
    assert client.scim_base_url == "https://scim.example.com/v2"
    assert client.scim.groups.base_url == "https://scim.example.com/v2"


def test_close() -> None:
    """The client can be closed."""
    client = HackerRank(api_key="test-key")
    client.close()


def test_context_manager() -> None:
    """The client can be used as a context manager."""
    with HackerRank(api_key="test-key") as client:
        assert isinstance(client, HackerRank)


def test_close_transport_without_close() -> None:
    """Closing works when the transport has no close method."""
    with (
        respx.mock(assert_all_called=True) as router,
        HTTPXTransport() as transport,
    ):
        _ = router.get(
            url="https://www.hackerrank.com/x/api/v3/tests",
        ).mock(return_value=httpx.Response(status_code=200, json={"data": []}))
        client = HackerRank(
            api_key="test-key",
            transport=transport.__call__,
        )
        client.close()
        with HackerRank(
            api_key="test-key",
            transport=transport.__call__,
        ) as other_client:
            assert not bool(other_client.tests.list().data)


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
    assert isinstance(client.candidates, client_module.CandidatesNamespace)
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
