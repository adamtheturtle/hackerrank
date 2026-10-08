"""Tests that news fragments are named so ``towncrier`` finds them."""

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_NEWSFRAGMENTS = _ROOT / "newsfragments"

# ``towncrier`` builds this name from ``[tool.towncrier]`` in
# ``pyproject.toml``: the fragment's issue number, then the ``directory``
# of its type, then ``.md``. Orphan changes use a descriptive ``+name``.
# The configuration rejects invalid names during release assembly.
_FRAGMENT_NAME = re.compile(pattern=r"^(?:\d+|\+[\w-]+)\.change\.md$")


def test_fragments_are_discoverable() -> None:
    """Every fragment is named the way ``towncrier`` expects."""
    fragments = [
        path
        for path in _NEWSFRAGMENTS.iterdir()
        if path.name not in {".gitkeep", "README.md"}
    ]
    misnamed = [
        path.name
        for path in fragments
        if not bool(_FRAGMENT_NAME.match(string=path.name))
    ]
    assert misnamed == []


def test_no_subdirectories() -> None:
    """No fragment hides in a subdirectory.

    ``towncrier`` reads a subdirectory as a *section*, not as a
    fragment type, so fragments filed in one are never rendered.
    """
    subdirectories = [
        path.name for path in _NEWSFRAGMENTS.iterdir() if path.is_dir()
    ]
    assert subdirectories == []
