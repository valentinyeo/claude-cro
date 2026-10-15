#!/usr/bin/env python3
"""
synthetic.py — Synthetic traffic: LLM visitors modelled on real traffic shop a site
in a real browser and report what got in their way.

Real analytics rows become weighted visitor templates (landing page, device,
channel, new/returning, real paths). Each synthetic visitor expands one template
into a believable person (Haiku or Sonnet), then browses like them: one
screenshot + clickable-element list per step, one action per step, friction
noted in their own words. Visitors stop at checkout (initiate checkout counts as
converted), never press a pay button, never type into card or password fields,
and never submit a form that carries an email or phone number. Analytics and ad
pixels are blocked so the client's data stays clean.

Commands:
  templates <export.csv|json> -o templates.json     real traffic -> weighted templates
  templates --assumed -o templates.json             no data: labelled ASSUMED mix
  run <url> --templates t.json --visitors 150 --out W/synthetic [--model haiku]
      [--goal checkout|atc|lead] [--concurrency 6] [--max-steps 20] [--yes]
  visit --visitor v.json --out dir ...              one visitor (run calls this)
  report W/synthetic                                SYNTHETIC-REPORT.md + clusters.json

Model backends: --backend api (ANTHROPIC_API_KEY, default when set), cli (the
`claude` command, slower), replay (scripted, for tests).
"""

import argparse
import base64
import csv
import json
import math
import os
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))

MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}
# Approximate USD per million tokens (input, output), for the pre-run estimate only.
PRICES = {"haiku": (1.0, 5.0), "sonnet": (3.0, 15.0), "opus": (15.0, 75.0)}
TOKENS_PER_STEP = (4500, 350)  # screenshot + elements + history in, JSON out

CATEGORIES = ["overlay_popup", "navigation", "product_info", "price_shipping", "trust", "checkout_cart",
              "performance", "mobile_layout", "copy_clarity", "search_filter", "form", "bug", "other"]
SEVERITY_W = {"critical": 4, "high": 3, "medium": 2, "low": 1}
STAGES = ["landed", "engaged", "product", "atc", "checkout"]

PAY_WORDS = re.compile(r"\b(pay now|place (my )?order|complete (my )?(order|purchase)|submit order|confirm (payment|order|purchase)|pay with|pay \$|pay £|pay €)\b", re.I)
CHECKOUT_URL = re.compile(r"/checkouts?(/|$|\?|\.)|/checkout\.html|/order-?form|[?&]step=(contact|shipping|payment)", re.I)
LEAD_URL = re.compile(r"calendar\.app\.google|calendly\.com|cal\.com/|meetings\.hubspot|savvycal|tidycal|zcal\.co|"
                      r"acuityscheduling|youcanbook\.me|bookwithme|/thank-?you|/danke", re.I)
CONTACT_HREF = re.compile(r"^(mailto:|tel:|https?://(wa\.me|api\.whatsapp\.com)/)", re.I)
CART_URL = re.compile(r"/(cart|basket|bag)(/|$|\?|\.)", re.I)
ATC_REQUEST = re.compile(r"cart/add|add[-_]?to[-_]?(cart|bag|basket)|/cart/items|addtocart|basket/add|/cart/lines|cartLinesAdd|cartCreate", re.I)
ATC_LABEL = re.compile(r"add to (cart|bag|basket)|in den warenkorb|ajouter au panier|buy now|add$", re.I)
SECRET_FIELD = re.compile(r"card|cc-|cvv|cvc|csc|expir|iban|passw|pin\b|security.?code|ssn|social", re.I)

TRACKERS = re.compile(
    r"google-analytics\.com|googletagmanager\.com|analytics\.google\.com|doubleclick\.net|googleadservices\.com|"
    r"google\.com/(pagead|ccm|ads)|facebook\.(com|net)/(tr|signals)|connect\.facebook\.net|hotjar\.(com|io)|clarity\.ms|"
    r"segment\.(io|com)|cdn\.segment|tiktok\.com/(i18n/pixel|api/v\d/pixel)|analytics\.tiktok|snap\.licdn|px\.ads\.linkedin|"
    r"bat\.bing\.com|ct\.pinterest|sc-static\.net|tr\.snapchat|criteo\.(com|net)|taboola|outbrain|posthog\.com|i\.posthog|"
    r"mixpanel\.com|amplitude\.com|heapanalytics|fullstory\.com|mouseflow|luckyorange|quantserve|scorecardresearch|"
    r"klaviyo\.com/(onsite|api/onsite|media/js/onsite)|static\.klaviyo|monorail-edge\.shopifysvc|/api/collect|"
    r"/\.well-known/shopify/monorail|/web-pixels|shopify-perf-kit|trekkie|rs\.fullstory|vwo\.com|optimizely|"
    r"cdn\.attn\.tv|attentivemobile|reddit\.com/rp|alb\.reddit|redditstatic\.com/ads|ads-twitter|t\.co/i/adsct|"
    r"stats\.wp\.com|plausible\.io/api|cloudflareinsights|sentry\.io|nr-data\.net|newrelic", re.I)


# ---------------------------------------------------------------- templates

COLS = {
    "landing": ["landing page", "landing_page", "landing page + query string", "landing page path", "entry page",
                "entry_url", "entry_page", "$entry_pathname", "$entry_current_url", "first_page", "page", "page path"],
    "device": ["device", "device category", "device_category", "$device_type", "devicecategory"],
    "source": ["session default channel group", "default channel group", "channel", "channel group",
               "session source / medium", "source / medium", "source/medium", "source", "utm_source",
               "$initial_referring_domain", "referrer", "$referring_domain", "medium"],
    "user": ["new / established", "new vs returning", "new_vs_returning", "user type", "user_type", "visitor type"],
    "country": ["country", "$geoip_country_name", "region"],
    "weight": ["sessions", "visits", "count", "users", "visitors", "active users", "total users", "views", "entrances"],
    "conversions": ["conversions", "purchases", "transactions", "ecommerce purchases", "key events", "orders"],
    "converted": ["converted", "purchased", "did_convert"],
    "path": ["path", "pages", "journey", "page path sequence", "session_path", "$pathnames"],
}


def _col(header, key):
    low = {h.strip().lower(): h for h in header}
    for name in COLS[key]:
        if name in low:
            return low[name]
    return None


def _num(v):
    try:
        return float(str(v).replace(",", "").replace("%", "").strip() or 0)
    except ValueError:
        return 0.0


def norm_device(v):
    v = (v or "").lower()
    if "tab" in v or "ipad" in v:
        return "tablet"
    if "mob" in v or "phone" in v or "android" in v or "ios" in v:
        return "mobile"
    return "desktop" if v else "mobile"


