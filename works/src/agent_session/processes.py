"""Shared process identity contract; worker management follows in AS-005."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessIdentity:
    pid: int
    created_at: float
