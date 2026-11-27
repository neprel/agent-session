"""Initial portable isolation; native execution is never implicit."""

import os
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def isolated_environment(tmp_path, monkeypatch):
    for key in tuple(os.environ):
        monkeypatch.delenv(key)
    for key in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
        folder = tmp_path / key.lower()
        folder.mkdir()
        monkeypatch.setenv(key, str(folder))
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    monkeypatch.setenv("PATH", str(bin_dir))
    monkeypatch.setenv("TERM", "dumb")
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
