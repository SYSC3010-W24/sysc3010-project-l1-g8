from gpiozero import TonalBuzzer
from gpiozero.tones import Tone
import pytest
import time

# The GPIO pin on the Pi that the buzzer will need to be connected to for this test
GPIO_PIN: int = 22

# The amount of time the buzzer will be on or off for during toggling
INTERVAL: float = 0.5


@pytest.fixture
def note() -> Tone:
    """The note for the buzzer to play."""
    return Tone.from_frequency(466.164)


@pytest.fixture
def buzzer() -> TonalBuzzer:
    """The note for the buzzer to play."""
    return TonalBuzzer(GPIO_PIN)


def test_buzzer_toggle(note: Tone, buzzer: TonalBuzzer) -> None:
    """Tests that the buzzer can be toggled on and off."""

    for _ in range(3):
        buzzer.play(note)
        time.sleep(INTERVAL)
        buzzer.stop()
        time.sleep(INTERVAL)
