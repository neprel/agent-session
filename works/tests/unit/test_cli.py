import argparse

import pytest

from agent_session import __version__
from agent_session.cli import build_parser, main
from agent_session.commands import COMMANDS
from agent_session.commands.base import Command
from agent_session.defaults import DEFAULTS
from agent_session.errors import AgentSessionError, ExitCode

pytestmark = pytest.mark.unit

MINIMAL = {
    "config": [],
    "prime": [],
    "init": [],
    "check": [],
    "run": [],
    "stop": [],
    "sync": [],
    "message": [],
    "watcher": ["--path", "tasks/**/*.md"],
    "timer": ["--every", "1m"],
}


@pytest.mark.parametrize("name,options", MINIMAL.items())
def test_every_command_help_and_explicit_unsupported(name, options, capsys):
    assert isinstance(COMMANDS[name], Command)
    assert main([name, "--help"]) == 0
    help_text = capsys.readouterr().out
    assert f"agent-session {name}" in help_text
    assert "--verbose" in help_text and "--quiet" in help_text
    if name not in {"config", "prime"}:
        assert "--target" in help_text and "(default: .)" in help_text
        assert ("5s" if name == "stop" else "15s") in help_text
    assert "--hook" not in help_text
    assert main([name, *options]) == ExitCode.UNSUPPORTED
    result = capsys.readouterr()
    assert result.out == ""
    assert f"unsupported: {name} is not implemented" in result.err


def test_root_help_version_and_no_command(capsys):
    assert main([]) == 0
    assert "watcher" in capsys.readouterr().out
    assert main(["--help"]) == 0
    assert "timer" in capsys.readouterr().out
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == f"agent-session {__version__}"


@pytest.mark.parametrize("name,options", MINIMAL.items())
def test_shared_options_omitted_and_explicit(name, options):
    parser = build_parser()
    default = parser.parse_args([name, *options])
    assert default.verbose is DEFAULTS.verbose and default.quiet is DEFAULTS.quiet
    explicit = parser.parse_args([name, *options, "-v"])
    assert explicit.verbose and not explicit.quiet
    assert parser.parse_args([name, *options, "-q"]).quiet
    if name not in {"config", "prime"}:
        assert default.target == DEFAULTS.target
        assert default.timeout == (5 if name == "stop" else 15)
        explicit = parser.parse_args(
            [name, *options, "--target", "a b/agent.json", "--timeout", "3ms"]
        )
        assert explicit.target == "a b/agent.json" and explicit.timeout == 0.003


@pytest.mark.parametrize("name,options", MINIMAL.items())
@pytest.mark.parametrize("invalid", [["-v", "-q"], ["--unknown"], ["--from", "."]])
def test_every_command_rejects_conflicts_unknown_options_and_sender_scope(name, options, invalid):
    if name == "message" and invalid[0] == "--from":
        assert build_parser().parse_args([name, *invalid]).sender == "."
    else:
        assert main([name, *options, *invalid]) == 2


@pytest.mark.parametrize("name", ["config", "prime"])
@pytest.mark.parametrize("option", [["--target", "."], ["--timeout", "2s"]])
def test_non_target_commands_reject_target_options(name, option):
    assert main([name, *option]) == 2


def test_config_defaults_and_repeated_selection():
    parser = build_parser()
    default = parser.parse_args(["config"])
    assert default.config_dir == DEFAULTS.config_dir
    assert default.harness == ("codex", "claude", "opencode", "pi")
    assert not default.dry_run
    explicit = parser.parse_args(
        ["config", "--harness", "pi", "--harness", "codex", "--config-dir", "custom", "--dry-run"]
    )
    assert explicit.harness == ("pi", "codex") and explicit.config_dir == "custom"
    assert explicit.dry_run
    # No parser-default mutation across repeated invocations.
    assert parser.parse_args(["config"]).harness == default.harness


