#!/usr/bin/env python3
"""Render structured audit slides as portable HTML. See cro-slides/references/slides-schema.md."""

import argparse
import base64
import hashlib
import html
import json
import math
import mimetypes
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import quote, urlparse


TYPES = {"title", "bottom-line", "score", "test-readiness", "finding", "before-after",
         "strengths", "roadmap", "offer", "next-steps", "appendix"}
MEANINGS = {
    "READY": "Enough orders to compare two versions of a page in a regular A/B testing program.",
    "LIMITED": "Research first. Only large changes are worth comparing, with 6-8 weeks per test.",
    "NOT_TESTABLE": "Not enough orders for reliable A/B tests. Watch customers use the site, fix problems, and track the baseline.",
}


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: expected non-empty text")
    return value


def number(value, label, low=0, high=100):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{label}: expected a number from {low} to {high}")
    return value


def strings(value, label, low=1, high=6):
    if not isinstance(value, list) or not low <= len(value) <= high:
        raise ValueError(f"{label}: expected {low}-{high} text items")
    for item in value:
        text(item, label)


def fields(obj, names, label):
    if not isinstance(obj, dict):
        raise ValueError(f"{label}: expected an object")
    for name in names.split():
        text(obj.get(name), f"{label}.{name}")


def link(value, label):
    text(value, label)
    parsed = urlparse(value)
    if parsed.scheme not in {"https", "http", "mailto", "tel"} or not parsed.path and not parsed.netloc:
        raise ValueError(f"{label}: use an https, http, mailto or tel link")
    return value


def validate(data):
    fields(data, "site", "deck")
    mode = data.get("mode", "PITCH")
    if mode not in {"PITCH", "CLIENT"}:
        raise ValueError("mode: use PITCH or CLIENT")
    fields(data.get("consultant"), "name site contact", "consultant")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", data.get("brand", "#21594e")):
        raise ValueError("brand: use a six-digit hex color")
    slides = data.get("slides")
    if not isinstance(slides, list) or not 1 <= len(slides) <= 30:
        raise ValueError("slides: expected 1-30 slides (aim for 12-15)")
    for i, s in enumerate(slides, 1):
        fields(s, "type title", f"slide {i}")
        kind = s["type"]
        if kind not in TYPES:
            raise ValueError(f"slide {i}: unknown type {kind}")
        if "source" in s:
            text(s["source"], "source")
        if kind == "title":
            fields(s, "subtitle", kind)
        elif kind == "bottom-line":
            strings(s.get("sentences"), kind, 3, 3)
        elif kind == "score":
            number(s.get("overall"), "overall")
            fields(s, "evidence", kind)
            cats = s.get("categories")
            if not isinstance(cats, list) or not 1 <= len(cats) <= 8:
                raise ValueError("categories: expected 1-8 categories")
            for c in cats:
                fields(c, "name", "category")
                number(c.get("score"), "category.score")
                number(c.get("weight"), "category.weight")
            if abs(sum(c["weight"] for c in cats) - 100) > .1:
                raise ValueError("category weights must total 100")
            weighted = sum(c["score"] * c["weight"] / 100 for c in cats)
            if abs(s["overall"] - weighted) > .51:
                raise ValueError("overall must match the rounded weighted category score")
        elif kind == "test-readiness":
            fields(s, "verdict baseline evidence", kind)
            if s["verdict"] not in MEANINGS:
                raise ValueError("verdict: use READY, LIMITED or NOT_TESTABLE")
            if s.get("status") not in {"CONFIRMED", "ASSUMED"}:
                raise ValueError("readiness status: use CONFIRMED or ASSUMED")
        elif kind == "finding":
            fields(s, "image problem evidence why fix", kind)
            calls = s.get("callouts")
            if not isinstance(calls, list) or not 1 <= len(calls) <= 4:
                raise ValueError("finding.callouts: expected 1-4 boxes")
            for c in calls:
                if not isinstance(c, dict):
                    raise ValueError("callout: expected an object")
                for key in ("x", "y", "w", "h"):
                    number(c.get(key), f"callout.{key}")
                if c["w"] <= 0 or c["h"] <= 0 or c["x"] + c["w"] > 100 or c["y"] + c["h"] > 100:
                    raise ValueError("callout must fit inside the image")
                text(c.get("label"), "callout.label")
        elif kind == "before-after":
            fields(s, "before after before_label after_label evidence", kind)
        elif kind in {"strengths", "appendix"}:
            strings(s.get("items"), "items", 1, 6)
        elif kind == "roadmap":
            phases = s.get("phases")
            if not isinstance(phases, list) or len(phases) != 3:
                raise ValueError("roadmap.phases: expected 3 phases (30/60/90 days)")
            for phase in phases:
                fields(phase, "label", "phase")
                strings(phase.get("items"), "phase.items", 1, 4)
            fields(s, "measurement", kind)
        elif kind == "offer":
            if mode == "CLIENT":
                raise ValueError("CLIENT decks must not contain an offer")
            packages = s.get("packages")
            if not isinstance(packages, list) or len(packages) not in {1, 3}:
                raise ValueError("offer.packages: use one package or three tiers")
            for p in packages:
                fields(p, "name price timeline", "package")
                strings(p.get("deliverables"), "deliverables", 1, 5)
            fields(s, "proof", kind)
        elif kind == "next-steps":
            strings(s.get("items"), "items", 1, 4)
            if "url" in s:
                link(s["url"], "next-steps.url")
                fields(s, "label", kind)
    return data


