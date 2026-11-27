"""Shared delivery outcomes; routing implementation follows in AS-004."""

from dataclasses import dataclass
from enum import StrEnum

from .errors import ExitCode


class DeliveryStatus(StrEnum):
    ACCEPTED = "accepted"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED = "unsupported"
    DEFERRED = "deferred"
    UNCERTAIN = "uncertain"


@dataclass(frozen=True)
class DeliveryResult:
    status: DeliveryStatus
    reason: str
    transport: str | None = None


def delivery_exit(status: DeliveryStatus) -> ExitCode:
    return {
        DeliveryStatus.ACCEPTED: ExitCode.SUCCESS,
        DeliveryStatus.UNAVAILABLE: ExitCode.UNAVAILABLE,
        DeliveryStatus.UNSUPPORTED: ExitCode.UNSUPPORTED,
        DeliveryStatus.DEFERRED: ExitCode.UNAVAILABLE,
        DeliveryStatus.UNCERTAIN: ExitCode.UNCERTAIN,
    }[status]
