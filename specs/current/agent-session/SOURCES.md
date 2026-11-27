# Technical references

Use these references to verify the current native interfaces before implementation. Pin tested versions and the upstream source revision. Do not assume a documented interface works in every runtime configuration.

- https://github.com/xhluca/session-migrate — source reference for portable history, readers/writers and native validation.
- https://github.com/xhluca/session-migrate/blob/main/docs/architecture.md — installation, loss accounting and privacy boundaries.
- https://learn.chatgpt.com/docs/hooks — Codex hooks and trust.
- https://github.com/openai/codex/issues/63991 — idle TUI queue issue; verify wake behavior.
- https://code.claude.com/docs/en/hooks — Claude lifecycle hooks.
- https://code.claude.com/docs/en/channels — Claude external event mechanism.
- https://opencode.ai/docs/plugins/ — OpenCode plugin configuration.
- https://opencode.ai/docs/build/plugins/cli/ — TUI plugin API and session routes.
- https://opencode.ai/docs/server/ — native server API (check version).
- https://github.com/earendil-works/pi — Pi source and extension/session docs.
- https://docs.pi.dev/latest/extensions — Pi extension APIs.
- https://pypi.org/project/unique-namer/ — name and suffix generation.
- https://github.com/gorakhargosh/watchdog — filesystem events.
- https://github.com/pallets-eco/croniter — cron.
- https://psutil.readthedocs.io/ — process identity.
- https://docs.astral.sh/uv/ — tooling and release.

MIT permits use and modification subject to retaining copyright and license notices. Preserve provenance for reused source. No source code is copied into this specification package.

## CI, testing and publication

- https://github.com/xhluca/session-migrate/blob/main/docs/development.md — synthetic fixtures, offline provider and pinned native acceptance.
- https://github.com/xhluca/session-migrate/blob/main/tests/offline_provider.py — source reference; inspect and pin before reuse.
- https://docs.astral.sh/uv/guides/integration/github/ — uv setup, locked tests and build.
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job — public hosted runners.
- https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments — release approval environment.
- https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/ — pending publisher.
- https://docs.pypi.org/trusted-publishers/adding-a-publisher/ — existing project publisher.
- https://docs.pypi.org/trusted-publishers/using-a-publisher/ — OIDC publish workflow.
- https://docs.pypi.org/trusted-publishers/security-model/ — least privilege.
- https://docs.pypi.org/attestations/producing-attestations/ — release attestations.
