from states import AlarmFSM
import netifaces as ni
import pyrebase
import json
from messages import Messages
from gpiozero import TonalBuzzer

FIREBASE_CONFIG: str = "./firebase_config.json"
RECEIVE_PORT: int = 2003
BUZZER_PIN: int = 22


def main():
    # Connect using configuration
    with open(FIREBASE_CONFIG, "r") as file:
        config = json.loads(file.read())
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    # Send current IP address for LAN communication between nodes
    ip_addr = ni.ifaddresses("wlan0")[ni.AF_INET][0]["addr"]
    db.child("devices").child("alarm").set(ip_addr)

    alarm_fsm = AlarmFSM(ip_addr, RECEIVE_PORT, TonalBuzzer(22))
    alarm_fsm.wait_for_message = lambda : Messages.EMERGENCY

    alarm_fsm.start()


if __name__ == "__main__":
    main()
