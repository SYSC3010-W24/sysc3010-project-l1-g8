import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine


def open_socket(ip):
    """
    Opens a socket on the specified IP address.

    Args:
    - ip (str): The IP address to open the socket on.

    Returns:
    - connection (socket): The opened socket.
    """
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection


def get_pass():
    """
    Prompts the user to enter the WiFi SSID and password.

    Returns:
    - ssid (str): The WiFi SSID entered by the user.
    - password (str): The WiFi password entered by the user.
    """
    while True:
        ssid = input("Enter your WiFi ssid: ")
        password = input("Enter your WiFi password: ")
        return ssid, password


def connect():
    """
    Connects to a WiFi network.

    Returns:
    - ip (str): The IP address of the connected WiFi network.
    """
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    while True:
        ssid, password = get_pass()
        wlan.connect(ssid, password)

        while wlan.isconnected() == False:
            print("Waiting for connection...")
            sleep(1)
        if wlan.isconnected():
            break

    ip = wlan.ifconfig()[0]
    print(f"Connected on {ip}")
    return ip


try:
    ip = connect()
    connection = open_socket(ip)
except KeyboardInterrupt:
    machine.reset()
