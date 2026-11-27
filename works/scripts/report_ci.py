"""Content-free JUnit and branch-coverage report for public CI artifacts."""

import argparse
import json
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def summarize(junit: Path, coverage: Path | None = None) -> dict:
    root = ET.parse(junit).getroot()
    cases = list(root.iter("testcase"))
    report = {
        "tests": len(cases),
        "failures": sum(c.find("failure") is not None for c in cases),
        "errors": sum(c.find("error") is not None for c in cases),
        "skipped": sum(c.find("skipped") is not None for c in cases),
    }
    if coverage:
        totals = json.loads(coverage.read_text())["totals"]
        branches = totals["num_branches"]
        report["branch_coverage"] = 100 * totals["covered_branches"] / branches if branches else 100
    return report


def verify_requirement_map(product: Path) -> None:
    text = (product / "docs/testing.md").read_text()
    references = set(re.findall(r"(?:unit|integration|native)/test_[\w]+\.py", text))
    if "FEATURE-011" not in text or not references:
        raise ValueError("requirement-to-test map is missing")
    for reference in references:
        if not (product / "tests" / reference).is_file():
            raise ValueError("requirement map references a missing test file")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--coverage", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--requirements", action="store_true")
    args = parser.parse_args()
    if args.requirements:
        verify_requirement_map(Path.cwd())
        return 0
    if not args.junit or not args.output:
        parser.error("--junit and --output are required")
    report = summarize(args.junit, args.coverage)
    report["commit"] = os.environ.get("GITHUB_SHA", "local")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    return int(
        not report["tests"]
        or any(report[k] for k in ("failures", "errors", "skipped"))
        or report.get("branch_coverage", 100) < 85
    )


if __name__ == "__main__":
    raise SystemExit(main())
