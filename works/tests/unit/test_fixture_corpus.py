import hashlib
import json

import pytest

from tests.support.fixtures import ROOT, materialize

pytestmark = pytest.mark.unit


def test_pinned_four_harness_corpus_copies_without_source_mutation(tmp_path):
    manifest = json.loads((ROOT / "manifest.json").read_text())
    assert manifest["version"] == 1
    assert {entry["harness"] for entry in manifest["files"].values()} == {
        "codex",
        "claude",
        "opencode",
        "pi",
    }
    for name, entry in manifest["files"].items():
        before = (ROOT / name).read_bytes()
        assert hashlib.sha256(before).hexdigest() == entry["sha256"]
        target = materialize(name, tmp_path / "fixtures")
        assert target.read_bytes() == before
        assert "synthetic" in target.read_text().lower()
        if name.endswith(".jsonl"):
            assert all(
                isinstance(json.loads(line), dict) for line in target.read_text().splitlines()
            )
        else:
            assert json.loads(target.read_text())["messages"]
        target.write_text("changed in isolated test")
        assert (ROOT / name).read_bytes() == before
        with pytest.raises(FileExistsError):
            materialize(name, tmp_path / "fixtures")


def test_lifecycle_invalid_records_and_endpoint_scenarios_are_explicit():
    cases = json.loads((ROOT / "scenarios.json").read_text())
    assert cases["version"] == 1
    for scenario in cases["scenarios"].values():
        assert scenario["lifecycle"][-1]["must_not_stop"] == "runtime-B"
        assert [p["available"] for p in scenario["probe_responses"]] == [True, False, None]
        with pytest.raises(json.JSONDecodeError):
            json.loads(scenario["invalid_records"][0])


def test_pi_branch_compaction_fixture_has_distinct_selected_and_inactive_branches():
    rows = [
        json.loads(line)
        for line in (ROOT / "pi-0.80.6-branch-compaction.jsonl").read_text().splitlines()
    ]
    by_id = {row["id"]: row for row in rows}
    path = []
    cursor = rows[-1]
    while cursor:
        path.append(cursor["id"])
        cursor = by_id.get(cursor.get("parentId"))
    assert "00000006" in path and "00000007" not in path
    assert by_id["00000006"]["type"] == "compaction"
