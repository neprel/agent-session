"""Send scheduled notifications to a target."""

from argparse import ArgumentParser, Namespace

from ..defaults import DEFAULTS
from ..errors import not_implemented
from ..options import add_worker_options
from ..validation import cron_expression, duration, timezone


class TimerCommand:
    name = "timer"
    description = "Send scheduled notifications to a target."

    def configure(self, parser: ArgumentParser) -> None:
        schedule = parser.add_mutually_exclusive_group(required=True)
        schedule.add_argument(
            "--cron",
            type=cron_expression,
            default=DEFAULTS.automatic,
            help="five-field cron expression; exactly one schedule is required",
        )
        schedule.add_argument(
            "--every",
            type=duration,
            default=DEFAULTS.automatic,
            help="positive interval; first tick after one interval",
        )
        parser.add_argument(
            "--timezone",
            type=timezone,
            default=DEFAULTS.automatic,
            help="IANA zone; system local for cron if omitted, ignored for intervals",
        )
        add_worker_options(parser)

    def execute(self, args: Namespace) -> int:
        return not_implemented(self.name)
