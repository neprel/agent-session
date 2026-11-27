# Implementation coordination

Manager: manager/1. Updated: 2026-11-27.

## Authority and baseline

Use specs/current/agent-session and task dependency metadata. The 18 task IDs are unique; all dependencies exist; the graph is acyclic. No tasks are accepted at startup. Existing LICENSE changes and untracked workspace instructions/specifications are owner input; preserve them. Do not create release tags, publish, change account settings or use paid inference.

## Execution order

Assign only when dependencies are in tasks/done/developer. Use one shared checkout sequentially; do not run concurrent implementation here.

1. AS-001: verified native contracts, session-migrate revision/license and offline-provider plan.
2. AS-002: package, CLI and shared typed contracts.
3. AS-017: isolated testing foundation immediately after AS-002.
4. AS-018: CI and release workflow foundation as soon as AS-017 is accepted. Complete native matrix as adapters become available.
5. AS-003: registration, followed by AS-004, AS-005 and AS-008 as eligible.
6. AS-009 and AS-010; AS-006 and AS-007 when shared transport/worker dependencies are accepted.
7. AS-011 through AS-014: harness adapters with pinned native evidence.
8. AS-015: all 12 native and synthetic routes, lifecycle and recovery.
9. AS-016: independent release candidate verification.

The order within a step can change to preserve work continuity. Dependency metadata remains authoritative. AS-018 can be submitted only with evidence for its acceptance criteria; deferred native completion must remain explicit and must not be marked accepted prematurely.

## Review and continuity

Every implementation task requires reviewer/1 acceptance. Developer records execution evidence before moving to review; reviewer records findings before accepting or returning to the original executor. No self-approval. Manager assigns newly eligible work after acceptance and wakes idle agents through native codex_tui messaging. Keep requests concise and task files authoritative.

## Verification gates

- Default portable suite requires no harness, tmux, credentials, GPU or model. Temporary homes, controlled PATH, synthetic fixtures, fake clocks/processes and local mock endpoints are mandatory.
- Native clients use pinned versions, loopback mock-provider tests and verified non-loopback egress denial. No paid inference. Unsupported native interfaces block corresponding support claims and release unless the owner approves a specification change.
- Reuse applicable session-migrate code with pinned provenance and MIT notices. No new runtime dependencies beyond approved requirements.
- CI: Linux/macOS, Python 3.11/3.12/3.13, locked uv, lint, at least 85% branch coverage, required tests without unexpected skips, wheel/sdist clean-install checks.
- Release: exact commit gates, build-only dry run, tested artifact handoff, separate OIDC publish job, owner-approved pypi environment, no long-lived token.
- Owner setup values: neprel/agent-session; workflow release.yml; environment pypi. Read-only gh repository inspection confirmed PUBLIC visibility and main default branch on 2026-11-27. Recheck the remote before final handoff. Account setup and publication remain owner actions.

## Communications

Manager thread: 01a21c90-df87-74d2-9c7a-987776f2c652.
Developer launch: agents/developer/1, tmux 9:0.1.
Reviewer launch: agents/reviewer/1, tmux 9:0.2.

Native discovery initially returned no developer/reviewer threads. Read-only pane inspection confirmed both at their initial prompts. The owner explicitly authorized the first tmux prompt to initialize them; sent once to each. All subsequent coordination uses native codex_tui messaging. Both agents reported their role, exact launch directory and CODEX_THREAD_ID through native messaging. Native list_threads independently confirmed the directories. Manager replies were delivered successfully to both threads; native round trips are verified. No more tmux input is authorized or needed.

Developer thread: 01a21c90-ef19-7612-a747-b9520f062deb.
Reviewer thread: 01a21c91-08df-7840-9f1c-123aca6c8794.

## Current state

AS-001 accepted at 37fa8d2; AS-002 accepted at 2e8c092; AS-017 accepted at 2dabf33. All three are in tasks/done/developer. AS-018 assigned to developer/1 with reviewer/1 designated. Establish workflows and hosted-runner provisioning now. Keep full native matrix pending while adapters are implemented; preserve task state and continue independent AS-003 when infrastructure work is ready. AS-003 is dependency-eligible but remains unassigned until this initial CI work is coordinated. Other tasks remain unassigned.

## Known verification risks

AS-001 report is authoritative for details. Track the following during downstream task review:

| Finding | Follow-up tasks |
| --- | --- |
| Upstream provider does not handle Claude query-bearing Messages URL or complete required tool/error protocols | AS-017 |
| Installed OpenCode 2.2.7 is outside upstream 2.0.x converter gate; isolated child listener startup failed | AS-013, AS-018 |
| Installed Pi 1.6.1 system-role record is rejected by pinned reader | AS-014 |
| Upstream native client pins are candidates, not project support evidence | AS-017, AS-011 through AS-015 |
| Codex queue acceptance may not wake idle TUI; safe delivery needs actual evidence | AS-011 |
| Claude native Channels has authentication constraints; no socket protocol assumed | AS-012 |
| Full native lifecycle ownership, safe tmux prompt states and all 12 resume routes remain unverified | AS-011 through AS-015 |

Approved specifications permit exact tested version support. Do not widen compatibility gates without evidence. Recording research gaps in AS-001 does not waive downstream native release gates.

## Probe traceability

Owner updated workspace instructions during AS-002: investigations belong in probes/{task-id}/. Manager notified both agents and relocated AS-001 artifacts to probes/AS-001 with task links and original acceptance preserved. Reusable tests belong in works/tests/.

## Product root

Owner approved the works/ layout and corresponding current-specification path edits on 2026-11-27. Product source, tests, documentation, scripts and package/build configuration belong in works/. Run product commands there. Root .github/workflows/ runs steps in works/ and uses works/dist/. Keep agents/specs/tasks/probes outside; no nested Git. Developer moved active AS-002 source, tests, package configuration, notices and build ignore rules into works/. Product README and LICENSE copies are present; root files remain repository entry points. Manager verified no product source/config remains at root and only the root .git exists. Task metadata and review history remain unchanged.

## Read-only release setup check

On 2026-11-27, GitHub reported zero repository environments, no active rules for main, and no legacy branch protection. Owner setup remains pending: protected main/required CI, pypi environment with owner approval/tag restrictions, and matching PyPI Trusted Publisher. No account settings were changed. Implementation and CI preparation continue; request owner setup only with the concrete release handoff.
