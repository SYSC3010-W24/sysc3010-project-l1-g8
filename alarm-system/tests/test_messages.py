import pytest
from messages import Messages


def test_valid_messages() -> None:
    """
    Test that valid numerical values create their corresponding messages.
    """

    assert Messages(0) == Messages.EMERGENCY
    assert Messages(1) == Messages.EMERGENCY_OVER


def test_invalid_message() -> None:
    """
    Tests that numerical values outside the range of encoded messages cannot be
    decoded.
    """

    with pytest.raises(ValueError):
        Messages(2)
