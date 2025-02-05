"""
This file tests that trying to access Firebase without the correct API key
results in an error.
"""

import pyrebase
import pytest
import json

FIREBASE_CONFIG: str = "firebase_config.json"


@pytest.fixture
def config() -> dict[str, str]:
    """Firebase configuration file."""
    with open(FIREBASE_CONFIG, "r") as file:
        config = json.loads(file.read())
    return config


def test_insecure_access(config: dict[str, str]) -> None:
    """Ensures that insecure access to the database is not possible."""
    config["apiKey"] = "obviously wrong"
    with pytest.raises(Exception):
        firebase = pyrebase.initialize_app(config)
        _ = firebase.database()
