"""
This file tests that the temperature sensor is functioning within the normal
range for room temperature. The Sense Hat must be connected to the Raspberry Pi
before this test is run.
"""

import pytest
from sense_hat import SenseHat

MIN_TEMP: float = 18.0
MAX_TEMP: float = 40.0


@pytest.fixture
def sensors() -> SenseHat:
    """Instantiates a controller for the sensors on board the SenseHat."""
    return SenseHat()


def test_temperature(sensors: SenseHat) -> None:
    """Tests that the temperature sensor reports data within a realistic range for room temperature."""

    assert MIN_TEMP <= sensors.get_temperature() <= MAX_TEMP
