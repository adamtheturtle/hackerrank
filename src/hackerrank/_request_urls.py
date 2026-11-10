"""Canonical URLs for HackerRank question writes and project uploads."""

from urllib.parse import urlsplit, urlunsplit


def question_write_url(*, method: str, url: str) -> str:
    """Use canonical question-write paths without following redirects."""
    parsed = urlsplit(url=url)
    if method in {"POST", "PUT"} and (
        parsed.path == "/x/api/v3/questions"
        or parsed.path.startswith("/x/api/v3/questions/")
    ):
        return urlunsplit(
            components=parsed._replace(path=parsed.path.rstrip("/") + "/")
        )
    return url


def project_upload_question_url(*, method: str, url: str) -> str | None:
    """Identify the question read needed to verify a project upload."""
    parsed = urlsplit(url=url)
    if (
        method != "POST"
        or not parsed.path.startswith("/x/api/v3/questions/")
        or not parsed.path.rstrip("/").endswith("/upload_project_zip")
    ):
        return None
    return urlunsplit(
        components=parsed._replace(
            path=parsed.path.rsplit(sep="/upload_project_zip", maxsplit=1)[0],
            query="",
            fragment="",
        )
    )
