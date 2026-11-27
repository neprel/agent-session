# Verification and release

## R1 - Test strategy

Use pytest with temporary homes, mock executable commands, fake clock and fake adapter. Unit tests must not need AI credentials. Test malformed input, symlink aliases, hidden globs, atomic writes, stale PID reuse, concurrent init/stop, delayed hooks, duplicate triggers, approval states, timeouts, uncertain delivery, offline recovery and session switching. Use process-level tests for foreground/background and worker cleanup. Verify no LLM invocation by infrastructure. Use the native acceptance suite in R7. Do not use paid inference in any test. Test all 12 cross-harness migration routes and repeat round trips. Record evidence and explicit omissions. Never use user transcripts or secrets as test fixtures.

## R2 - Documentation

`works/README.md` includes installation with uv/uvx, config/trust steps, normal and nested layout, all commands, examples, compatibility matrix, background processes, stop semantics (does not kill harness), Git/privacy, enabling sync and limitations. Include license and third-party notices. Document adapter addition in a short developer section. Verify examples against actual CLI. Do not claim universal support.

## R3 - Release gate

Run tests and build wheel/sdist. Verify packaged resources, entry points and license notices. Install wheel in clean environment; run help, prime and fake adapter tests. Verify PyPI name and publish credentials without printing or storing secrets. Use GitHub Actions and PyPI Trusted Publishing in accordance with R8 and R9. Publishing is an external action requiring explicit owner approval. Do not publish merely because implementation tasks are accepted.
## R4 - Architecture tests

Verify that all ten commands have separate modules and implement Command. Verify that all four harnesses have separate packages and implement Harness. Run a fake command through the common CLI. Run a fake harness through discovery, probe, launch planning, delivery, portable history read/write and configuration. Do not require changes to common services to register the fake harness. Verify that core code has no concrete harness imports outside the explicit registry. Verify all native resources are available from the installed wheel. Document the two interfaces and the procedure to add a command or harness.

## R5 - Defaults and configuration tests

Test every default in FEATURE-001 R6. Test all three environment variables when unset, overridden, empty and invalid. Verify help and actual behavior use the same defaults. Test non-destructive configuration merge, including existing hook arrays, repeated configuration, invalid JSON and dry-run. Verify the wheel does not contain Codex or Claude JSON configuration templates.

## R6 - Portable test suite

Use pytest. Keep test dependencies in the development dependency group. Commit `works/uv.lock`. Run product commands from `works/`. Separate tests into unit, integration and native groups. The default `uv run --locked pytest` runs the unit and synthetic integration groups without installed harnesses, tmux, model credentials, a GPU or a local model. Use explicit opt-in for native tests. Do not skip required tests because a harness is absent from the default environment.

Use synthetic records for all four harnesses. Include native history, tool calls and results, compaction, branches, invalid records, lifecycle payloads and endpoint responses. Pin the fixture format and version. Use temporary home, configuration, state and workspace directories. Do not read the user's real sessions, credentials, hooks or tmux server. Use fake executables on a controlled PATH, fake HTTP/socket services, a fake clock and real temporary files and worker processes as applicable. Test the actual adapter logic, not only the fake Harness interface.

Test all ten commands, all public options and defaults, all environment variables, output, exit codes, all supported event formats, all adapters, safety and failure paths. Test all 12 ordered cross-harness routes with synthetic fixtures and independent target parsing. Test repeated synchronization, crash recovery, conflicts, history rotation, ownership and no duplicate events. Verify source history remains unchanged. Test actual installed CLI entry points and packaged integration resources.

Maintain a requirement-to-test map in `works/docs/testing.md`. Measure branch coverage with a development-only coverage tool. Require at least 85% total branch coverage of product code. Coverage does not replace requirement tests. Do not exempt a module to meet the threshold. Document justified exclusions. Fail CI on a failed required test, unexpected skip or coverage below the threshold.

## R7 - Native acceptance without inference

Use the MIT-licensed session-migrate test provider and synthetic fixture techniques as source references. Inspect tests/offline_provider.py and native test scripts at the reviewed revision. Reuse only required code and retain notices. Keep the provider under `works/tests/support/`. Do not include it in the runtime package.

