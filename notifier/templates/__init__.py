"""
This file contains the Template class for text template management.
It supports template creation from files, dynamic content replacement,
and resetting content to its original state.
"""

from typing import Self


class Template:

    def __init__(self, content: str) -> None:
        self.content: str = content
        self.custom_content: str = content

    @classmethod
    def from_file(cls, file_path: str) -> Self:
        """
        Creates a new template from the contents of a file containing
        plain-text.
        """
        with open(file_path, "r") as file:
            return cls(file.read())

    def customize(self, fields: dict[str, str]) -> None:
        """
        Updates the contents of the template by finding the fields (keys) and
        replacing them with the values specified.
        """
        for item in fields:
            self.custom_content = self.custom_content.replace(
                item, fields[item]
            )

    def reset(self) -> None:
        """Resets the contents of this template to the original version."""
        self.custom_content = self.content

    def __str__(self) -> str:
        """Prints the customized content of this"""
        return self.custom_content
