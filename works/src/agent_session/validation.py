"""Pure public-value validation, without discovery or filesystem mutation."""

import math
import re
from decimal import Decimal
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from croniter import croniter

_DURATION = re.compile(r"(\d+(?:\.\d+)?|\.\d+)(ms|s|m|h)")
_SIZE = re.compile(r"([0-9]+)([KM]?)")


def nonempty(value: str) -> str:
    if not value.strip() or "\0" in value:
        raise ValueError("value must be nonempty and contain no NUL")
    return value


def component(value: str) -> str:
    if not value or value in {".", ".."} or any(c in value for c in "/\\\0"):
        raise ValueError("environment path value must be one nonempty component other than . or ..")
    return value


def _duration(value: str, *, zero: bool = False) -> float:
    match = _DURATION.fullmatch(value)
    if not match:
        raise ValueError("duration must be a positive number with ms, s, m or h")
    seconds = float(
        Decimal(match[1]) * {"ms": Decimal(".001"), "s": 1, "m": 60, "h": 3600}[match[2]]
    )
    if not math.isfinite(seconds) or seconds < 0 or (seconds == 0 and not zero):
        raise ValueError("duration must be finite and positive")
    return seconds


def duration(value: str) -> float:
    return _duration(value)


def unavailable_duration(value: str) -> float | None:
    if value == "never":
        return None
    if value == "0":
        return 0.0
    return _duration(value, zero=True)


def size_bytes(value: str) -> int:
    match = _SIZE.fullmatch(value)
    if not match or int(match[1]) <= 0:
        raise ValueError("history size must be positive integer bytes or have a K/M binary suffix")
    return int(match[1]) * {"": 1, "K": 1024, "M": 1024**2}[match[2]]


def event_types(value: str) -> tuple[str, ...]:
    # Import here to keep defaults usable during environment validation.
    from .defaults import DEFAULTS

    events = value.split(",")
    if any(event not in DEFAULTS.events for event in events):
        raise ValueError("events must be comma-separated created,modified,deleted,moved")
    return tuple(dict.fromkeys(events))


def cron_expression(value: str) -> str:
    if len(value.split()) != 5 or not croniter.is_valid(value):
        raise ValueError("cron must be a valid five-field expression")
    return value


def timezone(value: str) -> str:
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError("timezone must be an available IANA timezone") from exc
    return value


def endpoint_url(value: str) -> str:
    try:
        url = urlsplit(value)
        if (
            url.scheme not in {"http", "https"}
            or not url.hostname
            or url.username is not None
            or url.password is not None
            or url.fragment
        ):
            raise ValueError
        _ = url.port
    except ValueError as exc:
        raise ValueError("endpoint must be an http(s) URL without credentials or fragment") from exc
    return value
