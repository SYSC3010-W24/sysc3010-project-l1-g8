from __future__ import annotations
from abc import ABC, abstractmethod
import time
import socket
from messages import Messages
from typing import Protocol

BUFFER_SIZE: int = 100


class Context(Protocol):
    """Defines the interface for the context required for the AlarmFSM."""

    socket: socket.socket
    state: State

    def emergency(self) -> None:
        """Handles the event of an emergency."""
        ...

    def emergency_over(self) -> None:
        """Handles the event of an emergency ending."""
        ...

    def wait_for_message(self) -> Messages:
        """Waits for a message over UDP."""
        ...

    def start(self) -> None:
        """Starts the FSM."""
        ...

    def set_led_state(self, state: bool) -> None:
        """
        Turns on or off the LEDs.
        Args:
            state: True for on, False for off.
        """
        ...

    def set_alarm_state(self, state: bool) -> None:
        """
        Turns on or off the alarm buzzer.
        Args:
            state: True for on, False for off.
        """
        ...


class AlarmFSM:
    """Represents the state machine context for the alarm state machine."""

    def __init__(self, ip_addr: str, port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip_addr, port))
        self.__state: State = WaitForEmergency()  # Start by waiting for an emergency

    @property
    def state(self) -> State:
        """Gets the state attribute."""
        return self.__state

    @state.setter
    def set_state(self, new_state: State) -> None:
        """Sets the state attribute."""
        self.__state = new_state

        if hasattr(new_state, "entry"):
            self.__state.entry(self)  # type: ignore

    def emergency(self) -> None:
        """Handles the event of an emergency."""
        self.__state.emergency(self)  # type: ignore

    def emergency_over(self) -> None:
        """Handles the event of an emergency ending."""
        self.__state.emergency_over(self)  # type: ignore

    def wait_for_message(self) -> Messages:
        """Waits for a message over UDP."""
        data, _ = self.socket.recvfrom(BUFFER_SIZE)
        print(f"Received {Messages(int.from_bytes(data))} from address.")
        return Messages(int.from_bytes(data))

    def start(self) -> None:
        """Starts the FSM."""
        self.__state.entry(self)  # type: ignore

    def set_led_state(self, state: bool) -> None:
        """
        Turns on or off the LEDs.
        Args:
            state: True for on, False for off.
        """
        if state:
            print("LEDs ON!")
        else:
            print("LEDs OFF!")

    def set_alarm_state(self, state: bool) -> None:
        """
        Turns on or off the alarm buzzer.
        Args:
            state: True for on, False for off.
        """
        if state:
            print("Alarm ON!")
        else:
            print("Alarm OFF!")


class State(ABC):
    """Represents the interface that all states must implement to handle incoming events."""

    @abstractmethod
    def emergency(self, context: Context) -> None:
        """Handles the event of an emergency."""

    @abstractmethod
    def emergency_over(self, context: Context) -> None:
        """Handles the event of an emergency ending."""

    def entry(self, context: Context) -> None:
        """Performs the entry activity of the state."""

    def exit(self, context: Context) -> None:
        """Performs the exit activity of the state."""
        return


class WaitForEmergency(State):
    """Represents the state where the alarm is waiting for an emergency."""

    def entry(self, context: Context) -> None:
        """Performs the entry activity for this state."""
        msg = context.wait_for_message()

        # Handle the received message
        match msg:
            case Messages.EMERGENCY:
                self.emergency(context)
            case Messages.EMERGENCY_OVER:
                self.emergency_over(context)

    def emergency(self, context: Context) -> None:
        """Handles the event of an emergency."""
        context.state = AlarmActive()

    def emergency_over(self, context: Context) -> None:
        """Handles the event of the emergency ending. In this case, do nothing."""
        return


class AlarmActive(State):
    """Represents the superstate where the alarm is active."""

    def emergency(self, context: Context) -> None:
        """Handles the event of an emergency."""
        context.state = AlarmOn()

    def emergency_over(self, context: Context) -> None:
        """Handles the event of the emergency ending."""
        context.state = WaitForEmergency()


class AlarmOn(State):
    """Represents the state where the alarm has its buzzer and LED on."""

    def entry(self, context: Context) -> None:
        context.set_led_state(True)
        context.set_alarm_state(True)
        time.sleep(1)
        context.state = AlarmOff()

    def emergency(self, context: Context) -> None:
        """Handles the event of an emergency."""
        return

    def emergency_over(self, context: Context) -> None:
        """Handles the event of the emergency ending."""
        context.set_led_state(False)
        context.set_alarm_state(False)
        context.state = WaitForEmergency()


class AlarmOff(State):
    """Represents the state where the alarm has its buzzer and LED off."""

    def entry(self, context: Context) -> None:
        context.set_alarm_state(False)
        context.set_led_state(False)
        time.sleep(1)
        context.state = AlarmOn()

    def emergency(self, context: Context) -> None:
        """Handles the event of an emergency."""
        return

    def emergency_over(self, context: Context) -> None:
        """Handles the event of the emergency ending."""
        context.state = WaitForEmergency()
