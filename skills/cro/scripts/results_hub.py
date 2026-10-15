#!/usr/bin/env python3
"""
results_hub.py — One results page for a whole CRO run: every skill run shown the same way.

Each skill run (audit, tracking check, readiness, personas, skeptic, synthetic swarm,
wireframe, deck, message test) is a different test with its own result set. This page
gives every one the same structure, in the same order:

    What it tested · Result (one bold sentence) · Key numbers · What it found ·
    Evidence (screenshots) · Cost and time · How sure we are · Files

with a sticky index to jump between results and previous/next links on each.
Facts come from the workspace files. The agent's judgment (the one-sentence result,
status, confidence, dropped items) comes from `results-notes.json` in the workspace,
so nothing is guessed by the script. A run that did not happen is left out.

The page ends with the experiments: the output of the whole run. `experiments.json`
in the workspace holds them (written by the agent from the results), each:
    {"id": "E1", "title": "...", "hypothesis": "Because we saw ..., we believe ... will ..., for ...",
     "evidence": ["audit", "synthetic"],   # result keys that show the problem
     "method": "ship + baseline | usability test | synthetic A/B | A/B test | interviews",
     "metric": "...", "steps": ["..."], "duration": "...", "decide": "...", "priority": "High"}
The method must follow the readiness verdict: no A/B test on a NOT_TESTABLE site.

Usage:
    results_hub.py <audit-workspace> [--wireframe <wireframe-workspace>] [-o results.html]

results-notes.json (all keys optional):
    {"title": "...", "overall": {"result": "...", "next": "..."},
     "<skill key>": {"result": "...", "status": "done|partial|failed", "confidence": "...",
                     "found": ["..."], "images": [["path", "caption"]], "links": [["label", "https://..."]],
                     "cost": "...", "time": "..."}}
Skill keys: audit, speed, tracking, readiness, personas, skeptic, synthetic, wireframe, deck, message_test.
Optional per run: "score": [7, "1 of 2 buyers reached booking"] when the files cannot give one,
"to_ten": ["..."] to replace the fixes listed under "To reach 10/10".
Optional top level: "verify": ["..."], how results get checked when traffic is too low for A/B tests.

Scores: each result that measures the site gets a score out of 10, so a page can be fixed and
rerun until it reaches 10/10. Computed from the files where possible (audit score, lab speed
against Google's Core Web Vitals limits, the tracking category, share of visitors reaching the
goal). Runs that measure our own work or the traffic (readiness, skeptic, wireframe, deck,
message test) get no score.
"""

import argparse
import base64
import html
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

