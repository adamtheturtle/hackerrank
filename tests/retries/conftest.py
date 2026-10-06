"""Fixtures for retries tests."""

import asyncio
import time

import pytest


@pytest.fixture(name="sleeps", autouse=True)
def fixture_sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record, rather than perform, the delays between attempts.

    This is autouse so that no test ever really waits.

    Args:
        monkeypatch: The pytest monkeypatch fixture.

    Returns:
        The recorded delays, in the order they were requested.
    """
    recorded: list[float] = []
    monkeypatch.setattr(target=time, name="sleep", value=recorded.append)

    async def _record(delay: float) -> None:
        """Record an awaited delay without waiting.

        Args:
            delay: The number of seconds which would be slept.
        """
        recorded.append(delay)

    monkeypatch.setattr(target=asyncio, name="sleep", value=_record)
    return recorded
