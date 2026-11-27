"""Parser construction, common options, dispatch and common error handling."""

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .commands import COMMANDS
from .defaults import DEFAULTS, Environment
from .errors import AgentSessionError, ExitCode
from .harnesses import HARNESSES
from .validation import duration, endpoint_url, nonempty

TARGET_COMMANDS = frozenset({"init", "check", "run", "stop", "sync", "message", "watcher", "timer"})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-session", allow_abbrev=False)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")
    for name, command in COMMANDS.items():
        child = subparsers.add_parser(
            name,
            description=command.description,
            help=command.description,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            allow_abbrev=False,
        )
        verbosity = child.add_mutually_exclusive_group()
        verbosity.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            default=DEFAULTS.verbose,
            help="show detailed diagnostics",
        )
        verbosity.add_argument(
            "--quiet",
            "-q",
            action="store_true",
            default=DEFAULTS.quiet,
            help="suppress routine output",
        )
        if name in TARGET_COMMANDS:
            child.add_argument(
                "--target",
                type=nonempty,
                default=DEFAULTS.target,
                help="registration file or target directory",
            )
            child.add_argument(
                "--timeout",
                type=duration,
                default=DEFAULTS.stop_timeout if name == "stop" else DEFAULTS.timeout,
                help="bounded operation budget",
            )
        command.configure(child)
        for harness in HARNESSES.values():
            for option in harness.configure_options():
                if option.command == name:
                    child.add_argument(
                        *option.flags,
                        help=option.help,
                        type={"text": nonempty, "path": nonempty, "url": endpoint_url}[
                            option.value_type
                        ],
                        choices=option.choices,
                        default=DEFAULTS.automatic,
                    )
        child.set_defaults(_implementation=command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        # Snapshot package configuration once. Native discovery receives its own
        # explicitly scoped environment through the adapter request contract.
        args.environment = Environment.from_environ(os.environ)
        args.launch_directory = Path.cwd()
        if args.command is None:
            parser.print_help()
            return ExitCode.SUCCESS
        return args._implementation.execute(args)
    except SystemExit as exc:
        return int(exc.code)
    except AgentSessionError as exc:
        print(f"{exc.code}: {exc}", file=sys.stderr)
        return exc.exit_code
    except OSError:
        print("operation_failed: operating system operation failed", file=sys.stderr)
        return ExitCode.FAILURE
