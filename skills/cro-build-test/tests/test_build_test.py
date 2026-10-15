#!/usr/bin/env python3
"""Self-contained regression checks. Browser fixture uses a local test server only.

Run with the CRO Python environment. Output is kept under the buildtest scratch
folder, overridable with BUILDTEST_SCRATCH. No real site is contacted by these tests.
"""

import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL.parent / "cro" / "scripts"
sys.path.insert(0, str(SCRIPTS))
from playwright.sync_api import sync_playwright  # noqa: E402
import preview_variant  # noqa: E402
from test_readiness import assess  # noqa: E402

module = importlib.util.spec_from_file_location("render_test", SKILL / "scripts" / "render_test.py")
renderer = importlib.util.module_from_spec(module)
module.loader.exec_module(renderer)
SCRATCH = Path(os.environ.get("BUILDTEST_SCRATCH", "/tmp/claude-1000/-home-valentin-projects-claude-cro/b9de462a-95fc-48af-838d-9cb44d54afd2/scratchpad/buildtest"))
SCRATCH.mkdir(parents=True, exist_ok=True)

TEXT = "An ordinary store with a working purchase path and enough meaningful content for a real page preview. " * 8
HTML = '<!doctype html><html><head><title>Store fixture</title></head><body><main><p>' + TEXT + '</p><div id="slot"></div></main><script>setTimeout(function(){document.querySelector("#slot").innerHTML = \'<a id="cta" href="/products/shoe">Shop</a>\';}, 150);</script></body></html>'


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = HTML.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class BuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="regression-", dir=SCRATCH)
        self.root = Path(self.directory.name)
        self.spec = json.loads((SKILL / "assets" / "test.example.json").read_text())
        self.spec.update({"id": "fixture", "target": {"origin": self.origin, "pathname": "/"},
                          "click_selector": "#cta", "css": "[data-cro-fixture] { color: #123456; }",
                          "timeout_ms": 700,
                          "changes": [{"selector": "#cta", "count": 1, "action": "set_text", "value": "Choose Shoes"},
                                      {"selector": "#cta", "count": 1, "action": "insert_after", "value": "<p>Verified trust line</p>"}]})
        self.ready = assess(20000, 2)

    def tearDown(self):
        self.directory.cleanup()

    def bundle(self):
        return renderer.render(self.spec, self.ready, self.root / "bundle")

    def test_bundle_outputs_and_duration(self):
        bundle = self.bundle()
        names = {p.name for p in bundle.iterdir()}
        self.assertEqual(names, {"variant.js", "variant.css", "goals.js", "test-brief.md", "test.json", "readiness.json"})
        brief = (bundle / "test-brief.md").read_text()
        selected = next(r for r in self.ready["by_duration"] if r["weeks"] in (2, 4) and r["mde_relative_pct"] <= 10)
        self.assertIn(f"{selected['weeks']} full weeks", brief)
        self.assertIn(f"{selected['visitors_per_variant']:,}", brief)
        self.assertIn("ASSUMED", brief)
        self.assertIn("no", brief.lower())
        for filename in ("variant.js", "goals.js"):
            subprocess.run(["node", "--check", str(bundle / filename)], check=True, capture_output=True)
        self.assertEqual(preview_variant.read_manifest((bundle / "variant.js").read_text())["selectors"],
                         [{"selector": "#cta", "count": 1}])

    def test_wrapper_renders_sibling_script(self):
        spec_path, readiness_path = self.root / "spec.json", self.root / "readiness.json"
        spec_path.write_text(json.dumps(self.spec))
        readiness_path.write_text(json.dumps(self.ready))
        result = subprocess.run([str(SCRIPTS / "cro-py"), "../../cro-build-test/scripts/render_test.py",
                                 str(spec_path), "--readiness", str(readiness_path),
                                 "--output", str(self.root / "wrapped")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / "wrapped" / "variant.js").exists())

    def test_suite_index_reports_blocked_and_completed_previews(self):
        import shutil
        index_module = importlib.util.spec_from_file_location("render_index", SKILL / "scripts" / "render_index.py")
        index_renderer = importlib.util.module_from_spec(index_module)
        index_module.loader.exec_module(index_renderer)
        bundle = self.bundle()
        tests = self.root / "tests"
        for test_id in ("first", "second", "third"):
            destination = tests / test_id
            shutil.copytree(bundle, destination)
            data = json.loads((destination / "test.json").read_text())
            data["id"] = test_id
            (destination / "test.json").write_text(json.dumps(data))
        index = self.root / "index.md"
        self.assertFalse(index_renderer.render_index(tests, index))
        self.assertIn("BLOCKED", index.read_text())
        for destination in tests.iterdir():
            for device in ("desktop", "mobile"):
                path = destination / f"preview-{device}" / "report.json"
                path.parent.mkdir()
                path.write_text(json.dumps({"ok": True}))
        self.assertTrue(index_renderer.render_index(tests, index))
        self.assertEqual(index.read_text().count("desktop: PASS"), 3)
        self.assertIn("visual review pending", index.read_text())
        shutil.rmtree(tests / "third")
        with self.assertRaisesRegex(ValueError, "3-5"):
            index_renderer.render_index(tests, index)

    def test_noop_generated_runtime_cannot_pass(self):
        bundle = self.bundle()
        variant = self.root / "noop.js"
        source = (bundle / "variant.js").read_text()
        variant.write_text(source[:source.index("*/") + 2] + "\nvoid 0;")
        with patch.object(preview_variant, "resolve_and_check", return_value="127.0.0.1"):
            report = preview_variant.preview(self.origin, variant, output=self.root / "noop", settle=0.05)
        self.assertFalse(report["ok"])
        self.assertTrue(all(s["ok"] for s in report["selectors"]))

    def test_not_testable_refused(self):
        with self.assertRaisesRegex(ValueError, "NOT_TESTABLE"):
            renderer.render(self.spec, assess(30, 2), self.root / "blocked")
        self.assertFalse((self.root / "blocked").exists())

    def test_limited_rejects_tweak_allows_big_swing(self):
        limited = assess(500, 2)
        self.assertEqual(limited["verdict"], "LIMITED")
        with self.assertRaisesRegex(ValueError, "big-swing"):
            renderer.render(self.spec, limited, self.root / "limited")
        self.spec.update(big_swing=True, mde_relative_pct=25)
        bundle = renderer.render(self.spec, limited, self.root / "limited")
        brief = (bundle / "test-brief.md").read_text()
        self.assertTrue("6 full weeks" in brief or "8 full weeks" in brief)

    def test_tampered_readiness_and_undetectable_mde_refused(self):
        tampered = copy.deepcopy(self.ready)
        tampered["by_duration"][0]["mde_relative_pct"] = 0
        with self.assertRaisesRegex(ValueError, "rerun"):
            renderer.render(self.spec, tampered, self.root / "bad")
        self.spec["mde_relative_pct"] = 0.01
        with self.assertRaisesRegex(ValueError, "not detectable"):
            self.bundle()

    def test_existing_evidence_not_overwritten(self):
        self.bundle()
        with self.assertRaisesRegex(ValueError, "not empty"):
            self.bundle()

    def test_unscoped_css_invalid_action_and_event_handler_refused(self):
        self.spec["css"] = "body { display:none; }"
        with self.assertRaisesRegex(ValueError, "Scope CSS"):
            self.bundle()
        self.spec["css"] = ""
        self.spec["changes"][0]["action"] = "execute"
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            self.bundle()
        self.spec["changes"][0].update(action="set_attribute", attribute="onclick")
        with self.assertRaisesRegex(ValueError, "executable"):
            self.bundle()

    def test_manifest_fails_closed(self):
        for source in ("alert(1)", '/* CRO_TEST {"id":"x","selectors":[]} */',
                       '/* CRO_TEST {"id":"x","selectors":[{"selector":"#cta","count":0}]} */'):
            with self.assertRaises(ValueError):
                preview_variant.read_manifest(source)
        result = subprocess.run([sys.executable, str(SCRIPTS / "preview_variant.py"), self.origin,
                                 str(SKILL / "assets" / "variant-template.js")], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(json.loads(result.stdout)["ok"])

    def test_private_network_rejected_without_test_patch(self):
        with self.assertRaisesRegex(ValueError, "private"):
            preview_variant.preview(self.origin, self.bundle() / "variant.js", output=self.root / "private")

    def test_desktop_and_mobile_preview_pass(self):
        bundle = self.bundle()
        # The private-host bypass is local to the in-process fixture; CLI has no bypass flag.
        with patch.object(preview_variant, "resolve_and_check", return_value="127.0.0.1"):
            for mobile in (False, True):
                report = preview_variant.preview(self.origin, bundle / "variant.js", mobile=mobile, settle=0.05)
                self.assertTrue(report["ok"], report)
                self.assertTrue(report["runtime"]["applied"])
                self.assertEqual(len(report["screenshots"]), 4)
                self.assertTrue(all(Path(p).stat().st_size > 100 for p in report["screenshots"].values()))

    def test_missing_and_ambiguous_selectors_fail(self):
        bundle = self.bundle()
        source = (bundle / "variant.js").read_text()
        with patch.object(preview_variant, "resolve_and_check", return_value="127.0.0.1"):
            for selector in ("#absent", "p"):
                variant = self.root / "bad-selector.js"
                variant.write_text(source.replace("#cta", selector))
                report = preview_variant.preview(self.origin, variant, output=self.root / selector.replace("#", ""), settle=0.05)
                self.assertFalse(report["ok"])
                self.assertFalse(all(s["ok"] for s in report["selectors"]))

    def test_thrown_js_and_async_errors_fail(self):
        bundle = self.bundle()
        source = (bundle / "variant.js").read_text()
        with patch.object(preview_variant, "resolve_and_check", return_value="127.0.0.1"):
            for code in ("throw new Error('fixture throw');", "setTimeout(function(){throw new Error('fixture async');}, 100);"):
                variant = self.root / "throws.js"
                variant.write_text(source + "\n" + code)
                report = preview_variant.preview(self.origin, variant, output=self.root / "throws", settle=0.3)
                self.assertFalse(report["ok"])
                self.assertTrue(any("fixture" in e["text"] for e in report["page_errors"]))

    def test_late_target_reinjection_replacement_timeout_and_goals(self):
        bundle = self.bundle()
        source = (bundle / "variant.js").read_text()
        goals = (bundle / "goals.js").read_text()
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(self.origin, wait_until="domcontentloaded")
                page.add_script_tag(content=source)
                page.wait_for_function("window.__croTests.fixture.applied")
                page.add_script_tag(content=source)
                self.assertEqual(page.locator('[data-cro-insert]').count(), 1)
                self.assertEqual(page.locator('#cro-fixture-style').count(), 1)
                self.assertEqual(page.locator('#cta').text_content(), "Choose Shoes")
                self.assertEqual(page.locator('#cta').get_attribute('href'), '/products/shoe')
                page.evaluate("document.querySelector('#cta').outerHTML = '<a id=\"cta\" href=\"/products/shoe\">New DOM</a>'")
                page.wait_for_function("document.querySelector('#cta').textContent === 'Choose Shoes'")
                self.assertEqual(page.locator('[data-cro-insert]').count(), 1)
                # No assignment or analytics means suggestions must be inert.
                page.add_script_tag(content=goals)
                self.assertIsNone(page.evaluate("window.__croGoalSuggestions || null"))
                page.evaluate("() => { window.assignedVariant='variant'; window.calls=[]; window.gtag=function(){window.calls.push(Array.from(arguments));}; }")
                page.add_script_tag(content=goals)
                page.add_script_tag(content=goals)
                page.evaluate("document.querySelector('#cta').addEventListener('click', e => e.preventDefault())")
                page.locator('#cta').dispatch_event('click')
                self.assertEqual(page.evaluate("window.calls.map(c=>c[1])"), ['cro_experiment_view', 'cro_variant_click'])
                page.wait_for_timeout(800)
                self.assertFalse(page.evaluate("window.__croTests.fixture.timedOut"))
                # Verify timeout is a real negative control, not just a configured number.
                page.reload(wait_until="domcontentloaded")
                page.add_script_tag(content=source.replace('#cta', '#absent'))
                page.wait_for_function("window.__croTests.fixture.timedOut")
                self.assertTrue(page.evaluate("window.__croTests.fixture.errors.length > 0"))
                self.assertFalse(page.evaluate("window.__croTests.fixture.applied"))
            finally:
                browser.close()


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(BuildTest))
    if result.wasSuccessful():
        print("BUILDTEST CHECKS PASSED")
    sys.exit(0 if result.wasSuccessful() else 1)
