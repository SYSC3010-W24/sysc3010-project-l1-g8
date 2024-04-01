"""
This file contains the definitions of the messages that can be sent over UDP,
as well as a helper class for sending UDP messages to other system nodes.
"""

from typing import Self
from enum import IntEnum
import socket
from pyrebase.pyrebase import Database

# Default port for all devices to listen for messages
UDP_SEND_PORT: int = 2003


class Messages(IntEnum):
    """
    Describes the possible messages that can be sent over UDP to other nodes.
    """

    EMERGENCY = 0
    NO_EMERGENCY = 1


class SystemNode:
    """Represents a device/node in the FANS system."""

    def __init__(self, ip_addr: str, port: int = UDP_SEND_PORT) -> None:
        self.ip_addr: str = ip_addr
        self.port: int = port
        # Socket configured for sending UDP messages
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_message(self, message: Messages) -> None:
        """Sends a message to the system node."""
        self.socket.sendto(bytes(message), (self.ip_addr, self.port))

    @classmethod
    def from_db_device(cls, device_name: str, db: Database) -> Self:
        """Creates a system node from a device in the Firebase DB."""
        return cls(ip_addr=db.child("devices").child(device_name).get().val())
