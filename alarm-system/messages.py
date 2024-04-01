from enum import IntEnum


class Messages(IntEnum):
    """
    Represents the types of messages that are possible to received over UDP.
    """

    EMERGENCY = 0
    EMERGENCY_OVER = 1
