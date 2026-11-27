# AS-002 independent review

Reviewer: reviewer/1. Date: 2026-11-27.
Exact submission: `3d2207855676d1e3ce79490e4627567ecfc644d9`.
The submitted product, probe files and task matched that revision before review.
Dependency AS-001 is accepted in tasks/done/developer/AS-001.md.

## Verification

Executed from `works/`:

- `uv sync --locked --dev --python 3.12`: passed.
- `uv run --locked pytest`: 226 passed, no skips; 99.72% combined coverage,
  all 34 measured branches covered. Every product module is measured.
- `uv run --locked ruff check src tests`: passed.
- `uv run --locked ruff format --check src tests`: 39 files formatted.
- `uv build`: wheel and sdist built.
- `uv run --locked python ../probes/AS-002/verify_distribution.py`: all 15
  checks passed. Includes separate clean wheel/sdist installation, installed
  entrypoints and fake-interface tests, package resources/notices, runtime
  dependency boundaries and isolated local-wheel uvx invocation.
- `git diff --check`: passed.

Independently inspected all command modules, parser/dispatcher, defaults and
validators, common Harness/request/result contracts, portable model, registries,
native scaffolds, tests, package configuration, interface/test documentation and
provenance notices. Compared with SPEC and FEATURE-001/003/005/006/011.

## Acceptance criteria

All ten separate command modules implement Command, expose help and validate
shared/specific parameters. CLI code contains parser setup, dispatch and common
error handling. Shared defaults and package environment snapshots cover the
approved contract; automatic native values remain absent pending discovery.
Tests exercise omitted/explicit/invalid options, help and environment settings.

All eight Harness methods have typed contracts. The fake command/harness tests
exercise explicit registration, discovery, probe, launch plans, delivery,
portable history, configuration and native option declaration without changing
core dispatch. Native-format logic is absent from common services. The portable
model includes source identity, tools/results, images, summaries, cursor/loss and
projection values with the required upstream MIT notice.

Locked uv packaging, runtime/development dependency separation, pytest groups,
portable isolation and coverage configuration satisfy this foundation task.
No unapproved runtime dependency, native support claim or LLM call was found.

No blocking defect found. Accept AS-002. Builtin command execution and native
adapters explicitly return unsupported; service/adapter implementation, full
synthetic/provider infrastructure, native gates and CI remain later tasks.
This scoped acceptance does not accept those future behaviors. No product code,
requirements or acceptance criteria were changed during review.