def norm_channel(v):
    v = (v or "").lower().strip()
    if not v or v.startswith(("(direct)", "direct", "$direct")) or v in ("(none)", "(not set)", "none"):
        return "direct"
    if re.search(r"paid social|facebook.*(cpc|paid)|instagram.*(cpc|paid)|tiktok.*(cpc|paid)|meta|fb ads|paid_social", v):
        return "paid social"
    if re.search(r"paid search|cpc|ppc|google ads|adwords|bing.*cpc|sem|shopping", v):
        return "paid search"
    if re.search(r"email|newsletter|klaviyo|mailchimp|sms", v):
        return "email"
    if re.search(r"organic search|google|bing|duckduckgo|yahoo|ecosia|organic", v):
        return "organic search"
    if re.search(r"social|facebook|instagram|tiktok|pinterest|reddit|youtube|t\.co|twitter|linkedin|lnkd", v):
        return "organic social"
    if re.search(r"affiliate|partner", v):
        return "affiliate"
    return "referral"


def norm_path(v):
    v = (v or "").strip()
    if not v or v.startswith("@"):
        return v or "/"
    p = urlparse(v if "://" in v else "https://x" + (v if v.startswith("/") else "/" + v))
    return (p.path or "/") + (("?" + p.query) if p.query and not re.search(r"utm_|gclid|fbclid", p.query) else "")


def load_rows(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    if path.lower().endswith(".json"):
        data = json.loads(text)
        return data if isinstance(data, list) else data.get("rows", data.get("results", []))
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
    return list(csv.DictReader(lines))


def build_templates(rows, top=40):
    if not rows:
        raise ValueError("no rows in the traffic export")
    header = list(rows[0].keys())
    c = {k: _col(header, k) for k in COLS}
    if not c["landing"] and not c["path"]:
        raise ValueError(f"no landing page or path column; columns seen: {', '.join(header)}")
    groups = {}
    for r in rows:
        path_seq = [norm_path(p) for p in re.split(r"\s*(?:>|→|->|\|)\s*|,\s*(?=/)", r.get(c["path"]) or "") if p.strip()] if c["path"] else []
        landing = norm_path(r.get(c["landing"]) if c["landing"] else (path_seq[0] if path_seq else "/"))
        device = norm_device(r.get(c["device"]) if c["device"] else "")
        channel = norm_channel(r.get(c["source"]) if c["source"] else "")
        user = "returning" if c["user"] and re.search(r"return|establish", str(r.get(c["user"])), re.I) else "new"
        w = _num(r.get(c["weight"])) if c["weight"] else 1.0
        if w <= 0:
            continue
        conv = _num(r.get(c["conversions"])) if c["conversions"] else (
            w if c["converted"] and str(r.get(c["converted"])).strip().lower() in ("1", "true", "yes") else 0.0)
        key = (landing, device, channel, user)
        g = groups.setdefault(key, {"landing": landing, "device": device, "channel": channel, "user": user,
                                    "weight": 0.0, "conversions": 0.0, "countries": Counter(), "paths": Counter()})
        g["weight"] += w
        g["conversions"] += conv
        if c["country"] and r.get(c["country"]):
            g["countries"][r[c["country"]]] += w
        if len(path_seq) > 1:
            g["paths"][" > ".join(path_seq[:8])] += w
    total = sum(g["weight"] for g in groups.values())
    ranked = sorted(groups.values(), key=lambda g: -g["weight"])
    kept, other = ranked[:top], ranked[top:]
    out = []
    for i, g in enumerate(kept, 1):
        out.append({
            "id": f"T{i:02d}", "landing": g["landing"], "device": g["device"], "channel": g["channel"],
            "user": g["user"], "share": round(g["weight"] / total, 4), "sessions": round(g["weight"]),
            "cvr": round(g["conversions"] / g["weight"], 4) if c["conversions"] or c["converted"] else None,
            "countries": [k for k, _ in g["countries"].most_common(3)],
            "example_paths": [k for k, _ in g["paths"].most_common(3)],
        })
    return {"source": "CONFIRMED", "rows": len(rows), "sessions": round(total),
            "covered_share": round(sum(t["share"] for t in out), 4),
            "dropped_templates": len(other), "templates": out}


ASSUMED = {  # used only without real data; every report built on it says ASSUMED
    "ecommerce": [
        ("/", "mobile", "paid social", "new", 0.22), ("@product", "mobile", "paid social", "new", 0.18),
        ("/", "desktop", "direct", "returning", 0.12), ("@collection", "mobile", "organic search", "new", 0.14),
        ("@product", "desktop", "paid search", "new", 0.14), ("/", "mobile", "email", "returning", 0.10),
        ("@product", "mobile", "organic search", "new", 0.10)],
    "lead": [  # services, agencies, consultants, B2B: people arrive from LinkedIn, referrals and search
        ("/", "desktop", "organic social", "new", 0.25), ("/", "mobile", "organic social", "new", 0.20),
        ("/", "desktop", "referral", "new", 0.15), ("/", "desktop", "organic search", "new", 0.15),
        ("/", "desktop", "direct", "returning", 0.15), ("@blog", "mobile", "organic search", "new", 0.10)],
    "saas": [
        ("/", "desktop", "organic search", "new", 0.25), ("@pricing", "desktop", "direct", "returning", 0.15),
        ("/", "desktop", "paid search", "new", 0.20), ("/", "mobile", "organic social", "new", 0.15),
        ("@blog", "desktop", "organic search", "new", 0.15), ("/", "mobile", "direct", "returning", 0.10)],
}


def assumed_templates(business="ecommerce"):
    return {"source": "ASSUMED", "business": business, "rows": 0, "sessions": 0, "covered_share": 1.0,
            "dropped_templates": 0,
            "templates": [{"id": f"T{i:02d}", "landing": l, "device": d, "channel": ch, "user": u, "share": s,
                           "sessions": 0, "cvr": None, "countries": [], "example_paths": []}
                          for i, (l, d, ch, u, s) in enumerate(ASSUMED[business], 1)]}


def allocate(templates, n):
    """Largest-remainder split of n visitors across templates by share (deterministic)."""
    total = sum(t["share"] for t in templates) or 1
    raw = [(t, n * t["share"] / total) for t in templates]
    counts = {t["id"]: int(x) for t, x in raw}
    left = n - sum(counts.values())
    for t, x in sorted(raw, key=lambda tx: -(tx[1] - int(tx[1])))[:left]:
        counts[t["id"]] += 1
    return counts


# ---------------------------------------------------------------- model backends

def extract_json(text):
    text = re.sub(r"```(?:json)?", "", text or "")
    start = text.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                esc = (ch == "\\") and not esc
                if ch == '"' and not esc:
                    in_str = False
                elif ch != "\\":
                    esc = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    raise ValueError("no JSON object in model reply")


class Model:
    def __init__(self, backend, model, replay=None):
        self.backend, self.alias = backend, model
        self.model = MODELS.get(model, model)
        self.usage = {"input_tokens": 0, "output_tokens": 0, "calls": 0}
        self.replay = json.loads(Path(replay).read_text()) if replay else None
        self.replay_step = 0
        if backend == "api" and not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit("ANTHROPIC_API_KEY is not set (or use --backend cli)")

    def ask(self, system, text, image=None, kind="step", max_tokens=1200):
        self.usage["calls"] += 1
        if self.backend == "replay":
            return self._replay(kind)
        for attempt in range(2):
            raw = self._api(system, text, image, max_tokens) if self.backend == "api" \
                else self._cli(system, text, image)
            try:
                return extract_json(raw)
            except ValueError:
                text += "\n\nYour last reply was not valid JSON. Reply with the JSON object only."
        raise ValueError("model gave no JSON twice")

    def _api(self, system, text, image, max_tokens):
        content = []
        if image:
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                        "data": base64.b64encode(Path(image).read_bytes()).decode()}})
        content.append({"type": "text", "text": text})
        body = json.dumps({"model": self.model, "max_tokens": max_tokens,
                           "system": system, "messages": [{"role": "user", "content": content}]}).encode()
        for attempt in range(6):
            req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, headers={
                "x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01",
                "content-type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = json.loads(r.read())
                u = data.get("usage", {})
                self.usage["input_tokens"] += u.get("input_tokens", 0)
                self.usage["output_tokens"] += u.get("output_tokens", 0)
                return "".join(b.get("text", "") for b in data.get("content", []))
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 529) and attempt < 5:
                    time.sleep(min(60, 2 ** attempt * 3) + random.random() * 2)
                    continue
                raise RuntimeError(f"Anthropic API {e.code}: {e.read()[:200]!r}")
            except (urllib.error.URLError, TimeoutError):
                if attempt < 5:
                    time.sleep(5)
                    continue
                raise
        raise RuntimeError("Anthropic API kept failing")

    def _cli(self, system, text, image):
        prompt = f"{system}\n\n{text}"
        if image:
            prompt += f"\n\nFirst use the Read tool on this screenshot of what you see now: {image}"
        cmd = ["claude", "-p", "--model", self.model, "--output-format", "json", "--no-session-persistence",
               "--allowedTools", "Read", "--max-turns", "3"]
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=300)
        try:
            data = json.loads(r.stdout)
        except json.JSONDecodeError:
            raise RuntimeError(f"claude CLI failed: {(r.stderr or r.stdout)[:200]}")
        u = data.get("usage", {})
        self.usage["input_tokens"] += u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
        self.usage["output_tokens"] += u.get("output_tokens", 0)
        return data.get("result", "")

    def _replay(self, kind):
        script = self.replay or {}
        if kind != "step":
            return script.get(kind, {})
        steps = script.get("steps", [])
        s = steps[min(self.replay_step, len(steps) - 1)] if steps else {"action": "give_up"}
        self.replay_step += 1
        return dict(s)


