#!/usr/bin/env python3
"""
message_test.py — Message and offer test on a simulated audience, through a local MiroFish.

MiroFish (https://github.com/666ghj/MiroFish, AGPL, installed separately; we use the
MiroFish-Offline fork) turns a brief into hundreds of AI people who discuss it on a
simulated Twitter and Reddit, then writes a report. This script drives one full run
through its HTTP API: upload brief, build the knowledge graph, create and prepare the
simulation, run it, generate the report, and save it with an honest caveat.

It is simulated opinion: an early signal next to real interviews, never proof, and
never a conversion forecast.

Usage:
    message_test.py run <brief.md> --question "Which offer ..." --out <dir>
                        [--name "valentinyeo offer"] [--rounds 12] [--platform reddit|twitter|parallel]
                        [--api http://127.0.0.1:5001] [--relay http://127.0.0.1:5011] [--timeout 5400]
    message_test.py check [--api ...] [--relay ...]

Exit 0 = report written (run) or MiroFish up (check), 1 = failure.
"""

import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

PRICES = {"claude-haiku-5-5": (1.0, 5.0)}  # USD per million tokens, approximate; same rates as synthetic.py
CAVEAT = ("> Simulated opinion from AI agents (MiroFish, Claude Haiku). An early signal to compare messages "
          "and find objections, not proof and not a conversion forecast. Confirm with real interviews or data.")


class MiroFishError(RuntimeError):
    pass


