"""Unit tests for tracking_audit.analyze: vendor detection, duplicates, consent, access requests."""

import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "tracking_audit", Path(__file__).resolve().parents[1] / "skills" / "cro" / "scripts" / "tracking_audit.py")
ta = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ta)

GA_PV = "https://region1.google-analytics.com/g/collect?v=2&tid=G-ABC1234&en=page_view&dl=x"
GTAG = "https://www.googletagmanager.com/gtag/js?id=G-ABC1234"
GTM = "https://www.googletagmanager.com/gtm.js?id=GTM-K9X2"
META = "https://www.facebook.com/tr/?id=123456789&ev=PageView&dl=x"


def page(reqs, banner=False, url="https://s.example/"):
    return {"url": url, "requests": reqs, "consent_banner": banner}


class Analyze(unittest.TestCase):
    def test_nothing_installed_is_critical_and_asks_for_host_analytics(self):
        r = ta.analyze([page(["https://s.example/app.js", "https://fonts.googleapis.com/css2"])])
        self.assertFalse(r["has_analytics"])
        self.assertEqual(r["issues"][0]["issue"], "no_analytics")
        self.assertTrue(any("Cloudflare" in a for a in r["access_requests"]))
        self.assertTrue(any("Search Console" in a for a in r["access_requests"]))

    def test_double_page_view_and_gtm_plus_hardcoded(self):
        r = ta.analyze([page([GTAG, GTM, GA_PV, GA_PV])])
        kinds = {i["issue"] for i in r["issues"]}
        self.assertIn("double_counting", kinds)
        self.assertIn("gtm_and_hardcoded_ga4", kinds)
        self.assertTrue(any("G-ABC1234" in a and "Viewer" in a for a in r["access_requests"]))
        self.assertTrue(any("GTM-K9X2" in a for a in r["access_requests"]))

    def test_single_clean_setup_has_no_issues(self):
        r = ta.analyze([page([GTAG, GA_PV, META])])
        self.assertTrue(r["has_analytics"])
        self.assertEqual(r["issues"], [])
        self.assertTrue(any("123456789" in a for a in r["access_requests"]))

    def test_duplicate_loader_two_ids_and_consent(self):
        r = ta.analyze([page([META, "https://www.facebook.com/tr/?id=987&ev=PageView", GTAG, GTAG, GA_PV], banner=True)])
        kinds = [i["issue"] for i in r["issues"]]
        self.assertIn("duplicate_tag", kinds)
        self.assertIn("several_ids", kinds)
        self.assertIn("fires_before_consent", kinds)

    def test_ua_is_retired(self):
        r = ta.analyze([page(["https://www.google-analytics.com/collect?v=1&tid=UA-1234-1&t=pageview", GTAG, GA_PV])])
        self.assertIn("retired_tool", [i["issue"] for i in r["issues"]])

    def test_cloudflare_web_analytics_counts_as_analytics(self):
        r = ta.analyze([page(["https://static.cloudflareinsights.com/beacon.min.js/v8b", "https://s.example/cdn-cgi/rum?"])])
        self.assertTrue(r["has_analytics"])


if __name__ == "__main__":
    unittest.main()
