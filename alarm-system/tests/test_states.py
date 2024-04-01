import pytest
from states import State, Context, WaitForEmergency, AlarmOn, AlarmOff


class FakeContext:
    """Represents a fake context object for testing state actions."""

    def __init__(self) -> None:
        self.state: State = WaitForEmergency()


@pytest.fixture
def ctx() -> FakeContext:
    """Returns fake context that can be modified per test case."""
    return FakeContext()


def test_wait_for_emergency_entry(ctx: Context) -> None:
    """
    Tests that the entry logic for the WaitForEmergency state behaves as
    expected when an emergency is active.
    """

    state = WaitForEmergency()
    state.entry(ctx)
    assert ctx.state.__class__ is WaitForEmergency


def test_wait_for_emergency_emergency(ctx: Context) -> None:
    """
    Tests that the emergency event handler for the WaitForEmergency state
    behaves as expected.
    """

    state = WaitForEmergency()
    state.emergency(ctx)
    assert ctx.state.__class__ is AlarmOn


def test_wait_for_emergency_emergency_over(ctx: Context) -> None:
    """
    Tests that the emergency over event handler for the WaitForEmergency state
    behaves as expected.
    """

    state = WaitForEmergency()
    state.emergency_over(ctx)
    assert ctx.state.__class__ is WaitForEmergency


def test_alarm_on_entry(ctx: Context) -> None:
    """Tests that the entry logic for the AlarmOn state behaves as expected."""

    def _assert_on(value: bool) -> None:
        """Fails if the passed value is not true."""
        assert value

    def _assert_timeout_one(duration: int) -> None:
        """Fails if the passed value is not '1'."""
        assert duration == 1

    ctx.set_alarm_state = _assert_on  # type: ignore
    ctx.set_timeout = _assert_timeout_one  # type: ignore

    ctx.state = AlarmOn()
    ctx.state.entry(ctx)
    assert ctx.state.__class__ is AlarmOn


def test_alarm_on_emergency(ctx: Context) -> None:
    """
    Tests that the emergency event handler for the AlarmOn state behaves as
    expected.
    """

    ctx.state = AlarmOn()
    ctx.state.emergency(ctx)
    assert ctx.state.__class__ is AlarmOn


def test_alarm_on_emergency_over(ctx: Context) -> None:
    """
    Tests that the emergency over event handler for the AlarmOn state behaves
    as expected.
    """

    def _assert_off(value: bool) -> None:
        """Fails if the passed value is true."""
        assert not value

    ctx.set_alarm_state = _assert_off  # type: ignore

    state = AlarmOn()
    state.emergency_over(ctx)
    assert ctx.state.__class__ is WaitForEmergency


def test_alarm_off_emergency_over(ctx: Context) -> None:
    """
    Tests that the emergency over event handler for the AlarmOff state behaves
    as expected.
    """

    ctx.state = AlarmOff()
    ctx.state.emergency_over(ctx)
    assert ctx.state.__class__ is WaitForEmergency


def test_alarm_off_emergency(ctx: Context) -> None:
    """
    Tests that the emergency event handler for the AlarmOff state behaves as
    expected.
    """

    ctx.state = AlarmOff()
    ctx.state.emergency(ctx)
    assert ctx.state.__class__ is AlarmOff


def test_alarm_off_entry(ctx: Context) -> None:
    """
    Tests that the entry logic for the AlarmOff state behaves as expected.
    """

    def _assert_off(value: bool) -> None:
        """Fails if the passed value is true."""
        assert not value

    def _assert_timeout_one(duration: int) -> None:
        """Fails if the passed value is not '1'."""
        assert duration == 1

    ctx.state = AlarmOff()
    ctx.set_alarm_state = _assert_off  # type: ignore
    ctx.set_timeout = _assert_timeout_one  # type: ignore
    ctx.state.entry(ctx)
    assert ctx.state.__class__ is AlarmOff
