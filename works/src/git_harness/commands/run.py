"""Plan, start or resume a target harness."""

from argparse import ArgumentParser, Namespace

from ..defaults import DEFAULTS
from ..errors import not_implemented
from ..harnesses import harness_names


class RunCommand:
    name = "run"
    description = "Plan, start or resume a target harness."

    def configure(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--harness",
            choices=harness_names(),
            default=DEFAULTS.automatic,
            help="saved harness if omitted; required for a new target",
        )
        parser.add_argument(
            "--print",
            dest="print_only",
            action="store_true",
            default=DEFAULTS.flag,
            help="print the launch plan without writing or launching",
        )

    def execute(self, args: Namespace) -> int:
        return not_implemented(self.name)
