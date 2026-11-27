# Portable verification

Run from `works/`:

```sh
uv sync --locked --dev
uv run --locked pytest
uv run --locked ruff check src tests scripts
uv run --locked ruff format --check src tests scripts
uv build
uv run --locked python scripts/verify_distribution.py
```

The default pytest selection runs `unit` and synthetic `integration` tests and
excludes the explicit `native` marker. The native foundation currently checks
the provisioned executable version/integrity, not adapter compatibility. Missing
native prerequisites fail instead of skipping. Both runtime and collection
skips fail the session; deliberate deselection of native tests in the default
suite is not a skip. No synthetic test result certifies native compatibility.

Every current test runs in a temporary working directory with a newly built
environment, temporary HOME/XDG roots, and an empty controlled PATH. No harness,
tmux, credentials, external endpoint, GPU or model is required. The tests start
their own deterministic loopback provider. Subprocess checks
use absolute interpreter/entrypoint paths. There are no model calls. Coverage
measures all product modules and branches, with an 85% minimum and no module
exclusions. The thin `__main__` wrapper is checked in subprocesses even though
that subprocess coverage is not merged into the parent coverage report.

| Approved requirement | Current tests | Scope and later evidence |
| --- | --- | --- |
| FEATURE-001 R1/R4 distribution | `integration/test_entrypoints.py`; `scripts/verify_distribution.py` | Clean wheel/sdist installs, installed fake interface tests, local-wheel uvx, resources/licenses and repository-only test exclusion; release workflow is later. |
| FEATURE-001 R2/R5 command modules/dispatch | `unit/test_cli.py`, `integration/test_interfaces.py` | All ten help/parser/explicit-unsupported paths, fake command without dispatcher edits. |
| FEATURE-001 R3 errors | `unit/test_cli.py::test_common_error_mapping`, `unit/test_values.py::test_delivery_results_preserve_uncertain_and_deferred_outcomes` | Exit codes and stderr mapping; real transport policy follows AS-004. |
| FEATURE-001 R6 defaults | `unit/test_cli.py`, `unit/test_values.py` | Every current parser default, explicit overrides, required/conflicting options, durations, cron/zone validation, help, environment snapshots/empty/invalid values and fixed policy values. Automatic discovery remains absent until verified. |
| FEATURE-003 R1 adapter extension | `integration/test_interfaces.py` | Complete typed fake harness flow, native unsupported results and parser options from an adapter. No concrete native imports in core. |
| FEATURE-005 R3/R7 portable contracts | `integration/test_interfaces.py` | Repeated text has separate identities, linked tools and typed images/summaries/loss/projection values. Serialization, validation, storage and transaction tests follow AS-008. |
| FEATURE-006 R5 resources | `integration/test_interfaces.py` and AS-002 installed-wheel inspection | Package-relative placeholder resources; no working hooks/plugin/extension claimed. |
| FEATURE-011 R4/R6 layout/test foundation | `integration/test_interfaces.py`, `tests/conftest.py`, pyproject marker/coverage config | Explicit interfaces, isolated default tests, dev-only pytest/coverage/ruff and locked uv environment. Full requirement-to-test map grows with implemented tasks. |
| FEATURE-011 R1/R6 fake time/processes/corpus | `unit/test_foundation.py`, `unit/test_fixture_corpus.py` | Literal fake executables, clean homes, bounded forced worker cleanup, wall rollback versus monotonic time, immutable four-harness native corpus and explicit lifecycle/failure scenarios. Actual product parsing follows adapter tasks. |
| FEATURE-011 R7 provider | `unit/test_offline_provider.py` | Chat Completions, Responses and Anthropic Messages JSON/SSE, tools/results, terminal events, bounded/strict requests, query matching, errors/timeouts/malformed streams, local-only dummy keys and cleanup. No model inference. |
| FEATURE-011 R7 confinement | `unit/test_native_isolation.py`, `scripts/run_native.py --isolation-only` | Unit gate/audit tests plus host preflight: child loopback succeeds, IPv4/IPv6/DNS egress is denied; timeouts do not count as proof. Actual Linux namespace/strace gates remain runner verification work. |
| FEATURE-011 R7 pinned provisioning | `unit/test_provisioning.py`, `native/test_pinned_version.py`, `scripts/provision_native.py` | Exact Node hashes and npm integrity locks, no install scripts or inherited credentials, fail-closed native version gate. Provisioned client execution is opt-in and not a resume/delivery acceptance pass. |

