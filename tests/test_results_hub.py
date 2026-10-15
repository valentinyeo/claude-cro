"""results_hub.py builds one page with every run in the same format, an index and the experiments."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("results_hub", os.path.join(HERE, "..", "skills", "cro", "scripts", "results_hub.py"))
rh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rh)


class ResultsHubTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.W = Path(self.tmp.name)
        (self.W / "results-notes.json").write_text(json.dumps({
            "title": "example.com: CRO results",
            "overall": {"result": "Measure first.", "next": "Say yes to E1."},
            "audit": {"result": "61/100 <weak trust>", "found": ["No analytics"]},
            "message_test": {"result": "Did not finish.", "status": "failed"},
        }))
        (self.W / "experiments.json").write_text(json.dumps([{
            "id": "E1", "title": "Count bookings", "priority": "Critical", "method": "Setup",
            "hypothesis": "Because nothing is measured, we believe tracking will give a baseline.",
            "evidence": ["audit"], "steps": ["Add tracking"], "metric": "clicks", "duration": "4 weeks", "decide": "after 4 weeks",
        }]))

    def tearDown(self):
        self.tmp.cleanup()

    def test_every_run_same_sections_index_and_experiments(self):
        html = rh.build(self.W)
        self.assertIn("<title>example.com: CRO results</title>", html)
        for anchor in ("id='audit'", "id='message_test'", "id='E1'", "href='#audit'", "href='#experiments'"):
            self.assertIn(anchor, html)
        self.assertIn("Because nothing is measured", html)
        self.assertIn("status failed", html)
        self.assertIn("<p class='date'>2 results", html)
        # runs with neither files nor notes are left out
        self.assertNotIn("id='synthetic'", html)
        # notes are escaped, never injected
        self.assertIn("&lt;weak trust&gt;", html)
        self.assertNotIn("<weak trust>", html)

    def test_empty_workspace_still_builds(self):
        for f in ("results-notes.json", "experiments.json"):
            (self.W / f).unlink()
        html = rh.build(self.W)
        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertIn("</main></body></html>", html)


if __name__ == "__main__":
    unittest.main()
