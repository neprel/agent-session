"""Pinned native prerequisites and artifacts; installation is explicitly opt-in.

Client pins/path choices follow session-migrate install-native-test-clis.sh at
fefb719088dc0157b16f071065daa30434a0b980 (MIT, see LICENSE.session-migrate).
Changes: pinned Node archive hashes, per-client integrity locks, no lifecycle
scripts, private install roots and content-free manifests. Never executes a
native client during installation.
"""

import hashlib
import json
import subprocess
import tarfile
import time
import urllib.request
from pathlib import Path

NODE_VERSION = "22.19.0"
NODE_ARCHIVES = {
    ("linux", "x86_64"): (
        "linux-x64.tar.xz",
        "c0649af18e6a24f6fe5535a3e86b341dd49a8e71117c8b68bde973ef834f16f2",
    ),
    ("darwin", "arm64"): (
        "darwin-arm64.tar.gz",
        "c59006db713c770d6ec63ae16cb3edc11f49ee093b5c415d667bb4f436c6526d",
    ),
}
CLIENTS = {
    "codex": ("@openai/codex", "0.144.4"),
    "claude": ("@anthropic-ai/claude-code", "2.1.209"),
    "opencode": ("@opencode/cli", "2.0.23"),
    "pi": ("@earendil-works/pi-coding-agent", "0.80.6"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024**2):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, path: Path, expected: str) -> None:
    deadline = time.monotonic() + 120
    with urllib.request.urlopen(url, timeout=20) as response, path.open("xb") as stream:
        while chunk := response.read(1024**2):
            if stream.tell() + len(chunk) > 200 * 1024**2 or time.monotonic() > deadline:
                raise ValueError("native prerequisite download exceeded budget")
            stream.write(chunk)
    if sha256(path) != expected:
        raise ValueError("native prerequisite checksum mismatch")


def extract_node(archive: Path, destination: Path) -> Path:
    with tarfile.open(archive) as source:
        roots = set()
        for member in source.getmembers():
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or member.isdev() or member.islnk():
                raise ValueError("unsafe native prerequisite archive")
            target = destination / path
            if not target.resolve().is_relative_to(destination.resolve()):
                raise ValueError("archive path escaped destination")
            if member.issym() and not (target.parent / member.linkname).resolve().is_relative_to(
                destination.resolve()
            ):
                raise ValueError("archive symlink escaped destination")
            roots.add(path.parts[0])
            source.extract(member, destination, filter="data")
    if len(roots) != 1:
        raise ValueError("unexpected Node archive layout")
    return destination / roots.pop()


def npm_command(node: Path, arguments: list[str]) -> list[str]:
    return [str(node / "bin/node"), str(node / "lib/node_modules/npm/bin/npm-cli.js"), *arguments]


def client_executable(root: Path, client: str, platform: str) -> Path:
    if platform != "linux":
        raise ValueError("native client provisioning is currently Linux x86_64 only")
    relative = {
        "codex": "@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex",
        "opencode": "@opencode/cli-linux-x64/bin/opencode",
        # The top-level npm bin points to a Windows stub until postinstall.
        # Select the integrity-locked Linux optional package without hooks.
        "claude": "@anthropic-ai/claude-code-linux-x64/claude",
        "pi": ".bin/pi",
    }[client]
    return root / "node_modules" / relative


def install_client(node: Path, destination: Path, client: str, locks: Path) -> dict:
    package, version = CLIENTS[client]
    destination.mkdir(mode=0o700)
    lock = locks / f"{client}.json"
    value = json.loads(lock.read_text())
    if value["packages"][""]["dependencies"] != {package: version}:
        raise ValueError("native dependency lock does not match the approved pin")
    for key, record in value["packages"].items():
        if key and (
            not record.get("integrity")
            or not record.get("resolved", "").startswith("https://registry.npmjs.org/")
        ):
            raise ValueError("native dependency lock lacks public-registry integrity")
    (destination / "package.json").write_text(
        json.dumps(
            {
                "name": f"git-harness-native-{client}",
                "version": "0.0.0",
                "private": True,
                "dependencies": {package: version},
            }
        )
    )
    (destination / "package-lock.json").write_bytes(lock.read_bytes())
    home = destination / "home"
    home.mkdir()
    environment = {"HOME": str(home), "PATH": str(node / "bin") + ":/usr/bin:/bin"}
    subprocess.run(
        npm_command(
            node,
            [
                "ci",
                "--ignore-scripts",
                "--no-audit",
                "--no-fund",
                "--cache",
                str(destination / "cache"),
            ],
        ),
        cwd=destination,
        env=environment,
        check=True,
        timeout=180,
        capture_output=True,
    )
    executable = client_executable(destination, client, "linux").resolve()
    if not executable.is_relative_to(destination.resolve()) or not executable.is_file():
        raise ValueError("pinned native executable is unavailable")
    return {
        "version": version,
        "executable": str(executable),
        "sha256": sha256(executable),
        "lock_sha256": sha256(lock),
    }
