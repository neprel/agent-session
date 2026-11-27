# OpenCode integration

## R1 - Native integration

Use project-local TUI plugin, proposed .opencode/plugins/agent-session/tui.ts; verify required cli.json/plugin loading syntax for pinned version. Observe active session route and dispose/cleanup lifecycle; session.created/deleted are not equivalent to resume/exit. Obtain session ID directly from plugin; manual init can use OPENCODE_SESSION_ID only if verified. Resume with native --session option. Use documented session API with queued follow-up delivery; do not start a service during probe/send. Support verified server endpoint via opencode.url. Version-gate API paths and request bodies (older prompt_async versus newer API). Use official export/import, not direct writes to shared database. Test session switch, resume, TUI exit, server remaining alive, nested plugin discovery and external delivery. If TUI cleanup cannot be verified, document limitation and rely on explicit stop/reconcile.

## R2 - Acceptance

Record exact tested harness version, OS, supported features, commands and reproducible evidence. Use sanitized fixtures and isolated native sessions. Test register, check, message, run, stop and history import/export. Fail closed when identity, liveness or delivery safety cannot be established. Document unsupported features; do not advertise unverified behavior.
## R3 - Package boundary

Implement the common Harness interface in harnesses/opencode/adapter.py. Keep native discovery, probe, launch, delivery, history read/write and configuration inside this package. Include plugin.ts and any required harness-specific helper resources in the same package. Use the common portable event model. Do not modify the common services to handle this harness. Verify that the wheel contains the resources and the configure method installs them at the native paths specified above.

