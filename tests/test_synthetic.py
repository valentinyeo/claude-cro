"""Unit tests for synthetic.py: traffic templates, sampling, safety guards, parsing, clustering."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "synthetic", Path(__file__).resolve().parents[1] / "skills" / "cro" / "scripts" / "synthetic.py")
syn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(syn)


class Templates(unittest.TestCase):
    def test_ga4_export(self):
        rows = [
            {"Landing page": "/products/runner?utm_source=fb", "Device category": "mobile",
             "Session source / medium": "facebook / paid", "Sessions": "6,000", "Key events": "60"},
            {"Landing page": "/products/runner", "Device category": "mobile",
             "Session source / medium": "instagram / cpc", "Sessions": "2000", "Key events": "20"},
            {"Landing page": "/", "Device category": "desktop", "Session source / medium": "(direct) / (none)",
             "Sessions": "2000", "Key events": "60"},
        ]
        t = syn.build_templates(rows)
        self.assertEqual(t["source"], "CONFIRMED")
        self.assertEqual(t["sessions"], 10000)
        top = t["templates"][0]
        self.assertEqual((top["landing"], top["device"], top["channel"]), ("/products/runner", "mobile", "paid social"))
        self.assertAlmostEqual(top["share"], 0.8)
        self.assertAlmostEqual(top["cvr"], 0.01)
        self.assertEqual(t["templates"][1]["channel"], "direct")

    def test_posthog_paths(self):
        rows = [{"path": "/ > /collections/men > /products/a", "$device_type": "Mobile", "$initial_referring_domain": "google.com"},
                {"path": "/ > /collections/men > /products/a", "$device_type": "Mobile", "$initial_referring_domain": "google.com"},
                {"path": "/blog/x > /products/b", "$device_type": "Desktop", "$initial_referring_domain": ""}]
        t = syn.build_templates(rows)
        first = t["templates"][0]
        self.assertEqual((first["landing"], first["channel"], first["sessions"]), ("/", "organic search", 2))
        self.assertEqual(first["example_paths"], ["/ > /collections/men > /products/a"])

    def test_missing_columns_explains(self):
        with self.assertRaisesRegex(ValueError, "columns seen"):
            syn.build_templates([{"foo": "1"}])

    def test_allocation_is_proportional_and_exact(self):
        tpl = [{"id": "A", "share": 0.555}, {"id": "B", "share": 0.333}, {"id": "C", "share": 0.112}]
        c = syn.allocate(tpl, 100)  # 55.5 / 33.3 / 11.2: the one spare visitor goes to the biggest remainder
        self.assertEqual(c, {"A": 56, "B": 33, "C": 11})
        self.assertEqual(sum(syn.allocate(tpl, 150).values()), 150)

    def test_assumed_is_labelled(self):
        self.assertEqual(syn.assumed_templates()["source"], "ASSUMED")
        self.assertAlmostEqual(sum(t["share"] for t in syn.assumed_templates()["templates"]), 1.0)


class Guards(unittest.TestCase):
    def test_pay_buttons_refused(self):
        for label in ("Pay now", "Place order", "Complete purchase", "Confirm payment", "Pay $98.00"):
            self.assertTrue(syn.pay_refusal(label), label)
        for label in ("Add to cart", "Checkout", "Continue to shipping", "Payment options"):
            self.assertFalse(syn.pay_refusal(label), label)

    def test_secret_fields_refused(self):
        self.assertTrue(syn.secret_field({"type": "password", "name": "", "label": ""}))
        self.assertTrue(syn.secret_field({"type": "text", "name": "cc-number", "label": ""}))
        self.assertTrue(syn.secret_field({"type": "text", "name": "x", "label": "Security code"}))
        self.assertFalse(syn.secret_field({"type": "search", "name": "q", "label": "Search"}))

    def test_trackers_blocked_shop_assets_not(self):
        for u in ("https://www.google-analytics.com/g/collect?v=2", "https://connect.facebook.net/en_US/fbevents.js",
                  "https://static.hotjar.com/c/hotjar-1.js", "https://www.clarity.ms/tag/x",
                  "https://shop.example/.well-known/shopify/monorail/unstable/produce_batch"):
            self.assertTrue(syn.is_tracker(u), u)
        for u in ("https://cdn.shopify.com/s/files/1/x.js", "https://shop.example/cart/add.js",
                  "https://shop.example/products/runner"):
            self.assertFalse(syn.is_tracker(u), u)

    def test_checkout_only_from_url(self):
        s = {}
        syn.stage_of("https://shop.example/cart", "checkout", s)
        self.assertFalse(s.get("checkout"))
        syn.stage_of("https://shop.example/checkouts/cn/abc", "other", s)
        self.assertTrue(s.get("checkout"))
        self.assertEqual(syn.furthest(s), "checkout")


class Parsing(unittest.TestCase):
    def test_extract_json_with_noise(self):
        self.assertEqual(syn.extract_json('Sure!\n```json\n{"action": "click", "element": 3, "t": "a {b}"}\n```'),
                         {"action": "click", "element": 3, "t": "a {b}"})
        with self.assertRaises(ValueError):
            syn.extract_json("no json here")


class Report(unittest.TestCase):
    def test_clusters_rank_by_visitors_and_severity(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            def visit(i, frictions, device="mobile"):
                vd = root / "visitors" / f"v{i:03d}"
                vd.mkdir(parents=True)
                log = [{"n": 1, "url": "https://s/", "page_type": "home", "screenshot": "step-01.jpg", "thought": "",
                        "action": "click", "result": "clicked", "friction": frictions}]
                (vd / "visit.json").write_text(json.dumps({
                    "id": f"v{i:03d}", "template": "T01", "device": device, "channel": "paid social", "user": "new",
                    "start_url": "https://s/", "persona": {"name": "X"}, "goal": "checkout", "end_reason": "gave up",
                    "stage": "engaged", "converted": False, "atc": False, "steps": 1, "seconds": 1,
                    "trackers_blocked": 3, "trackers_allowed": 0, "exit": {"biggest_frustration": "popup in the way"},
                    "usage": {"input_tokens": 1000, "output_tokens": 100, "calls": 2}, "model": "claude-haiku-5-5",
                    "log": log}))
            popup = lambda q: {"severity": "high", "category": "overlay_popup", "issue": f"Discount popup covers the page {q}"}
            visit(1, [popup("on load")])
            visit(2, [popup("right away")])
            visit(3, [popup("again"), {"severity": "low", "category": "copy_clarity", "issue": "Headline is vague"}])
            visit(4, [{"severity": "critical", "category": "bug", "issue": "Menu button does nothing"}], "desktop")
            clusters = syn.write_report(root)
            self.assertEqual(clusters[0]["category"], "overlay_popup")
            self.assertEqual(clusters[0]["visitors"], 3)
            self.assertEqual(clusters[1]["category"], "bug")
            rep = (root / "SYNTHETIC-REPORT.md").read_text(encoding="utf-8")
            self.assertIn("[S-1]", rep)
            self.assertIn("**4x** popup in the way", rep)
            self.assertIn("let through: 0", rep)


class Merge(unittest.TestCase):
    def test_model_merge_joins_groups_and_keeps_the_rest(self):
        def f(v, issue, sev="high"):
            return {"visitor": v, "issue": issue, "severity": sev, "category": "overlay_popup", "page_type": "product",
                    "step": 1, "screenshot": "s.jpg", "device": "mobile", "url": "u"}
        groups = [[f("v1", "AI chat bubble covers size buttons")], [f("v2", "Shop with AI pill hides Select a size")],
                  [f("v3", "Cookie banner covers page", "low")]]

        class Fake:
            def ask(self, *a, **k):
                return {"groups": [{"title": "AI widget covers the size picker", "ids": ["G0", "G1", "G9"]}]}
        merged, titles = syn.merge_groups(groups, Fake())
        self.assertEqual(len(merged), 2)
        c = syn.summarize(merged[0], 3, titles.get(0))
        self.assertEqual((c["headline"], c["visitors"], c["score"]), ("AI widget covers the size picker", 2, 6))


if __name__ == "__main__":
    unittest.main()
