# Registration and lifecycle

## R1 - Target and environment

Resolve relative paths from the command launch directory. Default target is `.`. Use the first existing regular file: target itself, target/agent.json, target/.session/agent.json. If the first file is invalid, fail; do not use a lower-priority file. Environment variables `AGENT_SESSION_DIR` (default `.session`) and `AGENT_SESSION_FILE` (default `agent.json`) replace those names. Each must be a non-empty single path component other than `.` or `..`; reject separators. Explicit file targets take precedence. `init` creates the configured nested file for an existing directory, or an explicit nonexisting JSON file. Other commands do not invent targets; `run` can start a new harness in an existing directory. Canonicalize aliases for locking. For conventional registrations the launch directory is the parent of the configured session directory; for direct file targets use its parent. Reject ambiguous custom layouts rather than guessing. Auxiliary directories are siblings of the registration file. Long-running processes fix the target path and environment at startup.

## R2 - agent.json

UTF-8 JSON object. Preserve native IDs for all previously used harnesses. Example:

```json
{
  "agent_id": "curious-fox-a82f",
  "harness": "codex",
  "codex": {"session_id": "thread-A"},
  "claude": {"session_id": "session-B"},
  "opencode": {"session_id": "ses_C", "url": "http://localhost:4096"},
  "pi": {"session_id": "session-D"},
  "tmux": {"pane_id": "%27", "socket": "/tmp/tmux-1000/default"}
}
```

Required: agent_id, harness and the selected harness object with nonempty session_id. Each used harness has session_id. Optional claude.socket, pi.socket, opencode.url, tmux.pane_id (required if tmux object exists), tmux.socket. Omit unused objects and unavailable optional fields. `harness` is current or latest used, not a liveness flag. No top-level session_id, transport array or state.json. Store no credentials. Generate agent_id via unique-namer with animal category and four alphanumeric suffix characters; retry a detected collision. It is a registration label, not a security token. Preserve it for repeated init in the same live runtime; replace on new runtime or harness change. Use verified OS/runtime identity to distinguish resumed instances; an ownership guard must distinguish two processes even with the same native ID. A small private local ownership record or lock is permitted if necessary; do not track it in Git. Document the concrete proof and test it.

## R3 - init

Discover only verified current session information from hook payload, extension, environment or explicit arguments. Never launch a harness. Do not copy the caller's environment endpoints into a different target session. Reject ambiguous discovery. Update only the selected harness record and current runtime endpoints. Preserve other native session IDs. Remove obsolete runtime endpoints. Publish atomically under a per-target mutation lock. Failed initialization leaves previous data intact. Reconcile stale PID records. Do not replace a different confirmed live session in the same target. Hook invocation uses fixed launch directory and ownership evidence, never current shell changes or a guessed session.

## R4 - run

Use saved harness if --harness is absent. If no saved session exists, require a harness and start new. For a saved session, resume it. If switching with history continuity enabled, call sync before launch; use the returned native ID. Do not silently fall back to a new session on failure. Refuse a confirmed duplicate or uncertain live owner. Serialize launch attempts until registration or launch failure. Run interactively in target directory with inherited terminal I/O. --print prints the planned launch or migration steps without mutation. Do not manage tmux layout. First-start native hooks or extension call init; report missing integration. Strip unrelated inherited harness identity variables before launching another harness.

## R5 - check and stop

Check does not modify files. Report agent_id, harness, session_id, available (true/false/null), status (idle/busy/waiting/offline/unknown), transports, watchers, timers and history status. Probe without starting services or inference. Existence of transcript or pane alone is not proof of liveness. `stop` stops trigger processes, not the harness. Default stops all triggers for the target; selectors restrict by ID or exact name (all matching names); reject ambiguous ID prefixes. If selectors are supplied, do not clean unrelated session endpoints. Hooks use expected ownership to prevent delayed cleanup of a new runtime. Preserve agent.json, all native IDs and history. Full stop may remove obsolete runtime endpoints only if verified obsolete; never delete active sockets needed by the running harness. Repeated stop is safe. Recheck ownership before signaling or publishing. Serialize mutations and trigger registration to prevent stop/start races. Return failure if a verified worker cannot stop within timeout; preserve its record.

## R6 - Git

Track history and agent.json if the user opts in; do not auto-commit or push. Ignore watchers, timers, locks, sockets and temporary files. Keep local-only runtime proof out of Git. Restored descriptors from another machine are not live registrations. Use owner-only permissions for new runtime and history files where supported. Warn that transcript data can contain private code or credentials and Git history persists deleted data.
