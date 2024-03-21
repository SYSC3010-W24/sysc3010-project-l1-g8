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


def insecure_access(config: dict[str, str]) -> None:
    """Ensures that insecure access to the database is not possible."""
    config["apiKey"] = "obviously wrong"
    with pytest.raises(Exception):
        firebase = pyrebase.initialize_app(config)
        db = firebase.database()
