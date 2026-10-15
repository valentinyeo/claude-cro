#!/usr/bin/env python3
"""Render a suite index from test bundles, preserving honest preview status.

cro-py ../../cro-build-test/scripts/render_index.py <workspace>/tests --output <workspace>/index.md
Exit 1 when a selected test lacks passing desktop/mobile preview reports.
Visual review and platform QA remain manual, even when preview reports pass.
"""

import argparse
import json
import os
from pathlib import Path
import sys


def render_index(tests, output):
    tests, output = Path(tests), Path(output)
    bundles = sorted(path for path in tests.iterdir() if path.is_dir() and (path / "test.json").exists())
    if not bundles:
        raise ValueError("No test bundles found")
    rows = []
    complete = True
    limited = False
    cell = lambda text: str(text).replace("|", "\\|").replace("\n", " ")
    for bundle in bundles:
        spec = json.loads((bundle / "test.json").read_text(encoding="utf-8"))
        readiness = json.loads((bundle / "readiness.json").read_text(encoding="utf-8"))
        if readiness["verdict"] == "NOT_TESTABLE":
            raise ValueError("NOT_TESTABLE cannot have a test suite")
        limited = limited or readiness["verdict"] == "LIMITED"
        if readiness["verdict"] == "LIMITED" and spec.get("big_swing") is not True:
            raise ValueError("LIMITED suite contains a small tweak")
        qa = []
        for device in ("desktop", "mobile"):
            path = bundle / f"preview-{device}" / "report.json"
            passed = path.exists() and json.loads(path.read_text(encoding="utf-8")).get("ok") is True
            qa.append(f"{device}: {'PASS' if passed else 'BLOCKED'}")
            complete = complete and passed
        relative = Path(os.path.relpath(bundle, output.parent)).as_posix()
        visual = f"[Visual review]({relative}/visual-review.md)" if (bundle / "visual-review.md").exists() else "visual review pending"
        evidence = "; ".join(spec["evidence"])
        duration = next(row for row in readiness["by_duration"]
                        if row["weeks"] in ((6, 8) if readiness["verdict"] == "LIMITED" else (2, 4))
                        and row["mde_relative_pct"] <= spec["mde_relative_pct"])
        rows.append(f"| {cell(spec['id'])} / {cell(evidence)} | {cell(spec['hypothesis']['if'])} | {cell(spec['primary_metric'])} | {duration['weeks']} weeks; {duration['visitors_per_variant']:,}/arm | Run sequentially; review overlap before launch | {'; '.join(qa)}; {visual} | [Bundle]({relative}/test-brief.md), [readiness]({relative}/readiness.json), [desktop]({relative}/preview-desktop/report.json), [mobile]({relative}/preview-mobile/report.json) |")
    if limited and len(bundles) > 2:
        raise ValueError("LIMITED permits at most two big-swing suite candidates")
    if not limited and not 3 <= len(bundles) <= 5:
        raise ValueError("READY suites need 3-5 defensible tests; report any shortfall instead of padding")
    text = "# Test suite\n\nRun sequentially, not as a traffic-splitting multi-arm test. Confirm every audience baseline before launch. Visual review and platform QA are not certified by this index.\n\n| ID / evidence | Hypothesis | Primary metric | Duration | Dependencies / order | Desktop / mobile QA | Bundle |\n|---|---|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    return complete


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("tests")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    try:
        complete = render_index(args.tests, args.output)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print("SUITE PREVIEWS PASS; visual review still required" if complete else "SUITE BLOCKED; see index.md")
    return 0 if complete else 1


if __name__ == "__main__":
    sys.exit(main())
