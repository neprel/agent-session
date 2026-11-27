"""Single source of public defaults and process-start environment settings."""

from collections.abc import Mapping
from dataclasses import dataclass

from .errors import ExitCode, GitHarnessError
from .validation import component, size_bytes


@dataclass(frozen=True)
class Defaults:
    target: str = "."
    timeout: str = "15s"
    stop_timeout: str = "5s"
    config_dir: str = "."
    verbose: bool = False
    quiet: bool = False
    flag: bool = False
    automatic: None = None
    empty: tuple[()] = ()
    events: tuple[str, ...] = ("created", "modified", "deleted", "moved")
    debounce: str = "10s"
    max_wait: str = "60s"
    check_interval: str = "30s"
    unavailable_timeout: str = "10m"
    session_dir: str = ".harness"
    session_file: str = "agent.json"
    history_max_size: str = "256K"
    max_changes: int = 50
    pending_watcher_batches: int = 1
    pending_timer_ticks: int = 1
    first_tick: str = "next_scheduled"
    history_timezone: str = "UTC"
    history_retention: None = None
    history_compression: None = None
    history_enabled: bool = False
    transport_priority: tuple[str, ...] = ("native", "tmux")
    agent_category: str = "animal"
    agent_suffix_length: int = 4
    agent_suffix_alphabet: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


DEFAULTS = Defaults()


@dataclass(frozen=True)
class Environment:
    session_dir: str
    session_file: str
    history_max_size: int

    @classmethod
    def from_environ(cls, environ: Mapping[str, str]) -> "Environment":
        try:
            return cls(
                component(environ.get("GIT_HARNESS_DIR", DEFAULTS.session_dir)),
                component(environ.get("GIT_HARNESS_FILE", DEFAULTS.session_file)),
                size_bytes(environ.get("GIT_HARNESS_HISTORY_MAX_SIZE", DEFAULTS.history_max_size)),
            )
        except ValueError as exc:
            raise GitHarnessError("invalid_environment", str(exc), ExitCode.INVALID) from exc
