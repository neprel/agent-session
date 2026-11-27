"""Disposable configuration roots, literal fake executables and owned processes."""

import os
import signal
import subprocess
import sys
from contextlib import suppress
from pathlib import Path


class Workspace:
    def __init__(self, root: Path):
        self.root = root
        self.environment = {}
        for key in (
            "HOME",
            "XDG_CONFIG_HOME",
            "XDG_DATA_HOME",
            "XDG_STATE_HOME",
            "XDG_CACHE_HOME",
            "XDG_RUNTIME_DIR",
            "TMPDIR",
        ):
            folder = root / key.lower()
            folder.mkdir(parents=True, mode=0o700)
            self.environment[key] = str(folder)
        self.bin = root / "bin"
        self.bin.mkdir()
        self.work = root / "work"
        self.work.mkdir()
        self.environment.update(PATH=str(self.bin), TERM="dumb", NO_COLOR="1")
        for key, relative in (
            ("CODEX_HOME", ".codex"),
            ("CLAUDE_CONFIG_DIR", ".claude"),
            ("PI_CODING_AGENT_DIR", ".pi/agent"),
        ):
            folder = Path(self.environment["HOME"]) / relative
            folder.mkdir(parents=True, mode=0o700)
            self.environment[key] = str(folder)

    def executable(self, name: str, body: str) -> Path:
        if not name or Path(name).name != name or name in {".", ".."}:
            raise ValueError("fake executable requires a single filename")
        path = self.bin / name
        # No shell evaluation or dependency on the caller's PATH.
        path.write_text(f"#!{sys.executable}\n{body}\n")
        path.chmod(0o700)
        return path


class Processes:
    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        self.children: list[subprocess.Popen] = []

    def spawn(self, argv: list[str], **kwargs) -> subprocess.Popen:
        process = subprocess.Popen(
            argv,
            cwd=self.workspace.work,
            env=self.workspace.environment,
            start_new_session=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **kwargs,
        )
        self.children.append(process)
        return process

    def close(self):
        for process in reversed(self.children):
            # Signal the private group even if its leader already exited.
            with suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGTERM)
            try:
                process.communicate(timeout=1)
            except subprocess.TimeoutExpired:
                with suppress(ProcessLookupError):
                    os.killpg(process.pid, signal.SIGKILL)
                process.communicate(timeout=3)
            with suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream is not None:
                    stream.close()
