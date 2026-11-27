"""Checksum-pinned actionlint bootstrap; no Python dependency or runtime code."""

import hashlib
import platform
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from urllib.request import urlopen

PINS = {
    ("darwin", "arm64"): (
        "darwin_arm64",
        "aba9ced2dee8d27fecca3dc7feb1a7f9a52caefa1eb46f3271ea66b6e0e6953f",
    ),
    ("linux", "x86_64"): (
        "linux_amd64",
        "8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8",
    ),
}


def main():
    target, digest = PINS[(sys.platform, platform.machine())]
    with tempfile.TemporaryDirectory(prefix="as-actionlint-") as temporary:
        root = Path(temporary)
        url = f"https://github.com/rhysd/actionlint/releases/download/v1.7.12/actionlint_1.7.12_{target}.tar.gz"
        with urlopen(url, timeout=30) as response:
            data = response.read(10 * 1024**2)
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("actionlint archive checksum mismatch")
        archive = root / "actionlint.tar.gz"
        archive.write_bytes(data)
        with tarfile.open(archive) as source:
            member = source.getmember("actionlint")
            if not member.isfile():
                raise ValueError("invalid actionlint executable")
            binary = root / "actionlint"
            binary.write_bytes(source.extractfile(member).read())
            binary.chmod(0o700)
        files = sorted(Path("../.github/workflows").glob("*.yml"))
        return subprocess.run(
            [str(binary), "-shellcheck=", "-pyflakes=", *map(str, files)], timeout=30
        ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
