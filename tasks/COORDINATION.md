# Git Harness coordination

Manager: manager/1. Updated: 2026-11-27.

## Current work

AS-001, AS-002, AS-017 and AS-019 are independently accepted in tasks/done/developer/. AS-018 remains assigned to developer/1; hosted portable and Linux native foundation checks pass, while full native acceptance remains pending. AS-003 is assigned and paused until the owner supplies the renamed physical folder and says to continue. Reviewer is reviewer/1.

Approved requirements: specs/current/git-harness/. Completed rename record: specs/archive/AS-SPEC-002-git-harness/CHANGE.md. AS-019 is accepted at 21594a2; existing task IDs, dependencies and review histories remain unchanged. The reviewed earlier naming proposal is superseded and archived.

## Workspace and evidence

Product source/tests/docs/scripts/config live in works/. Run product commands there. Root .github/workflows/ uses works/ and works/dist/. Agents/specs/tasks/probes stay outside; only the root Git repository exists. Store investigations in probes/{task-id}/ and link findings from concise tasks. Preserve original probes, upstream evidence and historical execution/review records; their original names/paths are historical. A copy of the prior coordination view is in probes/AS-019/.

## Next work

1. AS-019 is completed and independently accepted.
2. All agents write relative-path handoffs and stop. The owner will rename the physical project folder.
3. Resume only after the owner supplies the new folder and says to continue. AS-003 is next; AS-018 remains open for its native gates.
4. Then follow the existing dependency graph through AS-016.

A dependency is satisfied only in done/. Keep one developer implementation at a time in this checkout. Concurrent review tests require an isolated exact-revision checkout. Wake idle agents through native Codex messaging when eligible work exists.

## Verification and release

Default portable tests require no native client, tmux, credentials, GPU or model. Native tests use pinned clients, fresh private homes and deterministic loopback providers, verified egress denial and connection auditing. No paid inference. Synthetic/version-only passes cannot replace native lifecycle/delivery/resume or all 12 migration routes. Preserve session-migrate MIT provenance. Keep runtime dependencies limited to the approved four packages.

Hosted CI must pass Linux/macOS Python 3.11/3.12/3.13, lint, architecture/default/requirement tests, at least 85% branch coverage and clean distribution installs. Publishing uses exact tested artifacts, a separate OIDC job and owner-approved pypi environment. No release tags, publication or account-setting changes without explicit approval.

Pending owner setup: branch protection/required CI, pypi environment approval/tag restrictions and PyPI Trusted Publisher. Values after repository resolution: neprel/git-harness, release.yml, pypi, distribution git-harness.

## Repository identity

Owner freed the target name. Authenticated gh user neprel verified the target returned 404, then renamed source repository ID 1472945224 to neprel/git-harness. The ID, history/default head and open draft PR #1 remain intact. Origin is git@github.com:neprel/git-harness.git; repository access and remote head verified. Current proof: probes/AS-019/repository-rename.json. Earlier collision evidence remains unchanged. PyPI git-harness returned 404 on 2026-11-27; recheck before publication. No tags or publication.

## Communication

Manager thread: 01a21c90-df87-74d2-9c7a-987776f2c652.
Developer thread: 01a21c90-ef19-7612-a747-b9520f062deb.
Reviewer thread: 01a21c91-08df-7840-9f1c-123aca6c8794.
Both native round trips and launch identities were verified. Initial tmux bootstrap was owner-authorized; all later coordination uses native messaging. No additional agents or threads.

## Owner pause after rename

The owner ordered all agents to stop with handoffs after the complete rename. Do not resume AS-003 or other work at rename completion. Each agent writes agents/{role}/1/HANDOFF.md, preserves task state/evidence and awaits the new folder/continuation instruction. Use relative workspace paths in handoffs. Historical records/upstream evidence remain intact as previously required.

## Final rename verification

Product 2e4d2c8 and final correction 3741287 accepted by reviewer/1 at 21594a2. Independent 308 portable tests and 23 install/native Git checks passed. Final manual Release 45998800861 and PR Release 45998807187 passed; publication skipped. Exact CI 45998807121 passes all infrastructure jobs and fails only the four intentionally missing native acceptance gates (AS-018). Hosted proof: probes/AS-019/hosted-verification.json; independent review: probes/AS-019/review.md. No further implementation before owner continuation.

## Stop handoffs

Reviewer and developer reported STOPPED after AS-019 acceptance. Handoffs: agents/reviewer/1/HANDOFF.md, agents/developer/1/HANDOFF.md and agents/manager/1/HANDOFF.md. Manager stops after recording this handoff. No further implementation or review until the owner provides the renamed folder and continuation. Preserve the owner root LICENSE modification.
