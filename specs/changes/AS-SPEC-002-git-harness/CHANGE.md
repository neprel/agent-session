# AS-SPEC-002: Git Harness

Status: owner approved on 2026-11-27; implementation and independent review pending.
Related task: AS-019.

Use Git Harness as the product; git-harness as repository, distribution and executable; git_harness as Python package; and git harness through native Git external command discovery. The default registration directory is .harness; agent.json stays unchanged. Public variables are GIT_HARNESS_DIR, GIT_HARNESS_FILE and GIT_HARNESS_HISTORY_MAX_SIZE. Preserve other behavior/defaults. Add no compatibility aliases, legacy configuration names, Git aliases or wrapper scripts. The utility must work outside a Git repository.

The owner authorized repository rename through authenticated gh after owner/identity verification, remote/URL/metadata updates, and preservation of repository history, issues and settings. Existing target-name collision requires a separate owner decision; no other repository may be overwritten or removed.

Update current specs, task requirements/references, instructions, product source/tests/docs/config, lifecycle resources, workflows and publishing instructions. Keep task IDs, dependencies, assignments, execution reports, original probes, upstream evidence and review history. Historical evidence retains its original names/paths. No Git history rewrite, nested Git repository, release tags or publication.

Current approved specs are in specs/current/git-harness/. Runtime package path is works/src/git_harness/. Product commands run from works/. Root workflows remain in .github/workflows/.

Verification: obsolete-name audit of maintained content with explicit historical-evidence exclusions; full applicable tests; locally built wheel/sdist clean installs; uvx/tool install; standalone and native Git subcommand tests outside Git repositories; GitHub identity/access/remote check; independent reviewer acceptance. Recheck PyPI name before release.

## Owner approval

Owner supplied these complete rename requirements in response to the naming decision on 2026-11-27. This supersedes AS-SPEC-001.

## Independent review

Pending reviewer/1 after AS-019 submission.