CSS = """:root{--bg:#fafafa;--card:#fff;--text:#171717;--muted:#666;--line:#e5e5e5;--accent:#e5572f;--good:#16a34a;--warn:#b45309;--warnbg:#fffbeb;--bad:#b91c1c}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0a0a0a;--card:#161616;--text:#ededed;--muted:#a1a1a1;--line:#2a2a2a;--accent:#ff7a50;--good:#4ade80;--warn:#fbbf24;--warnbg:#1f1a0e;--bad:#f87171}}
:root[data-theme="dark"]{--bg:#0a0a0a;--card:#161616;--text:#ededed;--muted:#a1a1a1;--line:#2a2a2a;--accent:#ff7a50;--good:#4ade80;--warn:#fbbf24;--warnbg:#1f1a0e;--bad:#f87171}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:120px}
body{margin:0;background:var(--bg);color:var(--text);font-family:Geist,system-ui,sans-serif;font-size:17px;line-height:1.55}
main{max-width:860px;margin:0 auto;padding:24px 16px 80px}
h1{font-size:32px;line-height:1.2;margin:0 0 6px}.date{color:var(--muted);font-size:14px;margin:0 0 24px}
.verdict{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:10px;padding:18px 20px;margin-bottom:28px}
.verdict p{margin:0 0 8px}.verdict p:last-child{margin:0}
nav.index{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);margin:0 -16px;padding:10px 16px;display:flex;flex-wrap:wrap;gap:8px}
@media (max-width:600px){nav.index{flex-wrap:nowrap;overflow-x:auto;white-space:nowrap;scrollbar-width:thin}}
nav.index a{font-size:14px;text-decoration:none;color:var(--text);border:1px solid var(--line);background:var(--card);border-radius:20px;padding:4px 12px}
nav.index a:hover{border-color:var(--accent)}
h2{font-size:22px;margin:44px 0 14px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:15px}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}th{font-weight:600;color:var(--muted);font-size:13px}tr:last-child td{border-bottom:none}
section.run{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;margin:28px 0}
section.run h2{margin:0 0 4px;font-size:23px}.kicker{font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin:0 0 6px}
.result{font-size:18px;margin:10px 0 14px}.label{font-weight:600;font-size:14px;color:var(--muted);margin:16px 0 4px;text-transform:uppercase;letter-spacing:.04em}
.nums{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:6px 0 4px}
.num{border:1px solid var(--line);border-radius:10px;padding:10px 12px}.num b{display:block;font-size:22px}.num span{font-size:13px;color:var(--muted)}
.images{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:6px 0}.images figure{margin:0}
.images img{width:100%;border-radius:8px;border:1px solid var(--line);display:block}.images figcaption{font-size:13px;color:var(--muted);margin-top:4px}
ul{margin:0 0 6px;padding-left:20px}li{margin:3px 0}a{color:var(--accent)}
.status{display:inline-block;font-size:12px;font-weight:600;border-radius:20px;padding:2px 10px;border:1px solid var(--line)}
.status.done{color:var(--good)}.status.partial{color:var(--warn)}.status.failed{color:var(--bad)}
.score{font-weight:700;white-space:nowrap}.score.hi{color:var(--good)}.score.mid{color:var(--warn)}.score.lo{color:var(--bad)}.score.na{color:var(--muted);font-weight:400}
.bar{height:6px;border-radius:3px;background:var(--line);margin-top:4px;min-width:60px}.bar i{display:block;height:100%;border-radius:3px;background:currentColor}
.scorebox{display:flex;align-items:center;gap:16px;border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:10px 0}.scorebox .big{font-size:30px}
.meta{font-size:14px;color:var(--muted);margin:12px 0 0}.pager{display:flex;justify-content:space-between;gap:12px;margin-top:16px;font-size:14px;border-top:1px solid var(--line);padding-top:12px}
@media (max-width:600px){h1{font-size:26px}.images{grid-template-columns:1fr}.hide-mobile{display:none}}"""

ORDER = [
    ("audit", "Site audit", "How well do the key pages convert, page by page, across UX, copy, trust, visual and tracking?"),
    ("speed", "Page speed", "How fast do the key pages load on a throttled phone, against Google's Core Web Vitals limits?"),
    ("tracking", "Tracking check", "What measures visits and conversions today, is anything doubled or broken, and what access do we need?"),
    ("readiness", "Test readiness", "Are there enough conversions to run A/B tests, or is research the right method?"),
    ("personas", "Persona walk-throughs", "Can a realistic buyer reach the main conversion in a real browser, and where do they struggle?"),
    ("skeptic", "Skeptic review", "Does every finding survive an adversarial re-check against screenshots and the live site?"),
    ("synthetic", "Synthetic visitor swarm", "When many AI buyers browse the real site, how far do they get and what stops them?"),
    ("wireframe", "Fix wireframe", "What would the fixed page look like, change by change, tied to the findings?"),
    ("deck", "Client deck", "Can the owner understand the results and decide in one sitting?"),
    ("message_test", "Message test (MiroFish)", "Which offer, price or headline does a simulated crowd of buyers prefer, and why?"),
]


def esc(s):
    return html.escape(str(s), quote=True)


def shrink(path, width=640):
    """Small JPEG as a data URI so the page is one file. Falls back to the original bytes."""
    p = Path(path)
    if not p.exists():
        return None
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as t:
            out = t.name
        # Long phone captures would dominate the page: keep the top screen of anything taller than about 4:3.
        subprocess.run(["convert", str(p), "-resize", f"{width}x>", "-gravity", "north", "-crop", f"{width}x{int(width * 1.35)}+0+0",
                        "+repage", "-quality", "72", out], check=True, capture_output=True)
        data, mime = Path(out).read_bytes(), "image/jpeg"
        os.unlink(out)
    except (OSError, subprocess.CalledProcessError):
        data, mime = p.read_bytes(), "image/png" if p.suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(data).decode()


