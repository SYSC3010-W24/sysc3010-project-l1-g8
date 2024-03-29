import machine
import utime
import urequests as requests
import json
from picozero import LED

# Firebase database URL
firebase_url = "https://fans-38702-default-rtdb.firebaseio.com/"

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
#emergency_flag = False

def get_emergency_flag():
    response = requests.get(firebase_url)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    return None

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
    else:
        # Stop buzzing
        buzzer_pwm.duty_u16(0)
        buzzer_pwm.freq(100)
        update_led()  # Update LED to reflect emergency flag state

def update_led():
    global last_emergency_time, emergency_duration, emergency_threshold
    current_time = utime.ticks_ms()
    
    if emergency_flag:
        # If emergency, turn on red LED and turn off green LED
        red_led.on()
        green_led.off()
    elif stop_button.value() == 0:
        red_led.blink(on_time=0.5, off_time=0.5)
        buzzer_pwm.duty_u16(0)
        buzzer_pwm.freq(100)
        
    else:
        # Otherwise, turn off red LED and turn on green LED
        red_led.off()
        green_led.on()

if __name__ == "__main__":

    # Main loop
    green_led.on() # Turn on green LED by default
    red_led.off()  # Turn off red LED by default
    emergency_flag = get_emergency_flag()

    if emergency_flag is not None:
        print("Emergency flag:", emergency_flag)
    else:
        print("Failed to fetch emergency flag")
    
    while True:
        try:
            if stop_button.value() == 0:
                print("Stop button pressed!")
            control_alarm(emergency_flag)
        except Exception as e:
            print("Error:", e)
        utime.sleep(1)

