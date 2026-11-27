"""Initial portable isolation; native execution is never implicit."""

import os
from pathlib import Path

import pytest

from tests.support.clock import FakeClock
from tests.support.offline_provider import offline_provider
from tests.support.workspace import Processes, Workspace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKIPPED = pytest.StashKey[bool]()
COLLECTION_SKIPS = []


def pytest_sessionstart(session):
    COLLECTION_SKIPS.clear()


def pytest_collectreport(report):
    if report.skipped:
        COLLECTION_SKIPS.append(report.nodeid)


def pytest_addoption(parser):
    parser.addoption("--native-manifest", type=Path)
    parser.addoption("--native-client", choices=("codex", "claude", "opencode", "pi"))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    if report.skipped:
        item.config.stash[SKIPPED] = True


def pytest_sessionfinish(session, exitstatus):
    if session.config.stash.get(SKIPPED, False) or COLLECTION_SKIPS:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED


@pytest.fixture
def workspace(tmp_path):
    return Workspace(tmp_path)


@pytest.fixture(autouse=True)
def isolated_environment(workspace, monkeypatch):
    for key in tuple(os.environ):
        monkeypatch.delenv(key)
    for key, value in workspace.environment.items():
        monkeypatch.setenv(key, value)
    monkeypatch.chdir(workspace.work)


@pytest.fixture
def processes(workspace):
    owned = Processes(workspace)
    try:
        yield owned
    finally:
        owned.close()


@pytest.fixture
def fake_clock():
    return FakeClock()


@pytest.fixture
def provider():
    with offline_provider() as instance:
        yield instance


@pytest.fixture
def fake_harness():
    from tests.support.fake_harness import FakeHarness

    return FakeHarness()
