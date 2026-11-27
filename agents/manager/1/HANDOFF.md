# Git Harness manager handoff

Status: STOPPED for the owner's physical folder rename. AS-019 is independently accepted.

The owner will rename the physical project folder. Do not rename it or start further work. Resume only after the owner supplies the new location and says to continue. Use repository-relative paths.

## Identity and communication

Role: manager/1. Relative launch directory: agents/manager/1/.

- Manager thread: 01a21c90-df87-74d2-9c7a-987776f2c652.
- Developer thread: 01a21c90-ef19-7612-a747-b9520f062deb.
- Reviewer thread: 01a21c91-08df-7840-9f1c-123aca6c8794.

Rediscover native Codex threads after the folder move or restart. Verify launch roles before messages. IDs may change if the owner restarts agents. Use native codex_tui communication. Do not create agents/threads, inject tmux input or use the product CLI for coordination.

## Repository and naming

Repository: https://github.com/neprel/git-harness. ID: 1472945224. Origin: git@github.com:neprel/git-harness.git. Branch: work/git-harness-implementation. Draft PR: https://github.com/neprel/git-harness/pull/2. Superseded PR #1 and its branch remain historical records; PR #1 is closed. No history rewrite, merge, release tag or publication.

The owner approved the complete Git Harness rename. Product/distribution/executable: Git Harness / git-harness. Package: git_harness. Native Git command: git harness. Default registration directory: .harness. Registration file: agent.json. Public variables: GIT_HARNESS_DIR, GIT_HARNESS_FILE, GIT_HARNESS_HISTORY_MAX_SIZE. No compatibility aliases or Git wrappers.

Repository rename and access proof: probes/AS-019/repository-rename.json. Maintained-name audit: probes/AS-019/workspace-name-audit.json. Original probes, upstream evidence, archived proposals and task execution/review records retain historical names and paths as required.

## Workspace and task state

Read AGENTS.md, the manager role/instance instructions, specs/current/git-harness/SPEC.md and TASK.md before resuming. Product files live in works/. Run uv commands there. Root workflows live in .github/workflows/. Investigations live in probes/{task-id}/. There is only one Git repository.

- AS-001, AS-002, AS-017 and AS-019 are independently accepted in tasks/done/developer/.
- AS-019 product commit: 2e4d2c8; final audit correction: 3741287; independent acceptance: 21594a2. Evidence: probes/AS-019/review.md. Completed specification change: specs/archive/AS-SPEC-002-git-harness/CHANGE.md.
- AS-003: assigned to developer/1, paused before implementation. Its metadata dependencies remain AS-002 and AS-017, both accepted. The owner pause is a scheduling instruction, not a dependency change.
- AS-018: assigned and open. Interim infrastructure review passed; full native adapter acceptance remains missing and intentionally fails closed. Task evidence links the exact snapshots and runs.
- Other implementation tasks remain unassigned. Follow their dependency metadata after owner continuation.

After the folder move, run uv sync --locked --dev from the new works/ and verify entry points resolve the new folder. Do not reuse previous absolute virtualenv paths.

After continuation, AS-003 is next. Keep AS-018 open while implementing the shared services/adapters and all 12 migration routes. Do not approve work on behalf of reviewer/1 or implement product code as manager.

## Verification and limits

Local rename verification: 308 portable tests, no skips, 99.72% combined product coverage, all 34 measured branches. Ruff/actionlint passed. Wheel/sdist builds and 23 clean-install checks passed, including module/standalone entry points, local-wheel uvx, private uv tool install and native Git discovery outside repositories. Evidence: probes/AS-019/product-rename.md and distribution-verification.json.

Final manual Release 45998800861 and PR Release 45998807187 passed at final correction 3741287; publication skipped. Hosted evidence is recorded at 5ed47e3 in probes/AS-019/hosted-verification.json. CI 45998807121 passes all infrastructure jobs and fails only the four missing native acceptance gates. Four Linux pinned-client foundation/version gates pass with confinement and auditing. Full lifecycle/delivery/history/resume routes are not implemented; a version-only pass is not native compatibility proof.

Built-in operations remain unsupported scaffolds. Native capabilities are unclaimed and TypeScript integration files are placeholders. The product is not release-ready. All required tests use isolated fixtures or deterministic loopback providers. No paid inference. Preserve session-migrate MIT provenance. Use only the four approved runtime dependencies and uv.

## Owner controls and preserved state

Preserve the pre-existing root LICENSE modification. Do not stage, revert or discard it. Package license copy is tracked under works/.

Pending release setup: protected default branch/required CI; pypi environment with owner approval and version-tag restrictions; PyPI Trusted Publisher for neprel/git-harness, release.yml, pypi, distribution git-harness. PyPI endpoint returned 404 on 2026-11-27; recheck before release. No account settings were changed by the agents. No tags or publication without explicit owner approval.

All agents must stop with handoffs after rename acceptance. Do not wake them for further implementation until owner continuation.
