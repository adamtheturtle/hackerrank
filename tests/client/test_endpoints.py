"""Tests for `hackerrank` endpoints client."""

from http import HTTPStatus

import pytest
import respx

from hackerrank.client import HackerRank


def test_list_tests(
    hackerrank_client: HackerRank,
) -> None:
    """The tests list endpoint returns a populated page."""
    result = hackerrank_client.tests.list()
    assert result.total >= 0


@pytest.mark.parametrize(
    argnames="invalid_data",
    argvalues=["invalid", ["invalid"]],
)
def test_list_tests_rejects_invalid_items(invalid_data: object) -> None:
    """The tests list rejects malformed response items."""
    with respx.mock(base_url="https://www.hackerrank.com") as router:
        _ = router.get(url="/x/api/v3/tests").respond(
            status_code=HTTPStatus.OK,
            json={"data": invalid_data},
        )
        client = HackerRank(api_key="test-key")
        with pytest.raises(
            expected_exception=TypeError,
            match="valid objects",
        ):
            _ = client.tests.list()
        client.close()


def test_list_interviews(
    hackerrank_client: HackerRank,
) -> None:
    """The interviews list endpoint returns a page."""
    result = hackerrank_client.interviews.list()
    assert result.total >= 0


def test_list_interviews_rejects_invalid_items() -> None:
    """The interviews list rejects malformed response items."""
    with respx.mock(base_url="https://www.hackerrank.com") as router:
        _ = router.get(url="/x/api/v3/interviews").respond(
            status_code=HTTPStatus.OK,
            json={"data": "invalid"},
        )
        client = HackerRank(api_key="test-key")
        with pytest.raises(expected_exception=TypeError):
            _ = client.interviews.list()
        client.close()


def test_get_interview_rejects_invalid_response() -> None:
    """The interview endpoint rejects a malformed response shape."""
    with respx.mock(base_url="https://www.hackerrank.com") as router:
        _ = router.get(url="/x/api/v3/interviews/1").respond(
            status_code=HTTPStatus.OK,
            json=[],
        )
        client = HackerRank(api_key="test-key")
        with pytest.raises(
            expected_exception=TypeError,
            match="did not have the expected shape",
        ):
            _ = client.interviews.get(interview_id="1")
        client.close()


def test_list_users(
    hackerrank_client: HackerRank,
) -> None:
    """The users list endpoint returns a page."""
    result = hackerrank_client.users.list()
    assert result.total >= 0


def test_list_teams(
    hackerrank_client: HackerRank,
) -> None:
    """The teams list endpoint returns a page."""
    result = hackerrank_client.teams.list()
    assert result.total >= 0


def test_list_templates(
    hackerrank_client: HackerRank,
) -> None:
    """The templates list endpoint returns a page."""
    result = hackerrank_client.templates.list()
    assert result.total >= 0


def test_list_audit_logs(
    hackerrank_client: HackerRank,
) -> None:
    """The audit-log list endpoint returns a page."""
    result = hackerrank_client.audit_logs.list()
    assert result.total >= 0


def test_list_interview_templates(
    hackerrank_client: HackerRank,
) -> None:
    """The interview-template list returns a page."""
    result = hackerrank_client.interview_templates.list()
    assert result.total >= 0


def test_list_questions(
    hackerrank_client: HackerRank,
) -> None:
    """The questions list endpoint returns a page."""
    result = hackerrank_client.questions.list()
    assert result.total >= 0


def test_get_environment_rejects_invalid_data() -> None:
    """The environment endpoint rejects malformed response data."""
    with respx.mock(base_url="https://www.hackerrank.com") as router:
        _ = router.get(url="/x/api/v3/environments/1").respond(
            status_code=HTTPStatus.OK,
            json={"environment": "invalid"},
        )
        client = HackerRank(api_key="test-key")
        with pytest.raises(
            expected_exception=TypeError,
            match="an environment",
        ):
            _ = client.environments.get(environment_id=1)
        client.close()
