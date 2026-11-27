import json
import subprocess
from pathlib import Path

import pytest

from scripts.report_ci import summarize, verify_requirement_map
from scripts.verify_release import release_identity, verify_owner_guards, verify_repository
from tests.support.acceptance import CASES, CLIENTS, acceptance_nodes

pytestmark = pytest.mark.unit
PRODUCT = Path(__file__).resolve().parents[2]
WORKFLOWS = PRODUCT.parent / ".github/workflows"
SHA = "a" * 40


def test_manual_and_pr_builds_cannot_be_publications_even_for_tag_like_refs():
    for event in ("workflow_dispatch", "pull_request"):
        assert release_identity(event, "refs/tags/v0.1.0", SHA, "0.1.0") is False
    assert release_identity("push", "refs/tags/v0.1.0", SHA, "0.1.0") is True


@pytest.mark.parametrize(
    "event,ref,sha,version",
    [
        ("push", "refs/heads/main", SHA, "0.1.0"),
        ("push", "refs/tags/v0.2.0", SHA, "0.1.0"),
        ("push", "refs/tags/v0.1.0", "abc", "0.1.0"),
        ("push", "refs/tags/v0.1.0rc1", SHA, "0.1.0rc1"),
        ("workflow_run", "refs/tags/v0.1.0", SHA, "0.1.0"),
    ],
)
def test_forged_release_identity_is_rejected(event, ref, sha, version):
    with pytest.raises(ValueError):
        release_identity(event, ref, sha, version)


def guards():
    return (
        {"protected": True},
        {
            "can_admins_bypass": False,
            "protection_rules": [
                {"type": "required_reviewers", "reviewers": [{"reviewer": {"login": "neprel"}}]}
            ],
            "deployment_branch_policy": {"custom_branch_policies": True},
        },
        {"branch_policies": [{"type": "tag", "name": "v*"}]},
    )


def test_owner_approval_and_tag_restriction_are_required_not_created_implicitly():
    branch, environment, policies = guards()
    verify_owner_guards(branch, environment, policies)
    for b, e, p in [
        ({}, environment, policies),
        (branch, {}, policies),
        (branch, {**environment, "can_admins_bypass": True}, policies),
        (branch, environment, {"branch_policies": [{"type": "branch", "name": "*"}]}),
        (branch, environment, {"branch_policies": []}),
    ]:
        with pytest.raises(ValueError):
            verify_owner_guards(b, e, p)


def test_exact_checkout_and_default_branch_ancestry_checks_use_argument_arrays(monkeypatch):
    calls = []

    def git(argv, **kwargs):
        calls.append(argv)
        assert kwargs["timeout"] == 30
        return SHA + "\n" if argv[1:3] == ["rev-parse", "HEAD"] else ""

    monkeypatch.setattr(subprocess, "check_output", git)
    verify_repository(SHA, "main", tagged=True)
    assert ["git", "merge-base", "--is-ancestor", SHA, "refs/remotes/origin/main"] in calls
    with pytest.raises(ValueError, match="checkout"):
        verify_repository("b" * 40, "main", tagged=True)


def test_public_reports_do_not_contain_failure_text_transcripts_or_stdout(tmp_path):
    xml = tmp_path / "report.xml"
    xml.write_text(
        '<testsuites><testsuite><testcase><failure message="SYNTHETIC_SECRET">'
        "SYNTHETIC_TRANSCRIPT</failure><system-out>SYNTHETIC_PROMPT</system-out>"
        "</testcase><testcase><skipped/></testcase></testsuite></testsuites>"
    )
    coverage = tmp_path / "coverage.json"
    coverage.write_text(json.dumps({"totals": {"num_branches": 20, "covered_branches": 17}}))
    result = summarize(xml, coverage)
    assert result == {"tests": 2, "failures": 1, "errors": 0, "skipped": 1, "branch_coverage": 85}
    assert "SYNTHETIC" not in json.dumps(result)
    verify_requirement_map(PRODUCT)


def test_incomplete_native_cases_cannot_be_replaced_with_version_only_tests(tmp_path):
    folder = tmp_path / "tests/native"
    folder.mkdir(parents=True)
    path = folder / "acceptance.json"
    path.write_text(json.dumps({"schema_version": 1, "clients": {}}))
    with pytest.raises(ValueError, match="incomplete"):
        acceptance_nodes("codex", root=tmp_path)
    entry = {
        "cases": dict.fromkeys(CASES, "tests/native/test_pinned_version.py::test_version"),
        "routes": {
            name: "tests/native/test_pinned_version.py::test_version"
            for name in CLIENTS
            if name != "codex"
        },
    }
    path.write_text(json.dumps({"schema_version": 1, "clients": {"codex": entry}}))
    (folder / "test_pinned_version.py").touch()
    with pytest.raises(ValueError, match="version gate"):
        acceptance_nodes("codex", root=tmp_path)
    (folder / "test_actual.py").write_text("def test_acceptance(): pass\n")
    entry["cases"] = dict.fromkeys(CASES, "tests/native/test_actual.py::test_acceptance")
    entry["routes"] = dict.fromkeys(entry["routes"], "tests/native/test_actual.py::test_acceptance")
    path.write_text(json.dumps({"schema_version": 1, "clients": {"codex": entry}}))
    assert acceptance_nodes("codex", root=tmp_path) == [
        "tests/native/test_actual.py::test_acceptance"
    ]


def test_workflow_permissions_matrix_and_artifact_handoff_are_enforced():
    workflows = {p.stem: json.loads(p.read_text()) for p in WORKFLOWS.glob("*.yml")}
    portable = workflows["_portable"]["jobs"]["portable"]
    assert portable["strategy"]["matrix"] == {
        "os": ["ubuntu-latest", "macos-latest"],
        "python": ["3.11", "3.12", "3.13"],
    }
    for name, workflow in workflows.items():
        assert "pull_request_target" not in workflow["on"]
        assert workflow["permissions"] == {"contents": "read"}
        for job_name, job in workflow["jobs"].items():
            if "uses" in job:
                continue
            assert job["timeout-minutes"] > 0
            for step in job["steps"]:
                if "uses" in step:
                    _, _, sha = step["uses"].partition("@")
                    assert len(sha) == 40 and all(c in "0123456789abcdef" for c in sha)
            if "permissions" in job:
                assert name == "release" and job_name == "publish"
    release = workflows["release"]
    publish = release["jobs"]["publish"]
    assert publish["permissions"] == {"id-token": "write"}
    assert publish["environment"]["name"] == "pypi"
    assert "github.event_name == 'push'" in publish["if"]
    assert {"build", "native-acceptance", "portable", "native-foundation", "identity"} == set(
        publish["needs"]
    )
    assert len(publish["steps"]) == 2
    assert all("run" not in s and "checkout" not in s["uses"] for s in publish["steps"])
    assert publish["steps"][0]["with"]["name"] == "distributions-${{ github.sha }}"
    assert publish["steps"][1]["with"] == {
        "packages-dir": "dist/",
        "attestations": True,
        "skip-existing": False,
    }
    assert "workflow_dispatch" in release["on"]
    assert "native-acceptance" not in release["jobs"]["build"]["needs"]
