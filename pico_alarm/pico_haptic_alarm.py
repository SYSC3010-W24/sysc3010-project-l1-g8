"""
Pico_Alarm System: A Raspberry Pi Pico-based alarm system that monitors a Firebase database 
for emergency flags. When triggered, it activates an alarm buzzer and LED indicators.
Author: Javeria Sohail 101197163

"""

import machine
import utime
import urequests
import requests
import network
from picozero import LED

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network')
        wlan.connect("bell511", 'javeriamnah@23')
        print('....')
        while not wlan.isconnected():
            print('Waiting for connection...')
            utime.sleep(1)
    print('connected to network', wlan.ifconfig()[0])

# Firebase database URL
firebase_url = 'https://fans-38702-default-rtdb.firebaseio.com//emergency.json'
auth_data = {
    "email": "javeria1228@gmail.com",
    "password": "firebase123!",
    "returnSecureToken": True
}
auth_response = requests.post("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyDCrm-YWek1mShoftACTezFdzn8PoLSNrY", json=auth_data)
auth_response_data = auth_response.json()
print(auth_response_data)
auth_response.close()

# Connects buzzer to PicoW
buzzer_pin = machine.Pin(1)
buzzer_pwm = machine.PWM(buzzer_pin)

# Connects LEDs to PicoW
green_led = LED(5)
red_led = LED(6)

# Connects button to PicoW
stop_button = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_UP)

# Frequencies (Hz) for alarm sound 
low_freq = 400
high_freq = 1000

# Amount of time alarm sound plays
last_emergency_time = 0
emergency_duration = 0
emergency_threshold = 30000  # 30 seconds
emergency_local = True

def control_alarm():
    global buzzer_pwm, emergency_flag, emergency_local
    if emergency_flag and emergency_local:
        # Start buzzing
        update_led()
        while emergency_flag:
            # Buzz for 200 milliseconds
            if emergency_flag:  # Check if emergency flag is still True
                buzzer_pwm.freq(low_freq) 
                buzzer_pwm.duty_u16(32768)  # 50% duty cycle
                utime.sleep(0.02)
            # Switch frequency to high for buzzing
            if emergency_flag:  # Check if emergency flag is still True
                buzzer_pwm.freq(high_freq)
                utime.sleep(0.02)
            if stop_button.value() == 0:
                # Button pressed, indicating awareness of the alarm
                emergency_local = False
                update_led()
                break
    else: # Stop buzzing
        buzzer_pwm.duty_u16(0)
        update_led()  # Update LED to reflect emergency flag state
    
def update_led():
    global emergency_flag, emergency_local, button
    if emergency_flag and not emergency_local:
        # If emergency, turn on red LED and turn off green LED
        red_led.blink(on_time=0.5, off_time=0.5)
        #red_led.on()
        green_led.off()
    if not emergency_flag:
        emergency_local= True
        red_led.off()
        green_led.on()
    elif emergency_flag and emergency_local:
        # If emergency, turn on red LED and turn off green LED
        red_led.on()
        green_led.off()
        

if __name__ == "__main__":
    button = False  # Global variable
    # Establish network connection
    do_connect()
    # Main loop
    green_led.on() # Turn on green LED by default
    red_led.off()  # Turn off red LED by default
    while True:
        try:
            if stop_button.value() == 0:
                button = True
                emergency_local = False
                print("Stop button pressed!")
            while True:    
                response=urequests.get(firebase_url)
                data=response.json()
                response.close()
                print(data)
                emergency_flag = data
                control_alarm()
        except Exception as e:
            print("Error:", e)
        utime.sleep(1)


