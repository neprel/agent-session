"""Checkpoint portable history or prepare a native session."""

from argparse import SUPPRESS, ArgumentParser, Namespace

from ..defaults import DEFAULTS
from ..errors import not_implemented
from ..harnesses import harness_names
from ..validation import nonempty


class SyncCommand:
    name = "sync"
    description = "Checkpoint portable history or prepare a native session."

    def configure(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--harness",
            choices=harness_names(),
            default=DEFAULTS.automatic,
            help="current or most recently used harness if omitted",
        )
        parser.add_argument(
            "--session",
            type=nonempty,
            default=DEFAULTS.automatic,
            help="saved native ID for the applicable harness if omitted",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=DEFAULTS.flag,
            help="show changes without writing",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            default=DEFAULTS.flag,
            help="print machine-readable results",
        )
        parser.add_argument(
            "--hook", choices=harness_names(), default=DEFAULTS.automatic, help=SUPPRESS
        )

    def execute(self, args: Namespace) -> int:
        return not_implemented(self.name)
