"""Inspect session availability without inference."""

from argparse import ArgumentParser, Namespace

from ..defaults import DEFAULTS
from ..errors import not_implemented


class CheckCommand:
    name = "check"
    description = "Inspect session availability without inference."

    def configure(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--json",
            action="store_true",
            default=DEFAULTS.flag,
            help="print machine-readable results",
        )

    def execute(self, args: Namespace) -> int:
        return not_implemented(self.name)