class Client:
    def __init__(self, api, relay=None, poll=5.0, sleep=time.sleep, clock=time.monotonic):
        self.api, self.relay, self.poll, self.sleep, self.clock = api.rstrip("/"), (relay or "").rstrip("/"), poll, sleep, clock

    def _req(self, method, path, body=None, headers=None, base=None):
        req = urllib.request.Request((base or self.api) + path, data=body, method=method, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            try:
                data = json.loads(e.read() or b"{}")
            except ValueError:
                data = {}
            raise MiroFishError(f"{method} {path}: HTTP {e.code} {data.get('error') or ''}".strip())
        except urllib.error.URLError as e:
            raise MiroFishError(f"{method} {path}: cannot reach MiroFish ({e.reason}); start it with ~/projects/mirofish/start.sh")
        if isinstance(data, dict) and data.get("success") is False:
            raise MiroFishError(f"{method} {path}: {data.get('error') or 'failed'}")
        return data

    def get(self, path, base=None):
        return self._req("GET", path, base=base)

    def post(self, path, payload):
        return self._req("POST", path, json.dumps(payload).encode(), {"Content-Type": "application/json"})

    def post_files(self, path, fields, files):
        boundary = uuid.uuid4().hex
        parts = []
        for k, v in fields.items():
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        for p in files:
            ctype = mimetypes.guess_type(p)[0] or "text/markdown"
            with open(p, "rb") as fh:
                parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="files"; filename="{os.path.basename(p)}"\r\n'
                             f'Content-Type: {ctype}\r\n\r\n'.encode() + fh.read() + b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        return self._req("POST", path, b"".join(parts), {"Content-Type": f"multipart/form-data; boundary={boundary}"})

    def wait(self, what, fetch, done, deadline, log=print):
        """Poll fetch() until done(data) is True/'failed'. Returns the last data."""
        last = None
        while True:
            data = fetch()
            state = done(data)
            if state == "failed":
                raise MiroFishError(f"{what} failed: {json.dumps(data)[:400]}")
            if state:
                return data
            note = json.dumps(data.get("progress") if isinstance(data, dict) else data)
            if note != last:
                log(f"  {what}: {note[:120]}")
                last = note
            if self.clock() > deadline:
                raise MiroFishError(f"{what} timed out")
            self.sleep(self.poll)

    def usage(self):
        if not self.relay:
            return None
        try:
            return self.get("/v1/stats", base=self.relay)
        except MiroFishError:
            return None


def _task_state(d):
    s = (d.get("data") or {}).get("status")
    return "failed" if s == "failed" else s == "completed"


def run(args, client=None, log=print):
    c = client or Client(args.api, args.relay)
    deadline = c.clock() + args.timeout
    os.makedirs(args.out, exist_ok=True)
    before = c.usage()
    ids = {}

    def save():
        with open(os.path.join(args.out, "run.json"), "w", encoding="utf-8") as fh:
            json.dump({"name": args.name, "question": args.question, "rounds": args.rounds, "platform": args.platform, **ids}, fh, indent=2)

    log("1/6 upload brief, generate ontology")
    d = c.post_files("/api/graph/ontology/generate",
                     {"simulation_requirement": args.question, "project_name": args.name}, [args.brief])["data"]
    ids["project_id"] = d["project_id"]; save()

    log("2/6 build knowledge graph")
    t = c.post("/api/graph/build", {"project_id": ids["project_id"]})["data"]["task_id"]
    c.wait("graph", lambda: c.get(f"/api/graph/task/{t}"), _task_state, deadline, log)
    graph_id = c.get(f"/api/graph/project/{ids['project_id']}")["data"].get("graph_id")
    ids["graph_id"] = graph_id; save()

    log("3/6 create and prepare simulation (agent personas)")
    sim = c.post("/api/simulation/create", {"project_id": ids["project_id"], "graph_id": graph_id,
                                            "enable_twitter": args.platform in ("twitter", "parallel"),
                                            "enable_reddit": args.platform in ("reddit", "parallel")})["data"]["simulation_id"]
    ids["simulation_id"] = sim; save()
    p = c.post("/api/simulation/prepare", {"simulation_id": sim})["data"]
    pt = p.get("task_id")
    c.wait("prepare", lambda: c.post("/api/simulation/prepare/status", {"task_id": pt, "simulation_id": sim}),
           lambda d: "failed" if (d.get("data") or {}).get("status") == "failed"
           else (d.get("data") or {}).get("status") in ("completed", "ready"), deadline, log)

    log(f"4/6 run simulation ({args.rounds} rounds, {args.platform})")
    c.post("/api/simulation/start", {"simulation_id": sim, "platform": args.platform, "max_rounds": args.rounds})
    c.wait("simulation", lambda: c.get(f"/api/simulation/{sim}/run-status"),
           lambda d: "failed" if (d.get("data") or {}).get("runner_status") in ("failed", "error")
           else (d.get("data") or {}).get("runner_status") in ("completed", "stopped"), deadline, log)

    log("5/6 generate report")
    r = c.post("/api/report/generate", {"simulation_id": sim})["data"]
    ids["report_id"] = r.get("report_id"); save()
    if r.get("status") != "completed":
        rt = r.get("task_id")
        c.wait("report", lambda: c.post("/api/report/generate/status", {"task_id": rt, "simulation_id": sim}), _task_state, deadline, log)
    rep = c.get(f"/api/report/{ids['report_id']}")["data"]
    md = rep.get("markdown_content") or ""
    if not md.strip():
        raise MiroFishError("report came back empty")

    log("6/6 save")
    after = c.usage()
    cost = ""
    if before and after:
        tin = after.get("input_tokens", 0) - before.get("input_tokens", 0)
        tout = after.get("output_tokens", 0) - before.get("output_tokens", 0)
        pin, pout = PRICES.get(after.get("model"), PRICES["claude-haiku-5-5"])
        cost = f"**Cost:** {tin / 1e6:.2f}M input + {tout / 1e6:.2f}M output tokens, about ${tin / 1e6 * pin + tout / 1e6 * pout:.2f}"
    head = [f"# Message test: {args.name}", "", f"**Question:** {args.question}",
            f"**Engine:** MiroFish-Offline, {args.rounds} rounds on {args.platform}, model {(after or {}).get('model', 'unknown')}",
            f"**MiroFish ids:** project {ids['project_id']}, simulation {sim}, report {ids['report_id']}"]
    if cost:
        head.append(cost)
    out = "\n".join(head + ["", CAVEAT, "", md.strip(), ""])
    path = os.path.join(args.out, "MESSAGE-TEST.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(out)
    log(f"Report: {path}")
    return path


def check(args, client=None, log=print):
    c = client or Client(args.api, args.relay)
    h = c.get("/health")
    u = c.usage()
    model = (u or {}).get("model", "unknown")
    if h.get("status") != "ok":
        raise MiroFishError(f"health: {h}")
    log(f"MIROFISH UP {model.split('-')[1] if model.startswith('claude-') else model}")
    return model


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "check"):
        s = sub.add_parser(name)
        s.add_argument("--api", default=os.environ.get("MIROFISH_API", "http://127.0.0.1:5001"))
        s.add_argument("--relay", default=os.environ.get("MIROFISH_RELAY", "http://127.0.0.1:5011"))
        if name == "run":
            s.add_argument("brief")
            s.add_argument("--question", required=True)
            s.add_argument("--out", required=True)
            s.add_argument("--name", default="message test")
            s.add_argument("--rounds", type=int, default=12)
            s.add_argument("--platform", choices=["reddit", "twitter", "parallel"], default="reddit")
            s.add_argument("--timeout", type=int, default=5400)
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(line_buffering=True)  # progress shows live when logged to a file
    try:
        (run if args.cmd == "run" else check)(args)
    except MiroFishError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
