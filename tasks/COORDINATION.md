# Git Harness coordination

Manager: manager/1. Updated: 2026-11-27.

## Current work

AS-001, AS-002 and AS-017 are independently accepted in tasks/done/developer/. AS-018 remains assigned to developer/1; hosted portable and Linux native foundation checks pass, while full native acceptance remains pending. AS-003 is assigned but paused until the owner-approved AS-019 rename is independently accepted. Reviewer is reviewer/1.

Approved requirements: specs/current/git-harness/. Complete rename: specs/changes/AS-SPEC-002-git-harness/CHANGE.md. AS-019 has priority; existing task IDs, dependencies and review histories remain unchanged. The reviewed earlier naming proposal is superseded and archived.

## Workspace and evidence

Product source/tests/docs/scripts/config live in works/. Run product commands there. Root .github/workflows/ uses works/ and works/dist/. Agents/specs/tasks/probes stay outside; only the root Git repository exists. Store investigations in probes/{task-id}/ and link findings from concise tasks. Preserve original probes, upstream evidence and historical execution/review records; their original names/paths are historical. A copy of the prior coordination view is in probes/AS-019/.

## Next work

1. Complete and independently review AS-019.
2. Resume AS-003, then eligible AS-004/AS-005/AS-008.
3. Continue AS-006/AS-007/AS-009/AS-010 as dependencies are accepted.
4. Implement AS-011 through AS-014 with pinned native evidence.
5. Complete AS-015 and remaining AS-018 gates, then AS-016.

A dependency is satisfied only in done/. Keep one developer implementation at a time in this checkout. Concurrent review tests require an isolated exact-revision checkout. Wake idle agents through native Codex messaging when eligible work exists.

## Verification and release

Default portable tests require no native client, tmux, credentials, GPU or model. Native tests use pinned clients, fresh private homes and deterministic loopback providers, verified egress denial and connection auditing. No paid inference. Synthetic/version-only passes cannot replace native lifecycle/delivery/resume or all 12 migration routes. Preserve session-migrate MIT provenance. Keep runtime dependencies limited to the approved four packages.

Hosted CI must pass Linux/macOS Python 3.11/3.12/3.13, lint, architecture/default/requirement tests, at least 85% branch coverage and clean distribution installs. Publishing uses exact tested artifacts, a separate OIDC job and owner-approved pypi environment. No release tags, publication or account-setting changes without explicit approval.

Pending owner setup: branch protection/required CI, pypi environment approval/tag restrictions and PyPI Trusted Publisher. Values after repository resolution: neprel/git-harness, release.yml, pypi, distribution git-harness.

## Repository rename blocker

Authenticated gh user and owner are neprel. Verified source repository ID 1472945224. Existing target neprel/git-harness is a different repository (ID 1462637028). Rename returned HTTP 422. Origin is restored to the verified source; no push went to the existing target. Evidence: probes/AS-019/repository-check.json. Owner decision is required before changing the separate existing repository. PyPI git-harness returned 404 on 2026-11-27; recheck before publication.

## Communication

Manager thread: 01a21c90-df87-74d2-9c7a-987776f2c652.
Developer thread: 01a21c90-ef19-7612-a747-b9520f062deb.
Reviewer thread: 01a21c91-08df-7840-9f1c-123aca6c8794.
Both native round trips and launch identities were verified. Initial tmux bootstrap was owner-authorized; all later coordination uses native messaging. No additional agents or threads.
