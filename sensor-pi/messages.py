from enum import IntEnum
import socket


class Messages(IntEnum):
    """Describes the possible messages that can be sent over UDP to other nodes."""

    EMERGENCY = 0
    NO_EMERGENCY = 1


class SystemNode:
    """Represents a device/node in the FANS system."""

    def __init__(self, ip_addr: str, port: int) -> None:
        self.ip_addr: str = ip_addr
        self.port: int = port
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM
        )  # Create a new UDP socket

    def send_message(self, message: Messages) -> None:
        """Sends a message to the system node."""
        self.socket.sendto(bytes(message), (self.ip_addr, self.port))
