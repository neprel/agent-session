# Portable verification

Run from `works/`:

```sh
uv sync --locked --dev
uv run --locked pytest
uv run --locked ruff check src tests
uv run --locked ruff format --check src tests
uv build
```

The default pytest selection runs `unit` and synthetic `integration` tests and
excludes the explicit `native` marker. No native tests exist in AS-002. Future
native gates must select `-m native` explicitly and fail on missing prerequisites
or unexpected skips. AS-017 owns the broader mock-provider/fixture/process test
foundation. No synthetic test result certifies native compatibility.

Every current test runs in a temporary working directory with a newly built
environment, temporary HOME/XDG roots, and an empty controlled PATH. No harness,
tmux, credentials, network endpoint, GPU or model is required. Subprocess checks
use absolute interpreter/entrypoint paths. There are no model calls. Coverage
measures all product modules and branches, with an 85% minimum and no module
exclusions. The thin `__main__` wrapper is checked in subprocesses even though
that subprocess coverage is not merged into the parent coverage report.

| Approved requirement | Current tests | Scope and later evidence |
| --- | --- | --- |
| FEATURE-001 R1/R4 distribution | `integration/test_entrypoints.py`; recorded AS-002 wheel/sdist/uvx install checks | Python package/entrypoints/development isolation; release workflow is later. |
| FEATURE-001 R2/R5 command modules/dispatch | `unit/test_cli.py`, `integration/test_interfaces.py` | All ten help/parser/explicit-unsupported paths, fake command without dispatcher edits. |
| FEATURE-001 R3 errors | `unit/test_cli.py::test_common_error_mapping`, `unit/test_values.py::test_delivery_results_preserve_uncertain_and_deferred_outcomes` | Exit codes and stderr mapping; real transport policy follows AS-004. |
| FEATURE-001 R6 defaults | `unit/test_cli.py`, `unit/test_values.py` | Every current parser default, explicit overrides, required/conflicting options, durations, cron/zone validation, help, environment snapshots/empty/invalid values and fixed policy values. Automatic discovery remains absent until verified. |
| FEATURE-003 R1 adapter extension | `integration/test_interfaces.py` | Complete typed fake harness flow, native unsupported results and parser options from an adapter. No concrete native imports in core. |
| FEATURE-005 R3/R7 portable contracts | `integration/test_interfaces.py` | Repeated text has separate identities, linked tools and typed images/summaries/loss/projection values. Serialization, validation, storage and transaction tests follow AS-008. |
| FEATURE-006 R5 resources | `integration/test_interfaces.py` and AS-002 installed-wheel inspection | Package-relative placeholder resources; no working hooks/plugin/extension claimed. |
| FEATURE-011 R4/R6 layout/test foundation | `integration/test_interfaces.py`, `tests/conftest.py`, pyproject marker/coverage config | Explicit interfaces, isolated default tests, dev-only pytest/coverage/ruff and locked uv environment. Full requirement-to-test map grows with implemented tasks. |

Do not weaken coverage or skip a required test to hide a missing native client.
The source distribution intentionally contains product source/tests/docs/build
files and licenses, not project management task files, probes or user state.
