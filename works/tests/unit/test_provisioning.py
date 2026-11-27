import hashlib
import io
import json
import tarfile
from contextlib import contextmanager
from pathlib import Path

import pytest

from tests.support.provisioning import (
    CLIENTS,
    client_executable,
    download,
    extract_node,
    install_client,
    npm_command,
    sha256,
)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("client", CLIENTS)
def test_integrity_locks_pin_exact_client_and_every_download(client):
    lock = json.loads((Path(__file__).parents[1] / "native/locks" / f"{client}.json").read_text())
    package, version = CLIENTS[client]
    assert lock["lockfileVersion"] == 3
    assert lock["packages"][""]["dependencies"] == {package: version}
    assert lock["packages"][f"node_modules/{package}"]["version"] == version
    for name, record in lock["packages"].items():
        if name:
            assert record["resolved"].startswith("https://registry.npmjs.org/")
            assert record["integrity"].startswith("sha512-")


def test_download_checksum_and_private_artifact_creation(tmp_path, monkeypatch):
    import urllib.request

    @contextmanager
    def fake_response(url, timeout):
        assert url == "https://example.invalid/pinned" and timeout == 20
        yield io.BytesIO(b"synthetic archive")

    monkeypatch.setattr(urllib.request, "urlopen", fake_response)
    path = tmp_path / "archive"
    expected = hashlib.sha256(b"synthetic archive").hexdigest()
    download("https://example.invalid/pinned", path, expected)
    assert sha256(path) == expected
    with pytest.raises(FileExistsError):
        download("https://example.invalid/pinned", path, expected)
    with pytest.raises(ValueError, match="checksum"):
        download("https://example.invalid/pinned", tmp_path / "bad", "0" * 64)


@pytest.mark.parametrize(
    "name,link", [("../escape", None), ("/absolute", None), ("node/link", "/escape")]
)
def test_archives_cannot_escape_destination(tmp_path, name, link):
    archive = tmp_path / "malformed.tar"
    with tarfile.open(archive, "w") as output:
        info = tarfile.TarInfo(name)
        if link:
            info.type = tarfile.SYMTYPE
            info.linkname = link
        output.addfile(info)
    with pytest.raises(ValueError):
        extract_node(archive, tmp_path / "output")


def test_native_install_uses_lock_ci_without_hooks_or_user_environment(tmp_path, monkeypatch):
    import subprocess

    node = tmp_path / "node"
    destination = tmp_path / "native-codex"

    def fake_run(argv, **kwargs):
        assert argv[:2] == npm_command(node, [])
        assert "ci" in argv and "--ignore-scripts" in argv
        assert set(kwargs["env"]) == {"HOME", "PATH"}
        binary = client_executable(destination, "codex", "linux")
        binary.parent.mkdir(parents=True)
        binary.write_text("synthetic pinned binary")

    monkeypatch.setattr(subprocess, "run", fake_run)
    pin = install_client(node, destination, "codex", Path(__file__).parents[1] / "native/locks")
    assert pin["version"] == "0.144.4" and pin["sha256"]
    with pytest.raises(FileExistsError):
        install_client(node, destination, "codex", Path(__file__).parents[1] / "native/locks")
    with pytest.raises(ValueError, match="Linux"):
        client_executable(destination, "codex", "darwin")
