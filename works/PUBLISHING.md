# Owner publishing guide

The owner approved the Git Harness name: PyPI distribution and executable
`git-harness`, Python package `git_harness`, repository `neprel/git-harness`.
The manager verified the repository rename preserves its identity and history.
The PyPI project endpoint returned HTTP 404 on 2026-11-27; this does not reserve
the name. Publication remains blocked by incomplete native acceptance and owner
release settings. No package, tag, release, merge or account-setting change is
authorized by these instructions alone.

## Workflow behavior

Root `.github/workflows/ci.yml` runs the Linux/macOS Python 3.11/3.12/3.13
portable matrix, workflow lint, builds/clean installs, pinned Linux native
provisioning/version checks and separate required native acceptance gates.
Native acceptance currently fails explicitly: adapter lifecycle/delivery/resume
and all 12 cross-harness tests are not implemented. A version-only pass never
satisfies that gate. Keep AS-018 open until the real native matrix passes.

`release.yml` builds and verifies distributions on a manual `workflow_dispatch`.
For infrastructure review, relevant pull requests exercise the same build-only
path. These events cannot enter the publish job, even with a tag-like ref.
New workflow files may require default-branch registration before GitHub accepts
a manual dispatch; a PR build does not prove manual-dispatch registration.

Only a pushed stable `vX.Y.Z` tag can request publication. Tag identity must
match `works/pyproject.toml`, checkout must match the event SHA, and the commit
must belong to the protected default branch. The tag path also verifies the
existing `pypi` environment requires owner review, forbids admin bypass and
restricts deployments to version tags. Missing owner settings fail the gate;
the workflow does not create them. Existing PyPI versions cannot be replaced.
Prerelease publication is not configured.

Both paths rerun the portable and pinned-native foundation jobs for the exact
commit, build wheel/sdist and verify clean installs, licenses, resources and
development-code exclusions. Tag publication additionally requires completed
native acceptance for every client/route. The build uploads exactly its tested
wheel and sdist as `distributions-COMMIT`; no rebuild occurs in the publish job.

The publish job alone requests `id-token: write`, uses environment `pypi`,
downloads that artifact from the same run and calls the official PyPA publishing
action with attestations enabled and `skip-existing: false`. It does not check
out or execute project source. No long-lived PyPI token is used. Release
concurrency prevents concurrent publication for the same tag. No GitHub Release
is created automatically.

Workflows use JSON-compatible YAML so policy tests need no additional parser
dependency. All external actions are pinned to reviewed complete commit SHAs;
uv is fixed at 0.13.0 with checksum enforcement. actionlint 1.7.12 is downloaded
with a fixed archive checksum. Native versions/locks remain repository-only.

## Owner setup after release-candidate acceptance

Confirm `neprel/git-harness` is still the intended public repository and that
the approved distribution name, import name and executable match the approved
specification. Protect `main`, require the complete CI gates, restrict workflow/tag
changes and keep default workflow permissions read-only.

Create the GitHub environment `pypi` with required reviewer `neprel`, admin bypass
disabled, and custom deployment policy permitting only version tags (`v*`). If
the owner is the sole reviewer, self-review must remain possible. Do not add a
PyPI API token. These settings are owner actions; no workflow configures them.

On PyPI, create the Trusted Publisher for the approved name `git-harness` with
GitHub owner `neprel`, repository `git-harness`, workflow filename `release.yml`
and environment `pypi`. A pending publisher does not reserve a name. Resolve any
collision before publication; never silently rename or use another account's
project. Account setup and publication require separate explicit owner approval.

Run CI and the manual build-only workflow, inspect exact commit/run reports and
distributions, and complete the native adapter/all-route acceptance. Only after
AS-016 acceptance and owner approval may an authorized operator create/push the
matching release tag. Approve the `pypi` deployment only for the reviewed tested
artifact. Inspect partial-upload failures; do not enable blanket skip-existing
or overwrite/delete releases automatically.

## Local review

From `works/`:

```sh
uv sync --locked --dev
uv run --locked pytest
uv run --locked python scripts/lint_workflows.py
uv build
uv run --locked python scripts/verify_distribution.py
```

CI uploads aggregate counts/branch coverage only, not native homes, request
bodies, transcripts, auth stores or raw process traces. Linux native execution
uses fresh homes and isolated network/PID namespaces with syscall auditing.
macOS native execution remains unavailable; its portable suite is independent.

References: [uv GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/),
[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/using-a-publisher/),
[GitHub environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments).