def read(p):
    p = Path(p)
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def jload(p):
    try:
        return json.loads(read(p) or "null")
    except ValueError:
        return None


# ------------------------------------------------------------- facts per skill run

def facts_audit(W, F):
    a = read(W / "FULL-AUDIT.md")
    if not a:
        return None
    m = re.search(r"CRO Health Score:?\**\s*(\d+)/100\s*\(?(\w+)?", a)
    cats = (F or {}).get("categories") or []
    pages = len([d for d in (W / "pages").iterdir() if d.is_dir()]) if (W / "pages").exists() else 0
    found = [f"{f['priority']}: {f['title']}" for f in (F or {}).get("findings", [])[:4]]
    nums = [(f"{m.group(1)}/100" if m else "?", f"score, {m.group(2) or ''}".strip(", ")), (str(pages), "pages captured")]
    nums += [(f"{c['score']}", c["name"]) for c in sorted(cats, key=lambda c: c["score"])[:2]]
    imgs = [(W / "pages/home/desktop.png", "Home page on desktop"), (W / "pages/home/mobile.png", "Home page on a phone")]
    return dict(nums=nums, found=found, images=imgs, files=["FULL-AUDIT.md", "ACTION-PLAN.md", "findings.json"])


LIMITS = {"LCP": (2.5, 4.0), "CLS": (0.1, 0.25), "TBT": (200, 600)}  # good / poor, Google Core Web Vitals (TBT stands in for INP)


def _num(v):
    m = re.match(r"\s*([\d.]+)", str(v or ""))
    return float(m.group(1)) if m else None


def facts_speed(W, F):
    rows = []
    for sp in sorted((W / "pages").glob("*/speed.json")) if (W / "pages").exists() else []:
        d = jload(sp) or {}
        lab = d.get("lab") or {}
        vals = {k: _num(lab.get(k)) for k in LIMITS}
        if any(v is not None for v in vals.values()):
            rows.append((sp.parent.name, vals, lab, d))
    if not rows:
        return None
    pts, misses = [], []
    for page, vals, lab, d in rows:
        for k, (good, poor) in LIMITS.items():
            v = vals[k]
            if v is None:
                continue
            pts.append(1 if v <= good else 0.5 if v <= poor else 0)
            if v > good:
                misses.append(f"{page}: {k} {lab.get(k)} (good is under {good}{' s' if k == 'LCP' else ' ms' if k == 'TBT' else ''})")
    worst = max(v["LCP"] or 0 for _, v, _, _ in rows)
    field = any(d.get("field_data") for *_, d in rows)
    found = [f"{page}: LCP {lab.get('LCP', '?')}, CLS {lab.get('CLS', '?')}, TBT {lab.get('TBT', '?')}, {lab.get('Requests', '?')} requests"
             for page, _, lab, _ in rows]
    nums = [(str(len(rows)), "pages measured"), (f"{worst:.1f} s", "slowest main content (LCP)"),
            ("yes" if field else "no", "real-visitor data")]
    return dict(nums=nums, found=found, images=[], files=["pages/*/speed.json", "findings/performance.md"],
                score=(round(10 * sum(pts) / len(pts), 1), "share of pages within Google's speed limits (lab, phone)"),
                to_ten=misses)


