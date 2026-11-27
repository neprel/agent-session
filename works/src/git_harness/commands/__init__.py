"""Explicit command registry; dispatch depends only on the Command protocol."""

from .base import Command
from .check import CheckCommand
from .config import ConfigCommand
from .init import InitCommand
from .message import MessageCommand
from .prime import PrimeCommand
from .run import RunCommand
from .stop import StopCommand
from .sync import SyncCommand
from .timer import TimerCommand
from .watcher import WatcherCommand

COMMANDS: dict[str, Command] = {
    "config": ConfigCommand(),
    "prime": PrimeCommand(),
    "init": InitCommand(),
    "check": CheckCommand(),
    "run": RunCommand(),
    "stop": StopCommand(),
    "sync": SyncCommand(),
    "message": MessageCommand(),
    "watcher": WatcherCommand(),
    "timer": TimerCommand(),
}
