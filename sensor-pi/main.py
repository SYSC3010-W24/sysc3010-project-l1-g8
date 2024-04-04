"""
Contains the main code for controlling the sensor data collection system node
of FANS. Sensor data is constantly read in a separate thread while the main
thread periodically uploads the recorded data to Firebase, reads user settings,
checks for data above thresholds and sends UDP messages to other system nodes
when an emergency has been activated or deactivated.
"""

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
from multiprocessing import Queue, Process, active_children
from signal import signal, SIGTERM
from smoke_sensor import SmokeSensor
import time
from messages import Messages, SystemNode
from settings import Thresholds

FIREBASE_CONFIG: str = "firebase_config.json"
TIMESTAMP_FORMAT: str = "%Y-%m-%dT%H:%M:%S+%f"
DEVICE_NAMES: list[str] = ["alarm", "notifier"]

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
    smoke_detector = SmokeSensor(
        sclk=SCLK,
        miso=MISO,
        mosi=MOSI,
        chip_select=CHIP_SELECT,
    )

    while True:
        time.sleep(0.5)  # Don't burn through CPU

        # Fetch temperature data and time stamp
        temperature = sensehat.get_temperature()

        # Fetch smoke status
        smoke_ppm = smoke_detector.read_ppm()

        # Give timestamp for measurements
        # Remove . because Firebase doesn't allow it
        timestamp = dt.datetime.now().isoformat().replace(".", "+")
        temp.put((timestamp, temperature))  # Put data on shared queue
        smoke.put((timestamp, smoke_ppm))


def get_latest_timeout(
    current_timeout: Optional[dt.datetime],
    db: Database,
) -> tuple[bool, dt.datetime, int]:
    """
    Returns the latest configured timeout from the database and a boolean which
    describes whether or not the timeout has changed in comparison to the
    currently active one.
    """
    data = db.child("timeout").order_by_key().limit_to_last(1).get().val()
    latest_timeout_timestamp = list(data.keys())[0]  # type: ignore
    duration = list(data.values())[0]  # type: ignore
    latest_timeout = dt.datetime.strptime(
        latest_timeout_timestamp,
        TIMESTAMP_FORMAT,
    )

    if current_timeout is not None:
        timeout_changed = latest_timeout > current_timeout
    else:
        timeout_changed = True

    return (timeout_changed, latest_timeout, duration)


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
    thresholds = Thresholds.from_db(db)

    db.child("emergency").set(False)  # Start with emergency disabled

    # Get the latest timeout configuration to start the timeout
    _, current_timeout, _ = get_latest_timeout(None, db)
    current_timer: Timer = Timer(1, thresholds.update)

    # Get IP addresses of other device nodes
    devices = [SystemNode.from_db_device(name, db) for name in DEVICE_NAMES]

    # Track if an emergency has been triggered locally. This will allow
    # comparison with the database for turning off emergencies
    local_emergency = False

    # Handle shutdown signal
    signal(SIGTERM, shutdown)  # type: ignore

    # Start data collection with message queues
    temp = Queue()
    smoke = Queue()
    data_collection = Process(target=collect_data, args=(temp, smoke))
    data_collection.start()

    while True:
        # Get latest measurement
        timestamp, temperature = temp.get()
        timestamp, smoke_ppm = smoke.get()

        # Alert of emergency if threshold is exceeded or if there is smoke
        if thresholds.temperature_exceeded(
            temperature
        ) or thresholds.smoke_exceeded(smoke_ppm):
            db.child("emergency").set(True)
            local_emergency = True
            for device in devices:
                device.send_message(Messages.EMERGENCY)

        # Write measurement to database
        db.child("sensordata").child("temperature").child(timestamp).set(
            temperature
        )
        db.child("sensordata").child("smoke").child(timestamp).set(smoke_ppm)

        # Update configuration unless there's a timeout
        if not current_timer.is_alive():
            thresholds.update(db)

        # Check for timeout
        timeout_changed, current_timeout, duration = get_latest_timeout(
            current_timeout, db
        )

        if timeout_changed:
            # If a timer is already running, stop it
            if current_timer.is_alive():
                current_timer.cancel()

            time_expired = dt.datetime.now() - current_timeout
            actual_duration = duration - int(time_expired.total_seconds())

            # Make sure timer is not too old to be relevant
            if actual_duration > 0:
                current_timer = Timer(
                    actual_duration,
                    lambda: thresholds.update(db),
                )

                # Make thresholds so high that nothing will happen
                thresholds.max_out()
                current_timer.start()  # Start timer

        # Check for differing emergency status in database (user deactivated)
        if local_emergency and not db.child("emergency").get().val():
            local_emergency = False

            # Notify other nodes that emergency is over
            for device in devices:
                device.send_message(Messages.NO_EMERGENCY)


if __name__ == "__main__":
    main()
