__author__ = "Matteo Golin"

from sense_hat import SenseHat
import pyrebase
import json
import datetime as dt

FIREBASE_CONFIG: str = "firebase_config.json"


def main() -> None:
    """Runs the primary logic of the sensor data fetcher."""

    # Connect using configuration
    with open(FIREBASE_CONFIG, "r") as file:
        config = json.loads(file.read())
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    # Open Sense Hat
    sensehat = SenseHat()

    while True:
        temperature = sensehat.get_temperature()
        timestamp = dt.datetime.now().isoformat().replace(".", "+")  # Remove . because Firebase doesn't allow it
        db.child("sensordata").child("temperature").child(timestamp).set(temperature)


if __name__ == "__main__":
    main()
