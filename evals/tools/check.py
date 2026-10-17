"""Check the eval fixtures and answer keys, score saved answers, and hold committed results to a floor.
  check.py fixtures                 planted pages hold every defect exactly once, clean pages hold none
  check.py score <case> <answer.md> score one saved answer (defects found, quotes that are really on the page)
  check.py results [scores dir]     recompute every committed run from its saved answer and apply the floor
Python standard library only, so CI needs no install."""
import html as htmllib
import json
import re
import sys
from pathlib import Path

EVALS = Path(__file__).resolve().parents[1]
KEYS = EVALS / "answer-keys"
FLOOR = json.loads((EVALS / "floor.json").read_text())


def js_re(pattern):
    # Answer-key patterns are JavaScript regexes for the eval graders; these ones are also valid in Python.
    return re.compile(pattern, re.I)


def norm(s):
    s = htmllib.unescape(s).replace(" ", " ")
    s = s.translate(str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", "–": "-", "—": "-"}))
    return re.sub(r"\s+", " ", s).strip().lower()


def page_texts(path):
    raw = path.read_text(encoding="utf-8")
    body = re.sub(r"<(script|style)\b[\s\S]*?</\1>", " ", raw, flags=re.I)
    visible = re.sub(r"<[^>]+>", " ", body)
    return norm(visible), norm(raw)


def check_fixtures():
    errors = []
    for key_file in sorted(KEYS.glob("*.json")):
        if key_file.name == "winner.json":
            continue
        key = json.loads(key_file.read_text())
        planted = (EVALS / key["fixture"]).read_text(encoding="utf-8")
        clean = (EVALS / key["clean"]).read_text(encoding="utf-8")
        if len(key["defects"]) != 5:
            errors.append(f"{key_file.name}: expected 5 defects, found {len(key['defects'])}")
        for d in key["defects"]:
            for part in d["snippet"].split(" / "):
                part = part if part in planted else htmllib.escape(part, quote=False)
                if planted.count(part) != 1:
                    errors.append(f"{key_file.name}: {d['id']} snippet appears {planted.count(part)} times in planted page")
                if part in clean:
                    errors.append(f"{key_file.name}: {d['id']} snippet already in the clean page")
            if js_re(d["found"]).search(norm(clean)) and not d["found"].startswith("^(?="):
                errors.append(f"{key_file.name}: {d['id']} pattern matches the clean page, so it cannot prove a find")
        case = EVALS / f"defects-{key_file.stem}"
        graders = (case / "case.yaml").read_text(encoding="utf-8") if (case / "case.yaml").exists() else ""
        for d in key["defects"]:
            if json.dumps(d["found"]) not in graders:
                errors.append(f"{case.name}/case.yaml: grader for {d['id']} does not use the answer-key pattern")
    win = json.loads((KEYS / "winner.json").read_text())
    held = [l.strip() for l in (EVALS / "holdout.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
    if sorted(t["evidence_id"] for t in win["tests"]) != sorted(held):
        errors.append("winner.json and holdout.txt list different tests")
    winners = [t["winner"] for t in win["tests"]]
    if abs(winners.count("A") - winners.count("B")) > 1:
        errors.append(f"winner key is unbalanced: {winners.count('A')} A, {winners.count('B')} B")
    for t in win["tests"]:
        rec = json.loads((EVALS.parent / "skills/cro/evidence/tests" / f"{t['evidence_id']}.json").read_text())
        expected = "variant" if rec["result"]["direction"] == "win" else "control"
        if rec["result"]["direction"] not in ("win", "loss") or t["winner_is"] != expected:
            errors.append(f"winner.json: {t['id']} does not match evidence record {t['evidence_id']}")
    return errors


def extract_findings(answer):
    blocks = re.findall(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", answer)
    for b in reversed(blocks):
        try:
            data = json.loads(b)
            if isinstance(data, list):
                return [x for x in data if isinstance(x, dict)]
        except json.JSONDecodeError:
            continue
    return []


def quote_on_page(quote, visible, raw):
    parts = [p for p in re.split(r"\s*(?:\.\.\.|…)\s*", norm(quote)) if p]
    return bool(parts) and all(p.strip(" \"'") in visible or p.strip(" \"'") in raw for p in parts)


def score_defects(case, answer):
    key = json.loads((KEYS / f"{case}.json").read_text())
    visible, raw = page_texts(EVALS / key["fixture"])
    found = [d["id"] for d in key["defects"] if js_re(d["found"]).search(answer)]
    quotes = [str(f.get("quote", "")) for f in extract_findings(answer) if str(f.get("quote", "")).strip()]
    real = [q for q in quotes if quote_on_page(q, visible, raw)]
    return {"found": found, "recall": len(found) / len(key["defects"]), "quotes": len(quotes),
            "quotes_real": len(real), "quote_accuracy": (len(real) / len(quotes)) if quotes else None,
            "bad_quotes": [q for q in quotes if q not in real]}


def score_winner(answer):
    key = json.loads((KEYS / "winner.json").read_text())
    right = [t["id"] for t in key["tests"] if re.search(rf'"{t["id"]}"\s*:\s*"{t["winner"]}"', answer)]
    return {"right": right, "accuracy": len(right) / len(key["tests"])}


def score(case, answer):
    return score_winner(answer) if case == "winner" else score_defects(case.removeprefix("defects-"), answer)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def summarize(runs):
    """runs: [{case, arm, answer}] -> per arm metrics."""
    out = {}
    for arm in ("with", "without"):
        rs = [r for r in runs if r["arm"] == arm]
        obvious = [score(r["case"], r["answer"]) for r in rs if r["case"].startswith("defects-") and not r["case"].endswith(".subtle")]
        subtle = [score(r["case"], r["answer"]) for r in rs if r["case"].startswith("defects-") and r["case"].endswith(".subtle")]
        w = [score(r["case"], r["answer"]) for r in rs if r["case"] == "winner"]
        d = obvious + subtle
        quotes = sum(x["quotes"] for x in d)
        out[arm] = {"defect_recall": mean([x["recall"] for x in obvious]),
                    "subtle_recall": mean([x["recall"] for x in subtle]),
                    "quote_accuracy": sum(x["quotes_real"] for x in d) / quotes if quotes else None,
                    "winner_accuracy": mean([x["accuracy"] for x in w]),
                    "runs": len(rs)}
    return out


def check_results(scores_dir):
    errors = []
    latest = json.loads((scores_dir / "latest.json").read_text())
    runs = json.loads((scores_dir / latest["runs"]).read_text())
    got = summarize(runs)
    for arm in got:
        for metric, value in got[arm].items():
            if metric != "runs" and value is not None and abs(value - latest["summary"][arm][metric]) > 1e-9:
                errors.append(f"{arm} {metric}: committed {latest['summary'][arm][metric]}, recomputed {value}")
    w = got["with"]
    for metric, floor in FLOOR.items():
        if w[metric] is None or w[metric] < floor:
            errors.append(f"with-pack {metric} {w[metric]} is below the floor {floor}")
    return errors, got


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "fixtures"
    if cmd == "fixtures":
        errs = check_fixtures()
    elif cmd == "score":
        print(json.dumps(score(sys.argv[2], Path(sys.argv[3]).read_text(encoding="utf-8")), indent=2))
        errs = []
    elif cmd == "results":
        errs, got = check_results(Path(sys.argv[2]) if len(sys.argv) > 2 else EVALS / "scores")
        print(json.dumps(got, indent=2))
    else:
        sys.exit(__doc__)
    for e in errs:
        print("FAIL", e)
    sys.exit(1 if errs else 0)
