"""Verify built artifacts from works/ without installing into the user's Python.

Run: uv run --locked python scripts/verify_distribution.py
Build first with uv build. Installs require only normal dependency downloads.
No native clients, models, credentials or user session stores are used.
"""

import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import zipfile
from email.parser import Parser
from importlib.metadata import version as package_version
from pathlib import Path


def main():
    product = Path(__file__).resolve().parents[2] / "works"
    assert Path.cwd() == product, "Run from works/"
    uv = shutil.which("uv")
    package_version_text = tomllib.loads((product / "pyproject.toml").read_text())["project"][
        "version"
    ]
    uvx = shutil.which("uvx")
    git = shutil.which("git")
    assert uv is not None and uvx is not None and git is not None
    (wheel,) = (product / "dist").glob("*.whl")
    (sdist,) = (product / "dist").glob("*.tar.gz")
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        assert {n.split("/")[0] for n in names if ".dist-info/" not in n} == {"git_harness"}
        metadata = Parser().parsestr(
            archive.read(next(n for n in names if n.endswith("/METADATA"))).decode()
        )
        requirements = metadata.get_all("Requires-Dist")
        assert {r.split(">=")[0] for r in requirements} == {
            "croniter",
            "psutil",
            "unique-namer",
            "watchdog",
        }
        assert all(
            "pytest" not in r and "coverage" not in r and "ruff" not in r for r in requirements
        )
        for resource in ("opencode/plugin.ts", "pi/extension.ts"):
            assert f"git_harness/harnesses/{resource}" in names
        assert not any(n.endswith(("hooks.json", "settings.json")) for n in names)
        notice = archive.read(
            next(n for n in names if n.endswith("/THIRD_PARTY_NOTICES.md"))
        ).decode()
        assert "Copyright (c) 2026 xhluca" in notice
        assert any(n.endswith("/licenses/LICENSE") for n in names)
        assert not any(n.startswith(("tests/", "tasks/", "agents/", "probes/")) for n in names)
    with tarfile.open(sdist) as archive:
        names = archive.getnames()
        assert any(n.endswith("/uv.lock") for n in names)
        assert not any("/tests/" in n or "/scripts/" in n for n in names)
        assert not any("/tasks/" in n or "/probes/" in n for n in names)
    with tempfile.TemporaryDirectory(prefix="git-harness-AS-017-dist-") as temporary:
        root = Path(temporary)
        env = {"HOME": str(root / "home"), "PATH": "/usr/bin:/bin", "TERM": "dumb"}
        # A clean HOME prevents uv config inheritance. Dependency caches are
        # installation input, not native harness state.
        env["UV_CACHE_DIR"] = str(Path(os.environ.get("UV_CACHE_DIR", Path.home() / ".cache/uv")))
        env.update(
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=os.devnull,
            UV_TOOL_DIR=str(root / "tools"),
            UV_TOOL_BIN_DIR=str(root / "tool-bin"),
        )
        Path(env["HOME"]).mkdir()
        assert (
            subprocess.run(
                [git, "rev-parse", "--is-inside-work-tree"],
                cwd=root,
                env=env,
                capture_output=True,
                timeout=10,
            ).returncode
            != 0
        )
        commands = []

        def run(arguments):
            result = subprocess.run(
                arguments, cwd=root, env=env, capture_output=True, text=True, timeout=120
            )
            assert result.returncode == 0, result.stderr
            commands.append({"argv": [str(a) for a in arguments], "exit": result.returncode})
            return result.stdout

        def check_commands(bin_dir):
            env["PATH"] = f"{bin_dir}{os.pathsep}/usr/bin:/bin"
            assert not (root / ".git").exists()
            expected = f"git-harness {package_version_text}"
            assert run([str(bin_dir / "git-harness"), "--version"]).strip() == expected
            assert run([git, "harness", "--version"]).strip() == expected
            assert "watcher" in run([git, "harness", "-h"])

        for label, artifact in (("wheel", wheel), ("sdist", sdist)):
            venv = root / label
            run([uv, "--no-config", "venv", "--python", sys.executable, str(venv)])
            python = venv / "bin/python"
            run([uv, "--no-config", "pip", "install", "--python", str(python), str(artifact)])
            check_commands(venv / "bin")
            assert "watcher" in run([str(python), "-m", "git_harness", "--help"])
            # The fake command/harness test uses only installed package APIs.
            # It cannot import the source checkout or rely on pytest.
            run(
                [
                    str(python),
                    "-c",
                    "\n".join(
                        [
                            "from pathlib import Path",
                            "from importlib import resources, metadata",
                            "scripts = metadata.distribution('git-harness').entry_points",
                            "assert [(s.name, s.value) for s in scripts "
                            "if s.group == 'console_scripts'] == "
                            "[('git-harness', 'git_harness.cli:main')]",
                            "import git_harness",
                            "from git_harness.cli import main",
                            "from git_harness.commands import COMMANDS",
                            "from git_harness.harnesses import HARNESSES",
                            "from git_harness.harnesses.base import ("
                            "Harness, Unsupported, DiscoverRequest)",
                            "assert 'site-packages' in git_harness.__file__",
                            "assert all(isinstance(a, Harness) for a in HARNESSES.values())",
                            "discovered = HARNESSES['codex'].discover("
                            "DiscoverRequest(Path.cwd(), {}))",
                            "assert isinstance(discovered, Unsupported)",
                            "assert resources.files('git_harness.harnesses.pi')"
                            ".joinpath('extension.ts').is_file()",
                            "class FakeCommand:",
                            " name='installed-fake'; description='installed test'",
                            " def configure(self, parser): "
                            "parser.add_argument('--answer', type=int, default=0)",
                            " def execute(self, args): return args.answer",
                            "COMMANDS['installed-fake']=FakeCommand()",
                            "assert main(['installed-fake']) == 0",
                        ]
                    ),
                ]
            )
            # Add only a test runner after checking the runtime-only install.
            # The source test file imports the clean installed distribution.
            run(
                [
                    uv,
                    "--no-config",
                    "pip",
                    "install",
                    "--python",
                    str(python),
                    f"pytest=={package_version('pytest')}",
                ]
            )
            run(
                [
                    str(python),
                    "-m",
                    "pytest",
                    "-q",
                    "-c",
                    os.devnull,
                    str(product / "tests/integration/test_interfaces.py"),
                ]
            )
        version = run(
            [
                uvx,
                "--no-config",
                "--isolated",
                "--from",
                str(wheel),
                "git-harness",
                "--version",
            ]
        )
        assert f"git-harness {package_version_text}" in version
        run([uv, "--no-config", "tool", "install", "--python", sys.executable, str(wheel)])
        check_commands(root / "tool-bin")
        print(
            json.dumps(
                {"artifacts": [wheel.name, sdist.name], "checks": len(commands), "result": "passed"}
            )
        )


if __name__ == "__main__":
    main()
