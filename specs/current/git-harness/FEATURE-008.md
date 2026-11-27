# Claude Code integration

## R1 - Native integration

Use .claude/settings.json SessionStart/SessionEnd command hooks. Read hook payload identity and launch directory; manual init may use CLAUDE_CODE_SESSION_ID if present. Resume with `claude --resume ID`. Investigate officially documented Channels or verified local messaging socket; do not treat undocumented socket as stable. Implement native transport only with a tested protocol and local ownership checks. If it needs a channel adapter, keep it in harness integration and document setup; do not invoke headless Claude to deliver messages. Safe tmux fallback is acceptable when native unsupported. Test /resume, /clear, startup and normal exit. Read/write portable history through reference adapters and validate native resume. Do not modify live JSONL.

## R2 - Acceptance

Record exact tested harness version, OS, supported features, commands and reproducible evidence. Use sanitized fixtures and isolated native sessions. Test register, check, message, run, stop and history import/export. Fail closed when identity, liveness or delivery safety cannot be established. Document unsupported features; do not advertise unverified behavior.
## R3 - Package boundary

Implement the common Harness interface in harnesses/claude/adapter.py. Keep native discovery, probe, launch, delivery, history read/write and configuration inside this package. Construct managed hook entries as Python dictionaries in the adapter. Merge them into the user's settings.json; do not package a JSON template. Keep any necessary executable helper resources in the same package. Use the common portable event model. Do not modify the common services to handle this harness. Test the configure method from an installed wheel. Verify that it preserves unrelated user settings and hooks at the native path specified above.

