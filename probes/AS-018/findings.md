# AS-018 infrastructure evidence before AS-019

Executor: developer/1. Snapshot: `9f54116aa285fd106b9965880c5db9ddf311bfd2`.
Date: 2026-11-27. This record preserves the original snapshot names and URLs.
Owner-approved AS-019 now renames the product to Git Harness; do not rewrite
this historical evidence or treat its old naming policy as current requirements.

## Implemented and verified snapshot

Root CI/release workflows use full action commit pins, uv 0.13.0 with checksum
enforcement, product steps under works/, Linux/macOS Python 3.11/3.12/3.13,
lint/format, requirement-map checks, actual branch coverage and clean artifact
installs. Repository-only tests, provider, fixtures and scripts stay out of both
distributions. Reports retain aggregate counts/coverage and native version/hash
pins, not transcripts, requests, homes or raw traces. No ordinary job requests
OIDC or publishing secrets. actionlint 1.7.12 is checksum-pinned.

Release separates exact-commit portable/native foundation, identity, artifact
build and native acceptance. Only a stable tag can request publishing; manual
and PR paths cannot. Publish alone uses environment pypi and OIDC, downloads
the exact tested same-run artifact and invokes pinned PyPA publishing with
attestations enabled and skip-existing disabled. It does not check out, rebuild
or execute project code. Identity checks enforce version/tag/SHA/default-branch
ancestry and owner-controlled protections. This historical snapshot also blocks
publishing pending the then-proposed distribution name. No account setting,
merge, tag, release or package publication was changed by developer/1.

## Hosted evidence

Shared implementation branch and draft PR were explicitly authorized by the
owner through manager/1. Branch change was coordinated with both peers before
switching. [Draft PR #1](https://github.com/neprel/agent-session/pull/1) was opened
without merging. Owner LICENSE remained unstaged and unchanged.

- [CI 45996461223](https://github.com/neprel/agent-session/actions/runs/45996461223):
  all six Linux/macOS portable jobs and workflow lint passed. All four actual
  Linux native foundation jobs passed: exact Codex 0.144.4, Claude 2.1.209,
  OpenCode 2.0.23 and Pi 0.80.6 plus Node 22.19.0. Child loopback was admitted;
  external IPv4/IPv6/DNS operations were denied with ENETUNREACH (101). Clients
  ran under strace after preflight inside network/PID namespaces. This closes
  AS-017's Linux provisioning/version foundation evidence gap, not native
  adapter compatibility. CI correctly remains red because all four required
  native acceptance jobs reject the incomplete real-test manifest.
- [PR build-only Release 45996461203](https://github.com/neprel/agent-session/actions/runs/45996461203):
  passed at the same snapshot, including identity, six portable jobs, lint,
  four native foundation jobs and tested distribution upload. Publish and
  tag-only native acceptance were skipped for the explicit non-publication
  event. No publication occurred.
- [Manual Release 45997347629](https://github.com/neprel/agent-session/actions/runs/45997347629):
  manually dispatched at the corrected snapshot before the AS-019 push hold;
  final outcome was pending when this snapshot record was prepared. Record its
  final result separately. No claim of a completed final manual gate yet.

Earlier runs at `6eaa2cdf6870ad35133f2b4efcb5e2b9cc0f7e69` found Claude's
top-level npm command link pointed at `bin/claude.exe` when install hooks were
disabled. The public pinned package metadata and platform tar header verified
the Linux executable at
`@anthropic-ai/claude-code-linux-x64/claude`. Selecting that integrity-locked
optional-package binary fixed the hosted gate without enabling install scripts
or weakening isolation. Other three native foundation jobs already passed.
This is recorded as a concrete provisioning correction, not a guessed native
transport protocol.

Local validation at the corrected snapshot: 307 portable tests, no skips and
one deliberately native test deselected; 99.72% product coverage, all 34 product
branches covered. Ruff lint/format and actionlint passed. Security tests cover
forged release identity, manual/PR non-publication, required owner guards,
exact checkout/ancestry, artifact handoff, report content exclusion, incomplete
acceptance mapping and rejection of version-only substitutes.

Independent interim inspection: `interim-review-9f54116.md`, authored by
reviewer/1 from an isolated immutable archive. It did not accept or move AS-018.

## Open work

AS-018 remains assigned/open. Required adapter lifecycle/delivery/idle/busy,
resume/context append and all 12 cross-harness gates do not exist yet; the
manifest fails explicitly rather than passing/skipping them. Successful final
manual build-only evidence and final release metadata/owner safeguards must be
rechecked after AS-019. Repository identity/remote naming collision resolution
belongs to manager/1 and the owner. No push is permitted during that hold.
Owner account/environment setup and publication remain separate actions.
