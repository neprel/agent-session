"""Common application errors and public exit codes."""

from enum import IntEnum


class ExitCode(IntEnum):
    SUCCESS = 0
    FAILURE = 1
    INVALID = 2
    UNAVAILABLE = 3
    UNSUPPORTED = 4
    UNCERTAIN = 5
    CONFLICT = 6


class AgentSessionError(Exception):
    def __init__(self, code: str, message: str, exit_code: ExitCode = ExitCode.FAILURE):
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code


def not_implemented(command: str) -> int:
    """Fail explicitly until the command's implementation task is complete."""
    raise AgentSessionError(
        "unsupported",
        f"{command} is not implemented in this foundation build",
        ExitCode.UNSUPPORTED,
    )
