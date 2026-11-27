"""Independent monotonic and UTC wall time, without real sleeps."""

from datetime import UTC, datetime, timedelta


class FakeClock:
    def __init__(self):
        self.elapsed = 0.0
        self.wall = datetime(2026, 1, 1, tzinfo=UTC)

    def monotonic(self) -> float:
        return self.elapsed

    def now(self) -> datetime:
        return self.wall

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("monotonic time cannot go backwards")
        self.elapsed += seconds
        self.wall += timedelta(seconds=seconds)

    def jump_wall(self, seconds: float) -> None:
        self.wall += timedelta(seconds=seconds)

    sleep = advance