# ---------------------------------------------------------------- browser visitor

ELEMENTS_JS = r"""
([start, maxN]) => {
  document.querySelectorAll('[data-synth-id]').forEach(e => e.removeAttribute('data-synth-id'));
  const sel = 'a[href],button,input:not([type=hidden]),select,textarea,[role=button],[role=link],[role=tab],' +
              '[role=menuitem],[role=option],[role=checkbox],[role=radio],[role=switch],summary,label[for],[onclick]';
  const out = []; const vh = innerHeight, vw = innerWidth;
  const semantic = [...document.querySelectorAll(sel)];
  // icon-only controls (close X, swatches, chat bubbles) are often plain divs/spans/svgs with a pointer cursor
  const extra = [...document.querySelectorAll('div,span,svg,i,li,img,p')].filter(el => {
    if (el.closest(sel)) return false;
    const r = el.getBoundingClientRect();
    if (r.width < 8 || r.height < 8 || r.width > vw * 0.9 || r.top > vh || r.bottom < 0) return false;
    if (getComputedStyle(el).cursor !== 'pointer') return false;
    const parent = el.parentElement;
    return !(parent && getComputedStyle(parent).cursor === 'pointer' && !parent.closest(sel));
  });
  for (const el of semantic.concat(extra)) {
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) continue;
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    if (cx < 0 || cx >= vw || cy < 0 || cy >= vh) continue;  // a visitor can only tap what is on screen
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.display === 'none' || +st.opacity === 0) continue;
    const top = document.elementFromPoint(cx, cy);
    const covered = !!top && !(el === top || el.contains(top) || top.contains(el));
    let label = (el.getAttribute('aria-label') || el.innerText || el.value || el.getAttribute('placeholder') ||
                 el.getAttribute('title') || '').trim().replace(/\s+/g, ' ');
    if (!label) { const img = el.querySelector('img[alt]'); if (img) label = img.alt; }
    if (!label && el.id) { const l = document.querySelector('label[for="' + el.id + '"]'); if (l) label = l.innerText.trim(); }
    if (!label) label = (el.getAttribute('class') || '').split(/\s+/).find(c => /close|dismiss|chat|menu|search|cart|bag/i.test(c)) || '';
    const tag = el.tagName.toLowerCase();
    const id = start + out.length;
    el.setAttribute('data-synth-id', id);
    const f = el.closest('form');
    out.push({id, tag, type: (el.getAttribute('type') || el.getAttribute('role') || '').toLowerCase(),
              label: label.slice(0, 80), covered, name: (el.getAttribute('name') || el.getAttribute('autocomplete') || el.id || '').slice(0, 40),
              href: (el.getAttribute('href') || '').slice(0, 120), in_form: !!f});
    if (out.length >= maxN) break;
  }
  return out;
}
"""

FORM_HAS_CONTACT_JS = r"""
(el) => {
  const f = el.closest('form'); if (!f) return false;
  return [...f.querySelectorAll('input')].some(i => i.value && (/email|tel/.test(i.type) || /mail|phone|tel/i.test(i.name + i.id + (i.autocomplete || ''))));
}
"""


def is_tracker(url):
    return bool(TRACKERS.search(url))


def pay_refusal(label):
    return bool(PAY_WORDS.search(label or ""))


def secret_field(el):
    return el.get("type") == "password" or bool(SECRET_FIELD.search(f"{el.get('name', '')} {el.get('label', '')}"))


def stage_of(url, page_type, state, goal="checkout"):
    if CHECKOUT_URL.search(url or ""):  # URL only: models call carts "checkout" too often
        state["checkout"] = True
    if goal == "lead" and LEAD_URL.search(url or ""):  # a booking page counts as the lead
        state["checkout"] = True
        state.setdefault("lead_via", "reached the booking page")
    if page_type == "product" or re.search(r"/products?/|/p/|/item/|/dp/", url or "", re.I):
        state["product"] = True
    if CART_URL.search(url or "") and state.get("clicked_atc"):
        state["atc"] = True


def furthest(state):
    best = "landed"
    for s in STAGES:
        if state.get(s):
            best = s
    return best


AGES = ["18-24", "25-34", "25-34", "35-44", "35-44", "45-54", "55-64", "65+"]
LIVES = ["student", "parent of young kids", "office worker", "tradesperson", "retiree", "freelancer",
         "shift worker", "small business owner", "frequent traveller", "gym regular", "buying a gift for someone",
         "deal hunter", "first time buying this kind of product", "long-time fan of the brand", "teacher",
         "creative professional", "new homeowner", "caregiver for a parent"]
MINDSETS = ["just curious, no plan to buy today", "comparing with a competitor in another tab",
            "has one specific item in mind", "waiting for a discount", "replacing something worn out",
            "needs it by a date", "came back to finish a purchase they started", "checking the price after a recommendation"]


def persona_hint(visitor_id):
    """Fixed per-visitor hints so 150 visitors do not all become the same person."""
    r = random.Random(visitor_id)
    return f"age {r.choice(AGES)}, {r.choice(LIVES)}, {r.choice(MINDSETS)}"


