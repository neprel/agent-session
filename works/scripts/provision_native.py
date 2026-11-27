"""Provision pinned native tests in a new private directory, without user tools.

Run from works/: uv run --locked python scripts/provision_native.py --destination
/tmp/NEW_DIRECTORY --client codex. Node bootstraps from a checked official archive;
npm ci verifies the committed per-client integrity lock. No client is executed.
Use --node-only to validate prerequisites on macOS without claiming client support.
"""

import argparse
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.support.provisioning import (  # noqa: E402
    CLIENTS,
    NODE_ARCHIVES,
    NODE_VERSION,
    download,
    extract_node,
    install_client,
    sha256,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--client", choices=tuple(CLIENTS))
    parser.add_argument("--node-only", action="store_true")
    args = parser.parse_args()
    if Path.cwd() != ROOT:
        parser.error("run product commands from works/")
    if not args.node_only and not args.client:
        parser.error("select --client or --node-only")
    native_platform = (sys.platform, platform.machine())
    if native_platform not in NODE_ARCHIVES or (not args.node_only and sys.platform != "linux"):
        parser.error(
            "pinned native client provisioning is Linux x86_64; this platform is unavailable"
        )
    destination = args.destination.resolve()
    destination.mkdir(mode=0o700)  # Refuse existing directories; preserve configuration.
    suffix, digest = NODE_ARCHIVES[native_platform]
    archive = destination / ("node-" + suffix)
    download(
        f"https://nodejs.org/dist/v{NODE_VERSION}/node-v{NODE_VERSION}-{suffix}", archive, digest
    )
    node = extract_node(archive, destination)
    manifest = {
        "schema_version": 1,
        "node": {
            "version": NODE_VERSION,
            "directory": str(node),
            "sha256": sha256(node / "bin/node"),
            "archive_sha256": digest,
        },
        "clients": {},
    }
    if args.client:
        manifest["clients"][args.client] = install_client(
            node, destination / args.client, args.client, ROOT / "tests/native/locks"
        )
    path = destination / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"manifest": str(path), "clients": list(manifest["clients"])}))


if __name__ == "__main__":
    main()
