# AS-002 verification evidence

Executor: developer/1. Date: 2026-11-27. OS: Darwin 24.6.0 arm64.
Python: 3.12.13. uv: 0.13.0. Task: `tasks/review/reviewer/1/AS-002.md`
(moves to `tasks/done/developer/` only after independent acceptance).

The owner approved `works/` as product root during execution. Moved active
`src/`, `tests/`, `pyproject.toml`, `uv.lock`, `THIRD_PARTY_NOTICES.md` and product
`.gitignore` there. Created product README/docs, copied the matching owner
LICENSE into `works/`, and preserved both root originals. Removed only the
obsolete developer-created root `.venv`; rebuilt `works/.venv`. No nested Git.
The manager handled specification/task-path changes in separate commits.

## Changes and scope

All ten commands have separate modules implementing the exact Command protocol.
Common parser/dispatch/error handling stays in cli.py; shared worker parser
declarations live in options.py. Explicit registries are the only integration
points. All eight Harness methods have typed requests/results; native adapters
return Unsupported and declare no verified versions or capabilities. A fake
command and fake harness exercise all interface operations plus an added native
flag through those registries, without changing core dispatch.

Portable event/provenance, cursor, projection, loss and ownership values follow
accepted AS-001 boundaries. The neutral model adaptation includes pinned MIT
provenance and complete upstream notice. No native converter was copied.
Default values and package environment settings have one common contract.
Automatic native values remain absent until a later service can verify them.

This foundation deliberately returns exit 4 on valid builtin command execution.
It does not implement registration, message/stdin selection, delivery routing,
workers, history serialization/storage, lifecycle configuration or native
protocols. Those have separate assigned tasks. TypeScript resources are explicit
reserved placeholders, not working plugins/extensions. No native compatibility,
owner proof or portable transaction behavior is claimed from contract types.

## Reproduce

Run every product command from `works/`:

```sh
uv sync --locked --dev --python 3.12
uv run --locked pytest
uv run --locked ruff check src tests
uv run --locked ruff format --check src tests
uv build
uv run --locked python ../probes/AS-002/verify_distribution.py
git diff --check
```

The default suite passed: **226 tests, no skips**, 99.72% measured statement and
branch coverage combined; all 34 measured branches covered. No product module
is excluded. The two-line `__main__` wrapper runs in subprocess entrypoint tests;
its subprocess execution is not merged into parent coverage. Ruff lint and
format checks passed. `uv sync --dev` and locked sync both succeeded; uv.lock
records the complete development/runtime dependency graph. No model SDK was
introduced. Runtime requirements are only watchdog, croniter, unique-namer and
psutil; pytest, pytest-cov and ruff are development-only.

The test suite uses temporary cwd/HOME/XDG roots, a clean environment and an
empty controlled PATH. Entry points use absolute interpreter/executable paths.
No native harness, tmux, credentials, model or network endpoint is required.
AS-017 expands synthetic fixture/mock-provider/process infrastructure.

`uv build` built wheel and sdist successfully. The distribution probe passed
15 checks, including separate clean wheel/sdist installs, console and module
help/version, installed-package imports and resources, explicit native
unsupported outcomes, fake command registration, all nine fake/interface tests
in each clean install, and `uv tool run --isolated --from LOCAL_WHEEL` (uvx).
The clean runtime installs run before adding pytest as a test runner.
Wheel metadata excludes test tools; archive inspection verifies packaged
TypeScript, both licenses and no native JSON templates. Sdist includes tests,
docs and uv.lock, and excludes tasks/probes/agents. A variable-shadowing error
in an intermediate distribution-probe iteration was corrected; its final run
passed. Build/install checks do not publish anything or certify native clients.

See `works/docs/testing.md` for the initial requirement-to-test map and
`works/docs/interfaces.md` for extension and contract boundaries. Release gates,
native version provisioning, all-route acceptance and CI belong to later tasks.
