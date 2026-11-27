"""Disposable native CLI discovery/exit checks using a pinned upstream stub.

Usage: uv run --no-project python probes/AS-001/offline_smoke.py PROVIDER.py
The provider must be the reviewed session-migrate tests/offline_provider.py.
This is research evidence, not the AS-017 acceptance suite.
"""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

from probe import PROFILE


def main():
    if sys.platform != "darwin":
        raise SystemExit("Requires macOS sandbox-exec")
    source = Path(sys.argv[1])
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != "7d32864357b473b12296022342afd2810583c75a8d39bc6875528c45957c30cb":
        raise SystemExit("Provider differs from the reviewed AS-001 source")
    print("provider sha256:", digest, flush=True)
    spec = importlib.util.spec_from_file_location("offline_provider", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = Path(tempfile.mkdtemp(prefix="agent-session-AS-001-offline-"))
    print("Evidence directory:", root, flush=True)
    with module.offline_provider("AS001_FIXED_REPLY") as provider:
        port = provider.server_port
        gate = subprocess.run(
            ["sandbox-exec", "-p", PROFILE, sys.executable, "-c",
             f"import socket; socket.create_connection(('127.0.0.1',{port}),2).close()\n"
             "try: socket.create_connection(('1.1.1.1',443),2)\n"
             "except PermissionError: print('loopback allowed; external IP denied')\n"
             "else: raise SystemExit(1)"],
            capture_output=True, text=True, timeout=10,
        )
        if gate.returncode or "external IP denied" not in gate.stdout:
            raise SystemExit("Isolation check failed")
        (root / "isolation.txt").write_text(gate.stdout)
        for name in ("codex", "claude", "pi", "opencode"):
            executable = shutil.which(name)
            home = root / name
            work = home / "work"
            work.mkdir(parents=True)
            for p in (".codex", ".claude", ".pi/agent", ".config", ".local/share", ".local/state", ".cache", "tmp"):
                (home / p).mkdir(parents=True, exist_ok=True)
            env = {
                "HOME": str(home), "PATH": "/opt/homebrew/bin:/usr/bin:/bin", "TERM": "dumb", "NO_COLOR": "1",
                "CODEX_HOME": str(home / ".codex"), "CLAUDE_CONFIG_DIR": str(home / ".claude"),
                "PI_CODING_AGENT_DIR": str(home / ".pi/agent"),
                "XDG_CONFIG_HOME": str(home / ".config"), "XDG_DATA_HOME": str(home / ".local/share"),
                "XDG_STATE_HOME": str(home / ".local/state"), "XDG_CACHE_HOME": str(home / ".cache"),
                "TMPDIR": str(home / "tmp"), "DISABLE_AUTOUPDATER": "1", "DISABLE_TELEMETRY": "1",
                "DISABLE_ERROR_REPORTING": "1", "PI_OFFLINE": "1", "PI_TELEMETRY": "0",
                "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "CLAUDE_CODE_SKIP_KEYCHAIN": "1",
                "OPENCODE_DISABLE_AUTOUPDATE": "true",
            }
            base = f"http://127.0.0.1:{port}"
            prompt = "AS001_SYNTHETIC_DISCOVERY"
            if name == "codex":
                (home / ".codex/config.toml").write_text(
                    'model = "fixture-model"\nmodel_provider = "fixture"\n'
                    '[model_providers.fixture]\nname = "AS001 loopback"\n'
                    f'base_url = "{base}/v1"\nenv_key = "FIXTURE_API_KEY"\n'
                    'wire_api = "responses"\nrequires_openai_auth = false\n'
                )
                env["FIXTURE_API_KEY"] = "local-dummy"
                args = ["exec", "--skip-git-repo-check", "--json", prompt]
            elif name == "claude":
                env.update(ANTHROPIC_API_KEY="local-dummy", ANTHROPIC_BASE_URL=base)
                args = ["--bare", "--strict-mcp-config", "--print", "--output-format", "stream-json", "--verbose", "--model", "claude-haiku-4-5-20251001", prompt]
            elif name == "pi":
                (home / ".pi/agent/models.json").write_text(json.dumps({"providers": {"fixture": {
                    "baseUrl": base + "/v1", "api": "openai-completions", "apiKey": "local-dummy",
                    "models": [{"id": "fixture-model", "name": "Fixture", "input": ["text"], "contextWindow": 32768, "maxTokens": 4096}],
                }}}))
                args = ["--offline", "--no-extensions", "--no-mcp", "--no-skills", "--no-prompt-templates", "--no-context-files", "--print", "--mode", "json", "--model", "fixture/fixture-model", prompt]
            else:
                config = work / "opencode.json"
                config.write_text(json.dumps({"warming": False, "disabled_providers": ["opencode"], "providers": {"fixture": {
                    "package": "@opencode/ai/providers/openai-compatible", "settings": {"apiKey": "local-dummy", "baseURL": base + "/v1"},
                    "models": {"test": {"limit": {"context": 64000, "output": 4096}}},
                }}}))
                env["OPENCODE_CONFIG"] = str(config)
                args = ["run", "--standalone", "--model", "fixture/test", "--format", "json", prompt]
            start = len(provider.requests)
            proc = subprocess.Popen(["sandbox-exec", "-p", PROFILE, executable, *args], cwd=work, env=env,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                                    start_new_session=True)
            timed_out = False
            try:
                out, err = proc.communicate(timeout=35)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(proc.pid, signal.SIGKILL)
                out, err = proc.communicate(timeout=5)
            finally:
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            (home / "stdout.txt").write_bytes(out)
            (home / "stderr.txt").write_bytes(err)
            requests = provider.requests[start:]
            (home / "requests.json").write_text(json.dumps(requests))
            summary = {"harness": name, "args": args, "returncode": proc.returncode,
                       "timeout": timed_out, "request_paths": [p for p, _ in requests],
                       "marker_received": any(prompt in json.dumps(b) for _, b in requests),
                       "reply_returned": b"AS001_FIXED_REPLY" in out,
                       "files": sorted(str(p.relative_to(home)) for p in home.rglob("*") if p.is_file())}
            (home / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
            print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
