"""Stop owned triggers; preserve the harness and history."""

from argparse import SUPPRESS, ArgumentParser, Namespace

from ..defaults import DEFAULTS
from ..errors import not_implemented
from ..harnesses import harness_names
from ..validation import nonempty


class StopCommand:
    name = "stop"
    description = "Stop owned triggers; preserve the harness and history."

    def configure(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--agent-id",
            type=nonempty,
            default=DEFAULTS.automatic,
            help="expected owner label; no filter by default",
        )
        parser.add_argument(
            "--session",
            type=nonempty,
            default=DEFAULTS.automatic,
            help="expected native ID; no filter by default",
        )
        parser.add_argument(
            "--watcher",
            type=nonempty,
            default=DEFAULTS.automatic,
            help="watcher ID or exact name; all owned triggers if neither selector is set",
        )
        parser.add_argument(
            "--timer",
            type=nonempty,
            default=DEFAULTS.automatic,
            help="timer ID or exact name; all owned triggers if neither selector is set",
        )
        parser.add_argument(
            "--hook", choices=harness_names(), default=DEFAULTS.automatic, help=SUPPRESS
        )

    def execute(self, args: Namespace) -> int:
        return not_implemented(self.name)
