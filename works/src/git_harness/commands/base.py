"""All commands implement this small dispatch interface."""

from argparse import ArgumentParser, Namespace
from typing import Protocol, runtime_checkable


@runtime_checkable
class Command(Protocol):
    name: str
    description: str

    def configure(self, parser: ArgumentParser) -> None: ...
    def execute(self, args: Namespace) -> int: ...