def esc(value):
    return html.escape(str(value), quote=True)


def bullets(items):
    return '<ul>' + ''.join(f'<li>{esc(item)}</li>' for item in items) + '</ul>'


class Media:
    def __init__(self, source, output, embed):
        self.source, self.output, self.embed = source, output, embed

    def image(self, name):
        path = (self.source / name).resolve()
        if not path.is_file():
            raise ValueError(f"missing image: {path}")
        mime = mimetypes.guess_type(path.name)[0]
        if mime not in {"image/png", "image/jpeg", "image/gif", "image/webp"}:
            raise ValueError(f"image must be PNG, JPEG, GIF or WebP: {path}")
        content = path.read_bytes()
        if self.embed:
            return f'data:{mime};base64,{base64.b64encode(content).decode("ascii")}'
        folder = self.output.parent / (self.output.stem + "-assets")
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / (hashlib.sha256(content).hexdigest()[:16] + path.suffix.lower())
        if path != dest:
            shutil.copyfile(path, dest)
        return quote(f"{folder.name}/{dest.name}")

    def shot(self, name, alt, callouts=()):
        boxes = ''.join(
            f'<span class="callout" style="left:{c["x"]}%;top:{c["y"]}%;width:{c["w"]}%;height:{c["h"]}%" '
            f'aria-label="{i}: {esc(c["label"])}"><b>{i}</b></span>'
            for i, c in enumerate(callouts, 1))
        return (f'<div class="visual"><div class="shot"><img src="{self.image(name)}" '
                f'alt="{esc(alt)}">{boxes}</div></div>')


