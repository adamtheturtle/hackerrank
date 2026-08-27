"""Tests that every side-effecting call documents whether it can repeat.

Callers cannot work this out from the HTTP method. Some of the ``POST``
endpoints replace state and are safe to send twice, while others append
a test case or send another email. The library already holds the
answer, as the ``repeatable`` argument to ``_request``, so these tests
require that each method says the same thing in prose.
"""

import ast
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SYNC = _ROOT / "src" / "hackerrank" / "client.py"
_ASYNC = _ROOT / "src" / "hackerrank" / "async_client.py"
_MODULES = (_SYNC, _ASYNC)

_SAFE = "Safe to retry:"
_UNSAFE = "Not safe to retry:"


def _note_of(*, docstring: str) -> str | None:
    """Read the retry-safety paragraph out of a docstring.

    Args:
        docstring: The docstring to read.

    Returns:
        The paragraph as a single line, or ``None`` if there is not
        one.
    """
    for paragraph in docstring.split(sep="\n\n"):
        joined = " ".join(paragraph.split())
        if joined.startswith((_SAFE, _UNSAFE)):
            return joined
    return None


def _requests_of(
    *,
    method: ast.AsyncFunctionDef | ast.FunctionDef,
) -> list[tuple[str, bool]]:
    """Find the requests a method sends.

    Args:
        method: The method to read.

    Returns:
        The HTTP method and ``repeatable`` argument of each call to
        ``_request`` in the method's body.
    """
    requests: list[tuple[str, bool]] = []
    for node in ast.walk(node=method):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "_request"):
            continue
        keywords = {keyword.arg: keyword.value for keyword in node.keywords}
        requests.append(
            (
                ast.literal_eval(node_or_string=keywords["method"]),
                ast.literal_eval(node_or_string=keywords["repeatable"]),
            ),
        )
    return requests


def _side_effecting(*, module: Path) -> dict[str, tuple[bool, str | None]]:
    """Find the methods which send a request other than a ``GET``.

    Args:
        module: The module to read.

    Returns:
        For each such method, keyed by ``Class.method`` with any
        ``Async`` prefix removed, its ``repeatable`` argument and its
        retry-safety note.
    """
    tree = ast.parse(source=module.read_text(encoding="utf-8"))
    found: dict[str, tuple[bool, str | None]] = {}
    for class_node in tree.body:
        if not isinstance(class_node, ast.ClassDef):
            continue
        for method in class_node.body:
            if not isinstance(method, ast.AsyncFunctionDef | ast.FunctionDef):
                continue
            repeatable = [
                flag
                for verb, flag in _requests_of(method=method)
                if verb != "GET"
            ]
            if not repeatable:
                continue
            key = f"{class_node.name.removeprefix('Async')}.{method.name}"
            found[key] = (
                all(repeatable),
                _note_of(docstring=ast.get_docstring(node=method) or ""),
            )
    return found


class TestNoteOf:
    """Tests for reading the note out of a docstring."""

    @staticmethod
    def test_finds_the_paragraph() -> None:
        """The paragraph is returned joined onto one line."""
        docstring = (
            "Archive a test.\n"
            "\n"
            "Safe to retry: an archived test\n"
            "stays archived.\n"
            "\n"
            "Args:\n"
            "    test_id: The id of the test.\n"
        )
        note = _note_of(docstring=docstring)
        assert note == "Safe to retry: an archived test stays archived."

    @staticmethod
    def test_no_note() -> None:
        """A docstring without a note reads as ``None``."""
        assert _note_of(docstring="List the tests.\n") is None


class TestRetrySafetyIsDocumented:
    """Tests for the retry-safety note on each side-effecting method."""

    @staticmethod
    def test_every_method_says_whether_it_is_safe() -> None:
        """Each side-effecting method's docstring answers the question."""
        documented = {
            f"{module.stem}:{key}": note is not None
            for module in _MODULES
            for key, (_, note) in _side_effecting(module=module).items()
        }
        assert documented == dict.fromkeys(documented, True)

    @staticmethod
    def test_the_note_matches_the_repeatable_argument() -> None:
        """The prose and the ``repeatable`` argument agree.

        A method documented as safe to retry is one the library will
        retry when ``retries`` is set, and the other way around.
        """
        said = {}
        marked = {}
        for module in _MODULES:
            for key, (repeatable, note) in _side_effecting(
                module=module,
            ).items():
                said[f"{module.stem}:{key}"] = not (note or "").startswith(
                    _UNSAFE,
                )
                marked[f"{module.stem}:{key}"] = repeatable
        assert said == marked

    @staticmethod
    def test_the_sync_and_async_notes_match() -> None:
        """A call is documented the same way in both clients."""
        sync = {
            key: note
            for key, (_, note) in _side_effecting(module=_SYNC).items()
        }
        asynchronous = {
            key: note
            for key, (_, note) in _side_effecting(module=_ASYNC).items()
        }
        assert sync == asynchronous