SYSTEM_PERSONA = """You create one believable website visitor from a real traffic segment. Reply with JSON only:
{"name": "...", "age": 0, "situation": "one sentence: who they are and why they came now",
 "goal": "what they want to get done on this visit", "intent": "browsing|comparing|ready_to_buy",
 "patience": "low|medium|high", "tech_comfort": "low|medium|high", "budget_sensitivity": "low|medium|high",
 "worries": ["1-3 concerns specific to this person and this kind of product"],
 "voice": "how they talk, a few words"}
Build the person from the hint you are given. Make them ordinary, not a stereotype. Match intent to the segment's real conversion rate when given:
most real visitors do not buy."""

SYSTEM_STEP = """You are {name}, {age}. {situation}
Goal this visit: {goal}. Intent: {intent}. Patience: {patience}. Comfort with websites: {tech_comfort}.
Worries: {worries}. You talk like: {voice}.
You are on {device} and came from {channel}{came_how}.

Act exactly like this person, not like a tester. Real people skim, look at the screenshot first,
click the obvious thing, close popups that block them, scroll a bit, and leave when the site is
confusing, slow, untrustworthy or does not answer their worry fast enough. Leave (give_up) when this
person would leave; do not push on just to finish. If you would buy, go as far as starting checkout.

Each turn you get a screenshot of what is on screen and a numbered list of clickable elements.
Reply with JSON only:
{{"page_type": "home|collection|product|search|cart|checkout|content|account|other",
  "thought": "first person, in your voice, what you notice and want, max 2 sentences",
  "action": "click|tap|type|select|scroll_down|scroll_up|back|wait|give_up|done",
  "element": <id for click/type/select>, "x": <tap only>, "y": <tap only>, "text": "<for type/select>", "submit": false,
  "friction": [{{"severity": "critical|high|medium|low", "category": "{categories}",
                "issue": "what got in your way on THIS screen, concrete, naming the element or text",
                "quote": "what you would mutter, in your voice"}}]}}
Friction only for real things visible now (blocking popup, missing price or delivery info, unclear
button, tiny text, slow load, doubt about trust); an empty list when this screen is fine.
Never invent problems you cannot see. Do not repeat friction you already noted. The element list is
a helper and can miss icons: never report the list as a problem. To press something you see on the
screenshot that is not in the list, use "tap" with x and y in screenshot pixels. An element marked
"covered" may only be partly hidden: check the screenshot before calling it blocked.
Use done only after starting checkout. Never enter real personal
data: for an email use synthetic@example.com."""

SYSTEM_EXIT = """You are the same visitor, now leaving the site. If you reached checkout, the visit was stopped
there on purpose: that stop is not a problem with the site. Reply with JSON only:
{"outcome": "one sentence on what happened", "why": "why you left or why you went to checkout",
 "biggest_frustration": "the single thing that most got in your way, concrete, or none",
 "what_would_have_helped": "one concrete change", "would_return": "yes|maybe|no", "trust": 1-5}"""


def observe(page, out_dir, n, max_elements=70):
    shot = os.path.abspath(os.path.join(out_dir, f"step-{n:02d}.jpg"))
    try:
        page.screenshot(path=shot, type="jpeg", quality=60, timeout=15000)
    except Exception:
        shot = None
    elements = []
    for frame in page.frames:
        if len(elements) >= max_elements:
            break
        try:
            got = frame.evaluate(ELEMENTS_JS, [len(elements) + 1, max_elements - len(elements)])
        except Exception:
            continue
        for e in got:
            e["frame"] = page.frames.index(frame)
        elements.extend(got)
    try:
        text = page.evaluate("() => (document.body ? document.body.innerText : '').replace(/\\s+/g, ' ').slice(0, 1200)")
        scroll = page.evaluate("() => Math.round(100 * (scrollY + innerHeight) / Math.max(document.body.scrollHeight, 1))")
    except Exception:
        text, scroll = "", 0
    return {"screenshot": shot, "elements": elements, "text": text, "scroll_pct": scroll,
            "url": page.url, "title": _safe_title(page)}


def _safe_title(page):
    try:
        return page.title()
    except Exception:
        return ""


def element_lines(elements):
    lines = []
    for e in elements:
        kind = e["tag"] + (f"[{e['type']}]" if e.get("type") else "")
        extra = " (covered by something on top)" if e.get("covered") else ""
        lines.append(f"[{e['id']}] {kind} \"{e['label'] or e.get('name') or e.get('href') or '?'}\"{extra}")
    return "\n".join(lines) or "(no clickable elements visible)"