def slide_body(s, media):
    kind = s["type"]
    if kind == "title":
        return f'<p class="lead">{esc(s["subtitle"])}</p>' + (media.shot(s["image"], s.get("image_alt", "Audited website")) if s.get("image") else '')
    if kind == "bottom-line":
        return '<div class="bottom-lines">' + ''.join(
            f'<div class="statement"><span class="step">0{i}</span><p>{esc(t)}</p></div>'
            for i, t in enumerate(s["sentences"], 1)) + '</div>'
    if kind == "score":
        bars = ''.join(f'<div class="bar-row"><div><span>{esc(c["name"])}</span><strong>{c["score"]:g}<small>/100</small></strong></div>'
                       f'<div class="track"><span style="width:{c["score"]}%"></span></div><small>Weight {c["weight"]:g}%</small></div>' for c in s["categories"])
        return (f'<div class="score-layout"><div><div class="score-number">{s["overall"]:g}<small>/100</small></div>'
                f'<p class="muted">Audit score, not a sales forecast</p><p class="evidence">{esc(s["evidence"])}</p></div><div class="bars">{bars}</div></div>')
    if kind == "test-readiness":
        return (f'<div class="readiness"><span class="badge">{esc(s["verdict"].replace("_", " "))}</span>'
                f'<p class="readiness-meaning">{esc(MEANINGS[s["verdict"]])}</p>'
                f'<div class="card"><h3>{esc(s["status"])} baseline</h3><p>{esc(s["baseline"])}</p></div>'
                f'<p class="evidence">{esc(s["evidence"])}</p></div>')
    if kind == "finding":
        legend = ' · '.join(f'{i}. {esc(c["label"])}' for i, c in enumerate(s["callouts"], 1))
        return ('<div class="finding-layout"><figure>' + media.shot(s["image"], s.get("image_alt", s["problem"]), s["callouts"]) +
                f'<figcaption>{legend}</figcaption></figure><div class="finding-copy">' +
                ''.join(f'<div class="finding-block"><h3>{label}</h3><p>{esc(s[key])}</p></div>' for key, label in
                        (("problem", "What we saw"), ("evidence", "Evidence"), ("why", "Why this may lose sales"), ("fix", "What we would change"))) + '</div></div>')
    if kind == "before-after":
        return ('<div class="comparison">' + ''.join(
            f'<figure>{media.shot(s[key], s[label])}<figcaption>{esc(s[label])}</figcaption></figure>'
            for key, label in (("before", "before_label"), ("after", "after_label"))) +
                f'</div><p class="evidence">{esc(s["evidence"])}</p>')
    if kind in {"strengths", "appendix"}:
        return f'<div class="list-panel">{bullets(s["items"])}</div>'
    if kind == "roadmap":
        return '<div class="cards">' + ''.join(
            f'<div class="card"><h3>{esc(p["label"])}</h3>{bullets(p["items"])}</div>' for p in s["phases"]) + f'</div><p class="measurement"><strong>How we prove progress</strong> {esc(s["measurement"])}</p>'
    if kind == "offer":
        return f'<div class="cards packages count-{len(s["packages"])}">' + ''.join(
            f'<div class="card"><h3>{esc(p["name"])}</h3><p class="price">{esc(p["price"])}</p><p class="muted">{esc(p["timeline"])}</p>{bullets(p["deliverables"])}</div>'
            for p in s["packages"]) + f'</div><p class="measurement"><strong>Proof, not promises</strong> {esc(s["proof"])}</p>'
    if kind == "next-steps":
        cta = f'<a class="cta" href="{esc(s["url"])}">{esc(s["label"])} <span aria-hidden="true">↗</span></a>' if s.get("url") else ''
        return f'<div class="next">{bullets(s["items"])}{cta}</div>'
    raise ValueError(f"unknown slide type: {kind}")


