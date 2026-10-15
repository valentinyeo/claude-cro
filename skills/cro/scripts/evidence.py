#!/usr/bin/env python3
"""Manage source-backed CRO evidence. Run with cro-py evidence.py --help."""

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from bs4 import BeautifulSoup

from fetch_page import fetch_page, looks_blocked

DEFAULT_DB = Path(__file__).resolve().parents[1] / "evidence"
BUSINESS_TYPES_FILE = Path(__file__).resolve().parents[1] / "references/business-types.md"
SOURCE_TYPES = {"company blog", "agency case study", "academic", "platform case study"}
REQUIRED = {
    "id", "title", "company", "industry", "business_type", "page_type", "element",
    "change", "result", "sample_size", "conversions", "significance", "test_duration",
    "date_published", "source_url", "source_type", "quote", "verification",
    "evidence_strength", "principles", "added_date", "added_by",
}


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def business_types():
    return set(re.findall(r"^\| \*\*(.+?)\*\* \|", BUSINESS_TYPES_FILE.read_text(), re.M))


def number(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


def valid_date(value):
    try:
        return isinstance(value, str) and date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def canonical_url(url):
    parts = urlsplit(url)
    query = sorted((k, v) for k, v in parse_qsl(parts.query) if not k.startswith("utm_") and k not in {"gclid", "fbclid"})
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), urlencode(query), ""))


def duplicate_key(record):
    return canonical_url(record["source_url"]), tuple(normalize(record["change"][k]) for k in ("control", "variant"))


