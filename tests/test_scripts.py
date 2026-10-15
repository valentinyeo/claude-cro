"""Regression tests for the deterministic CRO scripts. Standard library only (no network)."""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "cro" / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tr = load("test_readiness")
vr = load("validate_report")


class Readiness(unittest.TestCase):
    def test_sample_size_matches_reference(self):
        # Evan Miller style reference: 2% baseline, 10% relative MDE, 80% power, 5% two-sided ~ 80-81k per variant
        n = tr.visitors_per_variant(0.02, 0.10)
        self.assertTrue(78_000 < n < 83_000, n)

    def test_mde_inverts_sample_size(self):
        n = tr.visitors_per_variant(0.03, 0.15)
        self.assertAlmostEqual(tr.mde_for(n, 0.03), 0.15, places=3)

    def test_verdict_bands(self):
        self.assertEqual(tr.assess(50, 2)["verdict"], "NOT_TESTABLE")
        self.assertEqual(tr.assess(1500, 2)["verdict"], "LIMITED")
        self.assertEqual(tr.assess(8000, 2)["verdict"], "READY")

    def test_more_traffic_never_hurts(self):
        last = float("inf")
        for c in (20, 100, 400, 1600, 6400):
            m = tr.assess(c, 2.5)["by_duration"][1]["mde_relative_pct"]
            self.assertLess(m, last)
            last = m

    def test_traffic_share_lowers_power(self):
        full = tr.assess(2000, 2)["by_duration"][1]["mde_relative_pct"]
        half = tr.assess(2000, 2, 0.5)["by_duration"][1]["mde_relative_pct"]
        self.assertGreater(half, full)

    def test_cli_rejects_bad_input(self):
        r = subprocess.run([sys.executable, str(SCRIPTS / "test_readiness.py"), "--conversions", "0", "--cvr", "2"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


GOOD_AUDIT = """# CRO Audit: shop.example
**CRO Health Score:** 62/100 — Moderate

## Test Readiness
**Baseline:** 120 conversions/month, 1.5% CVR, 8,000 visitors/month — CONFIRMED
**Verdict:** NOT_TESTABLE

## Score
| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| UX | 60/100 | 25% | 15.0 |
| Copy | 70/100 | 20% | 14.0 |
| Trust | 50/100 | 15% | 7.5 |
| Visual | 60/100 | 15% | 9.0 |
| Forms | 80/100 | 10% | 8.0 |
| Performance | 50/100 | 10% | 5.0 |
| Tracking | 70/100 | 5% | 3.5 |
| **Total** | | **100%** | **62** |
"""

GOOD_PLAN = """# CRO Action Plan
## Critical
### [C-1] Checkout button hidden on mobile
- **Evidence:** mobile.png shows the button below 3 screens of text
- **Fix:** move it up
## Usability Research Plan
1. Five moderated sessions.
"""


class Validator(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.d)

    def write(self, audit, plan):
        (self.d / "FULL-AUDIT.md").write_text(audit, encoding="utf-8")
        (self.d / "ACTION-PLAN.md").write_text(plan, encoding="utf-8")
        return vr.check(self.d)

    def test_good_report_passes(self):
        self.assertEqual(self.write(GOOD_AUDIT, GOOD_PLAN), [])

    def test_wrong_headline_score(self):
        errs = self.write(GOOD_AUDIT.replace("62/100 — Moderate", "75/100 — Strong"), GOOD_PLAN)
        self.assertTrue(any("headline score" in e for e in errs), errs)

    def test_wrong_weighted_cell(self):
        errs = self.write(GOOD_AUDIT.replace("| 15.0 |", "| 20.0 |"), GOOD_PLAN)
        self.assertTrue(any("weighted" in e for e in errs), errs)

    def test_missing_evidence(self):
        errs = self.write(GOOD_AUDIT, GOOD_PLAN.replace("- **Evidence:** mobile.png shows the button below 3 screens of text\n", ""))
        self.assertTrue(any("Evidence" in e for e in errs), errs)

    def test_not_testable_with_ab_section(self):
        errs = self.write(GOOD_AUDIT, GOOD_PLAN + "\n## A/B Test Backlog\n1. test\n")
        self.assertTrue(any("NOT_TESTABLE" in e for e in errs), errs)

    def test_placeholders_left(self):
        errs = self.write(GOOD_AUDIT.replace("shop.example", "[Domain Name]"), GOOD_PLAN)
        self.assertTrue(any("placeholder" in e for e in errs), errs)

    def test_missing_baseline_label(self):
        errs = self.write(GOOD_AUDIT.replace("CONFIRMED", "maybe"), GOOD_PLAN)
        self.assertTrue(any("Baseline" in e for e in errs), errs)


try:
    import requests  # noqa: F401
    HAVE_REQUESTS = True
except ImportError:
    HAVE_REQUESTS = False


@unittest.skipUnless(HAVE_REQUESTS, "requests not installed")
class FetchSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fp = load("fetch_page")

    def test_private_ips_blocked(self):
        for ip in ("127.0.0.1", "10.1.2.3", "192.168.0.5", "169.254.169.254", "::1", "fd00::1", "::ffff:127.0.0.1"):
            self.assertTrue(self.fp.is_private_ip(ip), ip)
        self.assertFalse(self.fp.is_private_ip("93.184.216.34"))

    def test_block_page_detection(self):
        lb = self.fp.looks_blocked
        self.assertIsNotNone(lb(403, "<html>x</html>"))
        self.assertIsNotNone(lb(200, "<title>Just a moment...</title>"))
        self.assertIsNotNone(lb(200, "<title>Shop</title><body><div id=root></div></body>"))
        real = "<title>Shop</title><body>" + "<p>Great shoes made from wool for everyday comfort.</p>" * 10 + "</body>"
        self.assertIsNone(lb(200, real))

    def test_redirect_to_private_host_is_refused_before_request(self):
        fp = self.fp

        class Resp:
            def __init__(self, url, loc=None):
                self.url, self.is_redirect = url, loc is not None
                self.headers = {"Location": loc} if loc else {}
                self.status_code, self.text, self.content, self.encoding = (302 if loc else 200), "", b"", "utf-8"

        calls = []

        def fake_get(self, url, **kw):
            calls.append(url)
            return Resp(url, "http://internal.example/admin")

        def fake_resolve(host):
            if host == "internal.example":
                raise ValueError("private")
            return "93.184.216.34"

        with mock.patch.object(fp, "resolve_and_check", side_effect=fake_resolve), \
             mock.patch("requests.Session.get", fake_get):
            with self.assertRaises(RuntimeError) as ctx:
                fp.fetch_page("https://public.example/")
        self.assertIn("redirect", str(ctx.exception))
        self.assertEqual(calls, ["https://public.example/"])  # internal URL never requested


if __name__ == "__main__":
    unittest.main()
