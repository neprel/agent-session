# Project

agent-session is a deterministic CLI for managing and communicating with coding agent sessions.

## Workspace

- `specs/`: current specifications, proposed changes and archived changes.
- `tasks/`: planned, assigned, submitted and completed work.
- `agents/`: agent roles and instances.
- `src/`: product source code.
- `tests/`: product tests.

All paths in instructions and task documents are relative to the repository root unless specified otherwise.

## Team

- `manager`: plan, assign and coordinate work.
- `developer`: implement and verify assigned work.
- `reviewer`: independently review and accept work.

Your launch directory identifies your role and instance. Instructions for other roles do not apply to you.

## Specifications

- `specs/current/`: approved product specifications.
- `specs/changes/`: proposed changes to specifications.
- `specs/archive/`: completed or cancelled specification changes.

Read `SPEC.md`, `TASK.md` and the relevant feature specifications before starting work.

Follow approved requirements, interfaces and default values.

Create proposed specification changes in `specs/changes/`.

The manager coordinates specification changes. The reviewer verifies them. The owner approves them before implementation.

After all related tasks are accepted, the manager updates the current specifications and moves the completed change to `specs/archive/`.

Do not modify current specifications directly without owner approval.

Do not implement unapproved changes.

Do not use archived specifications as current requirements.

Report contradictions and missing requirements to the manager.

## Tasks

The task location defines its lifecycle state:

- `tasks/work/{role}/.unassigned/`: unassigned work.
- `tasks/work/{role}/{instance}/`: assigned work.
- `tasks/review/{role}/.unassigned/`: unassigned review.
- `tasks/review/{role}/{instance}/`: assigned review.
- `tasks/done/{role}/`: accepted work.

Preserve task IDs, dependencies, executor identity, reviewer identity and review history.

A dependency is satisfied only when its task is in `done/`.

Move task files atomically. Do not overwrite another task.

Return rejected work to its original executor. Return corrected work to its original reviewer.

## Execution

- Execute only work authorized for your role.
- Continue with eligible work until no actionable work remains.
- Do not stop after an intermediate step.
- Record blockers and continue independent work when possible.
- Record results and evidence in task files.
- Do not mark unverified work as complete.
- Do not approve your own work.
- Do not make unrelated changes.

## Engineering

- Keep the implementation simple and deterministic.
- Follow the specified command and harness interfaces.
- Keep harness-specific logic inside its harness implementation.
- Do not introduce additional dependencies without justification and approval.
- Preserve existing user configuration.
- Do not guess native harness behavior. Verify it.
- Reuse applicable session-migrate source code. Preserve required license notices.
- Use uv for dependency management, execution and builds.
- Use isolated tests and mock endpoints where possible.
- Do not consume paid inference resources for tests without approval.
- Do not publish packages without owner approval.

## Communication

Use task files as the source of truth.

Use concise, direct language. Follow ASD-STE100 principles.

Report completed work, blockers, decisions and unresolved issues. Do not repeat information already recorded in task files.

Do not depend on agent-session for coordination until its implementation has been verified.
