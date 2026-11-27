"""Typed harness contract. No argparse, native formats or CLI exit codes."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

from ..delivery import DeliveryResult
from ..history import JSONValue, LossCounter, NativeCursor, PortableEvent, ProjectionBoundary
from ..session import NativeSession, RuntimeOwner


class Capability(StrEnum):
    DISCOVER = "discover"
    PROBE = "probe"
    LAUNCH = "launch"
    SEND = "send"
    READ_HISTORY = "read_history"
    WRITE_HISTORY = "write_history"
    CONFIGURE = "configure"


@dataclass(frozen=True)
class Capabilities:
    supported: frozenset[Capability] = frozenset()
    tested_versions: tuple[str, ...] = ()


@dataclass(frozen=True)
class Unsupported:
    capability: Capability
    reason: str


@dataclass(frozen=True)
class DiscoverRequest:
    launch_directory: Path
    environment: Mapping[str, str]
    session_id: str | None = None
    endpoints: Mapping[str, str] | None = None
    hook_payload: Mapping[str, JSONValue] | None = None


@dataclass(frozen=True)
class DiscoverResult:
    session: NativeSession
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class ProbeRequest:
    session: NativeSession
    timeout: float


class Activity(StrEnum):
    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ProbeResult:
    available: bool | None
    status: Activity
    reason: str
    safe_queue: bool = False


@dataclass(frozen=True)
class LaunchRequest:
    launch_directory: Path
    environment: Mapping[str, str]
    session_id: str | None = None


@dataclass(frozen=True)
class LaunchPlan:
    argv: tuple[str, ...]
    cwd: Path
    environment: Mapping[str, str]


@dataclass(frozen=True)
class SendRequest:
    session: NativeSession
    message: str
    timeout: float
    expected_owner: RuntimeOwner


@dataclass(frozen=True)
class ReadHistoryRequest:
    session: NativeSession
    timeout: float
    cursor: NativeCursor | None = None


@dataclass(frozen=True)
class ReadHistoryResult:
    session: NativeSession
    events: tuple[PortableEvent, ...]
    cursor: NativeCursor
    losses: tuple[LossCounter, ...] = ()
    projection: ProjectionBoundary | None = None


@dataclass(frozen=True)
class WriteHistoryRequest:
    launch_directory: Path
    environment: Mapping[str, str]
    events: tuple[PortableEvent, ...]
    projection: ProjectionBoundary
    timeout: float
    dry_run: bool = False


@dataclass(frozen=True)
class WriteHistoryResult:
    session: NativeSession
    projection: ProjectionBoundary
    verified: bool
    losses: tuple[LossCounter, ...] = ()


@dataclass(frozen=True)
class ConfigureRequest:
    launch_directory: Path
    config_directory: Path
    environment: Mapping[str, str]
    executable: tuple[str, ...]
    dry_run: bool = False


@dataclass(frozen=True)
class ConfigurationChange:
    path: Path
    action: Literal["create", "update", "unchanged"]
    description: str


@dataclass(frozen=True)
class ConfigureResult:
    changes: tuple[ConfigurationChange, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class Option:
    """A declarative native option; the CLI owns parser construction."""

    command: str
    flags: tuple[str, ...]
    help: str
    value_type: Literal["text", "path", "url"] = "text"
    choices: tuple[str, ...] | None = None


@runtime_checkable
class Harness(Protocol):
    name: str
    capabilities: Capabilities

    def discover(self, request: DiscoverRequest) -> DiscoverResult | Unsupported: ...
    def probe(self, request: ProbeRequest) -> ProbeResult | Unsupported: ...
    def launch(self, request: LaunchRequest) -> LaunchPlan | Unsupported: ...
    def send(self, request: SendRequest) -> DeliveryResult | Unsupported: ...
    def read_history(self, request: ReadHistoryRequest) -> ReadHistoryResult | Unsupported: ...
    def write_history(self, request: WriteHistoryRequest) -> WriteHistoryResult | Unsupported: ...
    def configure(self, request: ConfigureRequest) -> ConfigureResult | Unsupported: ...
    def configure_options(self) -> tuple[Option, ...]: ...
