"""Save each run's final answer from a `claude plugin eval --keep-temp --json` result, so scores can be
recomputed in CI without rerunning the agents, and write the summary the score floor checks.
Usage: collect.py <eval.json> <label>   -> evals/scores/<label>.runs.json and evals/scores/<label>.json
Add --latest to also point evals/scores/latest.json at this label."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check import EVALS, score, summarize  # noqa: E402


def trace_info(path):
    answer, skills, reads = "", [], []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            continue
        if m.get("type") != "assistant":
            continue
        texts = []
        for c in m.get("message", {}).get("content", []):
            if c.get("type") == "text":
                texts.append(c["text"])
            elif c.get("type") == "tool_use":
                inp = c.get("input", {})
                if c["name"] == "Skill":
                    skills.append(inp.get("skill", ""))
                elif c["name"] in ("Read", "Glob", "Grep"):
                    reads.append(inp.get("file_path") or inp.get("path") or inp.get("pattern") or "")
        if texts:
            answer = "\n".join(texts)
    return answer, skills, reads


def main():
    src, label = Path(sys.argv[1]), sys.argv[2]
    data = json.loads(src.read_text())
    runs = []
    for case in data["cases"]:
        for arm, arm_runs in case["arms"].items():
            for n, r in enumerate(arm_runs, 1):
                answer, skills, reads = trace_info(r["tracePath"]) if r.get("tracePath") and Path(r["tracePath"]).exists() else ("", [], [])
                runs.append({"case": case["name"], "arm": arm, "run": n, "harness_score": r["score"],
                             "error": r["error"], "turns": r.get("turns"), "cost_usd": r.get("costUsd"),
                             "skills": skills, "eval_reads": [p for p in reads if "evals/" in p or "answer" in p],
                             "answer": answer})
    out = EVALS / "scores"
    out.mkdir(exist_ok=True)
    (out / f"{label}.runs.json").write_text(json.dumps(runs, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    per_case = {}
    for r in runs:
        s = score(r["case"], r["answer"])
        per_case.setdefault(r["case"], {}).setdefault(r["arm"], []).append(s.get("recall", s.get("accuracy")))
    summary = {"label": label, "claude_version": data.get("claudeVersion"), "started_at": data.get("startedAt"),
               "cost_usd": data.get("costUsd"), "runs": f"{label}.runs.json", "summary": summarize(runs),
               "per_case": per_case}
    (out / f"{label}.json").write_text(json.dumps(summary, indent=2) + "\n")
    if "--latest" in sys.argv:
        (out / "latest.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    leaks = [r for r in runs if r["eval_reads"]]
    if leaks:
        print("WARNING: runs read eval files:", [(r["case"], r["arm"], r["eval_reads"]) for r in leaks])


if __name__ == "__main__":
    main()