Do not weaken coverage or skip a required test to hide a missing native client.
Both wheel and source distribution exclude repository-only `tests/` and
`scripts/`, including provider, fixtures, native locks and provisioning code.
The sdist retains product source/docs/build metadata, uv.lock and licenses.
This changes the initial AS-002 sdist policy; its historical probe is preserved.

## Reusable support

`Workspace` creates independent HOME, native config, XDG state/cache/runtime,
temporary and work directories and a controlled executable PATH. `Processes`
owns private process groups, bounds shutdown, forces cleanup of remaining group
members, and closes pipes in fixture teardown. `FakeClock` separates monotonic
and UTC wall time. `FakeHarness` is shared by unit/integration tests; it never
starts a native process. `fixtures.materialize` verifies manifest hashes and
refuses overwrite. All recorded requests and fixture contents must be synthetic.

The provider adapts the reviewed MIT session-migrate implementation. The complete
notice is in `tests/support/LICENSE.session-migrate`. Supply `Step` values to
script text, tool call, error, timeout or malformed-event responses. Only exact
Chat/Responses/Messages paths (with optional `/v1`) are accepted; only the
Messages `beta=true` query is supported. Requests require JSON framing, a model,
valid conversation shape, finite JSON and bounded size/count/time. If credentials
are supplied, only the local dummy `local-dummy` is accepted. Call
`provider.assert_clean()` before accepting a native run. This is a tested wire
subset, not an implementation of every provider API feature.

## Explicit native entry point

Provision first on a **clean Linux x86_64 runner**, with network access for
dependency installation only. `unshare` (util-linux), user/PID/network namespace
support and `strace` are OS prerequisites; use hosted-runner provisioning in
AS-018. No preinstalled harness, local model, account or key is required.

```sh
uv sync --locked --dev
uv run --locked python scripts/provision_native.py --destination /tmp/NEW_NATIVE_ROOT --client codex
uv run --locked python scripts/run_native.py --manifest /tmp/NEW_NATIVE_ROOT/manifest.json --client codex
```

Choose `codex`, `claude`, `opencode` or `pi`. Exact candidate pins are Codex
0.144.4, Claude 2.1.209, OpenCode 2.0.23 and Pi 0.80.6. Node 22.19.0 downloads
from nodejs.org with committed SHA-256 values. Per-client npm lockfiles pin
transitive public-registry integrity. `npm ci --ignore-scripts` installs only
under a new private destination; provisioning executes no harness. Existing
destinations are refused, including partial attempts. Native execution verifies
the lock/binary hashes and versions again under confinement.

The launcher constructs a fresh environment, then enters isolated user, PID
and network namespaces. It enables only loopback and tests actual child socket
calls **before** invoking any harness. A PID namespace also bounds detached
descendants: killing its init process removes the contained processes. Each
native client runs under `strace -f` for connect/sendto/sendmsg/sendmmsg; attempted
external IPv4/IPv6/DNS destinations fail even when the kernel rejected them.
Unknown internet-address trace forms fail closed. Missing namespaces, audit
tools, manifests, binaries or tests are failures, never passed skips.

On macOS, `uv run --locked python scripts/run_native.py --isolation-only`
verifies the loopback-bind/outbound policy and child denial using sandbox-exec.
Audited native client execution is unavailable there and is explicitly refused;
no installed user client is used as a fallback. The macOS Node prerequisite can
be checked with `provision_native.py --destination NEW_PATH --node-only`.
Linux provisioning and audited execution still require real runner verification;
local macOS preflight success does not establish Linux or native adapter support.

Future adapter/integration tasks add native hook/ownership/delivery/resume and
all 12 cross-harness gates to this entry point. The current version check cannot
satisfy those release requirements. A fixed provider response alone does not
prove imported context, same-session append or safe lifecycle cleanup.
