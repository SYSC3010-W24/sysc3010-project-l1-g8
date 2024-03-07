import time
import pyrebase
import RPi.GPIO as GPIO

# Firebase configuration
config = { 
  "apiKey": "AIzaSyDCrm-YWek1mShoftACTezFdzn8PoLSNrY",
  "authDomain": "fans-38702.firebaseapp.com",
  "databaseURL": "https://fans-38702-default-rtdb.firebaseio.com/",
  "storageBucket": "fans-38702.appspot.com"
}


firebase = pyrebase.initialize_app(config)
db = firebase.database()

buzzer_pin = 17  # assuming I use pin 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer_pin, GPIO.OUT)

def control_alarm():
    while True:
        emergency_flag = db.child("emergency").get().val()
        print(emergency_flag)
        if emergency_flag:
            # Start buzzing
            GPIO.output(buzzer_pin, GPIO.HIGH)
            print("Emergency! Haptic alarm buzzing.")

        else:
            # Stop buzzing
            GPIO.output(buzzer_pin, GPIO.LOW)
            print("Emergency resolved. Haptic alarm stopped.")

        time.sleep(1)

if __name__ == "__main__":
    try:
        control_alarm()

    except KeyboardInterrupt:
        GPIO.cleanup()
