# Codex integration

## R1 - Native integration

Use official SessionStart/SessionEnd hooks in .codex/hooks.json. Merge existing hook configuration. Read hook stdin session_id/cwd/transcript_path when present. For manual init check CODEX_THREAD_ID and version support. Use `codex resume ID` for resume. Prefer `codex queue --thread ID --message TEXT` only on a verified reachable live thread and supported version. Do not use --resume for delivery. Verify actual idle TUI wake and busy queue behavior; issue #63991 reports a queue that accepts but does not wake an idle TUI with separate writer. Record limitations; do not claim accepted means awakened. If native queue cannot safely reach live session, use verified tmux or report unsupported. Read native rollout and indexes via upstream adapters or supported API; account for compaction and replaced rollout. Generate new native history without overwriting existing files. SessionEnd is time-limited and may not fire immediately on conversation switch; test delayed hooks and final checkpoint on run.

## R2 - Acceptance

Record exact tested harness version, OS, supported features, commands and reproducible evidence. Use sanitized fixtures and isolated native sessions. Test register, check, message, run, stop and history import/export. Fail closed when identity, liveness or delivery safety cannot be established. Document unsupported features; do not advertise unverified behavior.
## R3 - Package boundary

Implement the common Harness interface in harnesses/codex/adapter.py. Keep native discovery, probe, launch, delivery, history read/write and configuration inside this package. Construct managed hook entries as Python dictionaries in the adapter. Merge them into the user's hooks.json; do not package a JSON template. Keep any necessary executable helper resources in the same package. Use the common portable event model. Do not modify the common services to handle this harness. Test the configure method from an installed wheel. Verify that it preserves unrelated user settings and hooks at the native path specified above.

