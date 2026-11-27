# Owner guide: GitHub Actions and PyPI

This guide applies after AS-018 implements the workflows and AS-016 verifies the release candidate. Do not publish until the owner approves. Use the actual GitHub repository owner and repository name. No PyPI API token is necessary. Workflow files stay in `.github/workflows/`; product build and test steps run from `works/`.

## 1. GitHub repository

1. Keep the repository public to use free standard GitHub-hosted runners.
2. In Settings > Actions > General, enable the required actions. Keep the default workflow token read-only.
3. Protect the default branch and require the CI checks. Restrict changes to release workflow files to trusted maintainers. Restrict creation of release tags to trusted maintainers with rulesets where available.
4. Open Settings > Environments. Create an environment named `pypi`.
5. Add the owner as a required reviewer. Restrict deployment to version tags that match the release workflow. Disable administrator bypass where available. Do not enable prevention of self-review if the owner is the only person who can approve the deployment. Do not store a PyPI token in this environment.
6. Run `ci.yml` and the build-only manual path of `release.yml`. Make sure they pass without model credentials.

## 2. PyPI account

If `git-harness` does not yet exist on PyPI, sign in and open https://pypi.org/manage/account/publishing/. Add a pending GitHub Actions publisher. If the owner already controls the project, open the project's Manage > Publishing page instead.

| Field | Value |
|---|---|
| PyPI project name (pending publisher only) | `git-harness` |
| Owner | Actual GitHub repository owner (user or organization) |
| Repository name | Actual repository name, for example `git-harness` |
| Workflow name | `release.yml` (filename only) |
| Environment name | `pypi` |

Select Add. Make sure the values match the workflow exactly. A pending publisher does not reserve a project name. If another account owns the name, stop and resolve the name conflict with the owner. Do not change the distribution name automatically.

## 3. First release and subsequent releases

1. Verify the release commit, test reports, compatibility claims, license notices and package version in `works/pyproject.toml`.
2. Confirm that the commit is on the protected default branch. Obtain owner approval before creating a tag.
3. For version 0.1.0, the owner (or an explicitly authorized release operator) can run:

```bash
git tag -a v0.1.0 -m "Release 0.1.0"
git push origin v0.1.0
```

4. Open Actions and select the release workflow. Wait for the test and build jobs to pass. Inspect the distribution artifact. Review the `pypi` deployment and approve it only if the release is correct.
5. The publish job obtains a short-lived credential through GitHub OIDC. It uploads the tested wheel and sdist using the PyPA publishing action. The first successful publication activates the pending publisher.
6. Verify the release on PyPI. Test installation in a clean environment with `uvx git-harness@0.1.0 --help` and `uvx git-harness@0.1.0 prime`.

If a release fails, inspect the workflow before retrying. PyPI does not permit replacement of an existing distribution filename. If a partial upload has occurred, do not use a blanket skip-existing policy. Resolve the release state explicitly; a new version may be necessary. Never delete or overwrite a version automatically.

## References

- https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/
- https://docs.pypi.org/trusted-publishers/adding-a-publisher/
- https://docs.pypi.org/trusted-publishers/using-a-publisher/
- https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments
- https://docs.astral.sh/uv/guides/integration/github/
