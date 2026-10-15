#!/usr/bin/env python3
"""
program.py — Run a client's experiment program from one folder.

The folder (default ./cro-program-<client>/) is PRIVATE client data: keep it out
of the public skill repo.

Commands:
  init <client> <site> --conversions N --cvr X      create program.json + readiness verdict
  add <id> "<title>" [--page P] [--mde 0.15]        add an experiment to the backlog
  status <id> <backlog|building|qa|running|stopped|shipped|rejected> [--note ..]
  result <id> --cv N --cc N --vv N --vc N           record visitors/conversions, compute verdict
  board                                             print the program board
  snapshot <name> <elements.json>                   store a page-element baseline
  diff <name> <elements.json>                       compare a page against its baseline

Stats: two-sided two-proportion z-test, 95% CI on relative lift, sample ratio
mismatch (SRM) check. Standard library only.
"""

import argparse
import datetime as dt
import json
import math
import os
import sys
from statistics import NormalDist

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "tr", os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_readiness.py"))
tr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tr)

N = NormalDist()
STATUSES = ("backlog", "building", "qa", "running", "stopped", "shipped", "rejected")


def today():
    return dt.date.today().isoformat()


def analyse(vv_c, conv_c, vv_v, conv_v, planned_per_variant=None):
    """Return lift, CI, p-value, SRM and a plain verdict."""
    if min(vv_c, vv_v) <= 0:
        raise ValueError("visitors must be > 0")
    pc, pv = conv_c / vv_c, conv_v / vv_v
    pooled = (conv_c + conv_v) / (vv_c + vv_v)
    se0 = math.sqrt(pooled * (1 - pooled) * (1 / vv_c + 1 / vv_v)) or 1e-12
    z = (pv - pc) / se0
    p = 2 * (1 - N.cdf(abs(z)))
    # CI on relative lift via log ratio (delta method)
    if conv_c and conv_v:
        se_log = math.sqrt((1 - pc) / conv_c + (1 - pv) / conv_v)
        lr = math.log(pv / pc)
        ci = (math.exp(lr - 1.96 * se_log) - 1, math.exp(lr + 1.96 * se_log) - 1)
    else:
        ci = (float("nan"), float("nan"))
    # SRM: chi-square, 1 df, expected 50/50
    total = vv_c + vv_v
    chi = (vv_c - total / 2) ** 2 / (total / 2) * 2
    srm_p = 2 * (1 - N.cdf(math.sqrt(chi)))
    lift = (pv - pc) / pc if pc else float("nan")

    reached = planned_per_variant is None or min(vv_c, vv_v) >= planned_per_variant
    if srm_p < 0.001:
        verdict = "INVALID: sample ratio mismatch, the split is broken; fix targeting and rerun"
    elif not reached:
        verdict = (f"NOT FINISHED: {min(vv_c, vv_v):,} of {planned_per_variant:,} planned visitors per variant; "
                   "keep running, do not call it")
    elif p < 0.05:
        verdict = "WIN" if lift > 0 else "LOSS"
    else:
        verdict = "FLAT: no detectable difference at the planned size"
    return {"control_cr": pc, "variant_cr": pv, "relative_lift": lift, "ci95": ci,
            "p_value": p, "srm_p": srm_p, "verdict": verdict}


