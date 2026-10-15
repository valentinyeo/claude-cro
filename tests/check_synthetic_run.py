#!/usr/bin/env python3
"""Check a live synthetic traffic run folder: real model, real site, enough finished visitors,
screenshots and exit verdicts for each, no tracker requests let through, ranked clusters in the report.
Prints LIVE-RUN OK on success."""

import json
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
visits = [json.loads(p.read_text()) for p in sorted(root.glob("visitors/v*/visit.json"))]
problems = []
done = [v for v in visits if v["steps"] > 0 and not v["end_reason"].startswith(("blocked", "model error", "landing"))]
if len(done) < 5:
    problems.append(f"only {len(done)} finished visitors, need 5")
for v in done:
    if v["backend"] != "api" or "haiku" not in v["model"]:
        problems.append(f"{v['id']}: not a real Haiku run ({v['backend']}, {v['model']})")
    if not v["start_url"].startswith("https://"):
        problems.append(f"{v['id']}: not a live site ({v['start_url']})")
    shots = [e["screenshot"] for e in v["log"] if e.get("screenshot")]
    missing = [s for s in shots if not (root / "visitors" / v["id"] / s).is_file()]
    if len(shots) < v["steps"] or missing:
        problems.append(f"{v['id']}: {len(shots)} screenshots for {v['steps']} steps, missing {missing[:3]}")
    if not v.get("exit", {}).get("biggest_frustration"):
        problems.append(f"{v['id']}: no exit verdict")
    if v["trackers_allowed"]:
        problems.append(f"{v['id']}: {v['trackers_allowed']} tracker requests let through")
if sum(v["trackers_blocked"] for v in done) == 0:
    problems.append("no tracker requests were blocked at all: blocking is not working or the site has none")
rep = root / "SYNTHETIC-REPORT.md"
clusters = json.loads((root / "clusters.json").read_text())["clusters"] if (root / "clusters.json").exists() else []
if not rep.exists() or "[S-1]" not in rep.read_text(encoding="utf-8"):
    problems.append("SYNTHETIC-REPORT.md missing or has no ranked clusters")
if len(clusters) < 3 or clusters[0]["score"] < clusters[-1]["score"]:
    problems.append("clusters missing or not ranked by score")
if problems:
    print("LIVE-RUN FAIL", *problems, sep="\n  ")
    sys.exit(1)
print(f"LIVE-RUN OK: {len(done)} visitors, {sum(v['steps'] for v in done)} steps, "
      f"{sum(v['trackers_blocked'] for v in done)} trackers blocked, {len(clusters)} clusters")