def test_init_defaults_and_overrides():
    parser = build_parser()
    defaults = parser.parse_args(["init"])
    fields = (
        "harness",
        "session",
        "claude_socket",
        "opencode_url",
        "pi_socket",
        "tmux_pane",
        "tmux_socket",
        "hook",
    )
    assert all(getattr(defaults, key) is None for key in fields)
    assert not defaults.no_tmux
    options = [
        "init",
        "--harness",
        "pi",
        "--session",
        "session-A",
        "--claude-socket",
        "/tmp/c",
        "--opencode-url",
        "http://127.0.0.1:1234",
        "--pi-socket",
        "/tmp/p",
        "--tmux-pane",
        "%4",
        "--tmux-socket",
        "/tmp/t",
        "--hook",
        "pi",
        "--no-tmux",
    ]
    values = parser.parse_args(options)
    assert tuple(getattr(values, key) for key in fields) == (
        "pi",
        "session-A",
        "/tmp/c",
        "http://127.0.0.1:1234",
        "/tmp/p",
        "%4",
        "/tmp/t",
        "pi",
    )
    assert values.no_tmux


def test_check_run_stop_sync_and_message_options():
    p = build_parser()
    assert not p.parse_args(["check"]).json
    assert p.parse_args(["check", "--json"]).json
    run = p.parse_args(["run"])
    assert run.harness is None and not run.print_only
    run = p.parse_args(["run", "--harness", "claude", "--print"])
    assert run.harness == "claude" and run.print_only
    stop = p.parse_args(["stop"])
    assert all(
        getattr(stop, k) is None for k in ("agent_id", "session", "watcher", "timer", "hook")
    )
    stop = p.parse_args(
        [
            "stop",
            "--agent-id",
            "a",
            "--session",
            "b",
            "--watcher",
            "c",
            "--timer",
            "d",
            "--hook",
            "codex",
        ]
    )
    assert (stop.agent_id, stop.session, stop.watcher, stop.timer, stop.hook) == (
        "a",
        "b",
        "c",
        "d",
        "codex",
    )
    sync = p.parse_args(["sync"])
    assert sync.harness is None and sync.session is None and sync.hook is None
    assert not sync.json and not sync.dry_run
    sync = p.parse_args(
        [
            "sync",
            "--harness",
            "opencode",
            "--session",
            "s",
            "--hook",
            "opencode",
            "--dry-run",
            "--json",
        ]
    )
    assert (sync.harness, sync.session, sync.hook, sync.dry_run, sync.json) == (
        "opencode",
        "s",
        "opencode",
        True,
        True,
    )
    message = p.parse_args(["message"])
    assert message.message is None and message.sender is None
    message = p.parse_args(["message", "--from", "../sender", "héllo\nworld; $(false)"])
    assert message.message == "héllo\nworld; $(false)" and message.sender == "../sender"


@pytest.mark.parametrize(
    "name,options", [("watcher", ["--path", "**/*"]), ("timer", ["--every", "3s"])]
)
def test_worker_defaults_overrides_and_help(name, options, capsys):
    p = build_parser()
    defaults = p.parse_args([name, *options])
    assert defaults.name is None and defaults.message is None and defaults.log_file is None
    assert (
        not defaults.background
        and defaults.check_interval == 30
        and defaults.unavailable_timeout == 600
    )
    explicit = p.parse_args(
        [
            name,
            *options,
            "--name",
            "worker",
            "-b",
            "--message",
            "hello",
            "--log-file",
            "worker.log",
            "--check-interval",
            "2s",
            "--unavailable-timeout",
            "never",
        ]
    )
    assert (
        explicit.name,
        explicit.background,
        explicit.message,
        explicit.log_file,
        explicit.check_interval,
        explicit.unavailable_timeout,
    ) == ("worker", True, "hello", "worker.log", 2, None)
    assert p.parse_args([name, *options, "--unavailable-timeout", "0"]).unavailable_timeout == 0
    assert main([name, "--help"]) == 0
    help_text = capsys.readouterr().out
    assert "30s" in help_text and "10m" in help_text


