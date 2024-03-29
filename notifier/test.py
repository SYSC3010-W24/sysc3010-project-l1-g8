from messages import Messages
import socket
import netifaces as ni

# Create the receiving socket
ip_addr = ni.ifaddresses("wlan0")[ni.AF_INET][0]["addr"]
channel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
channel.bind((ip_addr, 2993))
socket.sendto(bytes(Messages.EMERGENCY), (ip_addr, 2003))
