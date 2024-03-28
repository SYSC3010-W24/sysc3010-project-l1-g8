import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

NO_PPM_VOLTAGE: float = 0.48
MAX_PPM: float = 10000


class SmokeSensor:
    """Represents the Flying-Fish MQ2 smoke sensor connected to the Raspberry Pi SPI interface."""

    def __init__(self, sclk: int, miso: int, mosi: int, chip_select: int) -> None:
        self.spi = busio.SPI(clock=sclk, MISO=miso, MOSI=mosi)
        self.cs = digitalio.DigitalInOut(digitalio.Pin(chip_select))
        self.mcp = MCP.MCP3008(self.spi, self.cs)
        self.channel = AnalogIn(self.mcp, MCP.P0)

    def read_voltage(self) -> float:
        """Reads the voltage output by the smoke sensor."""
        return self.channel.voltage

    def read_ppm(self) -> float:
        """Returns the estimated amount of smoke in the air in PPM."""
        slope = MAX_PPM / (self.mcp.reference_voltage - NO_PPM_VOLTAGE)
        return slope * (self.read_voltage() - NO_PPM_VOLTAGE)
