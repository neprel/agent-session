"""Opt-in provisioning/version gate, not a native adapter acceptance claim."""

import json
import re
import shutil
from pathlib import Path

import pytest

from tests.support.native_isolation import run_audited_client, verify_isolation
from tests.support.provisioning import CLIENTS, NODE_VERSION, sha256

pytestmark = pytest.mark.native


def test_provisioned_version_is_integrity_checked_and_confined(request, workspace):
    verify_isolation()
    manifest_path = request.config.getoption("--native-manifest")
    client = request.config.getoption("--native-client")
    assert manifest_path and client, "provisioned manifest/client are required, never skipped"
    manifest = json.loads(manifest_path.read_text())
    assert manifest["schema_version"] == 1
    pin = manifest["clients"][client]
    assert pin["version"] == CLIENTS[client][1]
    executable = Path(pin["executable"])
    assert sha256(executable) == pin["sha256"]
    assert sha256(Path(__file__).parent / "locks" / f"{client}.json") == pin["lock_sha256"]
    node = Path(manifest["node"]["directory"])
    assert manifest["node"]["version"] == NODE_VERSION
    assert sha256(node / "bin/node") == manifest["node"]["sha256"]
    environment = dict(workspace.environment)
    environment.update(
        PATH=f"{node / 'bin'}:/usr/bin:/bin",
        PI_OFFLINE="1",
        PI_TELEMETRY="0",
        CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1",
        DISABLE_AUTOUPDATER="1",
        OPENCODE_DISABLE_AUTOUPDATE="true",
    )
    strace = shutil.which("strace", path="/usr/bin:/bin")
    for name, binary, version in [
        ("node", node / "bin/node", NODE_VERSION),
        (client, executable, pin["version"]),
    ]:
        result = run_audited_client(
            [str(binary), "--version"],
            environment=environment,
            cwd=workspace.work,
            trace=workspace.work / f"{name}.trace",
            strace=strace,
        )
        assert result.returncode == 0
        assert re.search(rf"(?<![\d.]){re.escape(version)}(?![\d.])", result.stdout.decode())
