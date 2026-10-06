"""Question operations shared by retry tests."""

from hackerrank.client import HackerRank


def create_question(*, client: HackerRank) -> None:
    """Create a question, which is never safe to repeat.

    Args:
        client: The client to create the question with.
    """
    _ = client.questions.create(
        name="Q",
        type="code",
        problem_statement="Do the thing.",
        recommended_duration=10,
    )
