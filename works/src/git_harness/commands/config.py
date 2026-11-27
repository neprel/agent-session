"""Plan and install local integration configuration."""

from argparse import ArgumentParser, Namespace

from ..defaults import DEFAULTS
from ..errors import not_implemented
from ..harnesses import harness_names
from ..options import SelectHarness
from ..validation import nonempty


class ConfigCommand:
    name = "config"
    description = "Plan and install local integration configuration."

    def configure(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--config-dir",
            type=nonempty,
            default=DEFAULTS.config_dir,
            help="integration directory; AGENTS.md uses the launch directory",
        )
        parser.add_argument(
            "--harness",
            choices=harness_names(),
            action=SelectHarness,
            default=harness_names(),
            help="select a harness; repeatable, all by default",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=DEFAULTS.flag,
            help="show changes without writing",
        )

    def execute(self, args: Namespace) -> int:
        return not_implemented(self.name)
