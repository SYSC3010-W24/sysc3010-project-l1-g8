__author__ = "Matteo Golin"

from types import FrameType
from sense_hat import SenseHat
import pyrebase
from pyrebase.pyrebase import Database
import json
import datetime as dt
import netifaces as ni
import socket
from multiprocessing import Queue, Process, active_children
from signal import signal, SIGTERM
from smoke_sensor import SmokeSensor
import time

FIREBASE_CONFIG: str = "firebase_config.json"
SEND_PORT: int = 2003

# Smoke detector settings
SCLK: int = 11
MISO: int = 9
MOSI: int = 10
CHIP_SELECT: int = 22


def collect_data(temp: Queue, smoke: Queue) -> None:
    """Process for collecting data from sensors."""

    # Open Sense Hat
    sensehat = SenseHat()

    # Create smoke sensor instance
    smoke_detector = SmokeSensor(sclk=SCLK, miso=MISO, mosi=MOSI, chip_select=CHIP_SELECT)

    while True:
        time.sleep(0.5)  # Don't burn through CPU

        # Fetch temperature data and time stamp
        temperature = sensehat.get_temperature()

        # Fetch smoke status
        smoke_ppm = smoke_detector.read_ppm()

        # Give timestamp for measurements
        timestamp = dt.datetime.now().isoformat().replace(".", "+")  # Remove . because Firebase doesn't allow it
        temp.put((timestamp, temperature))  # Put data on shared queue
        smoke.put((timestamp, smoke_ppm))


def get_temperature_threshold(db: Database) -> float:
    """Gets the configured temperature threshold from the Firebase database."""
    return float(db.child("thresholds").get("temperature").val().get("temperature"))  # type: ignore


def get_smoke_threshold(db: Database) -> float:
    """Gets the configured smoke PPM threshold from the Firebase database."""
    return float(db.child("thresholds").get("smoke").val().get("smoke"))  # type: ignore


def shutdown(sig: int, frame: FrameType) -> None:
    """Kills all child processes before terminating."""
    for child in active_children():
        child.terminate()
        exit(0)


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
    temp_threshold = get_temperature_threshold(db)
    smoke_threshold = get_smoke_threshold(db)
    db.child("emergency").set(False)  # Start with emergency disabled

    # Create socket for sending
    channel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Handle shutdown signal
    signal(SIGTERM, shutdown)  # type: ignore

    # Start data collection
    temp = Queue()
    smoke = Queue()

    data_collection = Process(target=collect_data, args=(temp, smoke))
    data_collection.start()

    while True:
        # Get latest measurement
        timestamp, temperature = temp.get()
        timestamp, smoke_ppm = smoke.get()

        # Alert of emergency if threshold is exceeded or if there is smoke
        if temperature > temp_threshold or smoke_ppm > smoke_threshold:
            db.child("emergency").set(True)
            alarm_ip = db.child("devices").child("alarm").get().val()
            emergency_message = 0
            channel.sendto(emergency_message.to_bytes(), (alarm_ip, SEND_PORT))

        # Write measurement to database
        db.child("sensordata").child("temperature").child(timestamp).set(temperature)
        db.child("sensordata").child("smoke").child(timestamp).set(smoke_ppm)

        # Check configuration
        temp_threshold = get_temperature_threshold(db)
        smoke_threshold = get_smoke_threshold(db)


if __name__ == "__main__":
    main()