def act(page, obs, decision, goal, state):
    """Run one action. Returns a short result string; sets state flags for refusals and conversions."""
    action = (decision.get("action") or "wait").lower()
    by_id = {e["id"]: e for e in obs["elements"]}
    el = by_id.get(_int(decision.get("element")))
    if action in ("click", "type", "select") and not el:
        return f"no element {decision.get('element')} on screen"
    if action == "click":
        if pay_refusal(el["label"]):
            state["refused_pay"] = True
            state["checkout"] = True
            return "refused: synthetic visitors never press a pay button"
        if goal == "lead" and CONTACT_HREF.match(el.get("href") or ""):
            state["checkout"] = True
            state["lead_via"] = "chose to get in touch by " + ("WhatsApp" if "wa" in el["href"][:30] else el["href"].split(":")[0])
            return "converted: would get in touch this way (link not opened)"
        frame = page.frames[el["frame"]] if el["frame"] < len(page.frames) else page.main_frame
        loc = frame.locator(f'[data-synth-id="{el["id"]}"]').first
        try:
            if el.get("in_form") and loc.evaluate(FORM_HAS_CONTACT_JS) and (
                    el.get("type") == "submit" or el["tag"] == "button"):
                state["refused_submit"] = True
                if goal == "lead":
                    state["checkout"] = True
                return "refused: would submit a form with contact details (not sent)"
        except Exception:
            pass
        if ATC_LABEL.search(el["label"] or ""):
            state["clicked_atc"] = True
        try:
            loc.click(timeout=6000)
        except Exception as exc:
            msg = str(exc).splitlines()[0][:160]
            return "click did not work: " + ("something on top intercepted it" if "intercept" in msg else msg)
        page.wait_for_timeout(1800)
        return "clicked"
    if action in ("type", "select"):
        if secret_field(el):
            return "refused: synthetic visitors never type into card, password or security fields"
        text = str(decision.get("text") or "")[:80]
        if "@" in text:
            text = "synthetic@example.com"
        frame = page.frames[el["frame"]] if el["frame"] < len(page.frames) else page.main_frame
        loc = frame.locator(f'[data-synth-id="{el["id"]}"]').first
        try:
            if action == "select":
                loc.select_option(label=text, timeout=5000)
            else:
                loc.fill(text, timeout=5000)
                if decision.get("submit"):
                    if el.get("in_form") and loc.evaluate(FORM_HAS_CONTACT_JS):
                        state["refused_submit"] = True
                        return "typed; refused to submit a form with contact details"
                    loc.press("Enter")
                    page.wait_for_timeout(2000)
        except Exception as exc:
            return f"{action} did not work: " + str(exc).splitlines()[0][:160]
        return f"{action}d"
    if action == "tap":
        x, y = _int(decision.get("x")), _int(decision.get("y"))
        if x is None or y is None:
            return "tap needs x and y"
        dpr = page.evaluate("devicePixelRatio") or 1
        page.mouse.click(x / dpr, y / dpr)
        page.wait_for_timeout(1500)
        return f"tapped at {x},{y}"
    if action in ("scroll_down", "scroll_up"):
        vh = (page.viewport_size or {"height": 800})["height"]
        page.mouse.wheel(0, int(vh * 0.8) * (1 if action == "scroll_down" else -1))
        page.wait_for_timeout(900)
        return "scrolled"
    if action == "back":
        try:
            page.go_back(wait_until="domcontentloaded", timeout=20000)
        except Exception:
            pass
        page.wait_for_timeout(1200)
        return "went back"
    if action == "wait":
        page.wait_for_timeout(2500)
        return "waited"
    return action


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def visit(v, out_dir, backend, model, goal, max_steps, replay=None, timeout_s=420):
    import importlib.util
    from playwright.sync_api import sync_playwright

    spec = importlib.util.spec_from_file_location("fetch_page_mod", os.path.join(HERE, "fetch_page.py"))
    fp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fp)

    os.makedirs(out_dir, exist_ok=True)
    m = Model(backend, model, replay)
    t = v["template"]
    started = time.time()
    seg = (f"Segment: lands on {v['start_url']} ({t['landing']}), device {t['device']}, channel {t['channel']}, "
           f"{t['user']} visitor, countries {', '.join(t.get('countries') or []) or 'unknown'}, "
           f"real conversion rate {'%.1f%%' % (100 * t['cvr']) if t.get('cvr') is not None else 'unknown'}. "
           f"Real paths these visitors took: {'; '.join(t.get('example_paths') or []) or 'not given'}. "
           f"Site: {urlparse(v['start_url']).netloc}. Hint for this person: {persona_hint(v['id'])}.")
    persona = m.ask(SYSTEM_PERSONA, seg, kind="persona", max_tokens=1200)
    Path(out_dir, "persona.json").write_text(json.dumps({"template": t, "persona": persona}, indent=2))

    came_how = {"paid social": " after tapping an ad in their feed", "paid search": " after clicking a search ad",
                "organic search": " from a search result", "email": " from a marketing email",
                "organic social": " from a social media post", "referral": " from a link on another site",
                "affiliate": " from a review or deal site", "direct": " by typing the address"}.get(t["channel"], "")
    fields = {k: persona.get(k, "") for k in ("name", "age", "situation", "goal", "intent", "patience", "tech_comfort", "voice")}
    fields["worries"] = ", ".join(persona.get("worries") or [])
    system = SYSTEM_STEP.format(device=t["device"], channel=t["channel"], came_how=came_how,
                                categories="|".join(CATEGORIES), **fields)

    state = {"landed": True, "trackers_blocked": 0, "trackers_allowed": 0}
    log, history, noted, end_reason = [], [], [], "max_steps"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        dev = {"mobile": p.devices["iPhone 13"], "tablet": p.devices["iPad (gen 7)"]}.get(t["device"])
        ctx = browser.new_context(**dev) if dev else browser.new_context(
            viewport={"width": 1440, "height": 900}, user_agent=fp.DEFAULT_USER_AGENT)
        fp.guard_browser(ctx)

        def block_trackers(route):
            if is_tracker(route.request.url):
                state["trackers_blocked"] += 1
                route.abort("blockedbyclient")
            else:
                route.fallback()

        ctx.route("**/*", block_trackers)  # registered last, so it runs before the private-address guard

        def on_response(resp):
            if is_tracker(resp.url):
                state["trackers_allowed"] += 1
            # carts are often created on page load: only count an add after an add-to-cart click
            if state.get("clicked_atc") and resp.request.method in ("POST", "PUT") and ATC_REQUEST.search(resp.url) \
                    and resp.status < 400:
                state["atc"] = True
        ctx.on("response", on_response)
        pages = []
        ctx.on("page", lambda pg: pages.append(pg))
        page = ctx.new_page()
        load_ms = None
        try:
            t0 = time.time()
            resp = page.goto(v["start_url"], wait_until="domcontentloaded", timeout=45000)
            try:
                page.wait_for_load_state("networkidle", timeout=6000)
            except Exception:
                pass
            load_ms = round((time.time() - t0) * 1000)
            blocked = fp.looks_blocked(resp.status if resp else 200, page.content()) if v["start_url"].startswith("http") else None
            if blocked and "almost no visible text" not in blocked:
                end_reason = f"blocked: {blocked}"
                max_steps = 0
        except Exception as exc:
            end_reason = "landing page failed: " + str(exc).splitlines()[0][:160]
            max_steps = 0

        for n in range(1, max_steps + 1):
            if time.time() - started > timeout_s:
                end_reason = "visit timeout"
                break
            if pages and pages[-1] is not page and not pages[-1].is_closed():
                page = pages[-1]
            obs = observe(page, out_dir, n)
            hist = "\n".join(history[-8:]) or "(just arrived)"
            if noted:
                hist += "\nFriction you already noted (do not repeat): " + "; ".join(noted[-10:])
            prompt = (f"Step {n} of at most {max_steps}. URL: {obs['url']}\nTitle: {obs['title']}\n"
                      f"Scrolled to {obs['scroll_pct']}% of the page."
                      + (f" First load took {load_ms / 1000:.1f}s." if n == 1 and load_ms else "")
                      + f"\nWhat you did so far:\n{hist}\n\nVisible text (start of page):\n{obs['text'][:800]}\n\n"
                      f"Clickable elements on screen:\n{element_lines(obs['elements'])}")
            try:
                d = m.ask(system, prompt, image=obs["screenshot"])
            except Exception as exc:
                end_reason = "model error: " + str(exc)[:160]
                break
            if d.get("label") and d.get("element") is None:  # replay scripts name elements by label
                d["element"] = next((e["id"] for e in obs["elements"] if d["label"].lower() in (e["label"] or "").lower()), None)
            page_type = (d.get("page_type") or "other").lower()
            stage_of(obs["url"], page_type, state, goal)
            fr = [f for f in (d.get("friction") or []) if isinstance(f, dict) and f.get("issue")]
            for f in fr:
                noted.append(str(f["issue"])[:90])
                f["severity"] = (f.get("severity") or "medium").lower() if (f.get("severity") or "").lower() in SEVERITY_W else "medium"
                f["category"] = f.get("category") if f.get("category") in CATEGORIES else "other"
            entry = {"n": n, "url": obs["url"], "page_type": page_type, "screenshot": os.path.basename(obs["screenshot"] or ""),
                     "thought": d.get("thought", ""), "action": d.get("action"), "element": d.get("element"),
                     "element_label": next((e["label"] for e in obs["elements"] if e["id"] == _int(d.get("element"))), None),
                     "friction": fr}
            if state.get("checkout"):
                entry["result"] = "reached the conversion; synthetic visitors stop here"
                log.append(entry)
                end_reason = f"converted: {state['lead_via']}" if state.get("lead_via") else "converted: reached checkout"
                break
            action = (d.get("action") or "").lower()
            if action in ("give_up", "done"):
                entry["result"] = action
                log.append(entry)
                end_reason = "gave up" if action == "give_up" else "said done"
                break
            entry["result"] = act(page, obs, d, goal, state)
            if action != "wait":
                state["engaged"] = True
            try:
                page.wait_for_load_state("domcontentloaded", timeout=8000)
            except Exception:
                pass
            stage_of(page.url, "", state, goal)
            log.append(entry)
            history.append(f"step {n} ({page_type}): {action} {entry['element_label'] or ''} -> {entry['result']}")
            if goal == "atc" and state.get("atc"):
                end_reason = "converted: added to cart"
                break
            if state.get("checkout"):
                try:  # let the checkout render before the last screenshot, or it looks empty
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                obs = observe(page, out_dir, n + 1)
                log.append({"n": n + 1, "url": obs["url"], "page_type": "checkout",
                            "screenshot": os.path.basename(obs["screenshot"] or ""), "thought": "", "action": "stop",
                            "result": "reached checkout; synthetic visitors stop here", "friction": []})
                end_reason = "converted: lead form filled (not sent)" if goal == "lead" and state.get("refused_submit") \
                    else f"converted: {state['lead_via']}" if state.get("lead_via") else "converted: reached checkout"
                break
        browser.close()

    try:
        story = "\n".join(f"step {e['n']} {e['page_type']}: {e['thought']} -> {e.get('result', '')}"
                          + "".join(f" | friction: {f['issue']}" for f in e.get("friction", [])) for e in log)
        exit_iv = m.ask(system + "\n\n" + SYSTEM_EXIT, f"Your visit:\n{story or '(the page never loaded)'}\nEnded: {end_reason}",
                        kind="exit", max_tokens=800) if log else {}
    except Exception as exc:
        exit_iv = {"error": str(exc)[:160]}
    result = {"id": v["id"], "template": t["id"], "device": t["device"], "channel": t["channel"], "user": t["user"],
              "start_url": v["start_url"], "persona": persona, "goal": goal, "end_reason": end_reason,
              "stage": furthest(state), "converted": end_reason.startswith("converted") or (goal == "atc" and bool(state.get("atc"))),
              "atc": bool(state.get("atc")), "steps": len(log), "seconds": round(time.time() - started),
              "trackers_blocked": state["trackers_blocked"], "trackers_allowed": state["trackers_allowed"],
              "refused_pay": bool(state.get("refused_pay")), "refused_submit": bool(state.get("refused_submit")),
              "exit": exit_iv, "usage": m.usage, "model": m.model, "backend": backend, "log": log}
    Path(out_dir, "visit.json").write_text(json.dumps(result, indent=2))
    return result


