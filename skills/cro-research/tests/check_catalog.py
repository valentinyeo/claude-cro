"""Check the committed catalog against deterministic rendering of the JSON."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cro/scripts"))
import evidence

records = evidence.load_records(evidence.DEFAULT_DB)
expected = evidence.catalog(records)
actual = (evidence.DEFAULT_DB / "CATALOG.md").read_text(encoding="utf-8")
assert actual == expected, "run evidence.py export-md"
assert expected == evidence.catalog(list(reversed(records))), "rendering must ignore input order"
for record in records:
    assert f"## {record['page_type']}\n" in actual
    assert f"(`{record['id']}`)" in actual
    assert record["source_url"] in actual
    assert " ".join(record["quote"].split()) in actual
    if record.get("notes"):
        assert record["notes"] in actual
print("CATALOG CHECK PASSED")
