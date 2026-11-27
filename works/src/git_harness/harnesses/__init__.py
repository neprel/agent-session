"""Explicit harness registry; the only common module importing concrete adapters."""

from .base import Harness
from .claude.adapter import Adapter as Claude
from .codex.adapter import Adapter as Codex
from .opencode.adapter import Adapter as OpenCode
from .pi.adapter import Adapter as Pi

HARNESSES: dict[str, Harness] = {
    "codex": Codex(),
    "claude": Claude(),
    "opencode": OpenCode(),
    "pi": Pi(),
}


def harness_names() -> tuple[str, ...]:
    return tuple(HARNESSES)