# ---------------------------------------------------------------- run (fan-out)

def resolve_landing(site, landing, crawl_cache):
    if landing in ("", "/"):
        return site
    if landing.startswith("@"):
        if "pages" not in crawl_cache:
            import importlib.util
            spec = importlib.util.spec_from_file_location("crawl_mod", os.path.join(HERE, "crawl_site.py"))
            cm = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cm)
            try:
                crawl_cache["pages"] = cm.crawl(site)["pages"]
            except Exception:
                crawl_cache["pages"] = {}
        urls = crawl_cache["pages"].get(landing[1:]) or [site]
        return urls[0]
    return urljoin(site if site.endswith("/") else site + "/", landing.lstrip("/")) if not landing.startswith("http") else landing


def estimate(visitors, max_steps, model):
    steps = visitors * min(max_steps, 14)
    pin, pout = PRICES.get(model, PRICES["sonnet"])
    tin, tout = steps * TOKENS_PER_STEP[0], steps * TOKENS_PER_STEP[1]
    return tin, tout, tin / 1e6 * pin + tout / 1e6 * pout


def cmd_run(a):
    tpl = json.loads(Path(a.templates).read_text())
    site = a.url.rstrip("/") + "/" if a.url.startswith("http") and urlparse(a.url).path in ("", "/") else a.url
    counts = allocate(tpl["templates"], a.visitors)
    tin, tout, usd = estimate(a.visitors, a.max_steps, a.model)
    print(f"Plan: {a.visitors} visitors, model {a.model} ({MODELS.get(a.model, a.model)}), backend {a.backend}, "
          f"traffic {tpl['source']}, concurrency {a.concurrency}")
    print(f"Estimate: ~{tin / 1e6:.1f}M input + {tout / 1e6:.2f}M output tokens, about ${usd:.0f} (approximate prices)")
    if a.visitors > 10 and not a.yes:
        print("Re-run with --yes to spend this. Nothing was run.")
        sys.exit(2)
    out = Path(a.out)
    (out / "visitors").mkdir(parents=True, exist_ok=True)
    crawl_cache, plan, k = {}, [], 0
    for t in tpl["templates"]:
        start = resolve_landing(site, t["landing"], crawl_cache)
        for i in range(counts.get(t["id"], 0)):
            k += 1
            plan.append({"id": f"v{k:03d}", "n": i + 1, "template": t, "start_url": start})
    (out / "plan.json").write_text(json.dumps({"url": a.url, "templates_source": tpl["source"], "model": a.model,
                                                "goal": a.goal, "visitors": plan}, indent=2))
    (out / "templates.json").write_text(json.dumps(tpl, indent=2))

    def one(v):
        d = out / "visitors" / v["id"]
        if (d / "visit.json").exists() and not a.fresh:
            return json.loads((d / "visit.json").read_text())
        d.mkdir(parents=True, exist_ok=True)
        (d / "visitor.json").write_text(json.dumps(v))
        cmd = [sys.executable, os.path.abspath(__file__), "visit", "--visitor", str(d / "visitor.json"), "--out", str(d),
               "--backend", a.backend, "--model", a.model, "--goal", a.goal, "--max-steps", str(a.max_steps)]
        if a.replay:
            cmd += ["--replay", a.replay]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not (d / "visit.json").exists():
            (d / "error.txt").write_text((r.stderr or r.stdout)[-3000:])
            return {"id": v["id"], "error": (r.stderr or r.stdout).strip().splitlines()[-1:] or ["failed"]}
        return json.loads((d / "visit.json").read_text())

    done = 0
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        for res in ex.map(one, plan):
            done += 1
            if "error" in res:
                print(f"[{done}/{len(plan)}] {res['id']} ERROR {res['error'][0][:120]}", flush=True)
            else:
                print(f"[{done}/{len(plan)}] {res['id']} {res['device']:<7} {res['channel']:<15} {res['stage']:<9} "
                      f"{res['steps']:>2} steps  {res['end_reason'][:60]}", flush=True)
    write_report(out, None if a.no_merge else Model(a.backend, a.merge_model, a.replay))
    print(f"Report: {out / 'SYNTHETIC-REPORT.md'}")


# ---------------------------------------------------------------- report

def _tokens(s):
    return {w for w in re.findall(r"[a-z0-9$£€%]+", (s or "").lower()) if len(w) > 2 and w not in STOP}


