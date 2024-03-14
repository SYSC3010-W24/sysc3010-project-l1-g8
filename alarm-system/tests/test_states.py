import pytest
from states import State, Context, WaitForEmergency, AlarmActive
from messages import Messages


class FakeContext:
    """Represents a fake context object for testing state actions."""

    def __init__(self) -> None:
        self.state: State = WaitForEmergency()


@pytest.fixture
def ctx() -> FakeContext:
    """Returns fake context that can be modified per test case."""
    return FakeContext()


def test_wait_for_emergency_entry(ctx: Context) -> None:
    """Tests that the entry logic for the WaitForEmergency state behaves as expected when an emergency is active."""

    ctx.wait_for_message = lambda: Messages.EMERGENCY

    state = WaitForEmergency()
    state.entry(ctx)  # type: ignore
    assert ctx.state.__class__ == AlarmActive


def test_wait_for_emergency_emergency(ctx: Context) -> None:
    """Tests that the entry logic for the WaitForEmergency state behaves as expected."""

    state = WaitForEmergency()
    state.emergency(ctx)  # type: ignore
    assert ctx.state.__class__ == AlarmActive


def test_wait_for_emergency_emergency_over(ctx: Context) -> None:
    """Tests that the entry logic for the WaitForEmergency state behaves as expected."""

    state = WaitForEmergency()
    state.emergency_over(ctx)  # type: ignore
    assert ctx.state.__class__ == WaitForEmergency
