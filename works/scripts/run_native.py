"""Explicit repository-only native entry point; no implicit clients or inference.

Run from works/: uv run --locked python scripts/run_native.py --isolation-only
For pinned version gates: --manifest PATH --client NAME (provision first).
Linux needs unshare/user namespaces and strace. macOS supports isolation checks
only until a native syscall audit is available. Unavailable means failure.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.support.native_isolation import (  # noqa: E402
    IsolationUnavailable,
    confinement_command,
    enable_loopback,
    verify_isolation,
)
from tests.support.workspace import Processes, Workspace  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--isolation-only", action="store_true")
    parser.add_argument(
        "--linux-sudo",
        action="store_true",
        help="use privileged namespaces on clean hosted Linux runners",
    )
    parser.add_argument("--suite", choices=("foundation", "acceptance"), default="foundation")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--client", choices=("codex", "claude", "opencode", "pi"))
    parser.add_argument("--inside", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--report", type=Path, help="write content-free native test counts")
    args = parser.parse_args(argv)
    if Path.cwd() != ROOT:
        parser.error("run product commands from works/")
    if not args.isolation_only and (args.manifest is None or args.client is None):
        parser.error("native client gates require a provisioned --manifest and --client")
    try:
        if args.inside:
            enable_loopback()
            evidence = verify_isolation()
            print(json.dumps(evidence), flush=True)
            if args.isolation_only:
                return 0
            if sys.platform != "linux":
                raise IsolationUnavailable(
                    "macOS native client audit is unavailable; no client launched"
                )
            import pytest

            from tests.support.acceptance import acceptance_nodes

            nodes = (
                acceptance_nodes(args.client)
                if args.suite == "acceptance"
                else [str(ROOT / "tests/native/test_pinned_version.py")]
            )

            junit = Path(tempfile.gettempdir()) / "native-junit.xml"
            result = pytest.main(
                [
                    "-o",
                    "addopts=",
                    "-m",
                    "native",
                    "--strict-markers",
                    "-q",
                    "--junitxml",
                    str(junit),
                    "--native-manifest",
                    str(args.manifest.resolve()),
                    "--native-client",
                    args.client,
                    *nodes,
                ]
            )
            if args.report:
                from scripts.report_ci import summarize

                report = summarize(junit)
                report.update(client=args.client, suite=args.suite, exit=int(result))
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(json.dumps(report, indent=2) + "\n")
            return result
        tools = {
            name: path
            for name in ("sandbox-exec", "unshare", "sudo")
            if (path := shutil.which(name))
        }
        arguments = [sys.executable, str(Path(__file__).resolve()), "--inside"]
        arguments += ["--suite", args.suite]
        if args.report:
            arguments += ["--report", str(args.report.resolve())]
        arguments += (
            ["--isolation-only"]
            if args.isolation_only
            else ["--manifest", str(args.manifest.resolve()), "--client", args.client]
        )
        confined = confinement_command(sys.platform, arguments, tools, linux_sudo=args.linux_sudo)
        with tempfile.TemporaryDirectory(prefix="as-native-", dir="/tmp") as temporary:
            workspace = Workspace(Path(temporary))
            # Test dependencies are already installed by locked uv sync. Disable
            # user plugin auto-discovery and all inherited provider variables.
            workspace.environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
            workspace.work = ROOT
            owned = Processes(workspace)
            process = owned.spawn(confined)
            try:
                out, err = process.communicate(timeout=120)
                sys.stdout.write(out.decode(errors="replace"))
                sys.stderr.write(err.decode(errors="replace"))
                return process.returncode
            finally:
                owned.close()
    except (IsolationUnavailable, OSError, subprocess.TimeoutExpired, ValueError) as exc:
        print(f"native_isolation_unavailable: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
