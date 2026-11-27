"""Release requirements map to actual native tests; version gates cannot substitute."""

import json
from pathlib import Path

CLIENTS = ("codex", "claude", "opencode", "pi")
CASES = (
    "discovery",
    "configuration",
    "startup",
    "shutdown",
    "registration",
    "native_delivery",
    "idle_wake",
    "busy_queue",
    "check",
    "run_resume",
    "safe_cleanup",
    "nested_layout",
)
ROOT = Path(__file__).resolve().parents[2]


def acceptance_nodes(client: str, *, root: Path = ROOT) -> list[str]:
    value = json.loads((root / "tests/native/acceptance.json").read_text())
    if value.get("schema_version") != 1 or client not in CLIENTS:
        raise ValueError("unsupported native acceptance manifest/client")
    entry = value.get("clients", {}).get(client, {})
    missing = [case for case in CASES if not entry.get("cases", {}).get(case)]
    sources = [source for source in CLIENTS if source != client]
    missing += [
        f"route:{source}->{client}" for source in sources if not entry.get("routes", {}).get(source)
    ]
    if missing:
        raise ValueError(f"native acceptance incomplete for {client}: {', '.join(missing)}")
    nodes = [entry["cases"][case] for case in CASES]
    nodes += [entry["routes"][source] for source in sources]
    for node in nodes:
        filename, separator, test = node.partition("::")
        path = root / filename
        if (
            not separator
            or not test.startswith("test_")
            or not filename.startswith("tests/native/")
            or not path.resolve().is_relative_to((root / "tests/native").resolve())
            or path.name == "test_pinned_version.py"
            or not path.is_file()
        ):
            raise ValueError("acceptance must identify an existing native test, not a version gate")
    return list(dict.fromkeys(nodes))