def score_for(k, fx, F, W):
    """(score out of 10 or None, basis, fixes that stand between the site and 10/10)."""
    F = F or {}
    fixes = lambda pred: [f"{f['id']}: {f['title']}" for f in F.get("findings", []) if pred(f)]
    cat = {c["name"].lower(): c["score"] for c in F.get("categories", [])}
    if k == "audit" and F.get("score") is not None:
        return F["score"] / 10, "audit health score / 10", fixes(lambda f: f["priority"] in ("Critical", "High"))
    if k == "speed" and fx and fx.get("score"):
        return fx["score"][0], fx["score"][1], fx.get("to_ten", [])
    if k == "tracking" and "tracking" in cat:
        return cat["tracking"] / 10, "tracking category of the audit / 10", fixes(lambda f: f.get("category") == "tracking")
    if k == "synthetic":
        c = jload(W / "synthetic/clusters.json") or {}
        fun, v = c.get("funnel", {}), c.get("visitors", 0)
        if v:
            conv = fun.get("checkout", fun.get("atc", 0))
            return round(10 * conv / v, 1), f"{conv} of {v} AI visitors reached the goal", \
                [f"{cl['visitors']} visitors: {cl['headline']}" for cl in c.get("clusters", [])[:4]]
    return None, "", []


def fmt_score(v):
    if v is None:
        return "<span class='score na'>no score</span>"
    cls = "hi" if v >= 8 else "mid" if v >= 5 else "lo"
    txt = f"{v:.1f}".rstrip("0").rstrip(".")
    return f"<span class='score {cls}'>{txt}/10<span class='bar'><i style='width:{v * 10:.0f}%'></i></span></span>"


def facts_tracking(W, F):
    t = jload(W / "tracking.json")
    if not t:
        return None
    tools = [f"{i['vendor']} on {i['pages']} page(s)" for i in t.get("inventory", [])]
    found = [("No analytics tool fires on any audited page" if not t.get("has_analytics") else "Analytics fires")]
    found += [f"Found: {x}" for x in tools[:3]]
    found += [f"Access needed: {r.split(':')[0]}" for r in t.get("access_requests", [])[:3]]
    nums = [(str(len(t.get("pages", []))), "pages checked"), (str(len(t.get("inventory", []))), "tools found"),
            ("yes" if t.get("has_analytics") else "no", "analytics"), (str(len(t.get("issues", []))), "issues")]
    return dict(nums=nums, found=found, images=[], files=["tracking.json", "TRACKING.md"])


def facts_readiness(W, F):
    r = read(W / "readiness.txt")
    if not r:
        return None
    v = re.search(r"Verdict:\s*(\w+)", r)
    inp = re.search(r"Inputs:\s*([^\n]+)", r)
    need = re.search(r"needed[^:]*:\s*~?([\d,]+)", r)
    rows = re.findall(r"^\s*(\d+)\s+\d+\s+\d+\s+([\d.]+)%", r, re.M)
    status = ((F or {}).get("readiness") or {}).get("status", "")
    nums = [(v.group(1).replace("_", " ") if v else "?", "verdict"), (status or "?", "baseline")]
    if rows:
        nums.append((f"{float(rows[-1][1]):.0f}%", f"smallest lift an {rows[-1][0]}-week test can see"))
    if need:
        nums.append((need.group(1), "conversions a month needed"))
    return dict(nums=nums, found=[f"Inputs: {inp.group(1)}"] if inp else [], images=[], files=["readiness.txt"])


def facts_personas(W, F):
    ps = [p for p in (F or {}).get("personas", []) if not p["id"].startswith("synthetic")]
    if not ps:
        return None
    found = [f"{p['id'].split('-', 1)[-1].replace('-', ' ').title()}: {p['goal']}. {p['outcome']}." for p in ps]
    imgs = [(W / p["worst_step_image"], f"Worst moment: {p['id'].split('-', 1)[-1].replace('-', ' ')}") for p in ps if p.get("worst_step_image")]
    steps = sum(len([s for s in (W / "personas" / p["id"]).glob("step-*.png")]) for p in ps)
    return dict(nums=[(str(len(ps)), "buyers played"), (str(steps), "screenshots")], found=found, images=imgs[:2],
                files=[f"personas/{p['id']}/" for p in ps])


def facts_skeptic(W, F):
    s = read(W / "findings/skeptic.md")
    if not s:
        return None
    def count(label):
        m = re.search(rf"^- {label}[^:]*:\s*(\d+)", s, re.M)
        return int(m.group(1)) if m else 0
    k, rw, rj = count("KEEP"), count("REWORD"), count("REJECT")
    dn = re.search(r"also DOWNGRADE:\s*(\d+)", s)
    nums = [(str(k + rw + rj), "findings checked"), (str(k), "kept as written"), (str(rw), "reworded"), (str(rj), "rejected")]
    found = [f"{dn.group(1)} reworded findings also lost a priority level"] if dn else []
    return dict(nums=nums, found=found, images=[], files=["findings/skeptic.md"])


