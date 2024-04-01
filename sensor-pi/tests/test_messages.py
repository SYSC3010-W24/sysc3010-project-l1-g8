"""
This file tests that messages can be instantiated correctly using the enum
constructor, and that messages sent using the SystemNode class are properly
received.
"""

import pytest
from messages import Messages, SystemNode
import socket

TEST_UDP_PORT: int = 2993


@pytest.fixture
def node() -> SystemNode:
    """A system node with the test runner's IP address."""
    return SystemNode(socket.gethostbyname(socket.gethostname()), TEST_UDP_PORT)


def test_valid_message() -> None:
    """Test that a valid message is converted into the correct enum member."""

    assert Messages(0) == Messages.EMERGENCY
    assert Messages(1) == Messages.NO_EMERGENCY


def test_invalid_message() -> None:
    """Test that an unexpected numerical value cannot be turned into an enum member."""

    with pytest.raises(ValueError):
        Messages(3)


def test_system_node_constructor() -> None:
    """Test that a SystemNode object can be constructed properly."""

    port = 1000
    ip = "192.168.0.0"
    node = SystemNode(ip, port)

    assert node.port == port
    assert node.ip_addr == ip
    assert node.socket is not None


def test_send_message(node: SystemNode) -> None:
    """Test that a SystemNode object can properly send a UDP message to the recipient it represents."""

    # Create the receiving socket
    channel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    channel.bind((node.ip_addr, node.port))

    node.send_message(Messages.EMERGENCY)
    data, _ = channel.recvfrom(100)

    assert Messages(int.from_bytes(data)) == Messages.EMERGENCY
