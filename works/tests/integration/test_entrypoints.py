import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "invocation",
    [[sys.executable, "-m", "git_harness"], [str(Path(sys.executable).parent / "git-harness")]],
)
def test_real_entrypoints_have_same_version_and_help(invocation):
    for option in ("--version", "--help"):
        result = subprocess.run(
            [*invocation, option], env=dict(os.environ), capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0 and "git-harness" in result.stdout
        assert not result.stderr


def test_entrypoint_preserves_cli_error_exit():
    result = subprocess.run(
        [sys.executable, "-m", "git_harness", "timer"],
        env=dict(os.environ),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2 and not result.stdout and "required" in result.stderr