STOP = set("the and for with this that you was are not but have has had can cant don dont its it's just very "
           "what where when how why there their they them then than too into from your our out get got would "
           "could should will see seen page site some any all one also only even still really".split())


def similarity(a, b):
    """Jaccard, or the overlap share when both texts are long enough (same problem, longer wording)."""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    jac = inter / len(a | b)
    return max(jac, inter / min(len(a), len(b)) - 0.25) if min(len(a), len(b)) >= 5 else jac


def group_issues(items, threshold=0.3):
    """Greedy grouping of similar issue texts against each group's first members. Returns list of lists."""
    groups = []
    for it in items:
        toks = _tokens(it["issue"])
        best, best_s = None, 0.0
        for g in groups:
            sc = max(similarity(toks, m) for m in g["members"])
            if sc > best_s:
                best, best_s = g, sc
        if best and best_s >= threshold:
            best["items"].append(it)
            if len(best["members"]) < 8:
                best["members"].append(toks)
        else:
            groups.append({"members": [toks], "items": [it]})
    return [g["items"] for g in groups]


def load_visits(root):
    visits, errors = [], 0
    for d in sorted(Path(root, "visitors").glob("v*")):
        f = d / "visit.json"
        if f.exists():
            v = json.loads(f.read_text())
            v["_dir"] = str(d)
            visits.append(v)
        elif (d / "error.txt").exists():
            errors += 1
    return visits, errors


SYSTEM_MERGE = """You merge duplicate friction reports from synthetic website visitors. Two entries are the same
problem when fixing one would fix the other (same element or same missing information), even if worded
differently or seen on different pages. Do not merge different problems that share a category.
Reply with JSON only: {"groups": [{"title": "short plain problem statement naming the element", "ids": ["G3", "G7"]}]}
List only groups of two or more ids; each id at most once."""


def summarize(grp, n_visits, title=None):
    worst = {}
    for f in grp:  # each visitor counts once, at the worst severity they reported
        if f["visitor"] not in worst or SEVERITY_W[f["severity"]] > SEVERITY_W[worst[f["visitor"]]["severity"]]:
            worst[f["visitor"]] = f
    return {
        "page_type": Counter(f["page_type"] for f in grp).most_common(1)[0][0],
        "category": Counter(f["category"] for f in grp).most_common(1)[0][0],
        "visitors": len(worst), "visitor_ids": sorted(worst), "share": round(len(worst) / max(n_visits, 1), 3),
        "mentions": len(grp), "severity": dict(Counter(f["severity"] for f in worst.values())),
        "score": sum(SEVERITY_W[f["severity"]] for f in worst.values()),
        "devices": dict(Counter(f["device"] for f in worst.values())),
        "headline": title or Counter(f["issue"] for f in grp).most_common(1)[0][0],
        "examples": [{"visitor": f["visitor"], "step": f["step"], "issue": f["issue"], "quote": f.get("quote", ""),
                      "screenshot": f["screenshot"], "url": f["url"]}
                     for f in sorted(worst.values(), key=lambda f: -SEVERITY_W[f["severity"]])[:4]],
    }


def merge_groups(groups, model, limit=120):
    """One text-only model call that joins groups describing the same problem. Returns (groups, titles)."""
    order = sorted(range(len(groups)), key=lambda i: -len({f["visitor"] for f in groups[i]}))[:limit]
    listing = "\n".join(f"G{i}: [{groups[i][0]['category']}/{groups[i][0]['page_type']}] {groups[i][0]['issue'][:200]}"
                        for i in order)
    try:
        reply = model.ask(SYSTEM_MERGE, listing, kind="merge", max_tokens=4000)
    except Exception as exc:
        print(f"merge skipped: {exc}", file=sys.stderr)
        return groups, {}
    used, merged, titles = set(), [], {}
    for g in reply.get("groups", []):
        ids = [int(x[1:]) for x in g.get("ids", []) if re.fullmatch(r"G\d+", str(x)) and int(x[1:]) < len(groups)]
        ids = [i for i in ids if i not in used]
        if len(ids) < 2:
            continue
        used.update(ids)
        titles[len(merged)] = g.get("title")
        merged.append([f for i in ids for f in groups[i]])
    return merged + [g for i, g in enumerate(groups) if i not in used], titles


def cluster(visits, model=None):
    frictions = []
    for v in visits:
        for e in v.get("log", []):
            for f in e.get("friction", []):
                frictions.append({**f, "visitor": v["id"], "page_type": e.get("page_type", "other"), "step": e["n"],
                                  "screenshot": os.path.join(v["_dir"], e.get("screenshot") or ""),
                                  "device": v["device"], "url": e.get("url")})
    by_cat = defaultdict(list)
    for f in frictions:
        by_cat[f["category"]].append(f)
    groups = [grp for items in by_cat.values() for grp in group_issues(items)]
    titles = {}
    if model and len(groups) > 1:
        groups, titles = merge_groups(groups, model)
    clusters = [summarize(g, len(visits), titles.get(i)) for i, g in enumerate(groups)]
    clusters.sort(key=lambda c: (-c["score"], -c["visitors"]))
    for i, c in enumerate(clusters, 1):
        c["id"] = f"S-{i}"
    return clusters


