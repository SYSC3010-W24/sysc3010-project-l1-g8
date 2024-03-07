import pyrebase
import json
import time


def is_emergency(db) -> bool:
    """Checks if there is an emergency active in the Firebase database."""
    return db.child("emergency").get().val()


def main() -> None:

    # Connect to Firebase
    CREDENTIALS: str = "./firebase_config.json"

    # Initialize DB connection
    with open(CREDENTIALS, "r") as file:
        config = json.load(file)
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    # Constantly poll for emergency
    while True:

        while is_emergency(db):
            print("BUZZ!")  # Mock actuator
            time.sleep(1)

        time.sleep(1)  # Poll DB every second


if __name__ == "__main__":
    main()
