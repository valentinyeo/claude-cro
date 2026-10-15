#!/usr/bin/env python3
"""
test_readiness.py — Can this site run meaningful A/B tests?

Works out the smallest relative lift (MDE) a 50/50 A/B test can reliably detect
in 2-8 weeks, from monthly conversions and conversion rate. Standard library only.

Assumptions: two-sided alpha 0.05, power 0.80, two variants, even split,
fixed-horizon frequentist test.

Usage:
    python test_readiness.py --conversions 300 --cvr 2.1
    python test_readiness.py --conversions 300 --visitors 15000 --json
    python test_readiness.py --conversions 300 --cvr 2.1 --traffic-share 0.5
"""

import argparse
import json
import sys
from statistics import NormalDist

Z = NormalDist().inv_cdf(0.975) + NormalDist().inv_cdf(0.80)
WEEKS = (2, 4, 6, 8)

# Verdict thresholds on the relative MDE reachable within 4 / 8 weeks.
# Real wins from a single change are usually under 10% relative; big redesigns
# sometimes reach 20-30%. Above that, a test almost never reaches significance.
READY_MDE_4W = 0.10
LIMITED_MDE_8W = 0.25


def visitors_per_variant(p: float, mde: float) -> float:
    p2 = p * (1 + mde)
    return Z ** 2 * (p * (1 - p) + p2 * (1 - p2)) / (p2 - p) ** 2


def mde_for(n_per_variant: float, p: float) -> float:
    """Smallest relative lift detectable with n visitors per variant (bisection)."""
    lo, hi = 1e-4, 20.0
    if visitors_per_variant(p, hi) > n_per_variant:
        return float("inf")
    for _ in range(100):
        mid = (lo + hi) / 2
        if visitors_per_variant(p, mid) > n_per_variant:
            lo = mid
        else:
            hi = mid
    return hi


def assess(conversions: float, cvr: float, traffic_share: float = 1.0) -> dict:
    p = cvr / 100
    visitors_month = conversions / p
    weekly = visitors_month * 12 / 52 * traffic_share
    rows = []
    for w in WEEKS:
        n = weekly * w / 2
        rows.append({
            "weeks": w,
            "visitors_per_variant": round(n),
            "conversions_per_variant": round(n * p),
            "mde_relative_pct": round(mde_for(n, p) * 100, 1),
        })
    m4 = rows[1]["mde_relative_pct"] / 100
    m8 = rows[3]["mde_relative_pct"] / 100

    if m4 <= READY_MDE_4W:
        verdict = "READY"
        advice = ("Run a regular A/B testing program. Prioritise tests with ICE, "
                  "about one test per page area every 2-4 weeks.")
        tests_per_year = 52 // 4
    elif m8 <= LIMITED_MDE_8W:
        verdict = "LIMITED"
        advice = ("Traffic only supports a few big-swing tests (whole-page or offer "
                  "changes) run 6-8 weeks each. Do usability research first to pick "
                  "them. Small tweaks (button colour, microcopy) will not reach "
                  "significance: ship them as best-practice fixes instead.")
        tests_per_year = 52 // 8
    else:
        verdict = "NOT_TESTABLE"
        advice = ("Do not plan A/B tests as the main method. Use qualitative research: "
                  "moderated usability tests (5 users per round), session recordings, "
                  "on-site polls and customer interviews. Ship fixes and track a "
                  "before/after baseline. At most one long, radical test running "
                  "in the background.")
        tests_per_year = 0

    # Conversions needed per month for READY status at this CVR
    need_n = visitors_per_variant(p, READY_MDE_4W) * 2 / 4 * 52 / 12 / traffic_share
    return {
        "inputs": {"conversions_per_month": conversions, "cvr_pct": cvr,
                   "visitors_per_month": round(visitors_month), "traffic_share": traffic_share},
        "assumptions": "alpha 0.05 two-sided, power 0.80, 2 variants, 50/50 split",
        "by_duration": rows,
        "verdict": verdict,
        "advice": advice,
        "max_tests_per_year": tests_per_year,
        "conversions_per_month_needed_for_ready": round(need_n * p),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--conversions", type=float, required=True,
                    help="Conversions (orders, leads, sign-ups) per month on the tested flow")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--cvr", type=float, help="Conversion rate in percent, e.g. 2.1")
    g.add_argument("--visitors", type=float, help="Visitors (sessions) per month on the tested flow")
    ap.add_argument("--traffic-share", type=float, default=1.0,
                    help="Share of traffic that reaches the tested page (0-1, default 1)")
    ap.add_argument("--json", action="store_true", dest="json_output")
    a = ap.parse_args()

    cvr = a.cvr if a.cvr is not None else a.conversions / a.visitors * 100
    if a.conversions <= 0 or not 0 < cvr < 100 or not 0 < a.traffic_share <= 1:
        print("Error: need conversions > 0, 0 < cvr < 100, 0 < traffic-share <= 1", file=sys.stderr)
        sys.exit(2)

    r = assess(a.conversions, cvr, a.traffic_share)
    if a.json_output:
        print(json.dumps(r, indent=2))
        return
    i = r["inputs"]
    print(f"Inputs: {i['conversions_per_month']:g} conversions/month, CVR {i['cvr_pct']:.2f}%, "
          f"~{i['visitors_per_month']:,} visitors/month, traffic share {i['traffic_share']:g}")
    print(f"Assumptions: {r['assumptions']}\n")
    print(f"{'Weeks':>5}  {'Visitors/variant':>16}  {'Conv/variant':>12}  {'Min detectable lift':>19}")
    for row in r["by_duration"]:
        print(f"{row['weeks']:>5}  {row['visitors_per_variant']:>16,}  {row['conversions_per_variant']:>12,}  "
              f"{row['mde_relative_pct']:>18}%")
    print(f"\nVerdict: {r['verdict']}")
    print(r["advice"])
    print(f"Conversions/month needed for a regular test program: ~{r['conversions_per_month_needed_for_ready']:,}")


if __name__ == "__main__":
    main()
