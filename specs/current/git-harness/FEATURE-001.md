# CLI and distribution

## R1 - Runtime

Use Python >=3.11, uv, `works/pyproject.toml` and a `works/src/` layout. Distribution and executable: `git-harness`; import package: `git_harness`. Provide a console entry point and `python -m git_harness`. Use watchdog, croniter, unique-namer and psutil. Use the standard library for other operations unless a new dependency is approved. Use session-migrate source as a reference, not a required runtime dependency by default. Keep `works/uv.lock` for reproducible development. Use a standard PEP 517 build backend. Build a wheel and source distribution.

The console entry point is:

```toml
[project.scripts]
git-harness = "git_harness.cli:main"
```

Support `uvx git-harness`, `uv tool install git-harness`, `git-harness` and `git harness`. Use Git's native external command discovery; add no Git alias or wrapper script. The standalone utility and Git subcommand must work outside Git repositories. Test both from locally built distributions before publication. Do not retain compatibility aliases or legacy configuration names.

## R2 - CLI contract

All target commands accept `--target PATH` (default `.`), `--timeout DURATION` (15s per transport operation unless stated otherwise), `--verbose/-v`, `--quiet/-q`, `--help/-h`. Reject conflicting verbosity flags. Root accepts `--version` and `--help`; each command has help. Duration syntax: positive number with ms, s, m or h; allow zero and `never` only for unavailability timeout. Reject invalid or negative values. Options are parsed as data, not shell source.

| Command | Additional parameters | Result |
|---|---|---|
| config | --config-dir PATH (.), --harness H (repeatable, default all), --dry-run | Install integration files and managed instructions |
| prime | none | Short Markdown usage on stdout |
| init | --harness H, --session ID, --claude-socket PATH, --opencode-url URL, --pi-socket PATH, --tmux-pane ID, --tmux-socket PATH, --no-tmux, internal --hook H | Register current or explicitly identified session; print target and agent ID |
| check | --json | Read-only session, transport, trigger and history report |
| run | --harness H (saved if absent), --print | Start or resume interactive harness; print mode does not write or launch |
| stop | --agent-id ID, --session ID, --watcher SELECTOR, --timer SELECTOR, --timeout DURATION (5s), internal --hook H | Stop owned triggers and clean temporary resources; preserve history |
| sync | --harness H (current), --session ID, --dry-run, --json, internal --hook H | Checkpoint history and prepare requested native session |
| message | optional positional MESSAGE (stdin if absent), --from PATH (absent) | Submit one message and exit |
| watcher | --path GLOB (repeatable, required), --ignore GLOB (repeatable), --events TYPES (all), --debounce 10s, --max-wait 60s, --message TEXT | Monitor and send filesystem batches |
| timer | exactly one of --cron EXPR or --every DURATION, --timezone ZONE (local), --message TEXT | Send scheduled ticks |

Watcher and timer also accept `--name NAME` (optional), `--background/-b` (off), `--log-file PATH` (none), `--check-interval 30s`, `--unavailable-timeout 10m` (0 or never also valid). Config and prime do not accept target options. Config uses current directory for AGENTS.md. H is codex, claude, opencode or pi. Do not expose a generic transport override. See respective features for semantics.

## R3 - Results

Exit 0: operation succeeded, no change necessary, or identical trigger already running. Exit 1: other failure. Exit 2: invalid arguments/configuration. Exit 3: confirmed unavailable. Exit 4: unsupported capability. Exit 5: timeout or uncertain delivery (do not retry blindly). Exit 6: conflict. A `check` returns 3 for confirmed offline, 5 for unknown availability, and 0 for confirmed reachable. JSON results use stable named fields; errors include a short code and message on stderr. `run` returns the harness exit status if launched. A successful background command means the worker acquired its lock and published its record. Acceptance by a transport is not proof of inference or task completion.

## R4 - Distribution checks

From `works/`, `uv sync --dev`, `uv run pytest`, `uv build` MUST work. Test install from the built wheel in an isolated environment. Verify `uvx` invocation from a local wheel or test index. Do not publish until the owner approves. Verify distribution name availability before release; do not silently rename.
## R5 - Command interface

Each of the ten commands MUST implement the same typed Command protocol in commands/base.py. Use these members:

```python
class Command(Protocol):
    name: str
    description: str
    def configure(self, parser: ArgumentParser) -> None: ...
    def execute(self, args: Namespace) -> int: ...
```

