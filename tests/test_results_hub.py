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

    def test_scores_out_of_ten(self):
        (self.W / "findings.json").write_text(json.dumps({
            "score": 61, "categories": [{"name": "Tracking", "score": 10}],
            "findings": [{"id": "C-1", "title": "No analytics", "priority": "Critical", "category": "tracking"}]}))
        sp = self.W / "pages" / "home"
        sp.mkdir(parents=True)
        (sp / "speed.json").write_text(json.dumps({"lab": {"LCP": "3.0 s", "CLS": "0.000", "TBT": "19 ms"}}))
        n = json.loads((self.W / "results-notes.json").read_text(encoding="utf-8"))
        n["tracking"] = {"result": "none"}
        n["personas"] = {"result": "1 of 2", "score": [5, "1 of 2 reached booking"]}
        n["verify"] = ["Rescore before and after"]
        (self.W / "results-notes.json").write_text(json.dumps(n))
        html = rh.build(self.W)
        self.assertIn("6.1/10", html)              # audit 61/100
        self.assertIn("1/10", html)                # tracking category 10/100
        self.assertIn("8.3/10", html)              # speed: LCP needs work (0.5) + 2 good = 2.5 of 3
        self.assertIn("home: LCP 3.0 s", html)     # listed under To reach 10/10
        self.assertIn("5/10", html)                # notes override
        self.assertIn("id='verify'", html)
        self.assertIn("no score", html)            # message test measures our work, not the page

    def test_book_a_call_line_default_override_and_off(self):
        html = rh.build(self.W)
        self.assertIn("id='cta'", html)
        self.assertIn("<a href='https://cal.com/valentinyeo/teardown'>Book a free 20-minute teardown</a>", html)
        n = json.loads((self.W / "results-notes.json").read_text(encoding="utf-8"))
        n["cta"] = "Questions? Call Acme Agency: https://acme.example/call"
        (self.W / "results-notes.json").write_text(json.dumps(n))
        html = rh.build(self.W)
        self.assertIn("<a href='https://acme.example/call' style='overflow-wrap:anywhere'>https://acme.example/call</a>", html)
        self.assertNotIn("cal.com/valentinyeo/teardown", html)
        n["cta"] = False
        (self.W / "results-notes.json").write_text(json.dumps(n))
        self.assertNotIn("id='cta'", rh.build(self.W))

    def test_skeptic_canonical_counts_match_agent_contract(self):
        agent = (Path(__file__).resolve().parents[1] / "agents/cro-skeptic.md").read_text(encoding="utf-8")
        self.assertIn("Counts: CONFIRMED", agent)
        folder = self.W / "findings"
        folder.mkdir()
        (folder / "skeptic.md").write_text(
            "Status: complete\nCounts: CONFIRMED 5, DOWNGRADE 5, REWORD 7, REJECT 4\n", encoding="utf-8")
        facts = rh.facts_skeptic(self.W, {})
        self.assertEqual(dict((label, value) for value, label in facts["nums"]), {
            "findings checked": "21", "kept as written": "5", "downgraded": "5", "reworded": "7", "rejected": "4"})
        self.assertIn("<b>21</b><span>findings checked</span>", rh.build(self.W))

    def test_skeptic_legacy_bullets_and_colon_counts(self):
        folder = self.W / "findings"
        folder.mkdir()
        for summary in (
            "- KEEP: 5\n- DOWNGRADE: 5\n- REWORD: 7\n- REJECT: 4\n",
            "Counts: CONFIRMED: 5, DOWNGRADE: 5, REWORD: 7, REJECT: 4\n",
        ):
            with self.subTest(summary=summary):
                (folder / "skeptic.md").write_text(summary, encoding="utf-8")
                self.assertEqual([value for value, _ in rh.facts_skeptic(self.W, {})["nums"]],
                                 ["21", "5", "5", "7", "4"])

    def test_skeptic_legacy_overlapping_downgrades_are_not_counted_twice(self):
        folder = self.W / "findings"
        folder.mkdir()
        (folder / "skeptic.md").write_text(
            "- KEEP: 10\n- REWORD: 7 (also DOWNGRADE: 5)\n- REJECT: 4\n", encoding="utf-8")
        facts = rh.facts_skeptic(self.W, {})
        self.assertEqual([value for value, _ in facts["nums"]], ["21", "10", "5", "7", "4"])
        self.assertIn("5 reworded findings also lost a priority level", facts["found"])

    def test_readiness_baseline_accepts_both_keys(self):
        (self.W / "readiness.txt").write_text("Verdict: NOT_TESTABLE\n", encoding="utf-8")
        for readiness, expected in (
            ({"baseline": "ASSUMED"}, "ASSUMED"),
            ({"status": "CONFIRMED"}, "CONFIRMED"),
            ({"status": "CONFIRMED", "baseline": "ASSUMED"}, "CONFIRMED"),
            ({"status": "", "baseline": "ASSUMED"}, "ASSUMED"),
            ({}, "?"),
        ):
            with self.subTest(readiness=readiness):
                self.assertIn((expected, "baseline"), rh.facts_readiness(self.W, {"readiness": readiness})["nums"])

    def test_readiness_lift_reads_commas_preserves_precision_and_grammar(self):
        (self.W / "readiness.txt").write_text(
            "Weeks  Visitors/variant  Conv/variant  Min detectable lift\n"
            "    2               307            20               175.6%\n"
            "    4               615            40               114.5%\n"
            "    6               923            60                90.0%\n"
            "    8             1,231            80                75.7%\n"
            "Verdict: NOT_TESTABLE\n", encoding="utf-8")
        facts = rh.facts_readiness(self.W, {})
        self.assertIn(("75.7%", "smallest lift an 8-week test can see"), facts["nums"])
        self.assertIn("<b>75.7%</b><span>smallest lift an 8-week test can see</span>", rh.build(self.W))
        for row, expected in (
            ("2 307 20 175.6%", ("175.6%", "smallest lift a 2-week test can see")),
            ("8 1231 80 75.7%", ("75.7%", "smallest lift an 8-week test can see")),
            ("8 1,234,567 12,345 7.5%", ("7.5%", "smallest lift an 8-week test can see")),
        ):
            with self.subTest(row=row):
                (self.W / "readiness.txt").write_text(row, encoding="utf-8")
                self.assertIn(expected, rh.facts_readiness(self.W, {})["nums"])

    def test_findings_files_contract_uses_short_names(self):
        root = Path(__file__).resolve().parents[1]
        skill = (root / "skills/cro-audit/SKILL.md").read_text(encoding="utf-8")
        for name in ("ux", "copy", "trust", "visual", "performance", "tracking", "skeptic"):
            with self.subTest(name=name):
                agent = (root / f"agents/cro-{name}.md").read_text(encoding="utf-8")
                self.assertIn(f"W/findings/{name}.md", agent)
                self.assertIn(f"W/findings/{name}.md", skill)
        persona = (root / "agents/cro-persona.md").read_text(encoding="utf-8")
        self.assertIn("W/findings/persona-<persona-id>.md", persona)
        self.assertIn("W/findings/persona-<persona-id>.md", skill)
        self.assertNotIn("W/findings/<name>.md", skill)

    def test_findings_files_links_only_existing_artifacts_and_expands_globs(self):
        folder = self.W / "pages/home"
        folder.mkdir(parents=True)
        (folder / "speed.json").write_text(json.dumps({"lab": {"LCP": "3.0 s"}}), encoding="utf-8")
        html = rh.build(self.W)
        self.assertNotIn("findings/performance.md", html)
        self.assertNotIn("FULL-AUDIT.md", html)
        self.assertIn("href='pages/home/speed.json'", html)
        self.assertNotIn("pages/*/speed.json", html)
        (self.W / "findings").mkdir()
        (self.W / "findings/performance.md").write_text("Status: complete", encoding="utf-8")
        self.assertIn("href='findings/performance.md'", rh.build(self.W))
        wf = self.W / "wireframe"
        (wf / "renders").mkdir(parents=True)
        (wf / "after.html").write_text("<h1>Proposed</h1>", encoding="utf-8")
        html = rh.build(self.W, wf)
        self.assertIn("href='wireframe/after.html'", html)
        self.assertNotIn("before.html", html)
        self.assertNotIn("DESIGN-NOTES.md", html)

    def test_persona_fixes_only_claim_nothing_left_for_a_clean_perfect_score(self):
        notes = json.loads((self.W / "results-notes.json").read_text(encoding="utf-8"))
        for score, status, fixes, clean in (
            (6, "done", [], False),
            (10, "done", [], True),
            (10, "failed", [], False),
            (10, "partial", [], False),
            (6, "done", ["Make booking reachable"], False),
            (10, "done", ["Make booking reachable"], False),
        ):
            with self.subTest(score=score, status=status, fixes=fixes):
                notes["personas"] = {"score": [score, "buyer goal completion"], "status": status, "to_ten": fixes}
                (self.W / "results-notes.json").write_text(json.dumps(notes), encoding="utf-8")
                html = rh.build(self.W)
                self.assertEqual("Nothing left to fix on this test." in html, clean)
                if fixes:
                    self.assertIn("<li>Make booking reachable</li>", html)
                elif not clean:
                    self.assertIn("Fixes have not been listed", html)

    def test_empty_workspace_still_builds(self):
        for f in ("results-notes.json", "experiments.json"):
            (self.W / f).unlink()
        html = rh.build(self.W)
        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertIn("</main></body></html>", html)


if __name__ == "__main__":
    unittest.main()
