import machine
import time

buzzer_pin = machine.Pin(15, machine.Pin.OUT)

def beep():
    buzzer_pin.value(1)
    time.sleep(0.1)  
    buzzer_pin.value(0)
    time.sleep(0.1)  

def haptic_alarm():
    while True:

        for _ in range(3):
            beep()
            time.sleep(0.2)  
        time.sleep(1)

        for _ in range(3):
            beep()
            time.sleep(0.5)  

        time.sleep(1)

if __name__ == "__main__":
    haptic_alarm()

