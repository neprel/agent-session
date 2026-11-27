"""Portable history contracts; native formats belong only in harness packages.

Event/provenance structure adapted from xhluca/session-migrate model.py at
fefb719088dc0157b16f071065daa30434a0b980, copyright (c) 2026 xhluca, MIT.
See THIRD_PARTY_NOTICES.md. Changes: canonical/source identities, typed allowed
content, cursor/projection contracts; no raw reasoning/context/opaque payloads.
Storage/serialization/transactions are assigned to AS-008.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

JSONValue: TypeAlias = str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]
SCHEMA_VERSION = 1


class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class EventKind(StrEnum):
    MESSAGE = "message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    COMPACTION = "compaction"


@dataclass(frozen=True)
class Provenance:
    harness: str
    session_id: str
    record_index: int
    source_id: str | None = None
    block_index: int | None = None


@dataclass(frozen=True)
class Image:
    mime_type: str
    data_base64: str


@dataclass(frozen=True)
class MessageContent:
    text: str
    images: tuple[Image, ...] = ()


@dataclass(frozen=True)
class ToolCallContent:
    call_id: str
    name: str
    arguments: dict[str, JSONValue]


@dataclass(frozen=True)
class ToolResultContent:
    call_id: str
    text: str
    images: tuple[Image, ...] = ()
    is_error: bool = False


@dataclass(frozen=True)
class CompactionContent:
    summary: str


@dataclass(frozen=True)
class PortableEvent:
    event_id: str
    provenance: Provenance
    kind: EventKind
    content: MessageContent | ToolCallContent | ToolResultContent | CompactionContent
    role: Role | None = None
    timestamp: str | None = None
    version: int = SCHEMA_VERSION


@dataclass(frozen=True)
class NativeCursor:
    harness: str
    session_id: str
    format_version: str
    record_count: int
    prefix_sha256: str
    byte_offset: int | None = None
    last_record_id: str | None = None
    branch_head: str | None = None


@dataclass(frozen=True)
class LossCounter:
    reason: str
    count: int


@dataclass(frozen=True)
class ProjectionBoundary:
    canonical_revision: int
    event_count: int
    # Includes omitted records, so a readback cannot duplicate imported content.
    last_event_id: str | None
