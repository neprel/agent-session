"""Harness-neutral native-session and runtime ownership values."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from .processes import ProcessIdentity


@dataclass(frozen=True)
class RuntimeOwner:
    agent_id: str
    process: ProcessIdentity
    runtime_id: str


@dataclass(frozen=True)
class NativeSession:
    harness: str
    session_id: str
    launch_directory: Path
    endpoints: Mapping[str, str] = field(default_factory=dict)
    history_path: Path | None = None
    owner: RuntimeOwner | None = None