class Program:
    def __init__(self, folder):
        self.folder = folder
        self.path = os.path.join(folder, "program.json")

    def load(self):
        if not os.path.exists(self.path):
            sys.exit(f"Error: no program.json in {self.folder}; run init first")
        return json.load(open(self.path))

    def save(self, d):
        os.makedirs(self.folder, exist_ok=True)
        tmp = self.path + ".tmp"
        json.dump(d, open(tmp, "w"), indent=2)
        os.replace(tmp, self.path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=None, help="program folder (default ./cro-program-<client> or .)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("client"); s.add_argument("site")
    s.add_argument("--conversions", type=float, required=True); s.add_argument("--cvr", type=float, required=True)
    s = sub.add_parser("add"); s.add_argument("id"); s.add_argument("title")
    s.add_argument("--page", default=""); s.add_argument("--mde", type=float, default=None,
                                                         help="relative lift the test is sized for, e.g. 0.15")
    s = sub.add_parser("status"); s.add_argument("id"); s.add_argument("status", choices=STATUSES)
    s.add_argument("--note", default="")
    s = sub.add_parser("result"); s.add_argument("id")
    for k in ("cv", "cc", "vv", "vc"):
        s.add_argument(f"--{k}", type=int, required=True)
    sub.add_parser("board")
    s = sub.add_parser("snapshot"); s.add_argument("name"); s.add_argument("elements")
    s = sub.add_parser("diff"); s.add_argument("name"); s.add_argument("elements")
    a = ap.parse_args()

    folder = a.dir or (f"cro-program-{a.client}" if a.cmd == "init" else ".")
    prog = Program(folder)

    if a.cmd == "init":
        r = tr.assess(a.conversions, a.cvr)
        prog.save({"client": a.client, "site": a.site, "created": today(),
                   "baseline": {"conversions_per_month": a.conversions, "cvr_pct": a.cvr, "date": today()},
                   "readiness": {"verdict": r["verdict"], "mde_4w_pct": r["by_duration"][1]["mde_relative_pct"],
                                 "mde_8w_pct": r["by_duration"][3]["mde_relative_pct"], "date": today()},
                   "experiments": {}, "snapshots": {}})
        print(f"Program created in {folder}: readiness {r['verdict']} "
              f"(min detectable lift {r['by_duration'][1]['mde_relative_pct']}% in 4 weeks)")
        return

    d = prog.load()
    ex = d["experiments"]
    if a.cmd == "add":
        if d["readiness"]["verdict"] == "NOT_TESTABLE":
            print("WARNING: program is NOT_TESTABLE; log this as a research-backed fix, not an A/B test.")
        p = d["baseline"]["cvr_pct"] / 100
        planned = None
        if a.mde:
            planned = math.ceil(tr.visitors_per_variant(p, a.mde))
        ex[a.id] = {"title": a.title, "page": a.page, "status": "backlog", "mde": a.mde,
                    "planned_visitors_per_variant": planned, "history": [[today(), "backlog", ""]]}
        weekly = d["baseline"]["conversions_per_month"] / p * 12 / 52
        if planned:
            print(f"Added {a.id}: needs {planned:,} visitors per variant (~{planned * 2 / weekly:.1f} weeks at full traffic)")
        else:
            print(f"Added {a.id}")
    elif a.cmd == "status":
        e = ex[a.id]
        e["status"] = a.status
        e["history"].append([today(), a.status, a.note])
        if a.status == "running":
            e["started"] = today()
        print(f"{a.id} -> {a.status}")
    elif a.cmd == "result":
        e = ex[a.id]
        r = analyse(a.cv, a.cc, a.vv, a.vc, e.get("planned_visitors_per_variant"))
        e["result"] = {"date": today(), "control": [a.cv, a.cc], "variant": [a.vv, a.vc], **r}
        print(f"{a.id}: control {r['control_cr']:.2%}, variant {r['variant_cr']:.2%}, "
              f"lift {r['relative_lift']:+.1%} (95% CI {r['ci95'][0]:+.1%} to {r['ci95'][1]:+.1%}), "
              f"p={r['p_value']:.3f}, SRM p={r['srm_p']:.3f}")
        print(f"Verdict: {r['verdict']}")
    elif a.cmd == "board":
        rd = d["readiness"]
        print(f"{d['client']} ({d['site']}) · readiness {rd['verdict']} · baseline "
              f"{d['baseline']['conversions_per_month']:g} conv/month at {d['baseline']['cvr_pct']}%")
        for st in STATUSES:
            items = [(k, v) for k, v in ex.items() if v["status"] == st]
            if items:
                print(f"\n{st.upper()}")
                for k, v in items:
                    res = v.get("result", {}).get("verdict", "")
                    print(f"  {k:<8} {v['title'][:60]:<60} {res[:40]}")
    elif a.cmd in ("snapshot", "diff"):
        el = json.load(open(a.elements))
        keys = {
            "ctas": [c.get("text") for c in el.get("ctas", [])][:15],
            "forms": [len(f.get("fields", [])) for f in el.get("forms", [])],
            "headlines": el.get("headlines", {}),
            "trust_signals": sorted(el.get("trust_signals", {}).keys()) if isinstance(el.get("trust_signals"), dict) else el.get("trust_signals"),
            "tracking": el.get("tracking"),
        }
        if a.cmd == "snapshot":
            d["snapshots"][a.name] = {"date": today(), "data": keys}
            print(f"Snapshot '{a.name}' saved")
        else:
            old = d["snapshots"].get(a.name)
            if not old:
                sys.exit(f"Error: no snapshot named {a.name}")
            changed = [k for k in keys if keys[k] != old["data"].get(k)]
            if not changed:
                print(f"No change since {old['date']}")
            for k in changed:
                print(f"CHANGED {k}:\n  was {json.dumps(old['data'].get(k))[:300]}\n  now {json.dumps(keys[k])[:300]}")
            return
    prog.save(d)


if __name__ == "__main__":
    main()
