"""Test-only fake harness, exercised through the public typed interfaces."""

from argparse import ArgumentParser, Namespace
from dataclasses import replace
from importlib import resources
from pathlib import Path

import pytest

from agent_session.cli import main
from agent_session.commands import COMMANDS
from agent_session.delivery import DeliveryResult, DeliveryStatus
from agent_session.harnesses import HARNESSES
from agent_session.harnesses.base import (
    Activity,
    Capabilities,
    Capability,
    ConfigurationChange,
    ConfigureRequest,
    ConfigureResult,
    DiscoverRequest,
    DiscoverResult,
    Harness,
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
from agent_session.history import (
    CompactionContent,
    EventKind,
    Image,
    MessageContent,
    NativeCursor,
    PortableEvent,
    ProjectionBoundary,
    Provenance,
    Role,
    ToolCallContent,
    ToolResultContent,
)
from agent_session.processes import ProcessIdentity
from agent_session.session import NativeSession, RuntimeOwner

pytestmark = pytest.mark.integration


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


class FakeFlow:
    name = "fakeflow"
    description = "Exercise fake harness capabilities through unchanged dispatch."

    def configure(self, parser: ArgumentParser) -> None:
        parser.add_argument("--harness", required=True)

    def execute(self, args: Namespace) -> int:
        adapter = HARNESSES[args.harness]
        assert args.fake_label == "hello"
        discovered = adapter.discover(DiscoverRequest(args.launch_directory, {}))
        assert discovered.evidence == ("fake evidence",)
        native = discovered.session
        assert adapter.probe(ProbeRequest(native, 2)).available is True
        planned = adapter.launch(LaunchRequest(args.launch_directory, {}, native.session_id))
        assert planned.argv == ("fake-executable", "--session", "native-A")
        assert planned.cwd == args.launch_directory
        owner = RuntimeOwner("fox-a123", ProcessIdentity(123, 100.0), "runtime-token")
        payload = "Unicode 世界\n$(false); multiline message"
        sent = adapter.send(SendRequest(replace(native, owner=owner), payload, 2, owner))
        assert sent.status == DeliveryStatus.ACCEPTED and adapter.sent == [payload]
        # Repeated identical text stays separate through an import/export contract.
        events = tuple(
            PortableEvent(
                str(i),
                Provenance("fake", "native-A", i),
                EventKind.MESSAGE,
                MessageContent("same"),
                Role.USER,
            )
            for i in range(2)
        )
        projection = ProjectionBoundary(1, 2, "1")
        written = adapter.write_history(
            WriteHistoryRequest(args.launch_directory, {}, events, projection, 2)
        )
        assert written.verified and written.projection.event_count == 2
        assert written.losses == ()
        read = adapter.read_history(ReadHistoryRequest(written.session, 2))
        assert read.events == events and read.events[0].event_id != read.events[1].event_id
        assert read.cursor.record_count == 2
        assert read.cursor.session_id == written.session.session_id
        configuration = adapter.configure(
            ConfigureRequest(
                args.launch_directory, args.launch_directory, {}, ("agent-session",), True
            )
        )
        assert configuration.changes[0].action == "unchanged"
        assert not configuration.changes[0].path.exists()
        return 0


def test_new_command_and_harness_need_only_explicit_registry_entries(monkeypatch):
    fake = FakeHarness()
    assert isinstance(fake, Harness)
    monkeypatch.setitem(HARNESSES, fake.name, fake)
    monkeypatch.setitem(COMMANDS, FakeFlow.name, FakeFlow())
    assert main(["fakeflow", "--harness", "fake", "--fake-label", "hello"]) == 0
    assert main(["fakeflow", "--harness", "fake", "--fake-label", "bad"]) == 2
    assert main(["config", "--harness", "fake"]) == 4


@pytest.mark.parametrize("name", ["codex", "claude", "opencode", "pi"])
def test_unverified_native_adapters_fail_explicitly(name, tmp_path):
    adapter = HARNESSES[name]
    assert isinstance(adapter, Harness)
    assert adapter.capabilities == Capabilities()
    native = NativeSession(name, "synthetic", tmp_path)
    owner = RuntimeOwner("fox-a123", ProcessIdentity(123, 100.0), "runtime-token")
    requests = {
        "discover": DiscoverRequest(tmp_path, {}),
        "probe": ProbeRequest(native, 1),
        "launch": LaunchRequest(tmp_path, {}),
        "send": SendRequest(native, "hello", 1, owner),
        "read_history": ReadHistoryRequest(native, 1),
        "write_history": WriteHistoryRequest(tmp_path, {}, (), ProjectionBoundary(0, 0, None), 1),
        "configure": ConfigureRequest(tmp_path, tmp_path, {}, ("agent-session",)),
    }
    for method, request in requests.items():
        result = getattr(adapter, method)(request)
        assert isinstance(result, Unsupported)
        assert result.capability == method and "not implemented" in result.reason


@pytest.mark.parametrize("name,resource", [("opencode", "plugin.ts"), ("pi", "extension.ts")])
def test_resources_are_package_relative_without_claiming_functionality(name, resource):
    assert (
        "Reserved"
        in resources.files(f"agent_session.harnesses.{name}").joinpath(resource).read_text()
    )


def test_portable_tool_image_summary_values_have_explicit_content_types():
    image = Image("image/png", "c3ludGhldGlj")
    provenance = Provenance("fake", "native-A", 4, "event-A", 0)
    call = PortableEvent(
        "call",
        provenance,
        EventKind.TOOL_CALL,
        ToolCallContent("call-1", "read", {"path": "synthetic.txt"}),
        Role.ASSISTANT,
    )
    result = PortableEvent(
        "result",
        replace(provenance, record_index=5),
        EventKind.TOOL_RESULT,
        ToolResultContent("call-1", "synthetic result", (image,)),
        Role.TOOL,
    )
    summary = PortableEvent(
        "summary",
        replace(provenance, record_index=6),
        EventKind.COMPACTION,
        CompactionContent("compatible summary"),
    )
    assert call.content.call_id == result.content.call_id
    assert result.content.images[0] == image and summary.version == 1
    assert "thinking" not in {kind.value for kind in EventKind}


def test_source_layout_and_no_concrete_imports_in_core():
    import ast

    import agent_session

    root = Path(agent_session.__file__).parent
    assert set(COMMANDS) == {
        "config",
        "prime",
        "init",
        "check",
        "run",
        "stop",
        "sync",
        "message",
        "watcher",
        "timer",
    }
    for command in COMMANDS:
        assert (root / "commands" / f"{command}.py").is_file()
    for path in root.rglob("*.py"):
        if "harnesses" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not any(f"harnesses.{name}" in node.module for name in HARNESSES)
