# AS-018 interim infrastructure inspection

Reviewer: reviewer/1. Date: 2026-11-27.
Snapshot: `9f54116aa285fd106b9965880c5db9ddf311bfd2`.
Scope: interim inspection only. AS-018 remains open; no acceptance/task move.
Snapshot names below are historical and precede owner-approved AS-019.

## Independent evidence

Archived the exact tracked revision into a disposable checkout. All source
commands below ran from its works/ directory; shared product files/branch were
not changed. Initial extraction used the older system Python, which lacks the
filter argument; retried successfully with uv-managed Python 3.12.

- `uv sync --locked --dev --python 3.12`: passed.
- `uv run --locked pytest`: 307 passed, zero skips, one native deselected;
  99.72% product coverage and all 34 product branches covered.
- Ruff lint and formatting passed (63 files).
- `uv run --locked python scripts/lint_workflows.py`: passed.
- `uv run --locked python scripts/check_native_acceptance.py`: correctly
  exited 4, listing missing lifecycle/delivery/resume and 12 migration routes.
- All five external action pins independently matched the recorded upstream
  Git tags using git ls-remote. Workflow calls use complete pinned SHAs.

[CI run 45996461223](https://github.com/neprel/agent-session/actions/runs/45996461223)
completed for the exact snapshot. Independently fetched job results: all six
Linux/macOS Python 3.11/3.12/3.13 portable jobs and workflow lint passed. All four
real Linux native foundation jobs passed; downloaded each sanitized report and
verified one test, no failures/errors/skips, suite foundation and exact pins:
Codex 0.144.4, Claude 2.1.209, OpenCode 2.0.23, Pi 0.80.6, Node 22.19.0.
Inspected the Claude foundation log: child loopback connected; external IPv4,
IPv6 and DNS operations returned ENETUNREACH (101), then one native test passed.
The source runs clients under syscall audit after preflight inside namespaces.
This closes the AS-017 Linux provisioning/version foundation evidence gap.
It does not establish native protocol/adapter compatibility.

CI overall is correctly red: the four required native acceptance jobs fail
at the incomplete-manifest check. Their first multiline step is labelled
uv sync --locked --dev in GitHub, but also runs check_native_acceptance.py;
this is not evidence that dependency synchronization failed.

[Release PR build-only run 45996461203](https://github.com/neprel/agent-session/actions/runs/45996461203)
passed at the same exact snapshot: identity, six portable jobs, lint, four
foundation jobs and artifact build passed; native acceptance and publish were
skipped for the PR event. No publication occurred. The earlier manual-dispatch
run 45995736421 failed at older revision 6eaa2cdf; a successful current/final
manual-dispatch run remains to be recorded before full task acceptance.

## Source inspection and findings

Inspected all four workflows, action pins, native launcher/confinement changes,
acceptance manifest gate, release identity/owner guards, report sanitizer,
distribution checker, policy tests and owner publishing guide against approved
FEATURE-011 R8/R9. No new blocking infrastructure defect found in this scope.

The portable matrix runs locked tests/lint/coverage/build/install checks from
works/. Reports retain counts/coverage/pin hashes, not transcript or request
content. No publishing secrets or id-token permission exists in ordinary jobs.
The publish job requires all exact-run gates and pypi environment, alone obtains
OIDC, downloads only the tested distributions from its run, does not check out
or execute project source, and keeps attestations/no-skip-existing. Tag identity,
default-branch ancestry and owner safeguards are explicitly gated. PR/manual
paths cannot publish. Missing native tests are not replaced with version gates.

Outstanding requirements: implement and independently verify the full native
adapter/all-route matrix; run successful build-only manual dispatch at the final
revision; finish the separately owner-approved naming change and publisher
documentation/metadata consistency; verify final release safeguards without
tags/publication. Current hard publication block is intentional pending the
name decision in this historical snapshot. AS-019 supersedes that naming state.
Owner setup/publication remain separate actions. No task was accepted or moved,
no product/current specification changed, no new threads or agents created.
