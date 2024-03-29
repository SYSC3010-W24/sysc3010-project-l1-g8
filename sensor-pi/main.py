__author__ = "Matteo Golin"

from types import FrameType
from typing import Optional
from threading import Timer
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
from messages import Messages

FIREBASE_CONFIG: str = "firebase_config.json"
SEND_PORT: int = 2003
TIMESTAMP_FORMAT: str = "%Y-%m-%dT%H:%M:%S+%f"

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


def get_latest_timeout(current_timeout: Optional[dt.datetime], db: Database) -> tuple[bool, dt.datetime, int]:
    """
    Returns the latest configured timeout from the database and a boolean which describes whether or not the timeout has
    changed in comparison to the currently active one.
    """
    latest_timeout_timestamp = list(db.child("timeout").order_by_key().limit_to_last(1).get().keys())[0]
    duration = list(db.child("timeout").order_by_key().limit_to_last(1).get().val())[0]
    latest_timeout = dt.datetime.strptime(latest_timeout_timestamp, TIMESTAMP_FORMAT)

    return (latest_timeout == current_timeout, latest_timeout, duration)


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

    # This function is too large to fit in a lambda but needs access to threshold variables
    def refresh_thresholds() -> None:
        """Refresh the thresholds when the timer expires."""
        global temp_threshold, smoke_threshold
        temp_threshold = get_temperature_threshold(db)
        smoke_threshold = get_smoke_threshold(db)

    db.child("emergency").set(False)  # Start with emergency disabled

    # Get the latest timeout configuration to start the timeout
    _, current_timeout, _ = get_latest_timeout(None, db)
    current_timer: Optional[Timer] = None

    # Create socket for sending
    channel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Track if an emergency has been triggered locally. This will allow comparison with the database for turning off
    # emergencies
    local_emergency = False

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
            channel.sendto(Messages.EMERGENCY.value.to_bytes(), (alarm_ip, SEND_PORT))
            local_emergency = True

        # Write measurement to database
        db.child("sensordata").child("temperature").child(timestamp).set(temperature)
        db.child("sensordata").child("smoke").child(timestamp).set(smoke_ppm)

        # Check configuration
        temp_threshold = get_temperature_threshold(db)
        smoke_threshold = get_smoke_threshold(db)

        # Check for timeout
        timeout_changed, current_timeout, duration = get_latest_timeout(current_timeout, db)

        if timeout_changed:

            # If a timer is already running, stop it
            if current_timer is not None:
                current_timer.cancel()

            # Make thresholds so high that nothing will happen
            temp_threshold = float("inf")
            smoke_threshold = float("inf")

            time_expired = (dt.datetime.now() - current_timeout).total_seconds()
            actual_duration = duration - int(time_expired)

            # Make sure timer is not too old to be relevant
            if actual_duration > 0:
                current_timer = Timer(actual_duration, refresh_thresholds)
                current_timer.start()

        # Check for differing emergency status in database (user deactivated)
        if local_emergency and not db.child("emergency").get().val():
            local_emergency = False

            # Notify other nodes that emergency is over
            alarm_ip = db.child("devices").child("alarm").get().val()
            channel.sendto(Messages.NO_EMERGENCY.value.to_bytes(), (alarm_ip, SEND_PORT))


if __name__ == "__main__":
    main()