def test_watcher_and_timer_specific_defaults_overrides(capsys):
    p = build_parser()
    watcher = p.parse_args(["watcher", "--path", "x"])
    assert watcher.path == ["x"] and watcher.ignore == [] and watcher.events == DEFAULTS.events
    assert watcher.debounce == 10 and watcher.max_wait == 60
    watcher = p.parse_args(
        [
            "watcher",
            "--path",
            "x",
            "--path",
            ".*",
            "--ignore",
            "*.tmp",
            "--ignore",
            "cache/**",
            "--events",
            "moved,created",
            "--debounce",
            "2s",
            "--max-wait",
            "3s",
        ]
    )
    assert watcher.path == ["x", ".*"] and watcher.ignore == ["*.tmp", "cache/**"]
    assert (
        watcher.events == ("moved", "created") and watcher.debounce == 2 and watcher.max_wait == 3
    )
    assert p.parse_args(["watcher", "--path", "y"]).ignore == []
    timer = p.parse_args(["timer", "--every", "1h"])
    assert timer.every == 3600 and timer.cron is None and timer.timezone is None
    timer = p.parse_args(["timer", "--cron", "*/5 * * * *", "--timezone", "Europe/Moscow"])
    assert timer.cron == "*/5 * * * *" and timer.every is None and timer.timezone == "Europe/Moscow"
    assert main(["watcher", "--help"]) == 0
    assert "10s" in capsys.readouterr().out


@pytest.mark.parametrize(
    "argv",
    [
        ["config", "--harness", "unknown"],
        ["config", "--config-dir", ""],
        ["init", "--session", ""],
        ["init", "--harness", "bad"],
        ["init", "--hook", "bad"],
        ["init", "--opencode-url", "ftp://host"],
        ["check", "--target", ""],
        ["run", "--harness", "bad"],
        ["stop", "--agent-id", ""],
        ["stop", "--watcher", ""],
        ["stop", "--timer", ""],
        ["sync", "--session", ""],
        ["sync", "--harness", "bad"],
        ["message", ""],
        ["message", "--from", ""],
        ["message", "one", "two"],
        ["watcher"],
        ["watcher", "--path", ""],
        ["watcher", "--path", "x", "--events", "all"],
        ["timer"],
        ["timer", "--every", "1s", "--cron", "* * * * *"],
        ["timer", "--cron", "* * * * * *"],
        ["timer", "--cron", "bad"],
        ["timer", "--cron", "* * * * *", "--timezone", "No/Such_Zone"],
        ["prime", "--harness", "pi"],
        ["--unknown"],
        ["unknown"],
    ],
)
def test_invalid_specific_options(argv):
    assert main(argv) == 2


@pytest.mark.parametrize(
    "name,options", [(n, o) for n, o in MINIMAL.items() if n not in {"config", "prime"}]
)
@pytest.mark.parametrize("value", ["0", "0s", "never", "-1s", "NaNs", "1", ""])
def test_invalid_target_timeouts(name, options, value):
    assert main([name, *options, f"--timeout={value}"]) == 2


class FakeCommand:
    name = "fake"
    description = "Verify explicit command registration."

    def configure(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--answer", type=int, default=17)

    def execute(self, args: argparse.Namespace) -> int:
        assert args.environment.session_dir == ".session"
        return args.answer


def test_fake_command_uses_unchanged_dispatch(monkeypatch):
    fake = FakeCommand()
    monkeypatch.setitem(COMMANDS, fake.name, fake)
    assert main(["fake"]) == 17
    assert main(["fake", "--answer", "0"]) == 0


@pytest.mark.parametrize(
    "error,expected",
    [
        (AgentSessionError("conflict", "owner changed", ExitCode.CONFLICT), 6),
        (AgentSessionError("failure", "cannot complete"), 1),
        (OSError("do not expose internal details"), 1),
    ],
)
def test_common_error_mapping(monkeypatch, capsys, error, expected):
    def fail(args):
        raise error

    fake = FakeCommand()
    monkeypatch.setattr(fake, "execute", fail)
    monkeypatch.setitem(COMMANDS, fake.name, fake)
    assert main(["fake"]) == expected
    result = capsys.readouterr()
    assert result.out == "" and result.err
    assert "do not expose" not in result.err
