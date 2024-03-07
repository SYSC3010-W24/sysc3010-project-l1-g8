from abc import ABC, abstractmethod
import time
import socket
from messages import Messages

BUFFER_SIZE: int = 100


class Context:
    """Represents the state machine context for the alarm state machine."""

    def __init__(self, ip_addr: str, port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip_addr, port))
        self.state: State = WaitForEmergency()  # Start by waiting for an emergency

    def emergency(self) -> None:
        """Handles the event of an emergency."""
        self.state.emergency(self)

    def emergency_over(self) -> None:
        """Handles the event of an emergency ending."""
        self.state.emergency_over(self)

    def wait_for_message(self) -> Messages:
        """Waits for a message over UDP."""
        data, addr = self.socket.recvfrom(BUFFER_SIZE)
        print(f"Received {Messages(int.from_bytes(data))} from address.")
        return Messages(int.from_bytes(data))

    def start(self) -> None:
        """Starts the FSM."""
        self.state.entry(self)  # Start the first state in motion


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
        print("LEDS on.")
        print("Buzzer on.")
        time.sleep(1)
        context.state = AlarmOff()

    def emergency(self, context: Context) -> None:
        """Handles the event of an emergency."""
        return

    def emergency_over(self, context: Context) -> None:
        """Handles the event of the emergency ending."""
        print("LEDS off.")
        print("Buzzer off.")
        context.state = WaitForEmergency()


class AlarmOff(State):
    """Represents the state where the alarm has its buzzer and LED off."""

    def entry(self, context: Context) -> None:
        print("LEDS off.")
        print("Buzzer off.")
        time.sleep(1)
        context.state = AlarmOn()

    def emergency(self, context: Context) -> None:
        """Handles the event of an emergency."""
        return

    def emergency_over(self, context: Context) -> None:
        """Handles the event of the emergency ending."""
        context.state = WaitForEmergency()
