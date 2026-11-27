# Git Harness

Deterministic CLI for local coding agent sessions. Product development runs
from this `works/` directory; project specifications and task records live in
the parent repository.

This foundation build defines the CLI and typed adapter contracts. All ten
commands provide help and validate arguments. Execution currently reports
`unsupported` (exit 4); registration, delivery, workers, history storage and
native integration are implemented by subsequent tasks. No native harness
version is advertised as supported yet. The packaged TypeScript resources are
reserved placeholders and do not install working integrations.

```sh
uv sync --locked --dev
uv run --locked git-harness --help
uv run --locked python -m git_harness watcher --help
uv run --locked pytest
uv run --locked ruff check src tests scripts
uv build
uv run --locked python scripts/verify_distribution.py
uvx --from ./dist/git_harness-0.1.0-py3-none-any.whl git-harness --version
```

Installing `git-harness` also enables native `git harness` through Git's external
command discovery. Both forms work outside a Git repository. No Git alias or
additional wrapper is installed. For example, after `uv tool install git-harness`,
run `git-harness --version` or `git harness --version`.

Python 3.11 or newer is required. The runtime dependencies are watchdog,
croniter, unique-namer and psutil; there is no model SDK or inference dependency.
Tests, coverage and lint tools are development dependencies only. No publication
is authorized by a local build.

Run `git-harness COMMAND --help` for each command's options and defaults.
Target commands default to `--target .` and a `15s` operation budget, except
`stop` which defaults to `5s`. `config` and `prime` reject target options.
`--verbose` and `--quiet` conflict. Durations require ms, s, m or h; only
`--unavailable-timeout` accepts zero and `never`. Watcher paths are required;
timers require exactly one interval or five-field cron expression.

The only package-defined public environment settings are `GIT_HARNESS_DIR`
(`.harness`), `GIT_HARNESS_FILE` (`agent.json`) and
`GIT_HARNESS_HISTORY_MAX_SIZE` (`256K`, 262144 bytes). Empty/invalid settings
fail with exit 2. Names must be single components; history sizes are positive
integer bytes or K/M binary units. Values are snapshotted at CLI startup.
Native discovery defaults are intentionally unresolved until execution has
verified a session; no endpoint, native ID or local timezone is guessed by
the parser.

Exit codes: 0 success, 1 failure, 2 invalid arguments/configuration, 3 confirmed
unavailable or deferred, 4 unsupported, 5 timeout/uncertain delivery, 6 conflict.
Transport acceptance does not prove that a receiving agent processed a message.

See [interfaces](docs/interfaces.md), [testing](docs/testing.md) and
[third-party notices](THIRD_PARTY_NOTICES.md). Portable model adaptation retains
session-migrate's MIT notice; native converters are not runtime dependencies.

The repository-only test foundation supplies synthetic native histories,
fake time/executables/processes and a deterministic loopback protocol provider.
Tests, provider, provisioning scripts and native locks are excluded from both
wheel and sdist. The explicit native entry point fails closed on missing
isolation or prerequisites; see the testing guide for candidate pins and the
current macOS/Linux verification limits. No native support claim follows from
the portable suite or a version-only gate.