CSS = """
:root{--brand:BRAND;--ink:#182c2b;--muted:#5d6b67;--paper:#fffefa;--line:#dce4dd;--soft:#eff3ed}
*{box-sizing:border-box}body{margin:0;background:#e8ece7;color:var(--ink);font-family:Arial,Helvetica,sans-serif;line-height:1.45}
button,a{-webkit-tap-highlight-color:transparent}button{font:inherit}button:focus-visible,a:focus-visible{outline:3px solid var(--brand);outline-offset:4px}
#deck{width:min(100vw,calc((100dvh - 74px)*16/9));margin:18px auto 0;container-type:inline-size}
.slide{display:none;position:relative;aspect-ratio:16/9;width:100%;background:var(--paper);padding:3.6cqw 4.8cqw 4.5cqw;overflow:hidden;border-top:.55cqw solid var(--brand)}
.slide.active{display:flex;flex-direction:column;box-shadow:0 16px 60px #182c2b18}.kicker{display:flex;align-items:center;gap:1cqw;justify-content:space-between;color:var(--brand);font-size:1cqw;letter-spacing:.13em;text-transform:uppercase;margin-bottom:1.5cqw;min-height:1.5cqw}.logo{max-width:10cqw;max-height:2.4cqw;object-fit:contain}
h1{font-size:3.4cqw;letter-spacing:-.045em;line-height:1.12;margin:0 0 2.2cqw;max-width:94%;font-weight:700}h3{font-size:1.1cqw;margin:0 0 .65cqw;text-transform:uppercase;letter-spacing:.08em;color:var(--brand)}p{margin:0 0 1cqw}ul{margin:0;padding-left:1.5em}li{padding-left:.3em;margin-bottom:.8cqw}li::marker{color:var(--brand)}.body{flex:1;min-height:0;font-size:1.5cqw}.muted,small{color:var(--muted)}small{font-size:.9cqw}.lead{font-size:2cqw;max-width:80%}.source{font-size:.85cqw;color:var(--muted);margin-top:auto;padding-top:.6cqw;overflow-wrap:anywhere}
.footer{position:absolute;bottom:1.4cqw;left:4.8cqw;right:4.8cqw;display:flex;justify-content:space-between;gap:2cqw;border-top:1px solid var(--line);padding-top:.7cqw;font-size:.82cqw;color:var(--muted)}.footer span:first-child{max-width:82%}.footer span{overflow-wrap:anywhere}
.bottom-lines{display:grid;gap:1.25cqw}.statement{display:flex;gap:2cqw;padding:1.5cqw 0;border-bottom:1px solid var(--line)}.statement p{font-size:2.05cqw;line-height:1.35;margin:0;max-width:91%}.step{font-size:1.25cqw;color:var(--brand);font-weight:bold;padding-top:.3cqw}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5cqw}.card{background:var(--soft);border:1px solid var(--line);border-radius:.7cqw;padding:1.8cqw;min-width:0}.card li{font-size:1.35cqw}.measurement{margin-top:1.7cqw;font-size:1.25cqw;max-width:95%}.measurement strong{display:block;margin-bottom:.4cqw}.price{font-size:2.25cqw;font-weight:bold;letter-spacing:-.04em}.packages.count-1{grid-template-columns:1fr;max-width:80%}.packages.count-1 .card{display:grid;grid-template-columns:1fr 2fr;column-gap:3cqw}.packages.count-1 h3,.packages.count-1 .price,.packages.count-1 .muted{grid-column:1}.packages.count-1 ul{grid-column:2;grid-row:1/4}.packages .muted{font-size:1.15cqw}
.score-layout{display:grid;grid-template-columns:1fr 1.5fr;gap:6cqw}.score-number{font-size:10cqw;line-height:1.1;letter-spacing:-.07em;color:var(--brand)}.score-number small{font-size:2cqw;letter-spacing:0}.bars{display:grid;gap:.7cqw}.bar-row>div:first-child{display:flex;justify-content:space-between;font-size:1.2cqw}.track{height:.5cqw;background:var(--line);margin:.3cqw 0 .15cqw;border-radius:1cqw;overflow:hidden}.track span{display:block;height:100%;background:var(--brand)}.evidence{font-size:1.1cqw;color:var(--muted);margin-top:1.2cqw;overflow-wrap:anywhere}.badge{display:inline-block;background:var(--soft);border:1px solid var(--line);border-radius:2em;padding:.45em 1em;font-size:1.15cqw;letter-spacing:.08em;color:var(--brand);font-weight:bold}.readiness{max-width:88%}.readiness-meaning{font-size:2.3cqw;line-height:1.3;margin:1.5cqw 0 2cqw}.readiness .card{padding:1.3cqw 1.7cqw}.readiness .card p{margin:0}
.finding-layout{display:grid;grid-template-columns:1.25fr 1fr;gap:3cqw;height:100%}.finding-copy{display:grid;align-content:start;gap:1.1cqw}.finding-block p{font-size:1.25cqw;line-height:1.4;margin:0}.finding-block h3{font-size:.95cqw;margin-bottom:.35cqw}figure{margin:0;min-width:0}.visual{display:flex;justify-content:center;align-items:center;min-width:0;max-width:100%;--shot-height:29cqw}.shot{position:relative;display:inline-grid;max-width:100%;line-height:0;box-shadow:0 2px 16px #182c2b16}.shot img{display:block;max-width:100%;max-height:var(--shot-height);width:auto;height:auto;object-fit:contain}.callout{position:absolute;border:2px solid var(--brand);background:color-mix(in srgb,var(--brand) 9%,transparent);pointer-events:none;line-height:1}.callout b{position:absolute;top:0;left:0;background:var(--brand);color:white;font-size:1cqw;padding:.25em .4em;min-width:1.5em;text-align:center}figcaption{font-size:1cqw;line-height:1.35;margin-top:1cqw;color:var(--muted)}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:2cqw}.comparison .visual{--shot-height:27cqw}.title .visual{--shot-height:20cqw;justify-content:flex-start}.list-panel{background:var(--soft);border-radius:.8cqw;padding:2cqw 2.5cqw;max-width:95%}.list-panel li{margin-bottom:1.3cqw;font-size:1.65cqw}.list-panel li:last-child{margin-bottom:0}.next{max-width:90%;font-size:1.9cqw}.next li{margin-bottom:1.3cqw}.cta{display:inline-flex;gap:3cqw;background:var(--brand);color:white;text-decoration:none;padding:.8em 1.3em;border-radius:.4cqw;font-size:1.6cqw;margin-top:1.5cqw}
.controls{height:56px;display:flex;align-items:center;justify-content:center;gap:20px}.controls button{background:var(--paper);border:1px solid #c1cec5;border-radius:7px;padding:6px 18px;cursor:pointer;color:var(--ink)}.controls button:disabled{opacity:.4;cursor:default}#counter{font-size:13px;min-width:65px;text-align:center}.hint{font-size:11px;color:var(--muted)}
@media(max-width:600px){#deck{width:100%;margin:0}.slide{aspect-ratio:auto;min-height:calc(100dvh - 62px);padding:25px 22px 75px;border-top-width:5px;overflow:visible}.slide.active{box-shadow:none}.kicker{font-size:10px;min-height:24px;margin-bottom:22px;gap:12px}.logo{max-width:80px;max-height:28px}h1{font-size:32px;margin-bottom:24px;max-width:100%}.body{font-size:17px;min-height:auto}.lead{font-size:20px;max-width:100%}h3{font-size:12px;margin-bottom:9px}.bottom-lines{gap:12px}.statement{gap:18px;padding:16px 0}.statement p{font-size:21px;max-width:90%}.step{font-size:13px;padding-top:5px}.cards,.score-layout,.finding-layout,.comparison{display:grid;grid-template-columns:1fr;gap:20px;height:auto}.card{padding:20px;border-radius:10px}.card li,.packages .muted{font-size:16px}li{margin-bottom:12px}.measurement{font-size:15px;margin-top:22px;max-width:100%}.price{font-size:30px}.packages.count-1{max-width:100%}.packages.count-1 .card{display:block}.score-number{font-size:100px}.score-number small{font-size:24px}small{font-size:12px}.bars{gap:12px}.bar-row>div:first-child{font-size:16px}.track{height:7px;margin:6px 0 3px}.evidence{font-size:13px;margin-top:16px}.badge{font-size:12px}.readiness{max-width:100%}.readiness-meaning{font-size:23px;margin:22px 0}.readiness .card{padding:18px}.finding-copy{gap:18px}.finding-block p{font-size:16px}.finding-block h3{font-size:11px;margin-bottom:6px}.visual,.comparison .visual,.title .visual{--shot-height:420px}.callout b{font-size:12px}figcaption{font-size:12px;margin-top:10px}.list-panel{max-width:100%;padding:22px;border-radius:9px}.list-panel li{font-size:17px;margin-bottom:16px}.next{font-size:20px;max-width:100%}.next li{margin-bottom:18px}.cta{font-size:18px;border-radius:6px;margin-top:18px;gap:22px}.source{font-size:11px;margin-top:22px;padding-top:0}.footer{left:22px;right:22px;bottom:16px;font-size:10px;padding-top:9px;gap:12px}.controls{position:sticky;bottom:0;background:#e8ece7ed;height:62px;gap:12px}.hint{display:none}}
@page{size:13.333333in 7.5in;margin:0}
@media print{html,body{margin:0!important;background:white!important;width:1280px;-webkit-print-color-adjust:exact;print-color-adjust:exact}#deck{display:block;width:1280px;margin:0;container-type:inline-size}.slide,.slide.active{display:flex!important;width:1280px;height:720px;aspect-ratio:16/9;break-after:page;break-inside:avoid;box-shadow:none}.slide:last-child{break-after:auto}.controls{display:none!important}}
"""

