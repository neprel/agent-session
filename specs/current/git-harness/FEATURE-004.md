# Watcher, timer and process records

## R1 - Watcher

Watch repeatable path/glob patterns from launch directory, including hidden directories. Apply ignore globs. Watchdog provides native events. Support created, modified, deleted, moved (files and directories that match); for moves include old and new paths when known. Match a move if either endpoint matches inclusion and is not excluded. If continuity is unknown report create/delete instead. Do not send initial enumeration as new events. Debounce 10s after last event; max-wait 60s from first event. Deduplicate identical changes. Keep order of distinct changes. Bound batch to 50 distinct changes; overflow sends rescan=true and watched patterns instead of an unbounded list. Do not interpret task semantics. Use normalized paths relative to launch directory when possible, absolute otherwise. Reconcile after watcher overflow or root recreation.

```json
{"event":"fs.changed","changes":[{"type":"moved","from":"tasks/work/a/T.md","to":"tasks/review/b/T.md"},{"type":"modified","path":"specs/SPEC.md"}],"message":"Inspect changes"}
```

Other change objects have type and path. Optional message omitted if absent. Overflow example: {"event":"fs.changed","rescan":true,"paths":["tasks/**/*.md"]}. Preserve UTF-8. Send one JSON object per notification.

## R2 - Timer

Exactly one of --cron (five fields) and --every. Use croniter and timezone-aware local or explicit IANA timezone; reject invalid zones. Interval uses monotonic elapsed time. First tick occurs after interval or next cron match, not immediately. Do not replay missed ticks. Document and test DST behavior; avoid duplicate delivery of the same scheduled instant. No timer.idle event.

```json
{"event":"timer.tick","timestamp":"2026-11-27T06:00:00Z","message":"Check unfinished work"}
```

Timestamp is the scheduled instant in UTC; optional message omitted if absent.

## R3 - Worker lifecycle

Foreground is default; show changes, batch counts, sends and errors in terminal; --verbose can show message payloads (warn about sensitive output). Ctrl+C stops worker. --background detaches worker, returns only after successful initialization, prints name/record ID/PID; no default persistent log. --log-file appends in either mode. Use bounded checks and shutdown. One pending batch per watcher and one pending tick per timer. Defer while busy/waiting if safe queue cannot be proved. Do not flood native queues. Check every 30s and before send; timeout after 10m of continuous confirmed unavailability, 0 immediately, never indefinitely. Unknown is not confirmed offline. On reconnection to same agent_id resume pending delivery. Exit if registration removed or owner changes. On uncertain acceptance do not automatically resend same payload. Release resources on normal shutdown. Use no central daemon. Prevent duplicate equivalent triggers with an OS lock based on canonical target, owner and normalized execution configuration (exclude name/log/background). Allow different schedules or paths. Use a per-target lock for publication/stop races.

## R4 - PID records

Store under watchers/ or timers/ beside agent.json. Filename is full UUID4 hex + .pid, not name or PID. Names optional, duplicate names allowed. Use unique exclusive publication and private permissions. PID is actual worker, not uvx launcher. Record:

```json
{"name":"task-monitor","pid":18452,"agent_id":"curious-fox-a82f","created_at":1795708800.123,"cwd":"/workspace","command":["git-harness","watcher","--target","agents/supervisor/1","--path","tasks/**/*.md","--background"]}
```

Omit name if absent. created_at is psutil process creation time, not record creation time. Store public invocation argument array (not shell string); do not invent unavailable launcher arguments. Keep records out of Git. Do not execute recorded command automatically. Verify PID plus creation time and worker identity before termination; stale/reused PID is never signaled. Gracefully terminate with bounded wait. Remove record only after confirmed worker exit or stale identity; preserve on uncertain inspection. Check lists IDs, names, PID, running/stale/unknown; verbose/JSON includes metadata. Stop supports exact UUID or unambiguous prefix, or exact name (all matches); document precedence and reject ambiguous identifier/name collisions.
