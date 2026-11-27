"""Reusable stateful fake Harness; no native protocol or process access."""

from agent_session.delivery import DeliveryResult, DeliveryStatus
from agent_session.harnesses.base import (
    Activity,
    Capabilities,
    Capability,
    ConfigurationChange,
    ConfigureRequest,
    ConfigureResult,
    DiscoverRequest,
    DiscoverResult,
    LaunchPlan,
    LaunchRequest,
    Option,
    ProbeRequest,
    ProbeResult,
    ReadHistoryRequest,
    ReadHistoryResult,
    SendRequest,
    WriteHistoryRequest,
    WriteHistoryResult,
)
from agent_session.history import (
    NativeCursor,
)
from agent_session.session import NativeSession


class FakeHarness:
    name = "fake"
    capabilities = Capabilities(frozenset(Capability), ("1.0.0",))

    def __init__(self):
        self.events = ()
        self.sent = []

    def discover(self, request: DiscoverRequest) -> DiscoverResult:
        return DiscoverResult(
            NativeSession(self.name, "native-A", request.launch_directory), ("fake evidence",)
        )

    def probe(self, request: ProbeRequest) -> ProbeResult:
        return ProbeResult(True, Activity.IDLE, "fake runtime reachable", safe_queue=True)

    def launch(self, request: LaunchRequest) -> LaunchPlan:
        return LaunchPlan(
            ("fake-executable", "--session", request.session_id),
            request.launch_directory,
            request.environment,
        )

    def send(self, request: SendRequest) -> DeliveryResult:
        self.sent.append(request.message)
        return DeliveryResult(DeliveryStatus.ACCEPTED, "admitted", "fake-native")

    def read_history(self, request: ReadHistoryRequest) -> ReadHistoryResult:
        return ReadHistoryResult(
            request.session,
            self.events,
            NativeCursor(self.name, request.session.session_id, "1", len(self.events), "a" * 64),
        )

    def write_history(self, request: WriteHistoryRequest) -> WriteHistoryResult:
        self.events = request.events
        return WriteHistoryResult(
            NativeSession(self.name, "import-B", request.launch_directory),
            request.projection,
            True,
        )

    def configure(self, request: ConfigureRequest) -> ConfigureResult:
        return ConfigureResult(
            (ConfigurationChange(request.config_directory / "fake.conf", "unchanged", "no write"),)
        )

    def configure_options(self) -> tuple[Option, ...]:
        return (
            Option(
                "fakeflow", ("--fake-label",), "fake extension option", choices=("hello", "other")
            ),
        )
