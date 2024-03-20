import time
import pyrebase
import RPi.GPIO as GPIO
from gpiozero import TonalBuzzer

buzzer_pin = 22  # assuming I use pin 17
GPIO.setmode(GPIO.BOARD)
GPIO.setup(buzzer_pin, GPIO.OUT)
buzzer = TonalBuzzer(buzzer_pin)


def connectFirebase(config: dict):
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    return db

def control_alarm(emergency_flag):
    if emergency_flag:
        # Start buzzing
        buzzer.play('A4')  # Example tone, you can adjust the frequency as needed
        print("Emergency! Haptic alarm buzzing.")
    else:
        # Stop buzzing
        buzzer.stop()
        print("Emergency resolved. Haptic alarm stopped.")

def main() -> None:
    # Firebase configuration
    config = {
        "apiKey": "AIzaSyDCrm-YWek1mShoftACTezFdzn8PoLSNrY",
        "authDomain": "fans-38702.firebaseapp.com",
        "databaseURL": "https://fans-38702-default-rtdb.firebaseio.com/",
        "storageBucket": "fans-38702.appspot.com"
    }

    db = connectFirebase(config)

    # Constantly poll for emergency
    while True:
        emergency_flag = db.child("emergency").get().val()
        print(emergency_flag)
        control_alarm(emergency_flag)
        time.sleep(1)  # Poll DB every second

if __name__ == "__main__":
    main()

