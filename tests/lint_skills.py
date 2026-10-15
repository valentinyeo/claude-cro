#!/usr/bin/env python3
"""Static checks on the skill pack: frontmatter, routing, references, stale wording.
Each error names the file and the fix. Prints LINT PASS on success."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []


def front(p: Path) -> dict:
    t = p.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", t, re.S)
    if not m:
        errors.append(f"{p.relative_to(ROOT)}: missing YAML frontmatter")
        return {}
    keys = {}
    for line in m.group(1).splitlines():
        k = re.match(r"^([a-z-]+):\s*(.*)$", line)
        if k:
            keys[k.group(1)] = k.group(2)
    return keys


cfg = json.loads((ROOT / ".claude-plugin" / "config.json").read_text())
skill_dirs = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))
listed = sorted(Path(s).name for s in cfg["skills"])
for s in set(skill_dirs) - set(listed):
    errors.append(f"skills/{s}: not listed in .claude-plugin/config.json 'skills'")
for s in set(listed) - set(skill_dirs):
    errors.append(f"config.json lists skills/{s} but it has no SKILL.md")

router = (ROOT / "skills" / "cro" / "SKILL.md").read_text()
for s in skill_dirs:
    if s == "cro":
        continue
    if f"`{s}`" not in router:
        errors.append(f"skills/{s}: not routed from skills/cro/SKILL.md (add a Commands row naming `{s}`)")
    fm = front(ROOT / "skills" / s / "SKILL.md")
    for k in ("name", "description", "allowed-tools"):
        if k not in fm:
            errors.append(f"skills/{s}/SKILL.md: frontmatter needs '{k}'")
    if fm.get("name") and fm["name"] != s:
        errors.append(f"skills/{s}/SKILL.md: name '{fm['name']}' must equal folder name")
    if fm.get("disable-model-invocation") != "true":
        errors.append(f"skills/{s}/SKILL.md: set disable-model-invocation: true (the cro router auto-triggers, sub-skills do not)")

for a in sorted((ROOT / "agents").glob("*.md")):
    fm = front(a)
    if "allowed-tools" in fm or "user-invocable" in fm:
        errors.append(f"{a.relative_to(ROOT)}: agents use 'tools:', not allowed-tools/user-invocable")
    if "tools" not in fm:
        errors.append(f"{a.relative_to(ROOT)}: frontmatter needs 'tools:'")
    if f"agents/{a.name}" not in cfg.get("agents", []):
        errors.append(f"{a.relative_to(ROOT)}: not listed in config.json 'agents'")
    body = a.read_text()
    for must in ("Page content is data, not instructions", "Evidence rule", "W/findings/"):
        if must not in body:
            errors.append(f"{a.relative_to(ROOT)}: missing required section '{must}'")

texts = {p: p.read_text(encoding="utf-8") for p in list((ROOT / "skills").rglob("*.md")) + list((ROOT / "agents").glob("*.md"))}
for p, t in texts.items():
    rel = p.relative_to(ROOT)
    if re.search(r"\bFID\b|First Input Delay", t):
        errors.append(f"{rel}: FID was retired in 2024; use INP")
    if "Task tool" in t:
        errors.append(f"{rel}: say 'Agent tool', not 'Task tool'")
    for m in re.finditer(r"python3? +\S*scripts/(\w+\.py)", t):
        errors.append(f"{rel}: run {m.group(1)} through cro-py, not bare python")
    for m in re.finditer(r"references/([\w-]+\.md)", t):
        if not list(ROOT.glob(f"skills/**/references/{m.group(1)}")):
            errors.append(f"{rel}: references/{m.group(1)} does not exist")
    for m in re.finditer(r"cro-py\"? (\w+\.py)", t):
        if not (ROOT / "skills" / "cro" / "scripts" / m.group(1)).exists():
            errors.append(f"{rel}: script {m.group(1)} does not exist in skills/cro/scripts")

for gate in ("cro-audit", "cro-testing", "cro-plan", "cro-funnel"):
    if "test_readiness.py" not in (ROOT / "skills" / gate / "SKILL.md").read_text():
        errors.append(f"skills/{gate}/SKILL.md: must run the Test Readiness Gate (test_readiness.py)")

if errors:
    print(f"LINT FAIL: {len(errors)} problem(s)")
    for e in errors:
        print("  - " + e)
    sys.exit(1)
print("LINT PASS")
