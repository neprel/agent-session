# AS-001: harness contract research

Executor: developer/1. Date: 2026-11-27. Platform: Darwin 24.6.0 arm64.
Repository base: `4d45ddb64363b93f546e455698299423297fb046`.
Native manager round trip was verified before execution. This report records
research, not adapter support or completion of native acceptance gates.

## Reference pin and provenance

Reviewed source: [xhluca/session-migrate at fefb719088dc0157b16f071065daa30434a0b980](https://github.com/xhluca/session-migrate/tree/fefb719088dc0157b16f071065daa30434a0b980).
`git ls-remote https://github.com/xhluca/session-migrate.git HEAD` returned that
revision. `reference-manifest.json` records SHA-256 hashes of the reviewed files.
Retrieve each file using its manifest URL and verify its hash before reuse.
The repository clone/archive downloads were stopped when individual pinned raw
files proved sufficient. No upstream tests were claimed to have run locally.

The upstream LICENSE is MIT, copyright (c) 2026 xhluca. Copy/adapt applicable
neutral model, format readers/writers, validation and test-provider code. Keep
the complete license and copyright notice beside substantial reused code and
include them in distributions. Add per-file provenance, revision and changes.
No upstream implementation has been vendored into this project by AS-001.

Reviewed reuse boundaries:

| Upstream path | Reuse and required adaptation |
| --- | --- |
| `src/session_migrate/model.py` | Neutral event/provenance dataclasses; restrict persisted payloads as below. Its arbitrary `dict[str, Any]` is not a safe storage contract by itself. |
| `src/session_migrate/jsonl.py` | Strict bounded reads, source hashing and atomic private-file publication patterns; adapt to common history transactions. |
| `src/session_migrate/formats/{codex,claude,pi}.py` | Place native parsing/writing/validation inside the corresponding harness package. Retain loss accounting and active-branch checks. |
| `src/session_migrate/formats/opencode{,_v2}.py` | Public export/import and transfer validation; never write the shared native DB. Preserve version gates. |
| `src/session_migrate/formats/common.py` | Neutral image/text/time validation where applicable. |
| `tests/offline_provider.py` | Development-only deterministic HTTP provider under `tests/support/`; extend and test it before AS-017 acceptance. |
| Native scripts and tests in manifest | Provisioning and independent load/append assertions; do not copy unrelated 18-client infrastructure or private-corpus workflows. |

## Installed-client observations

All executable invocations used disposable HOME/config/data/cache directories
and a newly constructed environment without inherited credentials. No user
transcripts, auth files, settings or tmux server were read. Only installed code,
help and version output were inspected. The macOS sandbox allowed a connection
to our loopback listener and rejected a direct `1.1.1.1:443` connection with
`PermissionError: Operation not permitted` before native startup. Children
inherited the sandbox. These tests used fixed protocol replies, no model.

`observations.json` contains content-free results and installed executable
digests. The Pi launcher digest identifies its wrapper, not its entire package;
provisioned tests must verify the package lock/integrity as well.

| Harness | Installed version | Discovery and exit evidence | Limits |
| --- | --- | --- | --- |
| Codex | 0.165.0 | `codex exec --skip-git-repo-check --json TEXT`, custom loopback Responses provider: exit 0, one `/v1/responses` request, fixed reply. JSON emitted thread ID; matching rollout `session_meta` ID and cwd were found in isolated CODEX_HOME. Pinned reader recovered prompt and reply. Empty-home TUI exited 0 after Ctrl+C at onboarding. | Noninteractive discovery/exit is verified; lifecycle hooks, queue idle wake, busy queue, TUI owner and native writer resume remain untested. |
| Claude | 2.1.322 | `claude --bare --strict-mcp-config --print --output-format stream-json --verbose --model claude-haiku-4-5-20251001 TEXT`: emitted `session_id` and matching isolated transcript; bounded normal error exit 1. Pinned reader parsed the synthetic transcript. | Two `/v1/messages?beta=true` requests reached the local provider; its path matcher returned 404. No successful reply. Empty-home interactive onboarding required termination (143); normal interactive exit is unverified. `--bare` skips configured hooks, so this is not hook evidence. |
| OpenCode | 2.2.7 | `--version`, `--help`, `session --help`, `api --help`, `serve --help` succeeded. Both `opencode --standalone` and loopback-configured `opencode run --standalone --model fixture/test --format json TEXT` exited 1 before server readiness. No provider requests. | No session discovered. Child server failed to bind/start under the restrictive sandbox; this is an isolation/provisioning blocker, not proof of a broken native API. Installed version is rejected by the pinned converter's 2.0.x version parser. |
| Pi | 1.6.1 | `pi --offline --no-extensions --no-mcp --no-skills --no-prompt-templates --no-context-files --print --mode json --model fixture/fixture-model TEXT`: exit 0, one `/v1/chat/completions` request, fixed reply. Isolated session header contains ID/cwd/version 3. | New transcript includes a `system` message; pinned 0.80.6 reader rejects it as an unsupported role. Empty-home TUI needed termination after Ctrl+C; exit code 0 following SIGTERM is not normal-exit proof. Extension loading/delivery is untested. |

No installed-client result proves native delivery or all-route migration.
No version range is inferred from one version. These failures remain explicit;
they do not justify weakening validation or counting synthetic tests as native.

## Native contract inventory

The following combines observed help, pinned source and dated official docs.
Items identified as documented are not local runtime verification.

| Harness | Identity, storage and launch | Lifecycle/configuration | Delivery and ownership |
| --- | --- | --- | --- |
| Codex | Observed `codex resume ID`; manual `CODEX_THREAD_ID` is supplied in this developer runtime. Native isolated rollout under `$CODEX_HOME/sessions/YYYY/MM/DD/rollout-...-ID.jsonl`; current smoke has `history_mode=paginated`, integer ordinals, and separate SQLite thread history. Legacy writer emits `history_mode=legacy`, pinned to 0.144.4. | [Official hooks](https://learn.chatgpt.com/docs/hooks) describe `.codex/hooks.json`, SessionStart/SessionEnd and stdin `session_id`, `cwd`, `transcript_path`. End is synchronous and time-limited; unsubscribe/switch can delay it. Trust and installed-version support must be verified in AS-011. | Observed help: `codex queue --thread ID --message TEXT`, remote endpoint/token-env options. Help is not reachability proof. Require owner runtime/process identity plus verified endpoint/session association; neither a saved rollout nor successful queue acceptance proves a live TUI. [Issue 63991](https://github.com/openai/codex/issues/63991) reports separate-writer idle wake failure for 0.171.0/daemon 0.172.0; this is not a test result for 0.165.0. Never use queue resume to deliver. |
| Claude | Observed `claude --resume ID` and `--session-id UUID`; stream-json exposes ID/cwd. Transcript under `$CLAUDE_CONFIG_DIR/projects/<encoded-cwd>/<ID>.jsonl`. Native records form a UUID/parentUuid graph; preserve selected lineage. | [Official hooks](https://code.claude.com/docs/en/hooks): project `.claude/settings.json`, command SessionStart/SessionEnd, identity/cwd/transcript payload. Verify /resume, /clear and normal quit separately; bare-mode smoke cannot establish them. `CLAUDE_CODE_SESSION_ID` is not verified as an exported environment variable. | [Channels docs](https://code.claude.com/docs/en/channels) require Anthropic authentication and preview enablement. No credential-free local channel admission/ownership was verified. No stable socket protocol is assumed. Native send must return unsupported unless a tested owned transport exists; safe tmux fallback remains a separate gate. |
| OpenCode | Observed `--session/-s ID`, `--standalone`, `--server URL`, `session list/export/import`, `api` operation-or-method interface. Use official export/import, not internal DB files. No `OPENCODE_SESSION_ID` export was verified. | [TUI plugin docs](https://opencode.ai/docs/build/plugins/cli/) describe `Plugin.define` from `@opencode/plugin/tui`, setup returning cleanup, route APIs and `cli.json` plugins. Proposed `.opencode/plugins/agent-session/tui.ts` auto-discovery and nested loading still need testing. Creation/deletion events alone cannot identify the active route or quit. | [Current API docs](https://opencode.ai/docs/api) describe `/api/info`, `/api/session/{sessionID}` and `POST /api/session/{sessionID}/prompt`, returning queue admission. Current paths differ from older `/session/.../prompt_async`; version-gate request schema and test server identity, auth, project/cwd, active TUI association and idle/busy semantics. Server existence alone is insufficient. |
| Pi | Observed `pi --session <path|id>` and `--session-id`; default `$PI_CODING_AGENT_DIR/sessions/<encoded-cwd>/...jsonl`, schema v3 tree. Installed docs/types expose `ctx.sessionManager.getSessionId()/getSessionFile()`; read the active branch. | Installed 1.6.1 `docs/extensions.md` documents project `.pi/extensions`, start reasons startup/reload/new/resume/fork, shutdown reasons quit/reload/new/resume/fork. Reload tears down and rebinds extension instances. Explicit `-e PATH` exists; ancestor inheritance remains unverified. | Installed API declares `sendUserMessage(text, {deliverAs:'followUp', expandPromptTemplates:false})`. It starts idle work and queues busy work; this is a source/docs contract, not tested delivery. Implement the specified private socket in the extension later; no built-in external socket is assumed. Publish verified ID, cwd, native path and owner/process identity on init; validate expected agent_id per request. |

Integration configuration must merge only stable agent-session-owned entries.
Hook, plugin and extension resources remain inside their harness packages.
Actual hook payloads must be bound to the specific runtime, including same-ID
resume; delayed shutdown must not stop a newer owner. PID start identity and
launch cwd require independent liveness evidence. History metadata and global
environment variables alone cannot authorize delivery.

## Portable serialization and cursor strategy

This is the implementation mapping for AS-002/AS-008 to type and test against
FEATURE-005; it adds no public options or requirements. Canonical record schema
version is 1. Use strict UTF-8 JSON, LF, sorted object keys, compact separators,
`ensure_ascii=False`, `allow_nan=False`; reject duplicate JSON keys, invalid
Unicode, unknown schema versions and malformed field types. Timestamp strings
are metadata, never identity, direction or rotation authority.

Each stored record has `version`, stable `event_id`, source provenance, event
kind, optional role/timestamp, and a validated kind-specific content object.
Source provenance includes harness, exact native session ID, native record
identity or validated source position, and block position when needed. Stable
identity hashes a domain-separated, versioned tuple of source session identity,
record identity/position and block position. It never hashes text alone. Store
an independent payload digest to detect an existing identity changing content.
Assign positions in the original native stream before filtering. Identical
messages at different positions are distinct events.

Persist only user/assistant text, completed linked tool call/result data,
validated supported image blocks and compatible compaction summaries. Tools
carry names, IDs and validated JSON arguments/results; preserve links and order.
Allowlist payload fields by kind. Do not serialize upstream raw native payloads,
private/signed thinking, system/developer context, auth, approval state or caches.
Unknown and omitted events generate content-free counters/reasons, not copies
of arbitrary raw blocks. Keep source files intact. Do not use upstream THINKING,
CONTEXT and OPAQUE payloads as canonical transcript content. The Event payload is
excluded from upstream dataclass comparison, so that equality is not a semantic
history comparison or deduplication oracle.

A file cursor binds harness/session, parser/native-format version, stream mode,
complete-record byte boundary, last validated native identity/ordinal and a
SHA-256 of the exact consumed prefix. Include selected branch/head lineage for
tree formats. On append validate unchanged prefix and lineage before importing
new complete records. An unterminated tail is not committed input. On truncation,
replacement, changed prefix, branch or compaction, stop with conflict unless the
owning adapter can prove continuity. File timestamps/counts/inodes alone are not
continuity proof. For API exports bind session/project identity and ordered native
message IDs plus validated canonical export-prefix digest; never invent a byte
offset into a mutable database or unordered export.

Index schema version 1 tracks canonical revision, authoritative source identity,
per-session cursor, canonical-to-native projection boundary and loss counters.
Projection boundaries cover **all** canonical events, including omissions. Newly
materialized native identities must map back to the already imported revision;
on readback they cannot become new canonical history. A failed/partial import
does not update destination mapping. Use one history lock and durable staging;
publish data before index, detect uncommitted tails, validate recovery boundaries,
and never infer direction by matching message text. AS-008/AS-009 own transaction
implementation and fault-injection tests.

## Offline provider and native provisioning plan

Reviewed provider SHA-256:
`7d32864357b473b12296022342afd2810583c75a8d39bc6875528c45957c30cb`.
It provides fixed text JSON/SSE for Chat Completions, Responses and Messages,
records parsed requests and binds 127.0.0.1 on an ephemeral port. The reviewed
generic stub does **not** emit tool calls, strictly validate request schemas,
enforce body/time budgets, or match URL query strings correctly for Claude.
The separate Pi corpus test has a deterministic tool-call/result script. AS-017
must adapt these pieces with MIT notices and add terminal/tool events, errors,
timeouts, malformed streams, unknown-path rejection and bounded input. Do not
reuse Gemini or unrelated providers unless required by an approved client gate.

The reviewed installer pins Linux x86_64 clients through npm package versions:

| Client candidate | Provisioning reference | Required local protocol and native oracle |
| --- | --- | --- |
| Codex 0.144.4 | `@openai/codex@0.144.4`; upstream selected executable digest `2b3edc9cdfd1717fba3dbc92817205a8a2c7511d459e456d4817eeff6f78ed7a` | Custom `model_providers.fixture` with loopback `/v1`, `wire_api=responses`, dummy env key and no OpenAI auth. Assert loaded imported ID/prefix, sent context, completed reply and same native-session append. Verify hook and queue support separately; use a newer pin if those required capabilities are absent. |
| Claude 2.1.209 | `@anthropic-ai/claude-code@2.1.209`; upstream executable digest `b882f4b8b27772f897540df50f24000206f43a9426e8f7d19bd065959b69e9dd` | `ANTHROPIC_BASE_URL=http://127.0.0.1:PORT`, dummy API key; Messages JSON/SSE, including query normalization. Bare print mode is a history oracle only; separate trusted hook/TUI tests are required. No auth-gated Channels claim. |
| OpenCode 2.0.23 | `@opencode/cli@2.0.23`; upstream also validates stock 2.0.22. Legacy `opencode-ai@1.17.20` is a different schema, not the v2 baseline. | Explicit fixture provider `@opencode/ai/providers/openai-compatible`, loopback `baseURL`, dummy key, warming disabled and external providers disabled. Official import/export, cold reopen, retained prefix and fixed appended response. Test TUI plugin/API/version support before support claims. |
| Pi 0.80.6 | `@earendil-works/pi-coding-agent@0.80.6`; version 3 reader/writer and exact-native RPC tests | Isolated `models.json`: fixture provider, `baseUrl` loopback `/v1`, `api=openai-completions`, dummy key. `PI_OFFLINE=1`; RPC get_messages/get_entries verifies loaded tools/images/compaction without inference, then fixed-provider continuation proves append. Separate TUI extension/socket idle/busy and lifecycle gates. |

These are **upstream-tested candidate pins**, not locally verified support and
not an automatic decision to advertise those versions. Exact installer/runtime
prerequisites, OS/architecture hashes, npm lock/integrity, Node version and native
capabilities must be captured on clean runners in AS-017/AS-018/adapter tasks.
The upstream installer uses npm without a committed native dependency lock, so
strengthen provisioning with an integrity-locked artifact manifest rather than
claiming full transitive reproducibility from a top-level version alone.

The upstream `scripts/run-native-test-client.sh` selects exact test node IDs and
checks JUnit for unexpected skips. Its older `verify-native-resume.sh` pins a
local Docker image digest and disables all networking: it proves ID selection,
prefix retention and local append even when authentication fails. That is useful
partial evidence, but **does not meet** our completed-turn provider oracle. Do
not make the unpublished local Docker image a CI prerequisite.

Provision dependencies with networking first, then execute in an isolated
network namespace/container which permits only loopback and hosts the provider
inside that namespace. On Linux, test the actual network denial through a child
process (including direct external IPv4/IPv6, DNS and inherited proxy routes),
then run pinned clients, private PTYs or a private tmux socket, with fresh homes,
workspaces and runtime directories. Recheck offline isolation before each gate.
On macOS the tested sandbox profile permits outbound loopback but prevents the
OpenCode child listener: test an explicit loopback bind/listen profile or explicit
loopback `serve --hostname` transport before claiming this native matrix works.
If isolation cannot be enforced, report the platform gate unavailable.

Use dummy keys only in the local environment. No OAuth, keychain or real user
HOME mount, no model downloads, cloud fallback or paid inference. Ensure child
process groups are terminated on success/error/timeout and assert endpoint
admission separately from processing. Observe real hook/plugin/extension events
at startup/resume/clear/compaction/reload/fork/quit with regular and nested launch
directories. Assert late hooks cannot replace/stop a newer owner. Exercise all
12 ordered source/receiver routes with distinct synthetic markers, repeated
text, linked tools, images, compaction and repeated switches. Independently parse
the receiving native output; assert imported context reached the local provider,
one fixed turn completed and the same native session appended. Synthetic route
tests remain mandatory even when a native gate is unavailable.

## Reproduction and remaining gates

Run from repository root (no project runtime exists yet):

```sh
uv run --no-project --python 3.12 python probes/AS-001/probe.py
curl --fail --location --max-time 30 \
  https://raw.githubusercontent.com/xhluca/session-migrate/fefb719088dc0157b16f071065daa30434a0b980/tests/offline_provider.py \
  -o /tmp/AS001-offline_provider.py
shasum -a 256 /tmp/AS001-offline_provider.py
uv run --no-project --python 3.12 python probes/AS-001/offline_smoke.py /tmp/AS001-offline_provider.py
```

The probe scripts retain only their own disposable directories, print their
location and clean child processes. Inspect their summaries locally; do not
commit complete native homes, requests, system prompts or generated auth files.
The generic PTY probe cannot reliably exit Claude/Pi onboarding; it records
forced termination honestly. Earlier probe iterations encountered PTY-close
`EIO`; this was fixed by ignoring writes after terminal closure and the final
run completed. No product tests exist yet. AS-001 verifies its evidence scripts
by execution and syntax compilation; it does not claim default pytest/CI gates.

Outstanding support/release gates: all native hook payload/runtime ownership
checks; Codex idle wake and busy admission; safe tmux prompt-state evidence;
Claude native channel availability or explicit unsupported result; OpenCode
isolated bind/startup plus active-route/disposal and current-version schema;
Pi system-role handling and socket admission/reload; native writes/resume and
all 12 full cross-client routes; clean runner provisioning and Linux/macOS
network isolation. These belong to AS-017/AS-018 and adapter/integration tasks.
No runtime implementation or approved specification was changed by AS-001.