def facts_synthetic(W, F, folder="synthetic"):
    c = jload(W / folder / "clusters.json")
    if not c:
        return None
    fun = c.get("funnel", {})
    conv = fun.get("checkout", fun.get("atc", 0))
    u = c.get("usage", {})
    nums = [(str(c.get("visitors", 0)), "visitors"), (f"{conv} of {c.get('visitors', 0)}", "reached the goal"),
            (f"${c.get('usd', 0):.2f}", "model cost"), (c.get("templates_source", "?"), "traffic mix")]
    found = [f"{cl['visitors']} visitors: {cl['headline']}" for cl in c.get("clusters", [])[:4]]
    return dict(nums=nums, found=found, images=[], files=[f"{folder}/SYNTHETIC-REPORT.md", f"{folder}/clusters.json"],
                cost=f"{u.get('input_tokens', 0) / 1e6:.2f}M input + {u.get('output_tokens', 0) / 1e6:.2f}M output tokens")


def facts_wireframe(WF):
    if not WF or not (WF / "renders").exists():
        return None
    ann = jload(WF / "annotations.json") or []
    r = WF / "renders"
    pick = lambda *names: next((r / n for n in names if (r / n).exists()), None)
    imgs = [(pick("before-mobile-fold.png", "before-mobile.png"), "Today"), (pick("after-mobile-fold.png", "after-mobile.png"), "Proposed, not a measured result")]
    return dict(nums=[(str(len(ann)), "changes"), ("390 + 1440", "px widths rendered")],
                found=[f"{a['finding_id']}: {a['change']}" for a in ann[:4]], images=[i for i in imgs if i[0]],
                files=["before.html", "after.html", "annotations.json", "DESIGN-NOTES.md"])


def facts_deck(W):
    s = jload(W / "slides.json")
    if not s:
        return None
    slides = s.get("slides", [])
    kinds = sorted({x["type"] for x in slides})
    r = W / "deck-render"
    imgs = [(r / "slide-01.png", "Opening slide"), (r / "slide-05.png", "A finding slide")]
    return dict(nums=[(str(len(slides)), "slides"), (s.get("mode", "PITCH").title(), "mode"),
                      (str(len([x for x in slides if x["type"] == "finding"])), "finding slides")],
                found=[f"Slide types: {', '.join(kinds)}"], images=[i for i in imgs if i[0].exists()], files=["slides.json", "deck.html"])


def facts_message_test(W):
    run = jload(W / "message-test/run.json")
    if not run:
        return None
    done = (W / "message-test/MESSAGE-TEST.md").exists()
    return dict(nums=[(str(run.get("rounds", "?")), "rounds planned"), (run.get("platform", "?"), "platform"),
                      ("yes" if done else "no", "report written")],
                found=[f"Question: {run.get('question', '')}"], images=[], files=["message-test/brief.md", "message-test/run.json"])


# ------------------------------------------------------------- page

