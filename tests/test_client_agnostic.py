"""The pack is public and client agnostic: skills, agents, scripts and docs name no client, owner or private path.
The owner appears only in README, LICENSE and the plugin manifests."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN = ["skills", "agents", "docs", "tests", "install.sh", "install.ps1", "uninstall.sh"]
BANNED = re.compile(r"\binne\b|trivago|eduki|biosouth|hair ?& ?skin|valentin|£1,200", re.I)
ALLOWED = re.compile(r"github\.com/valentinyeo/claude-cro|valentinyeo/claude-cro|raw\.githubusercontent\.com/valentinyeo")


class ClientAgnosticTest(unittest.TestCase):
    def test_no_client_or_owner_names(self):
        hits = []
        for entry in SCAN:
            p = ROOT / entry
            files = [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file()]
            for f in files:
                if f.name == Path(__file__).name or f.name == "GATES.md" or f.suffix in {".png", ".jpg", ".pyc"}:
                    continue
                for n, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                    if BANNED.search(ALLOWED.sub("", line)):
                        hits.append(f"{f.relative_to(ROOT)}:{n}: {line.strip()[:100]}")
        self.assertEqual(hits, [], "client or owner names found:\n" + "\n".join(hits))

    def test_banned_pattern_catches_a_known_name(self):
        self.assertTrue(BANNED.search("results for inne.io"))
        self.assertFalse(BANNED.search(ALLOWED.sub("", "git clone https://github.com/valentinyeo/claude-cro.git")))


if __name__ == "__main__":
    unittest.main()
