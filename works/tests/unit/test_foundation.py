import json
import os
import select
import subprocess
import sys
from pathlib import Path

import pytest

from tests.support.clock import FakeClock
from tests.support.workspace import Processes

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[2]


def test_temporary_roots_and_fake_executable_preserve_literal_arguments(workspace, processes):
    fake = workspace.executable(
        "fake-client",
        "import json,os,sys; print(json.dumps({'args':sys.argv[1:],'home':os.environ['HOME']}))",
    )
    literal = "Unicode 世界\n$(false); quoted ' text"
    child = processes.spawn([str(fake), literal])
    stdout, stderr = child.communicate(timeout=5)
    assert child.returncode == 0 and not stderr
    result = json.loads(stdout)
    assert result == {"args": [literal], "home": workspace.environment["HOME"]}
    assert os.environ["PATH"] == str(workspace.bin)
    assert os.environ.get("OPENAI_API_KEY") is None
    assert os.environ.get("TMUX") is None
    assert Path(os.environ["CODEX_HOME"]).is_relative_to(Path(os.environ["HOME"]))
    assert (
        len(
            set(
                workspace.environment[k]
                for k in [
                    "HOME",
                    "XDG_CONFIG_HOME",
                    "XDG_DATA_HOME",
                    "XDG_STATE_HOME",
                    "XDG_CACHE_HOME",
                    "XDG_RUNTIME_DIR",
                    "TMPDIR",
                ]
            )
        )
        == 7
    )


def test_fake_executable_rejects_path_escape(workspace):
    with pytest.raises(ValueError):
        workspace.executable("../escape", "pass")


def test_worker_cleanup_even_when_assertion_fails(workspace):
    owned = Processes(workspace)
    process = owned.spawn([sys.executable, "-c", "import time; time.sleep(3600)"])
    try:
        raise RuntimeError("simulated test failure")
    except RuntimeError:
        owned.close()
    assert process.poll() is not None
    assert process.stdout.closed and process.stderr.closed
    owned.close()  # Teardown is idempotent.


def test_force_cleanup_of_worker_ignoring_termination(workspace, processes):
    owned = processes
    process = owned.spawn(
        [
            sys.executable,
            "-c",
            "import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); "
            "print('ready',flush=True); time.sleep(3600)",
        ]
    )
    assert select.select([process.stdout], [], [], 5)[0]
    assert process.stdout.readline() == b"ready\n"
    owned.close()
    assert process.returncode < 0


def test_clock_rollback_does_not_change_monotonic_deadline(fake_clock):
    initial = fake_clock.now()
    deadline = fake_clock.monotonic() + 10
    fake_clock.sleep(6)
    fake_clock.jump_wall(-3600)
    fake_clock.advance(4)
    assert fake_clock.monotonic() == deadline
    assert fake_clock.now() < initial
    with pytest.raises(ValueError):
        FakeClock().advance(-1)


def test_reusable_fake_adapter_is_independent(fake_harness, workspace):
    from agent_session.harnesses.base import DiscoverRequest, Harness

    assert isinstance(fake_harness, Harness)
    assert fake_harness.discover(DiscoverRequest(workspace.work, {})).session.harness == "fake"


@pytest.mark.parametrize(
    "body",
    [
        "import pytest\ndef test_required(): pytest.skip('unexpected')\n",
        "import pytest\npytest.skip('unexpected collection skip', allow_module_level=True)\n",
    ],
)
def test_unexpected_skip_is_a_failure(workspace, body):
    path = workspace.work / "test_skip.py"
    path.write_text(body)
    environment = dict(
        workspace.environment, PYTHONPATH=str(ROOT), PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"
    )
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-c", os.devnull, "-p", "tests.conftest", str(path)],
        cwd=workspace.work,
        env=environment,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 1 and "1 skipped" in result.stdout
