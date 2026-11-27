"""Shared parser declarations; services and harnesses never import this module."""

from argparse import Action, ArgumentParser, Namespace

from .defaults import DEFAULTS
from .validation import duration, nonempty, unavailable_duration


class SelectHarness(Action):
    """Repeatable selection replaces the all-harness default on first use."""

    def __call__(self, parser, namespace: Namespace, values, option_string=None):
        previous = getattr(namespace, self.dest)
        if previous is self.default:
            previous = ()
        setattr(namespace, self.dest, (*previous, values))


def add_worker_options(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--name",
        type=nonempty,
        default=DEFAULTS.automatic,
        help="optional display name; absent from record if omitted",
    )
    parser.add_argument(
        "--background",
        "-b",
        action="store_true",
        default=DEFAULTS.flag,
        help="detach after worker initialization; foreground by default",
    )
    parser.add_argument(
        "--log-file",
        type=nonempty,
        default=DEFAULTS.automatic,
        help="append a persistent log; none by default",
    )
    parser.add_argument(
        "--check-interval",
        type=duration,
        default=DEFAULTS.check_interval,
        help="availability polling interval",
    )
    parser.add_argument(
        "--unavailable-timeout",
        type=unavailable_duration,
        default=DEFAULTS.unavailable_timeout,
        help="confirmed-offline budget; 0 immediately, never indefinitely",
    )
    parser.add_argument(
        "--message",
        type=nonempty,
        default=DEFAULTS.automatic,
        help="optional text included in the event; omitted by default",
    )
