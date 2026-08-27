"""Tests that news fragments are named so ``towncrier`` finds them."""

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_NEWSFRAGMENTS = _ROOT / "newsfragments"

# ``towncrier`` builds this name from ``[tool.towncrier]`` in
# ``pyproject.toml``: the fragment's issue number, then the ``directory``
# of its type, then ``.rst``.  A fragment which does not match is
# silently ignored at release time, so its entry never reaches the
# changelog.
_FRAGMENT_NAME = re.compile(pattern=r"^\d+\.change\.rst$")


class TestNewsfragmentNames:
    """Tests for the contents of the ``newsfragments`` directory."""

    @staticmethod
    def test_fragments_are_discoverable() -> None:
        """Every fragment is named the way ``towncrier`` expects."""
        fragments = [
            path
            for path in _NEWSFRAGMENTS.iterdir()
            if path.name != ".gitkeep"
        ]
        misnamed = [
            path.name
            for path in fragments
            if not _FRAGMENT_NAME.match(string=path.name)
        ]
        assert not misnamed

    @staticmethod
    def test_no_subdirectories() -> None:
        """No fragment hides in a subdirectory.

        ``towncrier`` reads a subdirectory as a *section*, not as a
        fragment type, so fragments filed in one are never rendered.
        """
        subdirectories = [
            path.name for path in _NEWSFRAGMENTS.iterdir() if path.is_dir()
        ]
        assert not subdirectories
