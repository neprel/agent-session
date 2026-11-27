# Agent-session

## Intent

Use one local CLI to register, start, resume, contact and monitor coding-agent sessions. Preserve conversation continuity when the user changes harnesses. Do not use an LLM to perform infrastructure operations.

## Scope

Support Codex, Claude Code, OpenCode and Pi interactive local sessions. Prefer native message delivery. Use tmux only when delivery is safe. Support Linux and macOS first. Keep Windows-compatible core code; do not claim Windows integration support until tests pass. Support regular projects and nested agent role/instance directories. One active registered session per target directory.

## Architecture

CLI -> command implementations -> shared services -> harness implementations. The harness registry selects one adapter by name. An adapter provides discovery, probe, launch, delivery, history read/write and integration configuration capabilities. Do not require every adapter to implement an unsupported capability. Return a clear unsupported result. Keep tmux as a shared transport, not a harness. Do not create a central daemon, database, agent registry, workflow engine or background history process. Use subprocess argument arrays, not shell evaluation. Use bounded timeouts. Do not launch an agent during message delivery or availability checks.

## Source layout

Use this source layout. Each command MUST have a separate Python module. Each harness MUST have a separate Python package. Keep its integration resources in that package.

```text
src/agent_session/
    __init__.py
    __main__.py
    cli.py
    commands/
        __init__.py
        base.py
        config.py
        prime.py
        init.py
        check.py
        run.py
        stop.py
        sync.py
        message.py
        watcher.py
        timer.py
    harnesses/
        __init__.py
        base.py
        codex/
            __init__.py
            adapter.py
        claude/
            __init__.py
            adapter.py
        opencode/
            __init__.py
            adapter.py
            plugin.ts
        pi/
            __init__.py
            adapter.py
            extension.ts
    session.py
    history.py
    delivery.py
    processes.py
    tmux.py
```

Keep the common portable event model and history storage in history.py. Keep native history read/write in the harness packages. Do not create a common directory of native history converters. Additional private modules inside a harness package are permitted when necessary (for example, history.py for a large native converter). Keep adapter.py as the public implementation of the common interface. Additional harness-specific resources belong in the same package. Use package resource APIs to load these files. Install resources at the native paths required by each harness; source filenames do not define native installation paths.

Use explicit command and harness registries. Keep cli.py limited to parser setup, shared options, dispatch and common error handling. Use shared functions for operations used by more than one command. Do not invoke another command parser or spawn this CLI to reuse an internal operation. Native hooks and plugins can invoke the public CLI. Do not add a generic plugin framework, service container or dynamic discovery system.

## Features

| File | Subject |
|---|---|
| FEATURE-001.md | CLI and distribution |
| FEATURE-002.md | Registration, target and lifecycle |
| FEATURE-003.md | Message delivery and adapter contract |
| FEATURE-004.md | Watcher, timer and process records |
| FEATURE-005.md | History synchronization and storage |
| FEATURE-006.md | Configuration and lifecycle integration |
| FEATURE-007.md | Codex |
| FEATURE-008.md | Claude Code |
| FEATURE-009.md | OpenCode |
| FEATURE-010.md | Pi |
| FEATURE-011.md | Verification and release |

## Common rules

The package MUST NOT make LLM calls. The receiving harness can use inference to process a message. The CLI MUST work without AGENTS.md or skills. Keep configuration local. Use atomic publication and ownership checks. Do not modify a native session that is active. Do not remove conversation history. Do not bypass harness trust or approval. Keep stdout machine-readable when JSON output is requested; send diagnostics to stderr. Do not print transcript contents or secrets in diagnostics. Fail safely when session identity or delivery is uncertain.

## Status

Target specification for implementation. Adapter support is subject to native integration tests. See SOURCES.md for reference material and TASK.md for task dependencies.

## Defaults

FEATURE-001 R6 defines all public parameter and environment defaults. Use this contract in code, help and tests. Generate hook configuration in Python; do not ship JSON hook or settings templates.

## Automated verification and release

Use FEATURE-011 R6-R9 for the portable test suite, native mock-provider acceptance and GitHub Actions workflows. Use public hosted runners. Do not use real model inference for required tests. Use PyPI Trusted Publishing with owner approval. See PUBLISHING.md for owner setup. Keep test infrastructure out of the runtime package.