def write_report(root, merge_model=None):
    root = Path(root)
    visits, errors = load_visits(root)
    if not visits:
        raise SystemExit(f"no finished visitors in {root / 'visitors'}")
    plan = json.loads((root / "plan.json").read_text()) if (root / "plan.json").exists() else {}
    tpl = json.loads((root / "templates.json").read_text()) if (root / "templates.json").exists() else {"source": "UNKNOWN"}
    ran = [v for v in visits if not v["end_reason"].startswith(("blocked", "landing page failed", "model error"))]
    blocked = [v for v in visits if v["end_reason"].startswith("blocked")]
    clusters = cluster(ran, merge_model)
    n = len(ran) or 1
    stage_n = {s: sum(1 for v in ran if STAGES.index(v["stage"]) >= STAGES.index(s)) for s in STAGES}
    usage = Counter()
    for v in visits:
        usage.update(v.get("usage", {}))
    model = visits[0].get("model", "")
    alias = next((k for k, val in MODELS.items() if val == model), "sonnet")
    usd = usage["input_tokens"] / 1e6 * PRICES[alias][0] + usage["output_tokens"] / 1e6 * PRICES[alias][1]
    if merge_model:  # the merge call is billed at its own model's price
        mu, ma = merge_model.usage, next((k for k, val in MODELS.items() if val == merge_model.model), "sonnet")
        usd += mu["input_tokens"] / 1e6 * PRICES[ma][0] + mu["output_tokens"] / 1e6 * PRICES[ma][1]
    exits = [dict(issue=v["exit"].get("biggest_frustration", ""), visitor=v["id"]) for v in ran
             if v.get("exit", {}).get("biggest_frustration") and str(v["exit"]["biggest_frustration"]).lower() not in ("none", "nothing", "")]
    exit_groups = sorted(group_issues(exits, 0.25), key=len, reverse=True)

    L = [f"# Synthetic Traffic Report: {plan.get('url', '')}", "",
         f"**Visitors:** {len(ran)} completed, {len(blocked)} blocked by bot protection, {errors} crashed · "
         f"**Model:** {model} · **Goal:** {plan.get('goal', '')} · **Traffic template:** {tpl.get('source')}"
         + (f" ({tpl.get('sessions')} real sessions, {round(100 * tpl.get('covered_share', 0))}% covered)" if tpl.get("source") == "CONFIRMED" else
            " (no real analytics: segment mix is a guess)"),
         f"**Cost:** {usage['input_tokens'] / 1e6:.2f}M input + {usage['output_tokens'] / 1e6:.2f}M output tokens, about ${usd:.2f}",
         "", "> Synthetic visitors are language models acting on real traffic segments. Treat every cluster as a",
         "> hypothesis to confirm with real data (recordings, analytics, user tests). The synthetic funnel below",
         "> is not a conversion forecast.", "",
         "## Synthetic funnel", "", "| Stage | Visitors | Share |", "|---|---|---|"]
    for s in STAGES:
        label = "lead action" if s == "checkout" and plan.get("goal") == "lead" else s
        L.append(f"| {label} | {stage_n[s]} | {100 * stage_n[s] / n:.0f}% |")
    L += ["", "| Segment | Visitors | Reached product | Started checkout |", "|---|---|---|---|"]
    seg = defaultdict(list)
    for v in ran:
        seg[f"{v['device']} · {v['channel']}"].append(v)
    for k, vs in sorted(seg.items(), key=lambda kv: -len(kv[1])):
        L.append(f"| {k} | {len(vs)} | {sum(STAGES.index(v['stage']) >= 2 for v in vs)} | {sum(v['stage'] == 'checkout' for v in vs)} |")
    L += ["", "## Friction clusters (ranked by visitors affected x severity)", ""]
    for c in clusters[:25]:
        L.append(f"### [{c['id']}] {c['headline']}")
        L.append(f"**Page:** {c['page_type']} · **Category:** {c['category']} · **Visitors:** {c['visitors']} "
                 f"({100 * c['share']:.0f}%) · **Severity:** " + ", ".join(f"{k} {v}" for k, v in c["severity"].items())
                 + " · **Devices:** " + ", ".join(f"{k} {v}" for k, v in c["devices"].items()))
        for ex in c["examples"]:
            L.append(f"- {ex['visitor']} step {ex['step']}: {ex['issue']}"
                     + (f" *\"{ex['quote']}\"*" if ex.get("quote") else "")
                     + f" · Evidence: {os.path.relpath(ex['screenshot'], root)}")
        L.append("")
    L += ["## Why visitors left (exit interviews)", ""]
    for g in exit_groups[:12]:
        L.append(f"- **{len(g)}x** {g[0]['issue']} ({', '.join(x['visitor'] for x in g[:6])})")
    L += ["", "## Visitors", "", "| Visitor | Segment | Persona | Furthest | Steps | Ended |", "|---|---|---|---|---|---|"]
    for v in visits:
        p = v.get("persona") or {}
        L.append(f"| {v['id']} | {v['device']} · {v['channel']} | {p.get('name', '?')}, {p.get('intent', '?')}, "
                 f"{p.get('patience', '?')} patience | {v['stage']} | {v['steps']} | {v['end_reason'][:50]} |")
    trackers = sum(v.get("trackers_allowed", 0) for v in visits)
    L += ["", f"Tracker requests blocked: {sum(v.get('trackers_blocked', 0) for v in visits)}; let through: {trackers}.", ""]
    (root / "SYNTHETIC-REPORT.md").write_text("\n".join(L), encoding="utf-8")
    (root / "clusters.json").write_text(json.dumps({
        "url": plan.get("url"), "visitors": len(ran), "blocked": len(blocked), "errors": errors,
        "templates_source": tpl.get("source"), "funnel": stage_n, "clusters": clusters,
        "exit_reasons": [{"count": len(g), "issue": g[0]["issue"], "visitors": [x["visitor"] for x in g]} for g in exit_groups],
        "usage": dict(usage), "usd": round(usd, 2)}, indent=2), encoding="utf-8")
    return clusters


# ---------------------------------------------------------------- cli

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("templates")
    t.add_argument("export", nargs="?")
    t.add_argument("--assumed", nargs="?", const="ecommerce", choices=sorted(ASSUMED), help="no data: a labelled guess for this business type")
    t.add_argument("--top", type=int, default=40)
    t.add_argument("-o", "--output", required=True)
    r = sub.add_parser("run")
    r.add_argument("url")
    r.add_argument("--templates", required=True)
    r.add_argument("--visitors", type=int, default=150)
    r.add_argument("--out", required=True)
    for p_ in (r, v_ := sub.add_parser("visit")):
        p_.add_argument("--backend", choices=["api", "cli", "replay"],
                        default="api" if os.environ.get("ANTHROPIC_API_KEY") else "cli")
        p_.add_argument("--model", default="haiku")
        p_.add_argument("--goal", choices=["checkout", "atc", "lead"], default="checkout")
        p_.add_argument("--max-steps", type=int, default=20)
        p_.add_argument("--replay")
    r.add_argument("--concurrency", type=int, default=6)
    r.add_argument("--yes", action="store_true")
    r.add_argument("--fresh", action="store_true", help="re-run visitors that already finished")
    v_.add_argument("--visitor", required=True)
    v_.add_argument("--out", required=True)
    rp = sub.add_parser("report")
    rp.add_argument("folder")
    rp.add_argument("--backend", choices=["api", "cli", "replay"],
                    default="api" if os.environ.get("ANTHROPIC_API_KEY") else "cli")
    rp.add_argument("--replay")
    for p_ in (r, rp):
        p_.add_argument("--merge-model", default="sonnet", help="model that joins duplicate clusters (text only)")
        p_.add_argument("--no-merge", action="store_true")
    a = ap.parse_args()

    if a.cmd == "templates":
        if a.assumed:
            data = assumed_templates(a.assumed)
        elif a.export:
            data = build_templates(load_rows(a.export), a.top)
        else:
            ap.error("give an analytics export or --assumed")
        Path(a.output).write_text(json.dumps(data, indent=2))
        print(f"{len(data['templates'])} templates ({data['source']}), "
              f"{round(100 * data['covered_share'])}% of {data['sessions']} sessions -> {a.output}")
        for x in data["templates"][:10]:
            print(f"  {x['id']} {100 * x['share']:5.1f}%  {x['device']:<7} {x['channel']:<15} {x['user']:<9} {x['landing'][:50]}")
    elif a.cmd == "run":
        cmd_run(a)
    elif a.cmd == "visit":
        v = json.loads(Path(a.visitor).read_text())
        res = visit(v, a.out, a.backend, a.model, a.goal, a.max_steps, a.replay)
        print(json.dumps({k: res[k] for k in ("id", "stage", "steps", "end_reason")}))
    elif a.cmd == "report":
        cl = write_report(a.folder, None if a.no_merge else Model(a.backend, a.merge_model, a.replay))
        print(f"{len(cl)} friction clusters -> {Path(a.folder) / 'SYNTHETIC-REPORT.md'}")


if __name__ == "__main__":
    main()
