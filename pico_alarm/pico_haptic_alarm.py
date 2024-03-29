import machine
import utime
import urequests as requests
import json
from picozero import LED

# Connects buzzer to PicoW
buzzer_pin = machine.Pin(15)
buzzer_pwm = machine.PWM(buzzer_pin)

# Connects LEDs to PicoW
green_led = LED(11)
red_led = LED(12)

# Connects button to PicoW
stop_button = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)

# Frequencies (Hz) for alarm sound 
low_freq = 400
high_freq = 1000

# Amount of time alarm sound plays
last_emergency_time = 0
emergency_duration = 0
emergency_threshold = 30000  # 30 seconds

def connectFirebase(config: dict):
    firebase_url = config["databaseURL"] + "/emergency.json"  # Firebase URL for the emergency flag
    return firebase_url

def control_alarm(emergency_flag):
    global buzzer_pwm
    if emergency_flag:
        # Start buzzing
        update_led()
        for _ in range(200):  # Play the alarm sound for 200 milliseconds
            buzzer_pwm.freq(low_freq)
            buzzer_pwm.duty_u16(32768)  # 50% duty cycle
            utime.sleep_ms(100)
        
            buzzer_pwm.freq(high_freq)
            utime.sleep_ms(100)
        print("Emergency! Haptic alarm buzzing.")
    else:
        # Stop buzzing
        buzzer_pwm.duty_u16(0)
        update_led()
        print("Emergency resolved. Haptic alarm stopped.")

def update_led():
    global last_emergency_time, emergency_duration, emergency_threshold
    current_time = utime.ticks_ms()
    
    if stop_button.value() == 1 and current_time - last_emergency_time > emergency_duration:
        red_led.off()
        green_led.on()
        
    elif stop_button.value() == 1 and current_time - last_emergency_time <= emergency_duration:
        red_led.blink(on_time=0.5, off_time=0.5)  # Blink red LED
        
    else:
        red_led.on()  # Turn on red LED

if __name__ == "__main__":
    # Firebase configuration
    config = {"databaseURL": "https://fans-38702-default-rtdb.firebaseio.com/"}
    firebase_url = connectFirebase(config)

    # Main loop
    green_led.on() # Turn on green led by default
    red_led.off()
    
    while True:
        try:
            response = requests.get(firebase_url)
            if response.status_code == 200:
                emergency_flag = json.loads(response.text)
                print(emergency_flag)
                control_alarm(emergency_flag)
        except Exception as e:
            print("Error:", e)
        update_led()
        utime.sleep(1)  

