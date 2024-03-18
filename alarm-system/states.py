from __future__ import annotations
from abc import ABC, abstractmethod
import time
import socket
from messages import Messages
from typing import Protocol
from gpiozero import TonalBuzzer
from gpiozero.tones import Tone

BUFFER_SIZE: int = 100
B_FLAT: Tone = Tone.from_frequency(466.164)


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

    def set_alarm_state(self, state: bool) -> None:
        """
        Turns on or off the alarm buzzer.
        Args:
            state: True for on, False for off.
        """
        ...


class AlarmFSM:
    """Represents the state machine context for the alarm state machine."""

    def __init__(self, ip_addr: str, port: int, buzzer: TonalBuzzer) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip_addr, port))
        self.buzzer: TonalBuzzer = buzzer
        self.__state: State = WaitForEmergency()  # Start by waiting for an emergency

    @property
    def state(self) -> State:
        """Gets the state attribute."""
        return self.__state

    @state.setter
    def state(self, new_state: State) -> None:
        """Sets the state attribute after exiting the previous state, and then enters the next state."""
        self.__state.exit(self)  # type: ignore
        self.__state = new_state
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

    def set_alarm_state(self, state: bool) -> None:
        """
        Turns on or off the alarm buzzer in sync with the LEDS.
        Args:
            state: True for on, False for off.
        """
        if state:
            self.buzzer.play(B_FLAT)
        else:
            self.buzzer.stop()


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
        return

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
        context.state = AlarmOn()

    def emergency_over(self, context: Context) -> None:
        """Handles the event of the emergency ending. In this case, do nothing except wait again."""
        context.state = WaitForEmergency()


class AlarmOn(State):
    """Represents the state where the alarm has its buzzer and LED on."""

    def entry(self, context: Context) -> None:
        context.set_alarm_state(True)
        time.sleep(1)
        context.state = AlarmOff()

    def emergency(self, context: Context) -> None:
        """Handles the event of an emergency."""
        return

    def emergency_over(self, context: Context) -> None:
        """Handles the event of the emergency ending."""
        context.set_alarm_state(False)
        context.state = WaitForEmergency()


class AlarmOff(State):
    """Represents the state where the alarm has its buzzer and LED off."""

    def entry(self, context: Context) -> None:
        context.set_alarm_state(False)
        time.sleep(1)
        context.state = AlarmOn()

    def emergency(self, context: Context) -> None:
        """Handles the event of an emergency."""
        return

    def emergency_over(self, context: Context) -> None:
        """Handles the event of the emergency ending."""
        context.state = WaitForEmergency()
