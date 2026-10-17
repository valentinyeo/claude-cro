"""Blind fixtures and graders stay independent, deterministic and useful to experts."""
import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "evals" / "tools"


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


plant = load("plant")
check = load("check")
make_cases = load("make_cases")

# Paraphrases, not copied page text: graders must credit descriptions of the issue.
DESCRIPTIONS = {
    "cta-destination-mismatch": [
        "The CTA promises a download but sends visitors to contact sales.",
        "A sales enquiry is not the guide download the button promises.",
        "The guide link destination does not deliver what its label promises.",
    ],
    "blaming-error": [
        "The email error blames the user rather than offering help.",
        "Accusatory validation copy makes recovery unpleasant.",
        "The error message scolds visitors instead of helping them correct it.",
    ],
    "anonymous-testimonial": [
        "The testimonial is anonymous, with no way to verify the source.",
        "An unattributed quote is weak evidence beside the conversion button.",
        "The endorsement has no company or named author.",
    ],
    "late-contract-term": [
        "The twelve-month contract is buried in the footer.",
        "Disclose the minimum commitment before asking for a conversion.",
        "The annual term only appears after the CTA.",
    ],
    "image-only-headline": [
        "The headline is image-only and has no text alternative.",
        "Empty alt makes the main heading unavailable to assistive technology.",
        "The H1 is an image with no alternative text.",
    ],
}


class BlindEvals(unittest.TestCase):
    def test_generated_files_are_current(self):
        for path, text in (plant.build() | make_cases.build()).items():
            with self.subTest(path=path.name):
                self.assertEqual(path.read_text(encoding="utf-8"), text)

    def test_all_answer_keys_pass(self):
        self.assertEqual(check.check_answer_keys(), [])

    def test_five_new_defects_per_site_with_exact_snippets(self):
        old_ids = {d["id"] for d in plant.DEFECTS + plant.SUBTLE}
        for site in plant.SITES:
            key = json.loads((plant.KEYS / f"{site}.blind.json").read_text())
            html = (check.EVALS / key["fixture"]).read_text()
            clean = (check.EVALS / key["clean"]).read_text()
            self.assertEqual(len(key["defects"]), 5)
            self.assertEqual({d["id"] for d in key["defects"]}, set(DESCRIPTIONS))
            for defect in key["defects"]:
                with self.subTest(site=site, defect=defect["id"]):
                    self.assertNotIn(defect["id"], old_ids)
                    self.assertEqual(html.count(defect["snippet"]), 1)
                    self.assertNotIn(defect["snippet"], clean)
                    regex = check.js_re(defect["found"])
                    for text in (clean, *check.page_texts(check.EVALS / key["clean"])):
                        self.assertIsNone(regex.search(text))
                    for description in DESCRIPTIONS[defect["id"]]:
                        self.assertIsNotNone(regex.search(description), description)
                    for other, descriptions in DESCRIPTIONS.items():
                        if other != defect["id"]:
                            for description in descriptions:
                                self.assertIsNone(regex.search(description), description)

    @unittest.skipUnless(shutil.which("node"), "Node required to exercise eval grader regexes")
    def test_javascript_graders_credit_paraphrases_not_clean_pages(self):
        data = [{"pattern": d["found"], "positive": DESCRIPTIONS[d["id"]],
                 "negative": [(plant.FIX / f"{s}.clean.html").read_text() for s in plant.SITES]}
                for d in plant.BLIND]
        script = """
const fs = require('fs');
for (const test of JSON.parse(fs.readFileSync(0, 'utf8'))) {
    const regex = new RegExp(test.pattern, 'i');
    if (!test.positive.every(text => regex.test(text))) process.exit(1);
    if (test.negative.some(text => regex.test(text))) process.exit(2);
}
"""
        subprocess.run(["node", "-e", script], input=json.dumps(data), text=True, check=True)

    def test_answer_key_checker_rejects_clean_matches_even_with_lookahead(self):
        with tempfile.TemporaryDirectory() as tmp:
            keys = Path(tmp)
            for path in plant.KEYS.glob("*.json"):
                if path.name != "winner.json":
                    key = json.loads(path.read_text())
                    if key["tier"] == "blind":
                        key["defects"][0]["found"] = r"^(?=[\s\S]*html)"
                    (keys / path.name).write_text(json.dumps(key))
            with mock.patch.object(check, "KEYS", keys):
                errors = check.check_answer_keys()
            self.assertEqual(sum("pattern matches the clean page" in e for e in errors), len(plant.SITES))

    def test_missing_blind_key_fails_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            keys = Path(tmp)
            for path in plant.KEYS.glob("*.json"):
                if ".blind." not in path.name:
                    shutil.copy(path, keys / path.name)
            with mock.patch.object(check, "KEYS", keys):
                errors = check.check_answer_keys()
            self.assertEqual(sum("missing answer key" in e for e in errors), len(plant.SITES))

    def test_blind_case_prompt_uses_site_not_tier(self):
        for site in plant.SITES:
            case = (check.EVALS / f"defects-{site}.blind" / "case.yaml").read_text()
            self.assertIn(f"The landing page of {site} is saved", case)
            self.assertNotIn(f"The landing page of {site}.blind", case)

    def test_blind_recall_is_separate_and_quotes_count(self):
        site = plant.SITES[0]
        answer = "\n".join(descriptions[0] for descriptions in DESCRIPTIONS.values())
        answer += '\n```json\n' + json.dumps([{
            "problem": "Error blames visitors", "quote": "You failed to enter a valid email address. Try again."
        }]) + '\n```'
        runs = [{"case": f"defects-{site}{suffix}", "arm": "with", "answer": text}
                for suffix, text in (("", "No issues."), (".subtle", "No issues."), (".blind", answer))]
        summary = check.summarize(runs)["with"]
        self.assertEqual(summary["defect_recall"], 0)
        self.assertEqual(summary["subtle_recall"], 0)
        self.assertEqual(summary["blind_recall"], 1)
        self.assertEqual(summary["quote_accuracy"], 1)
        self.assertIsNone(check.summarize(runs[:2])["with"]["blind_recall"])


if __name__ == "__main__":
    unittest.main()
