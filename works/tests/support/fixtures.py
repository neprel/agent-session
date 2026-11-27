"""Copy immutable, version-pinned synthetic corpus records into an isolated home."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "fixtures/v1"


def materialize(name: str, directory: Path) -> Path:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    entry = manifest["files"][name]  # Only named manifest entries, never arbitrary paths.
    data = (ROOT / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise ValueError("synthetic fixture checksum mismatch")
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / name
    with destination.open("xb") as stream:
        stream.write(data)
    destination.chmod(0o600)
    return destination
