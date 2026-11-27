import errno
import json
import subprocess
from types import SimpleNamespace

import pytest

from tests.support import native_isolation
from tests.support.native_isolation import IsolationUnavailable, audit_network, confinement_command

pytestmark = pytest.mark.unit


def test_os_confinement_is_explicit_and_never_falls_back_to_unconfined():
    command = ["/python", "native.py"]
    mac = confinement_command("darwin", command, {"sandbox-exec": "/sandbox-exec"})
    assert mac[-2:] == command
    assert "(deny network*)" in mac[2]
    assert "network-bind" in mac[2]
    linux = confinement_command("linux", command, {"unshare": "/unshare"})
    assert linux == [
        "/unshare",
        "--user",
        "--map-root-user",
        "--net",
        "--pid",
        "--fork",
        "--kill-child",
        "--mount-proc",
        "--",
        *command,
    ]
    for platform in ["darwin", "linux", "win32"]:
        with pytest.raises(IsolationUnavailable):
            confinement_command(platform, command, {})


@pytest.mark.parametrize(
    "trace",
    [
        '123 connect(4, {sa_family=AF_INET, sin_addr=inet_addr("127.0.0.1")}, 16) = 0',
        '123 connect(4, {sa_family=AF_INET6, inet_pton(AF_INET6, "::1", &sin6_addr)}, 28) = 0',
        "123 connect(4, {sa_family=AF_INET6, "
        'inet_pton(AF_INET6, "::ffff:127.0.0.1", &sin6_addr)}, 28) = 0',
        '123 connect(4, {sa_family=AF_UNIX, sun_path="/tmp/synthetic/socket"}, 30) = 0',
    ],
)
def test_loopback_and_local_ipc_audit(trace):
    audit_network(trace)


@pytest.mark.parametrize(
    "trace",
    [
        "123 connect(4, {sa_family=AF_INET, "
        'sin_addr=inet_addr("198.51.100.1")}, 16) = -1 ENETUNREACH',
        '123 sendto(4, "x", 1, 0, {sa_family=AF_INET, '
        'sin_addr=inet_addr("192.0.2.53")}, 16) = -1 EPERM',
        "123 connect(4, {sa_family=AF_INET6, "
        'inet_pton(AF_INET6, "2001:db8::1", &sin6_addr)}, 28) = -1 ENETUNREACH',
        "123 connect(4, {sa_family=AF_INET, unrecognized_address}, 16) = -1",
    ],
)
def test_external_attempts_fail_even_if_the_kernel_denied_them(trace):
    with pytest.raises(IsolationUnavailable):
        audit_network(trace)


@pytest.mark.parametrize(
    "returncode,output,accepted",
    [
        (0, json.dumps({"ipv4": errno.EPERM, "ipv6": errno.EPERM, "dns": errno.EPERM}), True),
        (0, json.dumps({"ipv4": 0, "ipv6": errno.EPERM, "dns": errno.EPERM}), False),
        (0, json.dumps({"ipv4": errno.ETIMEDOUT, "ipv6": errno.EPERM, "dns": errno.EPERM}), False),
        (1, "", False),
        (0, "not json", False),
    ],
)
def test_preflight_requires_positive_child_denial_evidence(
    monkeypatch, returncode, output, accepted
):
    def child(arguments, **kwargs):
        assert "198.51.100.1" in arguments[-1]
        return subprocess.CompletedProcess(arguments, returncode, output, "")

    monkeypatch.setattr(native_isolation.subprocess, "run", child)
    if accepted:
        assert native_isolation.verify_isolation()["loopback"] == "connected"
    else:
        with pytest.raises(IsolationUnavailable):
            native_isolation.verify_isolation()


def test_no_client_process_is_launched_before_preflight(monkeypatch, workspace):
    def unavailable():
        raise IsolationUnavailable("gate failed")

    def forbidden(*args, **kwargs):
        pytest.fail("client launch preceded confinement proof")

    monkeypatch.setattr(native_isolation, "verify_isolation", unavailable)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    with pytest.raises(IsolationUnavailable, match="gate failed"):
        native_isolation.run_audited_client(
            ["never-run"],
            environment={},
            cwd=workspace.work,
            trace=workspace.work / "trace",
            strace=None,
        )


@pytest.mark.parametrize("address,accepted", [("127.0.0.1", True), ("198.51.100.1", False)])
def test_audit_enforced_after_client_cleanup(monkeypatch, workspace, address, accepted):
    monkeypatch.setattr(native_isolation, "verify_isolation", lambda: {})
    monkeypatch.setattr(native_isolation, "sys", SimpleNamespace(platform="linux"))
    line = f'connect(4, {{sa_family=AF_INET, sin_addr=inet_addr("{address}")}}, 16) = -1 EPERM'
    tracer = workspace.executable(
        "strace",
        "import pathlib,sys; pathlib.Path(sys.argv[sys.argv.index('-o')+1]).write_text("
        + repr(line)
        + ")",
    )
    arguments = dict(
        environment=workspace.environment,
        cwd=workspace.work,
        trace=workspace.work / "client.trace",
        strace=str(tracer),
    )
    if accepted:
        assert (
            native_isolation.run_audited_client(["synthetic-client"], **arguments).returncode == 0
        )
    else:
        with pytest.raises(IsolationUnavailable, match="non-loopback"):
            native_isolation.run_audited_client(["synthetic-client"], **arguments)