JS = """
const slides=[...document.querySelectorAll('.slide')];
let current=0;
function show(index){current=Math.max(0,Math.min(slides.length-1,index));slides.forEach((s,i)=>{s.classList.toggle('active',i===current);s.setAttribute('aria-hidden',i!==current)});document.querySelector('#counter').textContent=`${current+1} / ${slides.length}`;document.querySelector('#prev').disabled=current===0;document.querySelector('#next').disabled=current===slides.length-1;history.replaceState(null,'',`#slide-${current+1}`);window.scrollTo(0,0)}
window.showSlide=show;
document.querySelector('#prev').onclick=()=>show(current-1);
document.querySelector('#next').onclick=()=>show(current+1);
document.addEventListener('keydown',e=>{if(e.target.closest('a,button,input,textarea,select'))return; if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)){e.preventDefault();show(current+1)}if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();show(current-1)}if(e.key==='Home'){e.preventDefault();show(0)}if(e.key==='End'){e.preventDefault();show(slides.length-1)}});
document.querySelector('#deck').onclick=e=>{if(e.target.closest('a,button'))return;const r=e.currentTarget.getBoundingClientRect();show(current+(e.clientX-r.left<r.width/3?-1:1))};
show((Number(location.hash.match(/^#slide-(\\d+)$/)?.[1])||1)-1);
"""


