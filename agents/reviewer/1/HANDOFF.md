# reviewer/1 handoff

Owner requires STOP after AS-019 closure while the physical project folder is
renamed. Wait for the owner to provide the new folder and continuation. Do not
rename the folder or resume any task/review on your own.

## Identity

Role reviewer/1. Launch path relative to repository: agents/reviewer/1/.
Reviewer thread: 01a21c91-08df-7840-9f1c-123aca6c8794.
Manager thread: 01a21c90-df87-74d2-9c7a-987776f2c652.
Developer thread: 01a21c90-ef19-7612-a747-b9520f062deb.
Use native codex_tui discovery/read/send tools after verifying launch identities.
No new agents/threads or tmux injection. Do not use the product for coordination.

## Reviewed state

Git Harness: distribution/executable git-harness, import git_harness, native
Git discovery git harness; default .harness, file agent.json, public variables
GIT_HARNESS_DIR/FILE/HISTORY_MAX_SIZE. No compatibility aliases.
Repository neprel/git-harness, ID 1472945224.
Origin git@github.com:neprel/git-harness.git.
Branch work/git-harness-implementation; current draft PR #2.
Exact product revision: 2e4d2c8e7724081041638b4502353084e82d27f9.
Final test/verifier correction: 3741287d38aabd4ac0d13a4c151825f96ec35221.
Review evidence: probes/AS-019/review.md. Acceptance commit is the commit that
records this handoff and moves AS-019 to tasks/done/developer/.

Local independent checks: 308 tests, no skips/one native deselection; all 34
product branches covered; lint/format/actionlint, builds and 23 installed
wheel/sdist/uvx/tool/native Git checks pass. Historical records preserved.

## Open work

AS-001, AS-002, AS-017 and AS-019 are accepted in tasks/done/developer/.
Final manual Release 45998800861 and PR Release 45998807187 succeeded at the
exact final correction SHA; both skipped publication. Reviewer is stopped.
AS-018 stays open in tasks/work/developer/1/AS-018.md: full native lifecycle,
delivery, history/resume and all 12 directed migration routes remain absent.
Infrastructure review: probes/AS-018/interim-review-9f54116.md.
AS-003 is assigned and paused before implementation. Owner continuation is
required even after AS-019 acceptance. Do not begin any other review/work.
Commands/adapters still explicitly return unsupported; resources are placeholders.
No native support/release claim, merge, tag or publication is approved.

After owner continuation, read root/role/instance AGENTS.md, tasks/COORDINATION.md,
specs/current/git-harness/SPEC.md and TASK.md, then current assigned review queue.
Product verification commands run from works/. Probes belong in probes/{task-id}/.
Task files are authoritative; preserve execution/review history and owner LICENSE
changes. Original probes retain historical names/paths. Use relative paths after
the physical move; do not reuse temporary review copies or old virtualenv paths.