Define command-specific parameters in its module. Define shared options once in the CLI layer. Register implementations explicitly in commands/__init__.py. The CLI dispatches only through the common interface. Command modules call shared services and do not import concrete harness packages. Keep argparse Namespace out of shared services and harness implementations. Pass typed request values to those interfaces. Use the same error mapping for all commands. Test a fake command with the common dispatcher. Add a command without changes to the dispatcher. Do not add command logic to cli.py.

## R6 - Defaults contract

Use the following defaults when the user omits an option. An absent value is not an empty string. Reject invalid explicit values. Boolean flags are false unless stated otherwise. Show applicable defaults in command help. Resolve automatic values at execution time. Do not invent discovery values.

| Scope | Parameter | Default if omitted |
|---|---|---|
| init, check, run, stop, sync, message, watcher, timer | --target | `.` |
| Same target commands except stop | --timeout | `15s` per transport operation |
| stop | --timeout | `5s` graceful termination budget |
| All commands | --verbose, --quiet | false; mutually exclusive |
| Root and command help | --help | false; print help and exit 0 if set |
| Root | --version | false; print package version and exit 0 if set |
| config | --config-dir | `.` |
| config | --harness | all registered supported harnesses |
| config | --dry-run | false |
| prime | Command-specific options | none |
| init | --harness | verified current harness |
| init | --session | verified current native session ID |
| init | --claude-socket | verified current endpoint, otherwise absent |
| init | --opencode-url | verified endpoint or supported native default, otherwise absent |
| init | --pi-socket | verified current endpoint, otherwise absent |
| init | --tmux-pane, --tmux-socket | verified current pane and server socket, otherwise absent |
| init | --no-tmux | false |
| init, stop, sync | --hook | absent; internal native hook mode only when explicit |
| check, sync | --json | false; human-readable output |
| run | --harness | saved harness; required if no saved registration |
| run | --print | false |
| stop | --agent-id, --session | absent; no explicit owner filter for manual stop; hooks MUST supply verified ownership |
| stop | --watcher, --timer | absent; stop all owned triggers if neither is set |
| sync | --harness | current or most recently used harness |
| sync | --session | native ID from applicable saved harness record |
| sync | --dry-run | false |
| message | MESSAGE | read stdin if absent; reject empty input |
| message | --from | absent; no sender envelope |
| watcher | --path | required; no default |
| watcher | --ignore | empty list |
| watcher | --events | created,modified,deleted,moved |
| watcher | --debounce | `10s` |
| watcher | --max-wait | `60s` |
| watcher, timer | --message | absent; omit field from event |
| watcher, timer | --name | absent; omit field from PID record |
| watcher, timer | --background, -b | false; foreground |
| watcher, timer | --log-file | absent; no persistent log |
| watcher, timer | --check-interval | `30s` |
| watcher, timer | --unavailable-timeout | `10m` |
| timer | --cron, --every | neither; require exactly one |
| timer | --timezone | system local timezone for cron |

Explicit init registration of another session MUST NOT use the caller's environment to fill missing endpoints. See FEATURE-002. The local timezone does not affect interval timers. `--check-interval` does not replace the check immediately before delivery.

### Environment variables

These are the only package-defined public environment variables for the initial release.

| Variable | Default when unset | Accepted values | Scope |
|---|---|---|---|
| GIT_HARNESS_DIR | `.harness` | Nonempty single path component; not `.` or `..`; no path separators | Target lookup, init destination, config ignore rules |
| GIT_HARNESS_FILE | `agent.json` | Nonempty single filename; not `.` or `..`; no path separators | Target lookup and init destination |
| GIT_HARNESS_HISTORY_MAX_SIZE | `256K` (262144 bytes) | Positive integer bytes or positive integer with K/M binary suffix | History rotation |

Reject empty or invalid values. Explicit file targets bypass the directory and filename conventions. Read environment values at process startup. A running trigger does not change its environment when another process changes its environment. Do not introduce environment aliases for CLI parameters. Native harness environment variables used for discovery are adapter inputs, not package configuration.

### Fixed runtime defaults

| Setting | Value |
|---|---|
| Maximum distinct filesystem changes per batch | 50; send rescan notification on overflow |
| Pending watcher batches per process | 1 |
| Pending timer ticks per process | 1 |
| First timer notification | After first interval or next cron match |
| History rotation timezone | UTC |
| History retention | Unlimited; no automatic deletion |
| History compression | None |
| History synchronization | Disabled until explicit sync or explicit integration opt-in |
| Transport priority | Native, then verified safe tmux fallback |
| Agent identifier | unique-namer animal category, four alphanumeric suffix characters |

Define shared defaults once in code. Test actual behavior with omitted arguments, explicit overrides and invalid values. Test help output against the same defaults. Do not require the user to set an environment variable or pass an optional parameter to obtain the documented default behavior.
