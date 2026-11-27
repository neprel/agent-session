"""AS-001 disposable macOS startup probe; no prompts or inference.

Run with uv run --no-project python probes/AS-001/probe.py.
Only reads installed executable code. Never uses the user's harness home.
"""

import fcntl
import json
import os
from pathlib import Path
import pty
import select
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import termios
import time

PROFILE = '(version 1) (allow default) (deny network*) (allow network* (remote ip "localhost:*"))'


def main():
    if sys.platform != "darwin" or not shutil.which("sandbox-exec"):
        raise SystemExit("This probe requires macOS sandbox-exec; do not run unconfined.")
    root = Path(tempfile.mkdtemp(prefix="agent-session-AS-001-probe-"))
    print(f"Evidence directory: {root}", flush=True)
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    check = (
        "import socket; "
        f"socket.create_connection(('127.0.0.1',{listener.getsockname()[1]}),2).close(); "
        "\ntry: socket.create_connection(('1.1.1.1',443),2)"
        "\nexcept PermissionError: print('loopback allowed; external IP denied')"
        "\nelse: raise SystemExit('egress denial FAILED')"
    )
    gate = subprocess.run(
        ["sandbox-exec", "-p", PROFILE, sys.executable, "-c", check],
        capture_output=True, text=True, timeout=10,
    )
    listener.close()
    (root / "isolation.txt").write_text(gate.stdout + gate.stderr)
    if gate.returncode or "external IP denied" not in gate.stdout:
        raise SystemExit("Isolation gate failed: " + gate.stdout + gate.stderr)
    print(gate.stdout.strip(), flush=True)
    for name in ("codex", "claude", "opencode", "pi"):
        executable = shutil.which(name)
        if not executable:
            print(json.dumps({"harness": name, "unavailable": True}), flush=True)
            continue
        home = root / name
        work = home / "work"
        work.mkdir(parents=True)
        for folder in (".codex", ".claude", ".pi/agent", ".config", ".local/share", ".local/state", ".cache"):
            (home / folder).mkdir(parents=True, exist_ok=True)
        env = {
            "HOME": str(home), "PATH": "/opt/homebrew/bin:/usr/bin:/bin",
            "TERM": "xterm-256color", "NO_COLOR": "1",
            "CODEX_HOME": str(home / ".codex"),
            "CLAUDE_CONFIG_DIR": str(home / ".claude"),
            "PI_CODING_AGENT_DIR": str(home / ".pi/agent"),
            "XDG_CONFIG_HOME": str(home / ".config"),
            "XDG_DATA_HOME": str(home / ".local/share"),
            "XDG_STATE_HOME": str(home / ".local/state"),
            "XDG_CACHE_HOME": str(home / ".cache"),
            "DISABLE_AUTOUPDATER": "1", "PI_OFFLINE": "1", "PI_TELEMETRY": "0",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
            "CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY": "1",
            "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
            "CLAUDE_CODE_SKIP_KEYCHAIN": "1",
        }
        args = {
            "codex": ["--no-daemon", "--no-alt-screen"],
            "claude": ["--bare", "--strict-mcp-config"],
            "opencode": ["--standalone"],
            "pi": ["--offline", "--no-extensions", "--no-mcp", "--no-skills", "--no-prompt-templates", "--no-context-files"],
        }[name]
        for label, options in (("version", ["--version"]), ("help", ["--help"])):
            result = subprocess.run([executable, *options], cwd=work, env=env,
                                    capture_output=True, text=True, timeout=20)
            (home / f"{label}.txt").write_text(result.stdout + result.stderr)
        master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 40, 120, 0, 0))
        proc = subprocess.Popen(["sandbox-exec", "-p", PROFILE, executable, *args],
                                cwd=work, env=env, stdin=slave, stdout=slave, stderr=slave,
                                start_new_session=True)
        os.close(slave)
        output = bytearray()

        def collect(seconds):
            until = time.monotonic() + seconds
            while time.monotonic() < until:
                if select.select([master], [], [], 0.1)[0]:
                    try:
                        chunk = os.read(master, 65536)
                        if not chunk:
                            return
                        output.extend(chunk)
                        if b"\x1b[6n" in chunk:
                            os.write(master, b"\x1b[1;1R")
                    except OSError:
                        return

        collect(8)
        # Ctrl+C is a normal interactive cancellation/exit path; never type a prompt.
        def interrupt():
            try:
                os.write(master, b"\x03")
            except OSError:
                pass

        if proc.poll() is None:
            interrupt()
        collect(2)
        if proc.poll() is None:
            interrupt()
            collect(2)
        forced = proc.poll() is None
        if forced:
            os.killpg(proc.pid, signal.SIGTERM)
            collect(1)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=3)
        # Clean up any child processes retained in this probe's private group.
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        os.close(master)
        (home / "startup.txt").write_bytes(output)
        summary = {"harness": name, "args": args, "returncode": proc.returncode,
                   "forced_cleanup": forced,
                   "files": sorted(str(p.relative_to(home)) for p in home.rglob("*") if p.is_file())}
        (home / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