def validate_record(record):
    """Raise ValueError with actionable schema errors; never coerce unknown stats."""
    if not isinstance(record, dict):
        raise ValueError("record must be a JSON object")
    missing = REQUIRED - record.keys()
    if missing:
        raise ValueError("missing fields: " + ", ".join(sorted(missing)))
    for key in ("id", "title", "company", "industry", "business_type", "page_type", "element", "source_url", "quote", "added_by"):
        if not isinstance(record[key], str) or not record[key].strip():
            raise ValueError(f"{key} must be a nonempty string")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", record["id"]):
        raise ValueError("id must be a lowercase hyphenated slug")
    if record["business_type"] not in business_types():
        raise ValueError("business_type must match references/business-types.md")
    url = urlsplit(record["source_url"])
    if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
        raise ValueError("source_url must be an absolute HTTP(S) URL without credentials")
    if record["source_type"] not in SOURCE_TYPES:
        raise ValueError("invalid source_type")
    if record["verification"] not in {"verified", "unverified"}:
        raise ValueError("verification must be verified or unverified")
    if record["evidence_strength"] not in {"A", "B", "C"}:
        raise ValueError("evidence_strength must be A, B or C")
    for key in ("change", "result"):
        if not isinstance(record[key], dict):
            raise ValueError(f"{key} must be an object")
    for key in ("control", "variant"):
        if not isinstance(record["change"].get(key), str) or not record["change"][key].strip():
            raise ValueError(f"change.{key} must describe the tested experience")
    result = record["result"]
    if not isinstance(result.get("metric"), str) or not result["metric"].strip():
        raise ValueError("result.metric is required")
    if "relative_lift_pct" not in result:
        raise ValueError("result.relative_lift_pct is required (null if unpublished)")
    lift = result["relative_lift_pct"]
    if lift is not None and not number(lift):
        raise ValueError("result.relative_lift_pct must be a finite number or null")
    if result.get("direction") not in {"win", "loss", "flat"}:
        raise ValueError("result.direction must be win, loss or flat")
    desired = result.get("desired_direction", "increase")
    if desired not in {"increase", "decrease"}:
        raise ValueError("result.desired_direction must be increase or decrease")
    if lift is not None and result["direction"] != "flat":
        beneficial = lift > 0 if desired == "increase" else lift < 0
        if lift == 0 or beneficial != (result["direction"] == "win"):
            raise ValueError("lift sign contradicts result.direction and desired_direction")
    for field in ("sample_size", "conversions"):
        counts = record[field]
        if counts is None:
            continue
        if not isinstance(counts, dict) or not any(k in counts for k in ("total", "control", "variant")):
            raise ValueError(f"{field} must contain total, control or variant counts, or be null")
        for key in ("total", "control", "variant"):
            value = counts.get(key)
            if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
                raise ValueError(f"{field}.{key} must be a nonnegative integer")
        if not any(counts.get(k) is not None for k in ("total", "control", "variant")):
            raise ValueError(f"{field} needs at least one published count")
    sig = record["significance"]
    if sig is not None:
        if not isinstance(sig, dict) or not isinstance(sig.get("reported"), str) or not sig["reported"].strip():
            raise ValueError("significance needs a reported description, or must be null")
        for key, upper in (("confidence_pct", 100), ("p_value", 1)):
            value = sig.get(key)
            if value is not None and (not number(value) or not 0 <= value <= upper):
                raise ValueError(f"significance.{key} is out of range")
    strength = record["evidence_strength"]
    if strength == "A" and (record["sample_size"] is None or sig is None):
        raise ValueError("strength A requires published sample size and significance")
    if strength in {"A", "B"} and lift is None:
        raise ValueError("strength A/B requires a published lift")
    if strength == "B" and record["sample_size"] is not None and sig is not None:
        raise ValueError("published sample size and significance qualify as A, not B")
    for key in ("added_date", "date_published"):
        if record[key] is None and key == "date_published":
            continue
        if not valid_date(record[key]):
            raise ValueError(f"{key} must be YYYY-MM-DD (date_published may be null)")
    if record["test_duration"] is not None and (not isinstance(record["test_duration"], str) or not record["test_duration"].strip()):
        raise ValueError("test_duration must be a published description or null")
    tags = record["principles"]
    if not isinstance(tags, list) or not tags or any(not isinstance(t, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", t) for t in tags) or len(set(tags)) != len(tags):
        raise ValueError("principles must be unique lowercase hyphenated tags")
    if record.get("research_type", "ab-test") not in {"ab-test", "research"}:
        raise ValueError("research_type must be ab-test or research")
    if record["verification"] == "verified":
        details = record.get("verification_details", {})
        if not all(details.get(k) is True for k in ("source_loaded", "company_found", "lift_found", "quote_found")):
            raise ValueError("verified requires successful fetch, company, lift and quote checks")


def load_records(db):
    records, keys = [], {}
    for path in sorted((db / "tests").glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            validate_record(record)
            if path.stem != record["id"]:
                raise ValueError("filename must equal id.json")
            key = duplicate_key(record)
            if key in keys:
                raise ValueError(f"duplicate source_url + change: {keys[key]}")
            keys[key] = record["id"]
            records.append(record)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"{path}: {exc}") from exc
    return records


def write_record(db, record):
    folder = db / "tests"
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=folder, delete=False) as f:
        json.dump(record, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write("\n")
    Path(f.name).replace(folder / (record["id"] + ".json"))


def lift_present(text, lift):
    if lift is None:
        return False
    # Match a percentage token, not a year, sample count or part of another number.
    tokens = re.findall(r"(?<![\w.,])([+-]?\d+(?:[.,]\d+)?)\s*(?:%|percent\b|per cent\b)", normalize(text))
    return any(math.isclose(abs(float(t.replace(",", "."))), abs(lift), abs_tol=1e-8) for t in tokens)


def visible_text(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    root = soup.find("main") or soup.find("article") or soup
    return root.get_text(" ", strip=True)


def verify_record(record, timeout=30):
    details = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_loaded": False, "company_found": False, "lift_found": False,
        "quote_found": False, "fetched_with": "http",
    }
    try:
        response = fetch_page(record["source_url"], timeout=timeout)
        details.update(status_code=response["status_code"], final_url=response["final_url"])
        reason = looks_blocked(response["status_code"], response["html"])
        if not 200 <= response["status_code"] < 300 or reason:
            details["reason"] = reason or f"HTTP {response['status_code']}"
        else:
            text = visible_text(response["html"])
            details.update(
                source_loaded=True,
                company_found=normalize(record["company"]) in normalize(text),
                lift_found=lift_present(text, record["result"]["relative_lift_pct"]),
                quote_found=normalize(record["quote"]) in normalize(text),
                content_sha256=hashlib.sha256(text.encode()).hexdigest(),
            )
            # The number must occur in the supporting quote, not just a related-case link.
            details["lift_found"] = details["lift_found"] and lift_present(record["quote"], record["result"]["relative_lift_pct"])
            missing = [k.removesuffix("_found") for k in ("company_found", "lift_found", "quote_found") if not details[k]]
            details["reason"] = "company, lift and supporting quote confirmed; not a statistical replication" if not missing else "not confirmed: " + ", ".join(missing)
    except (ValueError, RuntimeError) as exc:
        details["reason"] = str(exc)
    record["verification"] = "verified" if all(details[k] for k in ("source_loaded", "company_found", "lift_found", "quote_found")) else "unverified"
    record["verification_details"] = details
    return record


def lift_label(record):
    lift = record["result"]["relative_lift_pct"]
    return "not published" if lift is None else f"{lift:+g}%"


def catalog(records):
    counts = Counter(r["result"]["direction"] for r in records)
    lines = ["# CRO Evidence Catalog", "", "Generated by `evidence.py export-md`. Do not edit by hand.", "",
             f"{len(records)} records: {counts['win']} wins, {counts['loss']} losses, {counts['flat']} flat/inconclusive.", "",
             "These are reported results, not promised lifts. Vendor case studies favor wins.",
             "Verified means the source loaded and the company, lift and supporting quote matched.",
             "It does not independently validate the experiment. A: sample size and significance",
             "published; B: numeric lift with incomplete stats; C: qualitative/anecdotal.",
             "Flat means no demonstrated difference, not proof of equivalence. Unknown fields stay null.", ""]
    for page_type in sorted({r["page_type"] for r in records}):
        lines += [f"## {page_type}", ""]
        for r in sorted((r for r in records if r["page_type"] == page_type), key=lambda r: r["id"]):
            lines += [f"### {r['title']} (`{r['id']}`)", "",
                      f"- **Company:** {r['company']} | **Business:** {r['business_type']} | **Element:** {r['element']}",
                      f"- **Control:** {r['change']['control']}", f"- **Variant:** {r['change']['variant']}",
                      f"- **Reported result:** {lift_label(r)} {r['result']['metric']}; {r['result']['direction']}.",
                      f"- **Strength:** {r['evidence_strength']} | **Verification:** {r['verification']} | **Principles:** {', '.join(r['principles'])}",
                      f"- **Source:** [{r['source_type']}]({r['source_url']}) | **Published:** {r['date_published'] or 'not published'}",
                      f"- **Sample size:** {json.dumps(r['sample_size'], ensure_ascii=False)} | **Conversions:** {json.dumps(r['conversions'], ensure_ascii=False)}",
                      f"- **Significance:** {json.dumps(r['significance'], ensure_ascii=False)} | **Duration:** {r['test_duration'] or 'not published'}",
                      "", "> " + " ".join(r["quote"].split()), ""]
            if r.get("notes"):
                lines += ["**Caveat:** " + r["notes"], ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Evidence folder containing tests/ (default: installed cro/evidence)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="Validate every record and reject duplicates")
    add = commands.add_parser("add", help="Add one JSON record; verification always starts unverified")
    add.add_argument("file", type=Path)
    search = commands.add_parser("search", help="AND filters; min strength B includes A and B")
    for flag in ("business-type", "page-type", "element", "principle"):
        search.add_argument("--" + flag)
    search.add_argument("--min-strength", choices=["A", "B", "C"], default="C")
    search.add_argument("--json", action="store_true")
    commands.add_parser("stats")
    export = commands.add_parser("export-md")
    export.add_argument("--output", type=Path, help="Default: <db>/CATALOG.md")
    verify = commands.add_parser("verify")
    verify.add_argument("id", help="One record id, or all")
    verify.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args(argv)
    try:
        records = load_records(args.db)
        if args.command == "validate":
            print(f"VALID: {len(records)} records; no schema errors or source/change duplicates")
        elif args.command == "add":
            record = json.loads(args.file.read_text(encoding="utf-8"))
            if not isinstance(record, dict):
                raise ValueError("record must be a JSON object")
            record["verification"] = "unverified"
            record.pop("verification_details", None)
            validate_record(record)
            if any(r["id"] == record["id"] for r in records):
                raise ValueError("id already exists; refusing to overwrite")
            if any(duplicate_key(r) == duplicate_key(record) for r in records):
                raise ValueError("duplicate source_url + change; inspect existing record")
            write_record(args.db, record)
            print(f"ADDED: {record['id']} (unverified; run verify)")
        elif args.command == "search":
            matches = [r for r in records if r["evidence_strength"] <= args.min_strength]
            for key in ("business_type", "page_type", "element"):
                value = getattr(args, key)
                if value:
                    matches = [r for r in matches if normalize(value) == normalize(r[key])]
            if args.principle:
                matches = [r for r in matches if normalize(args.principle) in r["principles"]]
            if args.json:
                print(json.dumps(matches, indent=2, ensure_ascii=False))
            else:
                print("ID | COMPANY | PAGE / ELEMENT | RESULT | GRADE / STATUS | SOURCE")
                for r in matches:
                    print(f"{r['id']} | {r['company']} | {r['page_type']} / {r['element']} | {lift_label(r)} {r['result']['metric']} ({r['result']['direction']}) | {r['evidence_strength']} / {r['verification']} | {r['source_url']}")
                print(f"{len(matches)} match(es)")
        elif args.command == "stats":
            print(json.dumps({"total": len(records), **{key: dict(sorted(Counter(r[key] for r in records).items())) for key in ("evidence_strength", "verification", "page_type")}, "direction": dict(sorted(Counter(r['result']['direction'] for r in records).items()))}, indent=2))
        elif args.command == "export-md":
            target = args.output or args.db / "CATALOG.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(catalog(records), encoding="utf-8")
            print(f"EXPORTED: {len(records)} records to {target}")
        elif args.command == "verify":
            if args.timeout <= 0:
                raise ValueError("timeout must be positive")
            matches = records if args.id == "all" else [r for r in records if r["id"] == args.id]
            if not matches:
                raise ValueError("no matching record")
            failed_load = False
            for record in matches:
                verify_record(record, args.timeout)
                write_record(args.db, record)
                d = record["verification_details"]
                failed_load |= not d["source_loaded"]
                print(f"{record['id']}: {record['verification']} | {d['reason']}")
            return 1 if failed_load else 0
        return 0
    except (ValueError, TypeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
