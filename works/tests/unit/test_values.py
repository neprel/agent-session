import math

import pytest

from agent_session.cli import main
from agent_session.defaults import DEFAULTS, Environment
from agent_session.delivery import DeliveryStatus, delivery_exit
from agent_session.errors import ExitCode
from agent_session.validation import (
    component,
    cron_expression,
    duration,
    endpoint_url,
    event_types,
    nonempty,
    size_bytes,
    timezone,
    unavailable_duration,
)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "value,seconds", [("1ms", 0.001), (".5s", 0.5), ("2.25m", 135), ("1h", 3600)]
)
def test_duration_units(value, seconds):
    assert duration(value) == seconds


@pytest.mark.parametrize(
    "value", ["-1s", "0s", "1", "never", "NaNs", "infs", "1e3s", "1 s", "", "9" * 400 + "h"]
)
def test_duration_rejects_invalid_or_unbounded(value):
    with pytest.raises(ValueError):
        duration(value)


def test_unavailable_timeout_special_values():
    assert unavailable_duration("never") is None
    assert unavailable_duration("0") == 0
    assert unavailable_duration("0ms") == 0
    assert unavailable_duration("1m") == 60
    assert math.isfinite(duration("0.001s"))


@pytest.mark.parametrize("value,expected", [("12", 12), ("256K", 262144), ("2M", 2097152)])
def test_size_units(value, expected):
    assert size_bytes(value) == expected


@pytest.mark.parametrize("value", ["", "0", "0K", "-1", "1.5K", "1G", "1k", "never"])
def test_size_invalid(value):
    with pytest.raises(ValueError):
        size_bytes(value)


def test_environment_defaults_and_fixed_policy():
    assert Environment.from_environ({}) == Environment(".session", "agent.json", 262144)
    assert (
        DEFAULTS.max_changes,
        DEFAULTS.pending_watcher_batches,
        DEFAULTS.pending_timer_ticks,
    ) == (50, 1, 1)
    assert DEFAULTS.first_tick == "next_scheduled"
    assert DEFAULTS.history_timezone == "UTC" and DEFAULTS.history_retention is None
    assert DEFAULTS.history_compression is None and not DEFAULTS.history_enabled
    assert DEFAULTS.transport_priority == ("native", "tmux")
    assert DEFAULTS.agent_category == "animal" and DEFAULTS.agent_suffix_length == 4
    assert DEFAULTS.agent_suffix_alphabet.isalnum()


@pytest.mark.parametrize(
    "key,value,field,expected",
    [
        ("AGENT_SESSION_DIR", "custom", "session_dir", "custom"),
        ("AGENT_SESSION_FILE", "custom.json", "session_file", "custom.json"),
        ("AGENT_SESSION_HISTORY_MAX_SIZE", "2M", "history_max_size", 2097152),
    ],
)
def test_environment_overrides_are_snapshots(key, value, field, expected, monkeypatch):
    env = {key: value}
    snapshot = Environment.from_environ(env)
    env[key] = ""
    assert getattr(snapshot, field) == expected
    monkeypatch.setenv(key, value)
    assert main(["check"]) == ExitCode.UNSUPPORTED


@pytest.mark.parametrize(
    "key", ["AGENT_SESSION_DIR", "AGENT_SESSION_FILE", "AGENT_SESSION_HISTORY_MAX_SIZE"]
)
@pytest.mark.parametrize("value", ["", ".", "..", "a/b", "a\\b", "\0"])
def test_environment_empty_and_invalid_fail_before_execution(key, value, monkeypatch, capsys):
    # NUL cannot be put into an OS environment; still validate direct input.
    if value == "\0":
        from agent_session.errors import AgentSessionError

        with pytest.raises(AgentSessionError):
            Environment.from_environ({key: value})
    else:
        monkeypatch.setenv(key, value)
        assert main(["check"]) == 2
        result = capsys.readouterr()
        assert result.out == "" and "invalid_environment" in result.err


@pytest.mark.parametrize("value", ["", " ", "\0"])
def test_nonempty(value):
    with pytest.raises(ValueError):
        nonempty(value)


def test_text_and_components_are_data():
    assert nonempty("hello\n世界; $(false)") == "hello\n世界; $(false)"
    assert component("custom.json") == "custom.json"
    assert event_types("moved,created,moved") == ("moved", "created")
    with pytest.raises(ValueError):
        event_types("modified,")


@pytest.mark.parametrize(
    "value",
    [
        "https://host:bad",
        "http://host:99999",
        "http://user:secret@host",
        "http://host/#secret",
        "noscheme",
        "ftp://host",
        "http://",
    ],
)
def test_url_rejects_malformed_or_credential_bearing_endpoints(value):
    with pytest.raises(ValueError):
        endpoint_url(value)


def test_valid_url_cron_and_zone():
    assert endpoint_url("http://127.0.0.1:4096") == "http://127.0.0.1:4096"
    assert endpoint_url("https://localhost/base") == "https://localhost/base"
    assert cron_expression("*/5 * * * *") == "*/5 * * * *"
    assert timezone("UTC") == "UTC"


@pytest.mark.parametrize(
    "status,expected",
    [
        (DeliveryStatus.ACCEPTED, 0),
        (DeliveryStatus.UNAVAILABLE, 3),
        (DeliveryStatus.UNSUPPORTED, 4),
        (DeliveryStatus.DEFERRED, 3),
        (DeliveryStatus.UNCERTAIN, 5),
    ],
)
def test_delivery_results_preserve_uncertain_and_deferred_outcomes(status, expected):
    assert delivery_exit(status) == expected


def test_public_exit_codes():
    assert list(ExitCode) == [0, 1, 2, 3, 4, 5, 6]
