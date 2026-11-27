# AS-019 independent review

Reviewer: reviewer/1. Date: 2026-11-27.
Implementation: `2e4d2c8e7724081041638b4502353084e82d27f9`.
Final audit correction: `3741287d38aabd4ac0d13a4c151825f96ec35221`.
Management rename: f93ecdd/c5ee5a0/bebe9a4; owner authority AS-SPEC-002.

## Independent verification

Reviewed the submitted implementation in an isolated archive; the final delta
changed only the distribution verifier and an environment test. Applied those
exact two tracked files to the isolated product and reran affected full checks.
Shared product source and branch were not changed by review.

From isolated works/:

- Locked uv sync succeeded.
- At both initial/final revisions: 308 portable tests passed, zero skips, one
  deliberate native deselection; 99.72% product coverage, all 34 branches.
- Ruff lint/format and checksum-pinned actionlint passed.
- Wheel/sdist built successfully; final distribution verifier passed 23 checks.
  Clean wheel/sdist installs verify the sole git_harness package and sole
  git-harness console entry point, installed APIs and resources, module help,
  isolated uvx and private uv tool install. Actual git-harness and native
  git harness --version/-h work outside repositories with clean HOME/Git config.
- Maintained product/workflow/root instructions/current specs audit has no
  former project names. Final correction removes even obsolete negative-test
  literals; exact current package/entrypoint checks remain.
- Public configuration reads only GIT_HARNESS_DIR/FILE/HISTORY_MAX_SIZE.
  Default directory is .harness; agent.json and all other defaults are unchanged.
  No compatibility names, Git aliases or wrapper scripts were introduced.
- Current specs, task references and instructions use specs/current/git-harness/,
  works/src/git_harness/, the renamed managed block and native resource paths.
  Generated integration behavior remains assigned to future implementation;
  existing TypeScript placeholders make no support claim.
- Compared all 18 prior tasks with their pre-rename revision: IDs, roles,
  dependencies, executor/reviewer identity preserved. Accepted task execution
  and review sections are unchanged. Original AS-001/002/017 probes are unchanged.
  All four native dependency packages/versions/integrities are unchanged.
- GitHub API independently confirms neprel/git-harness ID 1472945224, original
  creation time, main and access rights. Origin is renamed; git ls-remote HEAD
  remains 4d45ddb64363b93f546e455698299423297fb046. Historical PR #1 is retained
  closed; current draft PR #2 is open. Repository-rename proof records the
  owner-resolved target collision. No history rewrite, tag or publication.

## Hosted evidence

Initial renamed manual Release
[45998469282](https://github.com/neprel/git-harness/actions/runs/45998469282)
succeeded at 2e4d2c8: all six portable jobs, workflow lint, four Linux native
foundation jobs, identity and build passed; publish was skipped.

Final corrected manual Release
[45998800861](https://github.com/neprel/git-harness/actions/runs/45998800861)
completed successfully at exact 3741287: all six portable jobs, lint, four native
foundation jobs, identity and artifact build passed. The corresponding final
[PR Release 45998807187](https://github.com/neprel/git-harness/actions/runs/45998807187)
also passed at that same SHA. Both explicitly skipped publication.
Full native acceptance is deliberately skipped on build-only events and remains
incomplete in AS-018. Expected CI failures for its missing adapter/routes are
not rename regressions. Superseded metadata-push cancellations are not failures.

## Finding

No blocking rename defect found. All AS-019 acceptance criteria, including the
owner-requested maintained-content/history audit, are independently verified.
AS-019 accepted by reviewer/1; task moved to tasks/done/developer/AS-019.md.
Handoff recorded at agents/reviewer/1/HANDOFF.md. Reviewer stops per owner order. This review does not
accept AS-018 or certify native adapter/delivery/migration support. Owner-directed
physical folder rename and continuation remain owner actions.
