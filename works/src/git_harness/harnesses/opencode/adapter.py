"""opencode adapter boundary. No native capabilities are verified in this foundation."""

from ...delivery import DeliveryResult
from ..base import (
    Capabilities,
    Capability,
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
    Unsupported,
    WriteHistoryRequest,
    WriteHistoryResult,
)


class Adapter:
    name = "opencode"
    capabilities = Capabilities()

    def discover(self, request: DiscoverRequest) -> DiscoverResult | Unsupported:
        return Unsupported(Capability.DISCOVER, "opencode discover is not implemented")

    def probe(self, request: ProbeRequest) -> ProbeResult | Unsupported:
        return Unsupported(Capability.PROBE, "opencode probe is not implemented")

    def launch(self, request: LaunchRequest) -> LaunchPlan | Unsupported:
        return Unsupported(Capability.LAUNCH, "opencode launch is not implemented")

    def send(self, request: SendRequest) -> DeliveryResult | Unsupported:
        return Unsupported(Capability.SEND, "opencode send is not implemented")

    def read_history(self, request: ReadHistoryRequest) -> ReadHistoryResult | Unsupported:
        return Unsupported(Capability.READ_HISTORY, "opencode read_history is not implemented")

    def write_history(self, request: WriteHistoryRequest) -> WriteHistoryResult | Unsupported:
        return Unsupported(Capability.WRITE_HISTORY, "opencode write_history is not implemented")

    def configure(self, request: ConfigureRequest) -> ConfigureResult | Unsupported:
        return Unsupported(Capability.CONFIGURE, "opencode configure is not implemented")

    def configure_options(self) -> tuple[Option, ...]:
        return (
            Option(
                "init", ("--opencode-url",), "verified OpenCode server URL; otherwise absent", "url"
            ),
        )