def build(data, source, output, embed=True):
    validate(data)
    output.parent.mkdir(parents=True, exist_ok=True)
    media = Media(source, output, embed)
    consultant = data["consultant"]
    mode = data.get("mode", "PITCH")
    logo = f'<img class="logo" src="{media.image(data["logo"])}" alt="{esc(consultant["name"])} logo">' if data.get("logo") else ''
    pages = []
    for i, s in enumerate(data["slides"], 1):
        source_note = f'<p class="source">Source: {esc(s["source"])}</p>' if s.get("source") else ''
        pages.append(f'<section class="slide {esc(s["type"])}" aria-label="Slide {i}: {esc(s["title"])}">'
                     f'<div class="kicker"><span>{esc(data["site"])} / {"Initial audit" if mode == "PITCH" else "Audit & roadmap"}</span>{logo}</div>'
                     f'<h1>{esc(s["title"])}</h1><div class="body">{slide_body(s, media)}</div>{source_note}'
                     f'<div class="footer"><span>{esc(consultant["name"])} · {esc(consultant["site"])} · {esc(consultant["contact"])}</span><span>{i:02d} / {len(data["slides"]):02d}</span></div></section>')
    title = esc(data.get("title", f'{data["site"]} | Conversion audit'))
    output.write_text('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
                      '<meta name="viewport" content="width=device-width,initial-scale=1">'
                      f'<title>{title}</title><style>{CSS.replace("BRAND", data.get("brand", "#21594e"))}</style></head>'
                      '<body><main id="deck">' + ''.join(pages) + '</main><nav class="controls" aria-label="Slide navigation">'
                      '<button id="prev" aria-label="Previous slide">←</button><span id="counter" aria-live="polite"></span>'
                      '<button id="next" aria-label="Next slide">→</button><span class="hint">Arrow keys or click to navigate · Print to PDF</span></nav>'
                      f'<script>{JS}</script></body></html>', encoding="utf-8")


