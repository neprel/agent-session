# Command and Harness interfaces

Paths below are relative to `works/`. Run development commands here.

`commands/base.py` defines `Command` with `name`, `description`,
`configure(ArgumentParser)` and `execute(Namespace) -> int`. Each command has a
separate module and is listed in `commands/__init__.py:COMMANDS`. The CLI owns
common target/verbosity options; `options.py` holds shared worker declarations.
Command-specific parameters stay in their owning command. No concrete harness
is imported into the CLI or commands. Errors use `GitHarnessError` and the
shared `ExitCode`; parser errors are exit 2. An unimplemented operation returns
an explicit unsupported error, never a success.

To add a command, create its implementation module and add one explicit registry
entry. The dispatcher calls only the Command protocol. The test-only FakeFlow
proves this with a command unknown to the dispatcher.

`harnesses/base.py` defines the typed Harness protocol: `discover`, `probe`,
`launch`, `send`, `read_history`, `write_history`, `configure` and
`configure_options`. Each operation has a concrete request and result type.
Results can be `Unsupported(capability, reason)`; delivery also distinguishes
accepted, unavailable, deferred and uncertain admission. Capabilities declare
tested versions explicitly. All four native scaffolds declare no verified
capabilities or version range. Do not treat their existence as support evidence.

To add a harness, create one package implementing that protocol and add one
entry in `harnesses/__init__.py:HARNESSES`. Declare optional native flags with
`Option(command, flags, help, value_type, choices)`. The CLI builds the parser;
adapters never import argparse or use CLI exit codes. The test-only FakeHarness
provides discovery, probe, launch planning, delivery, portable history read/write,
configuration and an extra option without modifying common code.

Launch produces an argument tuple, cwd and environment; it does not spawn.
Send requires a native session, timeout and expected runtime owner. Discovery
receives an explicitly scoped environment/hook payload. A process ID plus its
creation time and a runtime identifier distinguish same-ID resumes. These typed
values carry evidence; a dataclass constructor does not verify OS ownership.
Adapters must validate liveness/identity before admitting operations.

`history.py` owns the version-1 portable model, cursor, projection and loss
contracts. Kinds admit user/assistant text, linked tools/results, supported images
and compaction summaries. The types intentionally omit arbitrary reasoning,
system/developer context and raw native payloads. They do not yet implement
serialization, storage validation, sync, transactions or recovery. Those belong
to AS-008/AS-009. The accepted AS-001 mapping is in
`../probes/AS-001/report.md`; preserve stable source positions, digest-validated
prefixes and projected omitted events when implementing it.

`session.py`, `processes.py` and `delivery.py` define common identity/outcome
values. `tmux.py` reserves the shared transport boundary. Native formats, hooks,
configuration merge and resources remain inside each harness package. Load
resources with `importlib.resources`; the wheel contains the reserved OpenCode
`plugin.ts` and Pi `extension.ts`. No Codex/Claude JSON templates are shipped.
Future implementation must preserve this boundary and verify supported native
versions before enabling a capability.