def build(W, WF=None):
    W = Path(W)
    WF = Path(WF) if WF else None
    F = jload(W / "findings.json") or {}
    N = jload(W / "results-notes.json") or {}
    facts = {"audit": facts_audit(W, F), "speed": facts_speed(W, F), "tracking": facts_tracking(W, F), "readiness": facts_readiness(W, F),
             "personas": facts_personas(W, F), "skeptic": facts_skeptic(W, F), "synthetic": facts_synthetic(W, F),
             "wireframe": facts_wireframe(WF), "deck": facts_deck(W), "message_test": facts_message_test(W)}
    runs = [(k, name, q, facts[k], N.get(k, {})) for k, name, q in ORDER if facts.get(k) or N.get(k)]
    X = jload(W / "experiments.json") or []
    S = {}
    for k, _, _, fx, n in runs:
        v, basis, fix = score_for(k, fx, F, W)
        if n.get("score"):
            v, basis = float(n["score"][0]), n["score"][1]
        S[k] = (None if v is None else max(0.0, min(10.0, v)), basis, n.get("to_ten", fix))
    site = F.get("site") or W.name
    title = N.get("title") or f"{site}: CRO results"

    out = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>",
           f"<title>{esc(title)}</title><link rel='preconnect' href='https://fonts.googleapis.com'>",
           "<link href='https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap' rel='stylesheet'>",
           f"<style>{CSS}</style></head><body><main>",
           f"<h1>{esc(title)}</h1><p class='date'>{esc(F['date']) + ' · ' if F.get('date') else ''}{len(runs)} results · about {max(2, len(runs) // 2)} min read</p>"]
    ov = N.get("overall", {})
    if ov:
        out.append(f"<div class='verdict'><p><b>{esc(ov.get('result', ''))}</b></p>"
                   + (f"<p><b>Next:</b> {esc(ov['next'])}</p>" if ov.get("next") else "") + "</div>")
    out.append("<nav class='index' aria-label='Results'>" + "".join(
        f"<a href='#{k}'>{i}. {esc(name)}</a>" for i, (k, name, *_ ) in enumerate(runs, 1))
        + (f"<a href='#experiments'><b>Experiments ({len(X)})</b></a>" if X else "")
        + ("<a href='#verify'>How we verify</a>" if N.get("verify") else "") + "</nav>")

    out.append("<h2>All results</h2><table><tr><th>#</th><th>Skill run</th><th>Score</th><th>Result</th><th class='hide-mobile'>Status</th></tr>")
    for i, (k, name, q, fx, n) in enumerate(runs, 1):
        st = n.get("status", "done")
        out.append(f"<tr><td>{i}</td><td><a href='#{k}'>{esc(name)}</a></td><td>{fmt_score(S[k][0])}</td><td>{esc(n.get('result', q))}</td>"
                   f"<td class='hide-mobile'><span class='status {esc(st)}'>{esc(st)}</span></td></tr>")
    out.append("</table><p class='meta'>Scores are out of 10 for each result that measures the site. "
               "Fix what is listed under \"To reach 10/10\", rerun the same test, and the score updates. "
               "No score means the run checks our own work or the traffic, not the page.</p>")

    for i, (k, name, q, fx, n) in enumerate(runs, 1):
        fx = fx or {}
        st = n.get("status", "done")
        out.append(f"<section class='run' id='{k}'><p class='kicker'>Result {i} of {len(runs)} · <span class='status {esc(st)}'>{esc(st)}</span></p>")
        out.append(f"<h2>{esc(name)}</h2>")
        out.append(f"<div class='label'>What it tested</div><p style='margin:0'>{esc(q)}</p>")
        if n.get("result"):
            out.append(f"<div class='label'>Result</div><p class='result' style='margin-top:0'><b>{esc(n['result'])}</b></p>")
        v, basis, fix = S[k]
        if v is not None:
            out.append(f"<div class='scorebox'><span class='big'>{fmt_score(v)}</span><span class='meta' style='margin:0'>{esc(basis)}</span></div>")
            out.append("<div class='label'>To reach 10/10</div>" + ("<ul>" + "".join(f"<li>{esc(x)}</li>" for x in fix) + "</ul>"
                       if fix else "<p style='margin:0'>Nothing left to fix on this test.</p>"))
        if fx.get("nums"):
            out.append("<div class='nums'>" + "".join(f"<div class='num'><b>{esc(v)}</b><span>{esc(l)}</span></div>" for v, l in fx["nums"]) + "</div>")
        found = n.get("found") or fx.get("found") or []
        if found:
            out.append("<div class='label'>What it found</div><ul>" + "".join(f"<li>{esc(x)}</li>" for x in found) + "</ul>")
        imgs = [(Path(p) if os.path.isabs(p) else W / p, c) for p, c in n.get("images", [])] or fx.get("images", [])
        figs = [(shrink(p), c) for p, c in imgs[:4]]
        figs = [(d, c) for d, c in figs if d]
        if figs:
            out.append("<div class='label'>Evidence</div><div class='images'>" + "".join(
                f"<figure><img src='{d}' alt='{esc(c)}'><figcaption>{esc(c)}</figcaption></figure>" for d, c in figs) + "</div>")
        meta = []
        if n.get("cost") or fx.get("cost"):
            meta.append(f"<b>Cost:</b> {esc(n.get('cost') or fx.get('cost'))}")
        if n.get("time"):
            meta.append(f"<b>Time:</b> {esc(n['time'])}")
        if n.get("confidence"):
            meta.append(f"<b>How sure:</b> {esc(n['confidence'])}")
        links = n.get("links", [])
        if links:
            meta.append("<b>Open:</b> " + ", ".join(f"<a href='{esc(u)}'>{esc(l)}</a>" for l, u in links))
        if fx.get("files"):
            meta.append(f"<b>Files in the run folder:</b> {esc(', '.join(fx['files']))}")
        out.append("".join(f"<p class='meta'>{m}</p>" for m in meta))
        prev_ = f"<a href='#{runs[i - 2][0]}'>&larr; {esc(runs[i - 2][1])}</a>" if i > 1 else "<span></span>"
        next_ = f"<a href='#{runs[i][0]}'>{esc(runs[i][1])} &rarr;</a>" if i < len(runs) \
            else ("<a href='#experiments'>Experiments &rarr;</a>" if X else "<a href='#top'>Back to top</a>")
        out.append(f"<div class='pager'>{prev_}{next_}</div></section>")

    if X:
        names = {k: (i, name) for i, (k, name, *_ ) in enumerate(runs, 1)}
        out.append(f"<section id='experiments'><h2>Experiments: what we test next ({len(X)})</h2>"
                   "<p>Every result above feeds these. Each one says what we believe, which results show the problem, "
                   "how to run it at this site's traffic, and when to call it.</p>")
        for e in X:
            ev = ", ".join(f"<a href='#{k}'>{names[k][0]}. {esc(names[k][1])}</a>" for k in e.get("evidence", []) if k in names)
            out.append(f"<section class='run' id='{esc(e['id'])}'><p class='kicker'>{esc(e['id'])} · {esc(e.get('priority', ''))} · {esc(e.get('method', ''))}</p>"
                       f"<h2>{esc(e['title'])}</h2><div class='label'>Hypothesis</div><p class='result' style='margin-top:0'><b>{esc(e['hypothesis'])}</b></p>")
            if ev:
                out.append(f"<div class='label'>Evidence from</div><p style='margin:0'>{ev}</p>")
            if e.get("steps"):
                out.append("<div class='label'>How to run it</div><ol>" + "".join(f"<li>{esc(x)}</li>" for x in e["steps"]) + "</ol>")
            out.append("<div class='nums'>" + "".join(f"<div class='num'><b style='font-size:16px'>{esc(e[k])}</b><span>{l}</span></div>"
                       for k, l in (("metric", "what we measure"), ("duration", "how long"), ("decide", "when we call it")) if e.get(k)) + "</div></section>")
        out.append("</section>")
    if N.get("verify"):
        out.append("<section id='verify'><h2>How we verify results at this traffic</h2>"
                   "<p>Too few conversions for an A/B test means no single number proves a change. "
                   "We stack weaker checks that point the same way:</p><ol>"
                   + "".join(f"<li>{esc(x)}</li>" for x in N["verify"]) + "</ol></section>")
    out.append("<h2>How these results were made</h2><p>Each section is one skill run on the same site, shown the same way. "
               "Numbers come straight from the run files; the one-line results are the reviewer's reading of them. "
               "Simulated visitors and simulated opinion are early signals, not measured conversion results.</p>")
    out.append("</main></body></html>")
    return "\n".join(out).replace("<main>", "<main id='top'>", 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workspace")
    ap.add_argument("--wireframe")
    ap.add_argument("-o", "--output")
    a = ap.parse_args()
    out = Path(a.output or Path(a.workspace) / "results.html")
    out.write_text(build(a.workspace, a.wireframe), encoding="utf-8")
    print(f"Results page: {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
