# developer/1 handoff

Owner requires STOP after AS-019 acceptance while the physical checkout is renamed. Do not resume AS-003 or other implementation until owner supplies the new location and continuation instruction. Use repository-relative paths; do not rename this checkout yourself.

## Identity and communication

- Role: developer/1; launch directory relative to repository: agents/developer/1/.
- Current thread: 01a21c90-ef19-7612-a747-b9520f062deb.
- Manager/1: 01a21c90-df87-74d2-9c7a-987776f2c652.
- Reviewer/1: 01a21c91-08df-7840-9f1c-123aca6c8794.
- Use native codex_tui discovery/read/send tools. Verify launch identities before messages. No new agents/threads, tmux injection, or product CLI coordination.

## Repository and work state

Origin: git@github.com:neprel/git-harness.git; repository ID 1472945224. Current branch: work/git-harness-implementation. Current draft PR: https://github.com/neprel/git-harness/pull/2. The historical branch and superseded PR #1 are preserved with history intact. No tags, merge or publication.

Read AGENTS.md, agents/developer/AGENTS.md, agents/developer/1/AGENTS.md and approved specs/current/git-harness/ before continuing. Product commands run from works/. Investigations belong in probes/{task-id}/. Management/specification edits belong to manager. Preserve owner root LICENSE modification.

AS-019 product commit: 2e4d2c8e7724081041638b4502353084e82d27f9. Review submission: 5265093. Product evidence: probes/AS-019/product-rename.md, distribution-verification.json, pypi-name-check.json; manager repository proof: probes/AS-019/repository-rename.json. Final correction: 3741287d38aabd4ac0d13a4c151825f96ec35221. Independent acceptance: 21594a26da29f1c4b459d9e71df7eceaeee23593; accepted task tasks/done/developer/AS-019.md and probes/AS-019/review.md. Hosted evidence commit: 5ed47e382db939fb243332343933d749576ef91d; exact jobs in probes/AS-019/hosted-verification.json. AS-019 is accepted, all agents stop. Manager workspace-name audit is probes/AS-019/workspace-name-audit.json.

Final product revision3741287 manual Release https://github.com/neprel/git-harness/actions/runs/45998800861 and PR Release https://github.com/neprel/git-harness/actions/runs/45998807187 both SUCCESS: all six Linux/macOS Python3.11–3.13 portable jobs, four Linux native foundation jobs, lint/identity/build passed; publication skipped. PR CI https://github.com/neprel/git-harness/actions/runs/45998807121 failed only four required native acceptance gates; all infrastructure jobs passed. Metadata/handoff commits after3741287 do not change product source.

## Verified local checks

At final AS-019 product revision3741287, Python 3.12.13: 308 portable tests passed, zero skips, one deliberate native deselection; combined coverage 99.72%, all 34 branches. Ruff and actionlint passed. Wheel/sdist built; 23 clean-install checks passed, including installed API tests, python -m git_harness, uvx local wheel, private uv tool install, standalone git-harness and real git harness outside repositories with isolated HOME/Git config. Four native dependency locks retain exact dependency metadata/integrities. No inference resources consumed.

Reproduce from works/: uv sync --locked --dev; uv run --locked pytest; uv run --locked ruff check src tests scripts; uv run --locked python scripts/lint_workflows.py; uv build; uv run --locked python scripts/verify_distribution.py.

## Open work and limits

- AS-003: tasks/work/developer/1/AS-003.md, paused before product implementation. No registration code was added. Metadata dependencies remain AS-002/AS-017. AS-019 acceptance and owner continuation are scheduling requirements, not added graph dependencies.
- AS-018: tasks/work/developer/1/AS-018.md, remains open. Infrastructure works; native lifecycle/delivery/history/resume and all 12 directed cross-harness acceptance routes are absent and must fail closed. Prior reviewed infrastructure revision 9f54116aa285fd106b9965880c5db9ddf311bfd2; evidence probes/AS-018/findings.md and interim-review-9f54116.md. Historical manual Release run45997347629 succeeded build-only; no publish.
- Built-ins still return unsupported exit4. Adapter capabilities remain empty, TypeScript resources are placeholders. No native compatibility claim.
- Publication requires real native acceptance, AS-016 acceptance, owner protections/environment/publisher setup and explicit authorization. PyPI git-harness endpoint was404 on2026-11-27; this does not reserve it.
- Do not modify current specifications directly, self-accept tasks, add dependencies, publish, or consume paid inference without approval.
