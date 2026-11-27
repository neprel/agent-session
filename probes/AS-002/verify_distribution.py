"""Verify built artifacts from works/ without installing into the user's Python.

Run: uv run --locked python ../probes/AS-002/verify_distribution.py
Build first with uv build. Installs require only normal dependency downloads.
No native clients, models, credentials or user session stores are used.
"""

from email.parser import Parser
from importlib.metadata import version as package_version
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile


def main():
    product = Path(__file__).resolve().parents[2] / "works"
    assert Path.cwd() == product, "Run from works/"
    uv = shutil.which("uv")
    assert uv is not None
    wheel, = (product / "dist").glob("*.whl")
    sdist, = (product / "dist").glob("*.tar.gz")
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata = Parser().parsestr(archive.read(next(n for n in names if n.endswith("/METADATA"))).decode())
        requirements = metadata.get_all("Requires-Dist")
        assert {r.split(">=")[0] for r in requirements} == {"croniter", "psutil", "unique-namer", "watchdog"}
        assert all("pytest" not in r and "coverage" not in r and "ruff" not in r for r in requirements)
        for resource in ("opencode/plugin.ts", "pi/extension.ts"):
            assert f"agent_session/harnesses/{resource}" in names
        assert not any(n.endswith(("hooks.json", "settings.json")) for n in names)
        notice = archive.read(next(n for n in names if n.endswith("/THIRD_PARTY_NOTICES.md"))).decode()
        assert "Copyright (c) 2026 xhluca" in notice
        assert any(n.endswith("/licenses/LICENSE") for n in names)
        assert not any(n.startswith(("tests/", "tasks/", "agents/", "probes/")) for n in names)
    with tarfile.open(sdist) as archive:
        names = archive.getnames()
        assert any(n.endswith("/uv.lock") for n in names)
        assert any("/tests/unit/test_cli.py" in n for n in names)
        assert not any("/tasks/" in n or "/probes/" in n for n in names)
    with tempfile.TemporaryDirectory(prefix="agent-session-AS-002-dist-") as temporary:
        root = Path(temporary)
        env = {"HOME": str(root / "home"), "PATH": "/usr/bin:/bin", "TERM": "dumb"}
        # A clean HOME prevents uv config inheritance. Dependency caches are
        # installation input, not native harness state.
        env["UV_CACHE_DIR"] = str(Path(os.environ.get("UV_CACHE_DIR", Path.home() / ".cache/uv")))
        Path(env["HOME"]).mkdir()
        commands = []

        def run(arguments):
            result = subprocess.run(arguments, cwd=root, env=env, capture_output=True, text=True, timeout=120)
            assert result.returncode == 0, result.stderr
            commands.append({"argv": [str(a) for a in arguments], "exit": result.returncode})
            return result.stdout

        for label, artifact in (("wheel", wheel), ("sdist", sdist)):
            venv = root / label
            run([uv, "--no-config", "venv", "--python", sys.executable, str(venv)])
            python = venv / "bin/python"
            run([uv, "--no-config", "pip", "install", "--python", str(python), str(artifact)])
            version = run([str(venv / "bin/agent-session"), "--version"])
            assert "agent-session 0.1.0" in version
            assert "watcher" in run([str(python), "-m", "agent_session", "--help"])
            # The fake command/harness test uses only installed package APIs.
            # It cannot import the source checkout or rely on pytest.
            run([str(python), "-c", "\n".join([
                "from pathlib import Path",
                "from importlib import resources",
                "import agent_session",
                "from agent_session.cli import main",
                "from agent_session.commands import COMMANDS",
                "from agent_session.harnesses import HARNESSES",
                "from agent_session.harnesses.base import Harness, Unsupported, DiscoverRequest",
                "assert 'site-packages' in agent_session.__file__",
                "assert all(isinstance(a, Harness) for a in HARNESSES.values())",
                "assert isinstance(HARNESSES['codex'].discover(DiscoverRequest(Path.cwd(), {})), Unsupported)",
                "assert resources.files('agent_session.harnesses.pi').joinpath('extension.ts').is_file()",
                "class FakeCommand:",
                " name='installed-fake'; description='installed test'",
                " def configure(self, parser): parser.add_argument('--answer', type=int, default=0)",
                " def execute(self, args): return args.answer",
                "COMMANDS['installed-fake']=FakeCommand()",
                "assert main(['installed-fake']) == 0",
            ])])
            # Add only a test runner after checking the runtime-only install.
            # The source test file imports the clean installed distribution.
            run([uv, "--no-config", "pip", "install", "--python", str(python), f"pytest=={package_version('pytest')}"])
            run([str(python), "-m", "pytest", "-q", "-c", os.devnull,
                 str(product / "tests/integration/test_interfaces.py")])
        version = run([uv, "--no-config", "tool", "run", "--isolated", "--from", str(wheel), "agent-session", "--version"])
        assert "agent-session 0.1.0" in version
        print(json.dumps({"artifacts": [wheel.name, sdist.name], "checks": len(commands), "result": "passed"}))


if __name__ == "__main__":
    main()
