"""Contract coverage for the complete documented operation catalogue."""

from __future__ import annotations

import json
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import respx

from hackerrank.api import api_catalogue, api_operations
from hackerrank.async_client import AsyncHackerRank
from hackerrank.client import HackerRank

if TYPE_CHECKING:
    from hackerrank.types import JSONValue


def test_catalogue_matches_every_documented_operation() -> None:
    """Exclude introduction pseudo-routes while retaining all real
    routes.
    """
    spec = json.loads(
        s=(Path(__file__).parents[1] / "openapi.json").read_text()
    )
    expected = {
        (method.upper(), path.split("?")[0])
        for path, methods in spec["paths"].items()
        for method in methods
        if method in {"get", "post", "put", "patch", "delete"}
    }
    operations = api_operations()
    assert {
        (value.method, value.path) for value in operations.values()
    } == expected
    assert "definitions" in api_catalogue()
    created = operations["api_create_user"]
    assert created.group == "Users"
    assert created.summary == "Create user"
    assert bool(created.description)
    assert created.body_schema is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
async def test_every_operation_uses_its_documented_method_and_host(
    *, asynchronous: bool
) -> None:
    """Exercise every route through both actual client transports."""
    with respx.mock(assert_all_called=True) as router:
        route = router.route().respond(
            status_code=HTTPStatus.OK, json={"ok": True}
        )
        with HackerRank(api_key="v3-token") as sync_client:
            async with AsyncHackerRank(api_key="v3-token") as async_client:
                for operation in api_operations().values():
                    path_parameters = {
                        str(object=parameter["name"]): "value/+"
                        for parameter in operation.parameters
                        if parameter["location"] == "path"
                    }
                    query = {
                        str(object=parameter["name"]): "1"
                        for parameter in operation.parameters
                        if parameter["location"] == "query"
                        and parameter["required"] is True
                    }
                    if asynchronous:
                        response = await async_client.api.call(
                            operation=operation.id,
                            path_parameters=path_parameters,
                            query=query,
                            body={} if operation.body_required else None,
                            scim_api_key="scim-token",
                        )
                    else:
                        response = sync_client.api.call(
                            operation=operation.id,
                            path_parameters=path_parameters,
                            query=query,
                            body={} if operation.body_required else None,
                            scim_api_key="scim-token",
                        )
                    request = route.calls.last.request
                    assert request.method == operation.method
                    assert request.url.host == (
                        "services.hackerrank.com"
                        if operation.scim
                        else "www.hackerrank.com"
                    )
                    assert request.headers["Authorization"] == (
                        "Bearer scim-token"
                        if operation.scim
                        else "Bearer v3-token"
                    )
                    if bool(path_parameters):
                        assert b"value%2F%2B" in request.url.raw_path
                    assert response.status == HTTPStatus.OK
                    assert response.data == {"ok": True}


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames="asynchronous", argvalues=[False, True])
async def test_pending_and_empty_responses(*, asynchronous: bool) -> None:
    """Preserve Retry-After, 202 and 204 rather than assuming object
    bodies.
    """
    with respx.mock(assert_all_called=True) as router:
        _ = router.get(
            url="https://www.hackerrank.com/x/api/v3/interviews/1/artifacts"
        ).respond(
            status_code=HTTPStatus.ACCEPTED,
            headers={"Retry-After": "180"},
            json={"message": "Pending"},
        )
        _ = router.delete(
            url="https://www.hackerrank.com/x/api/v3/users/1"
        ).respond(status_code=HTTPStatus.NO_CONTENT)
        if asynchronous:
            async with AsyncHackerRank(api_key="test") as client:
                pending = await client.api.call(
                    operation="api_get_interview_artifacts",
                    path_parameters={"interview_id": "1"},
                )
                empty = await client.api.call(
                    operation="api_lock_user", path_parameters={"id": "1"}
                )
        else:
            with HackerRank(api_key="test") as sync_client:
                pending = sync_client.api.call(
                    operation="api_get_interview_artifacts",
                    path_parameters={"interview_id": "1"},
                )
                empty = sync_client.api.call(
                    operation="api_lock_user", path_parameters={"id": "1"}
                )
    assert pending.status == HTTPStatus.ACCEPTED
    assert pending.headers["retry-after"] == "180"
    assert empty.status == HTTPStatus.NO_CONTENT
    assert empty.data is None


def test_query_normalization_and_separate_scim_credentials() -> None:
    """Correct Swagger path/query mistakes and preserve literal PDF
    options.
    """
    operations = api_operations()
    users = operations["api_list_all_users"]
    assert all(value["location"] == "query" for value in users.parameters)
    search = operations["api_search_users"]
    assert "search" in [value["name"] for value in search.parameters]
    with (
        HackerRank(api_key="v3-token") as client,
        pytest.raises(
            expected_exception=ValueError, match="separate scim_api_key"
        ),
    ):
        _ = client.api.call(operation="api_scim_list_users")
    with respx.mock(assert_all_called=True) as router:
        route = router.get(
            url="https://www.hackerrank.com/x/api/v3/tests/1/candidates/2/pdf"
        ).respond(
            status_code=HTTPStatus.OK,
            json={"url": "https://example.com/report"},
        )
        with HackerRank(api_key="test") as client:
            _ = client.api.call(
                operation="api_get_report_pdf",
                path_parameters={"test_id": "1", "candidate_id": "2"},
            )
    assert route.calls.last.request.url.params["format"] == "url"


@pytest.mark.parametrize(
    argnames=("operation", "path", "query", "body", "message"),
    argvalues=[
        ("unknown", None, None, None, "Unknown API operation"),
        ("api_get_interview_artifacts", None, None, None, "Missing path"),
        (
            "api_get_interview_artifacts",
            {"interview_id": ""},
            None,
            None,
            "Missing path",
        ),
        ("api_search_users", None, None, None, "Missing query"),
        ("api_create_user", None, None, None, "requires a JSON body"),
        ("api_list_all_users", None, {"limit": {}}, None, "scalars"),
    ],
)
def test_invalid_requests_fail_before_transport(
    operation: str,
    path: dict[str, str | int] | None,
    query: dict[str, JSONValue] | None,
    body: dict[str, JSONValue] | None,
    message: str,
) -> None:
    """Reject missing inputs and non-scalar query fields before
    sending.
    """
    with HackerRank(api_key="synthetic") as client:
        with pytest.raises(expected_exception=ValueError, match=message):
            _ = client.api.call(
                operation=operation,
                path_parameters=path,
                query=query,
                body=body,
            )


def test_query_preserves_scalar_types_and_arrays() -> None:
    """Keep false, zero, CSV arrays and omitted null fields distinct."""
    with respx.mock(assert_all_called=True) as router:
        route = router.get(
            url="https://www.hackerrank.com/x/api/v3/users"
        ).respond(status_code=HTTPStatus.OK, json={})
        with HackerRank(api_key="synthetic") as client:
            _ = client.api.call(
                operation="api_list_all_users",
                query={"flags": [True, False, "text", 0, 1.5], "omit": None},
            )
    assert dict(route.calls.last.request.url.params) == {
        "flags": "true,false,text,0,1.5"
    }


@pytest.mark.asyncio
async def test_async_scim_requires_its_own_credential() -> None:
    """Never use an ordinary API credential for provisioning."""
    async with AsyncHackerRank(api_key="synthetic") as client:
        with pytest.raises(
            expected_exception=ValueError, match="separate scim_api_key"
        ):
            _ = await client.api.call(
                operation="api_scim_list_users", scim_api_key=" "
            )
