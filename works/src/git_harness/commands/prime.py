"""Print concise session usage."""

from argparse import ArgumentParser, Namespace

from ..errors import not_implemented


class PrimeCommand:
    name = "prime"
    description = "Print concise session usage."

    def configure(self, parser: ArgumentParser) -> None:
        pass

    def execute(self, args: Namespace) -> int:
        return not_implemented(self.name)
