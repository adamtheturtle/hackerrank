"""Per-test fixtures."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import httpx
import pytest
import pytest_asyncio
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

_BASE_URL = "https://www.hackerrank.com"

_PAGE: dict[str, object] = {
    "data": [],
    "page_total": 0,
    "offset": 0,
    "previous": "",
    "next": "",
    "first": "",
    "last": "",
    "total": 0,
}
_SCIM_PAGE: dict[str, object] = {
    "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
    "Resources": [],
    "startIndex": 1,
    "itemsPerPage": 0,
    "totalResults": 0,
}
_TEST_OBJ = {"id": "t1", "name": "T"}
_CANDIDATE_OBJ = {"id": "c1", "email": "x@y.com"}
_CANDIDATE_INVITE_OBJ = {
    "test_link": "https://example.com/invite",
    "email": "x@y.com",
    "id": 10000,
}
_INTERVIEW_OBJ = {
    "id": "iv1",
    "status": "scheduled",
    "url": "https://example.com/iv1",
}
_INTERVIEW_TEMPLATE_OBJ = {
    "id": "template-1",
    "name": "T",
    "questions": [2687118],
}
_ENVIRONMENT_OBJ = {
    "id": 92,
    "name": "PERN",
    "tags": ["fullstack"],
    "runtime": [{"name": "Node", "version": "20"}],
}
_QUESTION_OBJ = {"id": "q1", "type": "code", "name": "Q"}
_TEMPLATE_OBJ = {"id": "tpl1", "name": "T"}
_USER_OBJ = {"id": "u1", "email": "u@x.com"}
_TEAM_OBJ = {"id": "tm1", "name": "Engineering"}
_MEMBERSHIP_OBJ = {"team": "tm1", "user": "u1"}
_SCIM_USER_OBJ = {"id": "scim-1", "userName": "x@y.com"}
_SCIM_TEAM_OBJ = {"id": "scim-2", "displayName": "G"}


def _response_for(  # noqa: C901, PLR0911, PLR0912  # pylint: disable=too-complex,too-many-branches
    request: httpx.Request,
) -> httpx.Response:
    """Return a plausible response for ``request``.

    Args:
        request: The intercepted HTTP request.

    Returns:
        A response whose body satisfies the corresponding
        client parser.
    """
    path = request.url.path
    method = request.method
    if method == "GET":
        if path in {
            "/x/api/v3/tests",
            "/x/api/v3/interviews",
            "/x/api/v3/users",
            "/x/api/v3/teams",
            "/x/api/v3/templates",
            "/x/api/v3/interview_templates",
            "/x/api/v3/questions",
            "/x/api/v3/audit_log",
        }:
            return httpx.Response(status_code=200, json=_PAGE)
        if path == "/x/api/v3/environments":
            return httpx.Response(
                status_code=200,
                json={"environments": [_ENVIRONMENT_OBJ]},
            )
        if path.endswith(("/inviters", "/candidates")):
            return httpx.Response(status_code=200, json=_PAGE)
        if path.endswith(("/candidates/search", "/users/search")):
            return httpx.Response(status_code=200, json=_PAGE)
        if re.fullmatch(pattern=r"/x/api/v3/teams/[^/]+/users", string=path):
            return httpx.Response(status_code=200, json=_PAGE)
        if path in {"/scim/v2/Users", "/scim/v2/Groups"}:
            return httpx.Response(status_code=200, json=_SCIM_PAGE)
        if path.endswith("/transcript"):
            return httpx.Response(
                status_code=200,
                json={"messages": []},
            )
        if re.fullmatch(
            pattern=r"/x/api/v3/tests/[^/]+/candidates/[^/]+/pdf", string=path
        ):
            return httpx.Response(
                status_code=200,
                json={"url": "https://example.com/r.pdf"},
            )
        if re.fullmatch(
            pattern=r"/x/api/v3/tests/[^/]+/candidates/[^/]+", string=path
        ):
            return httpx.Response(
                status_code=200,
                json=_CANDIDATE_OBJ,
            )
        if re.fullmatch(pattern=r"/x/api/v3/tests/[^/]+", string=path):
            return httpx.Response(status_code=200, json=_TEST_OBJ)
        if re.fullmatch(pattern=r"/x/api/v3/interviews/[^/]+", string=path):
            return httpx.Response(
                status_code=200,
                json=_INTERVIEW_OBJ,
            )
        if re.fullmatch(
            pattern=r"/x/api/v3/interview_templates/[^/]+", string=path
        ):
            return httpx.Response(
                status_code=200,
                json=_INTERVIEW_TEMPLATE_OBJ,
            )
        if re.fullmatch(pattern=r"/x/api/v3/environments/[^/]+", string=path):
            return httpx.Response(
                status_code=200,
                json={
                    "environment": {
                        **_ENVIRONMENT_OBJ,
                        "active": True,
                        "sample_project_url": (
                            "https://example.com/project.zip"
                        ),
                    },
                },
            )
        if re.fullmatch(pattern=r"/x/api/v3/questions/[^/]+", string=path):
            return httpx.Response(
                status_code=200,
                json=_QUESTION_OBJ,
            )
        if re.fullmatch(pattern=r"/x/api/v3/templates/[^/]+", string=path):
            return httpx.Response(
                status_code=200,
                json=_TEMPLATE_OBJ,
            )
        if re.fullmatch(pattern=r"/x/api/v3/users/[^/]+", string=path):
            return httpx.Response(status_code=200, json=_USER_OBJ)
        if re.fullmatch(
            pattern=r"/x/api/v3/teams/[^/]+/users/[^/]+", string=path
        ):
            return httpx.Response(
                status_code=200,
                json=_MEMBERSHIP_OBJ,
            )
        if re.fullmatch(pattern=r"/x/api/v3/teams/[^/]+", string=path):
            return httpx.Response(status_code=200, json=_TEAM_OBJ)
        if re.fullmatch(pattern=r"/scim/v2/Users/[^/]+", string=path):
            return httpx.Response(
                status_code=200,
                json=_SCIM_USER_OBJ,
            )
        if re.fullmatch(pattern=r"/scim/v2/Groups/[^/]+", string=path):
            return httpx.Response(
                status_code=200,
                json=_SCIM_TEAM_OBJ,
            )
    if method == "POST":
        if path == "/x/api/v3/tests":
            return httpx.Response(status_code=200, json=_TEST_OBJ)
        if path == "/x/api/v3/interviews":
            return httpx.Response(
                status_code=200,
                json=_INTERVIEW_OBJ,
            )
        if path == "/x/api/v3/interview_templates":
            return httpx.Response(
                status_code=200,
                json=_INTERVIEW_TEMPLATE_OBJ,
            )
        if path == "/x/api/v3/questions":
            return httpx.Response(
                status_code=200,
                json=_QUESTION_OBJ,
            )
        if re.fullmatch(
            pattern=r"/x/api/v3/questions/[^/]+/upload_project_zip",
            string=path,
        ):
            return httpx.Response(
                status_code=200,
                json={
                    "file_url": "https://example.com/project.zip",
                    "file_path": "question_projects/q1/project.zip",
                },
            )
        if re.fullmatch(
            pattern=r"/x/api/v3/questions/[^/]+/testcases", string=path
        ):
            return httpx.Response(status_code=200, json={"id": 1})
        if path == "/x/api/v3/users":
            return httpx.Response(status_code=200, json=_USER_OBJ)
        if path == "/x/api/v3/teams":
            return httpx.Response(status_code=200, json=_TEAM_OBJ)
        if re.fullmatch(
            pattern=r"/x/api/v3/teams/[^/]+/users/[^/]+", string=path
        ):
            return httpx.Response(
                status_code=200,
                json=_MEMBERSHIP_OBJ,
            )
        if re.fullmatch(
            pattern=r"/x/api/v3/tests/[^/]+/candidates", string=path
        ):
            return httpx.Response(
                status_code=200,
                json=_CANDIDATE_INVITE_OBJ,
            )
        if path.endswith("/archive"):
            return httpx.Response(status_code=204)
        if path == "/x/api/v3/ats/codepair":
            return httpx.Response(
                status_code=200,
                json=_INTERVIEW_OBJ,
            )
        if path == "/x/api/v3/ats/codescreen":
            return httpx.Response(
                status_code=200,
                json=_CANDIDATE_INVITE_OBJ,
            )
        if path == "/scim/v2/Users":
            return httpx.Response(
                status_code=200,
                json=_SCIM_USER_OBJ,
            )
        if path == "/scim/v2/Groups":
            return httpx.Response(
                status_code=200,
                json=_SCIM_TEAM_OBJ,
            )
    if method == "PUT":
        if re.fullmatch(
            pattern=r"/x/api/v3/interview_templates/[^/]+",
            string=path,
        ):
            return httpx.Response(
                status_code=200,
                json=_INTERVIEW_TEMPLATE_OBJ,
            )
        if re.fullmatch(
            pattern=r"/x/api/v3/interviews/[^/]+",
            string=path,
        ):
            return httpx.Response(
                status_code=200,
                json=_INTERVIEW_OBJ,
            )
        if re.fullmatch(
            pattern=r"/x/api/v3/tests/[^/]+/candidates/[^/]+",
            string=path,
        ):
            return httpx.Response(
                status_code=200,
                json=_CANDIDATE_OBJ,
            )
        if re.fullmatch(
            pattern=r"/x/api/v3/questions/[^/]+/(custom_codestubs|generate)",
            string=path,
        ):
            return httpx.Response(status_code=200, json={})
        if path == "/x/api/v3/questions/q-with-body":
            return httpx.Response(
                status_code=200,
                json=_QUESTION_OBJ,
            )
        if re.fullmatch(pattern=r"/scim/v2/Users/[^/]+", string=path):
            return httpx.Response(
                status_code=200,
                json=_SCIM_USER_OBJ,
            )
        return httpx.Response(status_code=204)
    if method == "PATCH":
        if re.fullmatch(pattern=r"/scim/v2/Users/[^/]+", string=path):
            return httpx.Response(
                status_code=200,
                json=_SCIM_USER_OBJ,
            )
        if re.fullmatch(pattern=r"/scim/v2/Groups/[^/]+", string=path):
            return httpx.Response(
                status_code=200,
                json=_SCIM_TEAM_OBJ,
            )
    if method == "DELETE":
        return httpx.Response(status_code=204)
    return httpx.Response(status_code=200, json={})


@pytest.fixture(name="hackerrank_client")
def fixture_hackerrank_client(
    mock_hackerrank_api: respx.MockRouter,
) -> Generator[HackerRank]:
    """Provide a sync ``HackerRank`` client wired to the mock API.

    Args:
        mock_hackerrank_api: The respx mock router fixture.

    Yields:
        A ``HackerRank`` client.
    """
    del mock_hackerrank_api
    client = HackerRank(api_key="test-key")
    try:
        yield client
    finally:
        client.close()


@pytest_asyncio.fixture(name="async_hackerrank_client")
async def fixture_async_hackerrank_client(
    mock_hackerrank_api: respx.MockRouter,
) -> AsyncGenerator[AsyncHackerRank]:
    """Provide an async ``AsyncHackerRank`` client.

    Args:
        mock_hackerrank_api: The respx mock router fixture.

    Yields:
        An ``AsyncHackerRank`` client.
    """
    del mock_hackerrank_api
    client = AsyncHackerRank(api_key="test-key")
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture(name="stub_router")
def fixture_stub_router() -> Generator[respx.MockRouter]:
    """A respx router that stubs every HackerRank endpoint.

    Yields:
        The respx mock router with a side-effect wired to
        ``_response_for``.
    """
    # No ``base_url`` guard: the v3 API and the SCIM v2 API live on
    # different hosts, so the router must intercept both. Requests are
    # dispatched by path inside ``_response_for``.
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=_response_for)
        yield router


@pytest.fixture(name="sync_client")
def fixture_sync_client(
    stub_router: respx.MockRouter,
) -> Generator[HackerRank]:
    """Provide a sync client wired to the stub router.

    Args:
        stub_router: The stub router fixture.

    Yields:
        A ``HackerRank`` client.
    """
    del stub_router
    client = HackerRank(api_key="test-key")
    try:
        yield client
    finally:
        client.close()


@pytest_asyncio.fixture(name="async_client")
async def fixture_async_client(
    stub_router: respx.MockRouter,
) -> AsyncGenerator[AsyncHackerRank]:
    """Provide an async client wired to the stub router.

    Args:
        stub_router: The stub router fixture.

    Yields:
        An ``AsyncHackerRank`` client.
    """
    del stub_router
    client = AsyncHackerRank(api_key="test-key")
    try:
        yield client
    finally:
        await client.aclose()
