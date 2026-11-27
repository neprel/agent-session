"""Monitor filesystem changes and notify a target."""

from argparse import ArgumentParser, Namespace

from ..defaults import DEFAULTS
from ..errors import not_implemented
from ..options import add_worker_options
from ..validation import duration, event_types, nonempty


class WatcherCommand:
    name = "watcher"
    description = "Monitor filesystem changes and notify a target."

    def configure(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--path",
            action="append",
            type=nonempty,
            required=True,
            help="path/glob to monitor; repeatable, no default",
        )
        parser.add_argument(
            "--ignore",
            action="append",
            type=nonempty,
            default=list(DEFAULTS.empty),
            help="excluded glob; repeatable",
        )
        parser.add_argument(
            "--events",
            type=event_types,
            default=DEFAULTS.events,
            help="comma-separated event types",
        )
        parser.add_argument(
            "--debounce", type=duration, default=DEFAULTS.debounce, help="delay after last change"
        )
        parser.add_argument(
            "--max-wait",
            type=duration,
            default=DEFAULTS.max_wait,
            help="maximum delay after first change",
        )
        add_worker_options(parser)

    def execute(self, args: Namespace) -> int:
        return not_implemented(self.name)
