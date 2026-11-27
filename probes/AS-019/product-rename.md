# AS-019 product rename verification

Implemented owner-approved full Git Harness rename in `works/` and root release workflow. Distribution/executable `git-harness`, package `git_harness`, default `.harness`, unchanged `agent.json` and remaining defaults. Only GIT_HARNESS_DIR/FILE/HISTORY_MAX_SIZE are read. No aliases or wrapper added. TypeScript placeholders remain placeholders; no lifecycle implementation was added.

## Local verification

From `works/`, Python 3.12.13:
- `uv sync --locked --dev` succeeded after regenerating lock metadata with uv.
- `uv run --locked ruff check src tests scripts` passed.
- `uv run --locked python scripts/lint_workflows.py` passed actionlint 1.7.12.
- `uv run --locked pytest -q --tb=short`: 308 passed, zero skips, one opt-in native test deselected; combined coverage 99.72%, all 34 branches covered.
- `uv build` built wheel and sdist.
- `uv run --locked python scripts/verify_distribution.py`: 23 checks passed; see distribution-verification.json. Clean wheel/sdist runtime installs, installed API tests, module entry point, uvx local wheel, private uv tool install, and actual `git harness --version`/`-h` passed. The temporary cwd is outside any Git repository (verified with git rev-parse); HOME/Git config/tool directories are private. Only one console entry point exists; old import/executable absent in clean installs.

## Maintained-content audit

Audited `works/src`, tests, scripts, docs, README, publishing guide, metadata/lockfile and `.github/workflows` for old names and registration directory. Remaining old product tokens occur only in explicit negative assertions for removed executable/import/environment variables. `session-migrate` license names and native session model attributes are unrelated names and preserved. Native lock root labels changed; dependency versions/integrities did not. Original upstream fixture payloads and historical probes/tasks/reviews were preserved. Generated build/venv/cache files are excluded from the audit and delivery.

The old occupied-name release blocker was removed after owner approval. Native acceptance and owner-controlled release safeguards still fail closed; no tags, packages or account settings were changed. Read-only https://pypi.org/pypi/git-harness/json returned HTTP 404 on 2026-11-27 (not a reservation). Repository identity evidence is manager-owned repository-rename.json.

Hosted results and exact source commit will be appended after branch publication. AS-003 remains paused; owner requires handoff and stop after AS-019 acceptance.
