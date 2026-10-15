#!/usr/bin/env python3
"""
validate_report.py — Objective checks on a finished CRO audit.

The audit skill runs this after writing FULL-AUDIT.md and ACTION-PLAN.md, fixes
every error, and runs it again until it passes.

Checks:
  - both files exist and no template placeholders remain
  - Test Readiness section has a baseline (CONFIRMED/ASSUMED) and a valid verdict
  - score table math: weights total 100% and the weighted sum matches the headline score
  - every action-plan item has an Evidence line
  - NOT_TESTABLE sites get a research plan, not an A/B test list

Usage:
    python validate_report.py ./cro-audit-example.com-2026-10-15/
Exit 0 = pass, 1 = fail.
"""

import re
import sys
from pathlib import Path

PLACEHOLDERS = re.compile(r"\[(X|Title|Domain Name|URL|Issue[^\]]*|Win[^\]]*|YYYY-MM-DD|Detected type)\]|XX/100")
ROW = re.compile(r"^\|\s*\**([A-Za-z ]+?)\**\s*\|\s*(\d{1,3})\s*/\s*100\s*\|\s*([\d.]+)\s*%\s*\|\s*([\d.]+)\s*\|", re.M)
HEADLINE = re.compile(r"CRO Health Score:?\**\s*:?\s*\**\s*(\d{1,3})\s*/\s*100", re.I)
VERDICT = re.compile(r"\*\*Verdict:\*\*\s*(READY|LIMITED|NOT_TESTABLE)")
BASELINE = re.compile(r"\*\*Baseline:\*\*.*\b(CONFIRMED|ASSUMED)\b")
ITEM = re.compile(r"^### \[([CHML]-\d+)\].*?(?=^### |^## |\Z)", re.M | re.S)


def check(folder: Path) -> list:
    errors = []
    audit, plan = folder / "FULL-AUDIT.md", folder / "ACTION-PLAN.md"
    for f in (audit, plan):
        if not f.exists():
            errors.append(f"{f.name} missing")
    if errors:
        return errors
    a, p = audit.read_text(encoding="utf-8"), plan.read_text(encoding="utf-8")

    for name, text in (("FULL-AUDIT.md", a), ("ACTION-PLAN.md", p)):
        left = sorted(set(m.group(0) for m in PLACEHOLDERS.finditer(text)))
        if left:
            errors.append(f"{name}: template placeholders left: {', '.join(left)}")

    v = VERDICT.search(a)
    if "## Test Readiness" not in a or not v:
        errors.append("FULL-AUDIT.md: '## Test Readiness' section with **Verdict:** READY|LIMITED|NOT_TESTABLE missing")
    if not BASELINE.search(a):
        errors.append("FULL-AUDIT.md: **Baseline:** line must say CONFIRMED or ASSUMED")

    rows = [r for r in ROW.findall(a) if r[0].strip().lower() != "total"]
    head = HEADLINE.search(a)
    if not rows:
        errors.append("FULL-AUDIT.md: score table (| Category | NN/100 | W% | weighted |) not found")
    else:
        wsum = sum(float(r[2]) for r in rows)
        if abs(wsum - 100) > 0.6:
            errors.append(f"FULL-AUDIT.md: weights add to {wsum:g}%, must be 100%")
        for cat, score, w, weighted in rows:
            expect = int(score) * float(w) / 100
            if abs(expect - float(weighted)) > 0.6:
                errors.append(f"FULL-AUDIT.md: {cat.strip()} weighted {weighted} should be {expect:.1f}")
        total = sum(int(r[1]) * float(r[2]) for r in rows) / wsum if wsum else 0
        if not head:
            errors.append("FULL-AUDIT.md: 'CRO Health Score: NN/100' headline missing")
        elif abs(int(head.group(1)) - total) > 1:
            errors.append(f"FULL-AUDIT.md: headline score {head.group(1)} but table works out to {total:.1f}")

    items = ITEM.findall(p)
    blocks = ITEM.finditer(p)
    missing = [m.group(1) for m in blocks if "Evidence:" not in m.group(0)]
    if not items:
        errors.append("ACTION-PLAN.md: no items like '### [C-1] Title'")
    if missing:
        errors.append(f"ACTION-PLAN.md: items without an Evidence line: {', '.join(missing)}")

    if v and v.group(1) == "NOT_TESTABLE":
        if re.search(r"^## .*A/B Test", p, re.M | re.I):
            errors.append("ACTION-PLAN.md: site is NOT_TESTABLE but the plan has an A/B test section; replace with the research plan")
        if not re.search(r"^## .*Research", p, re.M | re.I):
            errors.append("ACTION-PLAN.md: NOT_TESTABLE site needs a '## ... Research Plan' section")
    if v and v.group(1) == "LIMITED" and not re.search(r"^## .*Research", p, re.M | re.I):
        errors.append("ACTION-PLAN.md: LIMITED site needs a research section before its big-swing tests")
    return errors


def main():
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    errors = check(folder)
    if errors:
        print(f"FAIL: {len(errors)} problem(s) in {folder}")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(f"PASS: {folder}")


if __name__ == "__main__":
    main()
