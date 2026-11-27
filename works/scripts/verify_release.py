"""Validate release identity and owner-controlled safeguards; never publishes."""

import json
import os
import re
import subprocess
import tomllib
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

PUBLICATION_NAME_APPROVED = False  # Occupied PyPI name; owner-approved change is pending.


def release_identity(event: str, ref: str, sha: str, version: str) -> bool:
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("release commit must be a complete commit SHA")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("only stable X.Y.Z releases are configured")
    if event in {"workflow_dispatch", "pull_request"}:
        return False
    if event != "push" or ref != f"refs/tags/v{version}":
        raise ValueError("release tag must exactly match the package version")
    return True


def read_json(url: str):
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "agent-session-release-check",
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.load(response)


def verify_owner_guards(branch: dict, environment: dict, policies: dict) -> None:
    if not branch.get("protected"):
        raise ValueError("owner must protect the default branch before publication")
    reviewers = [
        reviewer.get("reviewer", {}).get("login")
        for rule in environment.get("protection_rules", [])
        if rule.get("type") == "required_reviewers"
        for reviewer in rule.get("reviewers", [])
    ]
    if "neprel" not in reviewers or environment.get("can_admins_bypass") is not False:
        raise ValueError("pypi environment must require owner approval without admin bypass")
    restriction = environment.get("deployment_branch_policy") or {}
    entries = policies.get("branch_policies", [])
    if (
        not restriction.get("custom_branch_policies")
        or not entries
        or any(
            p.get("type") != "tag" or p.get("name") not in {"v*", "v[0-9]*.[0-9]*.[0-9]*"}
            for p in entries
        )
    ):
        raise ValueError("pypi environment must restrict deployment to version tags")


def verify_repository(sha: str, branch: str, *, tagged: bool) -> None:
    def git(*args):
        return subprocess.check_output(["git", *args], text=True, timeout=30).strip()

    if git("rev-parse", "HEAD") != sha:
        raise ValueError("checkout does not match the tested release commit")
    if tagged:
        git("check-ref-format", "--branch", branch)
        git("fetch", "--no-tags", "origin", f"+refs/heads/{branch}:refs/remotes/origin/{branch}")
        git("merge-base", "--is-ancestor", sha, f"refs/remotes/origin/{branch}")


def main():
    project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
    version = project["version"]
    if project["name"] != "agent-session":
        raise ValueError("distribution name changed; owner review is required")
    sha = os.environ["GITHUB_SHA"]
    tagged = release_identity(
        os.environ["GITHUB_EVENT_NAME"], os.environ["GITHUB_REF"], sha, version
    )
    if tagged and not PUBLICATION_NAME_APPROVED:
        raise ValueError("publication is blocked pending the owner-approved distribution name")
    repository = os.environ["GITHUB_REPOSITORY"]
    if repository != "neprel/agent-session":
        raise ValueError("release repository does not match the owner configuration")
    branch = os.environ["DEFAULT_BRANCH"]
    verify_repository(sha, branch, tagged=tagged)
    if tagged:
        api = f"https://api.github.com/repos/{repository}"
        verify_owner_guards(
            read_json(f"{api}/branches/{quote(branch, safe='')}"),
            read_json(f"{api}/environments/pypi"),
            read_json(f"{api}/environments/pypi/deployment-branch-policies"),
        )
        try:
            read_json(f"https://pypi.org/pypi/agent-session/{version}/json")
        except HTTPError as exc:
            if exc.code != 404:
                raise
        else:
            raise ValueError("release version already exists on PyPI; refusing replacement")
    print(
        json.dumps(
            {"commit": sha, "version": version, "mode": "tag-release" if tagged else "build-only"}
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"release_gate_failed: {exc}") from exc
