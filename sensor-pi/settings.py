"""
This file contains the class definition for managing user-configured thresholds
and timeouts.
"""

from typing import Self
from dataclasses import dataclass
from pyrebase.pyrebase import Database


@dataclass
class Thresholds:
    """
    Bundles the smoke concentration and temperature thresholds into a class with
    utilities for comparison of measurement values and updating threshold values.
    """

    temperature: float  # In degrees Celsius
    smoke: float  # In parts per million

    def max_out(self) -> None:
        """Maxes out the current thresholds for temperature and smoke."""
        self.temperature = float("inf")
        self.smoke = float("inf")

    def update(self, db: Database) -> None:
        """
        Updates the thresholds using the values stored in the Firebase database.
        """
        self.temperature = float(db.child("thresholds").get("temperature").val().get("temperature"))
        self.smoke = float(db.child("thresholds").get("smoke").val().get("smoke"))

    @classmethod
    def from_db(cls, db: Database) -> Self:
        """
        Creates a threshold object using the values stored in the Firebase database.
        """
        instance = cls(temperature=0, smoke=0)
        instance.update(db)
        return instance

    def temperature_exceeded(self, temperature: float) -> bool:
        """
        Returns true if the temperature exceeds the threshold, false otherwise.
        """
        return temperature > self.temperature

    def smoke_exceeded(self, smoke: float) -> bool:
        """
        Returns true if the smoke concentration exceeds the threshold, false otherwise.
        """
        return smoke < self.smoke
