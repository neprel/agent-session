# AS-SPEC-001: resolve the PyPI distribution name

Status: independently reviewed; owner approval pending.
Manager: manager/1. Date: 2026-11-27.
Related tasks: AS-018, AS-016.

## Problem

PyPI already contains agent_session 0.1.0, owned by yihanc, with source at yingluosanqian/agent_session. PyPI normalizes underscores and hyphens, so the approved distribution name agent-session conflicts. See [PyPI](https://pypi.org/project/agent_session/) and probes/AS-018/pypi-name-check.json. No ownership by this project is established.

## Proposed decision

Use `agent-session-cli` as the distribution name. Keep the `agent-session` executable, `agent_session` import and neprel/agent-session repository. The candidate PyPI JSON endpoint returned 404 on 2026-11-27. Recheck before release; this does not reserve the name or guarantee PyPI acceptance.

Use explicit tool invocation: `uvx --from agent-session-cli agent-session`. Use `uv tool install agent-session-cli` for a persistent install. Hooks use the installed or cached, version-pinned agent-session executable as already required.

If the owner controls the existing PyPI project, retain the approved name only after confirming that ownership and choosing an unused release version; 0.1.0 already exists. Do not overwrite or skip an existing release.

## Specification changes after owner approval

- FEATURE-001 R1: distribution is agent-session-cli; executable is agent-session; import is agent_session.
- FEATURE-006: use `uvx --from agent-session-cli agent-session` in managed instructions and prime examples. Preserve the existing word limits and semantics.
- PUBLISHING.md and product release documentation: PyPI project and project URL use agent-session-cli. GitHub repository, release workflow filename and environment stay neprel/agent-session, release.yml and pypi.
- Update install examples and distribution assertions in the related implementation tasks.

This proposal changes no lifecycle, transport, history, option, environment or testing requirement. Do not implement it before owner approval. Preserve existing task IDs, dependencies, assignments and review history.

## Verification

- Recheck the candidate name on PyPI before publication.
- Independently verify metadata, wheel/sdist filenames, Trusted Publisher values and docs.
- Build and clean-install both artifacts; test both entry points and the explicit local-wheel uvx invocation.
- Verify managed instructions/prime word limits and command examples.
- Do not create tags, publish or change account settings.

## Independent review

Accepted for owner decision by reviewer/1 on 2026-11-27. No blocking issue.

Independent verification of the live PyPI JSON endpoints reproduced the recorded
evidence: `agent-session` returns HTTP 200, canonical name `agent_session`,
version `0.1.0`, owner `yihanc` and the unrelated repository; `agent-session-cli`
returns HTTP 404. The [PyPA normalization specification](https://packaging.python.org/en/latest/specifications/name-normalization/)
confirms the hyphen/underscore collision. The [uv tool documentation](https://docs.astral.sh/uv/guides/tools/#commands-with-different-package-names)
confirms explicit `--from` invocation when executable and distribution differ;
version pins belong on the distribution, for example
`uvx --from 'agent-session-cli==0.1.0' agent-session --help`.

The proposal is feasible and complete for a distribution-only change. It names
metadata, artifact filenames/assertions, installation/managed instructions and
Trusted Publisher documentation as verification targets. Executable, import,
repository, workflow/environment identifiers, existing behavior and test gates
remain unchanged. Existing managed-block and prime word limits still apply.
A 404 is availability evidence only; recheck before release as proposed.

Owner approval is still required before implementation or current-spec changes.
No product/current-spec files, tags, account settings or publication changed in
this review. Reviewer thread: `01a21c91-08df-7840-9f1c-123aca6c8794`.


## Owner decision

Pending.
