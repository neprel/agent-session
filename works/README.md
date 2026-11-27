# agent-session

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
uv run --locked agent-session --help
uv run --locked python -m agent_session watcher --help
uv run --locked pytest
uv run --locked ruff check src tests
uv build
uvx --from ./dist/agent_session-0.1.0-py3-none-any.whl agent-session --version
```

Python 3.11 or newer is required. The runtime dependencies are watchdog,
croniter, unique-namer and psutil; there is no model SDK or inference dependency.
Tests, coverage and lint tools are development dependencies only. No publication
is authorized by a local build.

Run `agent-session COMMAND --help` for each command's options and defaults.
Target commands default to `--target .` and a `15s` operation budget, except
`stop` which defaults to `5s`. `config` and `prime` reject target options.
`--verbose` and `--quiet` conflict. Durations require ms, s, m or h; only
`--unavailable-timeout` accepts zero and `never`. Watcher paths are required;
timers require exactly one interval or five-field cron expression.

The only package-defined public environment settings are `AGENT_SESSION_DIR`
(`.session`), `AGENT_SESSION_FILE` (`agent.json`) and
`AGENT_SESSION_HISTORY_MAX_SIZE` (`256K`, 262144 bytes). Empty/invalid settings
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