# Kept in the browser so checks use the same layout and image decoding as viewers.
ISSUES_JS = """() => {
 const slide=document.querySelector('.slide.active'); const issues=[];
 const elements=[slide,...slide.querySelectorAll('*')];
 for(const e of elements){
  if(e.tagName==='IMG' && (!e.complete || !e.naturalWidth)) issues.push('Missing image: '+e.alt);
  if(e.clientHeight && e.scrollHeight>e.clientHeight+2) issues.push('Vertical overflow: '+e.className+' '+e.textContent.slice(0,70));
  if(e.clientWidth && e.scrollWidth>e.clientWidth+2) issues.push('Horizontal overflow: '+e.className+' '+e.textContent.slice(0,70));
 }
 const body=slide.querySelector('.body').getBoundingClientRect();
 const source=slide.querySelector('.source'); const footer=slide.querySelector('.footer').getBoundingClientRect();
 if(body.bottom>(source?source.getBoundingClientRect().top:footer.top)+2) issues.push('Content overlaps source/footer');
 if(document.documentElement.scrollWidth>innerWidth+2)issues.push('Page exceeds viewport width');
 return [...new Set(issues)];
}"""


def inspect_deck(output, render=None, check=False, width=1440, height=900):
    from playwright.sync_api import sync_playwright

    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            # A generated deck is offline. Do not let a manipulated asset fetch a remote URL.
            page.route(re.compile(r"^https?://"), lambda route: route.abort())
            page.goto(output.resolve().as_uri(), wait_until="load")
            page.evaluate("document.fonts.ready")
            count = page.locator('.slide').count()
            if render:
                render.mkdir(parents=True, exist_ok=True)
            for i in range(count):
                page.evaluate('(i)=>window.showSlide(i)', i)
                page.evaluate("async()=>{await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))}")
                if check:
                    errors.extend(f"slide {i+1} ({width}x{height}): {issue}" for issue in page.evaluate(ISSUES_JS))
                if render:
                    page.locator('.slide.active').screenshot(path=str(render / f'slide-{i+1:02d}.png'))
        finally:
            browser.close()
    if errors:
        raise ValueError('\n'.join(errors))
    return count


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path, help='slides.json; image paths are relative to this file')
    ap.add_argument('-o', '--output', type=Path, help='default: deck.html beside the input')
    ap.add_argument('--embed', action=argparse.BooleanOptionalAction, default=True,
                    help='inline images (default); --no-embed copies images beside the deck')
    ap.add_argument('--render', nargs='?', const='', metavar='DIR', help='render every slide to PNG (default: <deck>-render)')
    ap.add_argument('--check', action='store_true', help='fail on overflow or missing images at desktop and phone widths')
    args = ap.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding='utf-8'))
        output = args.output or args.input.parent / 'deck.html'
        build(data, args.input.resolve().parent, output, args.embed)
        render = Path(args.render) if args.render else output.parent / (output.stem + '-render')
        if args.check or args.render is not None:
            inspect_deck(output, render if args.render is not None else None, args.check)
        if args.check:
            inspect_deck(output, render / 'phone' if args.render is not None else None, True, 375, 812)
            print('PASS: no overflowing text or missing images (desktop + phone)')
        print(f'Deck: {output.resolve()}')
        if args.render is not None:
            print(f'Rendered slides: {render.resolve()}')
    except (ValueError, OSError, ImportError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
