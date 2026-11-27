# Pi integration

## R1 - Native integration

Use project-local .pi/extensions/git-harness.ts. Verify extension discovery at actual launch directory; document symlink or explicit extension loading for nested roles. Use session_start/session_shutdown, distinguish reload from quit and replacement. Obtain ID from session manager and native file path if needed for resume. Resume with `pi --session ID` or verified native file argument. Implement local Unix socket inside extension (no extra daemon) with restrictive directory/socket permissions, bounded framed requests and expected agent_id validation. Use documented sendUserMessage followUp with prompt expansion disabled where supported. Return accepted only after successful admission. Probe without inference. Publish socket endpoint during init, close owned socket on shutdown; preserve owner during verified reload or explicitly stop/recreate triggers. Read/write native JSONL tree via reference adapter or SDK; retain active branch and report omissions. Test idle/busy delivery, lifecycle, socket reuse, nested discovery and resume. Do not claim Windows socket support until tested.

## R2 - Acceptance

Record exact tested harness version, OS, supported features, commands and reproducible evidence. Use sanitized fixtures and isolated native sessions. Test register, check, message, run, stop and history import/export. Fail closed when identity, liveness or delivery safety cannot be established. Document unsupported features; do not advertise unverified behavior.
## R3 - Package boundary

Implement the common Harness interface in harnesses/pi/adapter.py. Keep native discovery, probe, launch, delivery, history read/write and configuration inside this package. Include extension.ts and any required harness-specific helper resources in the same package. Use the common portable event model. Do not modify the common services to handle this harness. Verify that the wheel contains the resources and the configure method installs them at the native paths specified above.

