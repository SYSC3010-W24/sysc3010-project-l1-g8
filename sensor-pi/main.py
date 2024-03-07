__author__ = "Matteo Golin"

from sense_hat import SenseHat
import pyrebase
import json
import datetime as dt
import netifaces as ni
import socket

FIREBASE_CONFIG: str = "firebase_config.json"
SEND_PORT: int = 2003


def main() -> None:
    """Runs the primary logic of the sensor data fetcher."""

    # Connect using configuration
    with open(FIREBASE_CONFIG, "r") as file:
        config = json.loads(file.read())
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    # Send current IP address for LAN communication between nodes
    ip_addr = ni.ifaddresses("wlan0")[ni.AF_INET][0]["addr"]
    db.child("devices").child("sensor-pi").set(ip_addr)

    # Check for configured thresholds
    temp_threshold = float(db.child("thresholds").get("temperature").val().get("temperature"))  # type: ignore
    db.child("emergency").set(False)

    # Open Sense Hat
    sensehat = SenseHat()

    # Create socket for sending
    channel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        # Fetch data and time stamp
        temperature = sensehat.get_temperature()
        timestamp = dt.datetime.now().isoformat().replace(".", "+")  # Remove . because Firebase doesn't allow it

        # Alert of emergency if threshold is exceeded
        if temperature > temp_threshold:
            db.child("emergency").set(True)
            alarm_ip = db.child("devices").child("alarm").get().val()
            emergency_message = 0
            channel.sendto(emergency_message.to_bytes(), (alarm_ip, SEND_PORT))

        db.child("sensordata").child("temperature").child(timestamp).set(temperature)


if __name__ == "__main__":
    main()
