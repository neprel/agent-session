# AS-017: isolated test foundation

Executor: developer/1. Date: 2026-11-27. Host: Darwin 24.6.0 arm64.
Python 3.12.13; uv 0.13.0. Task: AS-017, original reviewer reviewer/1.

## Result

Reusable infrastructure lives under `works/tests/support/`: private workspaces,
literal fake executables, owned process-group cleanup, separate monotonic/UTC
fake time, shared fake Harness, immutable fixture copying, a deterministic
loopback provider, native confinement/audit helpers and pinned provisioning.
No runtime implementation or dependency was added. All native adapters still
declare no verified capability/version support.

The provider adapts the reviewed session-migrate provider at
`fefb719088dc0157b16f071065daa30434a0b980`. Complete MIT notice is retained in
`works/tests/support/LICENSE.session-migrate`; provenance and modifications are
documented in the module and product notices. Supported test wire subset:
OpenAI Chat Completions/Responses and Anthropic Messages, JSON and SSE, scripted
tool calls/results, completion/terminal events, provider errors, bounded timeout
and malformed streams. It records only accepted synthetic JSON bodies, rejects
unknown endpoints/query/framing/shapes, duplicate keys, non-finite JSON,
nonlocal credentials and exceeded budgets. Messages supports `?beta=true`.
No model or external HTTP client exists in the provider. Cleanup releases
pending timeout handlers and closes/join threads and listener.

`works/tests/fixtures/v1/manifest.json` pins six native synthetic files: reviewed
upstream Codex 0.144.4, Claude 2.1.209, Pi 0.80.6 and OpenCode 1.17.20 fixtures;
a generated OpenCode 2.0.23 public bundle; and an adapted Pi compaction/branch
fixture. All six reparsed successfully using the exact reviewed upstream
readers in the isolated reference tree. This is format evidence, not native
client resume proof. Harness-neutral lifecycle/endpoint/invalid-record scenarios
are explicit; unverified raw hook/plugin events were not invented.

## Verification

Run product commands from `works/`:

```sh
uv sync --locked --dev
uv run --locked pytest
uv run --locked ruff check src tests scripts
uv run --locked ruff format --check src tests scripts
uv build
uv run --locked python scripts/verify_distribution.py
uv run --locked python scripts/run_native.py --isolation-only
git diff --check
```

Results: **294 portable tests passed**, no skips; one explicitly native test
deselected by the default selection. Product coverage remains 99.72% combined,
all 34 product branches covered; no product module excluded. Runtime and
collection skip subprocess regressions prove skipped required work returns
failure. The final provider-only follow-up passed all 31 protocol tests after
adding complete assistant-call/result replay inputs. Lint/format, locked sync,
wheel/sdist build and 15 distribution checks passed.

Both artifacts exclude repository-only tests, provider, fixtures, provisioning
scripts and native locks. Both keep product native resources and license
notices. Clean wheel/sdist installs pass all nine interface tests against the
installed product; isolated local-wheel uvx passes. This intentionally changes
the initial AS-002 sdist policy per AS-017's acceptance criterion. Accepted
AS-002 probes/history remain unchanged; the current reusable check lives in
`works/scripts/verify_distribution.py`. Explicit sdist exclusions prevent nested
fixture README names from matching Hatch's README include pattern.

The macOS isolation-only entry point exited 0. It allowed a child loopback TCP
connection and denied child external IPv4, IPv6 and DNS UDP socket operations
with EPERM (1). Timeouts are not accepted as evidence. A second explicit
client-entry invocation exited **4 as expected**, stating audited macOS client
execution is unavailable; no native client was launched. `verification.json`
records the concise outcomes, prerequisite and artifact hashes.

## Native provisioning and remaining platform gates

`scripts/provision_native.py` bootstraps Node 22.19.0 from official nodejs.org
archives with committed SHA-256 pins. Linux x86_64 is the client provisioning
target. A macOS arm64 `--node-only` run downloaded, checksum-verified and
extracted its exact archive successfully; pinned Node/npm generated the four
per-client locks without installing/running a harness. Each lock binds all
transitive public-registry artifacts to integrity values. Three Pi dependency
entries initially omitted npm integrity; each was completed only after checking
its exact public registry version metadata and downloaded tarball SHA-512.

Client pins follow reviewed upstream acceptance: Codex 0.144.4, Claude 2.1.209,
OpenCode 2.0.23 and Pi 0.80.6. Installation uses `npm ci --ignore-scripts` in a new
private root, fresh HOME and no inherited credentials. It refuses existing
destinations. Installation never executes a native client. Tests verify lock
pins/integrity, download checksum failures, archive escape rejection, private
environment, safe command arrays and no install hooks. Native execution later
checks manifest schema, node/client/lock hashes and exact versions again.

On a clean Linux runner with util-linux `unshare`, enabled user/PID/network
namespaces and `strace`:

```sh
uv run --locked python scripts/provision_native.py --destination /tmp/NEW_NATIVE_ROOT --client codex
uv run --locked python scripts/run_native.py --manifest /tmp/NEW_NATIVE_ROOT/manifest.json --client codex
```

Use a new destination and substitute the client for each matrix job. Dependency
installation has network access; execution enters a new network/PID namespace,
enables only loopback and verifies real child egress denial **before** a client
launch. Native clients run under `strace -f` for connect/sendto/sendmsg/sendmmsg.
The audit rejects attempted external destinations even when already denied,
and rejects unrecognized internet-address trace forms. PID namespace teardown
kills detached descendants; owned process groups bound ordinary fixture cleanup.
Unit tests verify that a failed preflight prevents process creation and that an
external syscall trace fails after cleanup, regardless of the client's exit 0.

**Limits:** actual Linux namespace setup, native npm installs and audited pinned
client execution cannot be verified on this macOS host. AS-018 must establish
that runner evidence. macOS client execution is deliberately refused until an
auditable native path exists. Missing tools/isolation/manifests/clients fail;
there is no skip/pass or installed-user-harness fallback. The current opt-in
native test is a provisioning/version gate only. Adapter hook, ownership,
delivery, idle/busy, imported-context replay, same-session append and all 12
cross-harness routes remain mandatory adapter/integration/release gates. A
synthetic or version-only pass does not satisfy them. No paid inference, user
session/configuration access, global tool install or publication was performed.
