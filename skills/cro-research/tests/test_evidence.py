"""Offline schema, CLI and source-verification regression tests."""

import contextlib
from datetime import date
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[2] / "cro/scripts"
sys.path.insert(0, str(SCRIPTS))
import evidence as e


def fixture():
    return {
        "id": "example-test", "title": "Example test", "company": "Example Inc",
        "industry": "Software", "business_type": "SaaS", "page_type": "pricing",
        "element": "cta-copy", "change": {"control": "Buy now", "variant": "Start trial"},
        "result": {"metric": "trial signups", "relative_lift_pct": 12.5, "direction": "win"},
        "sample_size": None, "conversions": None, "significance": None,
        "test_duration": None, "date_published": None,
        "source_url": "https://example.org/case", "source_type": "company blog",
        "quote": "Trial signups increased by 12.5%.", "verification": "unverified",
        "evidence_strength": "B", "principles": ["clarity"],
        "added_date": date.today().isoformat(), "added_by": "test",
    }


def response(text=None, status=200):
    content = text or "Example Inc reports: Trial signups increased by 12.5%. "
    return {"status_code": status, "final_url": "https://example.org/case", "html": "<main><p>" + content + "</p><p>" + "Published experiment details and useful visible context. " * 15 + "</p></main>"}


class SchemaTests(unittest.TestCase):
    def test_valid_fixture(self):
        e.validate_record(fixture())

    def test_all_required_fields(self):
        for key in e.REQUIRED:
            r = fixture()
            del r[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                e.validate_record(r)

    def test_invalid_fields(self):
        bad = {
            "id": ["../escape", "", "Upper", "a_b"],
            "business_type": ["ecommerce", "unknown"],
            "source_url": ["", "file:///etc/passwd", "example.org", "https://" + "user:" + "pass@example.org"],
            "verification": ["confirmed"], "source_type": ["search snippet"],
            "evidence_strength": ["D"], "added_date": ["2026-99-01", "20261001"],
            "date_published": ["yesterday"], "principles": [[], ["X"], ["a", "a"]],
            "sample_size": [{}, {"total": -1}, {"total": True}, {"total": None}],
            "conversions": [{"control": 2.3}], "test_duration": [12, ""],
            "significance": [{}, {"reported": "95%", "confidence_pct": 101}],
        }
        for key, values in bad.items():
            for value in values:
                r = fixture()
                r[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    e.validate_record(r)

    def test_numeric_types_and_direction(self):
        for lift in [True, float("nan"), float("inf"), "12%", -3, 0]:
            r = fixture()
            r["result"]["relative_lift_pct"] = lift
            with self.subTest(lift=lift), self.assertRaises(ValueError):
                e.validate_record(r)
        r = fixture()
        r["result"].update(relative_lift_pct=-3, direction="win", desired_direction="decrease")
        e.validate_record(r)
        r["result"].update(direction="loss", desired_direction="increase")
        e.validate_record(r)

    def test_grade_requirements(self):
        r = fixture()
        r["evidence_strength"] = "A"
        with self.assertRaisesRegex(ValueError, "sample size"):
            e.validate_record(r)
        r["sample_size"] = {"total": 1000}
        r["significance"] = {"reported": "significant"}
        e.validate_record(r)
        r["evidence_strength"] = "B"
        with self.assertRaisesRegex(ValueError, "qualify as A"):
            e.validate_record(r)
        r["evidence_strength"] = "C"
        r["result"].update(relative_lift_pct=None, direction="flat")
        e.validate_record(r)

    def test_cannot_claim_verified_without_checks(self):
        r = fixture()
        r["verification"] = "verified"
        with self.assertRaisesRegex(ValueError, "requires successful fetch"):
            e.validate_record(r)

    def test_url_and_change_normalization(self):
        a, b = fixture(), fixture()
        b["source_url"] = "https://EXAMPLE.org/case/?utm_source=mail#result"
        b["change"] = {"variant": " START  TRIAL ", "control": "buy now"}
        self.assertEqual(e.duplicate_key(a), e.duplicate_key(b))
        b["change"]["variant"] = "Try a demo"
        self.assertNotEqual(e.duplicate_key(a), e.duplicate_key(b))


class VerificationTests(unittest.TestCase):
    def test_number_tokens_positive_and_negative_controls(self):
        for text in ["lift: 12.5%", "lift: 12,5 percent", "12.50 %", "-12.5%"]:
            self.assertTrue(e.lift_present(text, 12.5), text)
        for text in ["125%", "112.5%", "12.51%", "12.5 visitors", "year 2012.5", "0.125%"]:
            self.assertFalse(e.lift_present(text, 12.5), text)
        self.assertFalse(e.lift_present("no change", None))

    @patch.object(e, "fetch_page")
    def test_success(self, fetch):
        fetch.return_value = response()
        r = e.verify_record(fixture(), 7)
        self.assertEqual(r["verification"], "verified")
        self.assertTrue(r["verification_details"]["quote_found"])
        self.assertEqual(len(r["verification_details"]["content_sha256"]), 64)
        fetch.assert_called_once_with(r["source_url"], timeout=7)
        e.validate_record(r)

    @patch.object(e, "fetch_page")
    def test_failed_refresh_clears_verified(self, fetch):
        fetch.return_value = response()
        r = e.verify_record(fixture())
        fetch.side_effect = RuntimeError("source is unavailable")
        e.verify_record(r)
        self.assertEqual(r["verification"], "unverified")
        self.assertFalse(r["verification_details"]["source_loaded"])

    @patch.object(e, "fetch_page")
    def test_fetch_failures_block_pages_and_http_status(self, fetch):
        for data in [response(status=404), response(status=403), {"status_code": 200, "final_url": "https://example.org", "html": "<title>Just a moment</title>" + "blocked " * 50}]:
            fetch.return_value = data
            r = e.verify_record(fixture())
            self.assertEqual(r["verification"], "unverified")
            self.assertFalse(r["verification_details"]["source_loaded"])
        fetch.side_effect = ValueError("SSRF protection")
        self.assertIn("SSRF", e.verify_record(fixture())["verification_details"]["reason"])

    @patch.object(e, "fetch_page")
    def test_company_number_and_quote_required(self, fetch):
        for text in ["Another company reports: Trial signups increased by 12.5%.", "Example Inc reports: Trial signups increased by 15%.", "Example Inc reports something else by 12.5%."]:
            fetch.return_value = response(text)
            self.assertEqual(e.verify_record(fixture())["verification"], "unverified")

    @patch.object(e, "fetch_page")
    def test_hidden_claims_do_not_verify(self, fetch):
        fetch.return_value = response("No matched company or result here.<script>Example Inc Trial signups increased by 12.5%.</script>")
        self.assertEqual(e.verify_record(fixture())["verification"], "unverified")

    @patch.object(e, "fetch_page")
    def test_number_elsewhere_not_enough(self, fetch):
        r = fixture()
        r["quote"] = "Trial signups increased."
        fetch.return_value = response("Example Inc Trial signups increased. Another experiment won 12.5%.")
        self.assertEqual(e.verify_record(r)["verification"], "unverified")

    @patch.object(e, "fetch_page")
    def test_qualitative_claim_is_honestly_unverified(self, fetch):
        r = fixture()
        r["quote"] = "There was no discernible impact."
        r["result"].update(relative_lift_pct=None, direction="flat")
        r["evidence_strength"] = "C"
        fetch.return_value = response("Example Inc There was no discernible impact.")
        e.verify_record(r)
        self.assertEqual(r["verification"], "unverified")
        self.assertTrue(r["verification_details"]["source_loaded"])
        self.assertTrue(r["verification_details"]["quote_found"])


class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "db"
        self.input = Path(self.temp.name) / "candidate.json"
        self.addCleanup(self.temp.cleanup)

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = e.main(["--db", str(self.db), *args])
        return code, out.getvalue() + err.getvalue()

    def add(self, record=None):
        self.input.write_text(json.dumps(record or fixture()))
        return self.run_cli("add", str(self.input))

    def test_empty_validate_stats_search_export(self):
        for cmd in [("validate",), ("stats",), ("search",), ("export-md",)]:
            self.assertEqual(self.run_cli(*cmd)[0], 0)
        self.assertIn("0 records", (self.db / "CATALOG.md").read_text())

    def test_add_validate_and_stats(self):
        self.assertEqual(self.add()[0], 0)
        self.assertIn("VALID: 1", self.run_cli("validate")[1])
        self.assertEqual(json.loads(self.run_cli("stats")[1])["total"], 1)

    def test_duplicate_id_and_source_change_refused(self):
        self.add()
        self.assertIn("id already exists", self.add()[1])
        r = fixture()
        r["id"] = "duplicate"
        r["source_url"] += "?utm_source=x#result"
        self.assertIn("duplicate source_url + change", self.add(r)[1])
        self.assertEqual(len(list((self.db / "tests").glob("*.json"))), 1)

    def test_add_resets_spoofed_verification(self):
        r = fixture()
        r["verification"] = "verified"
        r["verification_details"] = {"source_loaded": True, "company_found": True, "lift_found": True, "quote_found": True}
        self.assertEqual(self.add(r)[0], 0)
        r = e.load_records(self.db)[0]
        self.assertEqual(r["verification"], "unverified")
        self.assertNotIn("verification_details", r)

    def test_all_search_filters_and_strength_order(self):
        self.add()
        r = fixture()
        r.update(id="strong-test", source_url="https://example.org/strong", evidence_strength="A", sample_size={"total": 1000}, significance={"reported": "95% confidence", "confidence_pct": 95})
        self.add(r)
        args = ["search", "--business-type", "saas", "--page-type", "PRICING", "--element", "cta-copy", "--principle", "clarity", "--min-strength", "B", "--json"]
        self.assertEqual(len(json.loads(self.run_cli(*args)[1])), 2)
        self.assertEqual(len(json.loads(self.run_cli("search", "--min-strength", "A", "--json")[1])), 1)
        for flag, value in [("--business-type", "E-commerce"), ("--page-type", "home"), ("--element", "reviews"), ("--principle", "trust")]:
            self.assertEqual(json.loads(self.run_cli("search", flag, value, "--json")[1]), [])
        output = self.run_cli("search")[1]
        self.assertIn("12.5%", output)
        self.assertIn("https://example.org/case", output)

    def test_catalog_deterministic_and_grouped(self):
        self.add()
        self.run_cli("export-md")
        before = (self.db / "CATALOG.md").read_bytes()
        self.run_cli("export-md")
        self.assertEqual(before, (self.db / "CATALOG.md").read_bytes())
        self.assertIn("## pricing", before.decode())
        self.assertIn(fixture()["quote"], before.decode())
        custom = Path(self.temp.name) / "custom.md"
        self.assertEqual(self.run_cli("export-md", "--output", str(custom))[0], 0)
        self.assertEqual(custom.read_bytes(), before)

    @patch.object(e, "fetch_page")
    def test_verify_cli_and_unknown_id(self, fetch):
        self.add()
        fetch.return_value = response()
        self.assertEqual(self.run_cli("verify", "example-test")[0], 0)
        self.assertEqual(e.load_records(self.db)[0]["verification"], "verified")
        fetch.return_value = response(status=404)
        self.assertEqual(self.run_cli("verify", "all")[0], 1)
        self.assertEqual(e.load_records(self.db)[0]["verification"], "unverified")
        self.assertEqual(self.run_cli("verify", "unknown")[0], 1)
        self.assertEqual(self.run_cli("verify", "all", "--timeout", "0")[0], 1)

    def test_invalid_record_and_file_errors(self):
        self.input.write_text('{"id": "bad"}')
        self.assertEqual(self.run_cli("add", str(self.input))[0], 1)
        self.assertEqual(self.run_cli("add", "/not/a/real/file")[0], 1)
        self.input.write_text('[]')
        self.assertEqual(self.run_cli("add", str(self.input))[0], 1)
        self.add()
        path = self.db / "tests/example-test.json"
        path.rename(path.with_name("wrong.json"))
        self.assertIn("filename must equal", self.run_cli("validate")[1])

    def test_validation_detects_existing_duplicate_and_bad_json(self):
        self.add()
        r = fixture()
        r["id"] = "duplicate"
        e.write_record(self.db, r)
        self.assertEqual(self.run_cli("validate")[0], 1)
        (self.db / "tests/duplicate.json").write_text("not JSON")
        self.assertEqual(self.run_cli("validate")[0], 1)

    def test_cli_is_not_cwd_dependent(self):
        self.assertTrue(e.DEFAULT_DB.is_absolute())
        self.assertTrue(e.BUSINESS_TYPES_FILE.is_file())


if __name__ == "__main__":
    unittest.main()
