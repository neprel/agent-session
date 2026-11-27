"""Fail-closed native test confinement. Never used by the runtime package."""

import errno
import ipaddress
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
from pathlib import Path


class IsolationUnavailable(RuntimeError):
    pass


def confinement_command(platform: str, command: list[str], tools: dict[str, str]) -> list[str]:
    if platform == "darwin" and tools.get("sandbox-exec"):
        profile = (
            "(version 1) (allow default) (deny network*) "
            '(allow network-outbound (remote ip "localhost:*")) '
            '(allow network-bind (local ip "localhost:*")) '
            '(allow network-inbound (local ip "localhost:*"))'
        )
        return [tools["sandbox-exec"], "-p", profile, *command]
    if platform == "linux" and tools.get("unshare"):
        return [
            tools["unshare"],
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
    raise IsolationUnavailable("no supported OS network confinement; native execution refused")


def enable_loopback() -> None:
    if sys.platform == "linux":
        import fcntl
        import struct

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as control:
            interface = struct.pack("16sH14x", b"lo", 0)
            state = fcntl.ioctl(control, 0x8913, interface)  # SIOCGIFFLAGS
            flags = struct.unpack("16sH14x", state)[1]
            fcntl.ioctl(control, 0x8914, struct.pack("16sH14x", b"lo", flags | 1))


def verify_isolation() -> dict:
    """Test actual child socket calls; a timeout is never accepted as denial."""
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(2)
        script = f"""
import errno,json,socket
socket.create_connection(('127.0.0.1',{listener.getsockname()[1]}),1).close()
results={{}}
for name,family,kind,address in [
 ('ipv4',socket.AF_INET,socket.SOCK_STREAM,('198.51.100.1',443)),
 ('ipv6',socket.AF_INET6,socket.SOCK_STREAM,('2001:db8::1',443)),
 ('dns',socket.AF_INET,socket.SOCK_DGRAM,('192.0.2.53',53))]:
 try:
  with socket.socket(family,kind) as client:
   client.settimeout(1)
   if kind==socket.SOCK_DGRAM: client.sendto(b'probe',address)
   else: client.connect(address)
 except OSError as exc: results[name]=exc.errno
 else: results[name]=0
print(json.dumps(results))
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            env=dict(os.environ),
            capture_output=True,
            text=True,
            timeout=5,
        )
    if result.returncode:
        raise IsolationUnavailable("loopback/child confinement check failed")
    try:
        outcomes = json.loads(result.stdout)
    except ValueError as exc:
        raise IsolationUnavailable("invalid confinement evidence") from exc
    denied = {errno.EPERM, errno.EACCES, errno.ENETUNREACH, errno.EAFNOSUPPORT}
    if set(outcomes) != {"ipv4", "ipv6", "dns"} or any(v not in denied for v in outcomes.values()):
        raise IsolationUnavailable("non-loopback egress was not demonstrably denied")
    return {"loopback": "connected", "child_denials": outcomes}


def audit_network(trace: str) -> None:
    """Reject attempted external destinations, even when connect was denied."""
    for line in trace.splitlines():
        if "AF_INET" not in line:
            continue
        addresses = re.findall(r'inet_addr\("([^"]+)"\)|inet_pton\(AF_INET6, "([^"]+)"', line)
        if not addresses:
            raise IsolationUnavailable("unrecognized internet socket trace; fail closed")
        for ipv4, ipv6 in addresses:
            address = ipaddress.ip_address(ipv4 or ipv6)
            if not (
                address.is_loopback
                or (
                    address.version == 6 and address.ipv4_mapped and address.ipv4_mapped.is_loopback
                )
            ):
                raise IsolationUnavailable("native client attempted non-loopback connection")


def run_audited_client(
    argv: list[str],
    *,
    environment: dict[str, str],
    cwd: Path,
    trace: Path,
    strace: str | None,
    timeout=20,
) -> subprocess.CompletedProcess:
    verify_isolation()
    if sys.platform != "linux" or not strace:
        raise IsolationUnavailable("audited native client execution requires Linux strace")
    from tests.support.workspace import Processes, Workspace

    with tempfile.TemporaryDirectory(prefix="owned-", dir=cwd) as temporary:
        workspace = Workspace(Path(temporary))
        workspace.work = cwd
        workspace.environment = environment
        owned = Processes(workspace)
        process = owned.spawn(
            [
                strace,
                "-f",
                "-qq",
                "-e",
                "trace=connect,sendto,sendmsg,sendmmsg",
                "-s",
                "256",
                "-o",
                str(trace),
                "--",
                *argv,
            ]
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        finally:
            owned.close()
            if not trace.exists():
                raise IsolationUnavailable("native syscall audit was not produced")
            audit_network(trace.read_text())
    return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)
