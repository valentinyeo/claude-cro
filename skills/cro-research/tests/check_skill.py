"""Check skill integration constraints and essential workflow content."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
text = (root / "SKILL.md").read_text(encoding="utf-8")
assert len(text.splitlines()) < 250
frontmatter = text.split("---", 2)[1]
for field in ("name", "description", "argument-hint", "disable-model-invocation", "allowed-tools"):
    assert re.search(rf"^{field}:", frontmatter, re.M), field
assert "name: cro-research" in frontmatter
assert "disable-model-invocation: true" in frontmatter
for phrase in ("find evidence for this finding", "Weekly run checklist", "Final self-review", "verify all", "export-md", "dedupe", "No matching published test found", "speaker notes", "NOT_TESTABLE", "null", "source_url"):
    assert phrase.casefold() in text.casefold() or phrase == "source_url" and "source URL" in text, phrase
sources = (root / "references/sources.md").read_text()
for source in ("Booking", "Etsy", "Airbnb", "VWO", "Convert", "Optimizely", "AB Tasty", "GoodUI", "Baymard"):
    assert source in sources, source
for folder in (root, root.parent / "cro/evidence"):
    for path in folder.rglob("*.md"):
        assert "\u2014" not in path.read_text(encoding="utf-8"), path
print("SKILL CHECK PASSED")
