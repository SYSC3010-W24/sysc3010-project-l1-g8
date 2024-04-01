"""
This is the main file of the alarm system which controls its behaviour. It
instantiates the alarm system finite state machine and starts it in motion,
while another thread waits for UDP events sent over the local network.
"""

from states import AlarmFSM
import netifaces as ni
import pyrebase
import json
import socket
from messages import Messages
from gpiozero import TonalBuzzer
from multiprocessing import Process, active_children
from types import FrameType
import warnings

FIREBASE_CONFIG: str = "./firebase_config.json"
UDP_RECEIVE_PORT: int = 2003
BUZZER_PIN: int = 22
UDP_BUFFER_SIZE: int = 100


def shutdown(sig: int, frame: FrameType) -> None:
    """Kills all child processes before terminating."""
    for child in active_children():
        child.terminate()
        exit(0)


def wait_for_message(channel: socket.socket) -> Messages:
    """Waits for a message over UDP."""
    data, _ = channel.recvfrom(UDP_BUFFER_SIZE)
    return Messages(int.from_bytes(data))


def main() -> None:
    # Suppress warnings
    warnings.simplefilter("ignore")

    # Connect using configuration
    with open(FIREBASE_CONFIG, "r") as file:
        config = json.loads(file.read())
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    # Store current IP address for LAN communication between nodes
    ip_addr = ni.ifaddresses("wlan0")[ni.AF_INET][0]["addr"]
    db.child("devices").child("alarm").set(ip_addr)

    # Set up socket for UDP
    channel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    channel.bind((ip_addr, UDP_RECEIVE_PORT))

    # Set up thread for the state machine
    alarm_fsm = AlarmFSM(TonalBuzzer(BUZZER_PIN))
    alarm_system = Process(target=alarm_fsm.start)
    alarm_system.start()

    # In main thread, constantly wait for UDP communication and trigger the
    # correct event upon receipt
    while True:
        msg = wait_for_message(channel)

        # Forward the received message as an FSM event
        match msg:
            case Messages.EMERGENCY:
                alarm_fsm.emergency()
            case Messages.EMERGENCY_OVER:
                alarm_fsm.emergency_over()


if __name__ == "__main__":
    main()
