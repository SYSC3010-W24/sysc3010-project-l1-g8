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
RECEIVE_PORT: int = 2003
BUZZER_PIN: int = 22
BUFFER_SIZE: int = 100


def shutdown(sig: int, frame: FrameType) -> None:
    """Kills all child processes before terminating."""
    for child in active_children():
        child.terminate()
        exit(0)


def wait_for_message(channel: socket.socket) -> Messages:
    """Waits for a message over UDP."""
    data, _ = channel.recvfrom(BUFFER_SIZE)
    print(f"Received {Messages(int.from_bytes(data))} from address.")
    return Messages(int.from_bytes(data))


def main() -> None:
    # Suppress warnings
    warnings.simplefilter("ignore")

    # Connect using configuration
    with open(FIREBASE_CONFIG, "r") as file:
        config = json.loads(file.read())
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    # Send current IP address for LAN communication between nodes
    ip_addr = ni.ifaddresses("wlan0")[ni.AF_INET][0]["addr"]
    db.child("devices").child("alarm").set(ip_addr)

    # Set up socket
    channel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    channel.bind((ip_addr, RECEIVE_PORT))

    # Set up alarm system handling thread
    alarm_fsm = AlarmFSM(TonalBuzzer(BUZZER_PIN))
    alarm_system = Process(target=alarm_fsm.start)
    alarm_system.start()

    # In main thread, constantly wait for UDP communication and trigger the correct event
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
