"""Per-test fixtures."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
import respx

from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from hackerrank.types import JSONValue

_BASE_URL = "https://www.hackerrank.com"

_PAGE: dict[str, JSONValue] = {
    "data": [],
    "page_total": 0,
    "offset": 0,
    "previous": "",
    "next": "",
    "first": "",
    "last": "",
    "total": 0,
}
_SCIM_PAGE: dict[str, JSONValue] = {
    "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
    "Resources": [],
    "startIndex": 1,
    "itemsPerPage": 0,
    "totalResults": 0,
}
_TEST_OBJ: dict[str, JSONValue] = {"id": "t1", "name": "T"}
_CANDIDATE_OBJ: dict[str, JSONValue] = {"id": "c1", "email": "x@y.com"}
_CANDIDATE_INVITE_OBJ: dict[str, JSONValue] = {
    "test_link": "https://example.com/invite",
    "email": "x@y.com",
    "id": 10000,
}
_INTERVIEW_OBJ: dict[str, JSONValue] = {
    "id": "iv1",
    "status": "scheduled",
    "url": "https://example.com/iv1",
}
_INTERVIEW_TEMPLATE_OBJ: dict[str, JSONValue] = {
    "id": "template-1",
    "name": "T",
    "questions": [2687118],
}
_ENVIRONMENT_OBJ: dict[str, JSONValue] = {
    "id": 92,
    "name": "PERN",
    "tags": ["fullstack"],
    "runtime": [{"name": "Node", "version": "20"}],
}
_QUESTION_OBJ: dict[str, JSONValue] = {"id": "q1", "type": "code", "name": "Q"}
_TEMPLATE_OBJ: dict[str, JSONValue] = {"id": "tpl1", "name": "T"}
_USER_OBJ: dict[str, JSONValue] = {"id": "u1", "email": "u@x.com"}
_TEAM_OBJ: dict[str, JSONValue] = {"id": "tm1", "name": "Engineering"}
_MEMBERSHIP_OBJ: dict[str, JSONValue] = {"team": "tm1", "user": "u1"}
_SCIM_USER_OBJ: dict[str, JSONValue] = {"id": "scim-1", "userName": "x@y.com"}
_SCIM_TEAM_OBJ: dict[str, JSONValue] = {"id": "scim-2", "displayName": "G"}
_SCIM_MESSAGE_OBJ: dict[str, JSONValue] = {
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
    "message": "Successful transaction",
}
_SCIM_GROUP_MESSAGE_OBJ: dict[str, JSONValue] = {
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
    "message": "Successful transaction",
}


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
        The respx mock router with representative endpoint responses.
    """
    responses: dict[str, dict[str, JSONValue]] = {
        "GET": {
            (
                r"/x/api/v3/(tests|interviews|users|teams|templates|"
                r"interview_templates|questions|audit_log)"
            ): _PAGE,
            r"/x/api/v3/environments": {"environments": [_ENVIRONMENT_OBJ]},
            r".*/(inviters|candidates|candidates/search|users/search)": _PAGE,
            r"/x/api/v3/teams/[^/]+/users": _PAGE,
            r"/scim/v2/(Users|Groups)": _SCIM_PAGE,
            r".*/transcript": {"messages": []},
            r"/x/api/v3/tests/[^/]+/candidates/[^/]+/pdf": {
                "url": "https://example.com/r.pdf"
            },
            r"/x/api/v3/tests/[^/]+/candidates/[^/]+": _CANDIDATE_OBJ,
            r"/x/api/v3/tests/[^/]+": _TEST_OBJ,
            r"/x/api/v3/interviews/[^/]+": _INTERVIEW_OBJ,
            r"/x/api/v3/interview_templates/[^/]+": _INTERVIEW_TEMPLATE_OBJ,
            r"/x/api/v3/environments/[^/]+": {
                "environment": {
                    **_ENVIRONMENT_OBJ,
                    "active": True,
                    "sample_project_url": "https://example.com/project.zip",
                },
            },
            r"/x/api/v3/questions/[^/]+": _QUESTION_OBJ,
            r"/x/api/v3/templates/[^/]+": _TEMPLATE_OBJ,
            r"/x/api/v3/users/[^/]+": _USER_OBJ,
            r"/x/api/v3/teams/[^/]+/users/[^/]+": _MEMBERSHIP_OBJ,
            r"/x/api/v3/teams/[^/]+": _TEAM_OBJ,
            r"/scim/v2/Users/[^/]+": _SCIM_USER_OBJ,
            r"/scim/v2/Groups/[^/]+": _SCIM_TEAM_OBJ,
        },
        "POST": {
            r"/x/api/v3/tests": _TEST_OBJ,
            r"/x/api/v3/interviews": _INTERVIEW_OBJ,
            r"/x/api/v3/interview_templates": _INTERVIEW_TEMPLATE_OBJ,
            r"/x/api/v3/questions": _QUESTION_OBJ,
            r"/x/api/v3/questions/[^/]+/upload_project_zip": {
                "file_url": "https://example.com/project.zip",
                "file_path": "question_projects/q1/project.zip",
            },
            r"/x/api/v3/questions/[^/]+/testcases": {"id": 1},
            r"/x/api/v3/users": _USER_OBJ,
            r"/x/api/v3/teams": _TEAM_OBJ,
            r"/x/api/v3/teams/[^/]+/users/[^/]+": _MEMBERSHIP_OBJ,
            r"/x/api/v3/tests/[^/]+/candidates": _CANDIDATE_INVITE_OBJ,
            r"/x/api/v3/ats/codepair": _INTERVIEW_OBJ,
            r"/x/api/v3/ats/codescreen": _CANDIDATE_INVITE_OBJ,
            r"/scim/v2/Users": _SCIM_USER_OBJ,
            r"/scim/v2/Groups": _SCIM_TEAM_OBJ,
        },
        "PUT": {
            r"/x/api/v3/interview_templates/[^/]+": _INTERVIEW_TEMPLATE_OBJ,
            r"/x/api/v3/interviews/[^/]+": _INTERVIEW_OBJ,
            r"/x/api/v3/tests/[^/]+/candidates/[^/]+": _CANDIDATE_OBJ,
            r"/x/api/v3/questions/[^/]+/(custom_codestubs|generate)": {},
            r"/x/api/v3/questions/q-with-body": _QUESTION_OBJ,
            r"/scim/v2/Users/[^/]+": _SCIM_USER_OBJ,
        },
        "PATCH": {
            r"/scim/v2/Users/[^/]+": _SCIM_MESSAGE_OBJ,
            r"/scim/v2/Groups/[^/]+": _SCIM_GROUP_MESSAGE_OBJ,
        },
    }
    # Both the v3 and SCIM hosts use these routes. Register specific
    # responses first so the fallback routes do not hide them.
    with respx.mock(assert_all_called=False) as router:
        for method, paths in responses.items():
            for path, payload in paths.items():
                _ = router.route(
                    method=method,
                    path__regex=f"^{path}$",
                ).respond(status_code=200, json=payload)
        _ = router.route(method="POST", path__regex=r".*/archive$").respond(
            status_code=204,
        )
        _ = router.route(method__in=["PUT", "DELETE"]).respond(status_code=204)
        _ = router.route().respond(status_code=200, json={})
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