Run actual pinned harness executables against a deterministic loopback HTTP provider. Support the OpenAI Chat Completions and Responses protocols and Anthropic Messages protocol only as needed by the tested clients. Implement required streaming, tool-call, tool-result and terminal events. Return fixed responses. Record requests and verify the imported conversation reaches the receiving client, a new turn completes and native history can be read again. Use no model inference, real or simulated credentials for external services, or external provider requests. Dummy credentials are local test values only. Reject unexpected endpoints and requests. Add tests for provider errors, timeouts and malformed events.

Provision exact harness versions and any native prerequisites on clean GitHub runners. Use verified download sources and hashes where available. Do not depend on preinstalled user harnesses. Use an isolated tmux server or PTY where necessary. Deny non-loopback network access for the native test execution, including child processes. Verify the deny rule. Separate dependency installation from offline execution. If a platform cannot enforce isolation, do not run the native harness there; report this limitation. Do not pass real credentials, OAuth state or provider secrets to tests. Fail if a test attempts an external provider connection. Terminate all child processes after each test.

For each of Codex, Claude, OpenCode and Pi, verify discovery, config installation, hook/plugin startup and shutdown, registration, native delivery, idle wake, busy queue, check, run/resume and safe cleanup. Verify actual native loading and appending for all 12 cross-harness routes. Use a receiving harness matrix if useful. Test clean and nested project layouts. Required native gates must not silently skip. An unavailable interface or unprovisionable harness blocks the corresponding support claim and release until resolved or the owner approves a scope change. A synthetic pass is not proof of native compatibility.

Optional local smoke tests may use installed OpenCode and Pi on macOS and an explicitly configured local model. Run them only on request, with no cloud fallback. They are not required for CI or release and must not access the user's real history. No test may spend paid inference tokens.

## R8 - GitHub Actions CI

Use free standard GitHub-hosted runners for the public repository. Add `.github/workflows/ci.yml` at the repository root. Run product steps from `works/`; resolve cache, report, script and distribution paths from that directory. Run on pull_request, push to the default branch and workflow_dispatch. Use ubuntu-latest and macos-latest for the default portable suite. Test Python 3.11, 3.12 and 3.13 on each. Test any additional Python version advertised as supported before release. Windows is not a release requirement.

Use the official setup-uv action. Pin all external actions to reviewed full commit SHAs and pin uv and native client versions. Use uv sync --locked --dev and uv run --locked pytest. Run lint, requirement coverage, architecture tests and package build/install checks. Run the required native acceptance matrix on provisioned Linux runners; test macOS native support before advertising it (use isolated macOS hosted runners where feasible, otherwise report a local verification gate). Upload concise test reports and sanitized diagnostics. Do not upload real histories, credentials, or agent session state. Use contents: read, no id-token permission and no publishing secrets. Do not use pull_request_target to execute untrusted code. Set finite job timeouts. Do not require a self-hosted runner.

## R9 - GitHub release and Trusted Publishing

Add `.github/workflows/release.yml` at the repository root. Build and test from `works/`; use `works/pyproject.toml` for the version and `works/dist/` for distribution artifacts. Trigger publication only on a pushed version tag vX.Y.Z (or a documented valid prerelease tag). Allow a manual build-only dry run without publication. Verify the tag equals the package version and its commit belongs to the protected default branch. Require successful tests for the exact release commit, including the native acceptance gates for the advertised support. Build wheel and sdist with uv build. Verify metadata, licenses, entry points and TypeScript resources. Install and smoke-test both distributions in clean environments. Upload the exact tested distributions as one workflow artifact.

Use a separate publish job on ubuntu-latest. Depend on all release gates. Use the GitHub environment pypi with required owner approval and restricted version tags. The publish job alone has id-token: write. Download only the distributions from this workflow run. Use the official PyPA pypi-publish action with a reviewed full commit SHA. Do not rebuild, check out or execute project code in the publishing job. Do not configure a PyPI API token. Keep publishing attestations enabled. Do not overwrite or silently skip an existing release version. Prevent concurrent publication of the same version. Create a GitHub Release only after successful publication, if the owner requests it.

Document the setup in this specification package's PUBLISHING.md and `works/PUBLISHING.md`. The owner creates the GitHub environment and the PyPI Trusted Publisher. Do not publish, create a release tag, or change account settings without explicit owner approval. Verify the package name before publishing. Report pending owner actions separately from implementation completion.
