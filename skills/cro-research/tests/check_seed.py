"""Reconcile seed records with their latest real HTTP verification evidence."""
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "cro/scripts"))
import evidence

records = evidence.load_records(evidence.DEFAULT_DB)
tests = [r for r in records if r.get("research_type", "ab-test") == "ab-test"]
assert len(tests) >= 25, "need at least 25 published test comparisons"
assert len({r["source_url"] for r in tests}) >= 25, "seed must not be padded with variants from a few publications"
for record in tests:
    details = record.get("verification_details", {})
    assert details.get("source_loaded") is True, record["id"]
    assert 200 <= details["status_code"] < 300, record["id"]
    assert details.get("company_found") is True, record["id"]
    assert details.get("quote_found") is True, record["id"]
    assert details.get("checked_at"), record["id"]
    assert len(details.get("content_sha256", "")) == 64, record["id"]
    if record["result"]["relative_lift_pct"] is None:
        assert record["verification"] == "unverified", record["id"]
        assert record["evidence_strength"] == "C", record["id"]
    else:
        assert record["verification"] == "verified", record["id"]
        assert details.get("lift_found") is True, record["id"]
        assert evidence.lift_present(record["quote"], record["result"]["relative_lift_pct"]), record["id"]
assert any(r["result"]["direction"] == "loss" for r in tests)
assert any(r["result"]["direction"] == "flat" for r in tests)
print("records:", len(records), "distinct source URLs:", len({r["source_url"] for r in tests}))
for key in ("evidence_strength", "verification"):
    print(key + ":", dict(sorted(Counter(r[key] for r in records).items())))
print("direction:", dict(sorted(Counter(r["result"]["direction"] for r in records).items())))
print("SEED CHECK PASSED")
