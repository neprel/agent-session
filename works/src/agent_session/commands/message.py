"""Submit text to the current harness."""

from argparse import ArgumentParser, Namespace

from ..defaults import DEFAULTS
from ..errors import not_implemented
from ..validation import nonempty


class MessageCommand:
    name = "message"
    description = "Submit text to the current harness."

    def configure(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "message",
            nargs="?",
            type=nonempty,
            default=DEFAULTS.automatic,
            help="message text; read stdin if absent",
        )
        parser.add_argument(
            "--from",
            dest="sender",
            type=nonempty,
            default=DEFAULTS.automatic,
            help="registered sender path for reply routing; absent by default",
        )

    def execute(self, args: Namespace) -> int:
        return not_implemented(self.name)
