from states import Context
import netifaces as ni
import pyrebase
import json

FIREBASE_CONFIG: str = "./firebase_config.json"
RECEIVE_PORT: int = 2003


def main():
    # Connect using configuration
    with open(FIREBASE_CONFIG, "r") as file:
        config = json.loads(file.read())
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    # Send current IP address for LAN communication between nodes
    ip_addr = ni.ifaddresses("wlan0")[ni.AF_INET][0]["addr"]
    db.child("devices").child("alarm").set(ip_addr)

    alarm_fsm = Context(ip_addr, RECEIVE_PORT)
    alarm_fsm.start()


if __name__ == "__main__":
    main()
