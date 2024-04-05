"""
Pico_Alarm System: A Raspberry Pi Pico-based alarm system that monitors a
Firebase database for emergency flags. When triggered, it activates an alarm
buzzer and LED indicators.
Author: Javeria Sohail 101197163
"""

import machine
import utime
import urequests
import network

# Adjusted to fit within the limit
firebase_url = (
    "https://fans-38702-default-rtdb." "firebaseio.com//emergency.json"
)

# Auth data for Firebase
auth_data = {
    "email": "javeria1228@gmail.com",
    "password": "firebase123!",
    "returnSecureToken": True,
}

# Making auth request# Adjusted to fit within the limit
auth_url = (
    "https://identitytoolkit.googleapis.com/v1/"
    "accounts:signInWithPassword?"
    "key=AIzaSyDCrm-YWek1mShoftACTezFdzn8PoLSNrY"
)
auth_response = urequests.post(auth_url, json=auth_data)
auth_response_data = auth_response.json()
print(auth_response_data)
auth_response.close()

# Connects buzzer and LEDs to Pico W
buzzer_pin = machine.Pin(1)
buzzer_pwm = machine.PWM(buzzer_pin)
green_led_pin = machine.Pin(5, machine.Pin.OUT)
red_led_pin = machine.Pin(6, machine.Pin.OUT)

# Connects button to Pico W
stop_button = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_UP)

# Frequencies (Hz) for alarm sound
low_freq = 400
high_freq = 1000

# Flags and thresholds
emergency_local = True


def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network")
        wlan.connect("bell511", "javeriamnah@23")
        while not wlan.isconnected():
            print("Waiting for connection...")
            utime.sleep(1)
    print("Network connected:", wlan.ifconfig()[0])


def control_alarm(emergency_flag):
    if emergency_flag and emergency_local:
        buzzer_pwm.duty_u16(32768)  # 50% duty cycle
        for _ in range(100):  # Buzz duration control
            buzzer_pwm.freq(low_freq if _ % 2 == 0 else high_freq)
            utime.sleep(0.1)
            if not stop_button.value():
                break
        buzzer_pwm.duty_u16(0)  # Stop buzzing
    update_led(emergency_flag)


def update_led(emergency_flag):
    if emergency_flag and not emergency_local:
        red_led_pin.high()
        green_led_pin.low()
    elif not emergency_flag:
        red_led_pin.low()
        green_led_pin.high()
    else:  # emergency_flag and emergency_local
        red_led_pin.high()
        green_led_pin.low()


if __name__ == "__main__":
    do_connect()
    green_led_pin.high()  # Green LED on by default
    red_led_pin.low()  # Red LED off by default
    while True:
        try:
            response = urequests.get(firebase_url)
            emergency_flag = response.json()
            response.close()
            control_alarm(emergency_flag)
        except Exception as e:
            print("Error:", e)
        utime.sleep(1)
