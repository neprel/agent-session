# AS-017 independent review

Reviewer: reviewer/1. Date: 2026-11-27.
Exact submission: `1dd3641487ef1f874a1194f1f8636f9403a08211`.
Submitted product, probes and task matched that revision before review edits.
AS-002 dependency is accepted in tasks/done/developer/AS-002.md.

## Reproduction and results

Executed from `works/`:

- `uv sync --locked --dev`: passed.
- `uv run --locked pytest`: 294 passed, zero skips, one deliberately native
  test deselected; 99.72% product coverage, all 34 product branches covered.
  Includes all 31 provider protocol tests and unexpected-skip regressions.
- `uv run --locked ruff check src tests scripts`: passed.
- `uv run --locked ruff format --check src tests scripts`: 57 files formatted.
- `uv build`: wheel/sdist built successfully.
- `uv run --locked python scripts/verify_distribution.py`: all 15 checks passed,
  including clean wheel/sdist installs, installed fake-interface tests, native
  resources/notices and local-wheel uvx. Both artifacts exclude tests/support,
  fixture/provisioning code and native locks.
- `uv run --locked python scripts/run_native.py --isolation-only`: exit 0;
  real child loopback connected; IPv4, IPv6 and DNS operations denied with EPERM.
- `uv run --locked python scripts/run_native.py --manifest
  /tmp/AS017-nonexistent-manifest --client codex`: exit 4 with explicit macOS
  audit-unavailable result after preflight; no native client launched.
- Independent upstream parsing of all six fixture files: succeeded, including
  tools/results, images/context, compaction and the selected Pi branch. Used
  the exact pinned source independently hash-verified during AS-001 review.
  Fixture hashes matched their committed manifest. The first review invocation
  used an incorrect upstream OpenCode function name; reran with its actual
  parse_session interface and all six completed.
- `git diff --check`: passed.

## Inspection and acceptance criteria

Inspected support workspace/process/clock/fake harness/fixture helpers, provider
and protocol tests, native isolation/audit/preflight, provisioning and native
entry/version test, integrity locks, package policy and requirement map against
FEATURE-011. No runtime dependency or product implementation was changed.

The default suite uses clean temporary homes/config/state/work roots and a
controlled PATH, without native clients or model credentials. Reusable helpers
cover literal fake executables, time rollback, forced process-group cleanup,
shared adapters and immutable four-harness fixtures. The provider implements
tested JSON/SSE text/tool/error/timeout/malformed paths for Chat Completions,
Responses and Messages, with bounded requests, local dummy credentials and
cleanup. Required skip failures are tested. MIT provenance/notice is retained.

Native execution constructs confinement before preflight/client invocation;
missing tools/proof fail explicitly. Linux namespaces, child egress preflight
and strace audit are implemented and unit-tested; actual Linux execution and
npm client installation were not verified on this macOS host. Documentation
correctly leaves those real-runner gates to AS-018 and refuses unauditable macOS
client execution. Exact Node/archive pins and transitive public-registry npm
integrity locks are present; installation uses private new roots and no lifecycle
scripts or inherited provider credentials. No installed user client fallback.

All six foundation acceptance criteria are satisfied; no blocking defect found.
Accept AS-017. This does not certify Linux runner execution, native adapter
support, imported-context replay, same-session append or any migration route.
AS-018 and adapter/integration work must establish those mandatory gates before
support/release claims. No requirements or acceptance criteria were changed.
