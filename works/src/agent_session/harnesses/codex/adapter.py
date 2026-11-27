"""codex adapter boundary. No native capabilities are verified in this foundation."""

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
    name = "codex"
    capabilities = Capabilities()

    def discover(self, request: DiscoverRequest) -> DiscoverResult | Unsupported:
        return Unsupported(Capability.DISCOVER, "codex discover is not implemented")

    def probe(self, request: ProbeRequest) -> ProbeResult | Unsupported:
        return Unsupported(Capability.PROBE, "codex probe is not implemented")

    def launch(self, request: LaunchRequest) -> LaunchPlan | Unsupported:
        return Unsupported(Capability.LAUNCH, "codex launch is not implemented")

    def send(self, request: SendRequest) -> DeliveryResult | Unsupported:
        return Unsupported(Capability.SEND, "codex send is not implemented")

    def read_history(self, request: ReadHistoryRequest) -> ReadHistoryResult | Unsupported:
        return Unsupported(Capability.READ_HISTORY, "codex read_history is not implemented")

    def write_history(self, request: WriteHistoryRequest) -> WriteHistoryResult | Unsupported:
        return Unsupported(Capability.WRITE_HISTORY, "codex write_history is not implemented")

    def configure(self, request: ConfigureRequest) -> ConfigureResult | Unsupported:
        return Unsupported(Capability.CONFIGURE, "codex configure is not implemented")

    def configure_options(self) -> tuple[Option, ...]:
        return ()
