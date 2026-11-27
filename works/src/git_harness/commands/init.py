"""Register a verified native session."""

from argparse import SUPPRESS, ArgumentParser, Namespace

from ..defaults import DEFAULTS
from ..errors import not_implemented
from ..harnesses import harness_names
from ..validation import nonempty


class InitCommand:
    name = "init"
    description = "Register a verified native session."

    def configure(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--harness",
            choices=harness_names(),
            default=DEFAULTS.automatic,
            help="verified current harness if omitted",
        )
        parser.add_argument(
            "--session",
            type=nonempty,
            default=DEFAULTS.automatic,
            help="verified current native ID if omitted",
        )
        parser.add_argument(
            "--tmux-pane",
            type=nonempty,
            default=DEFAULTS.automatic,
            help="verified current pane if omitted",
        )
        parser.add_argument(
            "--tmux-socket",
            type=nonempty,
            default=DEFAULTS.automatic,
            help="verified current server socket if omitted",
        )
        parser.add_argument(
            "--no-tmux", action="store_true", default=DEFAULTS.flag, help="disable tmux discovery"
        )
        parser.add_argument(
            "--hook", choices=harness_names(), default=DEFAULTS.automatic, help=SUPPRESS
        )

    def execute(self, args: Namespace) -> int:
        return not_implemented(self.name)
